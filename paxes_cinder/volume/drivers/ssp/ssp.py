# =================================================================
# =================================================================

"""
Driver for PowerVM servers running SharedStoragePools
"""

import re
import os
import uuid
import time
import json

from oslo.config import cfg

from cinder import context
from cinder import db as db_api
from cinder import exception
from cinder.openstack.common import excutils
from cinder.openstack.common import log as logging
from cinder.openstack.common.db import exception as db_exc
from cinder.volume import volume_types
from cinder.volume import driver

from paxes_cinder import _
from paxes_cinder.db import api as paxes_db_api
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient.v1.shell import K2Encoder

LOG = logging.getLogger(__name__)

ssp_opts = [
    cfg.StrOpt('powervm_mgr_cluster',
               default=None,
               help=('K2 uuid for PowerVM Cluster managing the'
                     ' Shared Storage Pool (SSP)')),
    cfg.StrOpt('ssp_excdir',
               default='/var/log/cinder/k2a-ffdc',
               help='K2 FFDC directory'),
    # TODO check before GA
    cfg.IntOpt('ssp_k2operation_timeout',
               default=300,
               help='The k2operator timeout to be used for all K2 operations'),
    cfg.BoolOpt('ssp_create_lu_by_job',
                default=True,
                help='Create LUs using K2 Job (True/False)'),
    # TODO check before GA
    cfg.BoolOpt('ssp_create_lu_by_job_single_step',
                default=True,
                help='Create LUs using K2 Job in single step (True/False)'),
    # TODO check before GA
    cfg.IntOpt('ssp_refresh_level',
               default=0,
               help='Refresh requests below this level will not be performed'),
    cfg.BoolOpt('ssp_log_elapsed_time',
                default=False,
                help=('If True print elapsed times for selected '
                      'driver requests.')),
    cfg.IntOpt('ssp_k2operation_retries',
               default=30,
               help=('Number of times driver should retry on a'
                     'K2 HTTP Status 412 (Precondition Failed)'))
]

CONF = cfg.CONF
CONF.register_opts(ssp_opts)


RESTRICTED_METADATA_LU_UDID_KEY = "lu_udid"
RESTRICTED_METADATA_LU_NAME_KEY = "lu_name"
RESTRICTED_METADATA_LU_SSP_UDID = "ssp_udid"


def _incorporate_restricted_metadata(volume_ref):
    """Retrieve and attach access-restricted volume metadata from
    the Cinder database

    Relies on P-specific extension.
    """

    ctxt = context.get_admin_context()
    metadata = paxes_db_api.\
        volume_restricted_metadata_get(ctxt, volume_ref['id'])
    volume_ref['restricted_metadata'] = metadata

    if ((RESTRICTED_METADATA_LU_UDID_KEY in metadata and
         RESTRICTED_METADATA_LU_NAME_KEY in metadata and
         RESTRICTED_METADATA_LU_SSP_UDID in metadata)):

        return (metadata[RESTRICTED_METADATA_LU_UDID_KEY],
                metadata[RESTRICTED_METADATA_LU_NAME_KEY],
                metadata[RESTRICTED_METADATA_LU_SSP_UDID])


def _update_restricted_metadata(volume_id, lu_udid,
                                lu_name, ssp_udid):
    """Update access-restricted volume metadata in the Cinder database

    Relies on P-specific extension.
    """

    metadata = {RESTRICTED_METADATA_LU_UDID_KEY: lu_udid,
                RESTRICTED_METADATA_LU_NAME_KEY: lu_name,
                RESTRICTED_METADATA_LU_SSP_UDID: ssp_udid}
    ctxt = context.get_admin_context()
    paxes_db_api.\
        volume_restricted_metadata_update_or_create(ctxt, volume_id,
                                                    metadata)


class K2_XA(object):
    """ K2 transaction context"""

    def __init__(self, task):
        self._service = "cinder-ssp"
        self._task = task
        self._i = 0
        self._ct = time.localtime()
        self._start = time.time()
        self._ctx = str(uuid.uuid4())

    def _fmt(self):
        return ("%(major)s %(minor)s %(ts)s %(i)d %(ctx)s" %
                {"major": self._service,
                 "minor": self._task,
                 "ts": time.strftime("%Y-%m-%d %H:%M:%S", self._ct),
                 "i": self._i,
                 "ctx": self._ctx, })

    def log(self):
        if CONF.ssp_log_elapsed_time:
            msg = ("%(major)s %(minor)s %(ts)s"
                   " %(ctx)s:"
                   "elapsed time: >%(et)s<")
            msg = msg % \
                {"major": self._service,
                 "minor": self._task,
                 "ts": time.strftime("%Y-%m-%d %H:%M:%S", self._ct),
                 "ctx": self._ctx,
                 "et": time.time() - self._start, }
            LOG.info(msg)

    def r(self):
        return self._fmt()

    def ri(self):
        x = self._fmt()
        self._i += 1
        return x


