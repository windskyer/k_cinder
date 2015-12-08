# =================================================================
# =================================================================
"""
Volume driver for Shared Storage Pools.
"""

from cinder.openstack.common import log as logging
from cinder import exception
from cinder.openstack.common import excutils
import math

from paxes_cinder.volume import discovery_driver
from paxes_cinder.volume.drivers.ssp import ssp
from paxes_cinder.volume.drivers.ssp.ssp import K2_XA
from paxes_cinder.k2aclient.v1 import k2uom

LOG = logging.getLogger(__name__)


class SSPProductDriver(ssp.SSPDriver, discovery_driver.VolumeDiscoveryDriver):

    def __init__(self, *args, **kwargs):
        super(SSPProductDriver, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_connection_info(unit_name, unique_device_id):
        """Get connection_info for a discover lu"""
        data = dict(access_mode='rw', qos_spec=None, target_discovered=True,
                    UnitName=unit_name, UniqueDeviceID=unique_device_id)
        connector = {'connection-type': 'ibm_ssp', 'connector': None}
        return dict(driver_volume_type='ibm_ssp', data=data,
                    volume_connector=connector)

    def _get_mapped_lus(self, k2xa):
        mapped_lus = []
        # refresh cached cluster
        try:
            self._cluster = self._k2aclient.cluster.refresh(self._cluster,
                                                            xa=k2xa.ri())
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<") % e)
                msg = _("ssp:"
                        " while discovering mapped LUs,"
                        " failed to refresh cluster"
                        " with cluster_id: >%(self._cluster.id)s<,"
                        " k2xa: >%(k2xa)s<")
                LOG.error(msg % {"self._cluster.id": self._cluster.id,
                                 "k2xa": k2xa.r(), })

        for node in self._cluster.node.node:
            if not node.virtual_io_server:
                LOG.info(_("Node >%s< has no virtual_io_server. "
                           "Skipping.") % str(node.__dict__))
                continue
            node_parts = node.virtual_io_server.split('/')
            ms_id = node_parts[-3]
            vios_id = node_parts[-1]
            try:
                vios = self._k2aclient.\
                    virtualioserver.get(ms_id,
                                        vios_id,
                                        xag=["ViosSCSIMapping"],
                                        xa=k2xa.ri())
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    LOG.error(_("ssp: exception: >%s<") % e)
                    msg = _("ssp:"
                            " while discovering mapped LUs,"
                            " in cluster with"
                            " cluster_id: >%(self._cluster.id)s<"
                            " failed to retrieve vios"
                            " with managedsystem_id: >%(ms_id)s< and"
                            " virtualioserver_id: >%(vios_id)s<,"
                            " k2xa: >%(k2xa)s<")
                    LOG.error(msg %
                              {"self._cluster.id": self._cluster.id,
                               "ms_id": ms_id, "vios_id": vios_id,
                               "k2xa": k2xa.r(), })
            for vsm in vios.virtual_scsi_mappings.virtual_scsi_mapping:
                if ((vsm.storage is not None and
                     isinstance(vsm.storage, k2uom.LogicalUnit) and
                     vsm.storage.logical_unit_type == "VirtualIO_Disk")):
                    mapped_lus.append(vsm.storage.unique_device_id)
        return set(mapped_lus)

    def get_storage_metadata(self):
        """ Return the driver metadata for the storage_metadata API"""

        k2xa = K2_XA("get_storage_metadata")

        volume_pools = []
        # If stats haven't been retrieved yet, retrieve them
        if not self._stats:
            self._update_volume_status(k2xa)
        ssp_stats = self._stats
        # Fall back to a simple set of info from _stats. First check if
        # any data populated.
        if ssp_stats and 'total_capacity_gb' in ssp_stats:
            total_gb = str(ssp_stats['total_capacity_gb']) + "GB"
            free_gb = str(ssp_stats['free_capacity_gb']) + "GB"
            used_gb = str(ssp_stats['allocated_capacity_gb']) + "GB"
            ssp_meta_dict = {'name': ssp_stats['pool_name'],
                             'capacity': total_gb, 'free_capacity': free_gb,
                             'used_capacity': used_gb,
                             'id': ssp_stats['udid']}
        else:
            # apparently there is trouble w/ the driver
            msg = _("No volume statistics available,"
                    " either driver has not been initialized"
                    " or there is a problem w/ the"
                    " driver, check cinder logs.")
            LOG.error(msg)
            raise exception.VolumeBackendAPIException(data=msg)

        volume_pools.append(ssp_meta_dict)
        k2xa.log()
        LOG.debug("Returning storage_metadata for SSP: >%s<" % volume_pools)
        return {'volume_pools': volume_pools}

    def discover_volumes(self, context, filters=None):
        """Returns a list of all of the Volumes that exist on the Provider"""

        k2xa = K2_XA("discover_volumes")

        volumes = []

        #Get the UniqueDeviceID values out of the Filter criteria
        filter_set = None
        if filters is not None and 'host_refs' in filters:
            filter_set = [unique_id for unique_id in filters['host_refs']]

        # refresh cache
        try:
            self._ssp = self._k2aclient.sharedstoragepool.refresh(self._ssp,
                                                                  xa=k2xa.ri())
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_("ssp: exception: >%s<") % e)
                msg = _("ssp:"
                        " while discovering volumes,"
                        " failed to refresh shared storage pool"
                        " with ssp_id: >%(self._ssp.id)s<,"
                        " k2xa: >%(k2xa)s<")
                LOG.error(msg %
                          {"self._ssp.id": self._ssp.id, "k2xa": k2xa.r(), })

        lus = self._ssp.logical_units
        mapped_lus = self._get_mapped_lus(k2xa)
        #loop on all LUs in the SSP
        for lu in lus.logical_unit:
            #Return a Dictionary for each of Volumes/LU's found
            volume = dict(name=lu.unit_name, status='available',
                          size=int(math.ceil(float(lu.unit_capacity))),
                          support=dict(status='supported'),
                          storage_pool=self._ssp.storage_pool_name)
            volume['restricted_metadata'] = {
                ssp.RESTRICTED_METADATA_LU_UDID_KEY: lu.unique_device_id,
                ssp.RESTRICTED_METADATA_LU_NAME_KEY: lu.unit_name,
                ssp.RESTRICTED_METADATA_LU_SSP_UDID: self._ssp.unique_device_id
            }

            if lu.unique_device_id in mapped_lus:
                volume['status'] = 'in-use'
                volume['support'] = {
                    "status": "not_supported",
                    "reasons": [_(
                        'This volume is not a candidate for management '
                        'because it is already attached to a virtual '
                        'machine.  To manage this volume with P, '
                        'you must bring the virtual machine under '
                        'management.  Select to manage the virtual '
                        'machine that has the volume attached.  The '
                        'attached volume will be automatically included '
                        'for management.')
                    ]
                }
                msg = _("ssp:"
                        " during Logical Unit discovery,"
                        " ssp_id: >%(ssp_id)s<,"
                        " lu_unique_device_id: >%(lu_unique_device_id)s<,"
                        " lu_unit_name: >%(lu_unit_name)s<,"
                        " volume is in use and not available for management,"
                        " k2xa: >%(k2xa)s<")
                LOG.info(msg % {"ssp_id": self._ssp.id,
                                "lu_unique_device_id": lu.unique_device_id,
                                "lu_unit_name": lu.unit_name,
                                "k2xa": k2xa.r(), })

            if lu.logical_unit_type == "VirtualIO_Image":
                volume['status'] = 'in-use'
                volume['support'] = {
                    "status": "not_supported",
                    "reasons": [_(
                        'Because it is of type VirtualIO_Image, this '
                        'volume is not a candidate for management. '
                        'Perhaps, while deleting a P image, '
                        'someone chose not to delete the backing storage? '
                        'If you wish to work with the underlying Shared '
                        'Storage Pool Logical Unit please use the HMC or '
                        'VIOS commands.')
                    ]
                }
                msg = _("ssp:"
                        " during Logical Unit discovery,"
                        " ssp_id: >%(ssp_id)s<,"
                        " lu_unique_device_id: >%(lu_unique_device_id)s<,"
                        " lu_unit_name: >%(lu_unit_name)s<,"
                        " volume is of type VirtualIO_Image and not available "
                        " for management,"
                        " k2xa: >%(k2xa)s<")
                LOG.info(msg % {"ssp_id": self._ssp.id,
                                "lu_unique_device_id": lu.unique_device_id,
                                "lu_unit_name": lu.unit_name,
                                "k2xa": k2xa.r(), })

            volume['connection_info'] = \
                self._get_connection_info(lu.unit_name, lu.unique_device_id)
            #Add the Volume if it meets the Filter criteria
            if filter_set is None or lu.unique_device_id in filter_set:
                volumes.append(volume)

