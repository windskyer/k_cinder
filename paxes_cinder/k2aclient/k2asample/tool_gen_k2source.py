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

import odf.opendocument
from odf.text import P
from odf.table import Table, TableRow, TableCell
import re
import json
import os

_first_cap_re = re.compile('(.)([A-Z][a-z]+)')
_all_cap_re = re.compile('([a-z0-9])([A-Z])')

fix_cc_to_us = {"CurrentMaximumProcessorsPerIBMiPartition":
                "current_maximum_processors_per_ibm_i_partition",
                "CurrentMaximumVirtualProcessorsPerIBMiPartition":
                "current_maximum_virtual_processors_per_ibm_i_partition",
                "IBMiCapable": "ibm_i_capable",
                "IBMiLogicalPartitionMobilityCapable":
                "ibm_i_logical_partition_mobility_capable",
                "IBMiLogicalPartitionSuspendCapable":
                "ibm_i_logical_partition_suspend_capable",
                "IBMiNetworkInstallCapable":
                "ibm_i_network_install_capable",
                "IBMiRestrictedIOModeCapable":
                "ibm_i_restricted_io_mode_capable",
                "MaximumProcessorUnitsPerIBMiPartition":
                "maximum_processor_units_per_ibm_i_partition",
                "MinimumRequiredMemoryForIBMi":
                "minimum_required_memory_for_ibm_i",
                "RelatedIBMiIOSlot": "related_ibm_i_io_slot",
                "PortVLANID": "port_vlan_id",
                "TaggedVLANIDs": "tagged_vlan_ids",
                "NetworkVLANID": "network_vlan_id"
                }


def convert_cc_to_us(attr_cc_to_us, name):
    if name in attr_cc_to_us:
        return attr_cc_to_us[name]

    if name in fix_cc_to_us:
        attr_cc_to_us[name] = fix_cc_to_us[name]
        return attr_cc_to_us[name]

    s1 = _first_cap_re.sub(r'\1_\2', name)
    us = _all_cap_re.sub(r'\1_\2', s1).lower()
    attr_cc_to_us[name] = us
    return us


class OdsDecoder:
    """Parse an Ods file"""

    # load the ODS
    def __init__(self, fn):
        self.ods = odf.opendocument.load(fn)
        self.sheets = {}
        for sheet in self.ods.spreadsheet.getElementsByType(Table):
            self.readSheet(sheet)

    def readSheet(self, sheet):
        sheetname = sheet.getAttribute("name")
        rows = sheet.getElementsByType(TableRow)
        rowList = []

        for row in rows:
            cellList = []
            cells = row.getElementsByType(TableCell)

            for cell in cells:
                repeat = cell.getAttribute("numbercolumnsrepeated")
                if(not repeat):
                    repeat = 1

                ps = cell.getElementsByType(P)
                text = ""

                for p in ps:
                    first = True
                    for cn in p.childNodes:
                        if first:
                            ntype = cn.nodeType
                            first = False
                        if (ntype == 3):
                            text += str(cn)
#                         if (cn.nodeType == 3):
#                             text = text + unicode(cn.data)
                cellList.extend([text] * int(repeat))
            rowList.append(cellList)
        self.sheets[sheetname] = rowList

    def getSheet(self, name):
        return self.sheets[name]

