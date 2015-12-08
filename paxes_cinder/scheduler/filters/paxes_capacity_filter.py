# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright (c) 2012 Intel
# Copyright (c) 2012 OpenStack Foundation
#
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

import re

from cinder.openstack.common import log as logging
from cinder.openstack.common.scheduler import filters

from paxes_cinder import _

LOG = logging.getLogger(__name__)


class PowerVCCapacityFilter(filters.BaseHostFilter):
    """
    PowerVCCapacityFilter filters based on capacity utilization if known.
    If the volume host is an SVC, accounts for rsize (thin provisioning).
    """

    def _is_svc(self, host_state):
        if 'location_info' in host_state.capabilities:
            location_info = host_state.capabilities['location_info']
            return re.match('StorwizeSVCDriver.*', location_info)
        return False

    def host_passes(self, host_state, filter_properties):
        """Return True if host has sufficient capacity or is not an SVC."""
        LOG.debug('filter_properties=%s' % filter_properties)
        LOG.debug(('host=%(host)s, '
                   'capabilities=%(capabilities)s, '
                   'service=%(service)s, '
                   'volume_backend_name=%(volume_backend_name)s, '
                   'vendor_name=%(vendor_name)s, '
                   'driver_version=%(driver_version)s, '
                   'storage_protocol=%(storage_protocol)s, '
                   'QoS_support=%(QoS_support)s, '
                   'total_capacity_gb=%(total_capacity_gb)s, '
                   'free_capacity_gb=%(free_capacity_gb)s, '
                   'reserved_percentage=%(reserved_percentage)s')
                  % vars(host_state))

        if host_state.free_capacity_gb is None:
            # Fail Safe
            # When the volume driver takes long time to initialize, the
            # volume state won't be collected until the end of init_host.
            # The volume create request comes in before it is fully
            #initialized will get this warning.
            LOG.warn(_("Free capacity not set: "
                       "Volume node is either still under initialization or "
                       "the node info collection is broken."))
            return False

        free_space = host_state.free_capacity_gb
        if free_space == 'infinite' or free_space == 'unknown':
            # NOTE(zhiteng) for those back-ends cannot report actual
            # available capacity, we assume it is able to serve the
            # request.  Even if it was not, the retry mechanism is
            # able to handle the failure by rescheduling
            return True

        volume_size = filter_properties.get('size')
        reserved = float(host_state.reserved_percentage) / 100
        free = free_space * (1 - reserved)

        rsize = -1
        if not self._is_svc(host_state):
            LOG.debug('host is not an SVC')
        else:
            # Determine rsize
            volume_type = filter_properties.get('volume_type', {})
            using_default = False
            if not volume_type:
                # Use host's default if requester didn't specify
                using_default = True
                capabilities = host_state.capabilities
                volume_type = capabilities.get('default_volume_type', {})
            if not volume_type:
                # someone may have deleted the default
                # in which case create will use rsize -1
                LOG.warn(_("missing default_volume_type"))
            else:
                extra_specs = volume_type.get('extra_specs', {})
                try:
                    rsize = float(extra_specs['drivers:rsize'])
                except:
                    default = 'default_' if using_default else ''
                    LOG.warn(_("missing valid rsize on \
                                %(default)svolume_type: %(vol_type)s")
                             % dict(default=default,
                                    vol_type=volume_type))

        if rsize == -1:
            sufficient = (free >= volume_size)
        else:
            sufficient = (free >= (volume_size * rsize / 100))

        if not sufficient:
            LOG.warning(_("Insufficient free space for volume creation "
                          "(requested / avail / rsize): "
                          "%(requested)s/%(available)s/%(rsize)s")
                        % {'requested': volume_size,
                           'available': free,
                           'rsize': rsize})
        else:
            LOG.debug(_("Sufficient free space for volume creation "
                        "(requested / avail / rsize): "
                        "%(requested)s/%(available)s/%(rsize)s")
                      % {'requested': volume_size,
                         'available': free,
                         'rsize': rsize})

        return sufficient
