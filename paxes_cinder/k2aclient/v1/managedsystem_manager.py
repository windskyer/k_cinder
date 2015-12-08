#
#
# =================================================================
# =================================================================

"""ManagedSystem interface."""

from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom


class ManagedSystemManager(base.ManagerWithFind):
    """Manage :class:`ManagedSystem` resources."""
    resource_class = k2uom.ManagedSystem

    def list(self, xa=None):
        """Get a list of all ManagedSystems.

        :rtype: list of :class:`ManagedSystem`.
        """
        return self._list("/rest/api/uom/ManagedSystem", xa=xa)

    def get(self, managedsystem, xa=None):
        """Get a specific ManagedSystem.

        :param managedsystem: The ID of the :class:`ManagedSystem` to get.
        :rtype: :class:`ManagedSystem`
        """
        return self._get("/rest/api/uom/ManagedSystem/%s" % managedsystem,
                         xa=xa)

    def create(self, managedsystem, child=None, xa=None):
        """Create the specified instance
        """
        return self._create("uom", managedsystem, child, xa=xa)

    def update(self, managedsystem, child=None, xa=None):
        """Update the specified instance
        """
        return self._update("uom", managedsystem, child=child, xa=xa)

    def delete(self, managedsystem, child=None, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom", managedsystem,
                            child=child, xa=xa)

    def deletebyid(self, managedsystem_id,
                   child_type=None, child_id=None, xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom", "ManagedSystem", managedsystem_id,
                                child_type, child_id, xa=xa)
