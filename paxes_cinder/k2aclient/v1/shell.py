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

from __future__ import print_function

import sys
import json
import types
import errno
import os
import time
import prettytable

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import utils
from paxes_cinder.k2aclient.v1.k2uom import K2Resource
from paxes_cinder.k2aclient.v1.k2web import K2WebResource
from paxes_cinder.k2aclient.openstack.common import strutils

import logging
_logger = logging.getLogger(__name__)


class K2Encoder(json.JSONEncoder):
    def default(self, obj):
#         if type(obj) is types.ListType:
        if isinstance(obj, types.ListType):
            ll = []
            for li in obj:
                if li is None:
                    ll.append("Null")
                elif isinstance(li, types.StringType):
                    ll.append(li)
                elif isinstance(li, K2Resource) or \
                        isinstance(li, K2WebResource):
                    ll.append(self.default(li))
                else:
                    msg = (_("k2aclient:"
                             " during encoding"
                             " unexpected type: >%s<") %
                           li)
                    _logger.warn(msg)
#             return "["+",".join(ll)+"]"
            return ll

        elif isinstance(obj, K2Resource) or isinstance(obj, K2WebResource):
            outdct = {}
            for k, v in obj.__dict__.iteritems():
                if k[:1] == "_" and not k.startswith("_pattr_"):
                    pass
                elif k == "_pattr_metadata":
                    if hasattr(obj, "id"):
                        outdct["id"] = obj.id
                elif v is None:
#                     outdct[k] = None
                    # if not assigned, don't output
                    pass
                elif k == "group":
                    outdct[k] = v
                elif isinstance(v, types.StringType):
                    outdct[k[7:]] = v
                else:
                    outdct[k[7:]] = self.default(v)

            return outdct

        return json.JSONEncoder.default(self, obj)


def print_k2_list(objs, fields, formatters={}):
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.aligns = ['l' for f in fields]

    for o in objs:

        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                data = getattr(o, field, '')
                row.append(data)
        pt.add_row(row)

    if len(pt._rows) > 0:
        print(strutils.safe_encode(pt.get_string(sortby=fields[0])))


######## UOM
def _print_cluster_list(clusters):
    # simplify for output
    for cluster in clusters:
        cluster._ssp_ = None
        if cluster.cluster_shared_storage_pool is not None:
            cluster._ssp_ = cluster.cluster_shared_storage_pool.split("/")[-1]
    print_k2_list(clusters, ['cluster_name', 'id', 'cluster_id', '_ssp_'])


def _print_logicalpartition_list(logicalpartitions):
    print_k2_list(logicalpartitions, ['partition_name',
                                      'id',
                                      'partition_type',
                                      'partition_id',
                                      'partition_state'])


def _print_managedsystem_list(managedsystems):
    print_k2_list(managedsystems, ['system_name',
                                   'id',
                                   'primary_ip_address',
                                   'state'])


def _print_managementconsole_list(managementconsole):
    print_k2_list(managementconsole, ['management_console_name',
                                      'id'])


def _print_sharedstoragepool_list(sharedstoragepools):
    print_k2_list(sharedstoragepools, ['storage_pool_name',
                                       'id',
                                       'capacity',
                                       'free_space',
                                       'over_commit_space',
                                       'total_logical_unit_size',
                                       'unique_device_id'])


def _print_sharedstoragepool_list_lus(sharedstoragepool, full=False):
    lus = sharedstoragepool.logical_units.logical_unit
    if not full:
        print_k2_list(lus, ['unit_name',
                            'unit_capacity',
                            'thin_device',
                            'logical_unit_type'])
    else:
        print_k2_list(lus, ['unit_name',
                            'unique_device_id',
                            'cloned_from',
                            'unit_capacity',
                            'thin_device',
                            'logical_unit_type'])


def _print_virtualioserver_list(virtualioservers):
    print_k2_list(virtualioservers, ['partition_name',
                                     'id',
                                     'partition_type',
                                     'partition_id',
                                     'partition_state'])


