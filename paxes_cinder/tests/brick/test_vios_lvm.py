'''
Created on Sep 7, 2015

@author: root
'''


import testtools
import stubout

from cinder.openstack.common import processutils
from paxes_cinder.brick import vios_lvm



class BrickViosLvmTestCase(testtools.TestCase):
    def setUp(self):
        super(BrickViosLvmTestCase, self).setUp()
        
        self.vgname = 'fake-vg'
        self.stubs = stubout.StubOutForTesting()
        #Stub processutils.execute for static methods
        self.stubs.Set(processutils, 'execute',
                       self.fake_execute)
        self.vioslvm = vios_lvm.VIOSLVM(self.vgname,
                                        'sudo',
                                        False, None,
                                        'default',
                                        self.fake_execute)
    
    def test_create_vg(self):
        pass
    
    def test_get_all_volumes(self):
        pass
    
    def test_get_volumes(self):
        pass
    
    def test_get_volume(self):
        pass
    
    def test_get_all_physical_volumes(self):
        pass
    
    def test_get_physical_volumes(self):
        pass
    
    def test_get_all_volume_groups(self):
        pass
    
    def test_update_volume_group_info(self):
        pass
    
    def test_create_volume(self):
        pass
    
    def test_create_lv_snapshot(self):
        pass
    
    def test_delete(self):
        pass
    
    def test_extend_volume(self):
        pass
    
    def test_vg_mirror_free_space(self):
        pass
    
    def test_vg_mirror_size(self):
        pass
    
    def test_rename_volume(self):
        pass
    

    
    
    def fake_execute(obj, *cmd, **kwargs):
        cmd_string = ', '.join(cmd)
        data = "\n"
        
        if ('env, LC_ALL=C, lsvg, fake-vg' in cmd_string):
            data = "VOLUME GROUP:       rootvg                   VG IDENTIFIER:  000072fa00007a000000014f676f02bb"
        elif ():
            pass 
        elif ():
            pass
        else:
            raise AssertionError('unexpected command called: %s' % cmd_string)

        return (data, "")
    
    
    
    
