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
"""
Driver for aix servers running LVM.

"""
import socket

from oslo.config import cfg

from cinder.brick import exception as brick_exception
from paxes_cinder.brick import vios_lvm as lvm
from cinder import exception
from paxes_cinder import exception as paxes_exception
from cinder.image import image_utils
from cinder.openstack.common import fileutils
from cinder.openstack.common import log as logging
from cinder.openstack.common import processutils
from cinder import units
from cinder import utils
from cinder.volume.drivers import lvm as driver
from cinder.volume import utils as volutils
from cinder.volume import volume_types
from cinder.openstack.common.db import exception as db_exc
from cinder import db as db_api


LOG = logging.getLogger(__name__)

volume_opts = [
    cfg.StrOpt('lvm_type',
               default='default',
               help='Type of LVM volumes to deploy; (default or thin)'),
]

CONF = cfg.CONF
CONF.register_opts(volume_opts)


class VIOSLVMDriver(driver.LVMVolumeDriver):
    """Executes commands relating to Volumes."""

    def __init__(self, vg_obj=None, *args, **kwargs):
        super(VIOSLVMDriver, self).__init__(*args, **kwargs)
        self.configuration.append_config_values(volume_opts)
        self.hostname = socket.gethostname()
        self.backend_name =\
            self.configuration.safe_get('volume_backend_name') or 'LVM'
        self.protocol = 'local'
        if vg_obj is None:
            root_helper = utils.get_root_helper()
            try:
                self.vg = lvm.VIOSLVM(self.configuration.volume_group,
                                  root_helper,
                                  lvm_type=self.configuration.lvm_type,
                                  executor=self._execute)
            except brick_exception.VolumeGroupNotFound:
                message = ("Volume Group %s does not exist" %
                           self.configuration.volume_group)
                raise exception.VolumeBackendAPIException(data=message)
        

    def check_for_setup_error(self):
        """Verify that requirements are in place to use LVM driver."""
        if self.vg is None:
            root_helper = utils.get_root_helper()
            try:
                self.vg = lvm.VIOSLVM(self.configuration.volume_group,
                                  root_helper,
                                  lvm_type=self.configuration.lvm_type,
                                  executor=self._execute)
            except brick_exception.VolumeGroupNotFound:
                message = ("Volume Group %s does not exist" %
                           self.configuration.volume_group)
                raise exception.VolumeBackendAPIException(data=message)

        vg_list = volutils.get_all_volume_groups(
            self.configuration.volume_group)
        vg_dict = \
            (vg for vg in vg_list if vg['name'] == self.vg.vg_name).next()
        if vg_dict is None:
            message = ("Volume Group %s does not exist" %
                       self.configuration.volume_group)
            raise exception.VolumeBackendAPIException(data=message)

        if self.configuration.lvm_type == 'thin':
            # Specific checks for using Thin provisioned LV's
            if not volutils.supports_thin_provisioning():
                message = ("Thin provisioning not supported "
                           "on this version of LVM.")
                raise exception.VolumeBackendAPIException(data=message)

            pool_name = "%s-pool" % self.configuration.volume_group
            if self.vg.get_volume(pool_name) is None:
                try:
                    self.vg.create_thin_pool(pool_name)
                except processutils.ProcessExecutionError as exc:
                    exception_message = ("Failed to create thin pool, "
                                         "error message was: %s"
                                         % exc.stderr)
                    raise exception.VolumeBackendAPIException(
                        data=exception_message)

    def check_for_setup_error(self):
        pass

    def local_path(self, volume, vg=None):
        if vg is None:
            vg = self.configuration.volume_group
        # NOTE(vish): stops deprecation warning
        #escaped_group = vg.replace('-', '--')
        #escaped_name = self._escape_snapshot(volume['name']).replace('-', '--')
        #return "/dev/mapper/%s-%s" % (escaped_group, escaped_name)
        return "/dev/%s" % volume['name'][:15]

    def ensure_export(self, context, volume):
        """Synchronously recreates an export for a volume."""
        pass

    def create_export(self, context, volume):
        """Exports the volume. Can optionally return a Dictionary of changes
        to the volume object to be persisted.
        """
        pass

    def remove_export(self, context, volume):
        """Removes an export for a volume."""
        pass

    def initialize_connection(self, volume, connector):

        volume_type = self.protocol.lower()
        properties = {}
        volume_name = volume['name'][0:15]
        properties['volume_id'] = volume['id']
        properties['volume_name'] = volume_name

        return {'driver_volume_type': volume_type, 'data': properties, }

    def terminate_connection(self, volume, connector, **kwargs):
        ##volume_name = volume["name"][0:15]
        ##mark
        pass

    def get_volume_stats(self, refresh=False):
        """Get volume status.

        If 'refresh' is True, run update the stats first.
        """

        if refresh:
            self._update_volume_stats()

        return self._stats

    def _update_volume_stats(self):
        """Retrieve stats info from volume group."""

        LOG.debug(_("Updating volume stats"))
        if self.vg is None:
            LOG.warning(_('Unable to update stats on non-initialized '
                          'Volume Group: %s'), self.configuration.volume_group)
            return

        self.vg.update_volume_group_info()
        data = {}

        # Note(zhiteng): These information are driver/backend specific,
        # each driver may define these values in its own config options
        # or fetch from driver specific configuration file.
        data["volume_backend_name"] = self.backend_name
        data["vendor_name"] = 'Open Source'
        data["driver_version"] = self.VERSION
        data["storage_protocol"] = self.protocol

        if self.configuration.lvm_mirrors > 0:
            data['total_capacity_gb'] =\
                self.vg.vg_mirror_size(self.configuration.lvm_mirrors)
            data['free_capacity_gb'] =\
                self.vg.vg_mirror_free_space(self.configuration.lvm_mirrors)
        elif self.configuration.lvm_type == 'thin':
            data['total_capacity_gb'] = self.vg.vg_thin_pool_size
            data['free_capacity_gb'] = self.vg.vg_thin_pool_free_space
        else:
            data['total_capacity_gb'] = self.vg.vg_size
            data['free_capacity_gb'] = self.vg.vg_free_space
        data['reserved_percentage'] = self.configuration.reserved_percentage
        data['QoS_support'] = False
        data['location_info'] =\
            ('VIOSLVMDriver:%(hostname)s:%(vg)s'
             ':%(lvm_type)s:%(lvm_mirrors)s' %
             {'hostname': self.hostname,
              'vg': self.configuration.volume_group,
              'lvm_type': self.configuration.lvm_type,
              'lvm_mirrors': self.configuration.lvm_mirrors})

        self._stats = data


    def extend_volume(self, volume, new_size):
        """Extend an existing volume's size."""
        extend_size = new_size - volume['size']
        self.vg.extend_volume(volume['name'][0:15],
                              self._sizestr(extend_size))


    def _volume_not_present(self, volume_name):
        return self.vg.get_volume(volume_name) is None

    def _delete_volume(self, volume, is_snapshot=False):
        """Deletes a logical volume."""
        name = volume['name']
        if is_snapshot:
            name = self._escape_snapshot(volume['name'])
        self.vg.delete(name[:15])

    def delete_volume(self, volume):
        """Deletes a logical volume."""

        # NOTE(jdg):  We don't need to explicitly call
        # remove export here because we already did it
        # in the manager before we got here.

        if self._volume_not_present(volume['name']):
            # If the volume isn't present, then don't attempt to delete
            return True

        #if self.vg.lv_has_snapshot(volume['name']):
        #    LOG.error(_('Unabled to delete due to existing snapshot '
        #                'for volume: %s') % volume['name'])
        #    raise exception.VolumeIsBusy(volume_name=volume['name'])

        self._delete_volume(volume)
        
    def create_snapshot(self, snapshot):
        """Creates a snapshot."""

        #self.vg.create_lv_snapshot(self._escape_snapshot(snapshot['name']),
        #                           snapshot['volume_name'],
        #                           self.configuration.lvm_type)
        mirror_count = 0
        LOG.info(_('Creating clone of volume: %s') % snapshot['id'])
        src_volume = {'name' : snapshot['volume_name'],
                      'id': snapshot['volume_id'],
                      }
        
        new_snapshot = {'name': snapshot['name'],
                         'size': snapshot['volume_size'],
                         'id': snapshot['id']
                         }
        new_snapshot_name = self._escape_snapshot(new_snapshot['name'])
        self._create_volume(new_snapshot_name,
                            self._sizestr(new_snapshot['size']),
                            self.configuration.lvm_type,
                            mirror_count)
        new_snapshot['name'] = new_snapshot_name
        try:
            self.copy_volume(
                self.local_path(src_volume),
                self.local_path(new_snapshot),
                new_snapshot['size'] * units.KiB,
                self.configuration.volume_dd_blocksize,
                execute=self._execute)
        except Exception:
            self._delete_volume(snapshot, is_snapshot=True)
            raise paxes_exception.SnapshotCreateError(snapshot_name = self._escape_snapshot(new_snapshot['name']))

    def delete_snapshot(self, snapshot):
        """Deletes a snapshot."""
        if self._volume_not_present(self._escape_snapshot(snapshot['name'])):
            # If the snapshot isn't present, then don't attempt to delete
            LOG.warning(_("snapshot: %s not found, "
                          "skipping delete operations") % snapshot['name'])
            return True

        # TODO(yamahata): zeroing out the whole snapshot triggers COW.
        # it's quite slow.
        
        self._delete_volume(snapshot, is_snapshot=True)

    def copy_volume(self, srcstr, deststr, size_in_m, blocksize, sync=False,
                execute=utils.execute, ionice=None):
        # Use O_DIRECT to avoid thrashing the system buffer cache
        extra_flags = ['iflag=direct', 'oflag=direct']
    
        # Check whether O_DIRECT is supported
        try:
            execute('dd', 'count=0', 'if=%s' % srcstr, 'of=%s' % deststr,
                    *extra_flags, run_as_root=True)
        except processutils.ProcessExecutionError:
            extra_flags = []
    
        # If the volume is being unprovisioned then
        # request the data is persisted before returning,
        # so that it's not discarded from the cache.
        if sync and not extra_flags:
            extra_flags.append('conv=sync')
    
        blocksize, count = volutils._calculate_count(size_in_m, blocksize)
    
        cmd = ['dd', 'if=%s' % srcstr, 'of=%s' % deststr,
               'count=%d' % count, 'bs=%s' % blocksize]
        cmd.extend(extra_flags)
    
        if ionice is not None:
            cmd = ['ionice', ionice] + cmd
    
        # Perform the copy
        execute(*cmd, run_as_root=True)

    def create_cloned_volume(self, volume, src_vref):
        """Creates a clone of the specified volume."""

        mirror_count = 0
        if self.configuration.lvm_mirrors:
            mirror_count = self.configuration.lvm_mirrors
        LOG.info(_('Creating clone of volume: %s') % src_vref['id'])
        volume_name = src_vref['name']
        temp_id = 'tmp-snap-%s' % volume['id']
        temp_snapshot = {'name': volume_name,
                         'size': src_vref['size'],
                         'volume_size': src_vref['size'],
                         'snap_name': 'clone-snap-%s' % volume['id'],
                         'id': temp_id}

        #self.create_snapshot(temp_snapshot)
        self._create_volume(volume['name'],
                            self._sizestr(volume['size']),
                            self.configuration.lvm_type,
                            mirror_count)

        #self.vg.activate_lv(temp_snapshot['name'], is_snapshot=True)

        # copy_volume expects sizes in MiB, we store integer GiB
        # be sure to convert before passing in
        try:
            self.copy_volume(
                self.local_path(temp_snapshot),
                self.local_path(volume),
                src_vref['size'] * units.KiB,
                self.configuration.volume_dd_blocksize,
                execute=self._execute)
        finally:
            #self.delete_snapshot(tmp_snapshot)
            pass

    def do_setup(self, ctxt):
        LOG.debug('enter: do_setup')
        self._context = ctxt
        # Ensure that the default volume type exists
        vtn = self.configuration.default_volume_type
        vtn = vtn.decode('utf-8') if vtn else vtn
        try:
            volume_types.get_volume_type_by_name(ctxt, vtn)
        except exception.VolumeTypeNotFoundByName:
            # If the default volume type does not exist, we create it here.
            LOG.info(_("Creating default volume type '%s'") % vtn)
            self._create_default_volume_type(ctxt, vtn)

        LOG.debug('leave: do_setup')
            
    def _create_default_volume_type(self, context, volume_type_name):
        """Internal Helper Method to Create a Default Volume Type for Host"""
        vbn = self.configuration.volume_backend_name
        storage_protocol = self.protocol

        extra_specs = {}
        extra_specs['drivers:display_name'] = volume_type_name
        extra_specs['capabilities:volume_backend_name'] = vbn
        extra_specs['capabilities:storage_protocol'] = storage_protocol

        def voltype_create(name, extra_specs):
            """ Don't use volume_type.create during init_host"""
            try:
                type_ref = db_api.volume_type_create(
                    context, dict(name=name, extra_specs=extra_specs))
            except db_exc.DBError as e:
                LOG.exception(_('DB error: %s') % e)
                raise exception.VolumeTypeCreateFailed(
                    name=name, extra_specs=extra_specs)
            return type_ref

        return voltype_create(volume_type_name, extra_specs)
