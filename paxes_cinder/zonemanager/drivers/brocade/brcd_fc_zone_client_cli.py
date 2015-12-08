# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#    (c) Copyright 2013 Brocade Communications Systems Inc.
#    All Rights Reserved.
#    Copyright 2013 OpenStack LLC
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


import paramiko
import re
import time
import socket
import random
import functools
from eventlet import greenthread
from eventlet.timeout import Timeout
from cinder.openstack.common import excutils
from cinder.openstack.common import log as logging
from paxes_cinder import _

from paxes_cinder import exception

import paxes_cinder.zonemanager.drivers.brocade.fc_zone_constants \
    as ZoneConstant

"""
Script to push the zone configuration to brocade SAN switches
"""

LOG = logging.getLogger(__name__)
SSH_KNOWN_HOST_FILE = '/opt/paxes/data/known_hosts'


def retry(message):
    """
    This decorator calls the wrapped function via _retry_if_problems, to ensure
    that it is run multiple times if it fails, and catches the exceptions.
    Exceptions that aren't part of FabricException are wrapped up in
    FabricUnknownException objects that include a reference to the switch that
    raised the exception.

    The 'message' parameter is used to say something about what we are doing,
    so that exceptions can be made a little friendlier.
    """
    def inner(func):
        @functools.wraps(func)
        def wrapped(self, *args, **kwargs):
            try:
                return self._retry_if_problems(func, self, *args, **kwargs)
            except exception.FabricException:
                # Exception is already friendly, don't do anything
                raise
            except Exception as e:
                # Wrap the exception up with details of the failing fabric and
                # an indication of what we were doing.
                problem = _(message)
                LOG.exception(e)
                raise exception.FabricUnknownException(self.exception_desc,
                                                       problem, e)
        return wrapped
    return inner


