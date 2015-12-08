#
#
# All Rights Reserved.
# Copyright 2013 OpenStack LLC
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

from paxes_cinder.k2aclient import client

from paxes_cinder.k2aclient.v1 import uom_manager
from paxes_cinder.k2aclient.v1 import paxes_manager

from paxes_cinder.k2aclient.v1 import cluster_manager
from paxes_cinder.k2aclient.v1 import logicalpartition_manager
from paxes_cinder.k2aclient.v1 import managedsystem_manager
from paxes_cinder.k2aclient.v1 import managementconsole_manager
from paxes_cinder.k2aclient.v1 import sharedstoragepool_manager
from paxes_cinder.k2aclient.v1 import virtualioserver_manager
from paxes_cinder.k2aclient.v1 import clientnetworkadapter_manager
from paxes_cinder.k2aclient.v1 import virtualnetwork_manager
from paxes_cinder.k2aclient.v1 import virtualswitch_manager

from paxes_cinder.k2aclient.v1 import web_file_manager

from paxes_cinder.k2aclient.v1 import web_job_manager

from paxes_cinder.k2aclient.v1 import v1k2loader
from paxes_cinder.k2aclient.k2exclogger import K2ResponseLogger


class Client(object):
    """
    Top-level object to access k2.

    Create an instance with your creds::

        >>> client = Client(K2_USERNAME, K2_PASSWORD, ...)

    Then call methods on its managers::

        >>> client.managedsystem.list()
        ...
    """

    k2loader = v1k2loader

    def __init__(self,
                 k2_url,
                 k2_username,
                 k2_password,
                 k2_auditmemento="cinder",
                 k2_certpath=None,
                 retries=0,
                 timeout=None,
                 excdir="/tmp/k2aexc",
                 k2o_use_cache=False):

        self.uom = uom_manager.UomManager(self)
        self.paxes = paxes_manager.PowerVcManager(self)

        # UOM
        self.cluster = cluster_manager.ClusterManager(self)
        self.logicalpartition = \
            logicalpartition_manager.LogicalPartitionManager(self)
        self.managedsystem = managedsystem_manager.ManagedSystemManager(self)
        self.managementconsole = \
            managementconsole_manager.ManagementConsoleManager(self)
        self.sharedstoragepool = \
            sharedstoragepool_manager.SharedStoragePoolManager(self)
        self.virtualioserver = \
            virtualioserver_manager.VirtualIOServerManager(self)
        self.clientnetworkadapter = \
            clientnetworkadapter_manager.ClientNetworkAdapterManager(self)
        self.virtualnetwork = \
            virtualnetwork_manager.VirtualNetworkManager(self)
        self.virtualswitch = \
            virtualswitch_manager.VirtualSwitchManager(self)

        # WEB
        self.web_file = web_file_manager.FileManager(self)
        self.web_job = web_job_manager.JobManager(self)

        self.retries = retries

        if excdir is None:
            msg = ("excdir may not be assigned to None")
            raise ValueError(msg)

        self.exclogger = K2ResponseLogger(excdir)

        self.client = client.HTTPClient(
            k2_url,
            k2_username,
            k2_password,
            k2_auditmemento,
            k2_certpath,
            timeout=timeout,
            exclogger=self.exclogger,
            k2o_use_cache=k2o_use_cache)

    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
