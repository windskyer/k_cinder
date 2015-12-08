# Copyright 2012, Intel, Inc.
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
Client side of the volume RPC API.
"""

from oslo.config import cfg
from oslo import messaging

from cinder.openstack.common import jsonutils
from cinder import rpc
from cinder.volume import rpcapi


CONF = cfg.CONF

import logging
LOG = logging.getLogger(__name__)

class VolumeAPI(rpcapi.VolumeAPI):
    def exist_volumes(self, ctxt):
        cctxt = self.client.prepare(version='1.15')
        return cctxt.call(ctxt, 'exist_volumes')
