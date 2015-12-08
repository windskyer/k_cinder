#
#
# =================================================================
# =================================================================

from cinder import exception
from cinder.openstack.common import log as logging
import cinder.openstack.common.importutils
from paxes_cinder.db.sqlalchemy import api as pvc_db
from cinder.volume import api as base_api
from paxes_cinder.volume import rpcapi_product as volume_rpc
import inspect
from paxes_cinder import _

LOG = logging.getLogger(__name__)


def volume_create_decorator(name, fn):
    """ Decorator for cinder.volume.api.create(). It will patch the
    default volume create api to bypass the volume type check when
    source_volume's volume type doesn't match the volume type passed
    in. This is the monkey patch to address the volume clone issue
    introduced by community fix: # 1276787
    This patch can be removed once PowerVC switches to the retype and
    volume migration approach to handle the volume type change during
    volume clone.

        :param name: name of the function
        :param function: - object of the function
        :returns: function -- decorated function

    """
    def wrapped_func(*args, **kwarg):
        if fn.__name__ == 'create':
            LOG = logging.getLogger(fn.__module__)
            try:
                idx_svol = inspect.getargspec(fn).args.index("source_volume")
                idx_voltp = inspect.getargspec(fn).args.index("volume_type")
            except Exception as e:
                LOG.error(_("cinder volume_create interface has been changed. "
                            "PowerVC monkey patch for volume clone won't work."
                            " function: %(fx)s, arguments: %(args)s") %
                          dict(fx=fn.__module__,
                               args=inspect.getargspec(fn).args))
                raise e

            svol = kwarg.get('source_volume')
            voltp = kwarg.get('volume_type')

            if svol and voltp:
                if svol['volume_type_id'] != voltp['id']:
                    # this is the condition that will trigger the
                    # volume clone to fail. Patch it here.
                    svol['volume_type_id'] = voltp['id']
                    LOG.info(_("Monkey patched volume clone by paxes "
                               "volume_create_decorator(). Source Volume ID: "
                               "%(svol)s, volume type name: %(voltpnm)s, "
                               "volume type ID: %(voltpid)s") %
                             dict(svol=svol['id'],
                                  voltpnm=voltp['name'],
                                  voltpid=voltp['id']))
                    return fn(*args, **kwarg)

        return fn(*args, **kwarg)
    return wrapped_func


def volume_type_decorator(name, fn):
    """Decorator for cinder.volume.volume_types.create() which is called
    by utils.monkey_patch(). It will set the default quota for the
    created volume type.

        :param name: name of the function
        :param function: - object of the function
        :returns: function -- decorated function

    """
    def wrapped_func(*args, **kwarg):
        if fn.__name__ == 'create':
            # cinder.volume.volume_types.create() decorator
            r = fn(*args, **kwarg)
            LOG = logging.getLogger(fn.__module__)
            try:
                idx_specs = inspect.getargspec(fn).args.index('extra_specs')
                idx_name = inspect.getargspec(fn).args.index('name')
                idx_ctxt = inspect.getargspec(fn).args.index('context')
            except Exception as e:
                LOG.warn(_("Failed to get the parameters from function "
                           "cinder.volume.volume_types.create(). Default "
                           "quota didn't set for the storage template. "
                           "Error: %(err)s") % dict(err=e))
                # Just return. Don't set the storage template default quota.
                return r

            volume_type = args[idx_name]
            extra_specs = args[idx_specs]
            ctxt = args[idx_ctxt]
            volume_host = None
            if extra_specs and isinstance(extra_specs, dict):
                volume_host = extra_specs.get(
                    "capabilities:volume_backend_name", None)

            if volume_host and volume_type and ctxt:
                volume_rpcapi = volume_rpc.VolumeAPIProduct()
                try:
                    volume_rpcapi.set_volume_type_quota(
                        ctxt, volume_host, volume_type)
                    LOG.info(_("Successfully set default quota for storage "
                               "template %(vol_type)s") %
                             dict(vol_type=volume_type))
                except Exception as e:
                    LOG.warn(_("Failed to set default quota for storage "
                               "template %(vol_type)s, error: %(err)s") %
                             dict(vol_type=volume_type, err=e))
            else:
                LOG.warn(_("Cannot set default quota for storage template "
                           "%(vol_type)s due to invalid Parameters from volume "
                           "type create.") % dict(vol_type=volume_type))
            return r
        else:
            return fn(*args, **kwarg)
    return wrapped_func


def API(*args, **kwargs):
    importutils = cinder.openstack.common.importutils
    class_name = 'paxes_cinder.volume.rpcapi_product.VolumeAPIProduct'
    return importutils.import_object(class_name, *args, **kwargs)


def HostAPI(*args, **kwargs):
    importutils = cinder.openstack.common.importutils
    class_name = 'paxes_cinder.volume.rpcapi_product.VolumeAPIProduct'
    return importutils.import_object(class_name, *args, **kwargs)


def monkey_patch_get_all():
    """
    Patch the cinder.volume.api.API class get_all method
    in order to implement a new filter.  This new filter,
    'data_volumes' will filter out all boot volumes from the
    response.  This filter will be used for both the cinder
    volumes and volumes/detail API.  Code calls a db method
    which checks for the volume_metadata attribute
    is_boot_volume.
    If the 'data_volumes' filter is not used, the base cinder
    get_all api is called.
    """
    #maintain the original api
    cndr_base_api_get_all = base_api.API.get_all

    base_api.API.paxes_mod_get_all = \
        base_api.API.get_all

    def paxes_mod_get_all(self, context, marker=None,
                            limit=None,
                            sort_key='created_at',
                            sort_dir='desc',
                            filters={}):
        volumes = {}
        if ('data_volumes' in filters):
            try:
                volumes = pvc_db.ibm_volume_get_all_except_bootable(context)
            except exception.NotFound:
                #ignore this exception
                LOG.debug("No data volumes found.")
                pass
            except Exception as ex:
                LOG.error(_("Error getting data volumes: %s " % ex))
                raise ex
        else:
            volumes = cndr_base_api_get_all(self, context, marker,
                                            limit, sort_key, sort_dir,
                                            filters)
        return volumes

    base_api.API.get_all = \
        paxes_mod_get_all

monkey_patch_get_all()
