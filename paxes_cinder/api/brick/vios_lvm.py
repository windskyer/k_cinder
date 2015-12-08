# Copyright 2013 OpenStack Foundation.
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
VIOSLVM class for performing VIOSLVM operations.
"""

import re

from cinder.brick import exception
from cinder.brick import executor
from cinder.openstack.common.gettextutils import _
from cinder.openstack.common import log as logging
from cinder.openstack.common import processutils as putils

LOG = logging.getLogger(__name__)


class VIOSLVM(executor.Executor):
    """LVM object to enable various LVM related operations."""

    def __init__(self, vg_name, root_helper, create_vg=False,
                 physical_volumes=None, lvm_type='default',
                 executor=putils.execute):

        """Initialize the LVM object.

        The LVM object is based on an LVM VolumeGroup, one instantiation
        for each VolumeGroup you have/use.

        :param vg_name: Name of existing VG or VG to create
        :param root_helper: Execution root_helper method to use
        :param create_vg: Indicates the VG doesn't exist
                          and we want to create it
        :param physical_volumes: List of PVs to build VG on
        :param lvm_type: VG and Volume type (default, or thin)
        :param executor: Execute method to use, None uses common/processutils

        """
        super(VIOSLVM, self).__init__(execute=executor, root_helper=root_helper)
        self.vg_name = vg_name
        self.pv_list = []
        self.lv_list = []
        self.vg_size = 0.0
        self.vg_free_space = 0.0
        self.vg_lv_count = 0
        self.vg_uuid = None
        self.vg_thin_pool = None
        self.vg_thin_pool_size = 0.0
        self.vg_thin_pool_free_space = 0.0
        self._supports_snapshot_lv_activation = None
        self._supports_lvchange_ignoreskipactivation = None
        self.su_padmin = 'su - padmin -c ioscli '

        if create_vg and physical_volumes is not None:
            self.pv_list = physical_volumes

            try:
                self._create_vg(physical_volumes)
            except putils.ProcessExecutionError as err:
                LOG.exception(_('Error creating Volume Group'))
                LOG.error(_('Cmd     :%s') % err.cmd)
                LOG.error(_('StdOut  :%s') % err.stdout)
                LOG.error(_('StdErr  :%s') % err.stderr)
                raise exception.VolumeGroupCreationFailed(vg_name=self.vg_name)

        if self._vg_exists() is False:
            LOG.error(_('Unable to locate Volume Group %s') % vg_name)
            raise exception.VolumeGroupNotFound(vg_name=vg_name)

        # NOTE: we assume that the VG has been activated outside of Cinder

        if lvm_type == 'thin':
            pool_name = "%s-pool" % self.vg_name
            if self.get_volume(pool_name) is None:
                self.create_thin_pool(pool_name)
            else:
                self.vg_thin_pool = pool_name

            self.activate_lv(self.vg_thin_pool)
        self.pv_list = self.get_all_physical_volumes(root_helper, vg_name)

    def _vg_exists(self):
        """Simple check to see if VG exists.

        :returns: True if vg specified in object exists, else False

        """
        exists = False

        cmd = [self.su_padmin + 'lsvg']
        (out, err) = self._execute(*cmd,
                shell=True
                )
        if out is not None:
            vgs = out.splitlines()
            if self.vg_name in vgs:
                exists  = True                                                            
        return exists

    def _create_vg(self, pv_list):
        cmd = ['mkvg', '-y', self.vg_name, ','.join(pv_list)]
        self._execute(*cmd, root_helper=self._root_helper, run_as_root=True)

    def _get_vg_uuid(self):
        pass

    def _get_thin_pool_free_space(self, vg_name, thin_pool_name):
        pass

    @staticmethod
    def get_lvm_version(root_helper):
        pass

    @staticmethod
    def supports_thin_provisioning(root_helper):
        pass

    @property
    def supports_snapshot_lv_activation(self):
        pass

    @property
    def supports_lvchange_ignoreskipactivation(self):
        pass

    @staticmethod
    def get_all_volumes(root_helper, vg_name=None):
        """Static method to get all LV's on a system.

        :param root_helper: root_helper to use for execute
        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with LV info

        """

        cmd = ['env', 'LC_ALL=C', 'lsvg']

        if vg_name is not None:
            cmd.append(vg_name)

        (out_vg, err) = putils.execute(*cmd,
                                      root_helper=root_helper,
                                      run_as_root=True)
        
        cmd = ['env', 'LC_ALL=C', 'lsvg']
        if vg_name is not None:
            cmd.append('-l')
            cmd.append(vg_name)
 

        (out, err) = putils.execute(*cmd,
                                    root_helper=root_helper,
                                    run_as_root=True)

        lv_list = []

        if out_vg is not None:
            pp_size = int(out_vg.split("\n")[1].split()[5])
            if out is not None:
                vg_name = out.split(":")[0]
                lv_array_tmp = out.split(":")[1].split('\n')
                lv_array_len = len(lv_array_tmp)-1
                lv_array = lv_array_tmp[2:lv_array_len]
                for volume in lv_array:
                    lv_list.append({"vg": vg_name, "name": volume.split()[0],
                                   "size": int(volume.split()[3]) * pp_size / 1024.0})

        return lv_list

    def get_volumes(self):
        """Get all LV's associated with this instantiation (VG).

        :returns: List of Dictionaries with LV info

        """
        self.lv_list = self.get_all_volumes(self._root_helper, self.vg_name)
        return self.lv_list

    def get_volume(self, name):
        """Get reference object of volume specified by name.

        :returns: dict representation of Logical Volume if exists

        """
        ref_list = self.get_volumes()
        for r in ref_list:
            if r['name'] == name[0:15]:
                r['name'] = name
                return r

    @staticmethod
    def get_all_physical_volumes(root_helper, vg_name=None):
        """Static method to get all PVs on a system.

        :param root_helper: root_helper to use for execute
        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with PV info

        """
        cmd = ['su - padmin -c ioscli lspv']

        (out, err) =  putils.execute(*cmd,
                                    shell=True)

        pv_list = []
        if out is None:
            LOG.error("No volume groups be found!")
            return None
        pvs_array = out.splitlines()
        for pv in pvs_array: 
            pv = pv.split()
            if 'active' in pv:
                cmd = ['su - padmin -c ioscli "lspv ' + pv[0] + 
                        ' -field \'VOLUME GROUP\' \'TOTAL PPs\' \'FREE PPs\' -fmt : "']
                (out, err) = putils.execute(*cmd,
                                        shell=True)
                params = out.split(":")
                pv_name = pv[0]
                vgname = params[0]
                total_size = re.search(r'\d+', params[1]).group(0)
                free_size = re.search(r'\d+', params[2]).group(0)
                #params = out.split("\n")
                #pv_name = params[0].split()[2]
                #vgname = params[0].split()[5]
                #pp_size = float(params[4].split()[2])
                #total_size = float(params[5].split()[2]) * pp_size / 1024.0
                #free_size = float(params[6].split()[2]) * pp_size / 1024.0
                pv_list.append({"vg": vgname,
                                "name": "/dev/" + pv_name,
                                "size": total_size,
                                "available": free_size})
        if vg_name is not None:
            cur_pv = [pv for pv in pv_list if vg_name == pv.get('vg')]
            return cur_pv
        else:        
            return pv_list

    def get_physical_volumes(self):
        """Get all PVs associated with this instantiation (VG).

        :returns: List of Dictionaries with PV info

        """
        self.pv_list = self.get_all_physical_volumes(self._root_helper,
                                                     self.vg_name)
        return self.pv_list

    @staticmethod
    def get_all_volume_groups(root_helper, vg_name=None):
        """Static method to get all VGs on a system.

        :param root_helper: root_helper to use for execute
        :param vg_name: optional, gathers info for only the specified VG
        :returns: List of Dictionaries with VG info

        """
        cmd = ['env', 'LC_ALL=C', 'lsvg']


        (out, err) = putils.execute(*cmd,
                                    root_helper=root_helper,
                                    run_as_root=True)
        if out is None:
            LOG.error("No volume groups be found!")
            return None
        list_vgs = out.split("\n")
        vgs = []
        for vgname in list_vgs:
            if vgname :
                cmd = ['env', 'LC_ALL=C', 'lsvg']
                cmd.append(vgname)
                (out, err) = putils.execute(*cmd,
                                    root_helper=root_helper,
                                    run_as_root=True)
                params = out.split("\n")
                pp_size = float(params[1].split()[5])
                total_size = float(params[2].split()[5]) * pp_size / 1024.0
                free_size = float(params[3].split()[5]) * pp_size / 1024.0
                lv_count = int(params[4].split()[1])
                vgs.append({"name": vgname,
                        "size": total_size,
                        "available": free_size,
                        "lv_count": lv_count})

        if vg_name is not None:
            list_vg = [vg for vg in vgs if vg_name == vg.get('name')]
            return list_vg
        else:
            return vgs

    def update_volume_group_info(self):
        """Update VG info for this instantiation.

        Used to update member fields of object and
        provide a dict of info for caller.

        :returns: Dictionaries of VG info

        """
        vg_list = self.get_all_volume_groups(self._root_helper, self.vg_name)

        if len(vg_list) != 1:
            LOG.error(_('Unable to find VG: %s') % self.vg_name)
            raise exception.VolumeGroupNotFound(vg_name=self.vg_name)

        self.vg_size = float(vg_list[0]['size'])
        self.vg_free_space = float(vg_list[0]['available'])
        self.vg_lv_count = int(vg_list[0]['lv_count'])
        #self.vg_uuid = vg_list[0]['uuid']

        if self.vg_thin_pool is not None:
            for lv in self.get_all_volumes(self._root_helper, self.vg_name):
                if lv['name'] == self.vg_thin_pool:
                    self.vg_thin_pool_size = lv['size']
                    tpfs = self._get_thin_pool_free_space(self.vg_name,
                                                          self.vg_thin_pool)
                    self.vg_thin_pool_free_space = tpfs

    def _calculate_thin_pool_size(self):
        """Calculates the correct size for a thin pool.

        Ideally we would use 100% of the containing volume group and be done.
        But the 100%VG notation to lvcreate is not implemented and thus cannot
        be used.  See https://bugzilla.redhat.com/show_bug.cgi?id=998347

        Further, some amount of free space must remain in the volume group for
        metadata for the contained logical volumes.  The exact amount depends
        on how much volume sharing you expect.

        :returns: An lvcreate-ready string for the number of calculated bytes.
        """

        # make sure volume group information is current
        self.update_volume_group_info()

        # leave 5% free for metadata
        return "%sg" % (self.vg_free_space * 0.95)

    def create_thin_pool(self, name=None, size_str=None):
        pass

    def create_volume(self, name, size_str, lv_type='default', mirror_count=0):
        """Creates a logical volume on the object's VG.

        :param name: Name to use when creating Logical Volume
        :param size_str: Size to use when creating Logical Volume
        :param lv_type: Type of Volume (default or thin)
        :param mirror_count: Use LVM mirroring with specified count

        """
        if lv_type == 'thin':
            lv_type = 'jfs'
        else:
            lv_type = 'jfs2'

        cmd = ['mklv','-t', lv_type, '-y', name, self.vg_name,  size_str]

        try:
            self._execute(*cmd,
                          root_helper=self._root_helper,
                          run_as_root=True)
        except putils.ProcessExecutionError as err:
            LOG.exception(_('Error creating Volume'))
            LOG.error(_('Cmd     :%s') % err.cmd)
            LOG.error(_('StdOut  :%s') % err.stdout)
            LOG.error(_('StdErr  :%s') % err.stderr)
            raise

    def create_lv_snapshot(self, name, source_lv_name, lv_type='default'):
        """Creates a snapshot of a logical volume.

        :param name: Name to assign to new snapshot
        :param source_lv_name: Name of Logical Volume to snapshot
        :param lv_type: Type of LV (default or thin)

        """
        source_lvref = self.get_volume(source_lv_name)
        if source_lvref is None:
            LOG.error(_("Trying to create snapshot by non-existent LV: %s")
                      % source_lv_name)
            raise exception.VolumeDeviceNotFound(device=source_lv_name)
        cmd = ['snapshot', '-o', source_lv_name]
        if lv_type != 'thin':
            size = source_lvref['size']
            cmd.extend(['-L', '%sg' % (size)])

        try:
            self._execute(*cmd,
                          root_helper=self._root_helper,
                          run_as_root=True)
        except putils.ProcessExecutionError as err:
            LOG.exception(_('Error creating snapshot'))
            LOG.error(_('Cmd     :%s') % err.cmd)
            LOG.error(_('StdOut  :%s') % err.stdout)
            LOG.error(_('StdErr  :%s') % err.stderr)
            raise

    def _mangle_lv_name(self, name):
        # Linux LVM reserves name that starts with snapshot, so that
        # such volume name can't be created. Mangle it.
        if not name.startswith('snapshot'):
            return name
        return '_' + name

    def activate_lv(self, name, is_snapshot=False):
        pass

    def delete(self, name):
        """Delete logical volume or snapshot.

        :param name: Name of LV to delete

        """

        def run_udevadm_settle():
            self._execute('udevadm', 'settle',
                          root_helper=self._root_helper, run_as_root=True,
                          check_exit_code=False)

        try:

            cmd = ['rmlv', ]

            cmd.append('-f')
            cmd.append('%s' % (name))
            self._execute(*cmd,
                          root_helper=self._root_helper, run_as_root=True)
        except putils.ProcessExecutionError as err:
            mesg = (_('Error reported running lvremove: CMD: %(command)s, '
                    'RESPONSE: %(response)s') %
                    {'command': err.cmd, 'response': err.stderr})
            LOG.debug(mesg)

            LOG.debug(_('Attempting udev settle and retry of rmlv...'))
            #run_udevadm_settle()

            self._execute('rmlv',
                          '-f',
                          '%s' % (name),
                          root_helper=self._root_helper, run_as_root=True)

    def revert(self, snapshot_name):
        pass

    def lv_has_snapshot(self, name):
        pass

    def extend_volume(self, lv_name, new_size):
        """Extend the size of an existing volume."""

        try:
            self._execute('extendlv', lv_name, new_size,
                          root_helper=self._root_helper,
                          run_as_root=True)
        except putils.ProcessExecutionError as err:
            LOG.exception(_('Error extending Volume'))
            LOG.error(_('Cmd     :%s') % err.cmd)
            LOG.error(_('StdOut  :%s') % err.stdout)
            LOG.error(_('StdErr  :%s') % err.stderr)
            raise

    def vg_mirror_free_space(self, mirror_count):
        free_capacity = 0.0

        disks = []
        for pv in self.pv_list:
            disks.append(float(pv['available']))

        while True:
            disks = sorted([a for a in disks if a > 0.0], reverse=True)
            if len(disks) <= mirror_count:
                break
            # consume the smallest disk
            disk = disks[-1]
            disks = disks[:-1]
            # match extents for each mirror on the largest disks
            for index in list(range(mirror_count)):
                disks[index] -= disk
            free_capacity += disk

        return free_capacity

    def vg_mirror_size(self, mirror_count):
        return (self.vg_free_space / (mirror_count + 1))

    def rename_volume(self, lv_name, new_name):
        """Change the name of an existing volume."""

        try:
            self._execute('chlv', '-n', new_name, lv_name,
                          root_helper=self._root_helper,
                          run_as_root=True)
        except putils.ProcessExecutionError as err:
            LOG.exception(_('Error renaming logical volume'))
            LOG.error(_('Cmd     :%s') % err.cmd)
            LOG.error(_('StdOut  :%s') % err.stdout)
            LOG.error(_('StdErr  :%s') % err.stderr)
            raise
