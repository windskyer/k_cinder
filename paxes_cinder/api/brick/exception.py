'''
Created on Sep 29, 2015

@author: root
'''

"""Exceptions for the Brick library."""
from cinder.openstack.common.gettextutils import _
from cinder.openstack.common import log as logging
from cinder.brick.exception import BrickException

LOG = logging.getLogger(__name__)

class ISCSITmiscsi_ProtoCreateFailed(BrickException):
    message = _("Failed to create iscsi tmiscsi_proto.")

class ISCSITmiscsi_ProtoRemoveFailed(BrickException):
    message = _("Failed to remove iscsi tmiscsi_proto %(tmsw)s")