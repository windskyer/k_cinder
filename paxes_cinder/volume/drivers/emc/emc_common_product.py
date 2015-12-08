# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright (c) 2012 EMC Corporation.
# Copyright (c) 2012 OpenStack Foundation
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


from cinder.volume.drivers.emc import emc_smis_common
from cinder.volume.drivers.emc.emc_smis_common import *
from cinder import units
from paxes_cinder import _


class EMCCommonProductDriver(emc_smis_common.EMCSMISCommon):
    def __init__(self, prtcl, configuration=None):
        emc_smis_common.EMCSMISCommon.__init__(self, prtcl, configuration)

    def update_volume_status(self):
        """Retrieve status info."""
        LOG.debug(_("Updating volume status"))
        self.conn = self._get_ecom_connection()
        storage_type = self._get_storage_type()
        pool, storagesystem = self._find_pool(storage_type, True)
        self.stats['total_capacity_gb'] = ((pool['TotalManagedSpace'])
                                           / int(units.GiB))
        self.stats['free_capacity_gb'] = ((pool['RemainingManagedSpace'])
                                          / int(units.GiB))
        return self.stats
