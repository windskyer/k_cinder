#
#
# =================================================================
# =================================================================

"""Extended Volume Driver interface to discover/query resource information"""


class VolumeDiscoveryDriver(object):
    """
    Extended Volume Driver interface for drivers to implementation to
    discover/query additional resource information from the managed system.

    The base VolumeDriver interface provides methods to take actions on the
    Storage Provider and its Volumes but given the premise that OpenStack is
    the authoritative management source for the Hosts being managed, it assumes
    the resources created by OpenStack are an accurate representation of the
    current state of the resources, so it provides very limited information
    through the driver interface about those resources.

    This interface extends those driver capabilities by asking the driver to
    provide 4 levels of information about the resources being managed:
        1) discover - provide a list of all Volumes that exist on the Provider
        2) query - provide enough info about the Volumes to import into OS
        3) inventory - provide additional details about the Volumes specified
        4) metrics - provide additional metric information about the Volumes
    """

    def discover_volumes(self, context, filters=None):
        """
        Returns a list of all of the Volumes that exist on the given Provider.
        For each Volumes the driver needs to return a dictionary containing
        the following attributes:
            name:      The Name of the Volume defined on the Storage Provider
            status:    The Status of the Volume, matching the status definition
            uuid:      The UUID of the VM when created thru OS (Optional)
            status:    The Status of the Volume, matching the definition
            size:      The Size of the Volume in GB
            restricted_metadata: The Additional Meta-data from the Driver
              vdisk_id:   The Identifier for the Volume on the Back-end
              vdisk_name: The Name of the Volume on the Back-end
            support:   Dictionary stating whether the Volume can be managed
              status:  Whether or not it is "supported" or "not_supported"
              reasons: List of Text Strings as to why it isn't supported

        :param context:   The security context for the query
        :param filters:   The filters to apply, such as {'wwpns': ['wwpn1',..]
        """
        raise NotImplementedError()

    def query_volumes(self, context, volumes, server_info={}, mark_boot=True):
        """
        Returns a list of Volumes (matching those specified on input) with
        enough additional details about each Volume to be able to import the
        Volume into the Cinder Database such as OpenStack can start managing.
        For each Volume the driver needs to return a dictionary containing
        the following attributes:
            uuid:      The UUID of the Volume when created thru OS
            name:      The Name of the Volume defined on the Storage Provider
            status:    The Status of the Volume, matching the definition
            size:      The Size of the Volume in GB
            restricted_metadata: The Additional Meta-data from the Driver
              vdisk_id:   The Identifier for the Volume on the Back-end
              vdisk_name: The Name of the Volume on the Back-end

        :param context:   The security context for the query
        :param volumes: A list of dictionary objects for each Volume with:
            uuid:      The UUID of the Volume when created thru OS
            name:      The Name of the Volume defined on the Storage Provider
            restricted_metadata: The Additional Meta-data from the Driver
              vdisk_id:   The Identifier for the Volume on the Back-end
              vdisk_name: The Name of the Volume on the Back-end
        :param server_info: The host info for the attached servers
        """
        #Currently the discover/query methods return the same data, so we can
        #return the values passed in since discover was called to get the info
        return volumes

    def inventory_volumes(self, context, volumes):
        """
        Provides a mechanism for the Driver to gather Inventory-related
        information for the Volumes provided off of the Back-end at
        periodic intervals.  The Driver is free from there to populate
        the information directly in the Database rather than return it.

        :param context: The security context for the query
        :param volumes: A list of dictionary objects for each Volume with:
            uuid:      The UUID of the Volume when created thru OS
            name:      The Name of the Volume defined on the Storage Provider
            restricted_metadata: The Additional Meta-data from the Driver
              vdisk_id:   The Identifier for the Volume on the Back-end
              vdisk_name: The Name of the Volume on the Back-end
        """
        pass