def _print_clientnetworkadapter_list(clientnetworkadapters):
    print_k2_list(clientnetworkadapters, ['id',
                                          'mac_address',
                                          'port_vlan_id',
                                          'virtual_switch_id',
                                          'adapter_type',
                                          'location_code',
                                          'local_partition_id',
                                          'virtual_slot_number'])


def _print_virtualnetwork_list(virtualnetworks):
    print_k2_list(virtualnetworks, ['network_name',
                                    'id',
                                    'network_vlan_id',
                                    'vswitch_id',
                                    'tagged_network'])


def _print_virtualswitch_list(virtualswitchs):
    print_k2_list(virtualswitchs, ['switch_name',
                                   'id',
                                   'switch_id',
                                   'switch_mode'])


# Cluster
def do_cluster_list(cs, args):
    """Output a list of cluster."""
    cluster_list = cs.cluster.list()
    _print_cluster_list(cluster_list)


@utils.arg('cluster',
           metavar='<cluster>',
           help=_('Id of the cluster.'))
def do_cluster_show(cs, args):
    """Output details for a specific cluster."""
    cluster = cs.cluster.get(args.cluster)
    json.dump(cluster, sys.stdout, sort_keys=True, indent=4, cls=K2Encoder)
    print ("\n")


@utils.arg('cluster',
           metavar='<cluster_id>',
           help=_('UUID of the cluster containing the LUs.'))
@utils.arg('source',
           metavar='<source_udid>',
           help=_('UDID of the source logicalunit.'))
@utils.arg('destination',
           metavar='<destination_udid>',
           help=_('UDID of the destination logicalunit.'))
def do_cluster_lulinkedclone(cs, args):
    """Clone a SharedStoragePool (SSP) LogicalUnit (LU)"""
    cluster = cs.cluster.get(args.cluster)
    cluster.api.lu_linked_clone(cluster, args.source, args.destination)


# LogicalPartitition
@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem to list logicalpartitions'))
def do_logicalpartition_list(cs, args):
    """Given a managedsystem, output its logicalpartitions."""
    logicalpartitions = cs.logicalpartition.list(args.managedsystem)
    _print_logicalpartition_list(logicalpartitions)


def do_logicalpartition_listasroot(cs, args):
    """Output a list of all logicalpartitions."""
    logicalpartitions = cs.logicalpartition.listasroot()
    _print_logicalpartition_list(logicalpartitions)


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('logicalpartition',
           metavar='<logicalpartition>',
           help=_('Id of the logicalpartition.'))
