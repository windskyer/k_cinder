#
# =================================================================
# =================================================================
"""
Cinder extensions:
This is the object-relational mapping (ORM) for P's Cinder sub-domains.
It defines the mappings between P resource types, such as StorageNode
and each type's corresponding database table.
Using SqlAlchemy, each resource type is mapped as Data Transfer Object,
such as StorageNodeDTO, because it has attributes but no behavior.
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

from cinder.openstack.common import log as logging
from cinder.openstack.common import timeutils
import cinder.db.sqlalchemy.models as cinder_models

NAME_LEN = 255
DESC_LEN = 1023
UUID_LEN = 36
STATUS_LEN = 31
USER_LEN = 63
CRED_LEN = 255
IP_LEN = 39
MODE_LEN = 31

LOG = logging.getLogger(__name__)


######################################################
#############    HMC Model Definition    #############
######################################################
class HmcDTO(cinder_models.BASE, cinder_models.CinderBase):
    """The HmcDTO class provides the ORM for the ibm_hmcs table"""
    __tablename__ = 'ibm_hmcs'
    __table_args__ = ()
    #HMC DTO Model Attributes
    id = Column('id', Integer, primary_key=True)
    hmc_uuid = Column('uuid', String(UUID_LEN), nullable=False)
    hmc_display_name = Column('display_name', String(NAME_LEN), nullable=False)
    access_ip = Column('access_ip', String(NAME_LEN), nullable=False)
    user_id = Column('user_id', String(USER_LEN), nullable=False)
    password = Column('user_credentials', String(CRED_LEN), nullable=False)
    registered_at = Column('registered_at', DateTime, default=timeutils.utcnow)


class HmcClustersDTO(cinder_models.BASE, cinder_models.CinderBase):
    """The HmcClustersDTO class provides the ORM for the hmc_clusters table"""
    __tablename__ = 'ibm_hmc_clusters'
    __table_args__ = ()
    #HMC Clusters DTO Model Attributes
    id = Column('id', Integer, primary_key=True)
    hmc_uuid = Column('hmc_uuid', String(UUID_LEN), nullable=False)
    host_name = Column('host_name', String(NAME_LEN), nullable=False)


######################################################
##########  Storage Node Model Definition  ###########
######################################################
class StorageNodeDTO(cinder_models.BASE, cinder_models.CinderBase):
    """The StorageNodeDTO class provides the ORM for storage_nodes table"""
    __tablename__ = 'storage_nodes'
    __table_args__ = ()
    #Storage Node DTO Model Attributes
    id = Column('id', Integer, primary_key=True)
    service_id = Column('service_id', Integer,
                        ForeignKey('services.id'), nullable=False)
    storage_hostname = Column('storage_hostname',
                              String(NAME_LEN), nullable=False)
    backend_state = Column('backend_state', String(STATUS_LEN))
    backend_type = Column('backend_type', String(MODE_LEN))
    backend_id = Column('backend_id', String(NAME_LEN))
    total_capacity_gb = Column('total_capacity_gb', Float)
    free_capacity_gb = Column('free_capacity_gb', Float)
    volume_count = Column('volume_count', Integer)


######################################################
###########   Meta-data Model Definition  ############
######################################################
class VolumeRestrictedMetadataDTO(cinder_models.BASE,
                                  cinder_models.CinderBase):
    """The VolumeMetaDTO class provides the ORM for restricted_meta table"""
    __tablename__ = 'volume_restricted_metadata'
    #Volume Restricted Meta-data DTO Model Attributes
    id = Column(Integer, primary_key=True)
    key = Column(String(NAME_LEN))
    value = Column(String(NAME_LEN))
    volume_id = Column(String(UUID_LEN),
                       ForeignKey('volumes.id'), nullable=False)
    #Volume Restricted Meta-data DTO Model Relationships
    volume = relationship(cinder_models.Volume,
                          backref="volume_restricted_metadata",
                          foreign_keys=volume_id,
                          primaryjoin='and_('
                          'VolumeRestrictedMetadataDTO.volume_id == Volume.id,'
                          'VolumeRestrictedMetadataDTO.deleted == 0)')


######################################################
##########  Health Status Model Definition   #########
######################################################
class VolumeHealthStatusDTO(cinder_models.BASE,
                            cinder_models.CinderBase):
    """The Volume Health DTO class provides the ORM for health_status table"""
    __tablename__ = 'volume_health_status'
    __table_args__ = ()
    #Volume Health Status DTO Model Attributes
    id = Column(String(UUID_LEN), primary_key=True)
    health_state = Column(String(STATUS_LEN))
    reason = Column(Text)
    unknown_reason_details = Column(Text)


class StorageNodeHealthStatusDTO(cinder_models.BASE,
                                 cinder_models.CinderBase):
    """The StorageNode Health DTO class provides the ORM for
       health_status table"""
    __tablename__ = 'storage_node_health_status'
    __table_args__ = ()
    #StorageNode Health Status DTO Model Attributes
    id = Column(String(UUID_LEN), primary_key=True)
    health_state = Column(String(STATUS_LEN))
    reason = Column(Text)
    unknown_reason_details = Column(Text)


######################################################
##########  On-board Task Model Definition   #########
######################################################
class OnboardTaskDTO(cinder_models.BASE, cinder_models.CinderBase):
    """The OnboardTaskDTO class provides the ORM for the onboard_tasks table"""
    __tablename__ = 'onboard_tasks'
    __table_args__ = ()
    #On-board Task DTO Model Attributes
    id = Column('id', Integer, primary_key=True)
    host = Column('host', String(NAME_LEN), nullable=False)
    status = Column('status', String(STATUS_LEN), default='waiting')
    started = Column('started_at', DateTime, default=timeutils.utcnow)
    ended = Column('ended_at', DateTime)
    progress = Column('progress', Integer, default=0)


class OnboardTaskVolumeDTO(cinder_models.BASE, cinder_models.CinderBase):
    """The OnboardTaskVolumeDTO class provides the ORM for the tasks table"""
    __tablename__ = 'onboard_task_volumes'
    __table_args__ = ()
    #On-board Task Volume DTO Model Attributes
    id = Column('id', Integer, primary_key=True)
    task_id = Column('task_id', Integer, nullable=False)
    volume_uuid = Column('volume_uuid', String(UUID_LEN), nullable=False)
    volume_name = Column('volume_name', String(NAME_LEN), nullable=False)
    status = Column('status', String(STATUS_LEN), nullable=False)
    fault_message = Column('fault_message', String(NAME_LEN))


###################################################
##########   List of PowerVC 1.2 DTO's   ##########
###################################################
POWERVC_V1R2_DTOS = [
    HmcDTO, HmcClustersDTO, StorageNodeDTO, VolumeRestrictedMetadataDTO,
    VolumeHealthStatusDTO, OnboardTaskDTO, OnboardTaskVolumeDTO,
    StorageNodeHealthStatusDTO
]
