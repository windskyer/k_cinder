import mock
import unittest
from cinder import test
from paxes_cinder.volume.drivers.vios import vios_lvm_iscsi

class ViosLvmIscsiTestCase(unittest.TestCase):
    def setUp(self):
        super(ViosLvmIscsiTestCase, self).setUp()
        self.driver = vios_lvm_iscsi.VIOSLVMISCSIDriver(configuration=mock.Mock())
        #self.driver.client = mock.Mock()
        #self.driver.vserver = mock.Mock()

    
    @mock.patch('vios_lvm_iscsi._create_export')
    def test_create_export(self, mock_create):
        mock_create.return_value = True
        result = self.driver.create_export('', 'com.nco-china.test1')
        
        self.assertEqual(True, result)

    def tearDown(self):
        super(ViosLvmIscsiTestCase, self).tearDown()
        

if __name__ == "__main__":
    unittest.main()