#         output = json.dumps(volumes, sort_keys=True, indent=4)
#         LOG.info(_("ssp:"
#                    " during discover_volumes,"
#                    " volumes: >%s<") % output)

        k2xa.log()
        return volumes

    def query_volumes(self, context, volumes, server_info={}, mark_boot=True):
        """Returns import-related details for the Volumes from the Provider"""
        returned_volumes = list()
        uid_map, boot_map = (dict(), dict())
        # Build a map of the UID's for each Server for quicker lookup
        for server_id, server in server_info.iteritems():
            for volume in server.get('volumes', []):
                uid = volume.get('unique_device_id')
                if uid is not None:
                    uid_map[uid] = server_id
        # Loop through the Volumes, setting the attachment info
        for volume in volumes:
            volume_copy = volume.copy()
            # Parse the UID out of the MetaData to use for matching Servers
            metadata = volume_copy.get('restricted_metadata', {})
            uid = metadata.get(ssp.RESTRICTED_METADATA_LU_UDID_KEY)
            # If the Server for this UID is in the Map, mark it attached
            if uid in uid_map:
                volume_copy['instance_uuid'] = uid_map[uid]
                # See if this should be flagged as the Server's Boot Volume
                if mark_boot is True and uid_map[uid] not in boot_map:
                    volume_copy['bootable'] = True
                    boot_map[uid_map[uid]] = volume_copy['uuid']
            #  Add the Copy of the Volume to the list to be returned
            returned_volumes.append(volume_copy)
        return returned_volumes

    def get_default_vol_type(self):
        """Returns the default volume type from the .conf file"""
        vtn = self.configuration.default_volume_type
        return vtn.decode('utf-8') if vtn else vtn

    def check_volume_health(self, volume):
        """
        Throws exceptions if something is wrong with the passed-in volume.

        Checks for existence of the underlying LU
        """

        k2xa = K2_XA("check_volume_health")

        self._get_and_check_lu(volume,
                               "check_volume_health",
                               1000,
                               k2xa)
        k2xa.log()
