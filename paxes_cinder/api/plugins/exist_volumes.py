#
#
# =================================================================
# =================================================================

"""Provides the REST API implementation for the /storage-providers URI"""

import webob.exc
from cinder.api import extensions
from cinder.api.openstack import wsgi
from cinder.api import xmlutil
from cinder.openstack.common import log as logging
from paxes_cinder.db import api as paxes_db_api
from paxes_cinder.volume import api as volume_api

LOG = logging.getLogger(__name__)
AUTHORIZE = extensions.extension_authorizer('volume', 'hosts')


class ExistedVolumesControllerExtension(wsgi.Controller):
    """Main Controller Class to extend the existed volumes API"""

    def __init__(self):
        """Constructor for the Storage Providers Controller Extension"""
	self.api = volume_api.API()
        super(ExistedVolumesControllerExtension, self).__init__()

    def index(self, req):
        context = req.environ['cinder.context']
        lvs = self.api.exist_volumes(context)
        return {'volumes': lvs}

    @staticmethod
    def _validate_authorization(context, action):
        """Internal Helper Method to Confirm the Requester is Authorized"""
        #We want to use the more granular version, but can't until it exists
        AUTHORIZE(context, action=action)
        return context.elevated()


class Exist_volumes(extensions.ExtensionDescriptor):
    """Provides additional Metric and Status for the Storage Providers"""
    name = "Get existed volumes"
    alias = "vios-exist-volumes"
    namespace = "http://docs.openstack.org/volume/ext/" + \
                "ibm_storage_providers/api/v1.2"
    updated = "2016-07-02T21:00:00-06:00"

    def get_resources(self):
        """Provide a Resource Extension to the /existed-volumes Resource"""
        resource = extensions.ResourceExtension(
            'os-exist-volumes', 
	    ExistedVolumesControllerExtension(),
            collection_actions={'index': 'GET'})
        return [resource]
