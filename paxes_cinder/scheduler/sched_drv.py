# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

"""
P Extension to the Cinder filtered Scheduler Driver
"""

from cinder import db
from cinder.openstack.common import log as logging
from cinder.openstack.common import timeutils
from cinder.scheduler import filter_scheduler as driver

from paxes_cinder import _

LOG = logging.getLogger(__name__)


class PowerVCSchedulerDriver(driver.FilterScheduler):
    """P extension to the Cinder Filter Scheduler."""

    def __init__(self, *args, **kwargs):
        super(PowerVCSchedulerDriver, self).__init__(*args, **kwargs)

    def _schedule(self, context, request_spec, filter_properties=None):
        """
        Returns a list of hosts that meet the required specs,
        ordered by their fitness.
        """
        s = super(PowerVCSchedulerDriver, self)
        hosts = s._schedule(context, request_spec,
                            filter_properties=filter_properties)

        if not hosts:
            # no hosts fitted. At least we cannot find the hosts
            # that matches capacity requirement. Log an error to
            # to volume meta data.

            # collect request related information
            volume_id = request_spec['volume_id']
            vol_properties = request_spec['volume_properties']
            req_size = vol_properties['size']

            # collect host_state information
            elevated = context.elevated()
            all_hosts = self.host_manager.get_all_host_states(elevated)

            # For now we are only focusing on the capacity.
            req_info = (_('volume request: '
                          'requested size: %(size)s. ') % {'size': req_size})

            info = ''
            for hstate_info in all_hosts:
                ts = timeutils.isotime(at=hstate_info.updated)
                info += (_("{host: %(hostname)s, free_capacity: %(free_cap)s, "
                           "total_capacity: %(total)s, reserved_percentage:"
                           " %(reserved)s, last update: %(time_updated)s}") %
                         {'hostname': hstate_info.host,
                          'free_cap': hstate_info.free_capacity_gb,
                          'total': hstate_info.total_capacity_gb,
                          'reserved': hstate_info.reserved_percentage,
                          'time_updated': ts})
            if len(info) > 0:
                msg = (_('request exceeds capacity: ' + req_info +
                         ('available capacity: %(info)s') %
                         {'info': info}))
            else:
                msg = (_("No storage has been registered. " + req_info))

            LOG.error(("Schedule Failure: volume_id: %s, " % volume_id) + msg)

            meta_data = {'schedule Failure description': msg[:255]}

            db.volume_update(context, volume_id, {'metadata': meta_data})

            return None
        else:
            return hosts
