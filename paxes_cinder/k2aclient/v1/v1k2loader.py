#
#
# =================================================================
# =================================================================

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient.v1.k2uom import k2dict as uom_k2dict
from paxes_cinder.k2aclient.v1.k2web import k2dict as web_k2dict
from paxes_cinder.k2aclient.v1.k2uom import k2choice as uom_k2choice
from paxes_cinder.k2aclient.v1.k2web import k2choice as web_k2choice
from paxes_cinder.k2aclient.v1.k2uom import attr_cc_to_us as \
    uom_attr_cc_to_us
from paxes_cinder.k2aclient.v1.k2web import attr_cc_to_us as \
    web_attr_cc_to_us

import re
import logging
import types

_uom_base_path = "paxes_cinder.k2aclient.v1.k2uom."
_web_base_path = "paxes_cinder.k2aclient.v1.k2web."

_logger = logging.getLogger(__name__)

_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_cc_to_us(attr_cc_to_us, name):
    """Return pythonic attribute name for input camel case name"""
    if name in attr_cc_to_us:
        return attr_cc_to_us[name]
    s1 = _first_cap_re.sub(r'\1_\2', name)
    return _all_cap_re.sub(r'\1_\2', s1).lower()


def _process_child(base_path, k2dict, k2choice, attr_cc_to_us, parent_tag,
                   parentobj, level,
                   childk2node, choicetag=None):
    """Recursively turn k2 output in object model"""

    _logger.debug("start processing child at level: >%d<, parent_tag: >%s<",
                  level, parent_tag)

    us_tag = convert_cc_to_us(attr_cc_to_us, childk2node.tag)
    us_tag_ass = "_pattr_" + us_tag

    if choicetag is not None:
        us_tag = convert_cc_to_us(attr_cc_to_us, choicetag)
        us_tag_ass = "_pattr_" + us_tag
#     _logger.debug("childk2node.tag: >%s<, us_tag: >%s<",
#                   childk2node.tag, us_tag,)

    if not hasattr(parentobj, us_tag_ass):
        msg = _("k2aclient:"
                " during k2 deserialization,"
                " for type: >%(pcname)s<, k2 gave unknown attr:"
                " >%(us_tag)s<, is there a schema mismatch?,"
                " will skip ...")
        _logger.warning(msg % {"pcname": parentobj.__class__.__name__,
                               "us_tag": us_tag, })
        return

    at = getattr(parentobj, us_tag_ass)

    # check if leaf node
    if len(childk2node) == 0:
        if not isinstance(at, types.ListType):
            s = getattr(parentobj, us_tag_ass, childk2node.text)
            if s is not None:
                msg = _("k2aclient:"
                        " during k2 deserialization,"
                        " for type: >%(pcname)s<,"
                        " k2 attr: >%(us_tag)s<: is listed"
                        " as scalar, but maybe its not?,"
                        " is there a schema mismatch?, will replace"
                        " existing scalar w/ next value ...")
                _logger.warning(msg % {"pcname": parentobj.__class__.__name__,
                                       "us_tag": us_tag, })

            # Empirical observation: if has an href it is a link
            if "href" in childk2node.attrib:
#                 _logger.debug("child is leaf scalar href node")
                setattr(parentobj, us_tag_ass, childk2node.attrib["href"])
            else:
#                 _logger.debug("child is leaf scalar text node")
                setattr(parentobj, us_tag_ass, childk2node.text)
        else:
            l = getattr(parentobj, us_tag_ass)

            # Empirical observation: if has an href it is a link
            if "href" in childk2node.attrib:
#                 _logger.debug("child is leaf list href node")
                l.append(childk2node.attrib["href"])
            else:
#                 _logger.debug("child is leaf list text node")
                l.append(childk2node.text)
#         print "return from leaf: level: >%d<" % (level,)
        return

    # instantiate object and populate w/ k2 data
    ctype = childk2node.tag

    #####
    # check for choice
    _logger.debug("not leaf")
    if parent_tag in k2choice and ctype in k2choice[parent_tag]:
#         _logger.debug("child is choice, so recurse")
        choicetype = childk2node[0].tag
        _process_child(base_path, k2dict, k2choice, attr_cc_to_us, choicetype,
                       parentobj,
                       level + 1, childk2node[0], choicetag=ctype)
        return

    if parent_tag in k2dict and ctype in k2dict[parent_tag]:
#         _logger.debug("childobject: >%s< -> >%s<", ctype,
#                       k2dict[parent_tag][ctype])
        ctype = k2dict[parent_tag][ctype]
    else:
#         _logger.debug("childobject: >%s< -> >%s<", ctype, ctype)
        pass
    C = _get_class(base_path + ctype)

    if C is None:
        msg = _("k2aclient:"
                " during k2 deserialization,"
                " while processing: k2 type: >%(parent_tag)s<,"
                " there is no definition for k2 type: >%(k2type)s<,"
                " is there a schema mismatch?,"
                " will skip ...")
        _logger.warning(msg % {"parent_tag": parent_tag,
                               "k2type": base_path + childk2node.tag, })
        return

    ####
    # instantiate child object
    childobj = C()

    # if present record XAG group
    if "group" in childk2node.attrib:
        childobj.group = childk2node.attrib["group"]

    if not isinstance(at, types.ListType):
#         msg = ("for parent attribute: >%s<, set new child object as scalar")
#         _logger.debug(msg, us_tag_ass)
        setattr(parentobj, us_tag_ass, childobj)
    else:
#         msg = ("for parent attribute: >%s<, set new child object as list")
#         _logger.debug(msg, us_tag_ass)
        l = getattr(parentobj, us_tag_ass)
        l.append(childobj)

    for c in childk2node:
#         _logger.debug("recurse on child")
        _process_child(base_path, k2dict, k2choice, attr_cc_to_us, ctype,
                       childobj, level + 1, c)


def _get_class(clazz):
    """dynamically load a class"""
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        if not hasattr(m, comp):
            return None
        m = getattr(m, comp)
    return m


def process_root(service, obj, k2node):
    """Marshal k2 response (k2node) into object model"""
    if service == "web":
        k2dict = web_k2dict
        k2choice = web_k2choice
        attr_cc_to_us = web_attr_cc_to_us
        base_path = _web_base_path
    elif service == "uom":
        k2dict = uom_k2dict
        k2choice = uom_k2choice
        attr_cc_to_us = uom_attr_cc_to_us
        base_path = _uom_base_path
    else:
        msg = _("k2aclient:",
                " during k2 deserialization,"
                " unrecognized service: >%s<")
        raise ValueError(msg % service)
    if len(k2node):
        for c in k2node:
            _process_child(base_path, k2dict, k2choice, attr_cc_to_us,
                           k2node.tag, obj, 0, c)
    else:
        msg = _("k2aclient:",
                " during k2 deserialization,"
                " very, very weird, no children for k2 root"
                " element: >%s<, continuing ...")
        _logger.warning(msg % k2node.tag)