def do_logicalpartition_show(cs, args):
    """Output details for a specific logicalpartition """
    """under a given managedsystem."""
    logicalpartition = cs.logicalpartition.get(args.managedsystem,
                                               args.logicalpartition)
    json.dump(logicalpartition, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('logicalpartition',
           metavar='<logicalpartition>',
           help=_('Id of the logicalpartition.'))
def do_logicalpartition_showasroot(cs, args):
    """Output details for a specific logicalpartition."""
    logicalpartition = cs.logicalpartition.getasroot(args.logicalpartition)
    json.dump(logicalpartition, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('logicalpartitions',
           metavar='<logicalpartitions>',
           help=_('UDIDs of the logicalpartition.'),
           nargs='+')
def do_logicalpartition_delete(cs, args):
    """Delete logicalpartitions."""
    for lpar in args.logicalpartitions:
        cs.managedsystem.deletebyid(args.managedsystem,
                                    "LogicalPartition",
                                    lpar)


# ManagedSystem
def do_managedsystem_list(cs, args):
    """Output a list of managedsystem."""
    managedsystem_list = cs.managedsystem.list()
    _print_managedsystem_list(managedsystem_list)


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
def do_managedsystem_show(cs, args):
    """Output details for a specific managedsystem."""
    managedsystem = cs.managedsystem.get(args.managedsystem)
    json.dump(managedsystem, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


# ManagmentConsole
def do_managementconsole_list(cs, args):
    """Output a list of managedsystem."""
    managementconsole_list = cs.managementconsole.list()
    _print_managementconsole_list(managementconsole_list)


@utils.arg('managementconsole',
           metavar='<managementconsole>',
           help=_('Id of the managementconsole.'))
def do_managementconsole_show(cs, args):
    """Output details for a specific managementconsole."""
    managementconsole = cs.managementconsole.get(args.managementconsole)
    json.dump(managementconsole, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('managementconsole',
           metavar='<managementconsole>',
           help=_('Id of the managementconsole.'))
@utils.arg('cmd',
           metavar='<cmd>',
           help=_('Command to run.'))
def do_managementconsole_cmd(cs, args):
    """Run command"""

#     # could get mc from list
#     mcs = cs.managementconsole.list()
#     mc = cs.managementconsole.get(mcs[0].id)

    mc = cs.managementconsole.get(args.managementconsole)

    jresponse = cs.managementconsole.run_cmd(mc,
                                             args.cmd)

    json.dump(jresponse, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('managementconsole',
           metavar='<managementconsole>',
           help=_('Id of the managementconsole.'))
@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualioserver',
           metavar='<virtualioserver_id>',
           help=_('UUID of the virtualioserver.'))
@utils.arg('cmd',
           metavar='<cmd>',
           help=_('Command to run.'))
def do_managementconsole_cmd_vios(cs, args):
    """Run vios command"""

#     # could get mc from list
#     mcs = cs.managementconsole.list()
#     mc = cs.managementconsole.get(mcs[0].id)

    mc = cs.managementconsole.get(args.managementconsole)
    ms = cs.managedsystem.get(args.managedsystem)
    vios = cs.virtualioserver.get(ms.id, args.virtualioserver)

    jresponse = cs.managementconsole.run_vios_cmd(mc,
                                                  ms,
                                                  vios,
                                                  args.cmd)

    json.dump(jresponse, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


# SharedStoragePool
# @utils.arg('cluster',
#     metavar='<cluster>',
#     help=_('Id of the cluster to list sharedstoragepool'))
def do_sharedstoragepool_list(cs, args):
    """Output a list of sharedstoragepool."""
#     sharedstoragepools = cs.sharedstoragepool.list(args.cluster)
    sharedstoragepools = cs.sharedstoragepool.list()
    _print_sharedstoragepool_list(sharedstoragepools)


# @utils.arg('cluster',
#            metavar='<cluster>',
#            help=_('Id of the cluster.'))
@utils.arg('sharedstoragepool',
           metavar='<sharedstoragepool>',
           help=_('Id of the sharedstoragepool.'))
def do_sharedstoragepool_show(cs, args):
    """Output details for a specific sharedstoragepool."""
    sharedstoragepool = cs.sharedstoragepool.get(args.sharedstoragepool)
    json.dump(sharedstoragepool, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('sharedstoragepool',
           metavar='<sharedstoragepool_id>',
           help=_('UUID of the sharedstoragepool.'))
@utils.arg('unitname',
           metavar='<unit_name>',
           help=_('Name of the new logicalunit.'))
@utils.arg('unitcapacity',
           metavar='<unit_capacity>',
           help=_('Capacity of the new logicalunit.'))
@utils.arg('--thin',
           metavar='<True|False>',
           help=_('Optional flag to control whether '
           'the new logicalunit will be thick or thin'),
           default=False)
@utils.arg('--lut',
           metavar='<logical_unit_type>',
           help=_('LogicalUnitType: VirtualIO_Disk | VirtualIO_Image'),
           default="VirtualIO_Disk")
@utils.arg('--cf',
           metavar='<cloned_from>',
           help=_('Optional udid of LU to clone from, new if omitted'),
           default=None)
def do_sharedstoragepool_update_append_lu(cs, args):
    """Add a logicalunit (LU) to a sharedstoragepool (SSP)"""
    ssp = cs.sharedstoragepool.get(args.sharedstoragepool)
    (new_lu, updated_ssp) = ssp.update_append_lu(args.unitname,
                                                 int(args.unitcapacity),
                                                 args.thin,
                                                 args.lut,
                                                 args.cf)
    print ("For sharedstoragepool: >%s<, appended logical unit:" %
           updated_ssp.id)

    json.dump(new_lu, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('sharedstoragepool',
           metavar='<sharedstoragepool_id>',
           help=_('UUID of the sharedstoragepool.'))
@utils.arg('logicalunits',
           metavar='<logicalunit_udids>',
           help=_('UDIDs of the logicalunit.'),
           nargs='+')
def do_sharedstoragepool_update_del_lus(cs, args):
    """Delete a logicalunits (LUs) from a sharedstoragepool (SSP)"""
    ssp = cs.sharedstoragepool.get(args.sharedstoragepool)
    ssp.update_del_lus(args.logicalunits)


@utils.arg('sharedstoragepool',
           metavar='<sharedstoragepool_id>',
           help=_('UUID of the sharedstoragepool.'))
@utils.arg('--full',
           metavar='<True|False>',
           help=_('Optional flag to control whether '
           'full details should be output'),
           default=False)
def do_sharedstoragepool_list_lus(cs, args):
    """List the logicalunits (LUs) in a sharedstoragepool (SSP)"""
    ssp = cs.sharedstoragepool.get(args.sharedstoragepool)
    _print_sharedstoragepool_list_lus(ssp, full=args.full)


# VirtualIOServer
@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem to list virtualioservers'))
def do_virtualioserver_list(cs, args):
    """Output a list of virtualioservers."""
    virtualioservers = cs.virtualioserver.list(args.managedsystem)
    _print_virtualioserver_list(virtualioservers)


def do_virtualioserver_listasroot(cs, args):
    """Output a list of all virtualioservers."""
    virtualioservers = cs.virtualioserver.listasroot()
    _print_virtualioserver_list(virtualioservers)


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualioserver',
           metavar='<virtualioserver>',
           help=_('Id of the virtualioserver.'))
@utils.arg('--xag',
           metavar='<xag>',
           action='append',
           help=_('Optional extended attributes'
                  ' Valid values include: All, Advanced, Hypervisor,'
                  ' SystemNetwork, ViosStorage, ViosNetwork, ViosFCMapping,'
                  ' ViosSCSIMapping, and None'
                  ' May be used multiple times.'
                  ' "All" if omitted'
                  ),
           default=[])
def do_virtualioserver_show(cs, args):
    """Output details for a virtualioserver."""
    virtualioserver = cs.virtualioserver.get(args.managedsystem,
                                             args.virtualioserver,
                                             xag=args.xag)
    json.dump(virtualioserver, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('virtualioserver',
           metavar='<virtualioserver>',
           help=_('Id of the virtualioserver.'))
def do_virtualioserver_showasroot(cs, args):
    """Output details for a virtualioserver."""
    virtualioserver = cs.virtualioserver.getasroot(args.virtualioserver)
    json.dump(virtualioserver, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


# @utils.arg('managedsystem',
#            metavar='<managedsystem>',
#            help=_('Id of the managedsystem.'))
# @utils.arg('virtualioserver',
#            metavar='<virtualioserver>',
#            help=_('Id of the virtualioserver.'))
# @utils.arg(
#     '--output-file-name-root',
#     metavar='<output-file-name-root>',
#     default='/tmp/vios-rtu',
#     help=_('Root file for output'))
# def do_virtualioserver_rtu(cs, args):
#     """Output round trip details for a virtualioserver."""
#
#     virtualioserver = cs.virtualioserver.get(args.managedsystem,
#                                              args.virtualioserver)
#
#     # get xml
#     body = virtualioserver._k2resp.body
#     with open(args.output_file_name_root + ".get.xml", 'w') as f:
#         f.write(body)
#
#     # json
#     with open(args.output_file_name_root + ".json", 'w') as f:
#         json.dump(virtualioserver, f, sort_keys=True, indent=4,
#                   cls=K2Encoder)
#         f.write("\n")
#
#     # updated xml
#     element = v1k2creater.process_root("uom",
#                                        v1k2creater.Mode.UPDATE,
#                                        virtualioserver)
#     xml = minidom.parseString(element.toxmlstring())
#     with open(args.output_file_name_root + ".update.xml", 'w') as f:
#         f.write(xml.toprettyxml(indent=' ' * 4))
#
# ######
#     ms_id = args.managedsystem
#     lpar_id = "1B071EC7-29A4-4717-9C15-B867BAE6BD7A"
#     new_virtual_scsi_mapping = []
#     print ("VSM edits:")
#     for vsm in virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping:
#
#         ####
# #         if vsm.client_adapter\
# #                 is not None and\
# #                 vsm.client_adapter.associated_logical_partition\
# #                 is not None:
#         keep = True
#         if vsm.associated_logical_partition is not None:
#             parts = vsm.associated_logical_partition.split('/')
#             cur_ms_id = parts[-3]
#             cur_lpar_id = parts[-1]
#             if cur_ms_id == ms_id and cur_lpar_id == lpar_id:
#                 keep = False
#                 msg = "  will delete: vsm.server_adapter.adapter_name: >%s<"
#                 print (msg % (vsm.server_adapter.adapter_name,))
#
#         if keep:
#             new_virtual_scsi_mapping.append(vsm)
#             msg = "  will keep: vsm.server_adapter.adapter_name: >%s<"
#             print (msg % (vsm.server_adapter.adapter_name,))
#
# #     print ("Updated VSM will be:")
# #     for vsm in new_virtual_scsi_mapping:
# #         msg = "  vsm.client_adapter.adapter_name: >%s<"
# #         print (msg % (vsm.server_adapter.adapter_name,))
#
#     if len(new_virtual_scsi_mapping) != \
#             len(virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping
#                 ):
#         virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping = \
#             new_virtual_scsi_mapping
#
#     # updated xml
#     element = v1k2creater.process_root("uom",
#                                        v1k2creater.Mode.UPDATE,
#                                        virtualioserver)
#     xml = minidom.parseString(element.toxmlstring())
#     with open(args.output_file_name_root + ".update2.xml", 'w') as f:
#         f.write(xml.toprettyxml(indent=' ' * 4))


# ClientNetworkAdapter
@utils.arg('logicalpartition',
           metavar='<logicalpartition>',
           help=_('Id of the logicalpartition to list clientnetworkadapters'))
def do_clientnetworkadapter_list(cs, args):
    """Given a logicalpartition, output its clientnetworkadapters."""
    clientnetworkadapters = cs.clientnetworkadapter.list(args.logicalpartition)
    _print_clientnetworkadapter_list(clientnetworkadapters)


@utils.arg('logicalpartition',
           metavar='<logicalpartition>',
           help=_('Id of the logicalpartition.'))
@utils.arg('clientnetworkadapter',
           metavar='<clientnetworkadapter>',
           help=_('Id of the clientnetworkadapter.'))
def do_clientnetworkadapter_show(cs, args):
    """Output details for a specific clientnetworkadapter """
    """under a given logicalpartition."""
    clientnetworkadapter = \
        cs.clientnetworkadapter.get(args.logicalpartition,
                                    args.clientnetworkadapter)
    json.dump(clientnetworkadapter, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('logicalpartition',
           metavar='<logicalpartition>',
           help=_('Id of the logicalpartition.'))
@utils.arg('clientnetworkadapters',
           metavar='<clientnetworkadapters>',
           help=_('UDIDs of the clientnetworkadapter.'),
           nargs='+')
def do_clientnetworkadapter_delete(cs, args):
    """Delete clientnetworkadapter."""
    for clientnetworkadapter in args.clientnetworkadapters:
        cs.clientnetworkadapter.deletebyid(args.logicalpartition,
                                           clientnetworkadapter)


# VirtualNetwork
@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem to list virtualnetworks'))
def do_virtualnetwork_list(cs, args):
    """Given a managedsystem, output its virtualnetworks."""
    virtualnetworks = cs.virtualnetwork.list(args.managedsystem)
    _print_virtualnetwork_list(virtualnetworks)


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualnetwork',
           metavar='<virtualnetwork>',
           help=_('Id of the virtualnetwork.'))
def do_virtualnetwork_show(cs, args):
    """Output details for a specific virtualnetwork """
    """under a given managedsystem."""
    virtualnetwork = cs.virtualnetwork.get(args.managedsystem,
                                           args.virtualnetwork)
    json.dump(virtualnetwork, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualnetworks',
           metavar='<virtualnetworks>',
           help=_('UDIDs of the virtualnetwork.'),
           nargs='+')
def do_virtualnetwork_delete(cs, args):
    """Delete virtualnetwork."""
    for virtualnetwork in args.virtualnetworks:
        cs.virtualnetwork.deletebyid(args.managedsystem,
                                     virtualnetwork)


# VirtualNetwork
@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem to list virtualswitchs'))
def do_virtualswitch_list(cs, args):
    """Given a managedsystem, output its virtualswitchs."""
    virtualswitchs = cs.virtualswitch.list(args.managedsystem)
    _print_virtualswitch_list(virtualswitchs)


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualswitch',
           metavar='<virtualswitch>',
           help=_('Id of the virtualswitch.'))
def do_virtualswitch_show(cs, args):
    """Output details for a specific virtualswitch """
    """under a given managedsystem."""
    virtualswitch = cs.virtualswitch.get(args.managedsystem,
                                         args.virtualswitch)
    json.dump(virtualswitch, sys.stdout, sort_keys=True, indent=4,
              cls=K2Encoder)
    print ("\n")


@utils.arg('managedsystem',
           metavar='<managedsystem>',
           help=_('Id of the managedsystem.'))
@utils.arg('virtualswitchs',
           metavar='<virtualswitchs>',
           help=_('UDIDs of the virtualswitch.'),
           nargs='+')
def do_virtualswitch_delete(cs, args):
    """Delete virtualnetwork."""
    for virtualswitch in args.virtualswitchs:
        cs.virtualswitch.deletebyid(args.managedsystem,
                                    virtualswitch)


######## WEB
def _print_web_file_list(files):
    print_k2_list(files, ['filename', 'id', 'file_uuid', 'file_enum_type'])


# WEB File
def do_web_file_list(cs, args):
    """Output a list of file."""
    file_list = cs.web_file.list()
    _print_web_file_list(file_list)


@utils.arg('file',
           metavar='<file>',
           help=_('Id of the file.'))
def do_web_file_show(cs, args):
    """Output details for a specific file."""
    uomfile = cs.web_file.get(args.file)
    json.dump(uomfile, sys.stdout, sort_keys=True, indent=4, cls=K2Encoder)
    print ("\n")


@utils.arg('files',
           metavar='<files>',
           help=_('Ids of the files.'),
           nargs='+')
def do_web_file_delete(cs, args):
    """Delete files."""
    for webfile in args.files:
        cs.web_file.deletebyid(webfile)


######## MISC
@utils.arg('uomresource',
           metavar='<uomresource>',
           help=_('/rest/api/uom<uomresource>.'))
@utils.arg(
    '--output-file-name',
    metavar='<output-file-name>',
    default=None,
    help=_('Send output to file'))
def do_uom_show(cs, args):
    """Output details for a UOM path."""
    k2resp = cs.uom.get(args.uomresource)
    if args.output_file_name:
        f = open(args.output_file_name, "w")
        f.write(k2resp.body)
        f.close()
    else:
        print (k2resp.body)


@utils.arg(
    '--cinder-conf-dir',
    metavar='<cinder-conf-dir>',
    default="/etc/cinder",
    help=_('Read cinder ssp conf files and report on health'))
def do_paxes_check_sspconf(cs, args):
    """Output health details for PowerVC ssp resources."""
    tset = cs.paxes.check_ssp_conf(args.cinder_conf_dir)
    tforj = cs.paxes.result_output_as_dict(tset)
    json.dump(tforj, sys.stdout, sort_keys=True, indent=4)
    print("")


################################
# VIOS SNAP FUNCTION
def _prepdir(targetdir):
    ct = time.localtime()
    subdir = time.strftime("%Y-%m-%d_%H-%M-%S", ct)
    return os.path.join(targetdir, subdir)


@utils.arg('cluster',
           metavar='<cluster>',
           help=_('Id of the cluster.'))
def do_cluster_vios_ips(cs, args):
    """Get VIOS ips for a specific cluster."""
    cluster = cs.cluster.get(args.cluster)
    vios_ips = cs.cluster.extract_vios_ips(cluster)
    json.dump(vios_ips, sys.stdout)
    print ("\n")
