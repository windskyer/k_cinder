# =================================================================
# =================================================================

import ConfigParser
from cinder.openstack.common import log as logging
from paxes_cinder import _
from cinder.volume.configuration import Configuration
from webob import exc
import six

from paxes_cinder.zonemanager import paxes_fc_zone_manager as fabmanager


LOG = logging.getLogger(__name__)


class MapInitiators():
    """
    Class for doing interfacing with the P_ZoneManager to do correlation
    with WWPN initiators that are plugged into the managed fabric(s).

    The use case for this class is the storage topology collection on the
    nova side. When FC ports are inventoried, the function in this module
    is used set the switch fabric designation on the port entry in the
    nova DB. Rather than extend the volume service with a new method that
    does not really belong there, this class will do the extra work needed
    of constructing the zone/fabric manager in the REST API flow. This
    allows the function to work independent of any storage providers being
    registered.
    """

    def __init__(self):
        """ Do configuration work. Construct the fabric manager """
        conf = self._load_fabric_opts()
        self.fabricmanager = None
        if conf:
            self.fabricmanager = fabmanager.PowerVCZoneManager(
                conf, overrides=self.opts)
            # import logging as g_logging
            # conf.local_conf.log_opt_values(LOG, g_logging.DEBUG)
            LOG.debug("P_ZoneManager initialized.")

    def get_wwpn_fabric_map(self, wwpn_list):
        """
        Given a list of WWPN initiators, return a dictionary mapping to
        the fabrics where the WWPN is logged into.

        :param wwpn_list: The list of wwpns. These strings should not be
                tokenized with colons (:).
                    Example:
                        [
                            "10000090FA2A5866",
                            "10000090FA2A8923",
                            "c0507606d56e03af"
                        ]
        :returns: A dictionary mapping of input wwpns to discovered fabric
                names. Example:
                        {
                            "10000090FA2A8923": "B",
                            "10000090FA2A5866": "A",
                            "c0507606d56e03af": None
                        }
        """
        if not self.fabricmanager:
            msg = _("Could not obtain a fabric manager client. Fibre "
                    "Channel switch fabrics may not be registered.")
            raise exc.HTTPInternalServerError(explanation=six.text_type(msg))

        # Add colons into input wwpns and put in a mapping dictionary.
        with_colons = dict([[fabmanager.get_formatted_wwn(w.lower()), w]
                            for w in wwpn_list])
        LOG.debug("ENTER get_wwpn_fabric_map: colon_map = %s" % with_colons)
        input_dict = {'initiators': with_colons.keys()}
        try:
            data = self.fabricmanager.get_san_context(input_dict)
        except Exception as ex:
            # The exception here may not be the root cause. If we cannot
            # get a normal response, then we raise our own error here.
            LOG.exception(ex)
            msg = (_("Unable to retrieve WWPN initiator information from "
                     "one or more fabric switches. Error: %(ex)s") %
                   dict(ex=ex))
            raise exc.HTTPInternalServerError(explanation=six.text_type(msg))
        LOG.debug("Zonemanager.get_san_context() returns: %s" % data)

        # Build a dictionary mapping of the original wwpn passed to the
        # result of the fabric lookup.
        map_dict = dict([[w, self._match_fabric(c, data)]
                         for c, w in with_colons.iteritems()])

        LOG.debug("RETURNS wwpn_mapping_dict: %s" % map_dict)
        return map_dict

    def _match_fabric(self, wwpn, fabricmanager_data):
        """ Helper to map the wwpn to a fabric returned in the passed data """
        for fabric, items in fabricmanager_data.iteritems():
            if wwpn in items['initiators']:
                # We upper case the fabric designator for API consumption.
                # e.g. 'a' --> 'A'
                return fabric.upper()
        return None

    def _load_fabric_opts(self):
        """
        We are not running in the volume service, so programmatically
        parse the fabrics.conf file and retrieve options that we care
        about so that fabric manager (a.k.a zone manager) can be
        initialized. Return a Configuration object with the fc_fabric_names
        property set. Return None if no fabrics are registered.
        """
        parser = ConfigParser.RawConfigParser()
        parser.read('/etc/cinder/fabrics.conf')
        if not parser.has_option('DEFAULT', 'fc_fabric_names'):
            LOG.info(_("No fabrics registered."))
            return None
        fabric_names = parser.get('DEFAULT', 'fc_fabric_names')
        fabric_names_list = fabric_names.split(',')
        if not fabric_names_list:
            LOG.info(_("No fabric names registered."))

        key_prefixes = ['fc_fabric_address_', 'fc_fabric_user_',
                        'fc_fabric_password_', 'fc_fabric_display_name_']
        key_prefixes_debug = ['fc_fabric_address_', 'fc_fabric_user_',
                              'fc_fabric_display_name_']
        options = []  # list of option tuples
        options_debug = []  # list of option tuples for debug
        # Loop over the fabric names (e.g. 'a', 'b')
        for fab in fabric_names_list:
            options.extend([(k + fab, parser.get('DEFAULT', k + fab))
                            for k in key_prefixes])
            options_debug.extend([(k + fab, parser.get('DEFAULT', k + fab))
                                  for k in key_prefixes_debug])

            # Instead of getting max attempts from the conf file, we
            # use an override here of 1 maximum attempt. We don't want
            # to keep trying for the default of 3 times, which will take
            # 30 or more seconds to timeout for a badly behaving switch.
            # The main use case for looking up wwpns comes from Nova's
            # host storage topology reconciliation periodic task and
            # the waiting of that task on the response here should be
            # minimized.
            options.append(('fc_fabric_num_attempts_' + fab, 1))
            options_debug.append(('fc_fabric_num_attempts_' + fab, 1))

        LOG.debug("Fabric options: %s" % options_debug)

        # Construct the empty configuration, then set the fabric names
        # to it, for use by the zone manager.
        conf = Configuration([])
        conf.local_conf.import_opt(
            'fc_fabric_names',
            'paxes_cinder.zonemanager.paxes_fc_zone_manager')
        conf.local_conf.fc_fabric_names = fabric_names
        self.opts = options
        return conf
