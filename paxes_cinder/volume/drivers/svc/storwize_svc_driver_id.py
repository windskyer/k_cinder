# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
# Copyright 2012 OpenStack LLC.
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

"""
Volume driver for IBM Storwize family and SVC storage systems.

Notes:
1. If you specify both a password and a key file, this driver will use the
   key file only.
2. When using a key file for authentication, it is up to the user or
   system administrator to store the private key in a safe manner.
3. The defaults for creating volumes are "-rsize 2% -autoexpand
   -grainsize 256 -warning 0".  These can be changed in the configuration
   file or by using volume types(recommended only for advanced users).

Limitations:
1. The driver expects CLI output in English, error messages may be in a
   localized format.
2. Clones and creating volumes from snapshots, where the source and target
   are of different sizes, is not supported.

"""

import eventlet
import random
import re
import string
import time

from oslo.config import cfg

from cinder import context
from cinder import db as db_api
from cinder import exception
from cinder.openstack.common import excutils
from cinder.openstack.common import log as logging
from paxes_cinder import _
from cinder.openstack.common import processutils
from cinder.openstack.common import loopingcall
from cinder.openstack.common import strutils
from cinder.openstack.common.db import exception as db_exc
from cinder import utils
from cinder.volume import volume_types

from paxes_cinder.db import api as paxes_db_api
from paxes_cinder.volume.drivers import paxes_san
from paxes_cinder import exception as paxes_exception

LOG = logging.getLogger(__name__)

RESTRICTED_METADATA_VDISK_ID_KEY = "vdisk_id"
RESTRICTED_METADATA_VDISK_NAME_KEY = "vdisk_name"
RESTRICTED_METADATA_VDISK_UID_KEY = "vdisk_uid"
RESTRICTED_METADATA_SCSI_INQUIRY_83_KEY = "scsi_inquiry_83"

# Regex to match WWPN!C0507606D56F01F2 from lshost
RE_WWPN = re.compile('WWPN!([A-Z]*[0-9]+[A-Z0-9]*)')

# Regex to match iscsi_name!iqn
RE_ISCSI_NAME = re.compile('iscsi_name!(.)')

#constant for flashcopy mapping processing
FCMAP_COPY_COMPLETE_PCT = 100

storwize_svc_opts = [
    cfg.StrOpt('storwize_svc_volpool_name',
               default='volpool',
               help='Storage system storage pool for volumes'),
    cfg.IntOpt('storwize_svc_vol_rsize',
               default=2,
               help='Storage system space-efficiency parameter for volumes '
                    '(percentage)'),
    cfg.IntOpt('storwize_svc_vol_warning',
               default=0,
               help='Storage system threshold for volume capacity warnings '
                    '(percentage)'),
    cfg.BoolOpt('storwize_svc_vol_autoexpand',
                default=True,
                help='Storage system autoexpand parameter for volumes '
                     '(True/False)'),
    cfg.IntOpt('storwize_svc_vol_grainsize',
               default=256,
               help='Storage system grain size parameter for volumes '
                    '(32/64/128/256)'),
    cfg.BoolOpt('storwize_svc_vol_compression',
                default=False,
                help='Storage system compression option for volumes'),
    cfg.BoolOpt('storwize_svc_vol_easytier',
                default=True,
                help='Enable Easy Tier for volumes'),
    cfg.IntOpt('storwize_svc_vol_iogrp',
               default=0,
               help='The I/O group in which to allocate volumes'),
    cfg.IntOpt('storwize_svc_flashcopy_timeout',
               default=120,
               help='Maximum number of seconds to wait for FlashCopy to be '
                    'prepared. Maximum value is 600 seconds (10 minutes)'),
    cfg.StrOpt('storwize_svc_connection_protocol',
               default='iSCSI',
               help='Connection protocol (iSCSI/FC)'),
    cfg.BoolOpt('storwize_svc_multipath_enabled',
                default=False,
                help='Connect with multipath (FC only; iSCSI multipath is '
                     'controlled by Nova)'),
    cfg.BoolOpt('storwize_svc_multihostmap_enabled',
                default=True,
                help='Allows vdisk to multi host mapping'),
    cfg.IntOpt('storwize_fcmap_poll_interval',
               default=30,
               help='A tunable determines how frequent Storwize driver should '
                    'poll the status of in-flight flashcopy monitor queue. '
                    'The poll interval is in seconds'),
    cfg.IntOpt('storwize_fcmap_poll_maxpct',
               default=80,
               help='A tunable determines the percentage of poll interval '
                    'a worker thread should spend at most when walking the '
                    'flashcopy monitor queue.'),
    cfg.BoolOpt('storwize_fcmap_delete_queue_enabled',
                default=True,
                help='Enable storwize driver flashcopy mapping queue to '
                     'have a single worker thread to manage the flashcopy '
                     'mapping per SVC backend and wakes up each pending '
                     'volume delete threads as needed. When it is disabled, '
                     'each volume delete request needs to poll the disk fcmap '
                     'individually.'),
    cfg.StrOpt('storwize_fcmap_delete_copy_clean_rate',
               default='50',
               help='A tunable to decide copy/clean rate used during fcmap'
                    'delete operation.')
]


CONF = cfg.CONF
CONF.register_opts(storwize_svc_opts)


