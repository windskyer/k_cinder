#
#
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import json
import httplib
import urlparse
import logging
import time
import os

LOG = logging.getLogger('paxes_client')


class PowerVCClient(object):

    def __init__(self, user, password, domain, project, auth_url,
                 key_file=None, cert_file=None):
        """
        Create a new client for issuing PowerVC REST API calls and
        authenticate with keystone using the given credentials. For SSL
        connections the user can provide a private key file and/or
        certificate chain file. The server's certificate will not be verified.
        :param user: The user name
        :param password: The password
        :param domain: domain name
        :param project: project name
        :param auth_url: URL for keystone authentication
        :param key_file: PEM formatted file that contains private key
        :param cert_file: PEM formatted certificate chain file
        :raise InvalidResponse: If keystone validation request does not return
        a 201 status code.
        """
        self.user = user
        self.password = password
        self.domain = domain
        self.project = project
        self.auth_url = auth_url
        self.key_file = key_file
        self.cert_file = cert_file
        self.auth_token = None
        self.catalog = None

        # Authenticate to keystone and save the token for future requests
        res = self._authenticate()
        if res['status'] == 201:
            self.auth_token = res['headers']['x-subject-token']
            self.catalog = self._extract_catalog(json.loads(res['body']))
        else:
            LOG.error('Keystone authentication failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_volume(self, volume_id):
        """
        Get a volume by id.
        :param volume_id: The ID of the volume to get
        :return dict: A dict of volume properties
        :raise InvalidResponse: If volume request does not return a 200
        status code.
        """
        url = '%s/volumes/%s' % (self.catalog['volume'], volume_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['volume']
        else:
            LOG.error('Get volume failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_volumes(self):
        """
        Get a list of all volumes.
        :return list: A list of dicts containing volume properties
        :raise InvalidResponse: If volume request does not return a 200
        status code.
        """
        res = self.get('%s/volumes' % self.catalog['volume'])
        if res['status'] == 200:
            return json.loads(res['body'])['volumes']
        else:
            LOG.error('Get volumes failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_volume_types(self):
        """
        Get a list of all volume types.
        :return list: A list of dicts containing volume type properties
        :raise InvalidResponse: If volume type request does not return a 200
        status code.
        """
        res = self.get('%s/types' % self.catalog['volume'])
        if res['status'] == 200:
            return json.loads(res['body'])['volume_types']
        else:
            LOG.error('Get volume types failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_volume_type(self, volume_type_id):
        """
        Get a volume type by id.
        :param volume_type_id: The ID of the volume type to get
        :return dict: A dict containing volume type properties
        :raise InvalidResponse: If volume type request does not return a 200
        status code.
        """
        url = '%s/types/%s' % (self.catalog['volume'], volume_type_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['volume_type']
        else:
            LOG.error('Get volume type failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def create_volume(self, name, size, description=None, source=None,
                      volume_type=None):
        """
        Create a volume.
        :param name: Name of the volume
        :param size: Size of the volume in GB
        :param description: Optional description of the volume
        :param source: Optional source volume ID to copy from
        :param volume_type: Optional volume type
        :return dict: A dict containing volume properties
        :raise InvalidResponse: If volume request does not return a 200
        status code.
        """
        body = {
            "volume": {
                "display_name": name,
                "display_description": description or name + " Description",
                "size": size
            }
        }
        if source:
            body['volume']['source_volid'] = source
        if volume_type:
            body['volume']['volume_type'] = volume_type
        res = self.post('%s/volumes' % self.catalog['volume'], body)
        if res['status'] == 200:
            return json.loads(res['body'])['volume']
        else:
            LOG.error('Create volume failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def delete_volume(self, volume_id):
        """
        Delete a volume.
        :param volume_id: The ID of the volume to delete
        :return boolean: True if delete request is successful
        :raise InvalidResponse: If volume request does not return a 202
        status code.
        """
        url = '%s/volumes/%s' % (self.catalog['volume'], volume_id)
        res = self.delete(url)
        if res['status'] == 202:
            return True
        else:
            LOG.error('Delete volume failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def import_disk_image(self, location, size, name, description=None,
                          volume_type=None, hmc_id=None):
        """
        Import an image over HTTP or from a local file.
        :param location: The location of the image (HTTP or local file)
        :param size: Size of the volume to create in GB
        :param name: Name to give the volume
        :param description: Optional volume description
        :param volume_type: Optional volume type
        :param hmc_id: ID of the HMC to use for importing the image.
        :return dict: A dict containing information about the volume that the
        image was imported into.
        :raise InvalidResponse: If import request does not return a 200
        status code.
        :raise VolumeCreationError: If volume creation fails
        """
        LOG.debug('Importing disk image from location %s' % location)
        is_http = location.startswith('http')

        # Make sure the file exists
        if not is_http and not os.path.exists(location):
            raise FileNotFound(location)

        LOG.debug('Creating volume of size %dGB to hold the image' % size)

        # Create the volume to import the disk image into
        volume = self.create_volume(name, size, description,
                                    volume_type=volume_type)

        # Poll until the volume is available
        while volume['status'].lower() != 'available':
            time.sleep(5)
            volume = self.get_volume(volume['id'])
            if volume['status'].lower() == 'error':
                LOG.error('Error creating volume for disk import. Check '
                          'the logs.')
                raise VolumeCreationError(volume['id'])
        LOG.debug('Volume created, now importing image')

        # Import the disk image into the volume
        url = '%s/imgupload' % self.catalog['volume']
        headers = {
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/json',
            'x-imgupload-copy-from': location,
            'x-imgupload-cinder-volume-id': volume['id'],
            'x-imgupload-hmc-id': hmc_id
        }

        body = None if is_http else open(location, 'rb')
        res = self.post(url, headers=headers, body=body, serialize=False)
        if body:
            body.close()
        if res['status'] == 200:
            return json.loads(res['body'])['imgupload']
        else:
            LOG.error('Import disk image failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def create_image_from_volume(self, name, volume_id,
                                 additional_volumes=None):
        """
        Create an image based on a volume.
        :param name: The name for the new image
        :param volume_id: The volume to use for the image
        :param additional_volumes: Array of additional volume information to
        add to the image.
        :return dict: A dict containing image properties
        :raise InvalidResponse: If image request does not return a 201
        status code.
        """
        url = '%s/v1/images' % self.catalog['image']

        def get_volume_type(volume_id):
            volume = self.get_volume(volume_id)
            if volume['volume_type'] == 'None':
                return 'null'
            return '\"' + volume['volume_type'] + '\"'
        volume_mapping = "[{" \
            "\"delete_on_termination\": true," \
            "\"device_name\": \"/dev/sda\"," \
            "\"volume_type\": " + get_volume_type(volume_id) + "," \
            "\"source_volid\": \"" + volume_id + "\"}"
        if additional_volumes:
            for vol_id in additional_volumes:
                volume_mapping += ",{" \
                    "\"volume_type\": " + get_volume_type(vol_id) + "," \
                    "\"volume_id\": \"" + vol_id + "\"}"
        volume_mapping += "]"
        headers = {
            'Content-Type': 'application/octet-stream',
            'x-image-meta-disk-format': 'raw',
            'x-image-meta-is-public': 'true',
            'x-image-meta-property-architecture': 'ppc64',
            'x-image-meta-property-hypervisor_type': 'powervm',
            'x-image-meta-property-image_type': 'snapshot',
            'x-image-meta-property-volume_mapping': volume_mapping,
            'x-image-meta-name': name,
            'x-image-meta-location': 'http://localhost/nonexistenturl',
            'x-image-meta-container-format': 'bare',
            'x-image-meta-property-meta_version': '2',
            'x-image-meta-property-boot_device_name': '/dev/sda',
            'x-image-meta-property-image_location': 'snapshot',
            'x-image-meta-property-os_distro': 'RHEL'
        }
        res = self.post(url, headers=headers)
        if res['status'] == 201:
            return json.loads(res['body'])['image']
        else:
            LOG.error('Create image failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_image(self, image_id):
        """
        Get an image by id.
        :param image_id: The ID of the image to get
        :return dict: A dict containing image properties
        :raise InvalidResponse: If image request does not return a 200
        status code.
        """
        url = '%s/v1/images/%s' % (self.catalog['image'], image_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['image']
        else:
            LOG.error('Get image failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def set_configuration_strategy(self, image_id, config_strategy):
        """
        Set the configuration strategy for an image.
        :param image_id: The ID of the image
        :param config_strategy: The configuration strategy
        :return dict: A dict containing image properties
        :raise InvalidResponse: If image request does not return a 200
        status code.
        """
        url = '%s/v2/images/%s' % (self.catalog['image'], image_id)
        headers = {
            'Content-Type': 'application/openstack-images-v2.0-json-patch'
        }
        body = [{
            'add': '/configuration_strategy',
            'value': config_strategy
        }]
        res = self.patch(url, body=body, headers=headers)
        if res['status'] == 200:
            return json.loads(res['body'])
        else:
            LOG.error('Set configuration strategy failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def create_server(self, name, flavor_id, image_id, networks, metadata,
                      hostname):
        """
        Create a server.
        :param name: Name of the server
        :param flavor_id: ID of the flavor to use
        :param image_id: ID of the image to use
        :param networks: Array of network information (each item with 'uuid'
        and optionally a 'fixed_ip' attribute)
        :param metadata: Server metadata properties to set (dict)
        :param hostname: Name of the host to create the server on
        :return dict: A dict containing server properties
        :raise InvalidResponse: If server request does not return a 202
        status code.
        """
        ref_link = 'http://openstack.example.com/openstack/%s/%s'
        body = {
            "server": {
                "name": name,
                "flavorRef": ref_link % ('flavors', flavor_id),
                "imageRef": ref_link % ('images', image_id),
                "networkRef": ref_link % ('networks', networks[0]['uuid']),
                "networks": networks,
                'metadata': metadata,
                'hypervisor_hostname': hostname
            }
        }
        res = self.post('%s/servers' % self.catalog['compute'], body)
        if res['status'] == 202:
            return json.loads(res['body'])['server']
        else:
            LOG.error('Create server failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_servers(self):
        """
        Get a list of all servers.
        :return list: A list of dicts containing server properties
        :raise InvalidResponse: If server request does not return a 200
        status code.
        """
        url = '%s/servers/detail' % self.catalog['compute']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['servers']
        else:
            LOG.error('Get servers failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_server(self, server_id):
        """
        Get a server by id.
        :param server_id: The ID of the server to get
        :return dict: A dict containing server properties
        :raise InvalidResponse: If server request does not return a 200
        status code.
        """
        url = '%s/servers/%s' % (self.catalog['compute'], server_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['server']
        else:
            LOG.error('Get server failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_flavors(self):
        """
        Get a list of all flavor details.
        :return list: A list of dicts containing flavor properties
        :raise InvalidResponse: If flavor request does not return a 200
        status code.
        """
        url = '%s/flavors/detail' % self.catalog['compute']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['flavors']
        else:
            LOG.error('Get flavors failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_flavor(self, flavor_id):
        """
        Get a flavor by ID.
        :param flavor_id: The ID of the flavor to get
        :return dict: A dict containing flavor properties
        :raise InvalidResponse: If flavor request does not return a 200
        status code.
        """
        url = '%s/flavors/%s' % (self.catalog['compute'], flavor_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['flavor']
        else:
            LOG.error('Get flavor failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_networks(self):
        """
        Get a list of all networks.
        :return list: A list of dicts containing network properties
        :raise InvalidResponse: If network request does not return a 200
        status code.
        """
        url = '%s/v2.0/networks' % self.catalog['network']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['networks']
        else:
            LOG.error('Get networks failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_network(self, network_id):
        """
        Get a network by ID.
        :param network_id: The ID of the network to get
        :return dict: A dict containing network properties
        :raise InvalidResponse: If network request does not return a 200
        status code.
        """
        url = '%s/v2.0/networks/%s' % (self.catalog['network'], network_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['network']
        else:
            LOG.error('Get network failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_subnets(self):
        """
        Get a list of all subnets.
        :return list: A list of dicts containing subnet properties
        :raise InvalidResponse: If subnet request does not return a 200
        status code.
        """
        url = '%s/v2.0/subnets' % self.catalog['network']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['subnets']
        else:
            LOG.error('Get subnets failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_storage_connectivity_groups(self):
        """
        Get a list of all storage connectivity groups.
        :return list: A list of dicts containing storage connectivity
        group properties
        :raise InvalidResponse: If storage connectivity group request does
        not return a 200 status code.
        """
        url = '%s/storage-connectivity-groups' % self.catalog['compute']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['storage-connectivity-groups']
        else:
            LOG.error('Get storage connectivity groups failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_storage_connectivity_group(self, scg_id):
        """
        Get a storage connectivity group by ID.
        :param scg_id: The ID of the storage connectivity group to get
        :return dict: A dict containing storage connectivity group properties
        :raise InvalidResponse: If storage connectivity group request does
        not return a 200 status code.
        """
        url = '%s/storage-connectivity-groups/%s' % (self.catalog['compute'],
                                                     scg_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['storage-connectivity-group']
        else:
            LOG.error('Get storage connectivity group failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_hmcs(self):
        """
        Get a list of all hardware management consoles.
        :return list: A list of dicts containing HMC properties
        :raise InvalidResponse: If HMC request does not return a 200
        status code.
        """
        url = '%s/ibm-hmcs' % self.catalog['compute']
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['hmcs']
        else:
            LOG.error('Get HMCs failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_hmc_hosts(self, hmc_id):
        """
        Get a list of all hosts in the given HMC.
        :param hmc_id: ID of the hardware management console.
        """
        url = '%s/ibm-hmcs/%s/hosts' % (self.catalog['compute'], hmc_id)
        res = self.get(url)
        if res['status'] == 200:
            return json.loads(res['body'])['hosts']
        else:
            LOG.error('Get HMC hosts failed: %s %s %s' %
                      (res['status'], res['reason'], res['body']))
            raise InvalidResponse(res)

    def get_addresses_in_use(self, network_id):
        """
        Get a list of all the IP addresses in use for the given network.
        :param network_id: The network ID
        :return list: A list of IP addresses currently is use for the given
        network.
        """
        addresses = []
        for server in self.get_servers():
            if 'addresses' in server:
                addrs = server['addresses']
                for network_name in addrs.keys():
                    for ip in addrs[network_name]:
                        addresses.append(ip['addr'])
        return addresses

    def get(self, url):
        """
        Perform an HTTP GET request.
        :param url: The URL to send the request to
        :return dict: A dict containing response properties
        """
        return self._request('GET', url)

    def post(self, url, body=None, headers=None, serialize=True):
        """
        Perform an HTTP POST request.
        :param url: The URL to send the request to
        :param body: The content of the request
        :param headers: Headers to send on the request
        :return dict: A dict containing response properties
        """
        return self._request('POST', url, body, headers, serialize)

    def patch(self, url, body=None, headers=None):
        """
        Perform an HTTP PATCH request.
        :param url: The URL to send the request to
        :param body: The content of the request
        :param headers: Headers to send on the request
        :return dict: A dict containing response properties
        """
        return self._request('PATCH', url, body, headers)

    def delete(self, url):
        """
        Perform an HTTP DELETE request.
        :param url: The URL to send the request to
        :return dict: A dict containing response properties
        """
        return self._request('DELETE', url)

    def _request(self, method, url, body=None, headers=None, serialize=True):
        """
        Perform an HTTP request of a given method.
        :param method: The method of request to make (GET, POST...)
        :param url: The URL to send the request to
        :param body: The content of the request
        :param headers: Headers to send on the request
        :return dict: A dict containing response properties
        """
        headers = headers or {}
        headers['Accept'] = 'application/json'
        headers['User-Agent'] = 'paxes-httpclient'
        if body and not 'Content-Type' in headers:
            headers['Content-Type'] = 'application/json'
        if self.auth_token:
            headers['X-Auth-Token'] = self.auth_token
        LOG.debug('>> %s %s, %s, %s' % (method, url, headers, body))
        conn = self._create_connection(url)
        if body and serialize:
            body = json.dumps(body)
        conn.request(method, url, body, headers)
        res = conn.getresponse()
        header_list = res.getheaders()
        header_dict = {}
        for ituple in header_list:
            header_dict[ituple[0].lower()] = ituple[1]
        response_info = {
            'status': res.status,
            'reason': res.reason,
            'headers': header_dict,
            'body': res.read()
        }
        LOG.debug('<< %d %s, %s, %s' % (response_info['status'],
                                        response_info['reason'],
                                        response_info['headers'],
                                        response_info['body']))
        conn.close()
        return response_info

    def _create_connection(self, url):
        """
        Create the connection to the PowerVC server.
        :param url: URL for creating the connection.
        :return HTTPConnection or HTTPSConnection: A httplib.HTTPConnection or
        httplib.HTTPSConnection depending on the URL scheme.
        """
        parsed_url = urlparse.urlparse(url)
        connection = None
        if parsed_url.scheme == 'https':
            connection = httplib.HTTPSConnection(parsed_url.netloc,
                                                 parsed_url.port,
                                                 self.key_file,
                                                 self.cert_file)
        else:
            connection = httplib.HTTPConnection(parsed_url.netloc,
                                                parsed_url.port)
        return connection

    def _authenticate(self):
        """
        Authenticate to keystone
        :return dict: A dict containing response properties
        :raise UnsupportedKeystoneVersion: If the keystone version being used
        is not v3.
        """
        url_parts = urlparse.urlparse(self.auth_url)
        version = 'v3'
        path_parts = url_parts.path.split('/')
        for part in path_parts:
            if len(part) > 0 and part[0] == 'v':
                version = part
                break

        if version == "v3":
            LOG.debug('Authenticating using keystone v3')
            return self._v3_auth(self.auth_url)
        else:
            message = 'Keystone auth version %s not supported' % version
            LOG.error(message)
            raise UnsupportedKeystoneVersion()

    def _v3_auth(self, url):
        """
        Authenticate using keystone v3 auth
        :return dict: A dict containing response properties
        """
        body = {
            "auth": {
                "identity": {
                    "methods": ["password"],
                    "password": {
                        "user": {
                            "domain": {
                                "name": self.domain
                            },
                            "name": self.user,
                            "password": self.password
                        }
                    }
                },
                "scope": {
                    "project": {
                        "domain": {
                            "name": self.domain
                        },
                        "name": self.project
                    }
                }
            }
        }
        if not url.endswith('/'):
            url += "/"
        return self.post(url + 'auth/tokens', body)

    def _extract_catalog(self, data):
        """
        Create the service catalog based on the given response object from
        the authentication request.
        :param data: The response from the authentication request
        :return dict: A dict of services and their respective URLs
        """
        interface = 'public'
        catalog = data['token']['catalog']
        service_map = {}
        for service in catalog:
            service_endpoint = None
            for endpoint in service['endpoints']:
                if endpoint['interface'] == interface:
                    service_endpoint = endpoint['url']
                    break
            if service_endpoint:
                service_map[service['type']] = service_endpoint
        LOG.debug('Service catalog: %s' % service_map)
        return service_map


class InvalidResponse(httplib.HTTPException):
    """
    Exception used when an HTTP response code is not what is expected.
    """
    def __init__(self, response):
        self.response = response
        message = "Invalid response: %s %s %s" % (response['status'],
                                                  response['reason'],
                                                  response['body'])
        super(InvalidResponse, self).__init__(message)


class FileNotFound(httplib.HTTPException):
    """
    Exception used when a file being accessed cannot be found.
    """
    def __init__(self, location):
        message = "File not found: %s" % location
        super(FileNotFound, self).__init__(message)


class VolumeCreationError(httplib.HTTPException):
    """
    Exception used when a volume being created ends up in 'error' state.
    """
    def __init__(self, volume_id):
        message = "Error creating volume for disk import: %s" % volume_id
        super(VolumeCreationError, self).__init__(message)


class UnsupportedKeystoneVersion(httplib.HTTPException):
    """
    Exception used when the keystone authentication version is not v3.
    """
    def __init__(self, version):
        message = 'Keystone auth version %s not supported' % version
        super(UnsupportedKeystoneVersion, self).__init__(message)
