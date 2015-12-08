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
Driver for aix servers running ISCSI.

"""
import socket

from oslo.config import cfg

from cinder import exception


from cinder import db as db_api
from cinder import units
from cinder import utils
from cinder.volume import iscsi
from cinder.volume import utils as volutils
from cinder.volume import volume_types
from cinder.openstack.common import log as logging
from cinder.openstack.common import processutils
from cinder.openstack.common import uuidutils
from cinder.openstack.common.db import exception as db_exc

from paxes_cinder.volume.drivers.vios import vios_iscsi as vios_iscsi
from paxes_cinder.volume.drivers.vios import vios_lvm as driver

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

class VIOSLVMISCSIDriver(driver.VIOSLVMDriver, vios_iscsi.VIOSISCSIDriver):
    def __init__(self, *args, **kwargs):
        self.db = kwargs.get('db')
        self.target_helper = self.get_target_helper(self.db)
        super(VIOSLVMISCSIDriver, self).__init__(*args, **kwargs)
        self.backend_name =\
            self.configuration.safe_get('volume_backend_name') or 'LVM_iSCSI'
        self.protocol = 'viSCSI'
        self.target_name = self.configuration.safe_get('host') or uuidutils.generate_uuid()[8]

    def set_execute(self, execute):
        super(VIOSLVMISCSIDriver, self).set_execute(execute)
        if self.target_helper is not None:
            self.target_helper.set_execute(execute)
    
#    def do_setup(self, ctxt):
#        LOG.debug('enter: do_setup')
#        self._context = ctxt
#        # Ensure that the default volume type exists
#        vtn = self.configuration.default_volume_type
#        vtn = vtn.decode('utf-8') if vtn else vtn
#        try:
#            volume_types.get_volume_type_by_name(ctxt, vtn)
#        except exception.VolumeTypeNotFoundByName:
#            # If the default volume type does not exist, we create it here.
#            LOG.info(_("Creating default volume type '%s'") % vtn)
#            self._create_default_volume_type(ctxt, vtn)
#
#        LOG.debug('leave: do_setup')
#            
#    def _create_default_volume_type(self, context, volume_type_name):
#        """Internal Helper Method to Create a Default Volume Type for Host"""
#        ##vbn = self.configuration.volume_backend_name
#
#        extra_specs = {}
#        extra_specs['drivers:display_name'] = volume_type_name
#        ##extra_specs['capabilities:volume_backend_name'] = vbn
#
#        def voltype_create(name, extra_specs):
#            """ Don't use volume_type.create during init_host"""
#            try:
#                type_ref = db_api.volume_type_create(
#                    context, dict(name=name, extra_specs=extra_specs))
#            except db_exc.DBError as e:
#                LOG.exception(_('DB error: %s') % e)
#                raise exception.VolumeTypeCreateFailed(
#                    name=name, extra_specs=extra_specs)
#            return type_ref
#
#        return voltype_create(volume_type_name, extra_specs)

    def initialize_connection(self, volume, connector):
        volume_name = volume['name'][0:15]
        target_name = '%s:%s' % (connector['initiator'], volume_name)
        #target_name = '%s:%s' % (connector['initiator'], self.target_name)
        volume_type = self.protocol.lower()
        properties = {}
        properties['target_portal'] =  '%s:%s' % (CONF.iscsi_ip_address, CONF.iscsi_port)
        properties['target_iqn'] =  target_name
        target, lun_id = self._create_export('', target_name, volume_name)
        properties['target_name'] =  target
        properties['target_lun'] =  lun_id
        properties['volume_id'] = volume['id']

        return {'driver_volume_type': volume_type, 'data': properties, }

    def terminate_connection(self, volume, connector, **kwargs):
        volume_name = volume["name"][0:15]
        iqn = '%s:%s' % (connector['initiator'], volume_name)        
        self._remove_export(volume_name, iqn)
    
    ##def create_export(self, context, volume):
    ##    """Creates an export for a logical volume."""
    ##    return self._create_export(context, volume)
    
    def create_volume(self, volume):
        #self._create_export("", "volume-7b7cdd64")
        """Creates a logical volume."""
        mirror_count = 0

        if self.configuration.lvm_mirrors:
            mirror_count = self.configuration.lvm_mirrors

        self._create_volume(volume['name'],
                            self._sizestr(volume['size']),
                            self.configuration.lvm_type,
                            mirror_count)

    def _create_export(self, context, iscsi_name, volume_name):
        """Creates an export for a logical volume."""\

        ##iscsi_name = "%s%s" % (CONF.iscsi_target_prefix,
        ##                        volume['name'])

        target = self.create_vios_iscsi_target(iscsi_name=iscsi_name, volume_name=volume_name)
        lun = None
        if target: 
            lun = self.export_vios_iscsi_target(target=target, volume_name=volume_name)
        return target, lun

    def _remove_export(self, volume_name, iqn):
        '''
          Delete the lu 
        '''
        lu = self.get_lu_by_volume(volume_name)
        
        ##Remove the lu
        self.remove_dev(lu)
        ##Remove the target
        target = self.get_target_by_iqn(iqn)
        self.remove_dev(target)
        
##    def remove_export(self, context, volume):
##        return self.remove_dev(volume)

##    def ensure_export(self, context, volume):
##        volume_name = volume['name']
##        result = self.ensure_vios_export(volume_name)
##        if result:
##            self.db.volume_update(context, volume['id'], model_update) ##need update
            
            
    def get_target_helper(self, db):
        root_helper = utils.get_root_helper()

        ##CONF.iscsi_helper == 'tgtadm':
        return iscsi.TgtAdm(root_helper,
                            CONF.volumes_dir,
                            CONF.iscsi_target_prefix,
                            db=db)

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
    
    
