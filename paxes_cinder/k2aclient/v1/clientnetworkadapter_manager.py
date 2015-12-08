#
#
# =================================================================
# =================================================================

"""ClientNetworkAdapter interface."""

from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom


class ClientNetworkAdapterManager(base.ManagerWithFind):
    """Manage :class:`ClientNetworkAdapter` resources."""
    resource_class = k2uom.ClientNetworkAdapter

    def new(self):
        return self.resource_class(self, None)

    def list(self, logicalpartition, xa=None):
        """Get a list of all ClientNetworkAdapters for a particular
        LogicalPartition accessed through a particular hmc.

        :rtype: list of :class:`ClientNetworkAdapter`.
        """
        x = "/rest/api/uom/LogicalPartition/%s/ClientNetworkAdapter"
        return self._list(x % logicalpartition, xa=xa)

    def get(self, logicalpartition, clientnetworkadapter, xa=None):
        """Given logicalpartition, get a specific ClientNetworkAdapter.

        :param clientnetworkadapter: The ID of the :class:
            `ClientNetworkAdapter`.
        :rtype: :class:`ClientNetworkAdapter`
        """
        x = "/rest/api/uom/LogicalPartition/%s/ClientNetworkAdapter/%s"
        return self._get(x % (logicalpartition, clientnetworkadapter,),
                         xa=xa)

    def delete(self, logicalpartition, clientnetworkadapter, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom",
                            logicalpartition,
                            child=clientnetworkadapter,
                            xa=xa)

    def deletebyid(self,
                   logicalpartition_id,
                   clientnetworkadapter_id,
                   xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom", "LogicalPartition",
                                logicalpartition_id,
                                k2uom.ClientNetworkAdapter,
                                clientnetworkadapter_id,
                                xa=xa)
