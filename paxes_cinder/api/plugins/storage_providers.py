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

LOG = logging.getLogger(__name__)
AUTHORIZE = extensions.extension_authorizer('volume', 'hosts')

#Define the list of Possible Attributes to be returned  on the REST API Calls
POSSIBLE_ATTRIBUTES = ['id', 'service', 'storage_hostname',
                       'backend_id', 'backend_type', 'backend_state',
                       'volume_count', 'total_capacity_gb', 'free_capacity_gb']


class StorageProviderListTemplate(xmlutil.TemplateBuilder):
    """Utility Class to Convert a JSON Response to XML for Storage Providers"""

    def construct(self):
        """Template Constructor to convert the JSON to an XML Response"""
        root = xmlutil.TemplateElement('storage_providers')
        elem = xmlutil.SubTemplateElement(root, 'storage_provider',
                                          selector='storage_providers')
        #Map each of the Possible Attributes to the same XML Attribute Name
        for attr in POSSIBLE_ATTRIBUTES:
            elem.set(attr)
        return xmlutil.MasterTemplate(root, 1)


class StorageProviderShowTemplate(xmlutil.TemplateBuilder):
    """Utility Class to Convert a JSON Response to XML for Storage Providers"""

    def construct(self):
        """Template Constructor to convert the JSON to an XML Response"""
        root = xmlutil.TemplateElement('storage_provider',
                                       selector='storage_provider')
        #Map each of the Possible Attributes to the same XML Attribute Name
        for attr in POSSIBLE_ATTRIBUTES:
            root.set(attr)
        return xmlutil.MasterTemplate(root, 1)


class StorageProviderControllerExtension(wsgi.Controller):
    """Main Controller Class to extend the storage-providers API"""

    def __init__(self):
        """Constructor for the Storage Providers Controller Extension"""
        super(StorageProviderControllerExtension, self).__init__()

    @wsgi.serializers(xml=StorageProviderListTemplate)
    def index(self, req):
        """Implements the HTTP GET for the /storage-providers URI"""
        providers = []
        context = req.environ['cinder.context']
        context = self._validate_authorization(context, 'index')
        #Retrieve all of the Storage Nodes from the Database
        storage_nodes = paxes_db_api.storage_node_get_all(context)
        for node in storage_nodes:
            provider = self._parse_storage_provider(node)
            hostname = provider['storage_hostname']
            #We only want to return the Id and Host-name from Index
            providers.append({'id': provider['id'],
                              'storage_hostname': hostname})
        return {'storage_providers': providers}

    @wsgi.serializers(xml=StorageProviderListTemplate)
    def detail(self, req):
        """Implements the HTTP GET for the /storage-providers/detail URI"""
        providers = []
        context = req.environ['cinder.context']
        context = self._validate_authorization(context, 'index')
        #Retrieve all of the Storage Nodes from the Database
        storage_nodes = paxes_db_api.storage_node_get_all(context)
        #Return all of the details for each of the Storage Nodes found
        for storage_node in storage_nodes:
            providers.append(self._parse_storage_provider(storage_node))
        return {'storage_providers': providers}

    @wsgi.serializers(xml=StorageProviderShowTemplate)
    def show(self, req, id):
        """Implements the HTTP GET for the /storage-providers/{id} URI"""
        storage_node = None
        context = req.environ['cinder.context']
        context = self._validate_authorization(context, 'show')
        #Retrieve the Storage Node for the ID from the Database
        if id.isdigit():
            storage_node = paxes_db_api.storage_node_get(context, id)
        #If we didn't find the Storage Provider, throw an exception
        if not storage_node:
            msgtxt = "Storage Provider with ID '" + id + "' could not be found"
            raise webob.exc.HTTPNotFound(explanation=msgtxt)
        #Parse the appropriate attributes out of the Storage Node
        provider = self._parse_storage_provider(storage_node)
        return {'storage_provider': provider}

    @staticmethod
    def _validate_authorization(context, action):
        """Internal Helper Method to Confirm the Requester is Authorized"""
        #We want to use the more granular version, but can't until it exists
        AUTHORIZE(context, action=action)
        return context.elevated()

    @staticmethod
    def _parse_storage_provider(storage_node):
        """Helper Method to Parse the return values out of the Storage Node"""
        provider = dict()
        for attr in POSSIBLE_ATTRIBUTES:
            #If this is the Service attribute, we need to parse it special
            if attr == 'service':
                provider['service'] = {'id': storage_node['service_id']}
                provider['service']['host'] = storage_node['storage_hostname']
            #Otherwise it is just a 1-to-1 mapping from the Storage Node
            else:
                provider[attr] = storage_node[attr]
        return provider


class Storage_providers(extensions.ExtensionDescriptor):
    """Provides additional Metric and Status for the Storage Providers"""
    name = "Retrieve Storage Providers"
    alias = "storage-providers"
    namespace = "http://docs.openstack.org/volume/ext/" + \
                "ibm_storage_providers/api/v1.2"
    updated = "2013-07-02T21:00:00-06:00"

    def get_resources(self):
        """Provide a Resource Extension to the /storage-providers Resource"""
        resource = extensions.ResourceExtension(
            'storage-providers', StorageProviderControllerExtension(),
            collection_actions={'detail': 'GET'})
        return [resource]
