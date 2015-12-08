#
#
# =================================================================
# =================================================================

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient.v1.k2uom import k2attr as uom_k2attr
from paxes_cinder.k2aclient.v1.k2uom import typeset as uom_typeset
from paxes_cinder.k2aclient.v1.k2web import k2attr as web_k2attr
from paxes_cinder.k2aclient.v1.k2web import typeset as web_typeset
from paxes_k2.k2operator import K2Element, web_ns, uom_ns

import logging
import types

_logger = logging.getLogger(__name__)

K2_SCHEMA_VERSION = "V1_0"


def _enum(**enums):
    return type('Enum', (), enums)

# Status of test
Mode = _enum(UPDATE="UPDATE",
             CREATE="CREATE")


def _attr_skip(mode, obj, attrus, av, ptype, cat1, cat2, rtype, xag):
    if mode is Mode.UPDATE:
        if av is None:
            return True
#         if cat1 == "ro":
#             return True
#         if not attrus in obj.modified_attrs:
#             return True
        return False
    elif mode is Mode.CREATE:
        if not attrus in obj.modified_attrs:
            return True
        return False
    else:
        msg = ("Illegal mode: >%s<")
        raise ValueError(msg % mode)


def _process_node(ns, typeset, k2attr, mode,
                  attr, obj, ptype, cat1, cat2, rtype, xag):

    # IOAdapterChoiceCollection.Type",
    if ptype.endswith("ChoiceCollection.Type"):
#         print "ChoiceCollection.Type: >%s<" % (obj.__class__.__name__,)
        cname = obj.__class__.__name__[:-10]
        iptype = cname + ".Type"

        (x, clazzattrs) = k2attr[obj.__class__.__name__]
        assert len(clazzattrs) == 1
        clazzattr = clazzattrs[0]  # Only one "choice" !
        (iattrus, iattr, x, icat1, icat2, irtype, ixag) = clazzattr

        iav = getattr(obj, "_pattr_%s" % iattrus)
        # No skip?
        assert isinstance(iav, types.ListType)
        k2nes = []
        for li in iav:
            k2nes.append(_process_node(ns, typeset, k2attr, mode,
                                       iattr, li, iptype, icat1,
                                       icat2, irtype, ixag))
        # children
        k2e = K2Element(attr,
                        ns=ns,
                        attrib={'schemaVersion': K2_SCHEMA_VERSION},
                        children=k2nes)

        if obj.group is not None:
#             print "AAAA: attr: >%s<, group: >%s<" % (attr, obj.group)
            k2e._element.set("group", obj.group)

        return k2e

    elif ptype.endswith("Choice.Type"):
        iptype = obj.__class__.__name__ + ".Type"
        iattr = obj.__class__.__name__
        k2nes = [_process_node(ns, typeset, k2attr, mode,
                               iattr, obj, iptype, cat1, cat2, rtype, xag)]
        k2e = K2Element(attr, ns=ns, children=k2nes)

        if obj.group is not None:
#             print "BBBB: attr: >%s<, group: >%s<" % (attr, obj.group)
            k2e._element.set("group", obj.group)

        return k2e

    elif attr == "link" or ptype.startswith("link rel="):
        return K2Element(attr,
                         ns=ns,
                         attrib={'href': str(obj),
                                 'rel': 'related'})

    # not a link and not in typeset, so set the string content
    elif not type(obj) in typeset:
        return K2Element(attr, ns=ns, text=str(obj))

    # traverse inheritance, top down
    it = obj.__class__.__name__
    itypes = []
    while True:
        itypes.append(it)
        (parenttype, x) = k2attr[it]
        it = parenttype
        if it is None:
            break
    itypes.reverse()

    # accumulate hierarchy of attributes
    k2nes = []
    for it in itypes:
        (x, clazzattrs) = k2attr[it]
        for clazzattr in clazzattrs:
            (iattrus, iattr, iptype, icat1, icat2, irtype, ixag) = clazzattr
            iav = getattr(obj, "_pattr_%s" % iattrus)
            if _attr_skip(mode, obj, iattrus, iav,
                          iptype, icat1, icat2, irtype, ixag):
                continue

            if isinstance(iav, types.ListType):
                for li in iav:
                    k2nes.append(_process_node(ns, typeset, k2attr, mode,
                                               iattr, li, iptype, icat1,
                                               icat2, irtype, ixag))
            else:
                k2nes.append(_process_node(ns, typeset, k2attr, mode, iattr,
                                           iav, iptype, icat1, icat2,
                                           irtype, ixag))

    if ptype.endswith("Choice.Type") or ptype.endswith("Links.Type"):
        objk2ne = K2Element(attr,
                            ns=ns,
                            children=k2nes)
    else:
        objk2ne = K2Element(attr,
                            ns=ns,
                            attrib={'schemaVersion': K2_SCHEMA_VERSION},
                            children=k2nes)

    if obj.group is not None:
#         print "CCCC: attr: >%s<, group: >%s<" % (attr, obj.group)
        objk2ne._element.set("group", obj.group)

    return objk2ne


def process_root(service, mode, obj):
    """Create k2node elements from object model instance"""
    if service == "web":
        ns = web_ns
        typeset = web_typeset
        k2attr = web_k2attr
    elif service == "uom":
        ns = uom_ns
        typeset = uom_typeset
        k2attr = uom_k2attr
    else:
        msg = _("k2aclient: during process_root, unrecognized service: >%s<")
        raise ValueError(msg % service)

    k2ne = _process_node(ns, typeset, k2attr, mode,
                         obj.__class__.__name__, obj,
                         "root", "co", "r", "R", "")
    return k2ne
