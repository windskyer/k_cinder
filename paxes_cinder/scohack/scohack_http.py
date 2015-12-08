#
#
# All Rights Reserved.
# Copyright 2010 OpenStack Foundation
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

import httplib
import urlparse

import cinder.openstack.common.log as logging
from paxes_cinder import _
import paxes_cinder.scohack.scohack_location

LOG = logging.getLogger(__name__)


class Indexable(object):
    """
    Wrapper that allows an iterator or filelike be treated as an indexable
    data structure. This is required in the case where the return value from
    Store.get() is passed to Store.add() when adding a Copy-From image to a
    Store where the client library relies on eventlet GreenSockets, in which
    case the data to be written is indexed over.
    """

    def __init__(self, wrapped, size):
        """
        Initialize the object

        :param wrappped: the wrapped iterator or filelike.
        :param size: the size of data available
        """
        self.wrapped = wrapped
        self.size = int(size) if size else (wrapped.len
                                            if hasattr(wrapped, 'len') else 0)
        self.cursor = 0
        self.chunk = None

    def __iter__(self):
        """
        Delegate iteration to the wrapped instance.
        """
        for self.chunk in self.wrapped:
            yield self.chunk

    def __getitem__(self, i):
        """
        Index into the next chunk (or previous chunk in the case where
        the last data returned was not fully consumed).

        :param i: a slice-to-the-end
        """
        start = i.start if isinstance(i, slice) else i
        if start < self.cursor:
            return self.chunk[(start - self.cursor):]

        self.chunk = self.another()
        if self.chunk:
            self.cursor += len(self.chunk)

        return self.chunk

    def another(self):
        """Implemented by subclasses to return the next element"""
        raise NotImplementedError

    def getvalue(self):
        """
        Return entire string value... used in testing
        """
        return self.wrapped.getvalue()

    def __len__(self):
        """
        Length accessor.
        """
        return self.size


MAX_REDIRECTS = 5


class StoreLocation(object):
    """Class describing an HTTP(S) URI"""

    def __init__(self, store_specs):
        self.specs = store_specs
        if self.specs:
            self.process_specs()

    def process_specs(self):
        self.scheme = self.specs.get('scheme', 'http')
        self.netloc = self.specs['netloc']
        self.user = self.specs.get('user')
        self.password = self.specs.get('password')
        self.path = self.specs.get('path')

    def _get_credstring(self):
        if self.user:
            return '%s:%s@' % (self.user, self.password)
        return ''

    def get_uri(self):
        return "%s://%s%s%s" % (
            self.scheme,
            self._get_credstring(),
            self.netloc,
            self.path)

    def parse_uri(self, uri):
        """
        Parse URLs. This method fixes an issue where credentials specified
        in the URL are interpreted differently in Python 2.6.1+ than prior
        versions of Python.
        """
        pieces = urlparse.urlparse(uri)
        assert pieces.scheme in ('https', 'http')
        self.scheme = pieces.scheme
        netloc = pieces.netloc
        path = pieces.path
        try:
            if '@' in netloc:
                creds, netloc = netloc.split('@')
            else:
                creds = None
        except ValueError:
            # Python 2.6.1 compat
            # see lp659445 and Python issue7904
            if '@' in path:
                creds, path = path.split('@')
            else:
                creds = None
        if creds:
            try:
                self.user, self.password = creds.split(':')
            except ValueError:
                reason = (_("BadStoreUri: credentials '%(creds)s' "
                            "not well-formatted.")
                          % dict(creds="".join(creds)))
                LOG.debug(reason)
                e = Exception(reason)
                e.scohack_httpcode = 400
                raise e
        else:
            self.user = None
        if netloc == '':
            reason = _("BadStoreUri: no address specified in HTTP URL")
            LOG.debug(reason)
            e = Exception(reason)
            e.scohack_httpcode = 400
            raise e
        self.netloc = netloc
        self.path = path


def http_response_iterator(conn, response, size):
    """
    Return an iterator for a file-like object.

    :param conn: HTTP(S) Connection
    :param response: httplib.HTTPResponse object
    :param size: Chunk size to iterate with
    """
    chunk = response.read(size)
    while chunk:
        yield chunk
        chunk = response.read(size)
    conn.close()


