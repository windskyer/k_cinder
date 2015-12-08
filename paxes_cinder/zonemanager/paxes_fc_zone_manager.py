# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================
"""
ZoneManager is responsible to manage access control using FC zoning
when zoning mode is set as 'fabric'.
ZoneManager provides interfaces to add connection and remove connection
for given initiator and target list associated with a FC volume attach and
detach operation.

This PowerVC implementation does not have a pluggable driver architecture.
It speaks directly to the Brocade backend library.

It maintains persistent connections to the fabrics, and performs operations
across fabrics in parallel using greenthreads.

It also changes the API used to add connections, by requiring the caller to
be explicit about which zones to create on which fabrics.  This results in
higher performance, because we don't have to query connectivity add the time
that connections are added.
"""

from oslo.config import cfg
from cinder.openstack.common import log as logging
from paxes_cinder import _
from cinder.openstack.common import lockutils
from cinder.openstack.common import local
from paxes_cinder import exception
from eventlet.greenpool import GreenPool
from paxes_cinder.zonemanager.drivers.brocade.brcd_fc_zone_client_cli \
    import BrcdFCZoneClientCLI
import re

LOG = logging.getLogger(__name__)

zone_manager_opts = [
    cfg.StrOpt('zoning_policy',
               default='initiator-target',
               help='Zoning policy configured by user'),
    cfg.BoolOpt('zone_activate',
                default=True,
                help="Indicates whether zone should be activated or not"),
    cfg.StrOpt('zone_name_prefix',
               default="paxes",
               help="A prefix to be used when naming zone"),
    cfg.StrOpt('fc_fabric_names',
               default='',
               help='FC Fabric names'),
]

CONF = cfg.CONF
CONF.register_opts(zone_manager_opts)


def get_formatted_wwn(wwn_str):
    """Utility API that formats WWN to insert ':'.
    """
    if (len(wwn_str) != 16):
        return wwn_str
    else:
        return ':'.join(
            [wwn_str[i:i + 2] for i in range(0, len(wwn_str), 2)])


