#
#
# =================================================================
# =================================================================

"""P SQL Alchemy DB API Implementation Class to wrapper DB access"""

import sys
from oslo.config import cfg
from sqlalchemy.sql.expression import literal_column

from cinder import exception
import cinder.db.sqlalchemy.api as cinder_db
import cinder.db.sqlalchemy.models as cinder_models
from sqlalchemy.orm import joinedload
from sqlalchemy import not_
from cinder.openstack.common import log as logging
from cinder.openstack.common import jsonutils
from cinder.openstack.common import timeutils

from paxes_cinder.db.sqlalchemy import models as paxes_models

# del one lines by lixx
#from paxes_keystone.encrypthandler import EncryptHandler

LOG = logging.getLogger(__name__)


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def model_query(context, model, *args, **kwargs):
    """ Wrappers the Base Model Query to provide PowerVC-specific logic """
    return cinder_db.model_query(context, model, *args, **kwargs)


####################################################
#########    HMC DB API Implementation    ##########
####################################################
def ibm_hmc_get_all(context, session=None):
    """ Retrieves all of the HMC's that are in the Database """
    hmcs = []
    query = model_query(context, paxes_models.HmcDTO, session=session)
    hmc_refs = query.all()
    for hmc_ref in hmc_refs:
        hmcs.append(_decode_hmc_values(hmc_ref))
    return hmcs


def ibm_hmc_get_all_by_cluster(context, host_name, session=None):
    """ Retrieves the HMC's for the given Cluster from the Database """
    hmcs = []
    #Query the DB to figure out which HMC's we should look up
    query = model_query(
        context, paxes_models.HmcClustersDTO, session=session)
    hmc_clusters = query.filter_by(host_name=host_name).all()
    #Loop through each of the UUID's, adding the HMC to the list
    for hmc_cluster in hmc_clusters:
        hmc = ibm_hmc_get_by_uuid(context, hmc_cluster['hmc_uuid'], session)
        if hmc:
            hmcs.append(hmc)
    return hmcs


def ibm_hmc_get_by_uuid(context, hmc_uuid, session=None):
    """ Retrieves the HMC with the given UUID from the Database """
    #If this is an invalid UUID, return None rather than blowing up
    if hmc_uuid is None or len(hmc_uuid) <= 0 or len(hmc_uuid) > 36:
        return None
    query = model_query(context, paxes_models.HmcDTO, session=session)
    hmc_ref = query.filter_by(hmc_uuid=hmc_uuid).first()
    return _decode_hmc_values(hmc_ref)


def ibm_hmc_create(context, values, session=None):
    """ Creates a new HMC instance in the Database """
    hmc_ref = paxes_models.HmcDTO()
    values = _encode_hmc_values(values)
    hmc_ref.update(values)
    hmc_ref.save(session=session)
    return _decode_hmc_values(hmc_ref)


def ibm_hmc_update(context, hmc_uuid, values, session=None):
    """ Updates an existing HMC instance in the Database """
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        query = model_query(context, paxes_models.HmcDTO, session=session)
        hmc_ref = query.filter_by(hmc_uuid=hmc_uuid).first()
        values = _encode_hmc_values(values)
        hmc_ref.update(values)
        hmc_ref.save(session=session)
    return _decode_hmc_values(hmc_ref)


def ibm_hmc_delete(context, hmc_uuid, session=None):
    """ Removes an existing HMC instance from the Database """
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        query = model_query(context, paxes_models.HmcDTO, session=session)
        hmc = query.filter_by(hmc_uuid=hmc_uuid).first()
        if hmc:
            hmc.delete(session=session)


def ibm_hmc_clusters_get_by_uuid(context, hmc_uuid, session=None):
    """ Retrieves the HMC/Clusters Mapping for a given UUID from the DB """
    query = model_query(
        context, paxes_models.HmcClustersDTO, session=session)
    return query.filter_by(hmc_uuid=hmc_uuid).all()


def ibm_hmc_clusters_create(context, hmc_uuid, host_name, session=None):
    """ Associates a new Cluster with the HMC in the Database """
    hmchosts_ref = paxes_models.HmcClustersDTO()
    hmchosts_ref.update({'hmc_uuid': hmc_uuid, 'host_name': host_name})
    hmchosts_ref.save(session=session)
    return hmchosts_ref


def ibm_hmc_clusters_delete(context, hmc_uuid, host_name, session=None):
    """ Dissociates an existing Cluster from an HMC in the Database """
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        query = model_query(
            context, paxes_models.HmcClustersDTO, session=session)
        query = query.filter_by(hmc_uuid=hmc_uuid, host_name=host_name)
        hmc_cluster = query.first()
        if hmc_cluster:
            hmc_cluster.delete(session=session)


def _encode_hmc_values(values):
    """Encrypts any necessary sensitive values for the HMC entry"""
    if values is not None:
        values = values.copy()
        #Make sure to Encrypt the Password before inserting the database
        ## del two lines by lixx
        #if values.get('password') is not None:
        #    values['password'] = EncryptHandler().encode(values['password'])
    return values