_uom_funcs = {"SharedStoragePool": '''

    def update_append_lus(self, inlus, xa=None):
        """For specified sharedstoragepool, add logicalunits.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_append_lus(self, inlus, xa=xa)

    def update_del_lus(self, lu_udids, xa=None):
        """Delete logicalunits.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_del_lus(self, lu_udids, xa=xa)

    def update_append_lu(self, unitname, unitcapacity, thin=True,
                         logicalunittype="VirtualIO_Disk",
                         clonedfrom=None,
                         xa=None):
        """Add a logicalunit.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_append_lu(self,
                                         unitname,
                                         unitcapacity,
                                         thin=thin,
                                         logicalunittype=logicalunittype,
                                         clonedfrom=clonedfrom,
                                         xa=xa)''', "Cluster": '''

    def sharedstoragepool_id(self):
        return self.cluster_shared_storage_pool.split("/")[-1]

    def lu_linked_clone(self, source_lu_udid, dest_lu_udid, xa=None):
        """Clone the source logicalunit to the dest logicalunit.

        See :class: ClusterManager for details.
        """

        return self.api.lu_linked_clone(self,
                                        source_lu_udid,
                                        dest_lu_udid,
                                        xa=xa)

    def lu_linked_clone_of_lu_bp(
        self,
        ssp,
        source_lu_udid,
        dest_lu_unit_name,
        dest_lu_unit_capacity=None,
        dest_lu_thin_device=None,
        dest_lu_logical_unit_type="VirtualIO_Disk",
        xa=None):
        """Create a new destination LU and linked_clone the source to it.

        See :class: ClusterManager for details."""

        return self.api.lu_linked_clone_of_lu_bp(
            self,
            ssp,
            source_lu_udid,
            dest_lu_unit_name,
            dest_lu_unit_capacity=dest_lu_unit_capacity,
            dest_lu_thin_device=dest_lu_thin_device,
            dest_lu_logical_unit_type=dest_lu_logical_unit_type,
            xa=xa)

    def lu_linked_clone_of_lu_bj(
        self,
        source_lu,
        dest_lu_unit_name,
        dest_lu_unit_capacity=None,
        dest_lu_thin_device=None,
        dest_lu_logical_unit_type="VirtualIO_Disk",
        xa=None):
        """Create a new destination LU cloned from existing source_lu_udid.

        See :class: ClusterManager for details."""

        return self.api.lu_linked_clone_of_lu_bj(
            self,
            source_lu,
            dest_lu_unit_name,
            dest_lu_unit_capacity=dest_lu_unit_capacity,
            dest_lu_thin_device=dest_lu_thin_device,
            dest_lu_logical_unit_type=dest_lu_logical_unit_type,
            xa=xa)

    def lu_create(self,
                  lu_unit_name,
                  lu_unit_capacity,
                  thin=True,
                  logicalunittype="VirtualIO_Disk",
                  clonedfrom=None,
                  xa=None):
        """Create a new logicalunit.

        See :class: ClusterManager for details.
        """

        return self.api.lu_create(self,
                                  lu_unit_name,
                                  lu_unit_capacity,
                                  thin=thin,
                                  logicalunittype=logicalunittype,
                                  clonedfrom=clonedfrom,
                                  xa=xa)'''}

_web_funcs = {"File": '''

    def upload(self,
               filelike,
               xa=None):
        """Upload a file to the HMC.

        filelike  a file-like object."""

        return self.api.upload(self, filelike, xa=xa)'''}

_head = '''#
#
# =================================================================
# =================================================================
#
#

import json

# from v1k2utils import K2Node


class %s(object):
    def __init__(self):
        # keep track of user-modified attributes
        self._modified_attrs = set()
        # keep track XAG (currently uom only)
        self.group = None

    @property
    def modified_attrs(self):
        return self._modified_attrs

'''

# for each noun
# (class name, <"K2Resource" for nonRoot, "K2RootResource"> for Root
_class_line = """
class %s(%s):"""

# init line
_init_line = """
    def __init__(self):
"""

# metadata_line
_metadata_line = """
        self._pattr_metadata = None
"""

# property line for each property
# (property name, <"None", "[]">
_prop_line = """
        self._pattr_%s = %s"""

# init tail line for roots
_root_init_tail = """

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None"""

# super line
# (class name)
_super_line = """
        super(%s,
              self).__init__()"""

# load function for roots
_root_load_line = """

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("%s", self, k2entry.element)
        self._id = self.metadata.atom.atom_id
        if hasattr(self, 'id') and len(self.id) == 36:
            manager.write_to_completion_cache('uuid', self.id)
        return self"""

# property line for roots
_property_line = """

    @property
    def id(self):
        return self._id

    @property
    def api(self):
        return self._api

    @property
    def k2entry(self):
        return self._k2entry

    @property
    def k2resp(self):
        return self._k2resp

    @property
    def k2resp_isfor_k2entry(self):
        return self._k2resp_isfor_k2entry"""

_metadata_getter_line = """

    @property
    def metadata(self):
        return self._pattr_metadata"""

_getter_line = """

    @property
    def %s(self):
        return self._pattr_%s"""

_setter_line = """
    @%s.setter
    def %s(self, value):
        self._modified_attrs.add("%s")
        self._pattr_%s = value"""


_class_tail = """

"""

