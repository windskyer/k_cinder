from cinder.openstack.common import log as logging
from cinder.openstack.common.scheduler import filters
from cinder.openstack.common.scheduler.filters import extra_specs_ops

LOG = logging.getLogger(__name__)


class StorageProtocolFilter(filters.BaseHostFilter):
    """StorageProtocol  filters based on volume host's storage protocol."""

    def _satisfies_metadata(self, host_stats, metadata):
        req = metadata.get('storage_protocol', None)
        if req is None:
            return True
        try:
            cap = host_stats.get('storage_protocol', None)
        except AttributeError:
            try:
                cap = host_stats.capabilities.get('storage_protocol', None)
            except AttributeError:
                return False
        if cap is None:
            return False
        if not extra_specs_ops.match(cap, req):
            LOG.debug(_("storage protocol requirement '%(req)s' does not match "
                        "'%(cap)s'"), {'req': req, 'cap': cap})
            return False
        return True

    def host_passes(self, host_state, filter_properties):
        """Return True if host has storage protocol eq metadata storage protocol."""
        metadata = filter_properties.get('metadata', None)    
        if metadata is None:
            return True

        if not self._satisfies_metadata(host_state, metadata):
            LOG.debug(_("%(host_state)s fails metadata strorage_protocol "
                      "requirements"), {'host_state': host_state})
            return False 
        return True