class Store(object):

    """An implementation of the HTTP(S) Backend Adapter"""

    CHUNKSIZE = (16 * 1024 * 1024)  # 16M

    def __init__(self, context=None, location=None):
        """
        Initialize the Store
        """
        self.store_location_class = None
        self.context = context
        self.configure()

    def configure(self):
        """
        Configure the Store to use the stored configuration options
        Any store that needs special configuration should implement
        this method.
        """
        pass

    def configure_add(self):
        """
        This is like `configure` except that it's specifically for
        configuring the store to accept objects.

        If the store was not able to successfully configure
        itself, it should raise `exception.BadStoreConfiguration`.
        """
        pass

    def add(self, image_file, image_meta, context):
        """
        Stores an image file to the backend storage system and returns
        a tuple containing information about the stored image.

        :param image_file: The image data to write, as a file-like object
        :param image_size: The size of the image data to write, in bytes

        :retval tuple of URL in backing store, bytes written, checksum
               and a dictionary with storage system specific information
        """
        raise NotImplementedError

    def delete(self, location):
        """
        Takes a Location object that indicates
        where to find the image file to delete

        :location `Location` object, supplied
                  from scohack_location.get_location_from_uri()
        """
        raise NotImplementedError

    def set_acls(self, location, public=False, read_tenants=[],
                 write_tenants=[]):
        """
        Sets the read and write access control list for an image in the
        backend store.

        :location `scohack_location.Location` object, supplied
                  from scohack_location.get_location_from_uri()
        :public A boolean indicating whether the image should be public.
        :read_tenants A list of tenant strings which should be granted
                      read access for an image.
        :write_tenants A list of tenant strings which should be granted
                      write access for an image.
        """
        raise NotImplementedError

    def get(self, location):
        """
        Takes a `scohack_location.Location` object that indicates
        where to find the image file, and returns a tuple of generator
        (for reading the image file) and image_size

        :param location `scohack_location.Location` object, supplied
                        from scohack_location.get_location_from_uri()
        """
        conn, resp, content_length = self._query(location, 'GET')

        iterator = http_response_iterator(conn, resp, self.CHUNKSIZE)

        class ResponseIndexable(Indexable):
            def another(self):
                try:
                    return self.wrapped.next()
                except StopIteration:
                    return ''

        return (ResponseIndexable(iterator, content_length), content_length)

    def get_schemes(self):
        return ('http', 'https')

    def get_size(self, location):
        """
        Takes a `scohack_location.Location` object that indicates
        where to find the image file, and returns the size

        :param location `scohack_location.Location` object, supplied
                        from scohack_location.get_location_from_uri()
        """
        try:
            return self._query(location, 'HEAD')[2]
        except Exception:
            return 0

    def _query(self, location, verb, depth=0):
        if depth > MAX_REDIRECTS:
            x = (_("MaxRedirectsExceeded: redirects: >%(max)d<")
                 % dict(max=MAX_REDIRECTS))
            e = Exception(x)
            e.scohack_httpcode = 400
            raise e
        loc = location.store_location
        conn_class = self._get_conn_class(loc)
        conn = conn_class(loc.netloc)
        conn.request(verb, loc.path, "", {})
        resp = conn.getresponse()

        # Check for bad status codes
        if resp.status >= 400:
            reason = (_("HTTP URL returned a %(status)s status code.")
                      % dict(status=resp.status))
            x = (_("BadStoreUri: loc.path: >%(path)s<, reason: >%(reason)s<")
                 % dict(path=loc.path, reason=reason))
            e = Exception(x)
            e.scohack_httpcode = resp.status
            raise e

        location_header = resp.getheader("location")
        if location_header:
            if resp.status not in (301, 302):
                reason = ("The HTTP URL attempted to redirect with an "
                          "invalid status code."
                          )
                x = (_("BadStoreUri: loc.path: >%(path)s<, "
                       "reason: >%(reason)s<")
                     % dict(path=loc.path, reason=reason))
                e = Exception(x)
                e.scohack_httpcode = resp.status
                raise e
            location_class = paxes_cinder.scohack.scohack_location.Location
            new_loc = location_class(location.store_name,
                                     location.store_location.__class__,
                                     uri=location_header,
                                     image_id=location.image_id,
                                     store_specs=location.store_specs)
            return self._query(new_loc, verb, depth + 1)
        content_length = int(resp.getheader('content-length', 0))
        return (conn, resp, content_length)

    def _get_conn_class(self, loc):
        """
        Returns connection class for accessing the resource. Useful
        for dependency injection and stubouts in testing...
        """
        return {'http': httplib.HTTPConnection,
                'https': httplib.HTTPSConnection}[loc.scheme]
