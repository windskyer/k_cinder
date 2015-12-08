#
#
# =================================================================
# =================================================================

"""VirtualNetwork interface."""

from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom


class VirtualNetworkManager(base.ManagerWithFind):
    """Manage :class:`ClientNetworkAdapter` resources."""
    resource_class = k2uom.VirtualNetwork

    def new(self):
        return self.resource_class(self, None)

    def list(self, managedsystem, xa=None):
        """Get a list of all VirtualNetwork for a particular
        ManagedSystem accessed through a particular hmc.

        :rtype: list of :class:`ClientNetworkAdapter`.
        """
        return self._list("/rest/api/uom/ManagedSystem/%s/VirtualNetwork"
                          % managedsystem, xa=xa)

    def get(self, managedsystem, virtualnetwork, xa=None):
        """Given managedsystem, get a specific VirtualNetwork.

        :param virtualnetwork: The ID of the :class:`VirtualNetwork`.
        :rtype: :class:`VirtualNetwork`
        """
        return self._get("/rest/api/uom/ManagedSystem/%s/VirtualNetwork/%s"
                         % (managedsystem, virtualnetwork,),
                         xa=xa)

    def delete(self, managedsystem, virtualnetwork, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom", managedsystem,
                            child=virtualnetwork, xa=xa)

    def deletebyid(self, managedsystem_id, virtualnetwork_id,
                   xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom",
                                "ManagedSystem",
                                managedsystem_id,
                                child_type=k2uom.VirtualNetwork,
                                child_id=virtualnetwork_id,
                                xa=xa)