class BrcdFCZoneClientCLI(object):
    switch_ip = '0.0.0.0'
    patrn = re.compile('[;\s]+')
    client = None

    def __init__(self, switch_ip, username, password, port, timeout,
                 cmd_timeout, descriptor, max_attempts, retry_min_gap,
                 retry_max_gap):
        """initializing the client."""

        # This data structure identifies the fabric when we raise exceptions
        self.exception_desc = descriptor
        self.max_attempts = max_attempts
        self.retry_min_gap = retry_min_gap
        self.retry_max_gap = retry_max_gap
        self.switch_ip = switch_ip
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.cmd_timeout = cmd_timeout

    def _initialise_connection(self):
        self.client = paramiko.SSHClient()
        self.client.load_host_keys(SSH_KNOWN_HOST_FILE)
        self.client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            self.client.connect(self.switch_ip, self.port, self.username,
                                self.password, timeout=self.timeout)
        except socket.timeout:
            # Connection timeout
            raise exception.FabricTimeoutException(self.exception_desc,
                                                   timeout=str(self.timeout))
        except paramiko.AuthenticationException:
            # Invalid username/password
            raise exception.FabricAuthException(self.exception_desc)
        except socket.gaierror as e:
            # Bad hostname/IP address
            raise exception.FabricConnectionException(self.exception_desc,
                                                      error=e.args[0],
                                                      detail=e.args[1])
        except Exception as e:
            # Catch everything else and raise the generic exception
            raise exception.FabricUnknownException(self.exception_desc,
                                                   _("Could not connect"),
                                                   e)
        self.debug(_("SSH Client created for %s"), self.exception_desc)

    def _ensure_connection(self):
        """
        Establishes a new connection to the switch if one is not already
        established.
        """
        if (not self.client or
           not self.client.get_transport() or
           not self.client.get_transport().is_authenticated()):
            self._initialise_connection()

    def warn(self, message, *args, **kwargs):
        """
        Wraps LOG.warn with context about the switch
        """
        LOG.warn("%(switch_info)s: %(message)s"
                 % {'switch_info': self.exception_desc,
                    'message': message}, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """
        Wraps LOG.error with context about the switch
        """
        LOG.error("%(switch_info)s: %(message)s"
                  % {'switch_info': self.exception_desc,
                     'message': message}, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """
        Wraps LOG.debug with context about the switch
        """
        LOG.debug("%(switch_info)s: %(message)s"
                  % {'switch_info': self.exception_desc,
                     'message': message}, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """
        Wraps LOG.info with context about the switch
        """
        LOG.info("%(switch_info)s: %(message)s"
                 % {'switch_info': self.exception_desc,
                    'message': message}, *args, **kwargs)

    def _get_active_zone_set(self):
        """Return the active zone configuration.

        Return active zoneset from fabric. When none of the configurations
        are active then it will return empty map.

        :returns: active zone set map
        """
        zoneSet = {}
        zone = {}
        zoneMember = ZoneConstant.EMPTY
        zoneSetName = ZoneConstant.EMPTY
        zoneName = ZoneConstant.EMPTY
        switchData = ''
        try:
            switchData = self._get_switch_data(
                ZoneConstant.GET_ACTIVE_ZONE_CFG)
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Failed getting active zone set "
                             "from %s"), self.exception_desc)
        try:
            for line in switchData:
                lineSplit = re.split('\\t', line)
                if len(lineSplit) > 2:
                    lineSplit = [x.replace(
                        '\n', ZoneConstant.EMPTY) for x in lineSplit]
                    lineSplit = [x.replace(
                        ZoneConstant.SPACE,
                        ZoneConstant.EMPTY) for x in lineSplit]
                    if ZoneConstant.CFG_ZONESET in lineSplit:
                        #ZoneSet
                        zoneSetName = lineSplit[1]
                        zoneSet[ZoneConstant.ACTIVE_ZONE_CONFIG] = zoneSetName
                        continue
                    if lineSplit[1]:
                        #Zone
                        zoneName = lineSplit[1]
                        zone[zoneName] = list()
                    if lineSplit[2]:
                        #ZoneMember
                        zoneMember = lineSplit[2]
                    if zoneMember:
                        #zonemember
                        zoneMemberList = zone.get(zoneName)
                        zoneMemberList.append(zoneMember)
            zoneSet[ZoneConstant.CFG_ZONES] = zone
        except Exception:
            """Incase of parsing error here, it should be malformed cli output
            """
            msg = _("Malformed zone configuration")
            raise exception.FCZoneDriverException(reason=msg)
            self.error(_("Failed getting active zone set from "
                         "fabric %s"), self.switch_ip)
        return zoneSet

    @retry("Could not obtain the name of the active zoneset")
    def get_active_zoneset_name(self):
        """Return the Active zoneset Name."""
        zoneSetCfg = self._get_active_zone_set()
        if ZoneConstant.ACTIVE_ZONE_CONFIG in zoneSetCfg:
            return zoneSetCfg[ZoneConstant.ACTIVE_ZONE_CONFIG]
        else:
            return ZoneConstant.EMPTY

    @retry("Could not obtain the list of existing zone names")
    def get_existing_zone_names(self):
        zoneSetCfg = self._get_active_zone_set()
        listOfActZones = zoneSetCfg[ZoneConstant.CFG_ZONES]
        return listOfActZones.keys()

    @retry("Could not obtain the list of active zones")
    def get_active_zone_map(self):
        """
        Returns a dictionary where keys are zone names and values are lists of
        WWPNs in that zone.  WWPNs are in the 'expanded' colon format.
        """
        zoneset = self._get_active_zone_set()
        return zoneset[ZoneConstant.CFG_ZONES]

    @retry("Could not add zones")
    def add_zones(self, zones, isActivate):
        """Add zone configuration

        This method will add the zone configuration passed by user.
            input params:
            zones -
            {   zonename1:[zonememeber1,zonemember2,...],
                zonename2:[zonemember1, zonemember2,...]...}
            isActivate - True/False
        """
        self.debug(_("Add Zones - Zones passed: %s"), zones)
        cfgName = ZoneConstant.EMPTY
        iteratorCount = 0
        zoneWithSep = ZoneConstant.EMPTY
        try:
            activeZoneMap = self.get_active_zone_map()
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Adding zone failed. Error in getting active "
                             "zone set from fabric %s"), self.switch_ip)
        for zoneName, zoneMembers in zones.iteritems():
            # if zone exists and had a different membership, its an update.
            # Delete & insert
            #TODO(sk): This need to change to an update call
            if zoneName in activeZoneMap:
                if set(activeZoneMap[zoneName]).issuperset(set(zoneMembers)):
                    # Zone is already defined and sufficient
                    self.info(_("Zone %(zoneName)s already contains required "
                                "members") % {'zoneName': zoneName})
                    continue
                else:
                    try:
                        self.delete_zones([zoneName], isActivate)
                        self.info(_("Deleted Zone before insert : %s"),
                                  zoneName)
                    except Exception:
                        with excutils.save_and_reraise_exception():
                            self.error(_("Deleting zone failed %s"), zoneName)
                            self._cfg_trans_abort()

            zoneMembersWithSep = ';'.join(str(member)
                                          for member in zoneMembers)
            cmd = '%s%s%s%s%s%s' % (ZoneConstant.ZONE_CREATE, " \"", zoneName,
                                    "\", \"",
                                    zoneMembersWithSep, "\"")
            self.debug(_("Adding zone, cmd to run %s"), cmd)
            try:
                status, msg = self.executecmd(cmd)
                if not status:
                    return (False, msg)
            except exception.FabricTransactionException:
                with excutils.save_and_reraise_exception():
                    self.error(_("Adding zone failed, cmd %s"), cmd)
            except Exception:
                with excutils.save_and_reraise_exception():
                    self.error(_("Adding zone failed, cmd %s"), cmd)
                    self._cfg_trans_abort()
            if(iteratorCount > 0):
                zoneWithSep += ';'
            iteratorCount += 1
            zoneWithSep += zoneName

        if iteratorCount == 0:
            self.info(_("No new zones created"))
        else:
            # We added at least one zone, need to update the configuration
            try:
                cfgName = self.get_active_zoneset_name()
                if(cfgName == ZoneConstant.EMPTY):
                    cfgName = ZoneConstant.OPENSTACK_CFG_NAME
                    status, cmd, output = self._cfg_add(
                        cfgName, zoneWithSep, ZoneConstant.ZONESET_CREATE)
                    if not status:
                        self.error(_("Zoneset create operation failed "
                                     "with output %s"), output)
                        self._cfg_trans_abort()
                        return (False, output)
                else:
                    status, cmd, output = self._cfg_add(
                        cfgName, zoneWithSep, ZoneConstant.CFG_ADD)
                    if not status:
                        self.error(_("cfgAdd operation failed : %s"), output)
                        self._cfg_trans_abort()
                        return (False, output)
                self._cfg_save()
                if isActivate:
                    self.activate_zoneset(cfgName)
            except exception.FabricTransactionException:
                with excutils.save_and_reraise_exception():
                    self.error(_("Adding zone failed, cmd %s"), cmd)
            except Exception:
                with excutils.save_and_reraise_exception():
                    self.error(_("Adding zone failed, cmd %s"), cmd)
                    self._cfg_trans_abort()
        self.info(_("Zoning completed"))
        return (True, ZoneConstant.SUCCESS)

    @retry("Could not activate zoneset")
    def activate_zoneset(self, cfgname):
        """Method to Activate the zone config. Param cfgname - ZonesetName."""
        self._execute_cmd(ZoneConstant.ACTIVATE_ZONESET + cfgname)
        return True

    @retry("Could not deactivate zoneset")
    def deactivate_zoneset(self):
        """Method to deActivate the zone config."""
        self._execute_cmd(ZoneConstant.DEACTIVATE_ZONESET)
        return True

    @retry("Could not delete zones")
    def delete_zones(self, zoneNames, isActivate):
        """ Delete zones from fabric.

        Method to delete the active zone config zones

        params zoneNames: list of zone names to delete
        params isActivate: True/False
        """
        activeZoneSetName = None

        try:
            activeZoneSetName = self.get_active_zoneset_name()
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Failed getting active zones from "
                             "fabric %s"), self.switch_ip)
        zoneString = ';'.join(zoneNames)
        cmd = ''
        try:
            cmd = '%s%s%s%s%s%s' % (ZoneConstant.CFG_REMOVE, "\"",
                                    activeZoneSetName, "\", \"",
                                    zoneString, "\"")
            status, msg = self.executecmd(cmd)
            if(status):
                for zone in zoneNames:
                    status, msg = self._zone_delete(zone)
                    if not status:
                        self._cfg_trans_abort()
                        return (False, msg)
            else:
                return (False, msg)
            if isActivate:
                self.activate_zoneset(activeZoneSetName)
                self._cfg_save()
        except exception.FabricTransactionException:
            with excutils.save_and_reraise_exception():
                self.error(_("Deleting zones failed, cmd %s"), cmd)
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Deleting zones failed, cmd %s"), cmd)
                self._cfg_trans_abort()
        return (True, ZoneConstant.SUCCESS)

    @retry("Could not retrieve details of logged-in ports")
    def get_nameserver_info(self):
        """ Get name server data from fabric.

        This method will return the connected node port wwn list(local
        and remote) for the given switch fabric
        """
        cliOutput = None
        try:
            cliOutput = self._get_switch_data(ZoneConstant.NS_SHOW)
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Failed collecting nsshow "
                             "info for fabric %s"), self.switch_ip)
        returnList = self._parse_ns_output(cliOutput)
        try:
            cliOutput = self._get_switch_data(ZoneConstant.NS_CAM_SHOW)
        except Exception:
            with excutils.save_and_reraise_exception():
                self.error(_("Failed collecting nscamshow "
                             "info for fabric %s"), self.switch_ip)
        returnList.extend(self._parse_ns_output(cliOutput))

        return returnList

    def _retry_if_problems(self, func, *args, **kwargs):
        """
        Executes a function with the specified arguments, retrying a specified
        number of times, pausing for a random time between attempts.

        In all exception cases, we shutdown and re-establish the SSH
        connection.  We log all issues as INFO messages and indicate that we
        will retry.

        Exceptions that are subclasses of FabricException can tell us that it
        is not worth retrying.
        """
        attempts = 0
        while attempts < self.max_attempts:
            attempts += 1
            try:
                self._ensure_connection()
                return func(*args, **kwargs)
            except Exception as e:
                # Doing str(e) on one of our fabric exceptions blows up with
                # 'UnicodeError: Message objects do not support str()...', so
                # case it out here for logging.
                if 'msg' in dir(e):
                    err = e.msg
                else:
                    err = _("%s") % e
                self.info(_("Problem: %(problem)s") % {'problem': err})

                # Ensure that the connection has been closed
                self.close_connection()

                # We retry if we've not hit the retry limit, and the exception
                # was either something that we don't understand, or a
                # FabricException that tells us that retrying is worthwhile.
                if attempts < self.max_attempts and \
                   (not isinstance(e, exception.FabricException) or
                        e.attempt_retry):
                    # We wait a random amount of time between the retry_min_gap
                    # and the retry_max_gap, plus retry_max_gap * (retries-1)
                    # so that the time between attempts increases
                    sleep_time = (random.randint(self.retry_min_gap,
                                                 self.retry_max_gap)
                                  + self.retry_max_gap * (attempts-1))

                    self.info(_("Will retry after %(seconds)s seconds...")
                              % {'seconds': sleep_time})
                    greenthread.sleep(seconds=sleep_time)
                    continue
                else:
                    # We either ran out of retries or we got an exception that
                    # was not worth retrying.
                    raise

    def close_connection(self):
        """This will close the client connection."""
        # Do nothing if there is no connection in existence.
        if self.client is None:
            return

        try:
            self.client.close()
        except Exception as e:
            # just log and move on.
            msg = _("Failed closing SSH connection %s") % e
            self.warn(msg)
        finally:
            self.client = None

    def _cfg_save(self):
        self._execute_cmd(ZoneConstant.CFG_SAVE)

    def _cfg_add(self, cfgName, zoneWithSep, cmd):
        cmd = '%s%s%s%s%s%s' % (cmd, "\"", cfgName, "\", \"", zoneWithSep,
                                "\"")
        status, msg = self.executecmd(cmd)
        if not status:
            return (False, cmd, msg)
        return (True, cmd, ZoneConstant.SUCCESS)

    def _execute_cmd(self, cmd):
        """ Execute cli with status update.

        Executes CLI commands such as cfgsave where status return is expected
        """
        with Timeout(self.cmd_timeout):
            try:
                self.info(_("running: '%s'") % cmd)
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdin.write("%s\n" % ZoneConstant.YES)

                # Wait for command completion.
                exit_status = stdout.channel.recv_exit_status()
                stdin.flush()

                data = stdout.read()
                self.debug(_("Returned data was %r") % data)
                stdin.close()
                stdout.close()
                stderr.close()
            except Timeout as timeout:
                # Close the connection so that nobody tries to re-used it.
                self.close_connection()
                desc = self.exception_desc
                raise exception.\
                    FabricCommandTimeoutException(desc,
                                                  timeout=self.cmd_timeout,
                                                  cmd=cmd)
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    msg = _("Error running command via ssh: %s") % e
                    self.error(msg)

    def _zone_delete(self, zonename):
        cmd = '%s%s%s%s' % (ZoneConstant.ZONE_DELETE, "\"", zonename, "\"")
        status, msg = self.executecmd(cmd)
        if not status:
            return (False, msg)
        return (True, ZoneConstant.SUCCESS)

    def _cfg_trans_abort(self):
        isAbortable = self._is_trans_abortable()
        if(isAbortable):
            cmd = ZoneConstant.CFG_ZONE_TRANS_ABORT
            status, msg = self.executecmd(cmd)
            if not status:
                return (False, msg)
        return (True, ZoneConstant.SUCCESS)

    def _is_trans_abortable(self):
        # If our connection is closed then our transaction has been aborted.
        if self.client is None:
            return False

        cmd = ZoneConstant.CFG_SHOW_TRANS
        with Timeout(self.cmd_timeout):
            try:
                self.info(_("running: '%s'") % cmd)
                stdin, stdout, stderr = self.client.exec_command(cmd)
                stdin.close()

                # Wait for command completion.
                exit_status = stdout.channel.recv_exit_status()

                output = stdout.readlines()
                isAbortable = False
                for line in output:
                    if(ZoneConstant.TRANS_ABORTABLE in line):
                        isAbortable = True
                        break
                stdout.close()
                stderr.close()
            except Timeout as timeout:
                # Close the connection so that nobody tries to re-use it.
                self.close_connection()
                desc = self.exception_desc
                raise exception.\
                    FabricCommandTimeoutException(desc,
                                                  timeout=self.cmd_timeout,
                                                  cmd=cmd)
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    msg = _("Error while checking zoning txn status: %s") % e
                    self.error(msg)
        return isAbortable

    def executecmd(self, cmd):
        """ Execute cli with no status update.

        Executes CLI commands such as addZone where status return is
        not expected
        """
        with Timeout(self.cmd_timeout):
            try:
                self.info(_("Executing: %s"), cmd)
                stdin, stdout, stderr = self.client.exec_command(cmd)
                output = stdout.readlines()
                stdin.close()
                stdout.close()
                stderr.close()
                if output:
                    res = output[0]
                    desc = self.exception_desc

                    self.error(_("CLI execution returned: %s"), output)
                    if "you are not the owner of that transaction" \
                       in output[0]:
                        raise exception.FabricTransactionException(desc,
                                                                   cmd=cmd)

                    if "Zone DB too large" in output[0]:
                        raise exception.FabricSizeExceededException(desc,
                                                                    cmd=cmd,
                                                                    res=res)

                    raise exception.FabricUnexpectedResponseException(desc,
                                                                      cmd=cmd,
                                                                      res=res)
            except Timeout as timeout:
                # Close the connection so that nobody tries to re-used it.
                self.close_connection()
                desc = self.exception_desc
                raise exception.\
                    FabricCommandTimeoutException(desc,
                                                  timeout=self.cmd_timeout,
                                                  cmd=cmd)
            except Exception as e:
                with excutils.save_and_reraise_exception():
                    msg = _("Error executing command '%(cmd)s': %(err)s") \
                        % {'cmd': cmd, 'err': _("%s") % e}
                    self.error(msg)

        return (True, ZoneConstant.SUCCESS)

    def _get_switch_data(self, cmd):
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdin.close()
            switchData = ''
            switchData = stdout.readlines()
            stdout.close()
            stderr.close()
        except Exception as e:
            with excutils.save_and_reraise_exception():
                msg = _("Failed when executing command '%(cmd)s': %(err)s") \
                    % {'cmd': cmd, 'err': _("%s") % e}
                self.error(msg)
        return switchData

    def _parse_ns_output(self, switchData):
        """Parses name server data.

        Parses nameserver raw data and adds the device port wwns to the list

        :return list of device port wwn from ns info
        """
        returnlist = []
        for line in switchData:
            if not(" NL " in line or " N " in line):
                continue
            linesplit = line.split(';')
            if len(linesplit) > 2:
                nodePortWwn = linesplit[2]
                returnlist.append(nodePortWwn)
            else:
                self.error(
                    _("Malformed nameserver output is: %s"), switchData)
                raise exception.InvalidParameterValue(
                    err=_("Malformed nameserver info"))
        return returnlist
