#
# =================================================================
# =================================================================
"""Table Creation/Deletion for Schema changes in the 1.2 Release"""

from sqlalchemy import MetaData
from cinder.openstack.common import log as logging
from paxes_cinder import _
from paxes_cinder.db.sqlalchemy import models

LOG = logging.getLogger(__name__)


def upgrade(migration_engine):
    """ Upgrades the Cinder DB Tables to include those for 1.2 """
    metadata = MetaData(migration_engine)
    metadata.reflect(migration_engine)
    metadata.bind = migration_engine

    #Loop through all of the DTO's that we added new in PowerVC 1.2
    #creating the tables off of the definition defined in the DTO
    for dto in models.POWERVC_V1R2_DTOS:
        try:
            table = dto.__table__.tometadata(metadata, None)
            table.create(checkfirst=True)
        except Exception as exc:
            LOG.info(_(repr(dto.__table__)))
            tbl = dto.__table__.__class__.__name__
            LOG.exception(_('Exception creating table %(table)s: %(ex)s')
                          % dict(table=tbl, ex=exc))
            raise exc


def downgrade(migration_engine):
    """ Downgrades the Cinder DB Tables to remove those for 1.2 """
    metadata = MetaData(migration_engine)
    metadata.reflect(migration_engine)
    metadata.bind = migration_engine

    #Loop through all of the DTO's that we added new in PowerVC 1.2
    #dropping the tables off of the definition defined in the DTO
    for dto in reversed(models.POWERVC_V1R2_DTOS):
        try:
            dto.__table__.metadata = metadata
            dto.__table__.drop(checkfirst=True)
        except Exception as exc:
            LOG.info(_(repr(dto.__table__)))
            tbl = dto.__table__.__class__.__name__
            LOG.exception(_('Exception dropping table %(table)s: %(ex)s')
                          % dict(table=tbl, ex=exc))
            raise exc
