# Copyright (c) 2011 OpenStack Foundation
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
Manage hosts in the current zone.
"""


from oslo.config import cfg 

from cinder import db
from cinder.scheduler import host_manager as hm
from cinder.openstack.common import log as logging
from cinder import utils

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

class ViosHostManager(hm.HostManager):

    def get_all_host_states(self, context):
        """Returns a dict of all the hosts the HostManager knows about.

        Each of the consumable resources in HostState are
        populated with capabilities scheduler received from RPC.

        For example:
          {'192.168.1.100': HostState(), ...}
        """
        # Get resource usage across the available volume nodes:
        topic = CONF.volume_topic
        volume_services = db.service_get_all_by_topic(context, topic)
        active_hosts = set()
        for service in volume_services:
            host = service['host']

            if not utils.service_is_up(service) or service['disabled']:
                LOG.warn(_("volume service is down or disabled. "
                           "(host: %s)") % host)
                continue
            capabilities = self.service_states.get(host, None)
            host_state = self.host_state_map.get(host)
            if host_state:
                # copy capabilities to host_state.capabilities
                host_state.update_capabilities(capabilities,
                                               dict(service.iteritems()))
            else:
                host_state = self.host_state_cls(host,
                                                 capabilities=capabilities,
                                                 service=
                                                 dict(service.iteritems()))
                self.host_state_map[host] = host_state
            # update attributes in host_state that scheduler is interested in
            host_state.update_from_volume_capability(capabilities)
            active_hosts.add(host)
            
            if context.host and context.host == host:
                active_hosts = set()
                active_hosts.add(host)
                break
        # remove non-active hosts from host_state_map
        nonactive_hosts = set(self.host_state_map.keys()) - active_hosts
        for host in nonactive_hosts:
            LOG.info(_("Removing non-active host: %(host)s from "
                       "scheduler cache.") % {'host': host})
            del self.host_state_map[host]
        return self.host_state_map.itervalues()
    