_typeset_code = """


def _class_for_name(module_name, class_name):

#     import importlib
#     # load the module, will raise ImportError if module cannot be loaded
#     m = importlib.import_module(module_name)
#     # get the class, will raise AttributeError if class cannot be found
#     c = getattr(m, class_name)
#     return c

    # load the module, will raise ImportError if module cannot be loaded
    m = __import__(module_name, globals(), locals(), class_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

typeset = set([_class_for_name("paxes_cinder.k2aclient.v1.%s",k)
    for k in k2attr.keys()])
"""

# def addsubsgroup(typedict, parentdict, attrset, final_propdicts, parent):
#     if parent is None:
#         return
#     parent_propdicts = typedict[parent]
#     for propdict in parent_propdicts:
#         usproperty = propdict["UsProperty"]
#         if usproperty not in attrset:
#             attrset.add(usproperty)
#             final_propdicts.append(propdict)
#     addsubsgroup(typedict, parentdict, attrset, final_propdicts,
#                  parentdict[parent])


def flattensecond(k2_schema_root, secondtypedict, parentdict, curdict, parent):
    """flatten secondtypedict map by recursing on parent"""

    if parent is k2_schema_root:
        return
    if parent in secondtypedict:
        for attr, attrtype in secondtypedict[parent].iteritems():
            assert attr not in curdict
            curdict[attr] = attrtype
    flattensecond(k2_schema_root, secondtypedict, parentdict, curdict,
                  parentdict[parent])


def schemajob(stype,
              ods_source_dir,
              gensource_target_dir,
              k2_schema_ods,
              k2_schema_root,
              gensource_target_fn):

    ods_fspec = os.path.join(ods_source_dir, k2_schema_ods)
    doc = OdsDecoder(ods_fspec)

    #########
    # attribute_names
    attr_cc_to_us = {"Metadata": "metadata"}

    #########
    # Base Types
    table = doc.getSheet("Base Types")

    basedict = {}
    # first row is headers
    row = 1
    currow = table[row]
    while True:
#         print "currow: >%s<" % (currow[0],)
        assert currow[0] not in basedict
        basedict[currow[0]] = currow[1]
        row += 1
        currow = table[row]
        if currow[0] is "":
            break

    #########
    # UOM Schema
    # note: both web and uom sheet are named "UOM"
    table = doc.getSheet("UOM Schema")

    #########
    # book keeping
    # keep track of elements that have metadata
    metadata_set = set()

    # basic map of type to attribute map
    # typedict = {"<type>":[{"attr":"value"}}
    typedict = {}

    #########
    # process entries from spreadsheet
    # start on 2nd non-empty row
    # (spreadsheet logic skips empty rows)
    row = 2
    currow = table[row]

    while True:
        curtype = currow[0].strip()
        metadata_set.add(curtype)
        if curtype not in typedict:
            # add class to typedict
            typedict[curtype] = []

        propdict = {}
        propdict["Property"] = currow[1].strip()
        propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us,
                                                  currow[1].strip())
        propdict["Type"] = currow[2].strip()
        propdict["Multiplicity"] = currow[3].strip()
        propdict["CreateOnly"] = currow[4].strip()
        propdict["CreateUpdate"] = currow[5].strip()
        propdict["UpdateOnly"] = currow[6].strip()
        propdict["ReadOnly"] = currow[7].strip()
        propdict["XAG"] = currow[8].strip()
        propdict["ExcludeFromETag"] = currow[9].strip()
        propdict["RestType"] = currow[10].strip()
        propdict["SubstitutionGroup"] = currow[11].strip()

        if "-" in propdict["Property"]:
            x = ("Contact JohnCook: "
                 "Bad attribute name, class: >%s<, attribute: >%s<")
            print x % (curtype, propdict["Property"])
            propdict["Property"] = propdict["Property"].replace("-", "_")
            propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us,
                                                      propdict["Property"])

        typedict[curtype].append(propdict)
        row += 1
        currow = table[row]
        if currow[0] is "":
            break

    #########
    # parentdict
    # track inheritence
    parentdict = {}
    #########
    # substitution group parents
    for clazz, propdicts in typedict.iteritems():
        for propdict in propdicts:
            substitutiongroup = propdict["SubstitutionGroup"]
            if substitutiongroup != "":
                parentdict[clazz] = substitutiongroup
            else:
                parentdict[clazz] = k2_schema_root

