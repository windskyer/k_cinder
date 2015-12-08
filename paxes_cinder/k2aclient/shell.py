#
#
# All Rights Reserved.
# Copyright 2011 OpenStack LLC.
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

"""
Command-line interface to k2.
"""

from __future__ import print_function

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient import exceptions as exc
from paxes_cinder.k2aclient.openstack.common import strutils
from paxes_cinder.k2aclient import utils
from paxes_cinder.k2aclient.v1 import shell as shell_v1

import argparse
import os
import sys
import logging
import logging.handlers

DEFAULT_K2A_API_VERSION = "1"

logger = logging.getLogger(__name__)


class K2aClientArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(K2aClientArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        #FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        msg = _("k2aclient:"
                " error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                " for more information.\n")
        msg = msg %\
            {'errmsg': message.split(choose_from)[0],
             'mainp': progparts[0],
             'subp': progparts[2]}
        self.exit(2, msg)


class OpenStackK2Shell(object):

    def __init__(self):

        self._log_varlog = None
        self._log_console = None

    def get_base_parser(self):
        parser = K2aClientArgumentParser(
            prog='k2a',
            description=__doc__.strip(),
            epilog=_('See "k2a help COMMAND" '
                     'for help on a specific command.'),
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
                            action='store_true',
                            help=argparse.SUPPRESS)

#   TODO :bh: add version that conform's w/ PowerVC
#        parser.add_argument('--version',
#                            action='version',
#                            version=client.__version__)

        parser.add_argument('--debug',
                            action='store_true',
                            default=utils.env('K2_DEBUG',
                                              default=False),
                            help=_('Print debugging output'))

        parser.add_argument('--api-version',
                            metavar='<api-ver>',
                            default=utils.env('K2A_API_VERSION',
                            default=DEFAULT_K2A_API_VERSION),
                            help=_('Accepts 1,defaults '
                                   'to env[K2A_API_VERSION].'))

        msg = _('Number of retries when attempting k2 operations.')
        parser.add_argument('--retries',
                            metavar='<retries>',
                            type=int,
                            default=0,
                            help=msg)

        parser.add_argument('--k2-url',
                            metavar='<k2-url>',
                            default=utils.env('K2_URL'),
                            help=_('url for k2 hmc, defaults '
                                   'to env[K2_URL].'))

        parser.add_argument('--k2-username',
                            metavar='<k2-username>',
                            default=utils.env('K2_USERNAME'),
                            help=_('k2 username, defaults '
                                   'to env[K2_USERNAME].'))

        parser.add_argument('--k2-password',
                            metavar='<k2-password>',
                            default=utils.env('K2_PASSWORD'),
                            help=_('k2 password, defaults '
                                   'to env[K2_PASSWORD].'))

        parser.add_argument('--k2-auditmemento',
                            metavar='<k2-auditmemento>',
                            default=utils.env('K2_AUDITMEMENTO',
                                              default='k2a'),
                            help=_('k2 auditmemento, defaults '
                                   'to, if set, env[K2_AUDITMEMENTO], '
                                   'otherwise to "k2a".'))

        parser.add_argument('--k2-certpath',
                            metavar='<k2-certpath>',
                            default=utils.env('K2_CERTPATH', default=None),
                            help=_('k2 certpath, defaults '
                                   'to, if set, env[K2_CERTPATH], '
                                   'otherwise to None.'))

        parser.add_argument('--logdir',
                            metavar='<logdir>',
                            default=utils.env('K2A_LOGDIR', default=None),
                            help=_('log directory, defaults '
                                   'to, if set, env[K2A_LOGDIR], '
                                   'otherwise to None. None turns'
                                   'off file logging'))

#         parser.add_argument('--excdir',
#                             metavar='<excdir>',
#                             default=utils.env('K2A_EXCDIR', default=None),
#                             help='directory where k2aexc subdirectory'
#                                  'will be placed'
#                                  'ie "<excdir>/k2aexc", '
#                                  'defaults '
#                                  'to, if set, env[K2A_EXCDIR], '
#                                  'otherwise to None. None turns'
#                                  'off exception logging')

        parser.add_argument('--excdir',
                            metavar='<excdir>',
                            default=utils.env('K2A_EXCDIR', default="/tmp"),
                            help=_('directory where k2aexc subdirectory'
                                   'will be placed'
                                   'ie "<excdir>/k2aexc", '
                                   'defaults '
                                   'to, if set, env[K2A_EXCDIR], '
                                   'otherwise to /tmp'))

        return parser

    def get_subcommand_parser(self, version):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        try:
            actions_module = {
                '1': shell_v1
            }[version]
        except KeyError:
            actions_module = shell_v1

        self._find_actions(subparsers, actions_module)
        self._find_actions(subparsers, self)

        self._add_bash_completion_subparser(subparsers)

        return parser

    def _add_bash_completion_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'bash_completion',
            add_help=False,
            formatter_class=OpenStackHelpFormatter)

        self.subcommands['bash_completion'] = subparser
        subparser.set_defaults(func=self.do_bash_completion)

    def _find_actions(self, subparsers, actions_module):
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            hlp = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            subparser = subparsers.add_parser(
                command,
                help=hlp,
                description=desc,
                add_help=False,
                formatter_class=OpenStackHelpFormatter)

            subparser.add_argument('-h', '--help',
                                   action='help',
                                   help=argparse.SUPPRESS,)

            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    def _setup_logging(self, loglevel, logdir=None):
        file_loglevel = loglevel
        console_loglevel = loglevel

        # consistent format
        lf = logging.Formatter
        logformatter = \
            lf('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        root_logger = logging.getLogger()

        # File logging
        if logdir is not None:
            logfn = "ibm-k2a.log"
            rfh = logging.handlers.RotatingFileHandler
            log_varlog = rfh(os.path.join(logdir, logfn),
                             maxBytes=5 * 1024 * 1024,
                             backupCount=5)
            log_varlog.setLevel(file_loglevel)
            log_varlog.setFormatter(logformatter)
            self._log_varlog = log_varlog
            root_logger.addHandler(log_varlog)

        # Console logging to STDERR
        log_console = logging.StreamHandler()
        log_console.setLevel(console_loglevel)
        log_console.setFormatter(logformatter)
        self._log_console = log_console
        root_logger.addHandler(log_console)

        root_logger.setLevel(logging.DEBUG)

    def main(self, argv):

        # Parse args once to find version and debug settings
        parser = self.get_base_parser()
        (options, _) = parser.parse_known_args(argv)

        ########
        # setup logging
        loglevel = logging.WARN
        if options.debug:
            loglevel = logging.DEBUG
        self._setup_logging(loglevel, logdir=options.logdir)

        subcommand_parser = self.get_subcommand_parser(
            options.api_version)
        self.parser = subcommand_parser

        if options.help or not argv:
            subcommand_parser.print_help()
            return 0

        args = subcommand_parser.parse_args(argv)

        # Short-circuit and deal with help right away.
        if args.func == self.do_help:
            self.do_help(args)
            return 0
        elif args.func == self.do_bash_completion:
            self.do_bash_completion(args)
            return 0

        (k2_url,
         k2_username,
         k2_password,
         k2_auditmemento,
         k2_certpath) = (args.k2_url,
                         args.k2_username,
                         args.k2_password,
                         args.k2_auditmemento,
                         args.k2_certpath)

        if not k2_url:
            raise exc.CommandError(
                _("k2aclient:"
                  " you must provide a url for a k2 hmc"
                  " via either --k2-url or env[K2_URL]"))

        if not k2_username:
            raise exc.CommandError(
                _("k2aclient:"
                  " you must provide a k2 username"
                  " via either --k2-username or env[K2_USERNAME]"))

        if not k2_password:
                raise exc.CommandError(
                    _("k2aclient:"
                      " you must provide a k2 password"
                      " via either --k2-password or via"
                      " env[K2_PASSWORD]"))

        self.cs = client.Client(options.api_version,
                                k2_url,
                                k2_username,
                                k2_password,
                                k2_auditmemento,
                                k2_certpath,
                                retries=options.retries,
                                excdir=options.excdir)

        args.func(self.cs, args)

    def do_bash_completion(self, args):
        """Print arguments for bash_completion.

        Prints all of the commands and options to stdout so that the
        cinder.bash_completion script doesn't have to hard code them.
        """
        commands = set()
        options = set()
        for sc_str, sc in self.subcommands.items():
            commands.add(sc_str)
            for option in sc._optionals._option_string_actions.keys():
                options.add(option)

        commands.remove('bash-completion')
        commands.remove('bash_completion')
        print (' '.join(commands | options))

    @utils.arg('command', metavar='<subcommand>', nargs='?',
               help=_('Display help for %s') % "<subcommand>")
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if args.command:
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                msg = _("k2aclient:"
                        ">%s< is not a valid subcommand")
                raise exc.CommandError(msg % args.command)
        else:
            self.parser.print_help()


# Somebody is picky about their shell help.
class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:],)
        super(OpenStackHelpFormatter, self).start_section(heading)


def main():
    rc = 0
    try:
        OpenStackK2Shell().main(map(strutils.safe_decode, sys.argv[1:]))
    except KeyboardInterrupt:
        msg = _("... terminating k2a client")
        print(msg, file=sys.stderr)
        rc = 130
    except Exception as e:
        logger.debug(e, exc_info=1)
        msg = _("ERROR: type: >%(type)s<, msg: >%(e)s<")
        print(msg % {"type": type(e), "e": e, }, file=sys.stderr,)
        rc = 1

    sys.exit(rc)

if __name__ == "__main__":
    main()
