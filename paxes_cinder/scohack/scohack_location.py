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

import urlparse
import logging
from paxes_cinder import _

LOG = logging.getLogger(__name__)

from paxes_cinder.scohack.scohack_http import Store as HttpStore
from paxes_cinder.scohack.scohack_http \
    import StoreLocation as HttpStoreLocation
from paxes_cinder.scohack.scohack_scohack \
    import Store as ScohackStore
from paxes_cinder.scohack.scohack_scohack \
    import StoreLocation as ScohackStoreLocation

SCHEME_TO_CLS_MAP = {"http":  {'store_class': HttpStore,
                               'location_class': HttpStoreLocation},
                     "scohack": {'store_class': ScohackStore,
                                 'location_class': ScohackStoreLocation}}


def get_location_from_uri(uri):
    """
    Given a URI, return a Location object that has had an appropriate
    store parse the URI.

    :param uri: A URI that could come from the end-user in the Location
                attribute/header
    """
    pieces = urlparse.urlparse(uri)
    if pieces.scheme not in SCHEME_TO_CLS_MAP.keys():
        x = (_("exception.UnknownScheme: scheme: >%(scheme)s<")
             % dict(scheme=pieces.scheme))
        raise Exception(x)
    scheme_info = SCHEME_TO_CLS_MAP[pieces.scheme]
    return Location(pieces.scheme, uri=uri,
                    store_location_class=scheme_info['location_class'])


class Location(object):
    """
    Class describing the location of an image
    """

    def __init__(self, store_name, store_location_class,
                 uri=None, image_id=None, store_specs=None):
        """
        Create a new Location object.

        :param store_name: The string identifier/scheme of the storage backend
        :param store_location_class: The store location class to use
                                     for this location instance.
        :param image_id: The identifier of the image in whatever storage
                         backend is used.
        :param uri: Optional URI to construct location from
        :param store_specs: Dictionary of information about the location
                            of the image that is dependent on the backend
                            store
        """
        self.store_name = store_name
        self.image_id = image_id
        self.store_specs = store_specs or {}
        self.store_location = store_location_class(self.store_specs)
        if uri:
            self.store_location.parse_uri(uri)