class StorwizeSVCDriverIdDriver(paxes_san.PowerVCSanDriver):
    """IBM Storwize V7000 and SVC iSCSI/FC volume driver.

    Version history:
    1.0 - Initial driver
    1.1 - FC support, create_cloned_volume, volume type support,
          get_volume_stats, minor bug fixes

    """

    """====================================================================="""
    """ SETUP                                                               """
    """====================================================================="""
    VERSION = "1.1.0"

    def __init__(self, *args, **kwargs):
        super(StorwizeSVCDriverIdDriver, self).__init__(*args, **kwargs)
        self.configuration.append_config_values(storwize_svc_opts)
        self._storage_nodes = {}
        self._enabled_protocols = set()
        self._compression_enabled = False
        self._available_iogrps = []
        self._context = None
        self._system_name = None
        self._system_id = None
        self._extent_size = None

        # This describes the storage controller, handy for attaching to
        # exceptions or mentioning in log messages.
        self.endpoint_desc = paxes_exception.SVCDescriptor(
            self.configuration.host,
            self.configuration.host_display_name,
            self.configuration.san_login,
            self.configuration.san_ip,
            self.configuration.san_ssh_port)

        # Build cleanup translation tables for host names
        invalid_ch_in_host = ''
        for num in range(0, 128):
            ch = str(chr(num))
            if (not ch.isalnum() and ch != ' ' and ch != '.'
                    and ch != '-' and ch != '_'):
                invalid_ch_in_host = invalid_ch_in_host + ch
        self._string_host_name_filter = string.maketrans(
            invalid_ch_in_host, '-' * len(invalid_ch_in_host))

        self._unicode_host_name_filter = dict((ord(unicode(char)), u'-')
                                              for char in invalid_ch_in_host)

    def _get_iscsi_ip_addrs(self):
        generator = self._port_conf_generator(['svcinfo', 'lsportip'])
        header = next(generator, None)
        if not header:
            return

        for port_data in generator:
            try:
                port_node_id = port_data['node_id']
                port_ipv4 = port_data['IP_address']
                port_ipv6 = port_data['IP_address_6']
                state = port_data['state']
            except KeyError:
                self._handle_keyerror('lsportip', header)

            if port_node_id in self._storage_nodes and (
                    state == 'configured' or state == 'online'):
                node = self._storage_nodes[port_node_id]
                if len(port_ipv4):
                    node['ipv4'].append(port_ipv4)
                if len(port_ipv6):
                    node['ipv6'].append(port_ipv6)

    def _get_fc_wwpns(self):
        for key in self._storage_nodes:
            node = self._storage_nodes[key]
            ssh_cmd = ['svcinfo', 'lsnode', '-delim', '!', node['id']]
            raw = self._run_ssh(ssh_cmd)
            resp = CLIResponse(raw, delim='!', with_header=False)
            wwpns = set(node['WWPN'])
            for i, s in resp.select('port_id', 'port_status'):
                if 'active' == s:
                    wwpns.add(i)
            node['WWPN'] = list(wwpns)
            LOG.info(_('WWPN on node %(node)s: %(wwpn)s')
                     % {'node': node['id'], 'wwpn': node['WWPN']})

    def _incorporate_restricted_metadata(self, volume_ref):
        """Query the Cinder database to retrieve any access-restricted
           metadata and attach it to the volume data.
           Returns the vdisk id, which most of the time is what we were after.
           If there is no restricted metadata, tries to find the disk and
           creates it.
        """
        ctxt = context.get_admin_context()
        metadata = paxes_db_api.\
            volume_restricted_metadata_get(ctxt, volume_ref['id'])

        # If the vdisk ID is not in the metadata, this could be because of an
        # upgrade from a version that didn't use it.  We try to find it by
        # looking for a volume on the SAN with a matching name
        if RESTRICTED_METADATA_VDISK_ID_KEY not in metadata:
            # Previous versions would have used this as the name on the SAN
            vdisk = self._find_vdisk_by_name(volume_ref['name'])
            if vdisk is not None:
                self._update_restricted_metadata(volume_ref['id'], vdisk)
                metadata = paxes_db_api.\
                    volume_restricted_metadata_get(ctxt, volume_ref['id'])
            else:
                return None

        volume_ref['restricted_metadata'] = metadata
        return metadata[RESTRICTED_METADATA_VDISK_ID_KEY]

    def _check_vdisk_exists(self, vdisk_id):
        ssh_cmd = ['svcinfo', 'lsvdisk', vdisk_id]

        out, err = self._run_ssh(ssh_cmd, check_exit_code=False)
        return err == ""

    def _find_vdisk_by_name(self, vdisk_name):
        ssh_cmd = ['svcinfo', 'lsvdisk', '-delim', '!', vdisk_name]

        out, err = self._run_ssh(ssh_cmd, check_exit_code=False)
        if "CMMVC5754E" in err:
            # Can't find the volume
            return None

        attributes = {}
        for attrib_line in out.split('\n'):
            key, foo, value = attrib_line.partition('!')
            if key is not None and len(key.strip()):
                attributes[key] = value

        return attributes

    def _update_restricted_metadata(self, volume_id, vdisk):
        """Perform a database update to associate the specified information
           with the specified volume.
        """

        required_keys = set(['id', 'name', 'vdisk_UID'])
        has_required_keys = required_keys.issubset(vdisk.keys())
        msg = _("Required keys %(required)s not found in vdisk dictionary "
                "%(dictionary)r") \
            % {'required': ', '.join(required_keys),
               'dictionary': vdisk}

        self._driver_assert(has_required_keys, msg)

        metadata = {RESTRICTED_METADATA_VDISK_ID_KEY: vdisk['id'],
                    RESTRICTED_METADATA_VDISK_NAME_KEY: vdisk['name'],
                    RESTRICTED_METADATA_VDISK_UID_KEY: vdisk['vdisk_UID'],
                    RESTRICTED_METADATA_SCSI_INQUIRY_83_KEY: vdisk['vdisk_UID']
                    }
        ctxt = context.get_admin_context()
        paxes_db_api.\
            volume_restricted_metadata_update_or_create(ctxt, volume_id,
                                                        metadata)

    def _generate_candidate_names(self, volume):
        """ Generate candidate names for vdisk creation"""

        if volume.get("display_name"):
            LOG.debug('ENTER: display_name %s' % volume['display_name'])

            # First we replace all non supported characters
            # in the display_name with underscores
            # only a-z, A-Z, 0-9, _ - are supported in volume name
            display_name_nospace = re.sub(r'[^a-zA-Z0-9_-]', "_",
                                          volume['display_name'])

            # Then we substitute it into the volume_name_template specified
            # in our configuration file
            friendly_name = CONF.volume_name_template % display_name_nospace

            # We would like to use this name, but fall back to the generic
            # (UUID-based) name if that doesn't work for some reason.
            LOG.debug('EXIT: friendly_name %s' % friendly_name)
            return [friendly_name, volume['name']]
        else:
            return [volume['name']]

    def do_setup(self, ctxt):
        """Check that we have all configuration details from the storage."""

        LOG.debug('enter: do_setup')
        self._context = ctxt

        # Get storage system name and id
        ssh_cmd = ['svcinfo', 'lssystem', '-delim', '!']
        attributes = self._execute_command_and_parse_attributes(ssh_cmd)
        if not attributes or not attributes['name']:
            msg = (_('do_setup: Could not get system name'))
            LOG.error(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        self._system_name = attributes['name']
        self._system_id = attributes['id']

        # Validate that the pool exists
        pool = self.configuration.storwize_svc_volpool_name
        ssh_cmd = ['svcinfo', 'lsmdiskgrp', '-bytes', '-delim', '!',
                   '"%s"' % pool]
        attributes = self._execute_command_and_parse_attributes(ssh_cmd)
        if not attributes:
            msg = (_('do_setup: Pool %s does not exist') % pool)
            LOG.error(msg)
            raise exception.InvalidInput(reason=msg)
        self._extent_size = attributes['extent_size']

        # Check if compression is supported
        self._compression_enabled = False
        """ no longer used
        try:
            ssh_cmd = ['svcinfo', 'lslicense', '-delim', '!']
            out, err = self._run_ssh(ssh_cmd)
            license_lines = out.strip().split('\n')
            for license_line in license_lines:
                name, foo, value = license_line.partition('!')
                if name in ('license_compression_enclosures',
                            'license_compression_capacity') and value != '0':
                    self._compression_enabled = True
                    break
        except processutils.ProcessExecutionError:
            LOG.exception(_('Failed to get license information.'))
        """

        # Get the available I/O groups
        ssh_cmd = ['svcinfo', 'lsiogrp', '-delim', '!']
        out, err = self._run_ssh(ssh_cmd)
        self._assert_ssh_return(len(out.strip()), 'do_setup',
                                ssh_cmd, out, err)
        iogrps = out.strip().split('\n')
        self._assert_ssh_return(len(iogrps), 'do_setup', ssh_cmd, out, err)
        header = iogrps.pop(0)
        for iogrp_line in iogrps:
            try:
                iogrp_data = self._get_hdr_dic(header, iogrp_line, '!')
                if int(iogrp_data['node_count']) > 0:
                    self._available_iogrps.append(int(iogrp_data['id']))
                    if (self._compression_enabled is False):
                        ssh_cmd = ['svcinfo', 'lsiogrp',
                                   '-delim', '!', iogrp_data['id']]
                        out, err = self._run_ssh(ssh_cmd)
                        raw = out.strip().split('\n')
                        for attr in raw:
                            if attr == "compression_supported!yes":
                                self._compression_enabled = True
                                break
            except exception.VolumeBackendAPIException:
                with excutils.save_and_reraise_exception():
                    self._log_cli_output_error('do_setup',
                                               ssh_cmd, out, err)
            except KeyError:
                self._handle_keyerror('lsnode', header)
            except ValueError:
                msg = (_('Expected integers for node_count and vdisk_count, '
                         'svcinfo lsiogrp returned: %(node)s and %(vdisk)s') %
                       {'node': iogrp_data['node_count'],
                        'vdisk': iogrp_data['vdisk_count']})
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(data=msg)

        # Get the iSCSI and FC names of the Storwize/SVC nodes
        ssh_cmd = ['svcinfo', 'lsnode', '-delim', '!']
        out, err = self._run_ssh(ssh_cmd)
        self._assert_ssh_return(len(out.strip()), 'do_setup',
                                ssh_cmd, out, err)

        nodes = out.strip().split('\n')
        self._assert_ssh_return(len(nodes), 'do_setup', ssh_cmd, out, err)
        header = nodes.pop(0)
        for node_line in nodes:
            try:
                node_data = self._get_hdr_dic(header, node_line, '!')
            except exception.VolumeBackendAPIException:
                with excutils.save_and_reraise_exception():
                    self._log_cli_output_error('do_setup',
                                               ssh_cmd, out, err)
            node = {}
            try:
                node['id'] = node_data['id']
                node['name'] = node_data['name']
                node['IO_group'] = node_data['IO_group_id']
                node['iscsi_name'] = node_data['iscsi_name']
                node['WWNN'] = node_data['WWNN']
                node['status'] = node_data['status']
                node['WWPN'] = []
                node['ipv4'] = []
                node['ipv6'] = []
                node['enabled_protocols'] = []
                if node['status'] == 'online':
                    self._storage_nodes[node['id']] = node
            except KeyError:
                self._handle_keyerror('lsnode', header)

        # Get the iSCSI IP addresses and WWPNs of the Storwize/SVC nodes
        self._get_iscsi_ip_addrs()
        self._get_fc_wwpns()

        # For each node, check what connection modes it supports.  Delete any
        # nodes that do not support any types (may be partially configured).
        to_delete = []
        for k, node in self._storage_nodes.iteritems():
            if ((len(node['ipv4']) or len(node['ipv6']))
                    and len(node['iscsi_name'])):
                node['enabled_protocols'].append('iSCSI')
                self._enabled_protocols.add('iSCSI')
            if len(node['WWPN']):
                node['enabled_protocols'].append('FC')
                self._enabled_protocols.add('FC')
            if not len(node['enabled_protocols']):
                to_delete.append(k)

        for delkey in to_delete:
            del self._storage_nodes[delkey]

        # Make sure we have at least one node configured
        self._driver_assert(len(self._storage_nodes),
                            _('do_setup: No configured nodes'))

        # Ensure that the default volume type exists
        vtn = self.configuration.default_volume_type
        vtn = vtn.decode('utf-8') if vtn else vtn
        try:
            volume_types.get_volume_type_by_name(ctxt, vtn)
        except exception.VolumeTypeNotFoundByName:
            # If the default volume type does not exist, we create it here.
            LOG.info(_("Creating default volume type '%s'") % vtn)
            self._create_default_volume_type(ctxt, vtn)

        LOG.debug('leave: do_setup')

    def get_compression_enabled(self):
        """Helper Method to get compression enablement"""
        return self._compression_enabled

    def _create_default_volume_type(self, context, volume_type_name):
        """Internal Helper Method to Create a Default Volume Type for Host"""
        vbn = self.configuration.volume_backend_name

        # Obtain our default options
        opts = self._build_default_opts()
        extra_specs = {}
        for key, value in opts.iteritems():
            extra_specs["drivers:" + key] = value

        extra_specs['drivers:display_name'] = volume_type_name
        extra_specs['capabilities:volume_backend_name'] = vbn

        def voltype_create(name, extra_specs):
            """ Don't use volume_type.create during init_host"""
            try:
                type_ref = db_api.volume_type_create(
                    context, dict(name=name, extra_specs=extra_specs))
            except db_exc.DBError as e:
                LOG.exception(_('DB error: %s') % e)
                raise exception.VolumeTypeCreateFailed(
                    name=name, extra_specs=extra_specs)
            return type_ref

        return voltype_create(volume_type_name, extra_specs)

    def _build_default_opts(self):
        # Ignore capitalization
        protocol = self.configuration.storwize_svc_connection_protocol
        if protocol.lower() == 'fc':
            protocol = 'FC'
        elif protocol.lower() == 'iscsi':
            protocol = 'iSCSI'

        opt = {'rsize': self.configuration.storwize_svc_vol_rsize,
               'warning': self.configuration.storwize_svc_vol_warning,
               'autoexpand': self.configuration.storwize_svc_vol_autoexpand,
               'grainsize': self.configuration.storwize_svc_vol_grainsize,
               'compression': self.configuration.storwize_svc_vol_compression,
               'easytier': self.configuration.storwize_svc_vol_easytier,
               'protocol': protocol,
               'multipath': self.configuration.storwize_svc_multipath_enabled,
               'iogrp': self.configuration.storwize_svc_vol_iogrp,
               'storage_pool': self.configuration.storwize_svc_volpool_name}
        return opt

    def check_for_setup_error(self):
        """Ensure that the flags are set properly."""
        LOG.debug('enter: check_for_setup_error')

        # Check that we have the system ID information
        if self._system_name is None:
            exception_msg = (_('Unable to determine system name'))
            raise exception.VolumeBackendAPIException(data=exception_msg)
        if self._system_id is None:
            exception_msg = (_('Unable to determine system id'))
            raise exception.VolumeBackendAPIException(data=exception_msg)
        if self._extent_size is None:
            exception_msg = (_('Unable to determine pool extent size'))
            raise exception.VolumeBackendAPIException(data=exception_msg)

        required_flags = ['san_ip', 'san_ssh_port', 'san_login',
                          'storwize_svc_volpool_name']
        for flag in required_flags:
            if not self.configuration.safe_get(flag):
                raise exception.InvalidInput(reason=_('%s is not set') % flag)

        # Ensure that either password or keyfile were set
        if not (self.configuration.san_password or
                self.configuration.san_private_key):
            raise exception.InvalidInput(
                reason=_('Password or SSH private key is required for '
                         'authentication: set either san_password or '
                         'san_private_key option'))

        # Check that flashcopy_timeout is not more than 10 minutes
        flashcopy_timeout = self.configuration.storwize_svc_flashcopy_timeout
        if not (flashcopy_timeout > 0 and flashcopy_timeout <= 600):
            raise exception.InvalidInput(
                reason=_('Illegal value %d specified for '
                         'storwize_svc_flashcopy_timeout: '
                         'valid values are between 0 and 600')
                % flashcopy_timeout)

        opts = self._build_default_opts()
        self._check_vdisk_opts(opts)

        LOG.debug('leave: check_for_setup_error')

    """====================================================================="""
    """ INITIALIZE/TERMINATE CONNECTIONS                                    """
    """====================================================================="""

    def ensure_export(self, ctxt, volume):
        """Check that the volume exists on the storage.

        The system does not "export" volumes as a Linux iSCSI target does,
        and therefore we just check that the volume exists on the storage.
        """
        vdisk_id = self._incorporate_restricted_metadata(volume)
        if vdisk_id is None:
            LOG.error(_('ensure_export: Volume %(volume_id)s does not '
                        'reference a vdisk')
                      % {'volume_id': volume['id']})
            return

        volume_defined = self._is_vdisk_defined(vdisk_id)
        if not volume_defined:
            LOG.error(_('ensure_export: Volume %(volume_id)s references '
                        'vdisk %(vdisk)s, which was not found on storage')
                      % {'volume_id': volume['id'],
                         'vdisk': vdisk_id})

    def create_export(self, ctxt, volume):
        model_update = None
        return model_update

    def remove_export(self, ctxt, volume):
        pass

    def _add_chapsecret_to_host(self, host_name):
        """Generate and store a randomly-generated CHAP secret for the host."""

        chap_secret = utils.generate_password()
        ssh_cmd = ['svctask', 'chhost', '-chapsecret', chap_secret, host_name]
        ssh_cmd_out = ['svctask', 'chhost', '-chapsecret',
                       "********", host_name]
        out, err = self._run_ssh(ssh_cmd)
        # No output should be returned from chhost
        self._assert_ssh_return(len(out.strip()) == 0,
                                '_add_chapsecret_to_host',
                                ssh_cmd_out, out, err)
        return chap_secret

    def _get_chap_secret_for_host(self, host_name):
        """Return the CHAP secret for the given host."""

        LOG.debug('enter: _get_chap_secret_for_host: host name %s'
                  % host_name)

        ssh_cmd = ['svcinfo', 'lsiscsiauth', '-delim', '!']
        out, err = self._run_ssh(ssh_cmd)

        if not len(out.strip()):
            return None

        host_lines = out.strip().split('\n')
        STDOUT = "***********"
        self._assert_ssh_return(len(host_lines), '_get_chap_secret_for_host',
                                ssh_cmd, STDOUT, err)

        header = host_lines.pop(0).split('!')
        self._assert_ssh_return('name' in header, '_get_chap_secret_for_host',
                                ssh_cmd, STDOUT, err)
        self._assert_ssh_return('iscsi_auth_method' in header,
                                '_get_chap_secret_for_host', ssh_cmd,
                                STDOUT, err)
        self._assert_ssh_return('iscsi_chap_secret' in header,
                                '_get_chap_secret_for_host', ssh_cmd,
                                STDOUT, err)
        name_index = header.index('name')
        method_index = header.index('iscsi_auth_method')
        secret_index = header.index('iscsi_chap_secret')

        chap_secret = None
        host_found = False
        for line in host_lines:
            info = line.split('!')
            if info[name_index] == host_name:
                host_found = True
                if info[method_index] == 'chap':
                    chap_secret = info[secret_index]

        self._assert_ssh_return(host_found, '_get_chap_secret_for_host',
                                ssh_cmd, STDOUT, err)

        LOG.debug('leave: _get_chap_secret_for_host: host name '
                  '%(host_name)s with secret %(chap_secret)s'
                  % {'host_name': host_name, 'chap_secret': "**********"})

        return chap_secret

    def _connector_to_hostname_prefix(self, connector):
        """Translate connector info to storage system host name.

        Translate a host's name and IP to the prefix of its hostname on the
        storage subsystem.  We create a host name host name from the host and
        IP address, replacing any invalid characters (at most 55 characters),
        and adding a random 8-character suffix to avoid collisions. The total
        length should be at most 63 characters.

        """

        host_name = connector['host']
        if isinstance(host_name, unicode):
            host_name = host_name.translate(self._unicode_host_name_filter)
        elif isinstance(host_name, str):
            host_name = host_name.translate(self._string_host_name_filter)
        else:
            msg = _('_create_host: Cannot clean host name. Host name '
                    'is not unicode or string')
            LOG.error(msg)
            raise exception.NoValidHost(reason=msg)

        host_name = str(host_name)

        if not re.match('^[A-Za-z]', host_name):
            host_name = "_" + host_name

        return host_name[:55]

    def _find_host_from_attached_volume(self, connector, vdisk_id):
        """ Another fastpath to find the existing hostmap that
        hasn't been logged in to SAN. So it will not show by
        lsfabric. But the disk may have been mapped.
        """
        ssh_cmd = ['lsvdiskhostmap', '-delim', '!', vdisk_id]

        if (not connector or not connector.get('wwpns') or
                not connector.get('initiator')):
            return None
        try:
            out, err = self._run_ssh(ssh_cmd, attempts=2)
        except processutils.ProcessExecutionError as e:
            if 'CMMVC5753E' in e.stderr:
                # CMMVC5753E: The specified object does not exist or is not a
                #             suitable candidate.
                return None
            else:
                # something bad happened
                raise
        if not len(out.strip()):
            return None
        if 'wwpns' in connector:
            # The connector wwpns passed in is unicode. Fix it for
            # the set compare.
            conn_wwpns = [x.encode('ascii', 'ignore').upper()
                          for x in connector.get('wwpns')]

        host_lines = out.strip().split('\n')
        header = host_lines.pop(0).split('!')
        self._assert_ssh_return('host_id' in header and
                                'host_name' in header,
                                '_find_host_from_attached_volume',
                                ssh_cmd, out, err)
        host_id_idx = header.index('host_id')
        host_name_idx = header.index('host_name')

        hostname = None
        for line in host_lines:
            host_id = line.split('!')[host_id_idx]
            host_name = line.split('!')[host_name_idx]
            ssh_cmd = ['lshost', '-delim', '!', host_id]
            try:
                out, err = self._run_ssh(ssh_cmd, attempts=2)
            except processutils.ProcessExecutionError:
                continue
            if not len(out.strip()):
                continue

            if 'wwpns' in connector:
                # find all the WWPNs from the lshost output. Expect all
                # the WWPNs in the lshost output are in upper case.
                wwpns = RE_WWPN.findall(out)

                if (set(conn_wwpns) == set(wwpns) or
                        set(conn_wwpns).issubset(set(wwpns))):
                    hostname = host_name
                    break
            else:
                if connector['initiator'] in set(RE_ISCSI_NAME.findall(out)):
                    hostname = host_name
                    break

        return hostname

    def _find_host_from_wwpn(self, connector):
        # SVC uses upper-case WWPNs
        for wwpn in [x.upper() for x in connector['wwpns']]:
            ssh_cmd = ['svcinfo', 'lsfabric', '-wwpn', wwpn, '-delim', '!']
            out, err = self._run_ssh(ssh_cmd)

            if not len(out.strip()):
                # This WWPN is not in use
                continue

            host_lines = out.strip().split('\n')
            header = host_lines.pop(0).split('!')
            self._assert_ssh_return('remote_wwpn' in header and
                                    'name' in header,
                                    '_find_host_from_wwpn',
                                    ssh_cmd, out, err)
            rmt_wwpn_idx = header.index('remote_wwpn')
            name_idx = header.index('name')

            wwpns = map(lambda x: x.split('!')[rmt_wwpn_idx], host_lines)

            if wwpn in wwpns:
                # All the wwpns will be the mapping for the same
                # host from this WWPN-based query. Just pick
                # the name from first line.
                hostname = host_lines[0].split('!')[name_idx]
                return hostname

        # Didn't find a host
        return None

    def _find_host_exhaustive(self, connector, hosts):
        for host in hosts:
            # The hosts list may go stale while the list is processed.
            # Handle it accordingly.
            ssh_cmd = ['svcinfo', 'lshost', '-delim', '!', host]
            try:
                out, err = self._run_ssh(ssh_cmd)
            except processutils.ProcessExecutionError as e:
                if 'CMMVC5754E' in e.stderr:
                    # CMMVC5754E: The specified object does not exist
                    #             The host has been deleted while walking
                    #             the list.
                    continue
                else:
                    # something bad happened.
                    raise e

            self._assert_ssh_return(len(out.strip()),
                                    '_find_host_exhaustive',
                                    ssh_cmd, out, err)
            for attr_line in out.split('\n'):
                # If '!' not found, return the string and two empty strings
                attr_name, foo, attr_val = attr_line.partition('!')
                if (attr_name == 'iscsi_name' and
                        'initiator' in connector and
                        attr_val == connector['initiator']):
                    return host
                elif (attr_name == 'WWPN' and
                      'wwpns' in connector and
                      attr_val.lower() in
                      map(str.lower, map(str, connector['wwpns']))):
                        return host
        return None

    def _get_host_from_connector(self, connector, vdisk_id, is_initconn=True):
        """List the hosts defined in the storage.

        Return the host name with the given connection info, or None if there
        is no host fitting that information.

        """

        prefix = self._connector_to_hostname_prefix(connector)
        LOG.debug('enter: _get_host_from_connector: prefix %s' % prefix)

        # GMN - this block of code fast-paths the common NPIV case where
        # a host definition does not exist, and the WWPNs are not yet logged
        # into the fabric.  Without this case, lsfabric can't help us to find
        # a host, so we end up falling back to the slow exhaustive method,
        # of doing lshost per host, which is very slow if you have a lot of
        # hosts (which you do for NPIV environments).
        #
        # What we do here is just jump in and try to create a new host
        # with all the desired WWPNs.  It will fail if the host already
        # exists or if some of the port specifiers are already present in
        # another host
        if is_initconn:
            # For initialize_connection, the host may not be defined
            # yet. Try it first.
            try:
                return self._create_host(connector, False)
            except paxes_exception.SVCHostDefsException:
                # Tried to create a host definition, but couldn't because we
                # have reached the limit.  Fail as there's nothing we can do
                # here.
                raise paxes_exception.SVCHostDefsException
            except Exception as ex:
                # Anything else and we carry on, looking further for an
                # existing host definition.
                LOG.info(_("Continue to fall back processing after initial "
                           "failure to make a host on the SAN controller: "
                           "%s") % ex)
                pass

        # ajiang - Another fastpath host lookup. If the _create_host failed
        # we know the wwpns have been defined in some hosts on SVC.
        # try to do fast lookup in two ways:
        # 1. check whether the volume has been mapped to the connector.
        #    If so, return the matching host
        # 2. If #1 doesn't find the host, look for lsfabric to see
        #    whether the wwpn has been logged in. If so, find the matching
        #    host.
        # If neither #1 or #2 finds any matching host, we have to go
        # through the host definition one by one which will be the slow path.

        LOG.debug("Trying to lookup SVC host from the vdisk ID.")
        hostname = self._find_host_from_attached_volume(connector, vdisk_id)

        if not hostname:
            if 'wwpns' in connector:
            # If we have FC information, we have a faster lookup option
                hostname = self._find_host_from_wwpn(connector)

        # If we don't have a hostname yet, try the long way
        if not hostname:
            LOG.debug("Trying to lookup up the host the long way...")
            # Get list of host in the storage
            ssh_cmd = ['svcinfo', 'lshost', '-delim', '!']
            out, err = self._run_ssh(ssh_cmd)

            if not len(out.strip()):
                return None

            host_lines = out.strip().split('\n')
            self._assert_ssh_return(len(host_lines),
                                    '_get_host_from_connector',
                                    ssh_cmd, out, err)
            header = host_lines.pop(0).split('!')
            self._assert_ssh_return('name' in header,
                                    '_get_host_from_connector',
                                    ssh_cmd, out, err)
            name_index = header.index('name')
            hosts = map(lambda x: x.split('!')[name_index], host_lines)
            hostname = self._find_host_exhaustive(connector, hosts)

        LOG.debug('leave: _get_host_from_connector: host %s' % hostname)

        return hostname

    def _create_host(self, connector, check_exit_code=True):
        """Create a new host on the storage system.

        We create a host name and associate it with the given connection
        information.

        """

        LOG.debug('enter: _create_host: host %s' % connector['host'])

        rand_id = str(random.randint(0, 99999999)).zfill(8)
        host_name = '%s-%s' % (self._connector_to_hostname_prefix(connector),
                               rand_id)

        # Get all port information from the connector
        ports = []
        if 'initiator' in connector:
            ports.append('-iscsiname %s' % connector['initiator'])
        if 'wwpns' in connector:
            for wwpn in connector['wwpns']:
                ports.append('-hbawwpn %s' % wwpn)

        # When creating a host, we need one port
        self._driver_assert(len(ports), _('_create_host: No connector ports'))
        port1 = ports.pop(0)
        arg_name, arg_val = port1.split()
        ssh_cmd = ['svctask', 'mkhost', '-force', arg_name, arg_val, '-name',
                   '"%s"' % host_name]
        out, err = self._run_ssh(ssh_cmd, check_exit_code=check_exit_code)
        if check_exit_code:
            self._assert_ssh_return('successfully created' in out,
                                    '_create_host', ssh_cmd, out, err)
        else:
            # We just want an exception if we didn't create the host
            if 'CMMVC6220E' in err:
                raise paxes_exception.SVCHostDefsException(
                    self.endpoint_desc)

            if not 'successfully created' in out:
                raise exception.VolumeBackendAPIException(data=err)

        # Add any additional ports to the host
        try:
            for port in ports:
                arg_name, arg_val = port.split()
                ssh_cmd = ['svctask', 'addhostport', '-force',
                           arg_name, arg_val, host_name]
                out, err = self._run_ssh(ssh_cmd,
                                         check_exit_code=check_exit_code)
                if err:
                    raise exception.VolumeBackendAPIException(data=err)
        except exception.VolumeBackendAPIException:
            with excutils.save_and_reraise_exception():
                ssh_cmd = ['svctask', 'rmhost', host_name]
                self._run_ssh(ssh_cmd, check_exit_code=check_exit_code)

        LOG.debug('leave: _create_host: host %(host)s - %(host_name)s' %
                  {'host': connector['host'], 'host_name': host_name})
        return host_name

    def _get_hostvdisk_mappings(self, host_name):
        """Return the defined storage mappings for a host, as vdisk IDs."""

        return_data = {}
        ssh_cmd = ['svcinfo', 'lshostvdiskmap', '-delim', '!', host_name]
        out, err = self._run_ssh(ssh_cmd)

        mappings = out.strip().split('\n')
        if len(mappings):
            header = mappings.pop(0)
            for mapping_line in mappings:
                mapping_data = self._get_hdr_dic(header, mapping_line, '!')
                return_data[mapping_data['vdisk_id']] = mapping_data

        return return_data

    def _map_vol_to_host(self, vdisk_id, host_name):
        """Create a mapping between a volume to a host."""

        LOG.debug('enter: _map_vol_to_host: vdisk %(vdisk_id)s to '
                  'host %(host_name)s'
                  % {'vdisk_id': vdisk_id, 'host_name': host_name})

        # Check if this volume is already mapped to this host
        mapping_data = self._get_hostvdisk_mappings(host_name)

        mapped_flag = False
        result_lun = '-1'
        if vdisk_id in mapping_data:
            mapped_flag = True
            result_lun = mapping_data[vdisk_id]['SCSI_id']
        else:
            lun_used = [int(v['SCSI_id']) for v in mapping_data.values()]
            lun_used.sort()
            # Assume all luns are taken to this point, and then try to find
            # an unused one
            result_lun = str(len(lun_used))
            for index, n in enumerate(lun_used):
                if n > index:
                    result_lun = str(index)
                    break

        # Volume is not mapped to host, create a new LUN
        if not mapped_flag:
            ssh_cmd = ['svctask', 'mkvdiskhostmap', '-host', host_name,
                       '-scsi', result_lun, vdisk_id]
            out, err = self._run_ssh(ssh_cmd, check_exit_code=False)
            if err and err.startswith('CMMVC6071E'):
                if not self.configuration.storwize_svc_multihostmap_enabled:
                    LOG.error(_('storwize_svc_multihostmap_enabled is set '
                                'to False, Not allow multi host mapping'))
                    raise paxes_exception.SVCMultiMapException(
                        self.endpoint_desc,
                        vdisk_id=vdisk_id,
                        host=host_name)
                for i in range(len(ssh_cmd)):
                    if ssh_cmd[i] == 'mkvdiskhostmap':
                        ssh_cmd.insert(i + 1, '-force')

                # try to map one volume to multiple hosts
                out, err = self._run_ssh(ssh_cmd)
                LOG.warn(_('vdisk %s mapping to multi host') % vdisk_id)
                self._assert_ssh_return('successfully created' in out,
                                        '_map_vol_to_host', ssh_cmd, out, err)
            else:
                self._assert_ssh_return('successfully created' in out,
                                        '_map_vol_to_host', ssh_cmd, out, err)
        LOG.debug('leave: _map_vol_to_host: LUN %(result_lun)s, vdisk '
                  '%(vdisk_id)s, host %(host_name)s' %
                  {'result_lun': result_lun,
                   'vdisk_id': vdisk_id,
                   'host_name': host_name})
        return result_lun

    def _delete_host(self, host_name):
        """Delete a host on the storage system."""

        LOG.debug('enter: _delete_host: host %s ' % host_name)

        ssh_cmd = ['svctask', 'rmhost', host_name]
        out, err = self._run_ssh(ssh_cmd)
        # No output should be returned from rmhost
        self._assert_ssh_return(len(out.strip()) == 0,
                                '_delete_host', ssh_cmd, out, err)

        LOG.debug('leave: _delete_host: host %s ' % host_name)

    def _get_conn_fc_wwpns(self, host_name):
        wwpns = []
        cmd = ['svcinfo', 'lsfabric', '-host', host_name]
        generator = self._port_conf_generator(cmd)
        header = next(generator, None)
        if not header:
            return wwpns

        for port_data in generator:
            try:
                wwpns.append(port_data['local_wwpn'])
            except KeyError as e:
                self._handle_keyerror('lsfabric', header)

        return wwpns

    def validate_connector(self, connector):
        """Check connector for at least one enabled protocol (iSCSI/FC)."""
        valid = False
        if 'iSCSI' in self._enabled_protocols and 'initiator' in connector:
            valid = True
        if 'FC' in self._enabled_protocols and 'wwpns' in connector:
            valid = True
        if not valid:
            err_msg = (_('The connector does not contain the required '
                         'information: %(connector)s, protocols %(protos)s')
                       % {'connector': connector,
                          'protos': self._enabled_protocols})
            LOG.error(err_msg)
            raise exception.VolumeBackendAPIException(data=err_msg)

    def initialize_connection(self, volume, connector):
        """Perform the necessary work so that an iSCSI/FC connection can
        be made.

        To be able to create an iSCSI/FC connection from a given host to a
        volume, we must:
        1. Translate the given iSCSI name or WWNN to a host name
        2. Create new host on the storage system if it does not yet exist
        3. Map the volume to the host if it is not already done
        4. Return the connection information for relevant nodes (in the
           proper I/O group)

        """
        vdisk_id = self._incorporate_restricted_metadata(volume)
        LOG.info(_("Enter: initialize_connection: %s") % volume.get('name'))
        LOG.debug('volume %(vol)s with connector %(conn)s' %
                  {'vol': str(volume), 'conn': str(connector)})

        vol_opts = self._get_vdisk_params(volume['volume_type_id'])
        # host_name = connector['host']

        # Obtain the disk's attributes, raises an exception on a communications
        # error, returns None if the disk doesn't exist.
        volume_attributes = self._get_vdisk_attributes(vdisk_id)

        if not volume_attributes:
            raise paxes_exception.SVCVdiskNotFoundException(
                self.endpoint_desc, volume['id'], vdisk_id=vdisk_id)

        # Ensure that the UID matches and we don't attach the wrong disk,
        # raise exception if the UID doesn't match.
        self._verify_uid(volume_attributes, volume)

        try:
            preferred_node = volume_attributes['preferred_node_id']
            IO_group = volume_attributes['IO_group_id']
        except KeyError as e:
            LOG.error(_('Did not find expected column name in '
                        'lsvdisk: %s') % e)
            exception_msg = (_('initialize_connection: Missing volume '
                               'attribute for vdisk %s') % vdisk_id)
            raise exception.VolumeBackendAPIException(data=exception_msg)

        # Check if a host object is defined for this host name
        host_name = self._get_host_from_connector(connector, vdisk_id)
        if host_name is None:
            # Host does not exist - add a new host to Storwize/SVC
            host_name = self._create_host(connector)
            # Verify that create_new_host succeeded
            self._driver_assert(
                host_name is not None,
                _('_create_host failed to return the host name.'))

        if vol_opts['protocol'] == 'iSCSI':
            chap_secret = self._get_chap_secret_for_host(host_name)
            if chap_secret is None:
                chap_secret = self._add_chapsecret_to_host(host_name)

        lun_id = self._map_vol_to_host(vdisk_id, host_name)

        try:
            # Get preferred node and other nodes in I/O group
            preferred_node_entry = None
            io_group_nodes = []
            for k, node in self._storage_nodes.iteritems():
                if vol_opts['protocol'] not in node['enabled_protocols']:
                    continue
                if node['id'] == preferred_node:
                    preferred_node_entry = node
                if node['IO_group'] == IO_group:
                    io_group_nodes.append(node)

            if not len(io_group_nodes):
                exception_msg = (_('initialize_connection: No node found in '
                                   'I/O group %(gid)s for vdisk %(vdisk_id)s')
                                 % {'gid': IO_group, 'vdisk_id': vdisk_id})
                LOG.error(exception_msg)
                raise exception.VolumeBackendAPIException(data=exception_msg)

            if not preferred_node_entry and not vol_opts['multipath']:
                # Get 1st node in I/O group
                preferred_node_entry = io_group_nodes[0]
                LOG.warn(_('initialize_connection: Did not find a preferred '
                           'node for vdisk %s') % vdisk_id)

            properties = {}
            properties['target_discovered'] = False
            properties['target_lun'] = lun_id
            properties['volume_id'] = volume['id']
            if vol_opts['protocol'] == 'iSCSI':
                type_str = 'iscsi'
                if len(preferred_node_entry['ipv4']):
                    ipaddr = preferred_node_entry['ipv4'][0]
                else:
                    ipaddr = preferred_node_entry['ipv6'][0]
                properties['target_portal'] = '%s:%s' % (ipaddr, '3260')
                properties['target_iqn'] = preferred_node_entry['iscsi_name']
                properties['auth_method'] = 'CHAP'
                properties['auth_username'] = connector['initiator']
                LOG.debug('leave: initialize_connection:\n volume: %(vol)s\n '
                          'connector %(conn)s\n properties: %(prop)s'
                          % {'vol': str(volume),
                             'conn': str(connector),
                             'prop': str(properties)})
                properties['auth_password'] = chap_secret
            else:
                type_str = 'fibre_channel'
                conn_wwpns = self._get_conn_fc_wwpns(host_name)
                if len(conn_wwpns) == 0:
                    msg = (_('Could not get FC connection information for the '
                             'host-volume connection. Is the host configured '
                             'properly for FC connections?'))
                    LOG.error(msg)
                    raise exception.VolumeBackendAPIException(data=msg)
                if not vol_opts['multipath']:
                    if preferred_node_entry['WWPN'] in conn_wwpns:
                        properties['target_wwn'] = preferred_node_entry['WWPN']
                    else:
                        properties['target_wwn'] = conn_wwpns[0]
                else:
                    properties['target_wwn'] = conn_wwpns
                LOG.debug('leave: initialize_connection:\n volume: %(vol)s\n '
                          'connector %(conn)s\n properties: %(prop)s'
                          % {'vol': str(volume),
                             'conn': str(connector),
                             'prop': str(properties)})
        except Exception:
            with excutils.save_and_reraise_exception():
                self.terminate_connection(volume, connector)
                LOG.error(_('initialize_connection: Failed to collect return '
                            'properties for volume %(vol)s and connector '
                            '%(conn)s.\n') % {'vol': str(volume),
                                              'conn': str(connector)})

        return {'driver_volume_type': type_str, 'data': properties, }

    def terminate_connection(self, volume, connector, **kwargs):
        """Cleanup after an iSCSI connection has been terminated.

        When we clean up a terminated connection between a given connector
        and volume, we:
        1. Translate the given connector to a host name
        2. Remove the volume-to-host mapping if it exists
        3. Delete the host if it has no more mappings (hosts are created
           automatically by this driver when mappings are created)
        """
        LOG.debug('enter: terminate_connection: volume %(vol)s with '
                  'connector %(conn)s' % {'vol': volume['id'],
                                          'conn': str(connector)})

        vdisk_id = self._incorporate_restricted_metadata(volume)

        # Ensure that the UID matches and we don't detach the wrong disk,
        # Warn for certain exceptions.
        try:
            self._verify_uid_by_vdisk_id(vdisk_id, volume)
        except paxes_exception.SVCVdiskMismatchException as e:
            # Volume has been deleted and recreated, probably in use by
            # someone else.  Do nothing, but warn.
            LOG.warn(_("terminate_connection: vdisk mismatch: %(err)s. "
                       "Performing no operation on the storage controller")
                     % {'err': (_("%s") % e)})
            return
        except paxes_exception.SVCVdiskNotFoundException as e:
            # Volume has been deleted, do nothing, but warn.
            LOG.warn(_("terminate_connection: vdisk deleted: %(err)s. "
                       "Performing no operation on the storage controller")
                     % {'err': (_("%s") % e)})
            return
        except Exception as e:
            with excutils.save_and_reraise_exception():
                LOG.exception(e)  # unexpected

        host_name = self._get_host_from_connector(connector, vdisk_id,
                                                  is_initconn=False)
        # Verify that _get_host_from_connector returned the host.
        # Is there any situation where this would just be a warning?
        if host_name is None:
            msg = _('Detach volume: failed to lookup host name '
                    'for vdisk ID: %(vdisk)s') % dict(vdisk=vdisk_id)
            LOG.error(msg)
            # don't raise without any exception. Otherwise will receive
            # exception "exceptions must be old-style classes or derived
            # from BaseException, not NoneType"
            raise exception.VolumeDriverException(message=msg)

        # Check if vdisk-host mapping exists, remove if it does
        mapping_data = self._get_hostvdisk_mappings(host_name)
        if vdisk_id in mapping_data:
            LOG.debug("Before rmvdiskhostmap: vdisk_id=%s, host_name"
                      "=%s, mapping_data=%s" % (vdisk_id, host_name,
                                                mapping_data[vdisk_id]))
            ssh_cmd = ['svctask', 'rmvdiskhostmap', '-host', host_name,
                       vdisk_id]
            try:
                out, err = self._run_ssh(ssh_cmd)
                LOG.debug("After rmvdiskhostmap: stdout=%s, stderr=%s" %
                          (out, err))
            except processutils.ProcessExecutionError as e:
                LOG.exception(e)
                err = _("%s") % e
            # check for error case. The non empty 'out' case is already
            # handled by the assert below.
            if err and len(out.strip()) == 0:
                msg = _("There was an error when attempting to remove the "
                        "host disk mappings for volume ID %(vol)s and vdsik "
                        "ID %(vdisk)s: %(err)s") %\
                    dict(vol=volume['id'], vdisk=vdisk_id, err=err)
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(data=msg)

            # Verify CLI behaviour - no output is returned from rmvdiskhostmap
            self._assert_ssh_return(len(out.strip()) == 0,
                                    'terminate_connection', ssh_cmd, out, err)
            del mapping_data[vdisk_id]
        else:
            LOG.warn(_('terminate_connection: No mapping of vdisk '
                       '%(vdisk_id)s to host %(host_name)s found') %
                     {'vdisk_id': vdisk_id, 'host_name': host_name})

        # If this host has no more mappings, delete it
        if not mapping_data:
            LOG.debug("No more mappings. Delete host definition on storage "
                      "backend: %s" % host_name)
            self._delete_host(host_name)
            LOG.debug("Host definition removed.")

        LOG.debug('leave: terminate_connection: volume %(vol)s with '
                  'connector %(conn)s' % {'vol': str(volume),
                                          'conn': str(connector)})

    """====================================================================="""
    """ VOLUMES/SNAPSHOTS                                                   """
    """====================================================================="""

    def _get_vdisk_attributes(self, vdisk_id):
        """Return vdisk attributes, or None if vdisk does not exist

        Exception is raised if the information from system can not be
        parsed/matched to a single vdisk.
        """

        ssh_cmd = ['svcinfo', 'lsvdisk', '-bytes', '-delim', '!', vdisk_id]
        return self._execute_command_and_parse_attributes(ssh_cmd)

    def _get_vdisk_fc_mappings(self, vdisk_id):
        """Return FlashCopy mappings that this vdisk is associated with."""

        ssh_cmd = ['svcinfo', 'lsvdiskfcmappings', '-nohdr', vdisk_id]
        out, err = self._run_ssh(ssh_cmd)

        mapping_ids = []
        if (len(out.strip())):
            lines = out.strip().split('\n')
            mapping_ids = [line.split()[0] for line in lines]
        return mapping_ids

    def _get_vdisk_params(self, type_id):
        opts = self._build_default_opts()
        if type_id:
            ctxt = context.get_admin_context()
            volume_type = volume_types.get_volume_type(ctxt, type_id)
        else:
            volume_type = volume_types.get_default_volume_type()
        if volume_type:
            specs = volume_type.get('extra_specs')
            for k, value in specs.iteritems():
                # Get the scope, if using scope format
                key_split = k.split(':')
                if len(key_split) == 1:
                    scope = None
                    key = key_split[0]
                else:
                    scope = key_split[0]
                    key = key_split[1]

                # We generally do not look at capabilities in the driver, but
                # protocol is a special case where the user asks for a given
                # protocol and we want both the scheduler and the driver to act
                # on the value.
                if scope == 'capabilities' and key == 'storage_protocol':
                    scope = None
                    key = 'protocol'
                    words = value.split()
                    self._driver_assert(words and
                                        len(words) == 2 and
                                        words[0] == '<in>',
                                        _('protocol must be specified as '
                                          '\'<in> iSCSI\' or \'<in> FC\''))
                    del words[0]
                    value = words[0]

                # Anything keys that the driver should look at should have the
                # 'drivers' scope.
                if scope and scope != "drivers":
                    continue

                if key in opts:
                    this_type = type(opts[key]).__name__
                    if this_type == 'int':
                        value = int(value)
                    elif this_type == 'bool':
                        value = strutils.bool_from_string(value)
                    opts[key] = value

        self._check_vdisk_opts(opts)
        return opts

    def _get_vdisk_id_from_vdisk_name(self, name):
        """Given a vdisk name, query and return the corresponding vdiskid.
           Returns None if there was no vdisk with the specified name.
        """
        ssh_cmd = ['svcinfo', 'lsvdisk', '-bytes', '-delim', '!', name]
        attrs = self._execute_command_and_parse_attributes(ssh_cmd)
        if attrs is None:
            return None

        return attrs['id']

    def _create_vdisk(self, names, size, units, opts):
        """Create a new vdisk, returns vdisk ID
        names contains a list of names to use in order of preference.  We try
        them all until one works, as a simple way of handling names that are
        invalid or already in use on the storage controller.
        """

        names_string = ', '.join(names)
        LOG.debug('enter: _create_vdisk: candidate names %s ' %
                  names_string)

        model_update = None
        params = self._get_vdisk_create_params(opts)
        # Iterate over all names.  We break out of the loop as soon as we find
        # a name that works.
        for name in names:

            # If an exception is raised here, we remember it in case we need to
            # raise it later.
            last_exception = None

            pool = self.configuration.storwize_svc_volpool_name
            ssh_cmd = ['svctask', 'mkvdisk', '-name', name,
                       '-mdiskgrp', '"%s"' % pool,
                       '-iogrp', str(opts['iogrp']), '-size', size,
                       '-unit', units] + params
            try:
                out, err = self._run_ssh(ssh_cmd)
            except processutils.ProcessExecutionError as e:
                if ("CMMVC6035E" in e.stderr or
                        "CMMVC6527E" in e.stderr or
                        "CMMVC5738E" in e.stderr):
                    # CMMVC6035E: Name already in use.
                    # CMMVC6527E: Invalid name
                    # CMMVC5738E: Name too long
                    # If we failed with one of the above errors, try again with
                    # a different name.  However, remember this exception, in
                    # case we have run out of names and really do have to raise
                    # this exception.
                    last_exception = e
                    continue
                else:
                    # Some other error occurred - raise the exception
                    # immediately.
                    raise

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

        LOG.debug('leave: _create_vdisk: volume %(name)s ID %(id)s ' %
                  {'name': name, 'id': vdisk_id})

        return vdisk_id, name

    def _make_fc_map(self, source_vdisk_id, target_vdisk_id, full_copy):
        fc_map_cli_cmd = ['svctask', 'mkfcmap', '-source', source_vdisk_id,
                          '-target', target_vdisk_id, '-autodelete']
        if not full_copy:
            fc_map_cli_cmd.extend(['-copyrate', '0'])
        try:
            out, err = self._run_ssh(fc_map_cli_cmd)
        except processutils.ProcessExecutionError as e:
            if "CMMVC6425E" in e.stderr:
                # Maximum flashcopy limit reached, can't create more.
                # Raise an SVCException so we can present it nicely to the user
                raise paxes_exception.SVCFCMapsException(self.endpoint_desc)
            else:
                raise

        self._driver_assert(
            len(out.strip()),
            _('create FC mapping from %(source)s to %(target)s - '
              'did not find success message in CLI output.\n'
              ' stdout: %(out)s\n stderr: %(err)s\n')
            % {'source': source_vdisk_id,
               'target': target_vdisk_id,
               'out': str(out),
               'err': str(err)})

        # Ensure that the output is as expected
        match_obj = re.search('FlashCopy Mapping, id \[([0-9]+)\], '
                              'successfully created', out)
        # Make sure we got a "successfully created" message with vdisk id
        self._driver_assert(
            match_obj is not None,
            _('create FC mapping from %(source)s to %(target)s - '
              'did not find success message in CLI output.\n'
              ' stdout: %(out)s\n stderr: %(err)s\n')
            % {'source': source_vdisk_id,
               'target': target_vdisk_id,
               'out': str(out),
               'err': str(err)})

        try:
            fc_map_id = match_obj.group(1)
            self._driver_assert(
                fc_map_id is not None,
                _('create FC mapping from %(source)s to %(target)s - '
                  'did not find mapping id in CLI output.\n'
                  ' stdout: %(out)s\n stderr: %(err)s\n')
                % {'source': source_vdisk_id,
                   'target': target_vdisk_id,
                   'out': str(out),
                   'err': str(err)})
        except IndexError:
            self._driver_assert(
                False,
                _('create FC mapping from %(source)s to %(target)s - '
                  'did not find mapping id in CLI output.\n'
                  ' stdout: %(out)s\n stderr: %(err)s\n')
                % {'source': source_vdisk_id,
                   'target': target_vdisk_id,
                   'out': str(out),
                   'err': str(err)})
        return fc_map_id

    def _call_prepare_fc_map(self, fc_map_id, source_vdisk_id,
                             target_vdisk_id):
        try:
            out, err = self._run_ssh(['svctask', 'prestartfcmap', fc_map_id])
        except processutils.ProcessExecutionError as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_('_prepare_fc_map: Failed to prepare FlashCopy '
                            'from %(source)s to %(target)s.\n'
                            'stdout: %(out)s\n stderr: %(err)s')
                          % {'source': source_vdisk_id,
                             'target': target_vdisk_id,
                             'out': e.stdout,
                             'err': e.stderr})

    def _prepare_fc_map(self, fc_map_id, source_vdisk_id, target_vdisk_id):
        self._call_prepare_fc_map(fc_map_id, source_vdisk_id, target_vdisk_id)
        mapping_ready = False
        wait_time = 5
        # Allow waiting of up to timeout (set as parameter)
        timeout = self.configuration.storwize_svc_flashcopy_timeout
        max_retries = (timeout / wait_time) + 1
        for try_number in range(1, max_retries):
            mapping_attrs = self._get_flashcopy_mapping_attributes(fc_map_id)
            if (mapping_attrs is None or
                    'status' not in mapping_attrs):
                break
            if mapping_attrs['status'] == 'prepared':
                mapping_ready = True
                break
            elif mapping_attrs['status'] == 'stopped':
                self._call_prepare_fc_map(fc_map_id, source_vdisk_id,
                                          target_vdisk_id)
            elif mapping_attrs['status'] != 'preparing':
                # Unexpected mapping status
                exception_msg = (_('Unexecpted mapping status %(status)s '
                                   'for mapping %(id)s. Attributes: '
                                   '%(attr)s')
                                 % {'status': mapping_attrs['status'],
                                    'id': fc_map_id,
                                    'attr': mapping_attrs})
                LOG.error(exception_msg)
                raise exception.VolumeBackendAPIException(data=exception_msg)
            # Need to wait for mapping to be prepared, wait a few seconds
            time.sleep(wait_time)

        if not mapping_ready:
            exception_msg = (_('Mapping %(id)s prepare failed to complete '
                               'within the allotted %(to)d seconds timeout. '
                               'Terminating.')
                             % {'id': fc_map_id,
                                'to': timeout})
            LOG.error(_('_prepare_fc_map: Failed to start FlashCopy '
                        'from %(source)s to %(target)s with '
                        'exception %(ex)s')
                      % {'source': source_vdisk_id,
                         'target': target_vdisk_id,
                         'ex': exception_msg})
            raise exception.InvalidSnapshot(
                reason=_('_prepare_fc_map: %s') % exception_msg)

    def _start_fc_map(self, fc_map_id, source_vdisk_id, target_vdisk_id):
        try:
            out, err = self._run_ssh(['svctask', 'startfcmap', fc_map_id])
        except processutils.ProcessExecutionError as e:
            with excutils.save_and_reraise_exception():
                LOG.error(_('_start_fc_map: Failed to start FlashCopy '
                            'from %(source)s to %(target)s.\n'
                            'stdout: %(out)s\n stderr: %(err)s')
                          % {'source': source_vdisk_id,
                             'target': target_vdisk_id,
                             'out': e.stdout,
                             'err': e.stderr})

    def _run_flashcopy(self, source_vdisk_id, target_vdisk_id, full_copy=True):
        """Create a FlashCopy mapping from the source to the target."""

        LOG.debug('enter: _run_flashcopy: execute FlashCopy from source '
                  '%(source)s to target %(target)s' %
                  {'source': source_vdisk_id, 'target': target_vdisk_id})

        fc_map_id = self._make_fc_map(source_vdisk_id, target_vdisk_id,
                                      full_copy)
        try:
            self._prepare_fc_map(fc_map_id, source_vdisk_id, target_vdisk_id)
            self._start_fc_map(fc_map_id, source_vdisk_id, target_vdisk_id)
        except Exception:
            with excutils.save_and_reraise_exception():
                self._delete_vdisk(target_vdisk_id, True)

        LOG.debug('leave: _run_flashcopy: FlashCopy started from '
                  '%(source)s to %(target)s' %
                  {'source': source_vdisk_id, 'target': target_vdisk_id})

    def _create_copy(self, src_vdisk_id, tgt_vdisk_names, full_copy, opts,
                     src_id, from_vol):
        """Create a new snapshot using FlashCopy."""

        tgt_vdisk_name_string = ', '.join(tgt_vdisk_names)
        LOG.debug('enter: _create_copy: snapshot with possible names '
                  '%(names)s from vdisk %(src_vdisk)s' %
                  {'names': tgt_vdisk_name_string,
                   'src_vdisk': src_vdisk_id})

        src_vdisk_attributes = self._get_vdisk_attributes(src_vdisk_id)
        if src_vdisk_attributes is None:
            exception_msg = (
                _('_create_copy: Source vdisk %s does not exist')
                % src_vdisk_id)
            LOG.error(exception_msg)
            if from_vol:
                raise paxes_exception.SVCVdiskNotFoundException(
                    self.endpoint_desc, src_id, vdisk_id=src_vdisk_id)
            else:
                raise exception.SnapshotNotFound(exception_msg,
                                                 snapshot_id=src_id)

        self._driver_assert(
            'capacity' in src_vdisk_attributes,
            _('_create_copy: cannot get source vdisk '
              '%(src)s capacity from vdisk attributes '
              '%(attr)s')
            % {'src': src_vdisk_id,
               'attr': src_vdisk_attributes})

        src_vdisk_size = src_vdisk_attributes['capacity']
        tgt_vdisk_id, tgt_vdisk_name = self._create_vdisk(tgt_vdisk_names,
                                                          src_vdisk_size, 'b',
                                                          opts)

        # Run the flashcopy.  If we fail to initiate (e.g. max out the number
        # of concurrent flashcopies, clean up.
        try:
            self._run_flashcopy(src_vdisk_id, tgt_vdisk_id, full_copy)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                self._delete_vdisk(tgt_vdisk_id, True)

        LOG.debug('leave: _create_copy: snapshot vdisk %(tgt_vdisk)s '
                  'from vdisk %(src_vdisk)s' %
                  {'tgt_vdisk': tgt_vdisk_id, 'src_vdisk': src_vdisk_id})

        return tgt_vdisk_id, tgt_vdisk_name

    def _get_flashcopy_mapping_attributes(self, fc_map_id):
        LOG.debug('enter: _get_flashcopy_mapping_attributes: mapping %s'
                  % fc_map_id)

        fc_ls_map_cmd = ['svcinfo', 'lsfcmap', '-delim', '!', fc_map_id]
        out, err = self._run_ssh(fc_ls_map_cmd)

        # Get list of FlashCopy mappings
        # We expect zero or one line if mapping does not exist,
        # two lines if it does exist, otherwise error
        lines = out.strip().split('\n')
        self._assert_ssh_return(lines[0] == ("id!" + fc_map_id),
                                '_get_flashcopy_mapping_attributes',
                                fc_ls_map_cmd, out, err)

        # since lambda function doesn't allow multiple statements,
        # create a helper function for map().
        def _helper_func(x):
            res = x.split('!')
            return (res[0], res[1])

        fcmaps = map(_helper_func, lines)
        attributes = dict(fcmaps)

        LOG.debug('leave: _get_flashcopy_mapping_attributes: mapping '
                  '%(fc_map_id)s, attributes %(attributes)s' %
                  {'fc_map_id': fc_map_id, 'attributes': attributes})

        return attributes

    def _is_vdisk_defined(self, vdisk_id):
        """Check if vdisk is defined."""
        LOG.debug('enter: _is_vdisk_defined: vdisk %s ' % vdisk_id)
        vdisk_attributes = self._get_vdisk_attributes(vdisk_id)
        LOG.debug('leave: _is_vdisk_defined: vdisk %(vdisk)s with %(str)s '
                  % {'vdisk': vdisk_id,
                     'str': vdisk_attributes is not None})
        if vdisk_attributes is None:
            return False
        else:
            return True

    def _ensure_vdisk_no_fc_mappings(self, vdisk_id, allow_snaps=True):
        """
        Call looping function with FixedIntervalLoopingCall so that it can
        loop as long as necessary without starving other threads.
        """

        timer = loopingcall.FixedIntervalLoopingCall(
            self._check_vdisk_fc_mappings, vdisk_id, allow_snaps
        )
        # Create a timer greenthread. The default volume service heart beat
        # is every 10 seconds. The flashcopy usually takes more than 2 hours
        # to finish. Don't set interval shorter than the heartbeat, otherwise
        # volume service heartbeat will not be serviced. The volume service
        # is running frmo greenpool.
        # The interval should be longer than the time takes to check
        # all the fcmaps and service heartbeat interval(10s). flashcopy
        # could run for hours. Do not check the fcmap status too frequently.
        ret = timer.start(interval=CONF.storwize_fcmap_poll_interval).wait()
        timer.stop()
        return ret

    def _check_vdisk_fc_mappings(self, vdisk_id, allow_snaps=True):
        # Ensure vdisk has no FlashCopy mappings
        mapping_ids = self._get_vdisk_fc_mappings(vdisk_id)
        wait_for_copy = False
        LOG.debug("_check_vdisk_fc_mappings")
        for map_id in mapping_ids:
            attrs = self._get_flashcopy_mapping_attributes(map_id)
            if not attrs:
                continue
            source_id = attrs['source_vdisk_id']
            target_id = attrs['target_vdisk_id']
            copy_rate = attrs['copy_rate']
            status = attrs['status']

            map_descriptor = _("%(map_id)s [vdisk %(src)s to vdisk %(tgt)s]") \
                % {'map_id': map_id,
                   'src': source_id,
                   'tgt': target_id}

            if copy_rate == '0':
                # Case #2: A vdisk that has snapshots
                if source_id == vdisk_id:
                    if not allow_snaps:
                        # fcmap exists due to snapshot. Return False
                        # to waiter.
                        raise loopingcall.LoopingCallDone(retvalue=False)
                    new_copy_rate = '50'
                    LOG.info(_("To delete vdisk %(vdisk_id)s, increasing "
                               "copyrate of flashcopy mapping %(map)s from 0 "
                               "to %(copyrate)s and waiting for completion.")
                             % {'vdisk_id': vdisk_id,
                                'map': map_id,
                                'copyrate': new_copy_rate
                                })

                    ssh_cmd = ['svctask', 'chfcmap', '-copyrate',
                               new_copy_rate, '-autodelete', 'on', map_id]
                    self._run_ssh(ssh_cmd)
                    wait_for_copy = True
                # Case #3: A snapshot
                else:
                    msg = (_('Vdisk %(id)s not involved in '
                             'mapping %(src)s -> %(tgt)s') %
                           {'id': vdisk_id, 'src': source_id,
                            'tgt': target_id})
                    self._driver_assert(target_id == vdisk_id, msg)
                    if status in ['copying', 'prepared']:
                        self._run_ssh(['svctask', 'stopfcmap', map_id])
                        LOG.info(_("To allow deletion of vdisk %(vdisk_id)s, "
                                   "flashcopy mapping %(map)s with status "
                                   "'%(status)s' was removed.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor,
                                    'status': status})
                        wait_for_copy = True
                    elif status in ['stopping', 'preparing']:
                        LOG.info(_("To allow deletion of vdisk %(vdisk_id)s, "
                                   "waiting for flashcopy mapping %(map)s "
                                   "with status '%(status)s' to complete.")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor,
                                    'status': status})
                        wait_for_copy = True
                    else:
                        self._run_ssh(['svctask', 'rmfcmap', '-force',
                                       map_id])
                        LOG.info(_("To allow deletion of vdisk %(vdisk_id)s, "
                                   "forcing removal of flashcopy mapping "
                                   "%(map)s with status '%(status)s'")
                                 % {'vdisk_id': vdisk_id,
                                    'map': map_descriptor,
                                    'status': status})
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
                elif status == 'idle_or_copied':
                    # Prepare failed
                    self._run_ssh(['svctask', 'rmfcmap', '-force', map_id])
                    LOG.info(_("To delete vdisk %(vdisk_id)s, flashcopy "
                               "mapping %(map)s with status 'idle_or_copied' "
                               "was removed.")
                             % {'vdisk_id': vdisk_id,
                                'map': map_descriptor})
                else:
                    LOG.info(_("To delete vdisk %(vdisk_id)s, waiting for "
                               "completion of flashcopy mapping %(map)s, "
                               "which is currently %(progress)s%% complete "
                               "and has status '%(status)s'.")
                             % {'vdisk_id': vdisk_id,
                                'map': map_descriptor,
                                'progress': attrs['progress'],
                                'status': status})
                    # process fcmap to speed up vdisk cleanup
                    wait_for_copy = self._prepare_fcmap_for_deletion(map_id,
                                                                     attrs)

        if not wait_for_copy or not len(mapping_ids):
            raise loopingcall.LoopingCallDone()
        else:
            # This will have _ensure_vdisk_no_fc_mappings() timer
            # to yeild CPU.to give other threads from greenpool a chance
            # to run.
            eventlet.greenthread.sleep(0.01)

    def _prepare_fcmap_for_deletion(self, map_id, map_attr):
        """ Helper function to process a fcmap to reduce the wait
        time on the dependent_mappings. This function should only
        be called from the clone path.
        :param map_id: The flashcopy mapping id to handle.
        :map_attr: The lsfcmap output that describes the fcmap attribute
        :return: True if caller needs to wait for fcmap progress
                 False if fcmap has been successfully stopped and removed
        """
        copyclean_rate = CONF.storwize_fcmap_delete_copy_clean_rate
        status = map_attr['status']
        copy_progress = map_attr['progress']
        copy_rate = map_attr['copy_rate']
        clean_rate = map_attr['clean_rate']
        dependent_mappings = map_attr['dependent_mappings']
        autodelete = True if map_attr['autodelete'] == 'on' else False

        if int(copy_rate) == 0:
            # this is the vdisk snapshot, shouldn't calling this
            # function. Return True.
            LOG.warn(_("Flashcopy mapping copy rate is 0. Copy is not"
                     " in progress. Return to caller."))
            return True

        if int(dependent_mappings) > 0:
            if status == 'copying':
                if int(copy_progress) < FCMAP_COPY_COMPLETE_PCT:
                    if int(copy_rate) < int(copyclean_rate):
                        self._run_ssh(['svctask', 'chfcmap',
                                       '-copyrate',
                                       copyclean_rate,
                                       '-cleanrate',
                                       copyclean_rate,
                                       '-autodelete', 'on', map_id])
                    return True
                else:
                    if int(clean_rate) < int(copyclean_rate):
                        # speed up clean up if possible and wait
                        self._run_ssh(['svctask', 'chfcmap',
                                       '-cleanrate',
                                       copyclean_rate,
                                       '-autodelete', 'on', map_id])
                    # start transition to stop state with proper clean rate
                    self._run_ssh(['svctask', 'stopfcmap', map_id])
                    return True
            elif status == 'stopping':
                if int(clean_rate) < int(copyclean_rate) or not autodelete:
                    self._run_ssh(['svctask', 'chfcmap',
                                   '-cleanrate',
                                   copyclean_rate,
                                   '-autodelete', 'on', map_id])
                # wait for fcmap to be cleaned up and deleted(by autodelete)
                return True
        else:
            if status in ['preparing', 'stopping']:
                # wait to transit to either prepared or stopped
                return True
            # fcmap has no dependencies, just remove it.
            elif status in ['copying', 'prepared']:
                self._run_ssh(['svctask', 'stopfcmap', '-force', map_id])
            self._run_ssh(['svctask', 'rmfcmap', '-force', map_id])
            return False

    def _delete_vdisk(self, vdisk_id, force):
        """Deletes existing vdisks.

        It is very important to properly take care of mappings before deleting
        the disk:
        1. If no mappings, then it was a vdisk, and can be deleted
        2. If it is the source of a flashcopy mapping and copy_rate is 0, then
           it is a vdisk that has a snapshot.  If the force flag is set,
           delete the mapping and the vdisk, otherwise set the mapping to
           copy and wait (this will allow users to delete vdisks that have
           snapshots if/when the upper layers allow it).
        3. If it is the target of a mapping and copy_rate is 0, it is a
           snapshot, and we should properly stop the mapping and delete.
        4. If it is the source/target of a mapping and copy_rate is not 0, it
           is a clone or vdisk created from a snapshot.  We wait for the copy
           to complete (the mapping will be autodeleted) and then delete the
           vdisk.

        """

        LOG.debug('enter: _delete_vdisk: vdisk %s' % vdisk_id)

        # Try to delete volume only if found on the storage
        vdisk_defined = self._is_vdisk_defined(vdisk_id)
        if not vdisk_defined:
            LOG.info(_('warning: Tried to delete vdisk %s but it does not '
                       'exist.') % vdisk_id)
            return

        self._ensure_vdisk_no_fc_mappings(vdisk_id)

        LOG.info(_("Removing vdisk %(vdisk_id)s")
                 % {'vdisk_id': vdisk_id})

        ssh_cmd = ['svctask', 'rmvdisk', '-force', vdisk_id]
        if not force:
            ssh_cmd.remove('-force')
        try:
            out, err = self._run_ssh(ssh_cmd)
        except Exception as e:
            with excutils.save_and_reraise_exception():
                # Dump the list of hosts currently using the vdisk
                ssh_cmd = ['lsvdiskhostmap', '-delim', ',', vdisk_id]
                out, err = self._run_ssh(ssh_cmd, attempts=2)
                LOG.info(_("Hosts mapped to vdisk %(vdisk)s:\n%(out)s") %
                         {'vdisk': vdisk_id, 'out': out})

                # Dump the complete list of flashcopy mappings
                ssh_cmd = ['lsfcmap']
                out, err = self._run_ssh(ssh_cmd, attempts=2)
                LOG.info(_("Existing FlashCopy mappings:\n%(out)s") %
                         {'out': out})

        # No output should be returned from rmvdisk
        self._assert_ssh_return(len(out.strip()) == 0,
                                ('_delete_vdisk %(id)s')
                                % {'id': vdisk_id},
                                ssh_cmd, out, err)
        LOG.debug('leave: _delete_vdisk: vdisk %s' % vdisk_id)

    def create_volume(self, volume):
        volume_type_id = volume.get('volume_type_id')
        if not volume_type_id:
            volume_type = volume_types.get_default_volume_type()
            if volume_type:
                volume_type_id = volume_type['id']
                volume['volume_type_id'] = volume_type_id
                #Update db to preserve volume_type
                LOG.info(_('adding volume_type_id to volume=%s') % volume)
                self.db.volume_update(self._context, volume['id'],
                                      {'volume_type_id': volume_type_id})
        opts = self._get_vdisk_params(volume_type_id)

        candidate_names = self._generate_candidate_names(volume)
        vdisk_id, name = self._create_vdisk(candidate_names,
                                            str(volume['size']), 'gb', opts)
        # Place the vdisk ID, name and UID into restricted metadata so that it
        # can be viewed by users and retrieved by this driver when it
        # subsequently performs operations on this volume.
        vdisk = self._get_vdisk_attributes(vdisk_id)
        self._update_restricted_metadata(volume['id'], vdisk)

        return None

    def delete_volume(self, volume):
        vdisk_id = self._incorporate_restricted_metadata(volume)

        # If there is no vdisk_id assigned then we probably failed during
        # creation.  Emit a message but do nothing.
        if vdisk_id is None:
            LOG.warn(_("Starting deletion of volume %(volume_id)s.  There is "
                       "no associated vdisk, so no operation will be "
                       "performed on the storage controller.") %
                     {'volume_id': volume['id']})
            return

        LOG.info(_("Starting deletion of volume %(volume_id)s, backed by "
                   "vdisk %(vdisk_id)s") %
                 {'volume_id': volume['id'],
                  'vdisk_id': vdisk_id})

        # Ensure that the UID matches and we don't delete the wrong disk,
        # raises exceptions if the UID doesn't match.
        try:
            self._verify_uid_by_vdisk_id(vdisk_id, volume)
        except paxes_exception.SVCVdiskMismatchException as e:
            # Volume has been deleted and recreated, probably in use by
            # someone else.  Do nothing, but warn.
            LOG.warn(_("delete_volume: vdisk mismatch: %(err)s. "
                       "Performing no operation on the storage controller")
                     % {'err': (_("%s") % e)})
            return
        except paxes_exception.SVCVdiskNotFoundException as e:
            # Volume has been deleted, do nothing, but warn.
            LOG.warn(_("delete_volume: vdisk deleted: %(err)s. "
                       "Performing no operation on the storage controller")
                     % {'err': (_("%s") % e)})
            return

        self._delete_vdisk(vdisk_id, False)

        return None

    def create_snapshot(self, snapshot):
        source_vol = self.db.volume_get(self._context, snapshot['volume_id'])
        src_vdisk_id = self._incorporate_restricted_metadata(source_vol)

        opts = self._get_vdisk_params(source_vol['volume_type_id'])

        tgt_vdisk_names = [snapshot['name']]
        vdisk_id = self._create_copy(src_vdisk_id=src_vdisk_id,
                                     tgt_vdisk_names=tgt_vdisk_names,
                                     full_copy=False,
                                     opts=opts,
                                     src_id=snapshot['volume_id'],
                                     from_vol=True)

        return None

    def delete_snapshot(self, snapshot):
        vdisk_id = self._get_vdisk_id_from_vdisk_name(snapshot['name'])

        # If the disk didn't exist for some reason, just return without trying
        # to initiate deletion.
        if vdisk_id is None:
            return

        self._delete_vdisk(vdisk_id, False)

    def create_volume_from_snapshot(self, volume, snapshot):
        if volume['size'] != snapshot['volume_size']:
            exception_message = (_('create_volume_from_snapshot: '
                                   'Source and destination size differ.'))
            raise exception.VolumeBackendAPIException(data=exception_message)

        volume_type_id = volume.get('volume_type_id')
        if not volume_type_id:
            volume_type = volume_types.get_default_volume_type()
            if volume_type:
                volume_type_id = volume_type['id']
                volume['volume_type_id'] = volume_type_id
                #Update db to preserve volume_type
                LOG.info(_('adding volume_type_id to volume=%s') % volume)
                self.db.volume_update(self._context, volume['id'],
                                      {'volume_type_id': volume_type_id})
        opts = self._get_vdisk_params(volume_type_id)
        src_vdisk_id = self._get_vdisk_id_from_vdisk_name(snapshot['name'])

        # If the snapshot vdisk doesn't exist for some reason, log error and
        # raise an exception
        if src_vdisk_id is None:
            exception_msg = (
                _('create_volume_from_snapshot: '
                  ' Source vdisk %s does not exist')
                % snapshot['name'])
            LOG.error(exception_msg)
            raise exception.VolumeNotFound(exception_msg,
                                           volume_id=snapshot['id'])

        # Generate a preference-ordered list of names for the new volume
        candidate_names = self._generate_candidate_names(volume)

        vdisk_id, name = self._create_copy(src_vdisk_id=src_vdisk_id,
                                           tgt_vdisk_names=candidate_names,
                                           full_copy=True,
                                           opts=opts,
                                           src_id=snapshot['id'],
                                           from_vol=False)

        # Place the vdisk ID, name and UID into restricted metadata so that it
        # can be viewed by users and retrieved by this driver when it
        # subsequently performs operations on this volume.
        vdisk = self._get_vdisk_attributes(vdisk_id)
        self._update_restricted_metadata(volume['id'], vdisk)

        return None

    def create_cloned_volume(self, tgt_volume, src_volume):
        if src_volume['size'] != tgt_volume['size']:
            exception_message = (_('create_cloned_volume: '
                                   'Source and destination size differ.'))
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)

        volume_type_id = tgt_volume.get('volume_type_id')
        if not volume_type_id:
            volume_type = volume_types.get_default_volume_type()
            if volume_type:
                volume_type_id = volume_type['id']
                tgt_volume['volume_type_id'] = volume_type_id
                #Update db to preserve volume_type
                LOG.info(_('adding volume_type_id to volume=%s') % tgt_volume)
                self.db.volume_update(self._context, tgt_volume['id'],
                                      {'volume_type_id': volume_type_id})
        opts = self._get_vdisk_params(volume_type_id)

        src_vdisk_id = self._incorporate_restricted_metadata(src_volume)

        # Ensure that the UID matches and we don't clone the wrong disk,
        # raise exception if the UID doesn't match.
        self._verify_uid_by_vdisk_id(src_vdisk_id, src_volume)

        candidate_names = self._generate_candidate_names(tgt_volume)

        vdisk_id, name = self._create_copy(src_vdisk_id=src_vdisk_id,
                                           tgt_vdisk_names=candidate_names,
                                           full_copy=True,
                                           opts=opts,
                                           src_id=src_volume['id'],
                                           from_vol=True)

        # Place the vdisk ID, name and UID into restricted metadata so that it
        # can be viewed by users and retrieved by this driver when it
        # subsequently performs operations on this volume.
        vdisk = self._get_vdisk_attributes(vdisk_id)
        self._update_restricted_metadata(tgt_volume['id'], vdisk)

        return None

    def extend_volume(self, volume, new_size):
        LOG.debug('enter: extend_volume: volume %s' % volume['id'])
        vdisk_id = self._incorporate_restricted_metadata(volume)

        # Ensure that the UID matches and we don't extend the wrong disk,
        # raise exception if the UID doesn't match.
        self._verify_uid_by_vdisk_id(vdisk_id, volume)

        ret = self._ensure_vdisk_no_fc_mappings(vdisk_id,
                                                allow_snaps=False)
        if not ret:
            exception_message = (_('extend_volume: Extending a volume with '
                                   'snapshots is not supported.'))
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)

        extend_amt = int(new_size) - volume['size']
        ssh_cmd = (['svctask', 'expandvdisksize', '-size', str(extend_amt),
                    '-unit', 'gb', vdisk_id])
        out, err = self._run_ssh(ssh_cmd)
        # No output should be returned from expandvdisksize
        self._assert_ssh_return(len(out.strip()) == 0, 'extend_volume',
                                ssh_cmd, out, err)
        LOG.debug('leave: extend_volume: volume %s' % volume['id'])

    def migrate_volume(self, ctxt, volume, host):
        """Migrate direclty if source and dest are managed by same storage.

        The method uses the migratevdisk method, which returns almost
        immediately, if the source and target pools have the same extent_size.
        Otherwise, it uses addvdiskcopy and rmvdiskcopy, which require waiting
        for the copy operation to complete.

        :param ctxt: Context
        :param volume: A dictionary describing the volume to migrate
        :param host: A dictionary describing the host to migrate to, where
                     host['host'] is its name, and host['capabilities'] is a
                     dictionary of its reported capabilities.
        """
        LOG.debug('enter: migrate_volume: id=%(id)s, host=%(host)s' %
                  {'id': volume['id'], 'host': host['host']})

        # Needs update to support vdisk IDs.
        raise NotImplementedError()

        false_ret = (False, None)
        if 'location_info' not in host['capabilities']:
            return false_ret
        info = host['capabilities']['location_info']
        try:
            (dest_type, dest_id, dest_pool) = info.split(':')
        except ValueError:
            return false_ret
        if (dest_type != 'StorwizeSVCDriver' or dest_id != self._system_id):
            return false_ret

        if 'extent_size' not in host['capabilities']:
            return false_ret
        if host['capabilities']['extent_size'] == self._extent_size:
            # If source and dest pools have the same extent size, migratevdisk
            ssh_cmd = ['svctask', 'migratevdisk', '-mdiskgrp', dest_pool,
                       '-vdisk', volume['name']]
            out, err = self._run_ssh(ssh_cmd)
            # No output should be returned from migratevdisk
            self._assert_ssh_return(len(out.strip()) == 0, 'migrate_volume',
                                    ssh_cmd, out, err)
        else:
            # If source and dest pool extent size differ, add/delete vdisk copy
            copy_info = self._get_vdisk_copy_info(volume['name'])
            copies = list(copy_info.keys())
            self._driver_assert(len(copies) == 1,
                                _('migrate_volume started with more than one '
                                  'vdisk copy'))
            orig_copy_id = copies[0]

            opts = self._get_vdisk_params(volume['volume_type_id'])
            params = self._get_vdisk_create_params(opts)
            ssh_cmd = (['svctask', 'addvdiskcopy'] + params + ['-mdiskgrp',
                       dest_pool, volume['name']])
            out, err = self._run_ssh(ssh_cmd)
            self._assert_ssh_return(len(out.strip()), 'migrate_volume',
                                    ssh_cmd, out, err)

            # Ensure that the output is as expected
            match_obj = re.search('Vdisk \[([0-9]+)\] copy \[([0-9]+)\] '
                                  'successfully created', out)
            # Make sure we got a "successfully created" message with copy id
            self._driver_assert(
                match_obj is not None,
                _('migrate_volume %(name)s - did not find '
                  'success message in CLI output.\n '
                  'stdout: %(out)s\n stderr: %(err)s')
                % {'name': volume['name'], 'out': str(out), 'err': str(err)})

            copy_id = match_obj.group(2)
            sync = False
            while not sync:
                ssh_cmd = ['svcinfo', 'lsvdiskcopy', '-delim', '!', '-copy',
                           copy_id, volume['name']]
                attrs = self._execute_command_and_parse_attributes(ssh_cmd)
                if not attrs:
                    msg = (_('migrate_volume: Could not get vdisk copy data'))
                    LOG.error(msg)
                    raise exception.VolumeBackendAPIException(data=msg)
                if attrs['sync'] == 'yes':
                    sync = True
                else:
                    time.sleep(5)

            ssh_cmd = ['svctask', 'rmvdiskcopy', '-copy', orig_copy_id,
                       volume['name']]
            out, err = self._run_ssh(ssh_cmd)
            # No output should be returned from rmvdiskcopy
            self._assert_ssh_return(len(out.strip()) == 0, 'migrate_volume',
                                    ssh_cmd, out, err)

        LOG.debug('leave: migrate_volume: id=%(id)s, host=%(host)s' %
                  {'id': volume['id'], 'host': host['host']})
        return (True, None)

    """====================================================================="""
    """ MISC/HELPERS                                                        """
    """====================================================================="""

    def get_volume_stats(self, refresh=False):
        """Get volume stats.

        If we haven't gotten stats yet or 'refresh' is True,
        run update the stats first.
        """
        if not self._stats or refresh:
            self._update_volume_stats()

        return self._stats

    def _update_volume_stats(self):
        """Retrieve stats info from volume group."""

        LOG.debug("Updating volume stats")
        data = {}

        data['vendor_name'] = 'IBM'
        data['driver_version'] = self.VERSION
        data['storage_protocol'] = list(self._enabled_protocols)

        data['total_capacity_gb'] = 0  # To be overwritten
        data['free_capacity_gb'] = 0   # To be overwritten
        data['reserved_percentage'] = self.configuration.reserved_percentage
        data['QoS_support'] = False

        pool = self.configuration.storwize_svc_volpool_name
        backend_name = self.configuration.safe_get('volume_backend_name')
        if not backend_name:
            underscored_pool = string.replace(pool, " ", "_")
            backend_name = '%s_%s' % (self._system_name, underscored_pool)
        data['volume_backend_name'] = backend_name

        ssh_cmd = ['svcinfo', 'lsmdiskgrp', '-bytes', '-delim', '!',
                   '"%s"' % pool]
        attributes = self._execute_command_and_parse_attributes(ssh_cmd)
        if not attributes:
            LOG.error(_('Could not get pool data from the storage'))
            exception_message = (_('_update_volume_stats: '
                                   'Could not get storage pool data'))
            raise exception.VolumeBackendAPIException(data=exception_message)

        data['total_capacity_gb'] = (float(attributes['capacity']) /
                                    (1024 ** 3))
        data['free_capacity_gb'] = (float(attributes['free_capacity']) /
                                    (1024 ** 3))
        data['easytier_support'] = attributes['easy_tier'] in ['on', 'auto']
        data['compression_support'] = self._compression_enabled
        data['extent_size'] = self._extent_size
        data['location_info'] = ('StorwizeSVCDriver:%(sys_id)s:%(pool)s' %
                                 {'sys_id': self._system_id,
                                  'pool': pool})

        data['default_volume_type'] = volume_types.get_default_volume_type()

        self._stats = data

    def _port_conf_generator(self, cmd):
        ssh_cmd = cmd + ['-delim', '!']
        out, err = self._run_ssh(ssh_cmd)

        if not len(out.strip()):
            return
        port_lines = out.strip().split('\n')
        if not len(port_lines):
            return

        header = port_lines.pop(0)
        yield header
        for portip_line in port_lines:
            try:
                port_data = self._get_hdr_dic(header, portip_line, '!')
            except exception.VolumeBackendAPIException:
                with excutils.save_and_reraise_exception():
                    self._log_cli_output_error('_port_conf_generator',
                                               ssh_cmd, out, err)
            yield port_data

    def _get_vdisk_copy_info(self, vdisk):
        ssh_cmd = ['svcinfo', 'lsvdiskcopy', '-delim', '!', vdisk]
        out, err = self._run_ssh(ssh_cmd)

        self._assert_ssh_return(len(out.strip()), '_get_vdisk_copy_info',
                                ssh_cmd, out, err)
        copy_lines = out.strip().split('\n')
        self._assert_ssh_return(len(copy_lines), '_get_vdisk_copy_info',
                                ssh_cmd, out, err)

        header = copy_lines.pop(0)
        ret = {}
        for copy_line in copy_lines:
            try:
                copy_data = self._get_hdr_dic(header, copy_line, '!')
            except exception.VolumeBackendAPIException:
                with excutils.save_and_reraise_exception():
                    self._log_cli_output_error('_get_vdisk_copy_info',
                                               ssh_cmd, out, err)
            ret[copy_data['copy_id']] = copy_data
        return ret

    def _get_vdisk_create_params(self, opts):
        easytier = 'on' if opts['easytier'] else 'off'

        # Set space-efficient options
        if opts['rsize'] == -1:
            params = []
        else:
            params = ['-rsize', '%s%%' % str(opts['rsize']),
                      '-autoexpand', '-warning',
                      '%s%%' % str(opts['warning'])]
            if not opts['autoexpand']:
                params.remove('-autoexpand')

            if opts['compression']:
                params.append('-compressed')
            else:
                params.extend(['-grainsize', str(opts['grainsize'])])

        params.extend(['-easytier', easytier])
        return params

    def _check_vdisk_opts(self, opts):
        # Check that rsize is either -1 or between 0 and 100
        if not (opts['rsize'] >= -1 and opts['rsize'] <= 100):
            raise exception.InvalidInput(
                reason=_('Illegal value specified for storwize_svc_vol_rsize: '
                         'set to either a percentage (0-100) or -1'))

        # Check that warning is either -1 or between 0 and 100
        if not (opts['warning'] >= -1 and opts['warning'] <= 100):
            raise exception.InvalidInput(
                reason=_('Illegal value specified for '
                         'storwize_svc_vol_warning: '
                         'set to a percentage (0-100)'))

        # Check that grainsize is 32/64/128/256
        if opts['grainsize'] not in [32, 64, 128, 256]:
            raise exception.InvalidInput(
                reason=_('Illegal value specified for '
                         'storwize_svc_vol_grainsize: set to either '
                         '32, 64, 128, or 256'))

        # Check that compression is supported
        if opts['compression'] and not self._compression_enabled:
            raise exception.InvalidInput(
                reason=_('System does not support compression'))

        # Check that rsize is set if compression is set
        if opts['compression'] and opts['rsize'] == -1:
            raise exception.InvalidInput(
                reason=_('If compression is set to True, rsize must '
                         'also be set (not equal to -1)'))

        # Check that the requested protocol is enabled
        if opts['protocol'] not in self._enabled_protocols:
            raise exception.InvalidInput(
                reason=_('Illegal value %(prot)s specified for '
                         'storwize_svc_connection_protocol: '
                         'valid values are %(enabled)s')
                % {'prot': opts['protocol'],
                   'enabled': ','.join(self._enabled_protocols)})

        if opts['iogrp'] not in self._available_iogrps:
            raise exception.InvalidInput(
                reason=_('I/O group %(iogrp)d is not valid; available '
                         'I/O groups are %(avail)s')
                % {'iogrp': opts['iogrp'],
                   'avail': ''.join(str(e) for e in self._available_iogrps)})

    def _execute_command_and_parse_attributes(self, ssh_cmd):
        """Execute command on the Storwize/SVC and parse attributes.

        Exception is raised if the information from the system
        can not be obtained.

        'None' is returned if the object cannot be found.
        """

        LOG.debug('enter: _execute_command_and_parse_attributes: '
                  ' command %s' % str(ssh_cmd))

        try:
            out, err = self._run_ssh(ssh_cmd)
        except processutils.ProcessExecutionError as e:
            if 'CMMVC5753E' in e.stderr:
                # CMMVC5753E: The specified object does not exist or is not a
                #             suitable candidate.
                return None
            else:
                # something bad happened
                LOG.error(_('CLI Exception output:\n command: %(cmd)s\n '
                            'stdout: %(out)s\n stderr: %(err)s') %
                          {'cmd': ssh_cmd,
                           'out': e.stdout,
                           'err': e.stderr})
                raise

        self._assert_ssh_return(len(out),
                                '_execute_command_and_parse_attributes',
                                ssh_cmd, out, err)
        attributes = {}
        for attrib_line in out.split('\n'):
            # If '!' not found, return the string and two empty strings
            attrib_name, foo, attrib_value = attrib_line.partition('!')
            if attrib_name is not None and len(attrib_name.strip()):
                attributes[attrib_name] = attrib_value

        LOG.debug('leave: _execute_command_and_parse_attributes:\n'
                  'command: %(cmd)s\n'
                  'attributes: %(attr)s'
                  % {'cmd': str(ssh_cmd),
                     'attr': str(attributes)})

        return attributes

    def _get_hdr_dic(self, header, row, delim):
        """Return CLI row data as a dictionary indexed by names from header.
        string. The strings are converted to columns using the delimiter in
        delim.
        """

        attributes = header.split(delim)
        values = row.split(delim)
        self._driver_assert(
            len(values) ==
            len(attributes),
            _('_get_hdr_dic: attribute headers and values do not match.\n '
              'Headers: %(header)s\n Values: %(row)s')
            % {'header': str(header),
               'row': str(row)})
        dic = dict((a, v) for a, v in map(None, attributes, values))
        return dic

    def _log_cli_output_error(self, function, cmd, out, err):
        LOG.error(_('%(fun)s: Failed with unexpected CLI output.\n '
                    'Command: %(cmd)s\nstdout: %(out)s\nstderr: %(err)s\n')
                  % {'fun': function, 'cmd': cmd,
                     'out': str(out), 'err': str(err)})

    def _driver_assert(self, assert_condition, exception_message):
        """Internal assertion mechanism for CLI output."""
        if not assert_condition:
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)

    def _assert_ssh_return(self, test, fun, ssh_cmd, out, err):
        self._driver_assert(
            test,
            _('%(fun)s: Failed with unexpected CLI output.\n '
              'Command: %(cmd)s\n stdout: %(out)s\n stderr: %(err)s')
            % {'fun': fun,
               'cmd': ssh_cmd,
               'out': str(out),
               'err': str(err)})

    def _handle_keyerror(self, function, header):
        msg = (_('Did not find expected column in %(fun)s: %(hdr)s') %
               {'fun': function, 'hdr': header})
        LOG.error(msg)
        raise exception.VolumeBackendAPIException(
            data=msg)

    def _verify_uid_by_vdisk_id(self, vdisk_id, volume):
        """
        Wrapper for _verify_uid when vdisk attributes are not readily
        available - obtains the attributes and passes through.
        """
        attributes = self._get_vdisk_attributes(vdisk_id)

        # Raise an error if the vdisk doesn't exist
        if not attributes:
            raise paxes_exception.SVCVdiskNotFoundException(
                self.endpoint_desc, volume['id'], vdisk_id=vdisk_id)

        return self._verify_uid(attributes, volume)

    def _verify_uid(self, vdisk_attributes, volume):
        """
        Raises an exception if the UID in the passed-in vdisk_attributes is
        not the same at the UID that we have embedded in the restricted
        metadata of the volume.
        """
        expected_uid = \
            volume['restricted_metadata'][RESTRICTED_METADATA_VDISK_UID_KEY]

        current_uid = vdisk_attributes['vdisk_UID']

        if current_uid != expected_uid:
            raise paxes_exception.\
                SVCVdiskMismatchException(self.endpoint_desc,
                                          volume['id'],
                                          vdisk_id=vdisk_attributes['id'],
                                          expected_uid=expected_uid,
                                          current_uid=current_uid)


