# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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
Handles all requests relating to volumes.
"""

from cinder import context
import cinder.policy
from cinder.volume import api
from paxes_cinder.volume import rpcapi as volume_rpcapi


class API(api.API):
    """API for interacting with the exist volume manager."""

    def __init__(self, db_driver=None, image_service=None):
        super(API, self).__init__(db_driver)
        self.volume_rpcapi = volume_rpcapi.VolumeAPI()


    def exist_volumes(self, context):
        lvs = self.volume_rpcapi.exist_volumes(context)
        return lvs

