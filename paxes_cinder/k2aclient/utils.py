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

from __future__ import print_function

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import exceptions
from paxes_cinder.k2aclient.openstack.common import strutils

import os
import re
import sys
import uuid

import six


def arg(*args, **kwargs):
    """Decorator for CLI args."""
    def _decorator(func):
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def env(*ivars, **kwargs):
    """
    returns the first environment variable set
    if none are non-empty, defaults to '' or keyword arg default
    """
    for v in ivars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def add_arg(f, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(f, 'arguments'):
        f.arguments = []

    # NOTE(sirp): avoid dups that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in f.arguments:
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        f.arguments.insert(0, (args, kwargs))


def find_resource(manager, name_or_id):
    """Helper for the _find_* methods."""
    # first try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id))
    except exceptions.NotFound:
        pass

    # now try to get entity as uuid
    try:
        uuid.UUID(strutils.safe_decode(name_or_id))
        return manager.get(name_or_id)
    except (ValueError, exceptions.NotFound):
        pass

    try:
        try:
            return manager.find(human_id=name_or_id)
        except exceptions.NotFound:
            pass

        # finally try to find entity by name
        try:
            return manager.find(name=name_or_id)
        except exceptions.NotFound:
            try:
                return manager.find(display_name=name_or_id)
            except (UnicodeDecodeError, exceptions.NotFound):
                try:
                    # Volumes does not have name, but display_name
                    return manager.find(display_name=name_or_id)
                except exceptions.NotFound:
                    msg = (_("k2aclient:"
                             " no %(res)s with a name or ID"
                             " of '%(name_or_id)s' exists.") %
                           {"res": manager.resource_class.__name__.lower(),
                            "name_or_id": name_or_id, })
                    raise exceptions.CommandError(msg)
    except exceptions.NoUniqueMatch:
        msg = (_("k2aclient:"
                 " multiple %(res)s matches found for '%(name_or_id)s',"
                 " use an ID to be more"
                 " specific.") %
               {"res": manager.resource_class.__name__.lower(),
                "name_or_id": name_or_id, })
        raise exceptions.CommandError(msg)


def safe_issubclass(*args):
    """Like issubclass, but will just return False if not a class."""

    try:
        if issubclass(*args):
            return True
    except TypeError:
        pass

    return False


def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    return getattr(sys.modules[mod_str], class_str)

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


# http://code.activestate.com/recipes/
#   577257-slugify-make-a-string-usable-in-a-url-or-filename/
def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = six.text_type(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = six.text_type(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)
