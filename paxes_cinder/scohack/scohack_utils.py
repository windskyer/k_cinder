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

"""
System-level utilities and helper functions.
"""

try:
    from eventlet import sleep
except ImportError:
    from time import sleep

import cinder.openstack.common.log as logging
from paxes_cinder import _

LOG = logging.getLogger(__name__)


def cooperative_iter(citer):
    """
    Return an iterator which schedules after each
    iteration. This can prevent eventlet thread starvation.

    :param citer: an iterator to wrap
    """
    try:
        for chunk in citer:
            sleep(0)
            yield chunk
    except Exception as err:
        msg = (_("Error: cooperative_iter exception %(error)s") %
               dict(error=err))
        LOG.error(msg)
        raise


def chunkiter(fp, chunk_size=65536):
    """
    Return an iterator to a file-like obj which yields fixed size chunks

    :param fp: a file-like object
    :param chunk_size: maximum size of chunk
    """
    while True:
        chunk = fp.read(chunk_size)
        if chunk:
            yield chunk
        else:
            break


def cooperative_read(fd):
    """
    Wrap a file descriptor's read with a partial function which schedules
    after each read. This can prevent eventlet thread starvation.

    :param fd: a file descriptor to wrap
    """
    def readfn(*args):
        result = fd.read(*args)
        sleep(0)
        return result
    return readfn


class CooperativeReader(object):
    """
    An eventlet thread friendly class for reading in image data.

    When accessing data either through the iterator or the read method
    we perform a sleep to allow a co-operative yield. When there is more than
    one image being uploaded/downloaded this prevents eventlet thread
    starvation, ie allows all threads to be scheduled periodically rather than
    having the same thread be continuously active.
    """
    def __init__(self, fd):
        """
        :param fd: Underlying image file object
        """
        self.fd = fd
        self.iterator = None
        # NOTE(markwash): if the underlying supports read(), overwrite the
        # default iterator-based implementation with cooperative_read which
        # is more straightforward
        if hasattr(fd, 'read'):
            self.read = cooperative_read(fd)

    def read(self, length=None):
        """Return the next chunk of the underlying iterator.

        This is replaced with cooperative_read in __init__ if the underlying
        fd already supports read().
        """
        if self.iterator is None:
            self.iterator = self.__iter__()
        try:
            return self.iterator.next()
        except StopIteration:
            return ''

    def __iter__(self):
        return cooperative_iter(self.fd.__iter__())


class ChunkReader(CooperativeReader):
    """
    An eventlet thread friendly class for reading chunked image data.

    When accessing data either through the iterator or the read method
    we perform a sleep to allow a co-operative yield. When there is more than
    one image being uploaded/downloaded this prevents eventlet thread
    starvation, ie allows all threads to be scheduled periodically rather than
    having the same thread be continuously active.
    """

    def __iter__(self):
        return chunkiter(self.fd)
