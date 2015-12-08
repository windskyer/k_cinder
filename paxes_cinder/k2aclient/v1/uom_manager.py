#
#
# =================================================================
# =================================================================

"""Raw access to UOM."""


class UomManager(object):
    """Manage retrieval of a UOM."""

    def __init__(self, api):
        self.api = api

    def get(self, uom, xa=None):
        """Get a specific uom.

        :param uom: The UOM to get.
        :rtype: k2operator.readbypath()`
        """
        return self.api.client.get("/rest/api/uom%s" % uom,
                                   xa=xa)
