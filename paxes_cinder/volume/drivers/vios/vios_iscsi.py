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
from networkx.algorithms.centrality.degree_alg import out_degree_centrality
"""
Driver for aix servers running LVM.

"""
import re

from cinder.openstack.common import log as logging
from cinder.openstack.common import processutils
from cinder.volume import driver

from paxes_cinder.brick import exception

LOG = logging.getLogger(__name__)

class VIOSISCSIDriver(driver.VolumeDriver):
    """
    Executes commands relating to ISCSI volumes.
    """
    def __init__(self, *args, **kwargs):       
        super(VIOSISCSIDriver, self).__init__(*args, **kwargs)
        self._target_atrr = "iscsi_name"
        self._lu_attr = "back_dev"
        
        self._tmiscsi_proto_is_exist()
        
    def _tmiscsi_proto_is_exist(self):
        try:
            (out, _err) = self._execute("lsdev -C -c driver -s node -t tmsw | sort | uniq",
                                        shell=True)
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from check tmiscsi proto is exist"))
            return None
        result = out.splitlines()
        if not len(result) > 0:
            self._create_tmiscsi_proto()
        else:
            try:
                (out, _err) = self._execute("lsdev -C -t target | grep ^tmiscsi",
                                        shell=True)
            except processutils.ProcessExecutionError as ex:
                LOG.warn(_("Error from check tmiscsi proto is exist"))
                self._remove_tmiscsi_proto(result[0].split(" ")[0])
                self._create_tmiscsi_proto()
                
    def _remove_tmiscsi_proto(self, tmsw_name):
        try:
            (out, _err) = self._execute("rmdev -d -l %s" % tmsw_name, shell=True)
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from remove tmiscsi proto"))
            raise exception.ISCSITmiscsi_ProtoRemoveFailed(tmsw=tmsw_name)
            
    def _create_tmiscsi_proto(self):
        try:
            (out, _err) = self._execute("mkdev -c driver -s node -t tmsw",
                                        shell=True)
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from create tmiscsi proto, check the proto is existed"))
            raise exception.ISCSITmiscsi_ProtoCreateFailed()

    def _target_is_exist(self, iscsi_name):    
        try:
            (out, _err) = self._execute("lsdev -C -t target |grep Available",
                                        shell=True)
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from check target is exist"))
            return None
        result = out.splitlines()
        if result is not None:
            for target in result:
                t_name = target.split()[0]
                iqn = self._get_dev(t_name, "iscsi_name")
                if iscsi_name == iqn:
                    return t_name
                else:
                    return None
        else:
            return None
        
    def create_vios_iscsi_target(self, iscsi_name="iscsi_ncochina", sub_class='tmtarget',
                                _class='tmiscsi', target='target',
                                parent_name='tmiscsi0', owner='tmsw0', volume_name=None):
        '''
            Create the iscsi target for lu
        '''
        
        cur_target = self._target_is_exist(iscsi_name)
        if cur_target:
            return cur_target
        
        if volume_name is None:
            return None
        try:
            lv = self.ensure_vios_export(volume_name)
            if lv:
                (out, _err) = self._execute("mkdev -c " +  _class +
                                        " -s " + sub_class + 
                                        " -t " + target + 
                                        " -p " + parent_name + 
                                        " -a " + "owner=" + owner + 
                                        " -a " + "iscsi_name=" + iscsi_name,
                                        shell=True)
            else:
                LOG.error("The target %s does not exist" %iscsi_name)
                return None
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from mkdev -c tmiscsi -s tmtarget -t target"))
            return None
        return out.splitlines()[0].split()[0]
   

    def export_vios_iscsi_target(self, volume_name=None,
                                _class='tmiscsi', sub_class='tmdev', 
                                type='lu', target="iscsi_ncochina", 
                                dev_type='lv'):
        '''
           Create the lu,  then the volume is exported
           :param volume_name: the volume name
           :param dev_type: Default is lv
        '''
        try:
            state = self._check_volume_state(volume_name)
            if state:
                (out, _err) = self._execute("mkdev -c " + _class + 
                                        " -s " + sub_class + " -t " + type +
                                        " -p " + target + 
                                        " -a " + "back_dev_type=" + dev_type +
                                        " -a " + "back_dev=" + volume_name,
                                        shell=True)
            else:
                LOG.error("The volume %s is been used" % volume_name)
                return None
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from mkdev -c tmiscsi -s tmtarget -t target, \
	                check if the iscsi_name %s is been used" % volume_name))
            return None
        result = out.splitlines()
        if "Available" in result[0]:
            lu_name = result[0].split()[0]
            lun_id = self._get_dev(lu_name, "lun_id")
            return lun_id
        else:
            return None
   
    def ensure_vios_export(self, volume_name):
        try:
            (out, _err) = self._execute("lslv -l  " + volume_name,
                                        shell=True)
        except processutils.ProcessExecutionError as ex:
            LOG.error(_("Error from lslv -l %s") % volume_name)
            return None
        return out

    def remove_dev(self, dev_name=None):
        if dev_name is not None:
            try:
                (out, _err) = self._execute("rmdev -d -l " + dev_name,
                                            shell=True)
            except processutils.ProcessExecutionError as ex:
                LOG.error(_("Error from rmdev -d -l %s") % dev_name)
        else:
            LOG.error("The dev_name is None")
            return False

        result = out.splitlines()
        if "Defined" in result[0]:
            return True
        else:
            return False


    def _check_volume_state(self, volume_name):
        try:    
            (out, _err) = self._execute("lslv " + volume_name +
                                        "|grep 'LV STATE'", 
                                        shell=True)
        except processutils.ProcessExecutionError as ex:  
            LOG.error(_("Error from check volume state"))
            return None
        result = re.search("closed/syncd", out)
        if result:
            return True
        else:   
            return False
        
        
    def get_lu_by_volume(self, volume_name=None):
        if volume_name is not None:
            try:    
                (out, _err) = self._execute("lsdev -C -t lu | grep 'iSCSI'| awk '{print $1}'", 
                                        shell=True)
            except processutils.ProcessExecutionError as ex:  
                LOG.error(_("Error from get lu by volume"))
                return None
        else:
            LOG.error(_("The iqn is None"))
            return None
        out = out.splitlines()
        for lu in out:
            result = self._get_dev(lu, "back_dev")
            if result == volume_name:
                return lu
            else:
                continue
        
    def get_target_by_iqn(self, iqn=None):
        if iqn is not None:
            try:    
                (out, _err) = self._execute("lsdev -C -t target | grep ^target | grep 'iSCSI'| awk '{print $1}'", 
                                        shell=True)
            except processutils.ProcessExecutionError as ex:  
                LOG.error(_("Error from get all target"))
                return None
        else:
            LOG.error(_("The iqn is None"))
            return None
        out = out.splitlines()
        for target in out:
            result = self._get_dev(target, "iscsi_name")
            if result == iqn:
                return target
        return None

    def _get_dev(self, dev_name, attr):
        try:    
            (out, _err) = self._execute("lsattr -El " + dev_name + 
                                    " -a " + attr, 
                                    shell=True)
        except processutils.ProcessExecutionError as ex:  
            LOG.error(_("Error from get special dev %s") % dev_name)
            return None   
        return out.split(" ")[1]
                    
