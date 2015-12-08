# Copyright (c) 2011 Intel Corporation
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
The FilterScheduler is for creating volumes.
You can customize this scheduler by specifying your own volume Filters and
Weighing Functions.
"""

from oslo.config import cfg 

from cinder import exception
from cinder.openstack.common import log as logging
from cinder.scheduler import driver
from cinder.scheduler import filter_scheduler as filter

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

class ViosFilterScheduler(filter.FilterScheduler):

    def schedule(self, context, topic, method, *args, **kwargs):
        """The schedule() contract requires we return the one
        best-suited host for this request.
        """
        self._schedule(context, topic, *args, **kwargs)
    def schedule_create_volume(self, context, request_spec, filter_properties):
        weighed_host = self._schedule(context, request_spec,
                                      filter_properties)
        if not weighed_host:
            raise exception.NoValidHost(reason="")
        
        host = weighed_host.obj.host
        volume_id = request_spec['volume_id']
        snapshot_id = request_spec['snapshot_id']
        image_id = request_spec['image_id']

        updated_volume = driver.volume_update_db(context, volume_id, host)
        self._post_select_populate_filter_properties(filter_properties,
                                                     weighed_host.obj)

        # context is not serializable
        filter_properties.pop('context', None)

        self.volume_rpcapi.create_volume(context, updated_volume, host,
                                         request_spec, filter_properties,
                                         allow_reschedule=True,
                                         snapshot_id=snapshot_id,
                                         image_id=image_id)


    def _get_weighted_candidates(self, context, request_spec,
                                 filter_properties=None):
        """Returns a list of hosts that meet the required specs,
        ordered by their fitness.
        """
        metadata =  request_spec['volume_properties'].get('metadata')
        if metadata and metadata.has_key('host'):
            host = metadata['host']
            context.host = host
        else:
            context.host = ""
        elevated = context.elevated()

        volume_properties = request_spec['volume_properties']
        # Since Cinder is using mixed filters from Oslo and it's own, which
        # takes 'resource_XX' and 'volume_XX' as input respectively, copying
        # 'volume_XX' to 'resource_XX' will make both filters happy.
        resource_properties = volume_properties.copy()
        volume_type = request_spec.get("volume_type", None)
        resource_type = request_spec.get("volume_type", None)
        request_spec.update({'resource_properties': resource_properties})

        config_options = self._get_configuration_options()

        if filter_properties is None:
            filter_properties = {}
        self._populate_retry(filter_properties, resource_properties)

        filter_properties.update({'context': context,
                                  'request_spec': request_spec,
                                  'config_options': config_options,
                                  'volume_type': volume_type,
                                  'resource_type': resource_type})
        self.populate_filter_properties(request_spec,
                                        filter_properties)

        # Find our local list of acceptable hosts by filtering and
        # weighing our options. we virtually consume resources on
        # it so subsequent selections can adjust accordingly.

        # Note: remember, we are using an iterator here. So only
        # traverse this list once.
        hosts = self.host_manager.get_all_host_states(elevated)
        # Filter local hosts based on requirements ...
        hosts = self.host_manager.get_filtered_hosts(hosts,
                                                     filter_properties)
        if not hosts:
            return []

        LOG.debug(_("Filtered %s") % hosts)
        # weighted_host = WeightedHost() ... the best
        # host for the job.
        weighed_hosts = self.host_manager.get_weighed_hosts(hosts,
                                                            filter_properties)
        if len(weighed_hosts) > 0:
            return weighed_hosts
        else:
            return []
        #return weighed_hosts

