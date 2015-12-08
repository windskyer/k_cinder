#
#
# =================================================================
# =================================================================

"""
P Extension to the Manager for the Cinder Scheduler Service
"""

from cinder.scheduler import manager as schedmgr
from cinder.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class PowerVCSchedulerManager(schedmgr.SchedulerManager):
    """P extension to the Cinder Scheduler Manager."""

    def __init__(self, scheduler_driver=None, *args, **kwargs):
        super(PowerVCSchedulerManager, self).__init__(scheduler_driver,
                                                      *args, **kwargs)

    def get_all_host_states(self, context):
        """Returns a dict of all the hosts the HostManager knows about."""
        output_map = {}
        host_states = self.driver.host_manager.get_all_host_states(context)
        for item in host_states:
            output_map[item.host] = {
                'free_capacity_gb': item.free_capacity_gb,
                'total_capacity_gb': item.total_capacity_gb
            }
        return output_map
