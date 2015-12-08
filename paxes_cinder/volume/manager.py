# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import re
import uuid
import os
from signal import SIGTERM
from datetime import datetime
from oslo.config import cfg

import cinder.context
from cinder import exception
from paxes_cinder import exception as paxes_exception
from cinder import quota
from cinder import utils
from cinder.db import api as db_api
from cinder.image import glance
from cinder.openstack.common import excutils
from cinder.openstack.common import lockutils
from cinder.openstack.common import log as logging
from cinder.openstack.common import periodic_task
from cinder.openstack.common import timeutils
from paxes_cinder import _
from cinder import rpc
from cinder.openstack.common import processutils
from cinder.volume import manager
from cinder.volume import volume_types
import eventlet.greenthread as greenthread

from paxes_cinder.db import api as paxes_db
from paxes_cinder.volume import discovery_driver

RESTRICTED_METADATA_CONN_WWPN_KEY = 'connector_wwpn'
RESTRICTED_METADATA_CONN_HOST_KEY = 'connector_host'

QUOTAS = quota.QUOTAS
LOG = logging.getLogger(__name__)
CONF = cfg.CONF
CONF.import_opt('volume_driver', 'cinder.volume.manager')

volume_direct_access_manager_opts = [
    cfg.ListOpt('san_allowed_prefixes',
                default=['image-'],
                help='List of prefixes of SAN volume names under our control'),
    cfg.StrOpt('host_type',
               default=None,
               help='The Type of Storage Back-end'),
    cfg.StrOpt('host_uniqueid',
               default=None,
               help='The Back-end Unique ID'),
    cfg.StrOpt('host_display_name',
               default=None,
               help='The user display name'),
    cfg.IntOpt('numtries_during_init',
               default=2,
               help='Number of times to try if driver is initializing'),
    cfg.IntOpt('sleeptime_during_init',
               default=10,
               help='Number of seconds to sleep between retries if driver is'
               'initializing')
]

CONF.register_opts(volume_direct_access_manager_opts)
CONF.import_opt('quota_volumes', 'cinder.quota')
CONF.import_opt('quota_snapshots', 'cinder.quota')
CONF.import_opt('quota_gigabytes', 'cinder.quota')
CONF.import_opt('zoning_mode', 'cinder.volume.manager')


class DirectAccessWithBadPrefixException(exception.CinderException):
    message = _("Cannot perform direct SAN operation on disk with prefix "
                "%(prefix)s")


def retry_during_init(function, descr):
    for x in range(CONF.numtries_during_init):
        try:
            return function()
        except exception.DriverNotInitialized:
            if x >= (CONF.numtries_during_init - 1):
                raise
            LOG.info(_("Driver still initializing, wait..."))
            greenthread.sleep(CONF.sleeptime_during_init)
            LOG.info(_("Try again: %s") % descr)


def log_errors(manager, context, errors, metadata, is_volume_error,
               volume_id, broadcasts=None):
    """
    Constructs a dictionary by combining errors with metadata, and then
    updates the volume metadata associated with the specified volume_id

    Will also put the volume into the Error state if requested.
    """
    # Add in the user-specified metadata
    errors.update(metadata)

    # get the existing volume metadata and merge it with errors metadata.
    # Otherwise, volume_update will delete existing paxes boot
    # volume metadata.
    vol_metadata = manager.db.volume_metadata_get(context, volume_id)

    if vol_metadata:
        vol_metadata.update(errors)
    else:
        vol_metadata = errors
    # Prepare the update
    new_data = {'metadata': vol_metadata}

    if is_volume_error:
        new_data.update({'status': 'error'})

    # Update the database
    manager.db.volume_update(context, volume_id, new_data)

    anotifier = rpc.get_notifier('volume', volume_id)
    anotifier.info(
        context, 'volume.update.errors', dict(volume_id=volume_id))

    if broadcasts:
        for message in broadcasts:
            anotifier.error(context, 'cinder.volume.log', message)


def to_value(v):
    """
    Truncate strings to fit in 255 characters, because that is the maximum
    length of values in Volume metadata
    """
    if isinstance(v, basestring):
        return v[:255]
    else:
        return None


def build_metadata(e, prefix, volume_id):
    """
    Build a dictionary containing all the error information we can extract from
    the passed-in Exception 'e'.  The 'prefix' is appended to the key values
    that we create.
    """

    is_volume_error = False
    broadcasts = []

    # Parallel exceptions from zoning operations cover everything that went
    # wrong on all switches.  We know that they are user-friendly and so are
    # suitable candidates to be broadcast.
    if isinstance(e, paxes_exception.ZoneManagerParallel):
        for e2 in e.exceptions:
            # If a contained exception is a SwitchException, then it has
            # details of the switch with the error.
            if isinstance(e2, paxes_exception.FabricException):
                info = {'msg': _("Fabric {fabric_name} ({user}@{ip}:{port}): "
                                 "%(message)s") %
                        {'message': e2.msg},
                        'fabric_name': e2.descriptor.name,
                        'fabric_display_name': e2.descriptor.display_name,
                        'user': e2.descriptor.username,
                        'ip': e2.descriptor.ip,
                        'port': e2.descriptor.port}
            else:
                info = {'msg': _("%s") % e2}
            broadcasts.append(info)

    try:
        if isinstance(e, paxes_exception.SVCException):
            # SVCException objects contains lots of useful information that we
            # can report back to the user.
            info = {'msg': _("Storage Provider {storage_provider_hostname} "
                             "({user}@{ip}:{port}) {volume_id}: %(message)s") %
                    {'message': e.msg},
                    'storage_provider_hostname': e.descriptor.name,
                    'storage_provider_display_name': e.descriptor.display_name,
                    'user': e.descriptor.username,
                    'ip': e.descriptor.ip,
                    'port': e.descriptor.port,
                    'volume_id': volume_id}
            broadcasts.append(info)
            is_volume_error = e.error_volume

        if isinstance(e, processutils.ProcessExecutionError):
            # SVC Error CMMVC5753E
            # "The specified object does not exist or is not a suitable
            # candidate."
            # If we are doing a mkvdiskhostmap, then this error is produced if
            # either the host or the disk does not exist.  For our purposes,
            # where we create the host definition, I think that the most
            # user-friendly thing we can do is assume this is a case where a
            # disk has been deleted from underneath us.
            if "CMMVC5753E" in e.stderr and ("mkvdiskhostmap" in e.cmd or
                                             "lsvdisk" in e.cmd):
                e.description = "The volume no longer exists on the storage " \
                                "controller."

            # SVC Error CMMVC6071E
            # "The VDisk-to-host mapping was not created because the VDisk is
            # already mapped to a host."
            # If we are doing a mkvdiskhostmap, then this is caused when the
            # disk is already in use by a host.  If this relationship was
            # already known about by PowerVC, then we wouldn't have got this
            # far, so the most likely explanation is that the disk is mapped to
            # a host that is not managed by PowerVC.
            if "CMMVC6071E" in e.stderr and "mkvdiskhostmap" in e.cmd:
                e.description = _("The volume is already attached to another "
                                  "virtual server, possibly one that is not "
                                  "managed by PowerVC.")
            if "CMMVC5840E" in e.stderr and "rmvdisk" in e.cmd:
                e.description = _("The volume cannot be deleted because it is "
                                  "either mapped to a host or part of a "
                                  "flashcopy or remote copy operation.")

            info = {prefix + ' Failure, exit code ': e.exit_code,
                    prefix + ' Failure, stdout': to_value(e.stdout),
                    prefix + ' Failure, stderr': to_value(e.stderr),
                    prefix + ' Failure, failing command': to_value(e.cmd),
                    prefix + ' Failure description': to_value(e.description)
                    }

            if e.description:
                msg = _("%(error_prefix)s failure for volume {volume_id}: "
                        "%(error)s") % \
                    {'error_prefix': prefix,
                     'error': e.description}
            else:
                msg = _("%(error_prefix)s failure for volume {volume_id}."
                        "Command %(cmd)s, error %(error)s") % \
                    {'error_prefix': prefix,
                     'cmd': e.cmd,
                     'error': e.stderr}

            bc_info = {'msg': msg, 'volume_id': volume_id}
            broadcasts.append(bc_info)

        elif isinstance(e, exception.CinderException):
            msg = str(e.msg)
            missing_vdisk = False
            if "CMMVC5753E" in msg and ("mkvdiskhostmap" in msg or
                                        "lsvdisk" in msg):
                missing_vdisk = True
            elif re.search('vdisk [0-9]* does not exist', msg):
                missing_vdisk = True
            if missing_vdisk:
                is_volume_error = True
                message = ("The volume no longer exists on the storage "
                           "controller.")
                info = {prefix + ' Failure description': to_value(message)}
            else:
                info = {prefix + ' Failure description': msg[:255]}
        else:
            info = {prefix + ' Failure description': (_("%s") % e)[:255]}
    except AttributeError as e:
        # Something was not as we expected - never mind, we just stringify
        # the exception and use that as the description.
        info = {prefix + ' Failure description': (_("%s") % e)[:255]}
    return (info, is_volume_error, broadcasts)