# flatten logic ...
#     #########
#     # inherit properties
#     for clazz, propdicts in typedict.iteritems():
#         # initial set of attributes
#         attrset = set()
#         for propdict in propdicts:
#             attrset.add(propdict["UsProperty"])
#         addsubsgroup(typedict, parentdict, attrset, propdicts,
#                      parentdict[clazz])

    #########
    # attribute map
    secondtypedict = {}
    for c, propdicts in typedict.iteritems():
        secondtypedict[c] = {}
        for propdict in propdicts:
            if propdict["Type"].endswith(".Type"):
                new_attr = propdict["Property"]
                new_clazz = propdict["Type"][:-5]
                if new_clazz.endswith("Links"):
                    continue
                if new_clazz.endswith("Collection"):
                    continue
                if new_clazz.endswith("Choice"):
                    continue
                assert new_attr not in secondtypedict[c]
                if new_clazz in typedict:
                    secondtypedict[c][new_attr] = new_clazz

    #########
    # find collection and link types
    collectiontype_dict = {}
    collectionchoicetype = []
    linkstype_dict = {}
    for c, propdicts in typedict.iteritems():
        for propdict in propdicts:
            if propdict["Type"].endswith("Collection.Type"):
                assert (propdict["Multiplicity"] != "+" and
                        propdict["Multiplicity"] != "*")
                new_attr = propdict["Property"]
                new_attr_us = convert_cc_to_us(attr_cc_to_us, new_attr)
                new_clazz = propdict["Type"][:-5]
                assert new_attr_us not in secondtypedict[c]
                secondtypedict[c][new_attr] = new_clazz
                if not new_clazz in collectiontype_dict:
                    collectiontype_dict[new_clazz] = new_attr
                    collectiontype_dict[new_clazz] = new_clazz[:-11]
                    if propdict["Type"].endswith("ChoiceCollection.Type"):
                        collectiontype_dict[new_clazz] = new_clazz[:-10]
                        collectionchoicetype.append(new_clazz)

            elif propdict["Type"].endswith("Links.Type"):
                assert (propdict["Multiplicity"] != "+" and
                        propdict["Multiplicity"] != "*")
                new_attr = propdict["Property"]
                new_attr_us = convert_cc_to_us(attr_cc_to_us, new_attr)
                new_clazz = propdict["Type"][:-5]
                assert new_attr_us not in secondtypedict[c]
                secondtypedict[c][new_attr] = new_clazz
                if not new_clazz in linkstype_dict:
                    linkstype_dict[new_clazz] = new_attr

    #########
    # add collection types to typedict
    for new_clazz, new_attr in collectiontype_dict.iteritems():

        parentdict[new_clazz] = k2_schema_root

        # collections have metadata
        metadata_set.add(new_clazz)

        propdicts = []

        propdict = {}
        propdict["Property"] = new_attr
        propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us, new_attr)
        propdict["Type"] = "_Collection.Type"
        propdict["Multiplicity"] = "*"
        propdict["CreateOnly"] = ""
        propdict["CreateUpdate"] = "r"  # TODO just guessing
        propdict["UpdateOnly"] = ""
        propdict["ReadOnly"] = ""
        propdict["XAG"] = ""
        propdict["ExcludeFromETag"] = ""
        propdict["RestType"] = ""
        propdict["SubstitutionGroup"] = ""
        propdicts.append(propdict)

        # add class to typedict: collections
        typedict[new_clazz] = propdicts

    #########
    # add link types to typedict
    for new_clazz, new_attr in linkstype_dict.iteritems():

        parentdict[new_clazz] = k2_schema_root

        # links have metadata
        metadata_set.add(new_clazz)

        propdicts = []

        # For now link attr is always "link"
        propdict = {}
        new_attr = "link"  # note link is lowercase
        propdict["Property"] = new_attr
        propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us, new_attr)
        propdict["Type"] = "_Links.Type"
        propdict["Multiplicity"] = "*"
        propdict["CreateOnly"] = ""
        propdict["CreateUpdate"] = "r"  # TODO just guessing
        propdict["UpdateOnly"] = ""
        propdict["ReadOnly"] = ""
        propdict["XAG"] = ""
        propdict["ExcludeFromETag"] = ""
        propdict["RestType"] = ""
        propdict["SubstitutionGroup"] = ""
        propdicts.append(propdict)

        # add class to typedict: links
        typedict[new_clazz] = propdicts

    #########
    # find choice types
    choicetype_dict = {}
    for c, propdicts in typedict.iteritems():
        for propdict in propdicts:

            if propdict["Type"].endswith("Choice.Type"):
                assert (propdict["Multiplicity"] != "+" and
                        propdict["Multiplicity"] != "*")

                if not c in choicetype_dict:
                    choicetype_dict[c] = []

                choice_attr = propdict["Property"]
                choicetype_dict[c].append(choice_attr)

    for c in collectionchoicetype:
        choice_attr = typedict[c][0]["Property"]
        if not c in choicetype_dict:
            choicetype_dict[c] = []
            choicetype_dict[c].append(choice_attr)

    #########
    # add Metadata type

    new_clazz = "Metadata"
    parentdict[new_clazz] = k2_schema_root
    propdicts = []

    # For now link attr is always "link"
    propdict = {}
    new_attr = "Atom"
    propdict["Property"] = new_attr
    propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us, new_attr)
    propdict["Type"] = "_Undefined.Type"
    propdict["Multiplicity"] = ""
    propdict["CreateOnly"] = ""
    propdict["CreateUpdate"] = ""
    propdict["UpdateOnly"] = ""
    propdict["ReadOnly"] = "r"  # TODO not sure this is right
    propdict["XAG"] = ""
    propdict["ExcludeFromETag"] = ""
    propdict["RestType"] = ""
    propdict["SubstitutionGroup"] = ""
    propdicts.append(propdict)

    # add class to typedict: metadata
    typedict[new_clazz] = propdicts

    #########
    # add Atom type

    new_clazz = "Atom"
    parentdict[new_clazz] = k2_schema_root
    propdicts = []

    # AtomCreated
    propdict = {}
    new_attr = "AtomCreated"
    propdict["Property"] = new_attr
    propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us, new_attr)
    propdict["Type"] = "_Undefined.Type"
    propdict["Multiplicity"] = ""
    propdict["CreateOnly"] = ""
    propdict["CreateUpdate"] = ""
    propdict["UpdateOnly"] = ""
    propdict["ReadOnly"] = "r"  # TODO not sure this is right
    propdict["XAG"] = ""
    propdict["ExcludeFromETag"] = ""
    propdict["RestType"] = ""
    propdict["SubstitutionGroup"] = ""
    propdicts.append(propdict)

    # AtomID
    propdict = {}
    new_attr = "AtomID"
    propdict["Property"] = new_attr
    propdict["UsProperty"] = convert_cc_to_us(attr_cc_to_us, new_attr)
    propdict["Type"] = "_Undefined.Type"
    propdict["Multiplicity"] = ""
    propdict["CreateOnly"] = ""
    propdict["CreateUpdate"] = ""
    propdict["UpdateOnly"] = ""
    propdict["ReadOnly"] = "r"  # TODO not sure this is right
    propdict["XAG"] = ""
    propdict["ExcludeFromETag"] = ""
    propdict["RestType"] = ""
    propdict["SubstitutionGroup"] = ""
    propdicts.append(propdict)

    # add class to typedict: atom
    typedict[new_clazz] = propdicts

    #########
    # Classify rots and multiplicity
    root_set = set()
    for c, propdicts in typedict.iteritems():
        for propdict in propdicts:
            if propdict["RestType"] == "R" or propdict["RestType"] == "I":
                root_set.add(c)
            # defaults
            k2acmult = "Scalar"
            if propdict["Multiplicity"] == "+":
                k2acmult = "Array"
            elif propdict["Multiplicity"] == "*":
                k2acmult = "Array"
            propdict["K2aCmult"] = k2acmult

    ##################
    # output
