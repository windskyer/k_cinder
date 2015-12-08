#
#
# =================================================================
# =================================================================

"""P Database API Class for providing access to the Cinder Database"""

from cinder.openstack.common.db import api as common_db

_BACKEND_MAPPING = {'sqlalchemy': 'paxes_cinder.db.sqlalchemy.api'}
IMPL = common_db.DBAPI(backend_mapping=_BACKEND_MAPPING)


##################################################
##########    HMC DB API Definition    ###########
##################################################
def ibm_hmc_get_all(context):
    """ Retrieves all of the HMC's that are in the Database """
    return IMPL.ibm_hmc_get_all(context)


def ibm_hmc_get_all_by_cluster(context, host_name):
    """ Retrieves the HMC's for the given Host from the Database """
    return IMPL.ibm_hmc_get_all_by_cluster(context, host_name)


def ibm_hmc_get_by_uuid(context, hmc_uuid):
    """ Retrieves the HMC with the given UUID from the Database """
    return IMPL.ibm_hmc_get_by_uuid(context, hmc_uuid)


def ibm_hmc_create(context, values):
    """ Creates a new HMC instance in the Database """
    return IMPL.ibm_hmc_create(context, values)


def ibm_hmc_update(context, hmc_uuid, values):
    """ Updates an existing HMC instance in the Database """
    return IMPL.ibm_hmc_update(context, hmc_uuid, values)


def ibm_hmc_delete(context, hmc_uuid):
    """ Removes an existing HMC instance from the Database """
    return IMPL.ibm_hmc_delete(context, hmc_uuid)


def ibm_hmc_clusters_get_by_uuid(context, hmc_uuid):
    """ Retrieves the HMC/Cluster Mapping for a given UUID from the DB """
    return IMPL.ibm_hmc_clusters_get_by_uuid(context, hmc_uuid)


def ibm_hmc_clusters_create(context, hmc_uuid, host_name):
    """ Associates a new Host with the HMC in the Database """
    return IMPL.ibm_hmc_clusters_create(context, hmc_uuid, host_name)


def ibm_hmc_clusters_delete(context, hmc_uuid, host_name):
    """ Dissociates an existing Cluster from an HMC in the Database """
    return IMPL.ibm_hmc_clusters_delete(context, hmc_uuid, host_name)


##################################################
######## Storage Node DB API Definition ##########
##################################################
def storage_node_get_by_host(context, host):
    """Retrieves a Storage Node from the DB that maps to a given Host."""
    return IMPL.storage_node_get_by_host(context, host)


def storage_node_get_all(context):
    """Retrieves all of the Storage Nodes that are in the Database."""
    return IMPL.storage_node_get_all(context)


def storage_node_get(context, storage_id):
    """Retrieves an individual Storage Node from the Database."""
    return IMPL.storage_node_get(context, storage_id)


def storage_node_create(context, values):
    """Creates a new Storage Node instance in the Database."""
    return IMPL.storage_node_create(context, values)


def storage_node_update(context, storage_id, values):
    """Updates an existing Storage Node in the Database."""
    return IMPL.storage_node_update(context, storage_id, values)


def service_delete(context, service_id):
    """Deletes both a Service and the Storage Node from the Database."""
    return IMPL.service_delete(context, service_id)


#######################################################
######### Restricted Metadata DB API Implementation ###
#######################################################
def volume_restricted_metadata_get(context, volume_id):
    """Get all restricted metadata for a volume."""
    return IMPL.volume_restricted_metadata_get(context, volume_id)


def volume_restricted_metadata_delete(context, volume_id, key):
    """Delete the given restricted metadata item."""
    IMPL.volume_restricted_metadata_delete(context, volume_id, key)


def volume_restricted_metadata_update_or_create(context,
                                                volume_id,
                                                metadata):
    """Create or update restricted metadata. This adds or modifies the
    key/value pairs specified in the metadata dict argument
    """
    IMPL.volume_restricted_metadata_update_or_create(context,
                                                     volume_id,
                                                     metadata)


##################################################
######## On-board Task DB API Definition #########
##################################################
def onboard_task_get_all(context, host):
    """Retrieves all of the On-board Tasks from the DB."""
    return IMPL.onboard_task_get_all(context, host)


def onboard_task_get(context, task_id):
    """Retrieves one of the On-board Tasks from the DB."""
    return IMPL.onboard_task_get(context, task_id)


def onboard_task_create(context, host):
    """Creates the given On-board Task in the DB."""
    return IMPL.onboard_task_create(context, host)


def onboard_task_update(context, task_id, values):
    """Updates the given On-board Task in the DB."""
    return IMPL.onboard_task_update(context, task_id, values)


def onboard_task_delete(context, task_id):
    """Deletes the given On-board Task from the DB."""
    return IMPL.onboard_task_delete(context, task_id)


def onboard_task_volume_create(context, task_id, vol_uuid, values):
    """Create the Volume record for the given On-board Task"""
    return IMPL.onboard_task_volume_create(context, task_id, vol_uuid, values)


def onboard_task_volume_update(context, task_id, vol_uuid, values):
    """Updates the Volume record for the given On-board Task"""
    return IMPL.onboard_task_volume_update(context, task_id, vol_uuid, values)


##############################################################
######## P DB API Extension for Admin metadata #########
##############################################################
def ibm_volume_get_all_except_bootable(context):
    """ return a list of volumes that don't have 'is_boot_volume' key"""
    return IMPL.ibm_volume_get_all_except_bootable(context)