class PowerVCVolumeManager(manager.VolumeManager):
    """
    The PowerVCVolumeManager is a subclass of the Volume Manager to provide
    any additional capabilities that are needed as part of the PowerVC
    product.  This includes the following capabilities:
        1) The ability to manage raw SAN disks that are not tracked by the
           Cinder Database, such as glance images or ephemeral volumes used
           for virtual server boot disks.
        2) The population of an entry in a new storage_node table created by
           PowerVC that will be used to store metric/status information for
           the Storage Provider, similar to the compute_node table in Nova

    Additional details on some of the specific implementation follows:

    However, we don't want to allow this service to delete arbitrary disks
    on the SAN that might not be owned by OpenStack.  To constrain possible
    damage, we only allow manipulation of disks whose names start with one
    of a set of prefixes, and these prefixes are specified in the
    configuration file using the san_allowed_prefixes option, e.g.:

      san_allowed_prefixes=glance-,nova-

    It is the responsibility of the caller (glance, nova...) to make sure
    that the user has the correct authority to manipulate the specific disks,
    and they should be careful to ensure that the disk name is not
    manipulatable by the user, e.g. in metadata.  For this reason, UUIDs make
    good postfixes for disk names.

    These functions are not exported through the cinder-api service; they are
    only available via RPC calls via volume_API.

    Example usage (from another service):

         from cinder.volume import rpcapi as vol_rpcapi
         msg = self.volume_rpcapi.make_msg('delete_san_disk',
                                           'disk_prefix'='glance-'
                                           'disk_postfix=glance_id)
         self.volume_rpcapi.call(context, msg)
    """

    def __init__(self, volume_driver=None,
                 service_name=None, *args, **kwargs):
        self.storage_node = None
        self.volume_chunk_map = dict()
        self.volume_chunk_counter = 0
        self.last_status_refresh = datetime.min
        self.default_volume_type_id = None
        self.first_storage_node_sync = True

        LOG.debug('volume_driver: %s' % CONF.volume_driver)
        super(PowerVCVolumeManager, self).__init__(
            volume_driver=CONF.volume_driver, *args, **kwargs)

    ########################################################
    #########  Storage Metadata Implementation     #########
    ########################################################

    # @lockutils.synchronized('storage_metadata', 'cinder-', external=True)
    def get_storage_metadata(self, context):
        try:
            metadata = self.driver.get_storage_metadata()
        except AttributeError:
            metadata = {}
        return metadata

    ########################################################
    #########  Default Volume Type Implementation  #########
    ########################################################
    # @lockutils.synchronized('default_volume_type', 'cinder-', external=True)
    def get_default_vol_type(self, context):
        volume_type = self.driver.get_default_vol_type()
        return volume_type

    ########################################################
    #########  Get Default Options Implementation  #########
    ########################################################
    def get_default_opts(self, context):
        options = self.driver._build_default_opts()
        return options

    ########################################################
    ######### Storage Node Insert Implementation  ##########
    ########################################################
    def _mask_deleting_volumes(self, context):
        """
        Mask all the volume in deleting state from parent's init_host()
        """
        volumes = self.db.volume_get_all_by_host(context, self.host)
        for vol in volumes:
            if vol['status'] == 'deleting':
                # change it to resume-deleting
                self.db.volume_update(context, vol['id'],
                                      {'status': 'resume-deleting'})

    def _unmask_deleting_volumes(self, context):
        """
        Unmask all the volume in deleting state from parent's init_host()
        """
        volumes = self.db.volume_get_all_by_host(context, self.host)
        volid_del = []
        for vol in volumes:
            if vol['status'] == 'resume-deleting':
                # change it to deleting
                self.db.volume_update(context, vol['id'],
                                      {'status': 'deleting'})
                volid_del.append(vol['id'])
        return volid_del

    def _init_host_delete_volumes(self, context, del_volids):
        """ worker thread to offload volume delete during
        init_host(), which resumes delete of any volumes that are
        still in deleting state. The volume delete will be handled
        sequentially.
        """
        for volid in del_volids:
            try:
                LOG.info(_("Resuming deletion of volume %s") % volid)
                self.delete_volume(context, volid)
            except Exception as ex:
                message = (_("Failed to delete volume %(volid)s during volume "
                             "service startup. Error: %(error)s") %
                           {'volid': volid,
                            'error': (_("%s") % ex)})
                LOG.error(message)
            # yield in case we have massive deletion during startup.
            greenthread.sleep(0)

    def _init_host_rollback_attach_volumes(self, context, att_volids):
        """ Workder thread to offload rollback of any volumes that are still
        in the attaching state during init_host(). The volume attaching
        rollback will be handled sequentially.
        """
        for volid in att_volids:
            LOG.info(_("Processing volume that was left in the attaching "
                       "state. Volume id: %(id)s") % dict(id=volid))
            self._volume_attach_rollback(context, volid)

    def _restricted_metadata_get_connector(self, context, volid):
        """ retrieve the saved connector information in the volume
        restricted metadata. If it return None, it means there is not
        validate connector saved during the transaction. VolumeNotFound
        exception may be thrown if no restricted metadata for the
        volume.
        """

        meta = paxes_db.volume_restricted_metadata_get(context, volid)
        connector = {}
        try:
            wwpnlist = map(lambda kv: kv[1] if
                           RESTRICTED_METADATA_CONN_WWPN_KEY in
                           kv[0] else None, meta.items())
            connector = {'host': meta[RESTRICTED_METADATA_CONN_HOST_KEY],
                         'wwpns': [x for x in wwpnlist if x],
                         'phy_to_virt_initiators': None}
        except Exception:
            connector = None

        return connector

    def _restrict_metadata_cleanup_connector(self, context, volid):
        """ remove the connector related info from restricted metadata"""
        try:
            metadata = paxes_db.volume_restricted_metadata_get(context,
                                                                 volid)
        except Exception:
            return
        # TODO: need to try DB2 SQL matching to delete all the
        # matching entries in one transaction. Should be something like
        # "connector_%" for the filter.
        for key, value in metadata.iteritems():
            if (RESTRICTED_METADATA_CONN_HOST_KEY in key or
                    RESTRICTED_METADATA_CONN_WWPN_KEY in key):
                paxes_db.volume_restricted_metadata_delete(
                    context, volid, key)

    def _restrict_metadata_save_connector(self, context, volume, connector):
        """ Update volume restricted metadata with connector once hostmap
        has been established during volume attach transaction. The multihost
        mapping for a single volume scenario is ignored here.
        "connector_host": <host> from connector
        "connector_wwpn_0: <wwpn>
        "connector_wwpn_1: <wwpn>
        ...
        """
        if (not connector or not connector.get("wwpns") or
                not volume or volume['status'] != 'attaching'):
            return
        # TODO: handle the multihost volume mapping for IVM. Currently
        # is it not handling the incomplete attach transaction during the
        # IVM LPM window.
        self._restrict_metadata_cleanup_connector(context, volume)
        metadata = {RESTRICTED_METADATA_CONN_HOST_KEY: connector.get('host')}
        index = 0
        for wwpn in connector['wwpns']:
            key = RESTRICTED_METADATA_CONN_WWPN_KEY + '_' + str(index)
            metadata[key] = wwpn
            index += 1
        paxes_db.volume_restricted_metadata_update_or_create(
            context, volume['id'], metadata)

    def _volume_attach_rollback(self, context, volid):
        connector = None
        try:
            connector = self._restricted_metadata_get_connector(context,
                                                                volid)
        except exception.VolumeNotFound:
            LOG.warn(_("_volume_attach_rollback: Volume %(id)s is missing "
                       "restricted metadata to recover the attaching state.") %
                     dict(id=volid))
        if connector is None:
            LOG.info(_("_volume_attach_rollback: No attach operation "
                       " to rollback for volume %(id)s") %
                     dict(id=volid))
        else:
            if not connector['wwpns']:
                # empty wwpns.
                LOG.warn(_("_volume_attach_rollback: Invalid connector "
                           "%(conn)s in volume %(id)s restrict metadata. "
                           "Rollback without termination") %
                         dict(conn=connector, id=volid))
            else:
                LOG.info(_("_volume_attach_rollback: Roll back attaching "
                           "state for volume %(id)s.") % dict(id=volid))
                try:
                    self.terminate_connection(context, volid, connector)
                    # remove the connector after rollback.
                    self._restrict_metadata_cleanup_connector(context, volid)
                except Exception as ex:
                    LOG.debug("_volume_attach_rollback: Failed to terminate "
                              "attach for volume %(id)s. Error: %(error)s" %
                              dict(id=volid, error=ex))
        message = ("The volume attach didn't finish successfully "
                   "before cinder service gets restarted or volume delete.")
        metadata = {'Attach Failure description':
                    to_value(message)}

        # volume status will be set log_errors
        log_errors(self, context, metadata, {}, False,
                   volid, broadcasts=None)
        self.db.volume_update(context, volid,
                              {'status': 'available'})
        LOG.info(_("_volume_attach_rollback: Finished. Volume %(id)s has "
                   "rolled back to available state.") % dict(id=volid))

    def _volumes_post_init_update(self, context):
        """
        Post init_host volume processing. For the volumes that have
        left in the transitional state, volume manager will try to
        clean up or reverse the state as much as possible.
        """
        volumes = self.db.volume_get_all_by_host(context, self.host)
        volid_del = []
        volid_att = []
        for vol in volumes:
            if vol['status'] == 'resume-deleting':
                # change it to pending-deleting
                self.db.volume_update(context, vol['id'],
                                      {'status': 'deleting'})
                volid_del.append(vol['id'])
            elif vol['status'] == 'attaching':
                # if the volume is in the attaching state, that means nova
                # didn't get successful return from cinder volume attach.
                # The BDM will not be updated with the connection_info.
                # It is not safe to set the volume to in-use state even
                # though the volume may has been mapped on storage controller.
                # Without connection information in BDM on Nova side, nova
                # won't know how to handle the attach volume.
                # PowerVC will save each successful initialize_connection into
                # volume restricted metadata, and clean it up at the
                # end of volume_attach. As long as we see volume in attaching
                # state and there is a left over connector, we know we
                # have an unfinished volume attach and terminate the connection
                # with the connector and roll back to the Available state.

                # change to error_attaching state to make sure no retry
                self.db.volume_update(context, vol['id'],
                                      {'status': 'error_attaching'})
                volid_att.append(vol['id'])
            elif vol['status'] == 'creating':
                # It is unknown to init_host() whether volume create request
                # is still pending to be consumed by volume service or it
                # actually failed before the service has been restarted.
                # Set it to error state. If volume create is still pending,
                # volume service will retry the create volume and it will
                # correct the state afterwards. Otherwise it is a true error
                # state.
                if not vol.get('source_volid', None):
                    # this is a volume create.
                    message = ("The volume create didn't finish successfully "
                               "before cinder service was restarted.")
                    metadata = {'Create Failure description':
                                to_value(message)}
                    broadcasts = None
                    # volume status will be set log_errors
                    log_errors(self, context, metadata, {}, True,
                               vol['id'], broadcasts=broadcasts)
                else:
                    # clone failure.
                    message = ("The volume clone from source volume %(id)s "
                               " didn't finish successfully before cinder "
                               "service gets restarted." %
                               dict(id=vol.get('source_volid')))
                    metadata = {'Create Failure description':
                                to_value(message)}
                    broadcasts = None
                    # volume status will be set log_errors
                    log_errors(self, context, metadata, {}, True,
                               vol['id'], broadcasts=broadcasts)
            elif vol['status'] == 'detaching':
                # The volume detach transaction didn't finish before
                # volume service gets restarted. And volume_detached()
                # function hasn't been invoked during the transaction.
                # There are several thing we can assume here:
                # 1. Nova BDM table entry for this attached volume hasn't
                #    been deleted.
                # 2. It is unknown in init_host() whether terminate_connection
                #    has been called or not with existing volume driver api.
                # 3. detach_volume may be still pending.
                # In order to get the volume back to a manageable state,
                # it is safe to set the volume state back to "in-use" and
                # user can retry another detach from Nova. If connection
                # has been termianted, there is no side effect to retry
                # terminate_connection.
                LOG.info(_("The volume detach didn't finish successfully "
                           "before cinder service was restarted. volume id: "
                           "%(id)s") % dict(id=vol['id']))
                message = ("The volume detach didn't finish successfully "
                           "before cinder service was restarted. Please try "
                           "again to detach the volume.")
                metadata = {'Detach Failure description': to_value(message)}
                log_errors(self, context, metadata, {}, False,
                           vol['id'], broadcasts=None)
                self.db.volume_update(context, vol['id'],
                                      {'status': 'in-use'})
            # extending state is not a long run transaction and
            # it is an synchronous call. It has a relatively small window
            # to be caught during cinder service restart. And it needs
            # code to remember the current size and desired size to roll
            # back transaction or roll forward. Will leave it as a risk
            # for now.

        return volid_del, volid_att

    def init_host(self):
        """Override Initialize Host to set the State to Error on Exception"""

        context = cinder.context.get_admin_context()
        self._mask_deleting_volumes(context)
        try:
            # cinder has zone manager which conflicts with current
            # paxes zone manager. Set zoning_mode to 'none' to prevent
            # cinder zone manager from being loaded.
            saved_zone_mode = self.configuration.safe_get('zoning_mode')
            self.configuration.local_conf.zoning_mode = 'none'
            super(PowerVCVolumeManager, self).init_host()
            if not self.driver.initialized:
                LOG.error(_('Unable to initialize host, driver is '
                            'uninitialized'))
                volumes = self.db.volume_get_all_by_host(context, self.host)
                if not volumes:
                    os.kill(os.getppid(), SIGTERM)
                    os.kill(os.getpid(), SIGTERM)
                driver_name = self.driver.__class__.__name__
                raise exception.DriverNotInitialized(driver=driver_name)
            # restore zoning_mode
            self.configuration.local_conf.zoning_mode = saved_zone_mode
            self.zonemanager = None
        except Exception:
            with excutils.save_and_reraise_exception():
                # If we got an exception, update the Storage Node to Error
                self._sync_storage_node(context, {}, 'error')
                self._unmask_deleting_volumes(context)

        LOG.info(_("update default quota class..."))
        self.set_volume_type_quota(context)
        LOG.info(_('Post init_host processing and update volume status.'))
        try:
            volids_del, volids_att = self._volumes_post_init_update(context)
        except Exception as ex:
            LOG.error(_("Error happened during post init_host volume "
                      "processing. Error: %s") % ex)

        if volids_att:
            LOG.info(_('Rollback volume still attaching during init_host: '
                       '%d volumes') % len(volids_att))
            greenthread.spawn(self._init_host_rollback_attach_volumes, context,
                              volids_att)
        if volids_del:
            LOG.info(_('Resume volume deletion during init_host: %d volumes')
                     % len(volids_del))
            greenthread.spawn(self._init_host_delete_volumes, context,
                              volids_del)

    def set_volume_type_quota(self, context, volume_type=None):
        """ Update the volume type based default quota, uses default
        volume type if vol_type_name is not specified."""
        if not volume_type:
            try:
                volume_type = self.get_default_vol_type(context)
            except Exception:
                vtn = CONF.default_volume_type
                volume_type = vtn.decode('utf-8') if vtn else vtn

        vol_type_quota = {}
        volumes_quota = "volumes_%s" % volume_type
        vol_type_quota[volumes_quota] = CONF.quota_volumes
        snapshots_quota = "snapshots_%s" % volume_type
        vol_type_quota[snapshots_quota] = CONF.quota_snapshots
        gigabytes_quota = "gigabytes_%s" % volume_type
        vol_type_quota[gigabytes_quota] = CONF.quota_gigabytes

        default_quota_class = db_api.quota_class_get_default(context)
        quota_class = default_quota_class.get('class_name', 'default')
        for key, value in vol_type_quota.iteritems():
            try:
                db_api.quota_class_update(context, quota_class, key, value)
            except exception.QuotaClassNotFound:
                db_api.quota_class_create(context, quota_class, key, value)

    def update_service_capabilities(self, capabilities):
        """Override update to populate the Storage Node in the Database"""
        context = cinder.context.get_admin_context()
        self.last_status_refresh = timeutils.utcnow()
        # Call the Parent class for the normal Service Capability Processing
        super(PowerVCVolumeManager,
              self).update_service_capabilities(capabilities)
        # Create/Update the Storage Node entry in the Database
        self._sync_storage_node(context, capabilities, 'running')

    @periodic_task.periodic_task
    def _refresh_driver_stats_if_needed(self, context):
        """Attempt to Refresh the Driver Status if the Parent hasn't"""
        # If the Parent already refreshed the Status in the last 5 minutes,
        # then we don't want to do anything here and just continue on
        if timeutils.is_older_than(self.last_status_refresh, 300):
            self._refresh_driver_stats(context)

    def _refresh_driver_stats(self, context):
        """Attempt to Refresh the Volume Statistics from the Driver"""
        try:
            self._report_driver_status(context)
        except Exception as exc:
            LOG.warn(_('Caught Exception Refreshing Driver Status: %s')
                     % exc)
            LOG.exception(exc)
            # If we got an exception, update the Storage Node to Error
            self._sync_storage_node(context, {}, 'error')

    def _sync_storage_node(self, ctxt, stats, state):
        """Override update to populate the Storage Node in the Database"""
        try:
            # First we want to convert the Volume Stats to a Storage Node
            values = self._build_storage_node_values(stats, self.host, state)
            # If we haven't cached the Storage Node yet, see if it exists
            if not self.storage_node:
                self.storage_node = \
                    paxes_db.storage_node_get_by_host(ctxt, self.host)
            create = self.storage_node is None
            changed = self._storage_node_changed(self.storage_node, values)
            # Notify that we are starting to create/update the Storage Node
            if create or changed or self.first_storage_node_sync:
                self._notify_storage_node_update(ctxt, values, 'start', create)
            # If the Storage Node doesn't exist in the DB, we need to create it
            if not self.storage_node:
                service = self._service_get_by_host(ctxt, self.host)
                # Only create the Storage Node if the Service already exists
                if service:
                    values['service_id'] = service['id']
                    self.storage_node = \
                        paxes_db.storage_node_create(ctxt, values)
            # Else the Storage Node is already in the DB, so just update it
            elif changed:
                self.storage_node = paxes_db.storage_node_update(
                    ctxt, self.storage_node['id'], values)
            # Notify that we are done creating/updating the Storage Node
            if create or changed or self.first_storage_node_sync:
                self._notify_storage_node_update(ctxt, values, 'end', create)
        except Exception as exc:
            LOG.warn(_('Caught Exception trying to update Storage Node in DB'))
            LOG.exception(exc)
        # Update to say we have Synchronized the Storage Node the First Time
        # We want to always send a Notification each time we Start in order
        # to account for Volume Type, etc being updated that aren't in the DB
        self.first_storage_node_sync = False

    def _notify_storage_node_update(self, context,
                                    values, postfix, creating):
        """Helper Method to Notify we are Creating/Updating Storage Node"""
        event_type = 'storage.node.create.'
        info = {'host': self.host, 'storage_hostname': self.host}
        info['host_display_name'] = CONF.host_display_name
        info['default_volume_type'] = self._get_default_volume_type_id(context)
        # If this is an update, we want to notify the caller of what we updated
        if not creating:
            event_type = 'storage.node.update.'
        # If the Storage Node was created, we can get the ID and Service ID
        if self.storage_node:
            info['storage_node_id'] = self.storage_node['id']
            info['service_id'] = self.storage_node['service_id']
            info.update(values)
        # Send the notification that we are Creating/Updating the Compute Node
        anotifier = rpc.get_notifier('volume', self.host)
        anotifier.info(context, event_type + postfix, info)

    def _get_default_volume_type_id(self, context):
        """Helper method to get the Identifier of the Default Volume Type"""
        # We will cache the ID of the Volume Type when we first retrieve it
        if self.default_volume_type_id is None:
            # Only retrieve it if the Volume Type Name is in the CONF file
            if CONF.default_volume_type is not None:
                try:
                    voltype = volume_types.get_volume_type_by_name(
                        context, CONF.default_volume_type.decode('utf-8'))
                    self.default_volume_type_id = voltype['id']
                # Log an exception if we couldn't retrieve the Volume Type
                except Exception as exc:
                    LOG.warn(_('Unable to retrieve Default Volume Type'))
                    LOG.exception(exc)
        return self.default_volume_type_id

    @staticmethod
    def _service_get_by_host(context, host):
        """Helper method to retrieve the Service instance from the DB."""
        try:
            return db_api.service_get_by_host_and_topic(
                context, host, cfg.CONF.volume_topic)
        except exception.ServiceNotFound:
            return None

    @staticmethod
    def _build_storage_node_values(volume_stats, host, state):
        """Helper method to construct the Node attribute to populate in DB."""
        stat_keys = ['total_capacity_gb', 'free_capacity_gb', 'volume_count']
        values = {'storage_hostname': host}
        values['backend_id'] = CONF.host_uniqueid
        values['backend_type'] = CONF.host_type
        values['backend_state'] = state
        for key in stat_keys:
            if volume_stats.get(key) is not None:
                values[key] = volume_stats.get(key)
        return values

    @staticmethod
    def _storage_node_changed(storage_node, values):
        """Helper method to see if a value really would change in the DB."""
        if storage_node is None:
            return True
        for key, val in values.iteritems():
            if storage_node.get(key) != val:
                return True
        return False

    ########################################################
    ######### Volume Direct-Access Implementation ##########
    ########################################################
    def _validate_disk_prefix(self, disk_prefix):
        """Helper method to check disk prefix against our allowed list."""
        if not (disk_prefix in cfg.CONF.san_allowed_prefixes):
            raise DirectAccessWithBadPrefixException(prefix=disk_prefix)

    @lockutils.synchronized('delete_san_disk', 'cinder-', external=True)
    def delete_san_disk(self, context, disk_prefix, disk_postfix):
        """Deletes the disk with the specified name from the SAN.
           The name is in two parts - disk_prefix is checked against the list
           of allowed prefixes, and if it passes, it is concatenated with
           disk_postfix and passed to the driver.
        """
        # Check that the disk has an allowed prefix.
        self._validate_disk_prefix(disk_prefix)

        volume_ref = {'name': disk_prefix + disk_postfix}

        try:
            LOG.debug(_("volume %s: removing export"), volume_ref['name'])
            self.driver.remove_export(context, volume_ref)
            LOG.debug(_("volume %s: deleting"), volume_ref['name'])
            self.driver.delete_volume(volume_ref)
        except exception.VolumeIsBusy:
            LOG.debug(_("volume %s: volume is busy"), volume_ref['name'])
            self.driver.ensure_export(context, volume_ref)
        except exception.VolumeBackendAPIException:
            LOG.debug(_("Fail to remove_export or delete_volume: %s" %
                        volume_ref['name']))
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.debug(_("Volume %s: deletion failed with exception ") %
                          volume_ref['name'])

        # not going to update DB since it is not a Cinder volume..
        self.publish_service_capabilities(context)

        # This space freed up is not tracked by Quotas.
        return True

    def create_volume(self, context, volume_id, request_spec=None,
                      filter_properties=None, allow_reschedule=True,
                      snapshot_id=None, image_id=None, source_volid=None):

        """
        1) Set the allow_reschedule option to be False, because it looks as if
        it isn't working quite right - we only have one storage controller
        anyway, and if reschedule is True, we see the volume go into the
        "Available" state after the reschedule, even if there was an error.
        2) Retry if the driver was initializing
        3) Refresh driver stats when we're done
        """
        try:
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.create_volume(context,
                                        volume_id,
                                        request_spec=request_spec,
                                        filter_properties=filter_properties,
                                        allow_reschedule=False,
                                        snapshot_id=snapshot_id,
                                        image_id=image_id,
                                        source_volid=source_volid)
            result = retry_during_init(f, 'create volume %s' % volume_id)
        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            with excutils.save_and_reraise_exception():
                missing_source = False
                # if there is a problem with the source volume, we need
                # to note that as well as the failure to create a new vol
                if source_volid and isinstance(e,
                   paxes_exception.SVCVdiskNotFoundException):
                    missing_volid = e.volume_id
                    if (missing_volid == source_volid):
                        missing_source = True
                        # log/update/notify regarding the source volume.
                        # For build_metadata, we still want to associate any
                        # notification messages with the new volume_id, even
                        # if it was the source volume that was in error.
                        (metadata, is_vol_err, broadcasts) = \
                            build_metadata(e, 'Clone', volume_id)
                        log_errors(self, context, metadata, {},
                                   True, source_volid,
                                   broadcasts=broadcasts)
                # TODO: add similar support for SnapshotNotFound?
                # log/update/notify regarding the new volume
                if missing_source:
                    message = ("The source volume no longer exists on the "
                               "storage controller.")
                    metadata = {'Create Failure description':
                                to_value(message)}
                    broadcasts = None
                else:
                    (metadata, is_vol_err, broadcasts) = \
                        build_metadata(e, 'Create', volume_id)
                log_errors(self, context, metadata, {}, True,
                           volume_id, broadcasts=broadcasts)

        # Make sure to refresh Capacity Statistics after the Volume Creation
        self._refresh_driver_stats(cinder.context.get_admin_context())
        return result

    def delete_volume(self, context, volume_id, unmanage_only=False):
        """
        Simple wrapper for parent delete_volume method, so we can a) prevent
        delete of image volumes and b) catch exceptions and log them in the
        volume metadata.
        """
        image = None
        metadata = None
        try:
            # Don't allow delete for image volumes unless that image no
            # longer exists
            metadata = self.db.volume_metadata_get(context, volume_id)
            if metadata and ('is_image_volume' in metadata and
                             bool(metadata['is_image_volume'])):
                image_service, image_id = \
                    glance.get_remote_image_service(context,
                                                    metadata['image_id'])
                try:
                    image = image_service.show(context.elevated(), image_id)
                except exception.ImageNotFound:
                    pass  # this is actually what we want here
        except Exception as e:
            LOG.exception(_('failed checking whether \
                             volume %(vol_id)s backs an image,'
                            ' metadata=%(mdata)s')
                          % dict(vol_id=volume_id,
                                 mdata=metadata))

        if image is not None and image.get('status') != 'deleted':
            self.db.volume_update(context, volume_id,
                                  {'status': 'available'})
            message = "Cannot delete image-backing volume"
            metadata = {'Delete Failure description': to_value(message)}
            log_errors(self, context, metadata, {}, False, volume_id)
            return False
