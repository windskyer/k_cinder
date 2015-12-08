# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#    (c) Copyright 2013 Brocade Communications Systems Inc.
#    All Rights Reserved.
#
#    Copyright 2013 OpenStack LLC
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
#


"""
Common constants used by Brocade FC Zone Driver
"""
EMPTY = ''
SPACE = ' '
COMMA = ','
YES = 'y'
ACTIVE_ZONE_CONFIG = 'active_zone_config'
CFG_ZONESET = 'cfg:'
CFG_ZONES = 'zones'
OPENSTACK_CFG_NAME = 'OpenStack_Cfg'
SUCCESS = 'Success'
TRANS_ABORTABLE = 'It is abortable'

"""
CLI Commands for FC zoning operations
"""
GET_ACTIVE_ZONE_CFG = 'cfgactvshow'
ZONE_CREATE = 'zonecreate' + SPACE
ZONESET_CREATE = 'cfgcreate' + SPACE
CFG_SAVE = 'cfgsave'
CFG_ADD = 'cfgadd' + SPACE
ACTIVATE_ZONESET = 'cfgenable' + SPACE
DEACTIVATE_ZONESET = 'cfgdisable'
CFG_DELETE = 'cfgdelete' + SPACE
CFG_REMOVE = 'cfgremove' + SPACE
ZONE_DELETE = 'zonedelete' + SPACE
CFG_SHOW_TRANS = 'cfgtransshow'
CFG_ZONE_TRANS_ABORT = 'cfgtransabort'
NS_SHOW = 'nsshow'
NS_CAM_SHOW = 'nscamshow'