def _decode_hmc_values(hmc_ref):
    """Decrypts any sensitive HMC values that were encrypted in the DB"""
    if hmc_ref is not None:
        hmc_ref = jsonutils.to_primitive(hmc_ref)
        #Make sure to DeCrypt the Password after retrieving from the database
        ## del two lines by lixx
        #if hmc_ref.get('password') is not None:
        #    hmc_ref['password'] = EncryptHandler().decode(hmc_ref['password'])
    return hmc_ref


#######################################################
######### Storage Node DB API Implementation ##########
#######################################################
def storage_node_get_by_host(context, host, session=None):
    """Retrieves a Storage Node from the DB that maps to a given Host."""
    query = model_query(
        context, cinder_models.Service, session=session, read_deleted="no")
    result = query.filter_by(host=host).\
        filter_by(topic=cfg.CONF.volume_topic).first()
    #If we were able to find the Service for the Host, get the matching Node
    if result:
        query = model_query(
            context, paxes_models.StorageNodeDTO, session=session)
        return query.filter_by(service_id=result['id']).first()
    return None


def storage_node_get_all(context, session=None):
    """Retrieves all of the Storage Nodes that are in the Database."""
    query = model_query(
        context, paxes_models.StorageNodeDTO, session=session)
    return query.all()


def storage_node_get(context, storage_id, session=None):
    """Retrieves an individual Storage Node from the Database."""
    query = model_query(
        context, paxes_models.StorageNodeDTO, session=session)
    return query.filter_by(id=storage_id).first()


def storage_node_create(context, values, session=None):
    """Creates a new Storage Node instance in the Database."""
    node_ref = paxes_models.StorageNodeDTO()
    node_ref.update(values)
    node_ref.save(session=session)
    return node_ref


def storage_node_update(context, storage_id, values, session=None):
    """Updates an existing Storage Node in the Database."""
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        node_ref = storage_node_get(context, storage_id, session=session)
        if node_ref:
            node_ref.update(values)
            node_ref.save(session=session)
    return node_ref


def storage_node_delete(context, storage_id, session=None):
    """Deletes an existing Storage Node from the Database."""
    query = model_query(
        context, paxes_models.StorageNodeDTO, session=session)
    storage_node = query.filter_by(id=storage_id).first()
    if storage_node:
        storage_node.delete(session=session)


def service_delete(context, service_id, session=None):
    """Deletes both a Service and the Storage Node from the Database."""
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        #First we want to cleanup the actual Service entry from the DB
        query = model_query(
            context, cinder_models.Service, session=session)
        service = query.filter_by(id=service_id).first()
        if service:
            service.delete(session=session)
        #Then we want to cleanup the related Storage Node entry from the DB
        query = model_query(
            context, paxes_models.StorageNodeDTO, session=session)
        storage_node = query.filter_by(service_id=service_id).first()
        if storage_node:
            storage_node.delete(session=session)

#######################################################
######### Restricted Metadata DB API Implementation ###
#######################################################


def _volume_restricted_metadata_query(context, volume_id, session=None):
    return model_query(context,
                       paxes_models.VolumeRestrictedMetadataDTO,
                       session=session,
                       read_deleted="no").filter_by(volume_id=volume_id)


def _volume_restricted_metadata_get_item(context, volume_id, key,
                                         session=None):
    result = _volume_restricted_metadata_query(
        context, volume_id, session=session).\
        filter_by(key=key).\
        first()

    if not result:
        raise exception.VolumeMetadataNotFound(
            metadata_key=key,
            volume_id=volume_id)

    return result


def volume_restricted_metadata_get(context, volume_id):
    rows = _volume_restricted_metadata_query(context, volume_id).all()

    result = {}
    for row in rows:
        result[row['key']] = row['value']

    return result


def volume_restricted_metadata_delete(context, volume_id, key):
    session = cinder_db.get_session()
    # Ensure that it exists, throw exception if it doesn't
    _volume_restricted_metadata_get_item(context, volume_id, key, session)

    # Flag the item as deleted.
    _volume_restricted_metadata_query(context, volume_id).\
        filter_by(key=key).\
        update({'deleted': True,
                'deleted_at': timeutils.utcnow(),
                'updated_at': literal_column('updated_at')})


def volume_restricted_metadata_update_or_create(context, volume_id,
                                                metadata):
    session = cinder_db.get_session()
    metadata_ref = None
    for key, value in metadata.iteritems():
        try:
            metadata_ref = _volume_restricted_metadata_get_item(
                context, volume_id, key, session)
        except exception.VolumeMetadataNotFound:
            metadata_ref = paxes_models.VolumeRestrictedMetadataDTO()
        metadata_ref.update({"key": key, "value": value,
                             "volume_id": volume_id,
                             "deleted": False})
        metadata_ref.save(session=session)
    return metadata


