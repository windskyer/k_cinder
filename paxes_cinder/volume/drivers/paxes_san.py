# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright 2011 Justin Santa Barbara
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

import random
import time

from eventlet import greenthread
from oslo.config import cfg

from cinder import utils
from cinder.openstack.common import excutils
from cinder.openstack.common import log as logging
from paxes_cinder import _
from cinder.openstack.common import processutils
from cinder.volume.drivers.san import san as san

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

ssh_san_opts = [
    cfg.BoolOpt('development_ssh_san_conn',
                default=False,
                help='Controls whether or not the SSH Connections are dev or '
                     'production'),
    cfg.IntOpt('san_retry_min_delay', default=2,
               help="The minimum number of seconds to wait before retrying a"
                    "command"),
    cfg.IntOpt('san_retry_max_delay', default=10,
               help="The maximum number of seconds to wait before retrying a"
                    "command"),
]

CONF.register_opts(ssh_san_opts)


class PowerVCSSHPool(utils.SSHPool):
    """
    Override pools.Pool's put method, which is called after
    each iteration of "with self.sshpool.item()" in
    _run_ssh. If development_ssh_san_conn flag is True,
    the cinder.utils remove() method will be invoked
    to close the ssh connection after each time a
    connection is get().
    """
    def put(self, item):
        # do max_size check because SSHPool isn't calling remove in that case
        # like it should
        if CONF.development_ssh_san_conn or self.current_size > self.max_size:
            self.current_size -= 1
            self.remove(item)
        else:
            super(PowerVCSSHPool, self).put(item)


class PowerVCSanDriver(san.SanDriver):
    """
    An internal implementation of the San Driver from the OSEE community.
    In the development organization, we typically have several instances
    managing single hardware devices...and run out of SSH connections on the
    systems.

    This code provides a flag - 'development_ssh_san_conn' - and if set to
    true will close the ssh connection after every command.  This is slower
    but leads to higher usage of a single device across several PowerVC
    instances.

    Due to the performance benefits, this flag should be set to 'false' in
    a customer environment.
    """

    """
    For debug purposes, we maintain a map of SSH connection objects to
    information about the command that they are currently executing.
    """
    pending_ssh = {}

    def _run_ssh(self, cmd_list, check_exit_code=True, attempts=1):
        """
        override _run_ssh() method from san.SanDriver.
        It is important to set connection timeout to None
        if development_ssh_san_conn is enabled to close ssh
        connection per get(). Otherwise, keepalive without
        timeout on the ssh transport will cause the service
        greenthread to be stuck on the join during close()
        when put() is invoked.
        """
        if CONF.development_ssh_san_conn:
            LOG.debug("PowerVCSSHPool: close ssh connection after _run_ssh")
            timeout = None
            # periodic task and volume driver ssh execution may
            # be launched at the same time which could cause paramiko
            # authentication error due to the attempt to create
            # multiple paramiko ssh connection at the sametime.
            attempts = attempts if attempts > 3 else 3
        else:
            timeout = self.configuration.ssh_conn_timeout

        if not self.sshpool:
            password = self.configuration.san_password
            privatekey = self.configuration.san_private_key
            min_size = self.configuration.ssh_min_pool_conn
            max_size = self.configuration.ssh_max_pool_conn
            self.sshpool = PowerVCSSHPool(self.configuration.san_ip,
                                          self.configuration.san_ssh_port,
                                          timeout,
                                          self.configuration.san_login,
                                          password=password,
                                          privatekey=privatekey,
                                          min_size=min_size,
                                          max_size=max_size)

        utils.check_ssh_injection(cmd_list)
        command = ' '.join(cmd_list)

        last_exception = None
        pauses_between_attempts = 0
        try:
            while attempts > 0:
                attempts -= 1
                try:
                    with self.sshpool.item() as ssh:
                        # Record the command that we are about to execute,
                        # along with start time (in seconds)
                        self.pending_ssh[id(ssh)] = {'command': command,
                                                     'time': time.time()}
                        (out, err) = \
                            processutils.ssh_execute(ssh,
                                                     command,
                                                     check_exit_code=
                                                     check_exit_code)

                        # Remove the command from the list of commands we're
                        # executing.
                        del self.pending_ssh[id(ssh)]
                        return (out, err)
                except Exception as e:
                    LOG.info(e)
                    last_exception = e
                    if attempts > 0:
                        sleep_time = (random.randint(CONF.san_retry_min_delay,
                                                     CONF.san_retry_max_delay)
                                      + (pauses_between_attempts *
                                         CONF.san_retry_max_delay))
                        LOG.info(_("Waiting %(seconds)d seconds before next "
                                 "attempt...")
                                 % {'seconds': sleep_time})
                        greenthread.sleep(sleep_time)
                        pauses_between_attempts += 1
            try:
                raise processutils.ProcessExecutionError(
                    exit_code=last_exception.exit_code,
                    stdout=last_exception.stdout,
                    stderr=last_exception.stderr,
                    cmd=last_exception.cmd)
            except AttributeError:
                raise processutils.ProcessExecutionError(
                    exit_code=-1,
                    stdout="",
                    stderr="Error running SSH command",
                    cmd=command)

        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("Error running SSH command: %s") % command)