#     f = open("/tmp/k2uom.py", "w")

    f = open(os.path.join(gensource_target_dir,
                          "paxes-cinder/paxes_cinder/k2aclient/v1/%s" %
                          (gensource_target_fn,)), "w")
    f.write(_head % (k2_schema_root))

    # sort classes for output
    sortedkeys = sorted(typedict.keys())
    parentsortedkeys = []
    for c in sortedkeys:
#         if c in parentsortedkeys:
#             continue
        chainkeys = []
        while True:
            if c not in parentsortedkeys:
                chainkeys.append(c)
            if parentdict[c] == k2_schema_root:
                break
            c = parentdict[c]
        chainkeys.reverse()
        parentsortedkeys.extend(chainkeys)

    #########
    #attributetype
    attrdict = {}
    for clazz, propdicts in typedict.iteritems():
        clazzattrs = []
        processed_set = set()
        for propdict in propdicts:
            propkey = propdict["UsProperty"]
            if propkey in processed_set:
                x = "Repeated attribute, class: >%s<, " + \
                    "CC attribute: >%s<, us attribute: >%s<"
                print x % (clazz, propdict["Property"], propkey)
                continue
            processed_set.add(propkey)
            propk2name = propdict["Property"]
            ptype = propdict["Type"].strip()
            co = propdict["CreateOnly"].strip()
            cu = propdict["CreateUpdate"].strip()
            uo = propdict["UpdateOnly"].strip()
            ro = propdict["ReadOnly"].strip()
            rtype = propdict["RestType"].strip()
            xag = propdict["XAG"].strip()

            if clazz == "LogicalUnit" and propkey == "logical_unit_type":
                co = "r"
                cu = ""
                uo = ""
                ro = ""
                x = ("Contact JohnCook: "
                     "re: uom:LogicalUnit:LogicalUnitType")
                print x

            if clazz == "OperationParameter" and propkey == "parameter_name":
                co = "r"
                cu = ""
                uo = ""
                ro = ""
                x = ("Contact JohnCook: "
                     "re: web:OperationParameter:ParameterName")
                print x

            co_t = co != ""
            cu_t = cu != ""
            uo_t = uo != ""
            ro_t = ro != ""