class PowerVCZoneManager:
    fabrics = {}

    def __init__(self, configuration, overrides=None):
        """
        Here we register the configuration options and extract all the
        configuration data.

        We also establish connections to the fabrics for use in subsequent
        operations.

        This will raise a ZoneManagerParallel exception if anything goes wrong
        during the connection process.
        """
        self.conf = configuration
        self.conf.register_opts(zone_manager_opts)

        fabric_names = self.conf.fc_fabric_names.split(',')

        # Check for uniqueness of names
        if len(fabric_names) != len(set(fabric_names)):
            msg = _("Fabric names are not unique: %(fabric_names)s") % \
                {'fabric_names': ','.join(fabric_names)}
            raise exception.ZoneManagerMisconfig(reason=msg)

        # First we add all the configuration options that we expect, given
        # the list of fabric names
        fc_fabric_opts = []

        for fabric_name in fabric_names:
            fc_fabric_opts.append(cfg.StrOpt('fc_fabric_address_'
                                             + fabric_name,
                                             default='',
                                             help='Management IP'
                                             ' of fabric'))
            fc_fabric_opts.append(cfg.StrOpt('fc_fabric_user_'
                                             + fabric_name,
                                             default='',
                                             help='Fabric user ID'))
            fc_fabric_opts.append(cfg.StrOpt('fc_fabric_password_'
                                             + fabric_name,
                                             default='',
                                             secret=True,
                                             help='Password for user'))
            fc_fabric_opts.append(cfg.IntOpt('fc_fabric_port_'
                                             + fabric_name,
                                             default=22,
                                             help='Connecting port'))
            fc_fabric_opts.append(cfg.FloatOpt('fc_fabric_timeout_'
                                               + fabric_name,
                                               default=10.0,
                                               help='Connection timeout '
                                                    '(seconds)'))
            fc_fabric_opts.append(cfg.FloatOpt('fc_fabric_cmd_timeout_'
                                               + fabric_name,
                                               default=100.0,
                                               help='Command execution '
                                                    'timeout (seconds)'))
            fc_fabric_opts.append(cfg.StrOpt('fc_fabric_display_name_'
                                             + fabric_name,
                                             default="",
                                             help='Display name'))
            fc_fabric_opts.append(cfg.StrOpt('zoning_policy_'
                                             + fabric_name,
                                             default=self.conf.zoning_policy,
                                             help='overridden '
                                             'zoning policy'))
            fc_fabric_opts.append(cfg.BoolOpt('zone_activate_'
                                              + fabric_name,
                                              default=self.conf.zone_activate,
                                              help='overridden zoning '
                                              'activation state'))
            fc_fabric_opts.append(cfg.StrOpt('zone_name_prefix_'
                                             + fabric_name,
                                             default=
                                             self.conf.zone_name_prefix,
                                             help='overridden zone '
                                             'name prefix'))
            fc_fabric_opts.append(cfg.StrOpt('principal_switch_wwn_'
                                             + fabric_name,
                                             default=fabric_name,
                                             help='Principal switch '
                                             'WWN of the fabric'))
            fc_fabric_opts.append(cfg.IntOpt('fc_fabric_num_attempts_'
                                             + fabric_name,
                                             default=3,
                                             help='Number of attempts of '
                                             'an operation'))
            fc_fabric_opts.append(cfg.IntOpt('fc_fabric_min_retry_gap_'
                                             + fabric_name,
                                             default=10,
                                             help='Minimum time to wait '
                                             'before retrying a failed '
                                             'operation'))
            fc_fabric_opts.append(cfg.IntOpt('fc_fabric_max_retry_gap_'
                                             + fabric_name,
                                             default=20,
                                             help='Maximum time to wait '
                                             'before retrying a failed '
                                             'operation'))

        self.conf.append_config_values(fc_fabric_opts)

        # If running in a process without fabric CLI options passed, allow
        # those options to be given and set via the overrides param, which
        # is a list of (key, value) tuples.
        if overrides:
            for item in overrides:
                self.conf.local_conf.set_override(item[0], item[1])

        # Now we initialise a connection to the switch for each of the fabrics

        # This function is called in a GreenThread for each registered switch.
        def _do_connect(context, fabric_name):
            # Mark this thread as running the passed-in context, so that log
            # messages can be correlated.
            context.update_store()

            @lockutils.synchronized(fabric_name, 'fcfabric-', True)
            def _do_locked_connect(fabric_name):
                fabric_ip = self.conf.safe_get('fc_fabric_address_' +
                                               fabric_name)
                fabric_user = self.conf.safe_get('fc_fabric_user_' +
                                                 fabric_name)
                fabric_pwd = self.conf.safe_get('fc_fabric_password_' +
                                                fabric_name)
                fabric_port = self.conf.safe_get('fc_fabric_port_' +
                                                 fabric_name)
                fabric_timeout = self.conf.safe_get('fc_fabric_timeout_' +
                                                    fabric_name)
                fabric_cmd_timeout = \
                    self.conf.safe_get('fc_fabric_cmd_timeout_' +
                                       fabric_name)

                fabric_display_name = \
                    self.conf.safe_get('fc_fabric_display_name_' +
                                       fabric_name)

                fabric_num_retries = \
                    self.conf.safe_get('fc_fabric_num_attempts_' +
                                       fabric_name)

                fabric_min_retry_gap = \
                    self.conf.safe_get('fc_fabric_min_retry_gap_' +
                                       fabric_name)

                fabric_max_retry_gap = \
                    self.conf.safe_get('fc_fabric_max_retry_gap_' +
                                       fabric_name)

                descriptor = exception.FabricDescriptor(fabric_name,
                                                        fabric_display_name,
                                                        fabric_user,
                                                        fabric_ip,
                                                        fabric_port)

                conn = BrcdFCZoneClientCLI(fabric_ip, fabric_user,
                                           fabric_pwd, fabric_port,
                                           fabric_timeout,
                                           fabric_cmd_timeout,
                                           descriptor,
                                           fabric_num_retries,
                                           fabric_min_retry_gap,
                                           fabric_max_retry_gap)

                return conn

            return _do_locked_connect(fabric_name)

        # Start a GreenThread for each fabric that we will connect to and
        # initiate the connection in it.
        pool = GreenPool(size=len(fabric_names))

        # Obtain our current context so that we can make sure that our child
        # threads have the same context, so that we can correlate log messages
        # that they generate.
        context = getattr(local.store, 'context', None)

        threads = {}
        for fabric_name in fabric_names:
            thread = pool.spawn(_do_connect, context, fabric_name)
            threads[fabric_name] = thread

        # Collect the resulting connection objects.
        # The wait() will raise an exception if something went wrong.
        exceptions = []
        for fabric_name, thread in threads.iteritems():
            try:
                self.fabrics[fabric_name] = thread.wait()
                LOG.info(_("Connection established to fabric %(f_name)s") %
                         dict(f_name=fabric_name))
            except Exception as e:
                exceptions.append(e)

        # If any exceptions were raised, we throw an exception that
        # encapsulates them all.
        if exceptions:
            raise exception.ZoneManagerParallel(exceptions)

    def _parallel_execute(self, operation, *args):

        def _spawn(context, operation, fabric_name, conn, *args):
            # Inherit this thread's context from the parent
            context.update_store()

            @lockutils.synchronized(fabric_name, 'fcfabric-', True)
            def _locked_spawn(operation, fabric_name, conn, *args):
                return operation(fabric_name, conn, *args)

            return _locked_spawn(operation, fabric_name, conn, *args)

        """
        Perform an operation against all fabrics, consolidate the responses
        into a dictionary keyed on fabric name.
        """
        pool = GreenPool(size=len(self.fabrics))

        # Obtain our current context so that we can make sure that our child
        # threads have the same context, so that we can correlate log messages
        # that they generate.
        context = getattr(local.store, 'context', None)
        threads = {}
        for fabric_name, conn in self.fabrics.iteritems():
            thread = pool.spawn(_spawn, context, operation, fabric_name, conn,
                                *args)
            threads[fabric_name] = thread

        # Collect the responses.  This may raise exceptions when we call wait()
        # If they do, we collect them and raise a collective exception at the
        # end.
        responses = {}
        exceptions = []

        for fabric_name, thread in threads.iteritems():
            try:
                responses[fabric_name] = thread.wait()
            except Exception as e:
                """
                FabricExceptions can indicate that a backtrace is not required
                if they contain sufficient debug information themselves.
                """
                if (not isinstance(e, exception.FabricException) or
                   e.backtrace_needed):
                    LOG.exception(e)
                exceptions.append(e)

        # If any exceptions were raised, we throw an exception that
        # encapsulates them all.
        if exceptions:
            raise exception.ZoneManagerParallel(exceptions)

        return responses

    def close(self):
        """
        Initiate a parallel close operation on all of the registered fabrics.
        Silently suppress any exceptions that are thrown.
        """
        def _do_close(fabric_name, conn):
            try:
                conn.close_connection()
            except Exception:
                # Not worth reporting anything that went wrong, we're closing.
                pass

        self._parallel_execute(_do_close)

    def add_connection(self, host_name, fabric_initiator_target_map):
        """
        Add new zones to the fabrics.

        The host_name is used to build the zone names.

        The fabric_initiator_target_map is like this:
        { 'a':  { 'initiator_A': [ target_W, target_X ],
                  'initiator_B': [ target_W, target_X ]
                }
          'b':  { 'initiator_C': [ target_Y, target_Z ],
                  'initiator_D': [ target_Y, target_Z ]
                }
        }

        So there is an initiator->target map per fabric.  We process this
        request on all fabrics in parallel, passing each one the appropriate
        piece of this data structure.
        """

        # This is the function that is called for each fabric.
        def _do_add_connection(fabric_name, conn,
                               fabric_initiator_target_map):

            # We build up a list of zones and ensure that the WWPNs are in the
            # correct format.
            if fabric_name in fabric_initiator_target_map:
                it_map = fabric_initiator_target_map[fabric_name]

                zone_map = {}
                for initiator, targets in it_map.iteritems():
                    for target in targets:
                        zone_name = self.make_zone_name(host_name, initiator,
                                                        target)
                        zone_map[zone_name] = [get_formatted_wwn(initiator),
                                               get_formatted_wwn(target)]

                LOG.info(_("Zones to be created for %(fabric)s are "
                           "%(zones)r") % {'fabric': conn.exception_desc,
                                           'zones': zone_map})

                conn.add_zones(zone_map, self.conf.zone_activate)

        # Perform the operation in parallel across all fabrics
        return self._parallel_execute(_do_add_connection,
                                      fabric_initiator_target_map)

    def delete_connection(self, initiators):
        """
        Removes all the zones that were created with our prefix and contains
        one of our initiators.
        """
        def _do_delete_zones(fabric_name, conn, initiators):
            # We look in the zone list for zones containing precisely one of
            # the specified initiators and one other thing, and remove it.
            # The zone name must also use our prefix.

            initiator_set = set(initiators)
            zones_to_delete = []

            # Maps zone name to list of WWPNs.  WWPNs are in colon-expanded
            # format.
            zone_map = conn.get_active_zone_map()

            for zone_name, zone_wwpns in zone_map.iteritems():
                zone_set = set(zone_wwpns)
                if zone_name.startswith(self.conf.zone_name_prefix) \
                   and len(zone_set & initiator_set) == 1:
                    zones_to_delete.append(zone_name)

            if len(zones_to_delete) > 0:
                LOG.info(_("%(fabric_descriptor)s: deleting zones "
                           "%(zone_list)s") %
                         {'fabric_descriptor': conn.exception_desc,
                          'zone_list': ', '.join(zones_to_delete)}
                         )
                conn.delete_zones(zones_to_delete,
                                  self.conf.zone_activate)

        # Perform the operation in parallel across all fabrics
        return self._parallel_execute(_do_delete_zones, initiators)

    def get_san_context(self, wwn_lists):
        """
        SAN lookup for end devices.

        wwn_lists is a dictionary of strings -> lists of WWPNs

        We pass this dictionary to every fabric, which returns the same
        dictionary, but only including the WWPNs that are present on the
        switch.

        We return a dictionary of fabric_name to filtered dictionary.

        e.g.

        ->   { 'initiators': [ A, B, C, D ],
               'targets': [ W, X, Y, Z ] }

        returns

            {
              'fabric_a': { 'initiators': [ A, B ],
                            'targets': [ W, X ] },
              'fabric_b': { 'initiators': [ C, D ],
                            'targets': [ Y, Z ] }
            }
        """
        def _do_get_san_context(fabric_name, conn, wwn_sets):
            nsinfo = conn.get_nameserver_info()
            LOG.info(_("Returned data from get_nameserver_info() is %(info)r")
                     % dict(info=nsinfo))
            nsset = set(nsinfo)

            found_wwns = {}
            for name, wwn_set in wwn_sets.iteritems():
                found_wwns[name] = list(nsset & wwn_set)

            return found_wwns

        # Convert the lists of WWPNs into sets to make it easier to find the
        # intersection with what is on the switches.
        wwn_sets = {}
        for name, wwpns in wwn_lists.iteritems():
            wwn_sets[name] = set(list(wwpns))

        return self._parallel_execute(_do_get_san_context, wwn_sets)

    def make_zone_name(self, host_name, initiator, target):
        # Maximum Brocade name length is 64 characters
        chars_remaining = 64 - len(self.conf.zone_name_prefix +
                                   initiator +
                                   target)

        trunc_host = host_name[-chars_remaining:]
        trunc_host = re.sub(r'[^a-zA-Z0-9_]', "_", trunc_host)
        return self.conf.zone_name_prefix + trunc_host + initiator + target
