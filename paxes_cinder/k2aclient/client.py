#
#
# All Rights Reserved.
# Copyright 2011 OpenStack LLC.
# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Piston Cloud Computing, Inc.
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

"""
OpenStack Client interface. Handles the REST calls and responses.
"""

from __future__ import print_function
try:
    from eventlet import sleep
except ImportError:
    from time import sleep  # @UnusedImport

from paxes_cinder.k2aclient import _
from paxes_k2.k2operator import K2Session, K2Operator
from paxes_cinder.k2aclient import exceptions
from paxes_cinder.k2aclient import utils
from paxes_cinder.k2aclient.k2exclogger import K2ResponseLogger

import logging

_logger = logging.getLogger(__name__)


class HTTPClient(object):

    def __init__(self,
                 k2_url,
                 k2_user,
                 k2_password,
                 k2_auditmemento,
                 k2_certpath=None,
                 timeout=None,
                 exclogger=None,
                 k2o_use_cache=False):

        self.k2_url = k2_url
        self.k2_user = k2_user
        self.k2_password = k2_password
        self.k2_auditmemento = k2_auditmemento
        self.k2_certpath = k2_certpath
        self.version = 'v1'
        self.timeout = timeout
        if exclogger is None:
            self.exclogger = K2ResponseLogger("/tmp/k2aexc")
        else:
            self.exclogger = exclogger
        self.k2o_use_cache = k2o_use_cache
        # have to authenticate before k2operator is assigned
        self._k2operator = None

        # hardcoded (may change someday?)
        self._protocol = "https"
        self._port = 12443

    @property
    def k2operator(self):
        """Get the k2operator."""
        return self._k2operator

    @property
    def k2location(self):
        return (self._protocol, self.k2_url, self._port)

    def getserviceurl(self, service):
        url = '%s://%s:%s' % (self._protocol, self.k2_url, self._port,)
        link = '%s/rest/api/%s' % (url, service,)
        return link

    def get(self, url, etag=None, xag=[], xa=None):
        if not self._k2operator:
            self.authenticate()
        # extend path w/ xag
        if len(xag) > 0:
            url += '?group=%s' % xag[0]
            if len(xag) > 1:
                for g in xag[1:len(xag)]:
                    url += ',%s' % g
        try:
            result = self._k2operator.readbypath(url,
                                                 etag=etag,
                                                 age=0,
                                                 auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during get")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def refresh(self,
                service,
                etag,
                root_type, root_id,
                child_type=None, child_id=None,
                xa=None):
        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.read(root_type,
                                           rootId=root_id,
                                           childType=child_type,
                                           childId=child_id,
                                           service=service,
                                           etag=etag,
                                           age=0,
                                           auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during refresh")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def create(self,
               service,
               element,
               root_type,
               root_id=None, child_type=None,
               xa=None):
        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.create(element,
                                             root_type,
                                             root_id,
                                             child_type,
                                             service=service,
                                             auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during create")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def update(self,
               service,
               etag,
               element,
               root_type, root_id,
               child_type=None, child_id=None,
               xa=None):
        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.update(element,
                                             etag,
                                             root_type,
                                             root_id,
                                             child_type,
                                             child_id,
                                             service=service,
                                             auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during create")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def delete(self,
               service,
               root_type, root_id,
               child_type=None, child_id=None,
               xa=None):

        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.delete(root_type,
                                             rootId=root_id,
                                             childType=child_type,
                                             childId=child_id,
                                             service=service,
                                             auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during delete")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def runjob(self, element, root_type, root_id, xa=None):
        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.createjob(element,
                                                root_type,
                                                root_id,
                                                auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during runJob")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def readjob(self, root_id, xa=None):
        if not self._k2operator:
            self.authenticate()
        try:
            result = self._k2operator.readjob(root_id,
                                              auditmemento=xa)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during readJob")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)
        return result

    def authenticate(self):
        try:
            # note timeout=None is no timeout (wait forever)
            k2_conn = K2Session(self.k2_url,
                                self.k2_user,
                                self.k2_password,
                                self.k2_auditmemento,
                                timeout=self.timeout,
                                certpath=self.k2_certpath)
        except Exception as e:
            x = exceptions.create_k2a_exception_from_k2o_exception
            addmsg = _(", during authenticate")
            raise x(e, addmsg=addmsg, exclogger=self.exclogger)

        self._k2operator = K2Operator(k2_conn, use_cache=self.k2o_use_cache)


def get_client_class(version):
    version_map = {
        '1': 'paxes_cinder.k2aclient.v1.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        msg = (_("k2aclient:"
                 " while obtaining client,"
                 " invalid client version >%(version)s<."
                 " must be one of: >%(versions)s<") %
               {"version": version,
                "versions": ', '.join(version_map.keys()), })
        raise exceptions.UnsupportedVersion(msg)

    return utils.import_class(client_path)


def Client(version, *args, **kwargs):
    client_class = get_client_class(version)
    return client_class(*args, **kwargs)