#             print clazz, propdict["Property"]
#             print ">%s<,>%s<,>%s<,>%s<" % (co, cu,uo,ro)
#             print co_t,cu_t,uo_t,ro_t
            # one must not be empty
            assert co_t or cu_t or uo_t or ro_t
            # assert at most one not empty
            if co_t:
                # exception (ask john cook)
                if not (clazz == "SystemMemoryConfiguration" and
                        propdict["Property"] ==
                        "DefaultHardwarePageTableRatio"):
                    assert not (cu_t or uo_t or ro_t)
                cat1 = "co"
                cat2 = co
            if cu_t:
                # exception (ask john cook)
                if not (clazz == "SystemMemoryConfiguration" and
                        propdict["Property"] ==
                        "DefaultHardwarePageTableRatio"):
                    assert not (co_t or uo_t or ro_t)
                cat1 = "cu"
                cat2 = cu
            if uo_t:
                assert not (co_t or cu_t or ro_t)
                cat1 = "uo"
                cat2 = uo
            if ro_t:
                assert not (co_t or cu_t or uo_t)
                cat1 = "ro"
                cat2 = ro

            if (clazz == "LogicalUnit" and propk2name == "UnitCapacity"
                    and cat1 == "ro"):
                cat1new = "co"
                x = ("Contact JohnCook: "
                     "Bad cat1 name, class: >%s<, attribute: >%s<, "
                     "bad cat1: >%s<, corrected cat1: >%s<")
                print x % (clazz, propk2name, cat1, cat1new)
                cat1 = cat1new

            if (clazz == "LogicalUnit" and propk2name == "ClonedFrom"
                    and cat1 == "ro"):
                cat1new = "co"
                x = ("Contact JohnCook: "
                     "Bad cat1 name, class: >%s<, attribute: >%s<, "
                     "bad cat1: >%s<, corrected cat1: >%s<")
                print x % (clazz, propk2name, cat1, cat1new)
                cat1 = cat1new

            clazzattrs.append((propkey, propk2name, ptype, cat1, cat2,
                               rtype, xag))

        parent = parentdict[clazz]
        if parent == k2_schema_root:
            parent = None
        assert clazz not in attrdict

        attrdict[clazz] = (parent, clazzattrs)

    # sort classes for output
    for c in parentsortedkeys:
        adct = {}
        for i, propdict in enumerate(typedict[c]):
            attr = propdict["UsProperty"]
            adct[attr] = i
        first = True
        # sort attributes for init output
        for attr in sorted(adct.keys()):
            propdict = typedict[c][adct[attr]]
            if first:
                first = False
                f.write(_class_line % (c, parentdict[c]))
                f.write(_init_line)
                if c in metadata_set:
                    f.write(_metadata_line)
            if propdict["K2aCmult"] == "Array":
                f.write(_prop_line % (attr, "[]"))
            else:
                f.write(_prop_line % (attr, "None"))

        if c in root_set:
            f.write(_root_init_tail)

        f.write(_super_line % (c,))

        if c in root_set:
            f.write(_root_load_line % (stype,))

        if c in root_set:
            f.write(_property_line)

        if c in metadata_set:
            f.write(_metadata_getter_line)

        assert c in attrdict
        (parent, clazzattrs) = attrdict[c]

