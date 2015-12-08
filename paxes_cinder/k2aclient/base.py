#
#
# All Rights Reserved.
# Copyright 2011 OpenStack LLC.
# Copyright 2010 Jacob Kaplan-Moss
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
Base utilities to build API operation managers and objects on top of.
"""
import abc

import six
import contextlib
import hashlib
import os
from paxes_cinder.k2aclient import utils
from paxes_cinder.k2aclient.v1 import v1k2creater
from paxes_cinder.k2aclient.v1 import v1k2loader
from paxes_cinder.k2aclient.v1 import k2web
# from paxes_cinder.k2aclient.k2exclogger import K2ResponseLogger


class Manager(object):
    """
    Managers interact with a particular uom element
    and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, api):
        self.api = api

    def _list(self, url, xa=None):
        obj_class = self.resource_class
        k2resp = self.api.client.get(url, xa=xa)
        with self.completion_cache('uuid', obj_class, mode="w"):
            return [obj_class().loadAsRoot(self, k2entry, k2resp, False)
                    for k2entry in k2resp.feed.entries]

    @contextlib.contextmanager
    def completion_cache(self, cache_type, obj_class, mode):
        """
        The completion cache store items that can be used for bash
        autocompletion, like UUIDs.

        A resource listing will clear and re-populate the cache.

        A resource create will append to the cache.

        Delete is not handled because listings are assumed to be performed
        often enough to keep the cache reasonably up-to-date.
        """
        base_dir = utils.env('K2ACLIENT_UUID_CACHE_DIR',
                             default="~/.k2aclient")

        # NOTE(sirp): Keep separate UUID caches for each username + endpoint
        # pair
        username = utils.env('K2_USERNAME')
        url = utils.env('K2_URL')
        uniqifier = hashlib.md5(username + url).hexdigest()

        cache_dir = os.path.expanduser(os.path.join(base_dir, uniqifier))

        try:
            os.makedirs(cache_dir, 0755)
        except OSError:
            # NOTE(kiall): This is typicaly either permission denied while
            #              attempting to create the directory, or the directory
            #              already exists. Either way, don't fail.
            pass

        resource = obj_class.__name__.lower()
        filename = "%s-%s-cache" % (resource, cache_type.replace('_', '-'),)
        path = os.path.join(cache_dir, filename)

        cache_attr = "_%s_cache" % cache_type

        try:
            setattr(self, cache_attr, open(path, mode))
        except IOError:
            # NOTE(kiall): This is typicaly a permission denied while
            #              attempting to write the cache file.
            pass

        try:
            yield
        finally:
            cache = getattr(self, cache_attr, None)
            if cache:
                cache.close()
                delattr(self, cache_attr)

    def write_to_completion_cache(self, cache_type, val):
        cache = getattr(self, "_%s_cache" % cache_type, None)
        if cache:
            cache.write("%s\n" % val)

    def _get(self, url, xag=[], xa=None):
        k2resp = self.api.client.get(url, xag=xag, xa=xa)
        obj_class = self.resource_class
        obj = obj_class().loadAsRoot(self, k2resp.entry, k2resp, True)
        return obj

    def _refresh(self, service, root, child=None, xa=None):
        etag = root.k2resp.headers['etag']
        root_type = root.__class__.__name__
        root_id = root.id

        child_type = None
        child_id = None
        if child is not None:
            etag = child.k2resp.headers['etag']
            child_type = child.__class__.__name__
            child_id = child.id

        k2resp = self.api.client.refresh(service,
                                         etag,
                                         root_type,
                                         root_id,
                                         child_type=child_type,
                                         child_id=child_id,
                                         xa=xa)
        obj = None
        if k2resp.status != 304:
            obj_class = self.resource_class
            obj = obj_class().loadAsRoot(self, k2resp.entry, k2resp, True)
        return obj

    def _create(self, service, root, child=None, xa=None):
        root_type = root.__class__.__name__

        root_id = None
        child_type = None
        if child is not None:
            element_type = type(child)
            root_id = root.id
            child_type = child.__class__.__name__
            element = v1k2creater.process_root(service,
                                               v1k2creater.Mode.CREATE,
                                               child)
        else:
            element_type = type(root)
            element = v1k2creater.process_root(service,
                                               v1k2creater.Mode.CREATE,
                                               root)

        k2resp = self.api.client.create(service,
                                        element,
                                        root_type,
                                        root_id=root_id,
                                        child_type=child_type,
                                        xa=xa)
        obj_class = element_type
        obj = obj_class().loadAsRoot(self, k2resp.entry, k2resp, True)
        return obj

    def _update(self, service, root, child=None, xa=None):
        etag = root.k2resp.headers['etag']
        root_type = root.__class__.__name__
        root_id = root.id

        child_type = None
        child_id = None
        if child is not None:
            etag = child.k2resp.headers['etag']
            element_type = type(child)
            child_type = child.__class__.__name__
            child_id = child.id
            element = v1k2creater.process_root(service,
                                               v1k2creater.Mode.UPDATE,
                                               child)
        else:
            element_type = type(root)
            element = v1k2creater.process_root(service,
                                               v1k2creater.Mode.UPDATE,
                                               root)
        k2resp = self.api.client.update(service,
                                        etag,
                                        element,
                                        root_type,
                                        root_id,
                                        child_type=child_type,
                                        child_id=child_id,
                                        xa=xa)

        obj_class = element_type