##################################################
###### On-board Task DB API Implementation #######
##################################################
def onboard_task_get_all(context, host, session=None):
    """Retrieves all of the On-board Tasks from the DB."""
    query = model_query(
        context, paxes_models.OnboardTaskDTO, session=session)
    return query.filter_by(host=host).all()


def onboard_task_get(context, task_id, session=None):
    """Retrieves one of the On-board Tasks from the DB."""
    query = model_query(
        context, paxes_models.OnboardTaskDTO, session=session)
    result = query.filter_by(id=task_id).first()
    #If we got a Task back, we need to append the Server records to it
    if result:
        result['volumes'] = []
        #Query the onboard_task_servers table to get the associated records
        query2 = model_query(
            context, paxes_models.OnboardTaskVolumeDTO, session=session)
        result2 = query2.filter_by(task_id=task_id).all()
        #Loop through each returned row and add it to the primary object
        for server in result2:
            result['volumes'].append(server)
    return result


def onboard_task_create(context, host, session=None):
    """Creates the given On-board Task in the DB."""
    task_ref = paxes_models.OnboardTaskDTO()
    task_ref.update(dict(host=host))
    task_ref.save(session=session)
    return task_ref


def onboard_task_update(context, task_id, values, session=None):
    """Updates the given On-board Task in the DB."""
    values = dict([(k, v) for k, v in values.iteritems() if v is not None])
    status = values.get('status', '')
    #If this is a final status, then set the end date/time
    if status == 'completed' or status == 'failed':
        values['ended'] = timeutils.utcnow()
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        query = model_query(
            context, paxes_models.OnboardTaskDTO, session=session)
        task_ref = query.filter_by(id=task_id).first()
        task_ref.update(values)
        task_ref.save(session=session)
    return task_ref


def onboard_task_delete(context, task_id, session=None):
    """Deletes the given On-board Task from the DB."""
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        #We need to cleanup both the Task and Task Server tables
        query1 = model_query(
            context, paxes_models.OnboardTaskDTO, session=session)
        query2 = model_query(
            context, paxes_models.OnboardTaskVolumeDTO, session=session)
        #Filter both tables on the Task ID that was given as input
        task = query1.filter_by(task_id=task_id).first()
        task_volumes = query2.filter_by(task_id=task_id).all()
        #Make sure to delete from the Task Server table first
        for task_volume in task_volumes:
            task_volume.delete(session=session)
        if task:
            task.delete(session=session)


def onboard_task_volume_create(context, task_id,
                               vol_uuid, values, session=None):
    """Create the Volume record for the given On-board Task"""
    values = dict(values)
    values['task_id'] = task_id
    values['volume_uuid'] = vol_uuid
    task_ref = paxes_models.OnboardTaskVolumeDTO()
    task_ref.update(values)
    task_ref.save(session=session)
    return task_ref


def onboard_task_volume_update(context, task_id,
                               vol_uuid, values, session=None):
    """Updates the Volume record for the given On-board Task"""
    values = dict([(k, v) for k, v in values.iteritems() if k is not None])
    if not session:
        session = cinder_db.get_session()
    with session.begin():
        query = model_query(
            context, paxes_models.OnboardTaskVolumeDTO, session=session)
        task_ref = query.filter_by(task_id=task_id,
                                   volume_uuid=vol_uuid).first()
        task_ref.update(values)
        task_ref.save(session=session)
    return task_ref


def _ibm_volume_get_all_except_key_query(context,
                                         key=None,
                                         session=None):
    # Find all the ids in volumes that has is_boot_volume key in
    # volume_metadata table. Create a subquery.
    if not session:
        # it takes ~ 4s to get_session for the first time.
        session = cinder_db.get_session()
    with session.begin():
        boot_vols = model_query(context,
                                cinder_models.Volume.id,
                                session=session).\
            join("volume_metadata").\
            filter(cinder_models.VolumeMetadata.key == key).\
            subquery()
        # Filter out all the boot volumes
        if cinder_db.is_admin_context(context):
            return model_query(context,
                               cinder_models.Volume,
                               session=session).\
                options(joinedload('volume_metadata')).\
                options(joinedload('volume_admin_metadata')).\
                filter(not_(cinder_models.Volume.id.in_(boot_vols)))
        else:
            return model_query(context,
                               cinder_models.Volume,
                               session=session).\
                options(joinedload('volume_metadata')).\
                filter(not_(cinder_models.Volume.id.in_(boot_vols)))


def _ibm_volume_get_all_except_key_all(context,
                                       key=None,
                                       session=None):
    items = _ibm_volume_get_all_except_key_query(context,
                                                 key=key,
                                                 session=session).all()
    if not items:
        raise exception.NotFound
    return items


def ibm_volume_get_all_except_bootable(context, session=None):
    """select all the volumes from volume table that have no is_boot_volume key
    in volume_metadata table
    """
    vols = _ibm_volume_get_all_except_key_all(context,
                                              key='is_boot_volume',
                                              session=session)
    return vols