class SSPDriver(driver.VolumeDriver):
    """IBM PowerVM Shared Storage Pool (SSP) volume driver."""

    VERSION = "1.0.0"

    def __init__(self, *args, **kwargs):
        super(SSPDriver, self).__init__(*args, **kwargs)
        self.configuration.append_config_values(ssp_opts)
        self._context = None
        self._k2aclient = None
        self._cluster = None
        self._ssp = None
        self._vios_state = {}

    def _retrieve_hmc(self):
        """Retrieve registered HMC details from DB.

        P extension.
        """

        hmcs = paxes_db_api.\
            ibm_hmc_get_all_by_cluster(self._context, CONF.host)

        if len(hmcs) <= 0:
            msg = (_("ssp: "
                     " no matching HMC was found in the DB for"
                     " host: >%s<")
                   % CONF.host)
            raise exception.VolumeBackendAPIException(data=msg)

        return hmcs[0]

    def _construct_name(self, volume):
        """ Construct name for LU creation"""

        if volume.get("display_name"):
            display_name_nospace = re.sub(r"\s+", "_", volume['display_name'])
            name = CONF.volume_name_template % display_name_nospace
        else:
            name = volume['name']

        return name

    def _uniquify_name(self, name):
        """ Uniquify name for LU creation (obsolete("""

        return name.ljust(32, "-")[:32] + uuid.uuid4().hex

    def _get_lu_params(self, type_id, vol_id=None):
        opts = self._build_default_opts()
        if type_id:
            ctxt = context.get_admin_context()
            volume_type = volume_types.get_volume_type(ctxt, type_id)
            specs = volume_type.get('extra_specs')
            for k, value in specs.iteritems():
                scope = None
                key = None
                key_split = k.split(':')

                if len(key_split) == 2:
                    scope = key_split[0]
                    key = key_split[1]

                if scope == "drivers":
                    opts[key] = value

        if vol_id is not None:
            # add options from metadata
            metadata = self.db.volume_metadata_get(self._context, vol_id)
            # setting logical unit type for capture or deploy operation
            if metadata is not None and 'is_image_volume' in metadata:
                if bool(metadata.get('is_image_volume')):
                    opts['logical_unit_type'] = 'VirtualIO_Image'

        return opts

    def _create_default_volume_type(self, context, volume_type_name):
        """Create a Default Volume Type for Host"""

        vbn = self.configuration.volume_backend_name

        # Obtain our default options
        opts = self._build_default_opts()
        extra_specs = {}
        for key, value in opts.iteritems():
            extra_specs["drivers:" + key] = value

        extra_specs['drivers:display_name'] = volume_type_name
        extra_specs['capabilities:volume_backend_name'] = vbn

        # Don't use volume_type.create during init_host
        try:
            type_ref = db_api.volume_type_create(
                context, dict(name=volume_type_name, extra_specs=extra_specs))
        except db_exc.DBError as e:
            LOG.exception(_('ssp:'
                            ' during create default volume type,'
                            ' DB error: >%s<'), e)
            raise exception.VolumeTypeCreateFailed(
                name=volume_type_name,
                extra_specs=extra_specs)

        return type_ref

    def _build_default_opts(self):
        opts = {'shared_storage_pool': self._ssp.unique_device_id,
                'provision_type': 'thin',
                'logical_unit_type': 'VirtualIO_Disk'}
        return opts

    def _create_lu_bp(self, name, size, opts, k2xa):
        """Create a new LU using POST"""

        thin = True
        #Check for override values specified in the extra-specs
        if (opts is not None and opts):
            for opt, val in opts.iteritems():
                if opt == 'shared_storage_pool':
                    if val is not None:
                        extra_spec_ssp_id = val
                if opt == 'provision_type':
                    if val is not None and val == 'thick':
                        thin = False

        ssp_udid = self._ssp.unique_device_id
        if ssp_udid != extra_spec_ssp_id:
            msg = (_("ssp:"
                     " during _create_lu for"
                     " LU: (name: >%(name)s<,"
                     " size: >%(size)s<, thin: >%(thin)s<),"
                     " ssp_udid: >%(ssp_udid)s< is not same as"
                     " extra_spec shared_storage_pool:"
                     " >%(extra_spec_ssp_id)s<") %
                   {"name": name, "size": size, "thin": thin,
                    "ssp_udid": ssp_udid,
                    "extra_spec_ssp_id": extra_spec_ssp_id, })
            raise exception.VolumeBackendAPIException(data=msg)
        # need to log.info JOB ID
        try:
            (lu, lu_ssp) = self._ssp.update_append_lu(
                name,
                size,
                thin=thin,
                logicalunittype=opts['logical_unit_type'],
                xa=k2xa.ri())
        except Exception as e:
            msg = (_("ssp:"
                     " failed during _create_lu for"
                     " LU: (name: >%(name)s<, size: >%(size)s<,"
                     " thin: >%(thin)s<),"
                     " message: >%(e)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"name": name, "size": size, "thin": thin, "e": e,
                    "k2xa": k2xa.r(), })
            raise exception.VolumeBackendAPIException(data=msg)
        # for now one ssp per cluster
        self._ssp = lu_ssp

        return lu

    def _create_lu_bj(self, name, size, opts, k2xa):
        """Create a new LU using JOB"""

        thin = True
        #Check for override values specified in the extra-specs
        if (opts is not None and opts):
            for opt, val in opts.iteritems():
                if opt == 'shared_storage_pool':
                    if val is not None:
                        extra_spec_ssp_id = val
                if opt == 'provision_type':
                    if val is not None and val == 'thick':
                        thin = False

        ssp_udid = self._ssp.unique_device_id
        if ssp_udid != extra_spec_ssp_id:
            msg = (_("ssp:"
                     " during _create_lu job for"
                     " LU: (name: >%(name)s<, size: >%(size)s<,"
                     " thin: >%(thin)s<),"
                     " ssp_udid: >%(ssp_udid)s< is not same as"
                     " extra_spec shared_storage_pool:"
                     " >%(extra_spec_ssp_id)s<") %
                   {"name": name, "size": size, "thin": thin,
                    "ssp_udid": ssp_udid,
                    "extra_spec_ssp_id": extra_spec_ssp_id, })
            raise exception.VolumeBackendAPIException(data=msg)

        try:
            cluster = self._cluster
            logicalunittype = opts['logical_unit_type']
            (status, lu_udid, job_id) = cluster.lu_create(
                name,
                size,
                thin=thin,
                logicalunittype=logicalunittype,
                xa=k2xa.ri())
        except Exception as e:
            msg = (_("ssp:"
                     " failure during _create_lu,"
                     " create parameters:"
                     " name: >%(name)s<,"
                     " size: >%(size)s<,"
                     " thin: >%(thin)s<,"
                     " logicalunittype: >%(logicalunittype)s<,"
                     " message: >%(e)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"name": name, "size": size, "thin": thin,
                    "logicalunittype": logicalunittype, "e": e,
                    "k2xa": k2xa.r(), })
            raise exception.VolumeBackendAPIException(data=msg)

        if status != "COMPLETED_OK":
            msg = (_("ssp:"
                     " failure during _create_lu job,"
                     " expecting COMPLETED_OK,"
                     " but for job_id: >%(job_id)s<"
                     " got status: >%(status)s<"
                     " create parameters:"
                     " name: >%(name)s<,"
                     " size: >%(size)s<,"
                     " thin: >%(thin)s<,"
                     " logicalunittype: >%(logicalunittype)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"job_id": job_id, "status": status, "name": name,
                    "size": size, "thin": thin,
                    "logicalunittype": logicalunittype, "k2xa": k2xa.r(), })
            raise exception.VolumeBackendAPIException(data=msg)

        msg = (_("ssp:"
                 " create complete,"
                 " job_id: >%(job_id)s<,"
                 " name: >%(name)s<,"
                 " size: >%(size)s<,"
                 " thin: >%(thin)s<,"
                 " logicalunittype: >%(logicalunittype)s<,"
                 " k2xa: >%(k2xa)s<") %
               {"job_id": job_id, "name": name, "size": size, "thin": thin,
                "logicalunittype": logicalunittype, "k2xa": k2xa.r(), })
        LOG.info(msg)

        return lu_udid

    def _find_lu_by_udid(self, lu_udid):
        found_lus = []
        for lu in self._ssp.logical_units.logical_unit:
            if lu_udid == lu.unique_device_id:
                found_lus.append(lu)
        return found_lus

    def _find_lu_by_name(self, lu_name):
        found_lus = []
        for lu in self._ssp.logical_units.logical_unit:
            if lu_name == lu.unit_name:
                found_lus.append(lu)
        return found_lus

    def _delete_lu(self, lu, k2xa):
        lu_udid = lu.unique_device_id
        try:
            self._ssp = self._ssp.update_del_lus([lu_udid],
                                                 xa=k2xa.ri())
        except Exception as e:
            msg = (_("ssp:"
                     " failed during _delete_lu"
                     " of LU w/"
                     " with unique_device_id: >%(lu_udid)s<, "
                     " message: >%(e)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"lu_udid": lu_udid, "e": e, "k2xa": k2xa.r(), })
            raise exception.VolumeBackendAPIException(data=msg)

    def _clone_lu_by_name(self,
                          src_lu_name, tgt_lu_size, tgt_lu_name,
                          opts,
                          k2xa):
        src_lus = self._find_lu_by_name(src_lu_name)
        if len(src_lus) == 0:
            msg = (_("ssp:"
                     " during _clone_lu_by_name,"
                     " couldnt find lu"
                     " with src_lu_name: >%(src_lu_name)s<,"
                     " tgt_lu_name: >%(tgt_lu_name)s<") %
                   {"src_lu_name": src_lu_name, "tgt_lu_name": tgt_lu_name, })
            raise exception.VolumeBackendAPIException(data=msg)
        if len(src_lus) > 1:
            msg = (_("ssp:"
                     " during _clone_lu_by_name,"
                     " found too many lus"
                     " with src_lu_name: >%(src_lu_name)s<,"
                     " tgt_lu_name: >%(tgt_lu_name)s<") %
                   {"src_lu_name": src_lu_name, "tgt_lu_name": tgt_lu_name, })
            raise exception.VolumeBackendAPIException(data=msg)
        src_lu = src_lus[0]

        return self._clone_lu(src_lu, tgt_lu_size, tgt_lu_name,
                              opts, k2xa)

    def _clone_lu(self,
                  src_lu, tgt_lu_size, tgt_lu_name,
                  opts,
                  k2xa):
        cluster = self._cluster
        if CONF.ssp_create_lu_by_job:
            if CONF.ssp_create_lu_by_job_single_step:
                try:
                    tgt_lu_name = self._uniquify_name(tgt_lu_name)
                    o = opts['logical_unit_type']
                    (status, tgt_lu_udid, job_id) = \
                        cluster.lu_linked_clone_of_lu_bj(
                            src_lu,
                            tgt_lu_name,
                            dest_lu_unit_capacity=tgt_lu_size,
                            dest_lu_logical_unit_type=o,
                            xa=k2xa.ri())
                except Exception as e:
                    msg = (_("ssp:"
                             " failure during _clone_lu_bj,"
                             " clone parameters:"
                             " src_lu_udid: >%(src_lu_udid)s<,"
                             " tgt_lu_name: >%(tgt_lu_name)s<"
                             " tgt_lu_size: >%(tgt_lu_size)s<"
                             " msg: >%(e)s<,"
                             " k2xa: >%(k2xa)s<") %
                           {"src_lu_udid": src_lu.unique_device_id,
                            "tgt_lu_name": tgt_lu_name,
                            "tgt_lu_size": tgt_lu_size,
                            "e": e,
                            "k2xa": k2xa.r(), })
                    raise exception.VolumeBackendAPIException(data=msg)

                if status != "COMPLETED_OK":
                    msg = (_("ssp:"
                             " apparent failure during _clone_lu_bj,"
                             " expecting COMPLETED_OK,"
                             " but for job_id: >%(job_id)s<"
                             " got status: >%(status)s<"
                             " clone parameters:"
                             " src_lu_udid: >%(src_lu_udid)s<,"
                             " tgt_lu_name: >%(tgt_lu_name)s<"
                             " tgt_lu_size: >%(tgt_lu_size)s<,"
                             " k2xa: >%(k2xa)s<") %
                           {"job_id": job_id, "status": status,
                            "src_lu_udid": src_lu.unique_device_id,
                            "tgt_lu_name": tgt_lu_name,
                            "tgt_lu_size": tgt_lu_size, "k2xa": k2xa.r(), })
                    raise exception.VolumeBackendAPIException(data=msg)

            else:
                try:
                    tgt_lu_udid = self._create_lu_bj(tgt_lu_name,
                                                     tgt_lu_size,
                                                     opts,
                                                     k2xa)
                except Exception as e:
                    with excutils.save_and_reraise_exception():
                        msg = (_("ssp:"
                                 " failure during _clone_lu_bj,"
                                 " during create,"
                                 " clone parameters:"
                                 " src_lu_udid: >%(src_lu_udid)s<,"
                                 " tgt_lu_name: >%(tgt_lu_name)s<"
                                 " tgt_lu_size: >%(tgt_lu_size)s<"
                                 " message: >%(e)s<,"
                                 " k2xa: >%(k2xa)s<") %
                               {"src_lu_udid": src_lu.unique_device_id,
                                "tgt_lu_name": tgt_lu_name,
                                "tgt_lu_size": tgt_lu_size,
                                "e": e,
                                "k2xa": k2xa.r(), })
                        LOG.error(msg)
                try:
                    status, job_id = cluster.lu_linked_clone(
                        src_lu.unique_device_id,
                        tgt_lu_udid,
                        xa=k2xa.ri())
                except Exception as e:
                    msg = (_("ssp:"
                             " failure during _clone_lu_bj,"
                             " during clone,"
                             " clone parameters:"
                             " src_lu_udid: >%(src_lu_udid)s<,"
                             " tgt_lu_name: >%(tgt_lu_name)s<"
                             " tgt_lu_size: >%(tgt_lu_size)s<"
                             " message: >%(e)s<,"
                             " k2xa: >%(k2xa)s<") %
                           {"src_lu_udid": src_lu.unique_device_id,
                            "tgt_lu_name": tgt_lu_name,
                            "tgt_lu_size": tgt_lu_size,
                            "e": e,
                            "k2xa": k2xa.r(), })
                    raise exception.VolumeBackendAPIException(data=msg)

                if status != "COMPLETED_OK":
                    msg = (_("ssp:"
                             " apparent failure during _clone_lu_bj,"
                             " expecting COMPLETED_OK,"
                             " but for job_id: >%(job_id)s<"
                             " got status: >%(status)s<"
                             " clone parameters:"
                             " src_lu_udid: >%(src_lu_udid)s<,"
                             " tgt_lu_name: >%(tgt_lu_name)s<"
                             " tgt_lu_size: >%(tgt_lu_size)s<,"
                             " k2xa: >%(k2xa)s<") %
                           {"job_id": job_id, "status": status,
                            "src_lu_udid": src_lu.unique_device_id,
                            "tgt_lu_name": tgt_lu_name,
                            "tgt_lu_size": tgt_lu_size,
                            "k2xa": k2xa.r(), })
                    raise exception.VolumeBackendAPIException(data=msg)
        else:
            try:
                tgt_lu_name = self._uniquify_name(tgt_lu_name)
                (status, tgt_lu, self._ssp, job_id) = \
                    cluster.lu_linked_clone_of_lu_bp(
                        self._ssp,
                        src_lu.unique_device_id,
                        tgt_lu_name,
                        dest_lu_unit_capacity=tgt_lu_size,
                        dest_lu_logical_unit_type=opts['logical_unit_type'],
                        xa=k2xa.ri())
                tgt_lu_udid = tgt_lu.unique_device_id
            except Exception as e:
                msg = (_("ssp:"
                         " failure during _clone_lu_bp,"
                         " clone parameters:"
                         " src_lu_udid: >%(src_lu_udid)s<,"
                         " tgt_lu_name: >%(tgt_lu_name)s<"
                         " tgt_lu_size: >%(tgt_lu_size)s<"
                         " message: >%(e)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"src_lu_udid": src_lu.unique_device_id,
                        "tgt_lu_name": tgt_lu_name,
                        "tgt_lu_size": tgt_lu_size,
                        "e": e, "k2xa": k2xa.r(), })
                raise exception.VolumeBackendAPIException(data=msg)

            if status != "COMPLETED_OK":
                msg = (_("ssp:"
                         " apparent failure during _clone_lu_bp,"
                         " expecting COMPLETED_OK,"
                         " but for job_id: >%(job_id)s<"
                         " got status: >%(status)s<"
                         " clone parameters:"
                         " src_lu_udid: >%(src_lu_udid)s<,"
                         " tgt_lu_name: >%(tgt_lu_name)s<"
                         " tgt_lu_size: >%(tgt_lu_size)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"job_id": job_id, "status": status,
                        "src_lu_udid": src_lu.unique_device_id,
                        "tgt_lu_name": tgt_lu_name,
                        "tgt_lu_size": tgt_lu_size, "k2xa": k2xa.r(), })
                raise exception.VolumeBackendAPIException(data=msg)
        msg = (_("ssp:"
                 " clone complete,"
                 " job_id: >%(job_id)s<,"
                 " src_lu_udid: >%(src_lu_udid)s<,"
                 " tgt_lu_name: >%(tgt_lu_name)s<"
                 " tgt_lu_size: >%(tgt_lu_size)s<,"
                 " k2xa: >%(k2xa)s<") %
               {"job_id": job_id,
                "src_lu_udid": src_lu.unique_device_id,
                "tgt_lu_name": tgt_lu_name,
                "tgt_lu_size": tgt_lu_size, "k2xa": k2xa.r(), })
        LOG.info(msg)

        return tgt_lu_udid

    def _update_volume_status(self, k2xa):
        """Retrieve status info from ssp."""

        if not self._ssp:
            msg = _("ssp: driver not yet initialized")
            LOG.info(msg)
            return
        try:
            t0 = time.time()
            self._ssp = self._k2aclient.sharedstoragepool.refresh(self._ssp,
                                                                  xa=k2xa.ri())
            delta = time.time() - t0
            if delta >= CONF.periodic_interval:
                LOG.warn(_("K2 GET SharedStoragePool time: >%(delta)f< "
                           "is bigger or equal to "
                           "update_stats periodic interval: "
                           ">%(periodic_interval)d<")
                         % {"delta": delta,
                            "periodic_interval": CONF.periodic_interval, })
        except Exception as e:
            msg = (_("ssp:"
                     " during get_volume_stats,"
                     " failed to refresh shared storage pool"
                     " with ssp_id: >%(self._ssp.id)s<,"
                     " message: >%(e)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"self._ssp.id": self._ssp.id, "e": e, "k2xa": k2xa.r(), })
            raise exception.VolumeBackendAPIException(data=msg)
        LOG.debug("_ssp dictionary: %s", self._ssp.__dict__)
        self._stats['vendor_name'] = 'IBM'
        self._stats['driver_version'] = self.VERSION
        self._stats['storage_protocol'] = 'ssp'
        self._stats['total_capacity_gb'] = \
            int(float(self._ssp.capacity))
        self._stats['free_capacity_gb'] = \
            int(float(self._ssp.free_space))
        # Do a subtraction here unless total_logical_unit_size factors in(?)
        self._stats['allocated_capacity_gb'] = \
            int(float(self._ssp.capacity) - float(self._ssp.free_space))
        self._stats['reserved_percentage'] = 0

        self._stats['volume_backend_name'] = CONF.host
        self._stats['pool_name'] = self._ssp.storage_pool_name
        self._stats['udid'] = self._ssp.unique_device_id
        # sync up fix from 9025.
        self._stats['default_volume_type'] = \
            volume_types.get_default_volume_type()

    def _cluster_vios_check(self, duringwhatstage, k2xa):
        """lu_clone sample for k2aclient"""

        # refresh cache
        try:
            self._cluster = \
                self._k2aclient.cluster.refresh(self._cluster,
                                                xa=k2xa.ri())
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error("ssp: exception: >%s<", e)
                msg = _("ssp:"
                        " during %(duringwhatstage)s,"
                        " while performing vios cluster check,"
                        " failed to refresh cluster"
                        " id: >%(self._cluster.id)s<,"
                        " k2xa: >%(k2xa)s<")
                LOG.error(msg % {"duringwhatstage": duringwhatstage,
                                 "self._cluster.id": self._cluster.id,
                                 "k2xa": k2xa.r(), })

        # updated vios state
        n_state = {}
        for node in self._cluster.node.node:
            if not node.virtual_io_server:
    #             LOG.info(_("Node %s has no virtual_io_server. "
    #                        "Skipping.") % str(node.__dict__))
                continue
            node_parts = node.virtual_io_server.split('/')
            ms_id = node_parts[-3]
            vios_id = node_parts[-1]
            try:
                vios = self._k2aclient.\
                    virtualioserver.get(ms_id,
                                        vios_id,
                                        xag=["None"],
                                        xa=k2xa.ri())
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    LOG.error("ssp: exception: >%s<", e)
                    msg = _("ssp:"
                            " during %(duringwhatstage)s,"
                            " while performing vios cluster check,"
                            " failed to get virtualioserver,"
                            " managedsystem id: >%(ms_id)s<,"
                            " virtualioserver id: >%(vios_id)s<,"
                            " k2xa: >%(k2xa)s<")
                    LOG.error(msg % {"duringwhatstage": duringwhatstage,
                                     "ms_id": ms_id,
                                     "vios_id": vios_id,
                                     "k2xa": k2xa.r(), })

            if vios_id not in n_state:
                n_state[vios_id] = (vios.operating_system_version,
                                    vios.partition_state,
                                    vios.resource_monitoring_control_state)

        c_state = self._vios_state

        c_k = set(c_state.keys())
        n_k = set(n_state.keys())

        # VIOS that have left
        del_k = c_k.difference(n_k)
        for k in del_k:
            (c_osv, c_ps, c_rmcs) = c_state[k]
            msg = (_("ssp:"
                     " during %(duringwhatstage)s,"
                     " for cluster"
                     " id: >%(cluster_id)s<,"
                     " vios disappeared,"
                     " vios id: >%(vios_id)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"duringwhatstage": duringwhatstage,
                    "cluster_id": self._cluster.id,
                    "vios_id": k,
                    "k2xa": k2xa.r(), })
            LOG.info(msg)

        # VIOS that are same
        common_k = c_k.intersection(n_k)
        for k in common_k:
            if c_state[k] != n_state[k]:
                (c_osv, c_ps, c_rmcs) = c_state[k]
                (n_osv, n_ps, n_rmcs) = n_state[k]

                msg = (_("ssp:"
                         " during %(duringwhatstage)s,"
                         " for cluster"
                         " id: >%(cluster_id)s<,"
                         " some vios parameter(s) changed,"
                         " vios id: >%(vios_id)s<,"
                         " version: >%(c_osv)s< to >%(n_osv)s<,"
                         " PartitionState: >%(c_ps)s< to >%(n_ps)s<,"
                         " ResourceMonitoringControlState:"
                         " >%(c_rmcs)s< to >%(n_rmcs)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"duringwhatstage": duringwhatstage,
                        "cluster_id": self._cluster.id,
                        "vios_id": k,
                        "c_osv": c_osv,
                        "n_osv": n_osv,
                        "c_ps": c_ps,
                        "n_ps": n_ps,
                        "c_rmcs": c_rmcs,
                        "n_rmcs": n_rmcs,
                        "k2xa": k2xa.r(), })
                LOG.info(msg)

        # New VIOS
        new_k = n_k.difference(c_k)
        for k in new_k:
            (osv, ps, rmcs) = n_state[k]
            msg = (_("ssp:"
                     " during %(duringwhatstage)s,"
                     " for cluster"
                     " id: >%(cluster_id)s<,"
                     " added vios,"
                     " vios id: >%(vios_id)s<,"
                     " version: >%(osv)s<,"
                     " PartitionState: >%(ps)s<,"
                     " ResourceMonitoringControlState: >%(rmcs)s<,"
                     " k2xa: >%(k2xa)s<") %
                   {"duringwhatstage": duringwhatstage,
                    "cluster_id": self._cluster.id,
                    "vios_id": k,
                    "osv": osv,
                    "ps": ps,
                    "rmcs": rmcs,
                    "k2xa": k2xa.r(), })
            LOG.info(msg)

        self._vios_state = n_state

    def _get_and_check_lu(self,
                          volume,
                          duringwhatstage,
                          refresh_level,
                          k2xa):

        ret = _incorporate_restricted_metadata(volume)
        if ret is None:
            msg = (_("ssp:"
                     " during %(duringwhatstage)s,"
                     " could not find"
                     " restricted metadata for"
                     " volume id: >%(volume_id)s<") %
                   {"duringwhatstage": duringwhatstage,
                    "volume_id": volume["id"], })
            raise exception.VolumeBackendAPIException(data=msg)
        (lu_udid, lu_name, lu_ssp_udid) = ret

        if refresh_level >= CONF.ssp_refresh_level:
            try:
                self._ssp = self._k2aclient.sharedstoragepool.refresh(
                    self._ssp,
                    xa=k2xa.ri())
            except Exception as e:
                msg = (_("ssp:"
                         " during %(duringwhatstage)s,"
                         " failed to refresh shared storage pool"
                         " with ssp_id: >%(self._ssp.id)s<,"
                         " message: >%(e)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"duringwhatstage": duringwhatstage,
                        "self._ssp.id": self._ssp.id, "e": e,
                        "k2xa": k2xa.r(), })
                raise exception.VolumeBackendAPIException(data=msg)

        lus = self._find_lu_by_udid(lu_udid)
        if len(lus) == 0:
            msg = (_("ssp:"
                     " during %(duringwhatstage)s,"
                     " couldnt find lu"
                     " for volume_id: >%(volume_id)s<"
                     " with: unique_device_id: >%(lu_udid)s<"
                     " and unit_name: >%(lu_name)s<") %
                   {"duringwhatstage": duringwhatstage,
                    "volume_id": volume["id"],
                    "lu_udid": lu_udid, "lu_name": lu_name, })
            raise exception.VolumeBackendAPIException(data=msg)
        if len(lus) > 1:
            msg = (_("ssp:"
                     " during %(duringwhatstage)s,"
                     " found too many lus"
                     " for volume_id: >%(volume_id)s<"
                     " with: unique_device_id: >%(lu_udid)s<"
                     " and unit_name: >%(lu_name)s<") %
                   {"duringwhatstage": duringwhatstage,
                    "volume_id": volume["id"],
                    "lu_udid": lu_udid, "lu_name": lu_name, })
            raise exception.VolumeBackendAPIException(data=msg)

        return ret, lus[0]

    def do_setup(self, context):
        LOG.debug(_('enter: do_setup'))

        k2xa = K2_XA("do_setup")

        self._context = context

        if CONF.host is None:
            raise exception.InvalidConfigurationValue(
                option='host',
                value=CONF.host)

        if CONF.powervm_mgr_cluster is None:
            raise exception.InvalidConfigurationValue(
                option='powervm_mgr_cluster',
                value=CONF.powervm_mgr_cluster)

        try:
            hmc = self._retrieve_hmc()
        except Exception:
            with excutils.save_and_reraise_exception():
                msg = _("ssp:"
                        " failure during do_setup,"
                        " cant find hmc.")
                LOG.error(msg)

        k2api_version = 1
        k2_url = hmc['access_ip']
        k2_username = hmc['user_id']
        k2_password = hmc['password']

        excdir = self.configuration.ssp_excdir
        if excdir is not None:
            excdir = os.path.join(excdir, CONF.host)

        retries = self.configuration.ssp_k2operation_retries
        timeout = self.configuration.ssp_k2operation_timeout
        try:
            self._k2aclient = \
                client.Client(k2api_version,
                              k2_url,
                              k2_username,
                              k2_password,
                              retries=retries,
                              timeout=timeout,
                              excdir=excdir,
                              k2o_use_cache=True)
        except:
            with excutils.save_and_reraise_exception():
                msg = (_("ssp:"
                         " during do_setup,"
                         " failed to obtain k2client,"
                         " k2_url: >%(k2_url)s<,"
                         " k2_username: >%(k2_username)s<") %
                       {"k2_url": k2_url, "k2_username": k2_username, })
                LOG.error(msg)

        try:
            mc = self._k2aclient.managementconsole.\
                get(hmc['hmc_uuid'], xa=k2xa.ri())
        except Exception:
            with excutils.save_and_reraise_exception():
                msg = (_("ssp:"
                         " during do_setup,"
                         " using hmc_uuid: >%(hmc_uuid)s<,"
                         " failed to retrieve managementconsole,"
                         " k2xa: >%(k2xa)s<") %
                       {"hmc_uuid": hmc['hmc_uuid'], "k2xa": k2xa.r(), })
                LOG.error(msg)

        output = json.dumps(mc.version_info, sort_keys=True, cls=K2Encoder)
        LOG.info(_("ssp:"
                   " during do_setup,"
                   " hmc version: >%s<") % output)

        try:
            self._cluster = self._k2aclient.cluster.\
                get(self.configuration.powervm_mgr_cluster,
                    xa=k2xa.ri())
        except Exception:
            with excutils.save_and_reraise_exception():
                msg = (_("ssp:"
                         " during do_setup,"
                         " using k2_url: >%(k2_url)s<,"
                         " failed to retrieve cluster,"
                         " cluster_id: >%(cluster_id)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"k2_url": k2_url,
                        "cluster_id": self.configuration.powervm_mgr_cluster,
                        "k2xa": k2xa.r(), })
                LOG.error(msg)

        self._cluster_vios_check("do_setup", k2xa)

        ssp_id = self._cluster.cluster_shared_storage_pool.split('/')[-1]
        try:
            self._ssp = self._k2aclient.sharedstoragepool.get(ssp_id,
                                                              xa=k2xa.ri())
        except Exception:
            with excutils.save_and_reraise_exception():
                msg = (_("ssp:"
                         " during do_setup,"
                         " using k2_url: >%(k2_url)s< and"
                         " cluster_id: >%(cluster_id)s<"
                         " failed to retrieve shared storage pool"
                         " with ssp_ip: >%(ssp_id)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"k2_url": k2_url,
                        "cluster_id": self.configuration.powervm_mgr_cluster,
                        "ssp_id": ssp_id, "k2xa": k2xa.r(), })
                LOG.error(msg)

        # Ensure that the default volume type exists
        vtn = self.configuration.default_volume_type
        vtn = vtn.decode('utf-8') if vtn else vtn
        try:
            volume_types.get_volume_type_by_name(context, vtn)
        except exception.VolumeTypeNotFoundByName:
            # If the default volume type does not exist, we create it here.
            LOG.info(_("ssp:"
                       " during do_setup,"
                       " creating default volume type: >%s<") % vtn)
            self._create_default_volume_type(context, vtn,)
        k2xa.log()
        LOG.debug(_('leave: do_setup'))

    def check_for_setup_error(self):
        LOG.debug(_('leave: check_for_setup_error'))

    def ensure_export(self, ctxt, volume):
        """Check that the volume exists on the storage."""

        k2xa = K2_XA("ensure_export")

        self._get_and_check_lu(volume,
                               "ensure_export",
                               1000,
                               k2xa)
        k2xa.log()

    def create_export(self, ctxt, volume):
        model_update = None
        return model_update

    def remove_export(self, ctxt, volume):
        pass

    def create_volume(self, volume):

        k2xa = K2_XA("create_volume")

        volume_type_id = volume.get('volume_type_id')
        if not volume_type_id:
            volume_type = volume_types.get_default_volume_type()
            volume_type_id = volume_type['id']
            volume['volume_type_id'] = volume_type_id
            #Update db to preserve volume_type
            self.db.volume_update(self._context, volume['id'],
                                  {'volume_type_id': volume_type_id})

        opts = self._get_lu_params(volume_type_id, volume['id'])
        volume_name = self._construct_name(volume)
        try:
            if CONF.ssp_create_lu_by_job:
                lu_udid = self._create_lu_bj(volume_name,
                                             str(volume['size']),
                                             opts,
                                             k2xa)
            else:
                volume_name = self._uniquify_name(volume_name)
                lu = self._create_lu_bp(volume_name,
                                        str(volume['size']),
                                        opts,
                                        k2xa)
                lu_udid = lu.unique_device_id
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<"), e)
                msg = (_("ssp:"
                         " failed during create_volume"))
                LOG.error(msg)

        # Place the LU UDID and name into restricted metadata so that it can
        # be viewed by users and retrieved by this driver when it subsequently
        # performs operations on this volume.
        _update_restricted_metadata(volume['id'],
                                    lu_udid,
                                    volume_name,
                                    self._ssp.unique_device_id)
        k2xa.log()

    def delete_volume(self, volume):

        k2xa = K2_XA("delete_volume")

        ret, lu = self._get_and_check_lu(volume,
                                         "delete_volume",
                                         1000,
                                         k2xa)
        (lu_udid, lu_name, lu_ssp_udid) = ret

        try:
            self._delete_lu(lu, k2xa)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<"), e)
                msg = _("ssp:"
                        " failed during delete_volume,"
                        " lu_udid: >%(lu_udid)s<"
                        " lu_name: >%(lu_name)s<"
                        " volume id: >%(volume_id)s<,"
                        " k2xa: >%(k2xa)s<")

                LOG.error(msg %
                          {"lu_udid": lu_udid, "lu_name": lu_name,
                           "volume_id": volume["id"], "k2xa": k2xa.r(), })
        k2xa.log()

    def create_snapshot(self, snapshot):

        k2xa = K2_XA("create_snapshot")

        source_vol = self.db.volume_get(self._context, snapshot['volume_id'])

        if source_vol is None:
            msg = (_('ssp:'
                     ' during create_snapshot,'
                     ' cant find volume_id: >%s<') %
                   snapshot['volume_id'])
            raise exception.VolumeBackendAPIException(data=msg)

        ret, src_lu = self._get_and_check_lu(source_vol,
                                             "create_snapshot",
                                             1000,
                                             k2xa)
        (src_lu_udid, src_lu_name, src_lu_ssp_udid) = ret

        opts = self._get_lu_params(source_vol['volume_type_id'])
        try:
            tgt_lu = self._clone_lu(src_lu,
                                    snapshot['volume_size'],
                                    snapshot['name'],
                                    opts,
                                    k2xa)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<"), e)
                msg = (_("ssp:"
                         " failure during create_snapshot:"
                         " lu_udid: >%(src_lu_udid)s<"
                         " lu_name: >%(src_lu_name)s<"
                         " volume id: >%(source_vol_id)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"src_lu_udid": src_lu_udid,
                        "src_lu_name": src_lu_name,
                        "source_vol_id": source_vol["id"], "k2xa": k2xa.r(), })
                LOG.error(msg)
        k2xa.log()

    def delete_snapshot(self, snapshot):

        k2xa = K2_XA("delete_snapshot")

        lu_name = snapshot['name']
        lus = self._find_lu_by_name(lu_name)
        if len(lus) == 0:
            msg = (_("ssp:"
                     " during delete_snapshot,"
                     " couldnt find lu"
                     " with unit_name: >%s<") %
                   lu_name)
            raise exception.VolumeBackendAPIException(data=msg)
        if len(lus) > 1:
            msg = (_("ssp:"
                     " during delete_snapshot,"
                     " found too many lus"
                     " with unit_name: >%s<") %
                   lu_name)
            raise exception.VolumeBackendAPIException(data=msg)

        self._delete_lu(lus[0], k2xa)
        k2xa.log()

    def create_volume_from_snapshot(self, volume, snapshot):

        k2xa = K2_XA("create_volume_from_snapshot")

        tgt_volume_name = self._construct_name(volume)
        opts = self._get_lu_params(volume['volume_type_id'])

        try:
            (tgt_lu_udid, ssp_udid) = \
                self._clone_lu_by_name(snapshot['name'],
                                       snapshot['volume_size'],
                                       volume['size'],
                                       tgt_volume_name,
                                       opts,
                                       k2xa)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error("ssp: exception: >%s<", e)
                msg = (_("ssp:"
                         " error during create_volume_from_snapshot:"
                         " snapshot with name: >%(snapshot_name)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"snapshot_name": snapshot['name'], "k2xa": k2xa.r(), })
                LOG.error(msg)

        _update_restricted_metadata(volume['id'],
                                    tgt_lu_udid, tgt_volume_name,
                                    ssp_udid)
        k2xa.log()

    def create_cloned_volume(self, tgt_volume, src_volume):

        k2xa = K2_XA("create_cloned_volume")

        volume_type_id = tgt_volume.get('volume_type_id')
        if not volume_type_id:
            volume_type = volume_types.get_default_volume_type()
            volume_type_id = volume_type['id']
            tgt_volume['volume_type_id'] = volume_type_id
            #Update db to preserve volume_type
            self.db.volume_update(self._context, tgt_volume['id'],
                                  {'volume_type_id': volume_type_id})

        ret, src_lu = self._get_and_check_lu(
            src_volume,
            "create_cloned_volume",
            1000,
            k2xa)
        (src_lu_udid, src_lu_name, src_lu_ssp_udid) = ret

        opts = self._get_lu_params(volume_type_id,
                                   tgt_volume['id'])
        tgt_volume_name = self._construct_name(tgt_volume)
        try:
            tgt_lu_udid = \
                self._clone_lu(src_lu,
                               tgt_volume['size'],
                               tgt_volume_name,
                               opts=opts,
                               k2xa=k2xa)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<"), e)
                msg = (_("ssp: "
                         " error during create_cloned_volume:"
                         " src_lu_udid: >%(src_lu_udid)s<"
                         " src_lu_name: >%(src_lu_name)s<"
                         " volume id: >%(src_volume_id)s<,"
                         " k2xa: >%(k2xa)s<") %
                       {"src_lu_udid": src_lu_udid, "src_lu_name": src_lu_name,
                        "src_volume_id": src_volume["id"],
                        "k2xa": k2xa.r(), })
                LOG.error(msg)

        _update_restricted_metadata(tgt_volume['id'],
                                    tgt_lu_udid, tgt_volume_name,
                                    src_lu_ssp_udid)

        self._get_and_check_lu(tgt_volume,
                               "create_cloned_volume",
                               800,
                               k2xa)
        k2xa.log()

    def initialize_connection(self, volume, connector):

        k2xa = K2_XA("initialize_connection")

        ret, lu = self._get_and_check_lu(volume,
                                         "initialize_connection",
                                         1000,
                                         k2xa)
        (lu_udid, lu_name, lu_ssp_udid) = ret

        k2xa.log()

        return {'driver_volume_type': 'ibm_ssp',
                'data': {'target_discovered': True,
                         'UniqueDeviceID': lu_udid,
                         'UnitName': lu_name}
                }

    def terminate_connection(self, volume, connector, force=False, **kwargs):

        k2xa = K2_XA("terminate_connection")
        self._get_and_check_lu(volume,
                               "terminate_connection",
                               1000,
                               k2xa)
        k2xa.log()

    def get_volume_stats(self, refresh=False):
        """Get volume status.

        If we haven't gotten stats yet or 'refresh' is True,
        run update the stats first."""

        k2xa = K2_XA("get_volume_stats")

        if not self._stats or refresh:
            self._update_volume_status(k2xa)
            self._cluster_vios_check("get_volume_stats", k2xa)

        k2xa.log()
        LOG.debug(_('stats = %(stats)s') % {'stats': str(self._stats)})
        return self._stats