#         print "Updated: child_type: >%s<, child_id: >%s" % (child_type,
#                                                             child_id)
        obj = obj_class().loadAsRoot(self, k2resp.entry, k2resp, True)
        return obj

    def _delete(self, service, root, child=None, xa=None):
        root_type = root.__class__.__name__
        root_id = root.id
        child_type = None
        child_id = None
        if child is not None:
            child_type = child.__class__.__name__
            child_id = child.id

        k2resp = self.api.client.delete(service,
                                        root_type,
                                        root_id,
                                        child_type=child_type,
                                        child_id=child_id,
                                        xa=xa)

#         krl = K2ResponseLogger("/tmp/testing")
#         krl.emit("OK", "DELETE SHOULD WORK", k2resp)
        return k2resp

    def _deletebyid(self, service, root_type, root_id,
                    child_type=None, child_id=None, xa=None):
        k2resp = self.api.client.delete(service,
                                        root_type,
                                        root_id,
                                        child_type=child_type,
                                        child_id=child_id,
                                        xa=xa)

#         krl = K2ResponseLogger("/tmp/testing")
#         krl.emit("OK", "DELETE SHOULD WORK", k2resp)
        return k2resp

    ####
    # Job methods
    def _getjob(self, root, jobname, xa=None):
        root_type = root.__class__.__name__
        root_id = root.id
        url = "/rest/api/uom/%s/%s/do/%s" % (root_type, root_id, jobname,)
        k2resp = self.api.client.get(url, xa=xa)
        obj = k2web.JobRequest()
        v1k2loader.process_root("web", obj, k2resp.entry.element)
        obj._k2resp = k2resp
        return obj

    def _runjob(self, root, child, xa=None):
        service = "web"
        root_type = root.__class__.__name__
        root_id = root.id
        element = v1k2creater.process_root(service,
                                           v1k2creater.Mode.UPDATE,
                                           child)
        k2resp = self.api.client.runjob(element,
                                        root_type,
                                        root_id=root_id,
                                        xa=xa)
        obj = k2web.JobResponse()
        v1k2loader.process_root("web", obj, k2resp.entry.element)
        obj._k2resp = k2resp
        return obj

    def _readjob(self, job_id, xa=None):
        k2resp = self.api.client.readjob(job_id, xa=xa)
        obj = k2web.JobResponse()
        v1k2loader.process_root("web", obj, k2resp.entry.element)
        obj._k2resp = k2resp
        return obj


class ManagerWithFind(six.with_metaclass(abc.ABCMeta, Manager)):
    """
    Like a `Manager`, but with additional `find()`/`findall()` methods.
    """

    @abc.abstractmethod
    def list(self):
        pass

#     def find(self, **kwargs):
#         """
#         Find a single item with attributes matching ``**kwargs``.
#
#         This isn't very efficient: it loads the entire list then filters on
#         the Python side.
#         """
#         matches = self.findall(**kwargs)
#         num_matches = len(matches)
#         if num_matches == 0:
#             msg = "No %s matching %s." % (self.resource_class.__name__,
#              kwargs)
#             raise exceptions.NotFound(msg)
#         elif num_matches > 1:
#             raise exceptions.NoUniqueMatch
#         else:
#             return matches[0]
#
#     def findall(self, **kwargs):
#         """
#         Find all items with attributes matching ``**kwargs``.
#
#         This isn't very efficient: it loads the entire list then filters on
#         the Python side.
#         """
#         found = []
#         searches = kwargs.items()
#         for obj in self.list():
#             try:
#                 if all(getattr(obj, attr) == value
#                        for (attr, value) in searches):
#                     found.append(obj)
#             except AttributeError:
#                 continue
#
#         return found
