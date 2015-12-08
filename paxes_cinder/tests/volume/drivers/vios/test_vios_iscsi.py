import mock
import uuid
import shutil
import tempfile

from cinder import context
from cinder import test
from cinder import quota
from cinder.openstack.common import importutils
from oslo.config import cfg
from stevedore import extension
from paxes_cinder.volume.drivers.vios import vios_iscsi

QUOTAS = quota.QUOTAS

CONF = cfg.CONF

ENCRYPTION_PROVIDER = 'nova.volume.encryptors.cryptsetup.CryptsetupEncryptor'

fake_opt = [
    cfg.StrOpt('fake_opt', default='fake', help='fake opts')
]

FAKE_UUID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa'

class DriverTestCase(test.TestCase):
    """Base Test class for Drivers."""
    driver_name = "cinder.volume.driver.FakeBaseDriver"

    def setUp(self):
        super(DriverTestCase, self).setUp()
        self.extension_manager = extension.ExtensionManager(
            "DriverTestCase")
        vol_tmpdir = tempfile.mkdtemp()
        import pdb
        pdb.set_trace()
        self.flags(volumes_dir=vol_tmpdir,
                   notification_driver=["test"])
#        self.flags(volume_driver=self.driver_name,
#                   volumes_dir=vol_tmpdir)
        self.volume = importutils.import_object("paxes_cinder.volume.manager.PowerVCVolumeManager")
        self.context = context.get_admin_context()
        self.output = ""
        #self.stubs.Set(vios_iscsi.VIOSISCSIDriver, '_get_target', self.fake_get_target)

        def _fake_execute(_command, *_args, **_kwargs):
            """Fake _execute."""
            pdb.set_trace()
            return self.output, None
        self.volume.driver.set_execute(_fake_execute)
        self.volume.driver.set_initialized()

    def tearDown(self):
        try:
            shutil.rmtree(CONF.volumes_dir)
        except OSError:
            pass
        super(DriverTestCase, self).tearDown()
 
    ##def fake_get_target(obj, iqn):
    ##    return 1


class ViosIscsiTestCase(test.TestCase):
    """Test Case for vios iscsi."""
    driver_name = "paxes_cinder.volume.drivers.vios.VIOSISCSIDriver"
    def setUp(self):
        super(ViosIscsiTestCase, self).setUp()
        self.driver = vios_iscsi.VIOSISCSIDriver(configuration=mock.Mock())
        self.driver.client = mock.Mock()
        self.fake_volume = str(uuid.uuid4())
        self.fake_target = str(uuid.uuid4())
        self.fake_lun = str(uuid.uuid4())
        self.fake_size = '1024'

        self.mock_request = mock.Mock()

    def test_create_vios_iscsi_target(self):
        #mock_create.return_value = None 
        #result = self.driver.create_vios_iscsi_target(iscsi_name='com.nco-china.test1')
        self.driver.create_vios_iscsi_target = mock.Mock(return_value={'target': 1})
        self.driver.client.invoke_successfully = mock.Mock(
            return_value=mock.MagicMock())
        #result = self.volume.driver.create_vios_iscsi_target(iscsi_name='com.nco-china.test1')
        
        #self.assertNotEqual(None, result)
        self.assertEqual(0, self.driver.client.invoke_successfully.call_count)        
        

    def tearDown(self):
        super(ViosIscsiTestCase, self).tearDown()