#            raise exception.InvalidVolume(reason=message)

        try:
            connector = None
            try:
                connector = self._restricted_metadata_get_connector(context,
                                                                    volume_id)
            except Exception:
                pass
            if connector:
                # There are unfinished volume attach transaction.
                # the nova compute manager will not save the connector
                # until reserve_volume->initialize_connection->volume_attach
                # flow is done. Then change from attaching to in-use.
                # If the instance delete request comes in the middle of this
                # attach flow, the nova compute clean up function will
                # unreserve the volume to available since  the volume
                # hasn't been attached and there is no information available
                # to detach. Fortunately, paxes has transaction for
                # attach process. We can safely terminate the connection
                # during volume delete if there is any outstanding attach
                # transaction. Otherwise, volume delete will fail with SVC
                # exception due to existing host mapping. zone will be
                # cleaned up as well during roll back.
                LOG.warn(_("volume %(volid)s has unfinished attach "
                           "transaction. Rolling back before deleting "
                           "the volume.") % dict(volid=volume_id))
                self._volume_attach_rollback(context, volume_id)

            # Call the method in our superclass
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.delete_volume(
                context, volume_id, unmanage_only=unmanage_only)
            result = retry_during_init(f, 'delete volume %s' % volume_id)
        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            # that we caught.
            with excutils.save_and_reraise_exception():
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(e, 'Delete', volume_id)
                log_errors(self, context, metadata, {}, is_volume_error,
                           volume_id, broadcasts=broadcasts)

        # Make sure to refresh Capacity Statistics after the Volume Deletion
        self._refresh_driver_stats(cinder.context.get_admin_context())
        return result

    def ibm_extend_volume(self, context, volume, new_size):
        volume_id = volume['id']
        volume_ref = self.db.volume_get(context, volume['id'])
        size_increase = (int(new_size)) - volume['size']

        anotifier = rpc.get_notifier('volume', self.host)
        anotifier.info(
            context, 'volume.extend.start', dict(volume_id=volume_id))

        try:
            reservations = QUOTAS.reserve(context, gigabytes=+size_increase)
        except exception.OverQuota as exc:
            overs = exc.kwargs['overs']
            usages = exc.kwargs['usages']
            quotas = exc.kwargs['quotas']

            def _consumed(name):
                return (usages[name]['reserved'] + usages[name]['in_use'])

            # not setting the volume to error as volume not set to extending
            if 'gigabytes' in overs:
                msg = _("Quota exceeded for %(s_pid)s, "
                        "tried to extend volume by "
                        "%(s_size)sG, (%(d_consumed)dG of %(d_quota)dG "
                        "already consumed)")
                LOG.warn(msg % {'s_pid': context.project_id,
                                's_size': size_increase,
                                'd_consumed': _consumed('gigabytes'),
                                'd_quota': quotas['gigabytes']})
                raise exception.VolumeSizeExceedsAvailableQuota()

        self.db.volume_update(context, volume_id, {'status': 'extending'})

        try:
            f = lambda: self._ibm_extend_volume(volume_ref, new_size)
            retry_during_init(f, 'ibm extend volume %s' % volume_id)
            anotifier = rpc.get_notifier('volume', self.host)
            anotifier.info(
                context, 'volume.extend.end', dict(volume_id=volume_id))
        except Exception as ex:
            try:
                if isinstance(ex,
                              paxes_exception.PVCExpendvdiskFCMapException):
                    # he action failed because the virtual
                    # disk (VDisk) is part of a FlashCopy mapping
                    # no change will be made to the boot volume
                    self.db.volume_update(context, volume_id,
                                          {'status': 'in-use'})
                    raise ex
                elif isinstance(ex, processutils.ProcessExecutionError):
                    if ("CMMVC5860E" in ex.stderr or
                        # CMMVC5860E : The action failed because there were
                        # not enough extents in the managed disk group
                        "CMMVC6973E" in ex.stderr or
                        # CMMVC6973E: The command cannot be initiated
                        # because the maximum number of extents for a VDisk
                        # would be exceeded.
                            "CMMVC6541E" in ex.stderr):
                        # The task cannot be initiated because the virtual
                        # capacity that you have requested for the VDisk
                        # is larger than the maximum capacity that is
                        # supported for the extent size.

                        # There is no change has been made. Just exceeds
                        # size limit.
                        self.db.volume_update(context, volume_id,
                                              {'status': 'in-use'})
                        ex_args = {'host': self.host,
                                   'volume_id': volume_id}
                        raise paxes_exception.\
                            PVCExpendvdiskCapacityException(**ex_args)
                # if trying to extend volume that doesn't support resize
                # and it is attached,  just restore the in-use state.
                # And log the NotImplementedError in the volume metadata.
                elif isinstance(ex, NotImplementedError):
                    self.db.volume_update(context, volume_id,
                                          {'status': 'in-use'})
                    msg = _("The host %(hostid)s for boot volume %(volid)s "
                            " does not support extend volume.")
                    LOG.warn(msg % {'volid': volume_id,
                                    'hostid': self.host})
                    raise NotImplementedError(msg %
                                              {'volid': volume_id,
                                               'hostid': self.host})

                # real volume error state for all the other cases
                # put the volume in error state.
                self.db.volume_update(context, volume_id,
                                      {'status': 'error_extending'})
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(ex, 'Extending volume', volume_id)
                # volume status has been set to error state, don't overwrite
                log_errors(self, context, metadata, {}, False,
                           volume_id, broadcasts=broadcasts)
                raise ex
            finally:
                QUOTAS.rollback(context, reservations)

        self.db.volume_update(context, volume_id, {'size': new_size})
        QUOTAS.commit(context, reservations)
        self.db.volume_update(context, volume_id, {'status': 'in-use'})
        # Make sure to refresh Capacity Statistics after the Volume Extension
        self._refresh_driver_stats(cinder.context.get_admin_context())

    def _ibm_extend_volume(self, volume_ref, new_size):
        utils.require_driver_initialized(self.driver)
        self.driver.extend_volume(volume_ref, new_size)

    def initialize_connection(self, context, volume_id, connector):
        """
        Simple wrapper for parent initialize_connection method, so we can catch
        exceptions and log them in the volume metadata.
        """
        anotifier = rpc.get_notifier('volume', self.host)
        anotifier.info(
            context, 'volume.attach.start', dict(volume_id=volume_id))

        try:
            # Call the method in our superclass
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.initialize_connection(context, volume_id, connector)
            info = retry_during_init(f, 'initialize connection %s' % volume_id)

            # If we have a successful attach, then we clear out any prior
            # errors.
            self._clear_errors(context, volume_id, 'Attach')
            # volume attach transaction started successfully. Save
            # the connector in the restrict metadata. It will be
            # cleaned at the end of attach_volume.
            volume = self.db.volume_get(context, volume_id)
            volume_meta = self.db.volume_metadata_get(context,volume_id)
            if 'data' in info and volume_meta.has_key('is_boot_volume'):
                info['data']['is_boot_volume'] = volume_meta['is_boot_volume']
            self._restrict_metadata_save_connector(context, volume, connector)
            LOG.info(_("Start attach transaction for volume %(id)s.") %
                     dict(id=volume_id))
            return info

        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            # that we caught.
            with excutils.save_and_reraise_exception():
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(e, 'Attach', volume_id)
                extra_metadata = {'Attach Failure, connection request':
                                  str(connector)[:255]}
                log_errors(self, context, metadata, extra_metadata,
                           is_volume_error, volume_id, broadcasts=broadcasts)

    def terminate_connection(self, context, volume_id, connector, force=False):
        """
        Simple wrapper for parent terminate_connection method, so we can catch
        exceptions and log them in the volume metadata.
        """
        anotifier = rpc.get_notifier('volume', self.host)
        anotifier.info(
            context, 'volume.detach.start', dict(volume_id=volume_id))

        try:
            # Call the method in our superclass
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.terminate_connection(context, volume_id, connector,
                                               force=force)
            info = retry_during_init(f, 'terminate connection %s' % volume_id)
            LOG.debug(_("Driver returned %s") % info)

            # If we have a successful detach, then we clear out any prior
            # errors
            self._clear_errors(context, volume_id, 'Detach')

            # terminate_connection doesn't return any data.
            return None
        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            # that we caught.
            with excutils.save_and_reraise_exception():
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(e, 'Detach', volume_id)
                extra_metadata = {'Detach Failure, connection request':
                                  str(connector)[:255]}
                log_errors(self, context, metadata, extra_metadata,
                           is_volume_error, volume_id, broadcasts=broadcasts)

    def attach_volume(self, context, volume_id, instance_uuid, host_name,
                      mountpoint, mode):
        """
        Simple wrapper for parent attach_volume method, so we can add
        a messaging notification.
        """
        try:
            # Call the method in our superclass
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.attach_volume(context, volume_id, instance_uuid,
                                        host_name, mountpoint, mode)
            result = retry_during_init(f, 'attach volume %s' % volume_id)
            # The volume attach transaction finished successfully. Clean
            # up the saved connector in the restricted metadata.
            LOG.info(_("Successfully attached the volume %(id)s. Clean up "
                       "transaction.") % dict(id=volume_id))
            self._restrict_metadata_cleanup_connector(context, volume_id)
            anotifier = rpc.get_notifier('volume', host_name)
            anotifier.info(
                context, 'volume.attach.end',
                dict(volume_id=volume_id, instance_id=instance_uuid,
                     host_name=host_name, mountpoint=mountpoint, mode=mode))

        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            # that we caught.
            with excutils.save_and_reraise_exception():
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(e, 'Attach', volume_id)
                extra_metadata = {
                    'Attach Failure, db update args':
                    'Volume %s, Server %s' % (volume_id, instance_uuid)}
                log_errors(self, context, metadata, extra_metadata,
                           is_volume_error, volume_id, broadcasts=broadcasts)

        return result

    def detach_volume(self, context, volume_id):
        """
        Simple wrapper for parent detach_volume method, so we can add
        a messaging notification.
        """
        try:
            # Call the method in our superclass
            s = super(PowerVCVolumeManager, self)
            f = lambda: s.detach_volume(context, volume_id)
            retry_during_init(f, 'detach volume %s' % volume_id)

            anotifier = rpc.get_notifier('volume', self.host)
            anotifier.info(
                context, 'volume.detach.end', dict(volume_id=volume_id))
        except Exception as e:
            # Log the error in Volume metadata, then re-raise the exception
            # that we caught.
            with excutils.save_and_reraise_exception():
                (metadata, is_volume_error, broadcasts) = \
                    build_metadata(e, 'Detach', volume_id)
                extra_metadata = {
                    'Detach Failure, db update args': 'Volume %s' % volume_id}
                log_errors(self, context, metadata, extra_metadata,
                           is_volume_error, volume_id, broadcasts=broadcasts)

        try:
            volume = self.db.volume_get(context, volume_id)
            self.driver.check_volume_health(volume)
        except Exception as e:
            (metadata, is_volume_error, broadcasts) = \
                build_metadata(e, 'Detach', volume_id)
            extra_metadata = {
                'Detach Failure, db update args': 'Volume %s' % volume_id}
            log_errors(self, context, metadata, extra_metadata,
                       is_volume_error, volume_id, broadcasts=broadcasts)

    ########################################################
    #########   Volume Discovery Implementation   ##########
    ########################################################
    def discover_volumes(self, context, filters=None):
        """Returns a list of all of the Volumes that exist on the Host"""
        # Currently we won't throw an exception if it isn't a Discover Driver
        if not isinstance(self.driver, discovery_driver.VolumeDiscoveryDriver):
            drvclass = self.driver.__class__.__name__
            LOG.warn(_('Driver %s does not implement Discover Driver')
                     % drvclass)
            return {'identifier': None, 'volumes': [], 'chunking': False}
        # Call the Volume Discovery Driver to get a list of existing Volumes
        all_volumes = self._discover_volumes(context, filters)
        # We need to modify the Instances returned from the Driver slightly
        self._manipulate_driver_volumes(all_volumes, False)
        # Break up the list of Volumes to a set of Chunks to be returned
        identifier = self._persist_volumes_chunks(all_volumes)
        # Return the first chunk of persisted volumes to the caller
        return self.get_next_volumes_chunk(context, identifier)

    def query_volumes(self, context, volume_ids,
                      extra_parms={}, allow_unsupported=False):
        """Returns details about the Volumes that were requested"""
        return_all = '*all' in volume_ids
        match_volumes, query_volumes = (list(), list())
        # First we need to figure out what Volumes really exist on the Host
        filters = self._parse_host_filters(extra_parms)
        all_volumes = self._discover_volumes(context, filters)
        uuid_map = dict([(vol_id, '') for vol_id in volume_ids])
        # Loop through each Volumes on the Host, seeing if we should query
        for volume in all_volumes:
            # See if they requested all instances or this specific one
            if return_all or volume['uuid'] in uuid_map:
                support = volume.get('support', {})
                supported = support.get('status', 'supported')
                # If this is managed, then no need to do a query, just return
                if volume.get('managed') is True:
                    volume.pop('connection_info', None)
                    match_volumes.append(volume)
                # If this isn't supported and no override, just return it
                elif not allow_unsupported and supported != 'supported':
                    volume.pop('connection_info', None)
                    match_volumes.append(volume)
                # Otherwise it is supported/un-managed and a match so query
                else:
                    volume.pop('support', volume.pop('managed', None))
                    query_volumes.append(volume)
        # Only worth calling the Driver if some VM's exist on the System
        if len(query_volumes) > 0:
            mark_boot = extra_parms.get('has_boot', {})
            server_info = extra_parms.get('server_info', {})
            volumes = self.driver.query_volumes(
                context, query_volumes, server_info, mark_boot)
            match_volumes.extend(volumes)
        # We need to modify the Volume returned from the Driver slightly
        self._manipulate_driver_volumes(match_volumes, True)
        # Break up the list of Volumes to a set of Chunks to be returned
        identifier = self._persist_volumes_chunks(match_volumes)
        # Return the first chunk of persisted volumes to the caller
        return self.get_next_volumes_chunk(context, identifier)

    @lockutils.synchronized('volume_chunking', 'cinder-')
    def get_next_volumes_chunk(self, context, identifier):
        """Provides Chunking of Volume Lists to avoid QPID Limits"""
        volume_chunks = self.volume_chunk_map.get(identifier)
        # If the Identifier doesn't exist, we will just return an empty list
        if volume_chunks is None:
            return dict(identifier=identifier, volumes=[], chunking=False)
        # If this is the last chunk (or no chunking), just return that list
        if len(volume_chunks) == 1:
            self.volume_chunk_map.pop(identifier, None)
            return dict(identifier=identifier,
                        volumes=volume_chunks[0], chunking=False)
        # Otherwise return the first chunk and say that there are more left
        self.volume_chunk_map[identifier] = volume_chunks[1:]
        return dict(identifier=identifier,
                    volumes=volume_chunks[0], chunking=True)

    def verify_host_running(self, context):
        """Verifies the cinder-volume service for the Host is running"""
        return True

    def _discover_volumes(self, context, filters=None):
        """Helper Method to list all of the Volumes that exist on the Host"""
        # Call the Volume Discovery Driver to get a list of existing Volumes
        drv_volumes = self.driver.discover_volumes(context, filters)
        # Generate the UUID's for the Volumes and determine which are Managed
        self._generate_volume_uuids(context, drv_volumes, filters)
        return drv_volumes

    @lockutils.synchronized('volume_chunking', 'cinder-')
    def _persist_volumes_chunks(self, volumes):
        """Internal Helper method to generate the UUID's for the Volumes"""
        current_len = 0
        current_list, volume_chunks = (list(), list())
        # First get an identifier to be used to reference this chunking
        identifier = str(self.volume_chunk_counter)
        self.volume_chunk_counter = self.volume_chunk_counter + 1
        # Loop through each volume, breaking it up into chunks based on size
        while len(volumes) > 0:
            volume = volumes.pop(0)
            volume_len = len(str(volume))
            # If we could possibly go over the 64K Message size, break up
            if len(current_list) > 0 and (current_len + volume_len) > 40000:
                volume_chunks.append(current_list)
                current_list = []
                current_len = 0
            # Add this volume to the current chunk that is going to be returned
            current_len = current_len + volume_len
            current_list.append(volume)
        # Add the final chunk to the overall set of chunks for the volume list
        volume_chunks.append(current_list)
        self.volume_chunk_map[identifier] = volume_chunks
        return identifier

    def _manipulate_driver_volumes(self, drv_volumes, query):
        """Internal Helper method to modify attributes on the Volumes"""
        for volume in drv_volumes:
            volume['id'] = volume.pop('uuid', None)
            if query:
                volume.pop('storage_pool', None)
            else:
                volume.pop('restricted_metadata', None)
                volume.pop('connection_info', None)

    def _generate_volume_uuids(self, context, drv_volumes, filters):
        """Internal Helper method to generate the UUID's for the Volumes"""
        uuid_map, provid_map = (dict(), dict())
        db_volumes = self.db.volume_get_all_by_host(context, self.host)
        # Loop through DB Volumes, construct UUID/VDisk Maps for lookup
        for db_volume in db_volumes:
            volid = db_volume['id']
            uuid_map[volid] = db_volume
            # Try to retrieve the Metadata out of the DB for the VOlume
            result = paxes_db.volume_restricted_metadata_get(context, volid)
            prov_id = self._get_provider_identifier(result)
            if prov_id is not None:
                provid_map[prov_id] = db_volume
        # Loop through the Volumes generating UUID's for any that need one
        for drv_vol in drv_volumes:
            managed = False
            # If the Driver returned UUID, see if the Volume is managed
            if drv_vol.get('uuid') is not None:
                db_vol = uuid_map.get(drv_vol['uuid'])
                if db_vol is not None:
                    drv_vol['name'] = db_vol['display_name']
                    inst_uuid = db_vol.get('instance_uuid')
                    # Mark it as managed unless this is an Attach and it is not
                    managed = not filters or inst_uuid is not None
            # If the UUID isn't set, do a secondary lookup to see if it exists
            else:
                metadata = drv_vol.get('restricted_metadata')
                prov_id = self._get_provider_identifier(metadata, '!')
                db_vol = provid_map.get(prov_id)
                # If an existing match based on provider id, use that UUID
                if db_vol is not None:
                    drv_vol['uuid'] = db_vol['id']
                    drv_vol['name'] = db_vol['display_name']
                    inst_uuid = db_vol.get('instance_uuid')
                    # Mark it as managed unless this is an Attach and it is not
                    managed = not filters or inst_uuid is not None
                # Otherwise it isn't managed, so we need to generate one
                else:
                    namesp = uuid.UUID('a0dd4880-6115-39d6-b26b-77df18fe749f')
                    namestr = self._get_unique_volume_str(drv_vol, prov_id)
                    drv_vol['uuid'] = str(uuid.uuid3(namesp, namestr))
            # Set the Managed attribute based on what we determined earlier
            drv_vol['managed'] = managed

    def _parse_host_filters(self, extra_parms):
        """Internal Helper Method to parse Host Refs from the Server Info"""
        host_refs = list()
        # If there were any Filters provided, just return those filters
        if extra_parms.get('filters') is not None:
            return extra_parms['filters']
        # If there weren't any attached servers, nothing to filter on
        if not extra_parms.get('server_info'):
            return None
        # Loop through each of the Servers provided, parsing out the Volumes
        for server in extra_parms['server_info'].values():
            volumes = server.get('volumes', [])
            # Loop through the list of WWPN's and UniqueDeviceID's identifiers
            for volume in volumes:
                if volume.get('unique_device_id') is not None:
                    host_refs.append(volume['unique_device_id'])
                if volume.get('wwpns') is not None:
                    host_refs = host_refs + volume['wwpns']
        return dict(host_refs=host_refs)

    def _get_unique_volume_str(self, volume, prov_id):
        """Internal Helper method to create a unique string for the volume"""
        volume_name = volume.get('name', '')
        return "ibm-paxes://volume/host='%s',id='%s',name='%s'" % \
            (self.host, str(prov_id), str(volume_name))

    @staticmethod
    def _get_provider_identifier(restricted_metadata, default=None):
        """Internal Helper method to parse the provider id out of meta-data"""
        if restricted_metadata is None:
            return default
        id_keys = ['lu_udid', 'vdisk_uid']
        # Try to find the Identifier attribute out of the Meta-data
        for key, val in restricted_metadata.iteritems():
            if key in id_keys:
                return val
        return default

    def _clear_errors(self, context, volume_id, prefix):
        """
        Removes the metadata keys that we added when an error occurred.
        We use this to clear out errors if we subsequently perform a
        successful operation
        """
        keys_to_delete = [prefix + ' Failure, exit code ',
                          prefix + ' Failure, stdout',
                          prefix + ' Failure, stderr',
                          prefix + ' Failure, failing command',
                          prefix + ' Failure description']

        # For attach failures we added this additional piece of information
        # that we should clean up.
        if prefix == 'Attach':
            keys_to_delete.append('Attach Failure, connection request')

        vol_metadata = self.db.volume_metadata_get(context, volume_id)

        if vol_metadata:
            # Remove all keys, if they exist
            for key in keys_to_delete:
                vol_metadata.pop(key, None)

            # Prepare the update
            new_data = {'metadata': vol_metadata}

            # Update the database
            self.db.volume_update(context, volume_id, new_data)

    def exist_volumes(self, context):
        lvs = self.driver.exist_volumes()
        return lvs
