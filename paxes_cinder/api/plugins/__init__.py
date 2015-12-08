#
#
# =================================================================
# =================================================================

from stevedore import extension
from cinder.api.contrib import standard_extensions
from cinder.openstack.common import log as logging
from paxes_cinder import _

LOG = logging.getLogger(__name__)


def api_extensions_v2(ext_mgr):
    """Factory to load all Cinder v2 API Extensions (P + Core)"""
    #First load all the standard extensions from the Cinder Contrib directory
    standard_extensions(ext_mgr)
    #Now we can load the P extensions specified in the Extension Point
    v2mgr = extension.ExtensionManager('cinder.api.v2.extensions')
    for ext in v2mgr.extensions:
        try:
            full_name = ext.plugin.__module__ + '.' + ext.plugin.__name__
            ext_mgr.load_extension(full_name)
        except Exception as ex:
            LOG.warn(_('Failed to load extension %(name)s: %(ex)s'),
                     dict(name=ext.name, ex=ex))
            LOG.exception(ex)
