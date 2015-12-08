#
#
# =================================================================
# =================================================================

"""VirtualSwitch interface."""

from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom


class VirtualSwitchManager(base.ManagerWithFind):
    """Manage :class:`ClientNetworkAdapter` resources."""
    resource_class = k2uom.VirtualSwitch

    def new(self):
        return self.resource_class(self, None)

    def list(self, managedsystem, xa=None):
        """Get a list of all VirtualSwitch for a particular
        ManagedSystem accessed through a particular hmc.

        :rtype: list of :class:`ClientNetworkAdapter`.
        """
        return self._list("/rest/api/uom/ManagedSystem/%s/VirtualSwitch"
                          % managedsystem, xa=xa)

    def get(self, managedsystem, virtualswitch, xa=None):
        """Given managedsystem, get a specific VirtualSwitch.

        :param virtualswitch: The ID of the :class:`VirtualSwitch`.
        :rtype: :class:`VirtualSwitch`
        """
        return self._get("/rest/api/uom/ManagedSystem/%s/VirtualSwitch/%s"
                         % (managedsystem, virtualswitch,),
                         xa=xa)

    def delete(self, managedsystem, virtualswitch, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom",
                            managedsystem,
                            child=virtualswitch,
                            xa=xa)

    def deletebyid(self, managedsystem_id, virtualswitch_id, xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom",
                                "ManagedSystem",
                                managedsystem_id,
                                child_type=k2uom.VirtualSwitch,
                                child_id=virtualswitch_id,
                                xa=xa)
