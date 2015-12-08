#
#
# =================================================================
# =================================================================

import gettext
import os
import six

from paxes_cinder.k2aclient.openstack.common.gettextutils import Message
from paxes_cinder.k2aclient.openstack.common.gettextutils import USE_LAZY

#
# The following code overrides _ to retrieve translated messages from
# paxes_cinder message catalogs (default in /usr/share/locale/<locale>)
#
_localedir = os.environ.get('paxes_cinder'.upper() + '_LOCALEDIR')
_t = gettext.translation('paxes_cinder', localedir=_localedir, fallback=True)


def _(msg):
    if USE_LAZY:
        return Message(msg, domain='paxes_cinder')
    else:
        if six.PY3:
            return _t.gettext(msg)
        return _t.ugettext(msg)
