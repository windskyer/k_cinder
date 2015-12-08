# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

from oslo.config import cfg
from oslo import messaging

from cinder.openstack.common import log as logging
from cinder.volume import rpcapi
from cinder import rpc

cfg.CONF.register_opts([
    cfg.IntOpt('onboard_query_timeout', default=600,
               help='Timeout for RPC Query Resource Details for On-boarding'),
    cfg.IntOpt('verify_connection_timeout', default=5,
               help='Timeout for RPC Verify Connection Timeout')
])

LOG = logging.getLogger(__name__)


class VolumeAPIProduct(rpcapi.VolumeAPI):
    def __init__(self, topic=None):
        super(VolumeAPIProduct, self).__init__(topic)

    def get_storage_metadata(self, ctxt, host):
        cctxt = self.client.prepare(server=host)
        return cctxt.call(ctxt, 'get_storage_metadata')

    def discover_volumes(self, ctxt, host, filters=None):
        cctxt = self.client.prepare(server=host,
                                    timeout=cfg.CONF.onboard_query_timeout)
        return cctxt.call(ctxt, 'discover_volumes',
                          filters=filters)

    def query_volumes(self, ctxt, host, volume_ids,
                      extra_parms={}, allow_unsupported=False):
        cctxt = self.client.prepare(server=host,
                                    timeout=cfg.CONF.onboard_query_timeout)
        return cctxt.call(ctxt, 'query_volumes',
                          volume_ids=volume_ids,
                          extra_parms=extra_parms,
                          allow_unsupported=allow_unsupported)

    def get_next_volumes_chunk(self, ctxt, host, identifier):
        cctxt = self.client.prepare(server=host)
        return cctxt.call(ctxt, 'get_next_volumes_chunk',
                          identifier=identifier)

    def get_default_vol_type(self, ctxt, host):
        cctxt = self.client.prepare(server=host)
        return cctxt.call(ctxt, 'get_default_vol_type')

    def get_default_opts(self, ctxt, host):
        cctxt = self.client.prepare(server=host)
        return cctxt.call(ctxt, 'get_default_opts')

    def ibm_extend_volume(self, ctxt, volume, size):
        # The ibm_textend_volume will be synchronize call and
        # raise exception if a flashcopy is in progress.
        cctxt = self.client.prepare(server=volume['host'])
        return cctxt.call(ctxt, 'ibm_extend_volume',
                          volume=volume,
                          new_size=size)

    def verify_host_running(self, ctxt, host, max_wait=0):
        """Verifies the cinder-volume service for the Host is running"""
        #We will default to checking once, but allow the caller to check more
        for index in range(max_wait / cfg.CONF.verify_connection_timeout + 1):
            if self._verify_host_running(ctxt, host):
                index = index + 1
                return True
        return False

    def _verify_host_running(self, ctxt, host):
        """Verifies the cinder-volume service for the Host is running"""
        cctxt = self.client.prepare(server=host,
                                    timeout=cfg.CONF.verify_connection_timeout)
        try:
            return cctxt.call(ctxt, 'verify_host_running')
        #If we got a timeout, just log for debug that the process is down
        except Exception:
            LOG.debug('RPC verify_host_running timed-out for ' + host)
            return False

    def set_volume_type_quota(self, ctxt, host, volume_type):
        """ setup the volume type based quota in the default quota class """
        cctxt = self.client.prepare(server=host)
        return cctxt.call(ctxt, 'set_volume_type_quota',
                          volume_type=volume_type)
