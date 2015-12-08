# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# Authors:
#   Ronen Kat <ronenkat@il.ibm.com>
#   Avishay Traeger <avishay@il.ibm.com>

import operator
import re
import time

from cinder import exception
from cinder import context
from cinder.openstack.common import log as logging
from paxes_cinder import _
from cinder.openstack.common import loopingcall
from cinder.openstack.common import processutils

from collections import deque
from eventlet.event import Event
from functools import reduce

from paxes_cinder.volume import discovery_driver
from paxes_cinder import exception as paxes_exception
from paxes_cinder.volume.drivers.svc import storwize_svc_driver_id
from paxes_cinder.zonemanager.paxes_fc_zone_manager \
    import PowerVCZoneManager
from cinder.openstack.common import excutils
from oslo.config import cfg
from cinder import rpc

import paramiko
import math

LOG = logging.getLogger(__name__)

RESTRICTED_METADATA_VDISK_ID_KEY = "vdisk_id"
RESTRICTED_METADATA_VDISK_UID_KEY = "vdisk_uid"
RESTRICTED_METADATA_VDISK_NAME_KEY = "vdisk_name"
RESTRICTED_METADATA_SCSI_INQUIRY_83_KEY = "scsi_inquiry_83"
RESTRICTED_METADATA_BYTE_SIZE_KEY = "byte_size"


CONF = cfg.CONF
CONF.import_opt('storwize_fcmap_poll_maxpct',
                'paxes_cinder.volume.drivers.svc.storwize_svc_driver_id')
CONF.import_opt('storwize_fcmap_poll_interval',
                'paxes_cinder.volume.drivers.svc.storwize_svc_driver_id')
CONF.import_opt('storwize_fcmap_delete_queue_enabled',
                'paxes_cinder.volume.drivers.svc.storwize_svc_driver_id')