#         for (propusname, propk2name, cat1, cat2) in clazzattrs:
        clazzattorder = {}
        for (i, (propusname,  _,  _,  _,  _,  _, _)) in enumerate(clazzattrs):
            clazzattorder[propusname] = i
        for k in sorted(clazzattorder.keys()):
            (propusname, propk2name, ptype, cat1, cat2, rtype, xag) = \
                clazzattrs[clazzattorder[k]]
            # getter
            f.write(_getter_line % (propusname, propusname))

            if cat1 != "ro":
                f.write(_setter_line % (propusname,
                                        propusname,
                                        propusname,
                                        propusname))

        if stype == "uom":
            if c in _uom_funcs:
                f.write(_uom_funcs[c])
        elif stype == "web":
            if c in _web_funcs:
                f.write(_web_funcs[c])

        f.write(_class_tail)

    #########
    #decoder
    for clazz, curdict in secondtypedict.iteritems():
        flattensecond(k2_schema_root, secondtypedict, parentdict, curdict,
                      parentdict[clazz])

    decoder = json.dumps(secondtypedict, f, sort_keys=True, indent=4)

    f.write('_k2dict_json = """%s"""\n' % (decoder.replace(" \n", "\n"),))

    f.write('k2dict = json.loads(_k2dict_json)\n')

    #########
    # output attribute classifier

    attclassifier = json.dumps(attrdict, f, sort_keys=True, indent=4)

    f.write('_k2attr_json = """%s"""\n' %
            (attclassifier.replace(" \n", "\n"),))

    f.write('k2attr = json.loads(_k2attr_json)\n')

    #########
    # output choice classifier

    choiceclassifier = json.dumps(choicetype_dict, f, sort_keys=True, indent=4)

    f.write('_k2choice_json = """%s"""\n' %
            (choiceclassifier.replace(" \n", "\n"),))

    f.write('k2choice = json.loads(_k2choice_json)\n')

    #########
    # typset
    f.write(_typeset_code % (gensource_target_fn[:-3],))

    #########
    # output camelcase to underscore
    attr_cc_to_us_json = json.dumps(attr_cc_to_us, f, sort_keys=True, indent=4)

    f.write('_attr_cc_to_us_json = """%s"""\n' %
            (attr_cc_to_us_json.replace(" \n", "\n"),))

    f.write('attr_cc_to_us = json.loads(_attr_cc_to_us_json)\n')

    #########
    # done
    f.close()

if __name__ == '__main__':

    # Job invariants
#     ods_source_dir = "/home/openstack/workspace-bill-1201/" +\
#         "PMC.REST.SDK.BASE_7.7.8.0_20131027T1109/target/"
#     gensource_target_dir = "/home/openstack/workspace-bill-trunk/"
#     ods_source_dir = "/home/openstack/workspace-bill-trunk/" +\
#         "PMC.REST.SDK.BASE_8.8.1.0_20140217T1257/target/"
    ods_source_dir = "/home/openstack/workspace-bill-trunk/" +\
        "PMC.REST.SDK.BASE_8.8.1.0_20140310T0717/target/"
    gensource_target_dir = "/home/openstack/workspace-bill-trunk/"

    # UOM
    stype = "uom"
    k2_schema_ods = "uom/SchemaDesignV4.ods"
    k2_schema_root = "K2Resource"
    gensource_target_fn = "k2uom.py"
    schemajob(stype, ods_source_dir, gensource_target_dir,
              k2_schema_ods, k2_schema_root, gensource_target_fn)

    # WEB
    stype = "web"
    k2_schema_ods = "web/WebDesignV2.ods"
    k2_schema_root = "K2WebResource"
    gensource_target_fn = "k2web.py"
    schemajob(stype, ods_source_dir, gensource_target_dir,
              k2_schema_ods, k2_schema_root, gensource_target_fn)