class CLIResponse(object):
    '''Parse SVC CLI output and generate iterable'''

    def __init__(self, raw, delim='!', with_header=True):
        super(CLIResponse, self).__init__()
        self.raw = raw
        self.delim = delim
        self.with_header = with_header
        self.result = self._parse()

    def select(self, *keys):
        for a in self.result:
            vs = []
            for k in keys:
                v = a.get(k, None)
                if isinstance(v, basestring):
                    v = [v]
                if isinstance(v, list):
                    vs.append(v)
            for item in zip(*vs):
                yield item

    def __getitem__(self, key):
        return self.result[key]

    def __iter__(self):
        for a in self.result:
            yield a

    def __len__(self):
        return len(self.result)

    def _parse(self):
        def get_reader(content, delim):
            for line in content.lstrip().splitlines():
                line = line.strip()
                if line:
                    yield line.split(delim)
                else:
                    yield []

        if isinstance(self.raw, basestring):
            stdout, stderr = self.raw, ''
        else:
            stdout, stderr = self.raw
        reader = get_reader(stdout, self.delim)
        result = []

        if self.with_header:
            hds = tuple()
            for row in reader:
                hds = row
                break
            for row in reader:
                cur = dict()
                for k, v in zip(hds, row):
                    CLIResponse.append_dict(cur, k, v)
                result.append(cur)
        else:
            cur = dict()
            for row in reader:
                if row:
                    CLIResponse.append_dict(cur, row[0], ' '.join(row[1:]))
                elif cur:  # start new section
                    result.append(cur)
                    cur = dict()
            if cur:
                result.append(cur)
        return result

    @staticmethod
    def append_dict(dict_, key, value):
        key, value = key.strip(), value.strip()
        obj = dict_.get(key, None)
        if obj is None:
            dict_[key] = value
        elif isinstance(obj, list):
            obj.append(value)
            dict_[key] = obj
        else:
            dict_[key] = [obj, value]
        return dict_