class StorwizeSVCProductDriver(
        discovery_driver.VolumeDiscoveryDriver,
        storwize_svc_driver_id.StorwizeSVCDriverIdDriver):
    def __init__(self, *args, **kwargs):
        super(StorwizeSVCProductDriver, self).__init__(*args, **kwargs)
        # create deque to hold all the vdisk delete requests that has
        # pending flashcopy mapping.
        self.fcmap = deque()
        self.fcmap_timer = []

    def do_setup(self, ctxt):

        # Do not start fcmap delete queue polling timer thread
        # if per vdisk delete thread polling is used.
        if CONF.storwize_fcmap_delete_queue_enabled:
            # Start the fixed interval timer thread to poll the flashcopy
            # mapping delete queue(fcmap). The fcmap queue is used to hold
            # all the pending delete vdisks that have an in-flight flashcopy.
            # The polling timer will scan the queue and speed up the flashcopy
            # to removal for the pending delete vdisk. Every cycle, the queue
            # will be scanned and create a list ordered by the flashcopy
            # dependent-mappings. The fcmap that has the least dependency
            # will be handled first. storwize_fcmap_poll_maxpct tunable will be
            # used to control the timer run interval per cycle to prevent
            # timer overrun. With 30 seconds storwize_fcmap_poll_interval
            # (default) and 80% runtime of the polling interval, delete fifty
            # 10GB vdisks that are cloned from the single source vdisks in
            # parallel takes about 7 minutes.
            timer = loopingcall.FixedIntervalLoopingCall(
                self.fcmapping_handler,
                self.fcmap, CONF.storwize_fcmap_poll_interval)
            timer.start(interval=CONF.storwize_fcmap_poll_interval)
            self.fcmap_timer.append(timer)
            msg = (_("StorwizeSVCProductDriver: start flashcopy mapping "
                     "polling timer, polling interval: %(intval)s seconds") %
                   dict(intval=CONF.storwize_fcmap_poll_interval))
            LOG.info(msg)

        super(StorwizeSVCProductDriver, self).do_setup(ctxt)

    def _create_vdisk(self, names, size, units, opts):
        """Create a new vdisk, returns vdisk ID
        names contains a list of names to use in order of preference.  We try
        them all until one works, as a simple way of handling names that are
        invalid or already in use on the storage controller.
        """

        names_string = ', '.join(names)
        LOG.debug(_('enter: _create_vdisk: candidate names %s ') %
                  names_string)

        model_update = None
        easytier = 'on' if opts['easytier'] else 'off'

        ###############################################################
        # This section is the delta from community driver which only
        # use storwize_svc_volpool_name config option to choose
        # storage pool. PowerVC supports dynamic pool selection
        # from extra_spects. Remove this _create_vdisk if we
        # contribute this back.

        #Set the default Storage Pool from the configuration file.
        mdiskgrp = self.configuration.storwize_svc_volpool_name

        #Check for override values specified in the extra-specs
        for opt, val in opts.iteritems():
            #Override the Storage Pool if specified.
            if opt == 'storage_pool':
                mdiskgrp = val
        ###############################################################

        # Set space-efficient options
        if opts['rsize'] == -1:
            ssh_cmd_se_opt = []
        else:
            ssh_cmd_se_opt = ['-rsize', '%s%%' % str(opts['rsize']),
                              '-autoexpand', '-warning',
                              '%s%%' % str(opts['warning'])]
            if not opts['autoexpand']:
                ssh_cmd_se_opt.remove('-autoexpand')

            if opts['compression']:
                ssh_cmd_se_opt.append('-compressed')
            else:
                ssh_cmd_se_opt.extend(['-grainsize', str(opts['grainsize'])])

        # Iterate over all names.  We break out of the loop as soon as we find
        # a name that works.
        for name in names:

            # If an exception is raised here, we remember it in case we need to
            # raise it later.
            last_exception = None

            ssh_cmd = ['svctask', 'mkvdisk', '-name', name,
                       '-mdiskgrp', '"%s"' % mdiskgrp, '-iogrp', '0',
                       '-size', size, '-unit', units,
                       '-easytier', easytier] + ssh_cmd_se_opt

            # We do our own error checking because we want to be able to
            # silently retry if we fail.
            out, err = self._run_ssh(ssh_cmd, check_exit_code=False)

            if err:
                cmd = ' '.join(ssh_cmd)

                if ("CMMVC6035E" in err or
                        "CMMVC6527E" in err or
                        "CMMVC5738E" in err):
                    # CMMVC6035E: Name already in use.
                    # CMMVC6527E: Invalid name
                    # CMMVC5738E: Name too long
                    # If we failed with one of the above errors, try again with
                    # a different name.  However, remember this exception, in
                    # case we have run out of names and really do have to raise
                    # this exception.
                    e = processutils.ProcessExecutionError(exit_code=1,
                                                           stdout=out,
                                                           stderr=err,
                                                           cmd=cmd)
                    last_exception = e
                    continue
                else:
                    # Some other error occurred - raise the exception
                    # immediately.
                    raise processutils.ProcessExecutionError(exit_code=1,
                                                             stdout=out,
                                                             stderr=err,
                                                             cmd=cmd)

            self._assert_ssh_return(len(out.strip()), '_create_vdisk',
                                    ssh_cmd, out, err)

            # If we get here then we don't need to try any more names
            break

        # If we came out of the loop with last_exception set, then this is
        # because we ran out of names that we could try, and we really should
        # raise the exception that we remembered.
        if last_exception:
            raise last_exception

        # Ensure that the output is as expected
        match_obj = re.search('Virtual Disk, id \[([0-9]+)\], '
                              'successfully created', out)
        # Make sure we got a "successfully created" message with vdisk id
        self._driver_assert(
            match_obj is not None,
            _('_create_vdisk %(name)s - did not find '
              'success message in CLI output.\n '
              'stdout: %(out)s\n stderr: %(err)s')
            % {'name': name, 'out': str(out), 'err': str(err)})

        vdisk_id = match_obj.group(1)

        LOG.debug(_('leave: _create_vdisk: volume %(name)s ID %(id)s ') %
                  {'name': name, 'id': vdisk_id})

        return vdisk_id, name

    def get_default_vol_type(self):
        """Returns the default volume type from the svc's .conf file"""
        vtn = self.configuration.default_volume_type
        return vtn.decode('utf-8') if vtn else vtn

    def get_storage_metadata(self):
        """Helper Method to Retrieve meteadata for a host on the SVC"""
        volume_pools = []
        ssh_cmd = ['svcinfo', 'lsmdiskgrp', '-delim', ':']
        out, err = self._run_ssh(ssh_cmd)
        #Out should return a string with the values
        #of the keys as the first item, id:name:status...
        #and the values for the keys in the following items
        #ex: 0:mdiskgrp0:online:1:175.....
        self._assert_ssh_return(len(out) > 0 and out is not None,
                                'get_volume_pools',
                                ssh_cmd, out, err)
        pool_lines = out.strip().split('\n')
        table_headers = pool_lines.pop(0).split(':')
        compression = 'yes' if self.get_compression_enabled() else 'no'
        #pool_lines.pop(0) ex: ['id:name:status:mdisk_count:more_fields']
        #need to use .split to get ['id','name','mdisk_count','more_fields']
        for line in pool_lines:
            line = line.split(':')
            volume_pool = dict(zip(table_headers, line))
            volume_pools.append(volume_pool)
        return {'volume_pools': volume_pools,
                'compression_supported': compression}

    def discover_volumes(self, context, filters=None):
        """Helper Method to Retrieve a list of volumes for a host
        Currently supported filters:

         'host_refs': [ WWPN, ... ]
           Returns only volumes that are mapped to at least one of the WWPNS in
           the specified list.  Matching is case-insensitive.
        """

        # If we are filtering, create a set from the WWPN list to make
        # filtering easier.  Convert the WWPNs to upper-case for consistency
        filter_set = None
        if filters is not None and 'host_refs' in filters:
            upper_refs = [ref.upper() for ref in filters['host_refs']]
            filter_set = set(upper_refs)

        # Obain vdisk-to-wwpn mapping information, which we use to
        # augment the vdisk list, and also possibly filter.
        # We will also return the vdisk-to-scsi_id mapping information
        vdisk_to_rmt_wwpn, vdisk_connect_info = self._get_vdisk_to_wwpn_map()

        volume_list = []
        # retrieve size in bytes
        ssh_cmd = ['svcinfo', 'lsvdisk', '-bytes', '-delim', ':']
        out, err = self._run_ssh(ssh_cmd)
        #self.discover_volumes(ssh_cmd)
        #Out in string format a list containing
        #a row of headers followed by rows of values
        #example of the header status:se_copy_count:IO_group_id:
        #capacity:name and so on
        #example of the values online:0:0:10.00GB:etc
        self._assert_ssh_return(len(out) > 0 and out is not None,
                                'get_volume_pools',
                                ssh_cmd, out, err)
        list_lines = out.strip().split('\n')
        table_headers = list_lines.pop(0).split(':')
        for line in list_lines:
            line = line.split(':')
            volume = {}
            volume_table = {}
            volume_table = dict(zip(table_headers, line))
            volume['name'] = volume_table['name']
            volume['storage_pool'] = volume_table['mdisk_grp_name']
            volume['status'] = self._map_volume_status(volume_table['status'])
            volume['size'] = self._parse_volume_size(volume_table['capacity'])
            vdisk_uid = volume_table['vdisk_UID']
            volume['restricted_metadata'] = {
                RESTRICTED_METADATA_VDISK_ID_KEY: volume_table['id'],
                RESTRICTED_METADATA_VDISK_UID_KEY: vdisk_uid,
                RESTRICTED_METADATA_VDISK_NAME_KEY: volume_table['name'],
                RESTRICTED_METADATA_SCSI_INQUIRY_83_KEY: vdisk_uid,
                RESTRICTED_METADATA_BYTE_SIZE_KEY: volume_table['capacity']
            }
            if volume['status'] == 'error':
                volume['support'] = {
                    "status": "not_supported",
                    "reasons": [
                        'This volume is not a candidate for management '
                        'because it is offline. '
                        'A volume is offline and unavailable if one '
                        'of the following takes place: '
                        'both nodes in the I/O group are missing, '
                        'none of the nodes in the I/O group that are '
                        'present can access the volume, '
                        'all synchronized copies for the volume '
                        'are in storage pools that are offline, '
                        'the volume is formatting. '
                    ]
                }
                err_msg = (_("The volume %(name)s is in the error state "
                             "and not a candidate for management.  "
                             "vdisk status: %(status)s  "
                             "vdisk id: %(vdisk_id)s  "
                             "vdisk uid: %(vdisk_uid)s  ") %
                           {'name': volume['name'],
                            'status': volume['status'],
                            'vdisk_id': volume_table['id'],
                            'vdisk_uid': vdisk_uid})
                LOG.error(err_msg)
            else:
                volume['support'] = {"status": "supported"}

            # Add mapping data, if it exists.
            rmt_wwpns, lcl_wwpns = (set(), set())
            if volume_table['id'] in vdisk_to_rmt_wwpn:
                wwpns = vdisk_to_rmt_wwpn[volume_table['id']]
                volume['mapped_wwpns'] = wwpns
                if filter_set is not None:
                    rmt_wwpns = set([wwpn.upper() for wwpn in wwpns])
                # If the Volume is attached, then Import isn't Supported
                if len(wwpns) > 0:
                    volume['status'] = 'in-use'
                    volume['support'] = {
                        "status": "not_supported",
                        "reasons": [
                            'This volume is not a candidate for management '
                            'because it is already attached to a virtual '
                            'machine.  To manage this volume with PowerVC, '
                            'you must bring the virtual machine under '
                            'management.  Select to manage the virtual '
                            'machine that has the volume attached.  The '
                            'attached volume will be automatically included '
                            'for management.'
                        ]
                    }
            # If there is the Target Port Info, add it to the Connection Info
            if volume_table['id'] in vdisk_connect_info:
                connect_info = vdisk_connect_info[volume_table['id']]
                wwpns = connect_info.get('target_wwn', [])
                if filter_set is not None:
                    lcl_wwpns = set([wwpn.upper() for wwpn in wwpns])
                if len(connect_info) > 0:
                    volume['connection_info'] = connect_info
            # If we are not filtering on WWPNs or UID's, or we ARE filtering
            # and there is a match, add this disk to the list to be returned.
            if ((filter_set is None or len(filter_set & rmt_wwpns) > 0 or
                 len(filter_set & lcl_wwpns) > 0 or vdisk_uid in filter_set)):
                volume_list.append(volume)

        return volume_list

    def query_volumes(self, context, volumes, server_info={}, mark_boot=True):
        """Returns import-related details for the Volumes from the Provider"""
        uid_map, wwpn_map = (dict(), dict())
        returned_volumes, boot_map = (list(), dict())
        #Build a map of the WWPN/UID's for each Server for quicker lookup
        for server_id, server in server_info.iteritems():
            for volume in server.get('volumes', []):
                uid = volume.get('unique_device_id')
                wwpns = volume.get('wwpns', [])
                #Build maps of the UID and WWPN depending on which is set
                if uid is not None:
                    uid_map[uid] = server_id
                for wwpn in wwpns:
                    wwpn_map[wwpn.upper()] = server_id
        #Loop through the Volumes, setting the attachment info
        for volume in volumes:
            volume_copy = volume.copy()
            server_id, connect_info = (None, None)
            #Parse the UID out of the MetaData to use for matching Servers
            metadata = volume_copy.get('restricted_metadata', {})
            uid = metadata.get(RESTRICTED_METADATA_VDISK_UID_KEY)
            #Parse the correct Connection Info based on the WWPN's
            connect_infos = volume_copy.pop('connection_info', {})
            if len(connect_infos) > 0:
                #Default to the first one if the WWPN's weren't specified
                connect_info = connect_infos.values()[0]
                for cinfo in connect_infos.values():
                    wwpns = cinfo.get('source_wwn', [])
                    #Loop through each of the WWPN's looking for the Server
                    for wwpn in wwpns:
                        #If we found a Server for the WWPN, use this Info
                        if wwpn_map.get(wwpn.upper()) is not None:
                            server_id = wwpn_map[wwpn.upper()]
                            connect_info = cinfo
                            break
                    #If we already found a matching Server, continue on
                    if server_id is not None:
                        break
            #If the Server for this UID is in the Map, mark it attached
            if not server_id and uid in uid_map:
                server_id = uid_map[uid]
            if server_id is not None:
                volume_copy['instance_uuid'] = server_id
                #If we were given valid Connection Primer, set the full value
                if connect_info is not None:
                    target_lun = connect_info.get('target_lun')
                    target_wwn = connect_info.get('target_wwn')
                    #If given the VDisk UID from the VM, then it isn't NPIV
                    npiv = uid not in uid_map
                    volume_copy['connection_info'] =\
                        self._get_connection_info(target_lun, target_wwn, npiv)
                #See if this should be flagged as the Server's Boot Volume
                if mark_boot is True and server_id not in boot_map:
                    volume_copy['bootable'] = True
                    boot_map[server_id] = volume_copy['uuid']
            #Add the Copy of the Volume to the list to be returned
            returned_volumes.append(volume_copy)
        return returned_volumes

    @staticmethod
    def _get_connection_info(target_lun, target_wwn, npiv):
        """Helper method to get Connection Info for the Discovered Volume"""
        data = dict(access_mode='rw', qos_spec=None, target_discovered=False,
                    target_lun=target_lun, target_wwn=target_wwn)
        connect_info = dict(driver_volume_type='fibre_channel', data=data)
        #If this is NPIV, we want to set the connection type as such
        if npiv is True:
            connect_info['volume_connector'] = {
                'connection-type': 'npiv', 'connector': None}
        return connect_info

    @staticmethod
    def _parse_volume_size(size_bytes):
        """Helper Method to convert bytes to GB"""
        size = float(size_bytes) / 1073741824
        #round up to nearest GB
        size = int(math.ceil(size))
        return size

    @staticmethod
    def _map_volume_status(statusstr):
        """Helper Method to Map the SVC Status to Openstack Statuses"""
        #Currently anything other than online would be considered error
        return 'available' if statusstr == 'online' else 'error'

    def _svc_cmd_to_map(self, cmd, delim, key1, key2):
        ret = {}

        out, err = self._run_ssh(cmd)
        self._assert_ssh_return(out is not None,
                                '_svc_cmd_to_map',
                                cmd, out, err)
        list_lines = out.strip().split('\n')
        table_headers = list_lines.pop(0).split(delim)
        for line in list_lines:
            line = line.split(delim)
            row = dict(zip(table_headers, line))
            if not row[key1] in ret:
                ret[row[key1]] = {}
            ret[row[key1]][row[key2]] = row

        return ret

    def _get_wwpns_for_hosts(self, host_ids, host_names, host_wwpns):
        host_id = ''
        ssh_cmd = list()
        for host_id in host_ids:
            ssh_cmd.extend([';', 'svcinfo', 'lshost', '-delim', '!', host_id])

        out, err = self._run_ssh(ssh_cmd[1:])
        self._assert_ssh_return(len(out.strip()),
                                '_get_wwpns_for_host',
                                ssh_cmd, out, err)

        for attr_line in out.split('\n'):
            # If '!' not found, return the string and two empty strings
            attr_name, foo, attr_val = attr_line.partition('!')
            if attr_name == 'id':
                host_id = attr_val
                host_wwpns[host_id] = list()
            if attr_name == 'name':
                host_names[host_id] = attr_val
            if attr_name == 'WWPN':
                host_wwpns[host_id].append(attr_val)

    def _get_vdisk_to_wwpn_map(self):
        """Via a call to lshostviskmap and repeated calls to lshost, produces
           a map from vdisk ID to a list of WWPNs"""
        scsi_ids = dict()
        rmt_wwpns, connect_info = (dict(), dict())
        #Build a Map of the Output for the each Virtual Disk
        vdisk_map = self._svc_cmd_to_map(['svcinfo', 'lshostvdiskmap',
                                          '-delim', '!'],
                                         '!', 'vdisk_id', 'id')
        #Build a Map of the Local WWPN's for each of the Hosts
        lclhost_wwns = self._svc_cmd_to_map(['svcinfo', 'lsfabric', '-delim',
                                             '!'], '!', 'name', 'local_wwpn')
        #Build a Map of the Remote WWPN's for each of the Hosts
        host_ids = list()
        host_names = dict()
        rmthost_wwns = dict()
        for vdisk_id in vdisk_map.keys():
            for host_id in vdisk_map[vdisk_id].keys():
                #We only want to do anything if we haven't processed this Host
                if host_id not in host_ids and host_id not in rmthost_wwns:
                    host_ids.append(host_id)
                    #For Performance reasons group multiple Hosts in one call
                    if len(host_ids) >= 20:
                        self._get_wwpns_for_hosts(
                            host_ids, host_names, rmthost_wwns)
                        host_ids = list()
        #If there were any Hosts left, make one final call to process those
        if len(host_ids) > 0:
            self._get_wwpns_for_hosts(host_ids, host_names, rmthost_wwns)
        #Loop through the Virtual Disks a second time to build the return maps
        for vdisk_id in vdisk_map.keys():
            scsi_ids[vdisk_id] = '-1'
            rmt_wwpns[vdisk_id] = list()
            connect_info[vdisk_id] = dict()
            #Update Remote and Local WWPN's for each Virtual Disk Identifier
            for host_id in vdisk_map[vdisk_id].keys():
                host_name = host_names.get(host_id, '')
                rmt_wwpns[vdisk_id].extend(rmthost_wwns.get(host_id, []))
                #Add the Local WWPN's to the list for the given Virtual Disk
                connect_info[vdisk_id][host_id] = dict()
                connect_info[vdisk_id][host_id]['source_wwn'] =\
                    rmthost_wwns.get(host_id, [])
                connect_info[vdisk_id][host_id]['target_wwn'] =\
                    lclhost_wwns.get(host_name, {}).keys()
                #Add the SCSI Identifier for the given Virtual Disk Identifier
                connect_info[vdisk_id][host_id]['target_lun'] =\
                    vdisk_map[vdisk_id][host_id]['SCSI_id']

        return rmt_wwpns, connect_info

    def initialize_connection(self, volume, connector):
        """
        Calls the parent class to mask the volume on the storage controller,
        and here performs additional processing to work out which zones should
        be created on the switches.

        For NPIV, the virtual fibre channel ports will not yet be logged in,
        but we need to know which fabrics which ports will appear on, so that
        we know which fabrics to create the zones on.  For this reason, the
        connector must also include a data structure that maps physical WWPNs
        (which will be logged in) to the virtual WWPNs that they will provide.
        To support live partition mobility, we expect each physical WWPN to be
        providing two virtual WWPNs.

        The expected structure of a fibre channel connector is:

        {
            'host': hostname,
            'wwpns': [ list of virtual WWPNs ]  <-- this is used for masking
            'phy_to_virt_initiators': {phy_wwpn_X: [virt_wwpn_a, virt_wwpn_b],
                                      phy_wwpn_Y: [virt_wwpn_c, virt_wwpn_d]
                                        }
        }

        The expected structure of an iSCSI connector is:

        {
          'host': hostname,
          'initiator': initiator  <-- IQN format
        }
        """

        # Ensure that the passed-in data structure is correct.
        expected_fc_keys = set(['host', 'wwpns'])
        expected_iscsi_keys = set(['host', 'initiator'])
        if not (expected_fc_keys.issubset(connector) |
                expected_iscsi_keys.issubset(connector)):
            err_msg = (_('The connector %(connector)s does not contain the '
                         'required keys, which are %(expected_fc_keys)s.'
                         'or %(expected_iscsi_keys)s') %
                       {'connector': connector,
                        'expected_fc_keys': expected_fc_keys,
                        'expected_iscsi_keys': expected_iscsi_keys})
            LOG.error(err_msg)
            raise exception.VolumeBackendAPIException(data=err_msg)

        # Perform the masking on the storage controller
        s = super(StorwizeSVCProductDriver, self)
        info = s.initialize_connection(volume, connector)

        if 'phy_to_virt_initiators' in connector:
            try:
                fabric_initiator_target_map = \
                    self._do_zoning(volume,
                                    connector['host'],
                                    connector['phy_to_virt_initiators'],
                                    )
                # we have disabled zonemanager in cinder volume manager.
                # cinder's zonemanager will not be triggered. Just to
                # be safe, don't add the initiator_target_map to the
                # info['data'].

            except Exception as e:
                # Something went wrong during zoning, make sure that the disk
                # is unmapped and any host that we created is deleted before we
                # return
                with excutils.save_and_reraise_exception():
                    s.terminate_connection(volume, connector)
        return info

    def _do_zoning(self, volume, host, phy_to_virt_initiators):
        # Extract the map of physical-to-virtual WWPNs, sanitising to all
        # lowercase with no colons, and also build a list of physical WWPNs.
        phy_to_virt_map = {}
        virt_initiators = []
        for phy, virt in phy_to_virt_initiators.items():
            phy_to_virt_map[strip_colons(phy)] = map(strip_colons, virt)
            virt_initiators.extend(virt)
        phy_initiators = phy_to_virt_map.keys()

        # Identify the IO Group associated with this volume
        vdisk_id = self._incorporate_restricted_metadata(volume)
        volume_attributes = self._get_vdisk_attributes(vdisk_id)
        iogrp = volume_attributes['IO_group_id']

        # Build lists of:
        #  all the target wwpns in this iogrp, and all nodes in
        # this iogrp.
        target_wwpns = []
        target_nodes = []
        for node_id, node in self._storage_nodes.items():
            if node['IO_group'] == iogrp:
                LOG.info(_('Incorporating WWPNS for Node %(node_id)s: '
                           '%(wwpns)s') %
                         {'node_id': node_id, 'wwpns': node['WWPN']})
                target_nodes.append(node)
                target_wwpns.extend(node['WWPN'])

        # Return immediately unless we are doing fabric zoning
        if self.configuration.zoning_mode != 'fabric':
            # We emit useful information to the log file and send a
            # notification in case the user wants to perform some zoning later
            # on - they can write scripts to look for these and perform the
            # appropriate zoning.
            LOG.info(_("Attachment for host '%(host)s' to %(storage)s for "
                       "volume %(volume)s expects zoning between initiator "
                       "WWPNs %(initiators)s and target WWPNs %(targets)s") %
                     {'host': host,
                      'storage': self.endpoint_desc,
                      'volume': volume['id'],
                      'initiators': ', '.join(virt_initiators),
                      'targets': ", ".join(target_wwpns)}
                     )
            message = {'host': host,
                       'storage': self.configuration.san_ip,
                       'volume': volume['display_name'],
                       'vdisk_id': vdisk_id,
                       'targets': target_wwpns,
                       'phy_to_virt_initiators': phy_to_virt_initiators
                       }
            anotifier = rpc.get_notifier('volume', self.host)
            anotifier.info(context.get_admin_context(), 'volume.zone', message)
            return None

        zonemanager = PowerVCZoneManager(self.configuration)

        mapping = self._get_fabric_mapping(zonemanager, phy_initiators,
                                           target_wwpns)

        # We use this Fabric object to build up a list of all the zones that
        # we want to create.  It knows about the initiators, storage controller
        # nodes and the chosen WWPN on each node.
        class Fabric:
            def __init__(self, name, phy_initiator_wwpns, phy_to_virt_map):
                """
                Pass in a list of all physical initiator WWPNs, and a
                phy_to_virt_map that looks like:

                {
                  phy_wwpn_X: [ virt_wwpn_a, virt_wwpn_b ],
                  phy_wwpn_Y: [ virt_wwpn_c, virt_wwpn_d ]
                }

                No target node information is passed in here, we call
                add_node_wwpn() for every node that we want to use.
                """
                self.name = name
                self._phy_initiator_wwpns = phy_initiator_wwpns
                self._phy_to_virt_map = phy_to_virt_map
                self._nodes = []
                self._zones = {}

            def add_node_wwpn(self, target_wwpn):
                """
                For each target node, we have chosen a WWPN to which we
                want to connect.  We should call this once for each target node
                on the fabric.
                """
                self._nodes.append(target_wwpn)

            def zone_initiator_to_node(self, phy_initiator_index, node_index):
                """
                Adds a zone from each virtual wwpn associated with the
                specified physical wwpn to the chosen target WWPN on the
                specified node.
                """
                LOG.info(_("Mapping initiator %(phy)s to node %(node)s")
                         % {'phy': phy_initiator_index,
                            'node': node_index})

                phy_initiator_wwpn = \
                    self._phy_initiator_wwpns[phy_initiator_index]
                for virt_wwpn in self._phy_to_virt_map[phy_initiator_wwpn]:
                    if virt_wwpn not in self._zones:
                        self._zones[virt_wwpn] = []
                    self._zones[virt_wwpn].append(self._nodes[node_index])

            def initiator_count(self):
                return len(self._phy_initiator_wwpns)

            def node_count(self):
                return len(self._nodes)

            def zones(self):
                return self._zones

        fabrics = []

        # We iterate through every fabric that we got from the WWPN lookup.
        for name, wwpns in mapping.items():
            # We only care about fabrics that can see at least one initiator
            # WWPN and one target WWPN.
            if (wwpns['target_port_wwn_list'] and
                    wwpns['initiator_port_wwn_list']):
                # Create a Fabric object to represent this fabric.  We use that
                # object to build up our list of zones to be created.
                fabric = Fabric(name, wwpns['initiator_port_wwn_list'],
                                phy_to_virt_map)
                fabrics.append(fabric)

                # Build a set of all target WWPNs visible on this fabric.
                found_target_set = set(wwpns['target_port_wwn_list'])

                # For each of the nodes that we are interested in, ensure that
                # we found at least one WWPN that belongs to that node.
                for node in target_nodes:
                    formatted_wwpns = [strip_colons(x) for x in node['WWPN']]
                    found_node_ports = list(found_target_set &
                                            set(formatted_wwpns))

                    if not found_node_ports:
                        msg = (_('Fabric %(fabric)s does not have visibility '
                                 'to any WWPNs in node %(node)s, part of '
                                 'iogrp %(iogrp)s of storage controller '
                                 '%(name)s. WWPNs visible on the fabric are '
                                 '%(visible)s. WWPNs on the controller are '
                                 '%(available)s.')
                               % {'fabric': name,
                                  'node': node['id'],
                                  'iogrp': iogrp,
                                  'name': self.configuration.host,
                                  'visible': ';'.join(found_target_set),
                                  'available': ';'.join(formatted_wwpns)}
                               )
                        LOG.error(msg)
                        raise exception.VolumeBackendAPIException(data=msg)

                    # We have a list of logged-in target ports on this fabric,
                    # for this node, and we want to select one to use.  When
                    # multiple ports are available, we don't want to select the
                    # same one each time, so we hash the hostname and index
                    # into a list of sorted node ports.
                    #
                    # We are building up a list of WWPNs in the Fabric object,
                    # one per node.
                    sorted_ports = sorted(found_node_ports)
                    hash_index = hash(host) % len(sorted_ports)
                    fabric.add_node_wwpn(sorted_ports[hash_index])

        # When we get here we have a fabrics[] array of Fabric objects, with
        # each one configured with the subset of physical initiator ports
        # visible on that fabric, and for each node in the volume's iogrp, a
        # chosen WWPN to which we want to connect.

        # If we don't find a supported pattern, we revert to zoning to a
        # default configuration which is not best practice, but is reasonably
        # sensible and will work.
        create_default_zones = False

        # Now we match against patterns of best practice.  We expect two
        # storage controller nodes to be visible on each fabric.
        # We support model with 1 and 2 fabrics, and with 1 or 2 initiators
        # on both fabrics.
        if len(fabrics) == 1 and fabrics[0].node_count() == 2:
            # Single fabric cases
            if fabrics[0].initiator_count() == 1:
                LOG.info(_('Zoning for single fabric, one initiator.'))
                # One fabric, one initiator;
                # zone the initiator to both targets.
                #
                # F0   I0 --+-------------> T0
                #            \
                #             +-----------> T1
                fabrics[0].zone_initiator_to_node(0, 0)
                fabrics[0].zone_initiator_to_node(0, 1)
            elif fabrics[0].initiator_count() == 2:
                LOG.info(_('Zoning for single fabric, two initiators.'))
                # One fabric, two initiators;
                # zone both initiators to both targets.
                #
                #      I0 --+---------+---> T0
                #            \       /
                # F0          +---------+-> T1
                #                  /   /
                #      I1 --------+---+
                fabrics[0].zone_initiator_to_node(0, 0)
                fabrics[0].zone_initiator_to_node(0, 1)
                fabrics[0].zone_initiator_to_node(1, 0)
                fabrics[0].zone_initiator_to_node(1, 1)
            else:
                LOG.info(_('Zoning for single fabric, general case due to '
                           '%(count)s initiators on fabric.') %
                         {'count': fabrics[0].initiator_count()})
                create_default_zones = True
        elif (len(fabrics) == 2 and
              fabrics[0].node_count() == 2 and
              fabrics[1].node_count() == 2):
            # Dual fabric cases
            if (fabrics[0].initiator_count() == 1 and
                    fabrics[1].initiator_count() == 1):
                LOG.info(_('Zoning for dual fabric, one initiator per '
                           'fabric.'))
                # Two fabrics, one initiator per fabric;
                # zone each initiator to both targets
                #
                # F0   I0 --+-------------> T0
                #            \
                #             +-----------> T1
                #
                #
                # F1   I0 --+-------------> T0
                #            \
                #             +-----------> T1
                fabrics[0].zone_initiator_to_node(0, 0)
                fabrics[0].zone_initiator_to_node(0, 1)
                fabrics[1].zone_initiator_to_node(0, 0)
                fabrics[1].zone_initiator_to_node(0, 1)
            elif (fabrics[0].initiator_count() == 2 and
                  fabrics[1].initiator_count() == 2):
                LOG.info(_('Zoning for dual fabric, two initiators per '
                           'fabric.'))
                # Two fabrics, two initiators per fabric;
                # Zone each initiator to one node, ensuring
                # that each fabric has connectivity to
                # both nodes.
                #
                #      I0 ----------------> T0
                # F0
                #      I1 ----------------> T1
                #
                #
                #      I0 ----------------> T0
                # F1
                #      I1 ----------------> T1
                fabrics[0].zone_initiator_to_node(0, 0)
                fabrics[0].zone_initiator_to_node(1, 1)
                fabrics[1].zone_initiator_to_node(0, 0)
                fabrics[1].zone_initiator_to_node(1, 1)
            else:
                LOG.info(_('Zoning for dual fabric, general case due to '
                           '%(count1)s initiators on first fabric and '
                           '%(count2)s initiators on second fabric.') %
                         {'count1': fabrics[0].initiator_count(),
                          'count2': fabrics[1].initiator_count()})

                create_default_zones = True
        elif len(fabrics) == 0:
            raise paxes_exception.SVCNoZonesException(self.endpoint_desc)
        else:
            LOG.info(_('Zoning for general case due to %(count)s fabrics.')
                     % {'count': len(fabrics)})
            create_default_zones = True

        if create_default_zones:
            # This isn't a configuration that we explicitly support.  We map
            # all initiators on all fabrics to both nodes.
            for fabric in fabrics:
                for i in range(fabric.initiator_count()):
                    for n in range(fabric.node_count()):
                        fabric.zone_initiator_to_node(i, n)

        # Merge the zone list across all fabrics.
        fabric_initiator_target_map = {}
        for fabric in fabrics:
            fabric_initiator_target_map[fabric.name] = fabric.zones()

        LOG.info(_("Creating zones: %r") % fabric_initiator_target_map)
        zonemanager.add_connection(host,
                                   fabric_initiator_target_map)

        zonemanager.close()
        return fabric_initiator_target_map

    # Given a list of physical initiator wwpns, and a list of target wwpns,
    # asks our registered SAN lookup service to tell is which of those
    # wwpns are visible on which fabrics.
    def _get_fabric_mapping(self, zone_manager, phy_initiator_wwpns,
                            target_wwpns):
        LOG.info(_('Requested mapping for initiators  %(initiators)s'
                   ' and targets %(targets)s')
                 % {'initiators': phy_initiator_wwpns,
                    'targets': target_wwpns})

        # The brocade code only works if we add colons to the incoming WWPNs.
        initiator_colons = map(add_colons, phy_initiator_wwpns)
        target_colons = map(add_colons, target_wwpns)

        # Produce a mapping that shows which of the specified initiator and
        # target wwpns are logged into which switches.
        #               'a': [...]}
        #               'b': [...]}
        wwpns = {'initiator_port_wwn_list':  initiator_colons,
                 'target_port_wwn_list': target_colons}

        mapping = zone_manager.get_san_context(wwpns)

        LOG.info(_("Returned mapping is %(mapping)s")
                 % {'mapping': mapping})

        # Remove any colons that might be in the returned structure
        for fabric_name, wwpn_lists in mapping.iteritems():
            for name, wwpns in wwpn_lists.iteritems():
                wwpn_lists[name] = \
                    map(strip_colons, wwpn_lists[name])

        LOG.info(_("Returned mapping is %(mapping)s")
                 % {'mapping': mapping})

        return mapping

    def _get_conn_fc_wwpns(self, host_name):
        """
        We override this method because for NPIV the virtual ports are not yet
        logged in, so we don't expect our host to have any connectivity to the
        storage controller.  We call the parent, and if we get nothing back,
        we just return all WWPNs.  It doesn't matter, because for NPIV
        we don't do anything with this connection info anyway - the disk will
        just appear to the client LPAR without us having to perform any
        special detection.
        """
        s = super(StorwizeSVCProductDriver, self)
        wwpns = s._get_conn_fc_wwpns(host_name)

        # If no WWPNs returned, build a list of all WWPNs.
        if not wwpns:
            for node_id, node in self._storage_nodes.items():
                wwpns.extend(node['WWPN'])

        return wwpns

    def terminate_connection(self, volume, connector, **kwargs):
        LOG.info(_("Terminating connection with parameters %(connector)s" %
                   {'connector': connector}))

        # Perform the masking on the storage controller
        s = super(StorwizeSVCProductDriver, self)
        s.terminate_connection(volume, connector, **kwargs)

        # Test to see if we should remove zones on the fabrics
        if connector.get('clean_zones', None) == "all" and \
           self.configuration.zoning_mode == 'fabric':
            LOG.info(_("Removing zones for initiators: %(initiator_list)s") %
                     {'initiator_list': ', '.join(connector['wwpns'])})
            # Create a zonemanager and ask it to remove zones for these
            # initiators
            try:
                zonemanager = PowerVCZoneManager(self.configuration)
                zonemanager.delete_connection(map(add_colons,
                                                  connector['wwpns']))
            except Exception as ex:
                LOG.exception(ex)
                LOG.error(_("There was a failure when the zone manager "
                            "attempted to remove zones created for WWPNs "
                            "%(wwpns)s during detach of volume %(vol)s.") %
                          (connector['wwpns'], volume['id']))

    def _run_ssh(self, *args, **kwargs):
        """
        Wrapper for SSH command execution, captures a specific case where we
        can't establish a connection due to an overloaded SVC.
        """
        s = super(StorwizeSVCProductDriver, self)
        try:
            return s._run_ssh(*args, **kwargs)
        except paramiko.SSHException as e:
            if "Error reading SSH protocol banner" in e.msg:
                raise paxes_exception.SVCConnectionException(
                    self.endpoint_desc)
            else:
                raise

    def extend_volume(self, volume, new_size):
        """
        I version of extend_volume which will not be blocked by
        the volume flashcopy. It will raise exception and return
        immediately and indicate there is an in-flight flashcopy.
        So the caller, which is nova resize function doesn't have
        to poll the volume state. The caller should call back extend
        volume again.
        """
        LOG.debug(_('enter: extend_volume: volume %s') % volume['id'])
        vdisk_id = self._incorporate_restricted_metadata(volume)
        volume_attribute = self._get_vdisk_attributes(vdisk_id)
        if not volume_attribute:
            # the vdisk has been deleted out-of-band.
            raise paxes_exception.SVCVdiskNotFoundException(
                self.endpoint_desc, volume['id'], vdisk_id=vdisk_id)

        # Ensure that the UID matches and we don't extend the wrong disk,
        # raise exception if the UID doesn't match.
        self._verify_uid(volume_attribute, volume)

        extend_amt = int(new_size) - volume['size']
        ssh_cmd = (['svctask', 'expandvdisksize', '-size', str(extend_amt),
                    '-unit', 'gb', vdisk_id])
        out, err = self._run_ssh(ssh_cmd, check_exit_code=False)

        if 'CMMVC5837E' in err:
            # The action failed because the virtual disk (VDisk)
            # is part of a FlashCopy mapping.
            raise paxes_exception.PVCExpendvdiskFCMapException()
        else:
            # No output and stderr should be returned from expandvdisksize
            self._assert_ssh_return(len(out.strip()) + len(err.strip()) == 0,
                                    'extend_volume', ssh_cmd, out, err)

        LOG.debug(_('leave: extend_volume: volume %s') % volume['id'])

    def check_volume_health(self, volume):
        """
        Throws exceptions if something is wrong with the passed-in volume.

        Checks for existence of the underlying vdisk
        """
        vdisk_id = self._incorporate_restricted_metadata(volume)

        if not self._check_vdisk_exists(vdisk_id):
            raise paxes_exception.SVCVdiskNotFoundException(
                self.endpoint_desc, volume['id'], vdisk_id=vdisk_id)

    def _update_volume_stats(self):
        """Retrieve stats info from volume group."""
        # First perform some checks on driver health
        self.log_driver_status()

        # Then call the parent to collect the stats
        super(StorwizeSVCProductDriver, self)._update_volume_stats()

    def log_driver_status(self):
        """
        Logs internal state of the driver if something looks interesting.
        """

        # If we have waiting connections, or there are in-flight commands,
        # then we display the number of free connections, the number of
        # requests for connections, and the duration and parameters for all
        # currently oustanding SSH commands.
        if self.sshpool.waiting() or self.pending_ssh:
            LOG.info(_("SSH Pool: %d free, %d waiting, in-flight commands:") %
                     (self.sshpool.free(), self.sshpool.waiting()))
            for ssh_id, info in self.pending_ssh.iteritems():
                duration = time.time() - info['time']
                LOG.info(_(" %(duration).2f %(commands)s")
                         % {'duration': duration,
                            'commands': info['command']})

    def _ensure_vdisk_no_fc_mappings(self, vdisk_id, allow_snaps=True):
        """ Override storwize_svc base driver's blocking timer threads.
        Due to the nature of storwize_svc flashcopy, all the vdisk delete
        has to wait for either fcmap in the proper state to be removed or
        there is no fcmap. The base driver's implementation is using
        timer thread per vdisk delete, which may schedule too many
        greenthread under cloud usecase. The idea here is to create a single
        fcmap processing queue and each _delete_vdisk operation will be
        blocked on the specific fcmap wait event until the associated
        fcmap is processed(removed or none)."""

        if not CONF.storwize_fcmap_delete_queue_enabled:
            s = super(StorwizeSVCProductDriver, self)
            s._ensure_vdisk_no_fc_mappings(vdisk_id, allow_snaps=allow_snaps)
            return

        fc_mappings = self._get_vdisk_fc_mappings(vdisk_id)
        # No flashcopy mappings, it if safe to delete the vdisk
        if not fc_mappings:
            return True
        # If the vdisk fcmap has zero dependent mappings, it is handled
        # immediately without going through the normal fcmapping handler
        # per periodic task. Based on the Storwize specificaton, the
        # flashcopy mappings are orgnized by link list. All the new
        # flashcopy mappings will be added to the head of the list. That
        # means the oldest flashcopy mappings from the same clone source
        # will have the least dependencies. If a flashcopy mapping for a
        # vdisk clone has zero dependency, it is safe to be stopped and
        # removed without breaking other in-flight flashcopy mappings.
        if len(fc_mappings) == 1:
            fcmap_attr = self._get_flashcopy_mapping_attributes(fc_mappings[0])
            if int(fcmap_attr['dependent_mappings']) == 0:
                if fcmap_attr['status'] in ['copying', 'prepared']:
                    self._run_ssh(['svctask', 'stopfcmap', fc_mappings[0]])
                self._run_ssh(['svctask', 'rmfcmap', '-force', fc_mappings[0]])
                return True

        waiter = FcmapWaiter(vdisk_id)

        def get_attr_depmap(fcmap_id):
            attr = self._get_flashcopy_mapping_attributes(fcmap_id)
            return int(attr['dependent_mappings'])

        # each vdisk's fcmap waiter priority equals to the sum of each
        # dependent fcmap's dependent_mappings.
        pri = reduce(operator.add, map(get_attr_depmap, fc_mappings))

        waiter.update(fc_mappings, pri)
        # add the waiter to the fcmap delete queue.
        self.fcmap.append(waiter)
        LOG.info(_("vdisk %(vdsk)s has been added to the flashcopy mapping "
                   "delete queue with priority %(pri)s.") %
                 dict(vdsk=vdisk_id, pri=pri))

        try:
            # wait for the removal of flashcopy mapping.
            retval = waiter.wait()
            dur = time.time() - waiter.enqueue_tb
            msg = (_("Successfully returned from flashcopy mapping waiter for "
                     "vdisk %(vdsk)s, returned value: %(ret)s, total wait "
                     "time: %(wt)s seconds.") %
                   dict(vdsk=vdisk_id, ret=retval, wt=dur))
            LOG.info(msg)
            # The retval will be either true or false.
            # True means there is no more flashcopy associated with the vdisk
            # for delete operation. Caller can go ahead to delete the vdisk.
            # It may also mean the vdisk has no snapshot and can be extended
            # (if allow_snaps=False)
            # False is a special case for extend_valume to ensure the vdisk
            # that has snapshot cannot be deleted. The allow_snaps=False has to
            # be specified for this check.
            return retval
        except Exception as ex:
            with excutils.save_and_reraise_exception():
                dur = time.time() - waiter.enqueue_tb
                msg = (_("Exception happened when waiting for flashcopy "
                         "mapping handling for vdisk %(vdsk)s, total wait "
                         "time: %(wt)s seconds.") %
                       dict(vdsk=vdisk_id, wt=dur))
                LOG.error(msg)
        finally:
            msg = (_("Removed flashcopy mappings waiter from waiting queue for"
                     " vdisk %(vdsk)s deletion.") % dict(vdsk=vdisk_id))
            LOG.info(msg)
            self.fcmap.remove(waiter)

    def fcmapping_handler(self, fcmap_queue, poll_interval):
        """Timer thread that polls fcmap queue on a fixed interval. It
        processes all the pending flashcopy mapping in an optimized way to
        speed up flashcopy mapping deletion."""

        vdsks = map(lambda x: x.vdisk_id, fcmap_queue)
        LOG.debug(_("Flashcopy mapping delete queue: %(vdsks)s") %
                  dict(vdsks=vdsks))
        if not fcmap_queue:
            return

        current_tb = time.time()
        avg_wait = (current_tb -
                    sum(map(lambda x: x.enqueue_tb, fcmap_queue)) /
                    len(fcmap_queue))

        msg = (_("Flashcopy mapping delete queue: %(cnt)s vdisks "
                 "pending delete, average wait time: %(avg)s seconds") %
               dict(cnt=len(fcmap_queue), avg=avg_wait))
        LOG.info(msg)
        # Create a fcmap waiter list ordered by normalized
        # dependent_mappings priority. The priority here is not current.
        # But the normalized priority should alway decrease due to the
        # forward progress of flashcopy. The storwize/svc flashcopy
        # will always put the newest fcmap to the head of the map list,
        # which has the highest priority number(lowest priority). Process
        # the highest priority fcmap that has least dependency increases
        # the chance to remove the vdisk fcmap earlier.
        waiters = sorted(fcmap_queue, key=lambda x: x.priority)

        def _process_fcmap(waiter):
            vdisk_id = waiter.vdisk_id
            allow_snaps = waiter.allow_snaps
            attrs = None
            fcmap_removed = []

            fcmap_ids = self._get_vdisk_fc_mappings(vdisk_id)
            if not fcmap_ids:
                # All the dependent fcmappings have been handled.
                waiter.update([], 0)
                return

            pri = 0
            for map_id in fcmap_ids:

                attrs = self._get_flashcopy_mapping_attributes(map_id)
                source_id = attrs['source_vdisk_id']
                target_id = attrs['target_vdisk_id']
                copy_rate = attrs['copy_rate']
                status = attrs['status']
                pri += int(attrs['dependent_mappings'])
                map_descriptor = (_("%(map_id)s [vdisk %(src)s to vdisk "
                                    "%(tgt)s]")
                                  % {'map_id': map_id,
                                     'src': source_id,
                                     'tgt': target_id})
                if copy_rate == '0':
                    # Case #2: A vdisk that has snapshots
                    if source_id == vdisk_id:
                        if not allow_snaps:
                            # fcmap exists due to snapshot. Return False
                            # to waiter.
                            ex = paxes_exception.\
                                SVCExtendSnapshotSrcNotAllowed(
                                    vdisk_id=vdisk_id, fcmapid=map_id)
                            LOG.warn(_("fcmapping_handler: %s") % ex)
                            raise ex
                        new_copy_rate = '50'
                        LOG.info(_("fcmapping_handler: to delete vdisk "
                                   "%(vdisk_id)s, increasing "
                                   "copyrate of flashcopy mapping %(map)s "
                                   "from 0 to %(copyrate)s and waiting for "
                                   "completion.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_id,
                                    'copyrate': new_copy_rate
                                    })

                        ssh_cmd = ['svctask', 'chfcmap', '-copyrate',
                                   new_copy_rate, '-autodelete', 'on', map_id]

                        self._run_ssh(ssh_cmd)
                    # Case #3: A snapshot
                    else:
                        msg = (_('Vdisk %(id)s not involved in '
                                 'mapping %(src)s -> %(tgt)s') %
                               {'id': vdisk_id, 'src': source_id,
                                'tgt': target_id})
                        self._driver_assert(target_id == vdisk_id, msg)
                        if status in ['copying', 'prepared']:
                            self._run_ssh(['svctask', 'stopfcmap', map_id])
                            LOG.info(_("To allow deletion of vdisk "
                                       "%(vdisk_id)s, flashcopy mapping "
                                       "%(map)s with status "
                                       "'%(status)s' was removed.")
                                     % {'vdisk_id': vdisk_id,
                                        'map': map_descriptor,
                                        'status': status})
                        elif status in ['stopping', 'preparing']:
                            LOG.info(_("To allow deletion of vdisk "
                                       "%(vdisk_id)s, waiting for flashcopy "
                                       "mapping %(map)s with status "
                                       "'%(status)s' to complete.")
                                     % {'vdisk_id': vdisk_id,
                                        'map': map_descriptor,
                                        'status': status})
                        else:
                            self._run_ssh(['svctask', 'rmfcmap', '-force',
                                           map_id])
                            LOG.info(_("To allow deletion of vdisk "
                                       "%(vdisk_id)s, forcing removal of "
                                       "flashcopy mapping %(map)s with status "
                                       "'%(status)s'")
                                     % {'vdisk_id': vdisk_id,
                                        'map': map_descriptor,
                                        'status': status})
                            pri -= int(attrs['dependent_mappings'])
                            fcmap_removed.append(map_id)
                # Case 4: Copy in progress - wait and will autodelete
                else:
                    if status == 'prepared':
                        self._run_ssh(['svctask', 'stopfcmap', map_id])
                        self._run_ssh(['svctask', 'rmfcmap', '-force', map_id])
                        LOG.info(_("To allow deletion of vdisk %(vdisk_id)s, "
                                   "prepared flashcopy mapping %(map)s was "
                                   "removed.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor})
                        pri -= int(attrs['dependent_mappings'])
                        fcmap_removed.append(map_id)
                    elif status == 'idle_or_copied':
                        # Prepare failed
                        self._run_ssh(['svctask', 'rmfcmap', '-force', map_id])
                        LOG.info(_("To delete vdisk %(vdisk_id)s, flashcopy "
                                   "mapping %(map)s with status "
                                   "'idle_or_copied' was removed.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor})
                        pri -= int(attrs['dependent_mappings'])
                        fcmap_removed.append(map_id)
                    else:
                        LOG.info(_("To delete vdisk %(vdisk_id)s, waiting for "
                                   "completion of flashcopy mapping %(map)s, "
                                   "which is currently %(progress)s%% "
                                   "complete and has status '%(status)s'.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor,
                                    'progress': attrs['progress'],
                                    'status': status})
                        # process fcmap to speed up vdisk cleanup
                        wait_for_copy = self._prepare_fcmap_for_deletion(
                            map_id, attrs)
                        if not wait_for_copy:
                            pri -= int(attrs['dependent_mappings'])
                            fcmap_removed.append(map_id)

            for x in fcmap_removed:
                fcmap_ids.remove(x)
            waiter.update(fcmap_ids, pri)
            return
            # ---- END OF _process_fcmap()

        for x in waiters:
            try:
                _process_fcmap(x)
            except Exception as ex:
                if (isinstance(ex, processutils.ProcessExecutionError) and
                        'CMMVC5804E' in ex.stderr):
                    # If vdisk still exists, it means fcmap has been removed
                    # during processing, just increase the priority. Then the
                    # waiter will be handled earlier when timer pops again.
                    # otherwise, vdisk is missing, which is an error
                    # condition.
                    vdisk_defined = self._is_vdisk_defined(x.vdisk_id)
                    if vdisk_defined:
                        # fcmap has been removed, make the waiter's
                        # priority more favorate.
                        x.update(x.fcmap_ids, 0)
                        continue
                    else:
                        msg = (_("Exception happened during processing "
                                 "flashcopy mapping per vdisk %(vdsk)s "
                                 "deletion: %(err)s") %
                               dict(vdsk=x.vdisk_id, err=ex))
                        LOG.error(msg)
                        # ready to wake up waiter with exception.
                        x.update([], 0, exc=ex)

            if x.is_ready():
                if isinstance(x.exc,
                              paxes_exception.
                              SVCExtendSnapshotSrcNotAllowed):
                    # keep the driver's original behavior. Just tell the
                    # caller extend volume is not allowed with snapshot.
                    x.exc = None
                    x.done(ret=False)
                else:
                    # There is no fcmap for the vdisk. Ready for deletion
                    # or notify waiter there is an error occurred.
                    x.done()
            # make sure the timer is not outlasting the a tunable ratio of
            # fixed polling interval. Otherwise, the timer will consume too
            # much volume service ticks. Since the queue will be sorted every
            # time with the most favorate vdisk upfront, it is effective
            # to process the front portion of the queue only.
            lasted_time = time.time() - current_tb
            poll_ratio = CONF.storwize_fcmap_poll_maxpct * 1.0 / 100
            if lasted_time >= poll_ratio * poll_interval:
                break
        runtime = time.time() - current_tb
        LOG.info(_("Duration of fcmapping_handler timer: %(runtime)s seconds,"
                   " %(pct)s%% of fixed polling interval.") %
                 dict(runtime=runtime, pct=(runtime / poll_interval * 100)))


def add_colons(wwpn):
    return ':'.join([wwpn[i:i + 2] for i in range(0, len(wwpn), 2)]).lower()


def strip_colons(wwpn):
    wwpn = wwpn.lower()
    if len(wwpn) > 16:
        return wwpn.replace(":", "")
    else:
        return wwpn


class FcmapWaiter(object):
    """ A flashcopy mapping event waiter. It will be blocked on the
    eventlet event created during vdisk delete operation.The fcmap waiter
    will be queued to the fcmap delete queue and will be polled by the
    fcmap polling timer every 30 seconds(configurable). Once the fcmap
    is removed for a given vdisk, the notification will be sent from the
    timer to wake up the vdisk delete thread that is blocked. deque, which
    holds the fcmap waiter, is thread safe. Once the waiter is created by
    the vdisk delete thread and enqueued, the content of the waiter will only
    be updated by the fcmap timer thread and each vdisk delete thread has
    its own waiter. This machanism makes it lock free. """
    def __init__(self, vdisk_id, allow_snaps=True):
        self.vdisk_id = vdisk_id
        self.priority = 0
        self.fcmap_ids = []
        self.exc = None
        self.event = Event()
        self.enqueue_tb = time.time()
        self.allow_snaps = allow_snaps

    def update(self, fcmap_ids, pri, exc=None):
        """ function to update the fcmap waiter properties. It is called
        by both fcmap handler timer and vdisk delete thread(not concurrently).
        """
        self.fcmap_ids = fcmap_ids
        self.priority = pri
        self.exc = exc

    def wait(self):
        """ function called by vdisk delete thread to wait during
        flashcopy mapping processing"""
        return self.event.wait()

    def is_ready(self):
        """ helper function called by fcmap handler timer thread. It makes
        sure the fcmap for a given vdisk delete operation is done."""
        return True if len(self.fcmap_ids) == 0 else False

    def done(self, ret=True):
        """function called by fcmap handler timer thread only. It wakes up
        the vdisk delete thread that is waiting for the fcmap processing."""
        if self.exc:
            self.event.send_exception(self.exc)
        else:
            self.event.send(ret)
