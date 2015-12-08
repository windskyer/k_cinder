# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

"""
P Extension to the Cinder Host Manager
"""
from oslo.config import cfg

from cinder import db
from cinder import exception
from cinder.openstack.common import lockutils
from cinder.openstack.common import log as logging
from cinder.scheduler import host_manager as hostmgr

from paxes_cinder import _

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
CONF.import_opt('scheduler_default_filters', 'cinder.scheduler.host_manager')
CONF.set_default('scheduler_default_filters',
                 ['AvailabilityZoneFilter',
                  'PowerVCCapacityFilter',
                  'CapabilitiesFilter'])


class PowerVCHostManager(hostmgr.HostManager):
    """ P Host Manager Extension """
    def __init__(self, *args, **kwargs):
        super(PowerVCHostManager, self).__init__(*args, **kwargs)

    @lockutils.synchronized('PowerVCHostManager', 'cinder-', external=True)
    def get_all_host_states(self, context):
        """
        The host_state_map in the HostManager isn't
        maintained properly during storage host registration/deregistration.
        Override get_all_host_states and add proper serialization.

        For example:
        {'192.168.1.100': HostState(), ...}
        """
        topic = CONF.volume_topic
        for host, host_state in self.host_state_map.items():
            try:
                db.service_get_by_host_and_topic(context,
                                                 host,
                                                 topic)
            except exception.ServiceNotFound:
                # The host has been deregistered
                LOG.debug(_("clean up host_state_map: %(host)s" %
                            {'host': host}))
                del self.host_state_map[host]
                continue

        s = super(PowerVCHostManager, self)
        hosts = s.get_all_host_states(context)

        return hosts
