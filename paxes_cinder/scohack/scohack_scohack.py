#
#
# All Rights Reserved.
# Copyright 2010 OpenStack Foundation
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

"""Storage backend for P R2 SCO image uploader"""

import time
import datetime
import json

from oslo.config import cfg

import cinder.openstack.common.log as logging
from cinder import exception
from cinder import volume as vol_api
from cinder.openstack.common import excutils
from cinder.openstack.common import lockutils

from paxes_cinder import _
from paxes_cinder.k2aclient.v1.k2uom import PhysicalFibreChannelAdapter
from paxes_cinder.volume import rpcapi_product as vol_rpcapi
from paxes_cinder.k2aclient import client
from paxes_cinder.db import api as paxes_db_api
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.v1.shell import K2Encoder

synchronized = lockutils.synchronized_with_prefix('scohack-')

LOG = logging.getLogger(__name__)


CONF = cfg.CONF
scohack_opts = [
    cfg.IntOpt('scohack_k2_timeout',
               default=60,
               help='K2 timeout for scohack.'),
    cfg.StrOpt('scohack_k2_excdir',
               default='/var/log/cinder/k2a-ffdc/scohack',
               help='Location of k2 ffdc files.')
]

CONF.register_opts(scohack_opts)


class StoreLocation(object):
    """Class describing a Scohack URI"""

    def __init__(self, store_specs):
        self.specs = store_specs
        if self.specs:
            self.process_specs()

    def process_specs(self):
        self.scheme = self.specs.get('scheme', 'scohack')
        self.volume_id = self.specs.get('volume_id')

    def get_uri(self):
        return "scohack://%s" % self.volume_id

    def parse_uri(self, uri):
        if not uri.startswith('scohack://'):
            reason = _("URI must start with scohack://")
            LOG.error(reason)
            msg = (_("BadStore: uri: >%(uri)s<, reason: >%(reason)s<") %
                   dict(uri=uri, reason=reason))
            raise Exception(msg)

        self.scheme = 'scohack'
        self.volume_id = uri[10:]


def _parse_scg_vios_id(k2aclient, scg_vios_id):

#     scg_vios_id = "789542X_066B1FB##1"

    if (len(scg_vios_id) != 18 or
            scg_vios_id[7] != "_"):
        msg = (_("x-scg-vios-id: >%(id)s< not of form 'ttttmmm_sssssssnnn'")
               % dict(id=scg_vios_id))
        raise ValueError(msg)

    (pt1, pt2) = scg_vios_id.split("_", 1)
    input_machine_type = pt1[:4]
    input_machine_model = pt1[-3:]
    input_serial_number = pt2[:-3]
    input_partition_id = str(int(pt2[-3:].replace("#", "0")))

    try:
        mss = k2aclient.managedsystem.list()
    except Exception as e:
        msg = (_("scohack: x-scg-vios-id: cant list ManagedSystem: >%(ex)s<")
               % dict(ex=e))
        raise Exception(msg)
    ms_found = None
    for ms in mss:
        machine_type = ms.machine_type_model_and_serial_number.machine_type
        model = ms.machine_type_model_and_serial_number.model
        serial_number = ms.machine_type_model_and_serial_number.serial_number
        if (input_machine_type == machine_type and
                input_machine_model == model and
                input_serial_number == serial_number):
            ms_found = ms
            break

    if ms_found is None:
        msg = (_("scohack: x-scg-vios-id: cant find ManagedSystem for: "
                 ">%(id)s<") % dict(id=scg_vios_id))
        raise Exception(msg)

    vios_found = None
    try:
        vioss = k2aclient.virtualioserver.list(ms_found.id)
    except Exception as e:
        msg = (_("scohack: x-scg-vios-id: cant list VirtualIoServer: "
                 ">%(ex)s<") % dict(ex=e))
        raise Exception(msg)

    for vios in vioss:
        if input_partition_id == vios.partition_id:
            vios_found = vios
            break

    if vios_found is None:
        msg = (_("scohack: x-scg-vios-id: cant find VirtualIOServer for: "
                 ">%(id)s<") % dict(id=scg_vios_id))
        raise Exception(msg)

    return (ms_found, vios_found)


def _get_vios(k2aclient, image_meta):

    scg_vios_id = image_meta.get("scg_vios_id")
    ms_id = image_meta.get("ms_id")
    vios_id = image_meta.get("vios_id")

    if scg_vios_id is not None:
        ms_vios = _parse_scg_vios_id(k2aclient, scg_vios_id)
        vios = ms_vios[1]
        image_meta["vios_id"] = vios.id

    elif ms_id is None and vios_id is None:
        try:
            vios_list = k2aclient.virtualioserver.listasroot()
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: cant list vios"))
        if len(vios_list) > 0:
            vios = vios_list[0]
            vios_id = vios.id
            image_meta["vios_id"] = vios_id
        else:
            msg = _("scohack: no vios found")
            LOG.error(msg)
            raise Exception(msg)

    elif ms_id is not None and vios_id is None:
        try:
            vios_list = k2aclient.virtualioserver.list(ms_id)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: cant list vios for ms: >%(id)s<")
                          % dict(id=ms_id))
        if len(vios_list) > 0:
            vios = vios_list[0]
            vios_id = vios.id
            image_meta["vios_id"] = vios_id
        else:
            msg = (_("scohack: no vios found for ms: >%(id)s<") %
                   dict(id=ms_id))
            LOG.error(msg)
            raise Exception(msg)

    elif ms_id is not None and vios_id is not None:
        # VIOS from ManagedSystem
        try:
            vios = k2aclient.virtualioserver.get(ms_id, vios_id)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: for ms: >%(mid)s<, "
                            "cant find vios: >%(vid)s<")
                          % dict(mid=ms_id, vid=vios_id))
    elif ms_id is None and vios_id is not None:
        # VIOS from root
        try:
            vios = k2aclient.virtualioserver.getasroot(vios_id)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: cant find vios: >%(vid)s<")
                          % dict(vid=vios_id))

    return vios


class Store(object):
    """Scohack backend store adapter."""
    EXAMPLE_URL = "scohack://volume-id"

    CHUNKSIZE = (16 * 1024 * 1024)  # 16M

    def __init__(self, context=None, location=None):
        """
        Initialize the Store
        """
        self.store_location_class = None
        self.context = context
        self.configure()
        self.volume_rpcapi = vol_rpcapi.VolumeAPIProduct()
        self.volume_api = vol_api.API()
        self._hmc_uuid = None
        self._k2aclient = None

    def configure(self):
        """
        Configure the Store to use the stored configuration options
        Any store that needs special configuration should implement
        this method.
        """
        pass

    def configure_add(self):
        """
        This is like `configure` except that it's specifically for
        configuring the store to accept objects.

        If the store was not able to successfully configure
        itself, it should raise `exception.BadStoreConfiguration`.
        """
        pass

    def get(self, location):
        """
        Takes a `scohack_location.Location` object that indicates
        where to find the image file, and returns a tuple of generator
        (for reading the image file) and image_size

        :param location `scohack_location.Location` object, supplied
                        from scohack_location.get_location_from_uri()
        """
        raise NotImplementedError

    def get_size(self, location):
        """
        Takes a `scohack_location.Location` object that indicates
        where to find the image file, and returns the size

        :param location `scohack_location.Location` object, supplied
                        from scohack_location.get_location_from_uri()
        """
        raise NotImplementedError

    def set_acls(self, location, public=False, read_tenants=[],
                 write_tenants=[]):
        """
        Sets the read and write access control list for an image in the
        backend store.

        :location `scohack_location.Location` object, supplied
                  from scohack_location.get_location_from_uri()
        :public A boolean indicating whether the image should be public.
        :read_tenants A list of tenant strings which should be granted
                      read access for an image.
        :write_tenants A list of tenant strings which should be granted
                      write access for an image.
        """
        raise NotImplementedError

    def get_schemes(self):
        return ('scohack',)

    def delete(self, location):
        """
        Takes a `scohack_location.Location` object that indicates
        where to find the image file to delete

        :location `scohack_location.Location` object, supplied
                  from scohack_location.get_location_from_uri()

        :raises NotFound if image does not exist
        :raises Forbidden if cannot delete because of permissions
        """
        raise NotImplementedError

    @staticmethod
    def _initk2client(hmc):
        """initialize a k2aclient using the specific HMC details """

        api_version = 1
        k2_url = hmc['access_ip']
        k2_username = hmc['user_id']
        k2_password = hmc['password']

        scohack_k2_timeout = CONF.scohack_k2_timeout
        scohack_k2_excdir = CONF.scohack_k2_excdir

        cs = client.Client(api_version,
                           k2_url,
                           k2_username,
                           k2_password,
                           timeout=scohack_k2_timeout,
                           excdir=scohack_k2_excdir)
        return cs

    def _getk2client(self, ctxt, hmc_uuid):
        """ create k2aclient for this volume driver instance """

        # check for first time
        if self._hmc_uuid is None:
            self._hmc_uuid = hmc_uuid

        # maybe relaxed in future versions
        if hmc_uuid != self._hmc_uuid:
            msg = (_("scohack: only single hmc is supported: "
                     "prev: >%(prev_id)s<, new: >%(new_id)s<")
                   % dict(prev_id=self._hmc_uuid,
                          new_id=hmc_uuid))
            raise Exception(msg)

        if self._k2aclient is not None:
            return self._k2aclient

        hmc = paxes_db_api.ibm_hmc_get_by_uuid(ctxt, hmc_uuid)
        if hmc is None:
            msg = (_("scohack: no HMC for id: >%(id)s<")
                   % dict(id=hmc_uuid))
            e = Exception(msg)
            e.scohack_httpcode = 400
            raise e

        self._k2aclient = self._initk2client(hmc)

        self._managementconsole = None
        try:
            self._managementconsole = \
                self._k2aclient.managementconsole.get(hmc_uuid)
        except Exception as e:
            msg = (_("scohack:"
                     " managemenconsole: >%(mc)s<"
                     " could not be retrieved,"
                     " hdisks will not be cleaned up,"
                     " msg: >%(msg)s<")
                   % dict(mc=hmc_uuid, msg=e))
            LOG.warning(msg)

        return self._k2aclient, self._managementconsole

    @synchronized('scohack_add')
    def add(self, image_file, image_meta, context):
        """
        Stores an image file with supplied identifier to the backend
        storage system and returns a tuple containing information
        about the stored image.

        :param image_file: The image data to write, as a file-like object
        :param image_meta: Image metadata

        :retval tuple of URL in backing store, bytes written, checksum
                and a dictionary with storage system specific information
        """

        hmc_id = image_meta.get("hmc_id")
        volume_id = image_meta.get("volume_id")

        k2aclient, managementconsole = self._getk2client(context, hmc_id)

        vios = _get_vios(k2aclient, image_meta)
        volume = self._get_volume(context, volume_id)
        msg = (_("scohack: vios: >%(vios)s<, volume: >%(vol)s<")
               % dict(vios=vios.id, vol=volume["id"]))
        LOG.info(msg)

        image_meta['vios_id'] = vios.id
        image_meta['volume_name'] = volume['display_name']

        connector = self._get_connector(vios)

        try:
            (hdisk_name, hdisk_uuid, vios) = self._discover_volume(
                context,
                k2aclient,
                vios,
                volume,
                connector)

            msg = (_("scohack: image upload: hdisk: >%(hdisk)s<, "
                     "vios: >%(vios)s<")
                   % dict(hdisk=hdisk_uuid, vios=vios.id))
            LOG.info(msg)

            self._upload(context, k2aclient, managementconsole,
                         image_meta, image_file, vios,
                         hdisk_name, hdisk_uuid)
        finally:
            self.volume_rpcapi.\
                terminate_connection(context, volume, connector)

    def _get_volume(self, context, volume_id):

        try:
            volume = self.volume_api.get(context, volume_id)
        except exception.NotFound:
            msg = (_("scohack: volume not found: >%(volume)s<")
                   % dict(volume=volume_id))
            LOG.error(msg)
            e = Exception(msg)
            e.scohack_httpcode = 400
            raise e

        try:
            self.volume_api.check_attach(context, volume)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: volume: invalid status: >%(status)s<")
                          % dict(status=volume['status']))
        return volume

    def _get_connector(self, vios):

        ports = []
        for slot in vios.partition_io_configuration.profile_io_slots.\
                profile_io_slot:
            adapter = slot.associated_io_slot.related_io_adapter
            if isinstance(adapter, PhysicalFibreChannelAdapter):
                for port in adapter.\
                        physical_fibre_channel_ports.\
                        physical_fibre_channel_port:
                    ports.append(port.wwpn)

        if len(ports) == 0:
            msg = (_("scohack: no ports for vios: >%(vios)s<")
                   % dict(vios=vios.id))
            LOG.error(msg)
            raise Exception(msg)

        connector = {'host': 'scohack', 'wwpns': ports}

        return connector

    def _discover_volume(self, context, k2aclient, vios, volume, connector):

        try:
            connection_info = self.volume_rpcapi.\
                initialize_connection(context, volume, connector)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.exception(_("scohack: failed to connect to volume "
                                ">%(volume_id)s< "),
                              {'volume_id': volume["id"]},
                              context=context)

        # validate connection
        if (connection_info is None
                or not 'data' in connection_info
                or not 'target_lun' in connection_info['data']
                or connection_info['data']['target_lun'] is None):
            msg = (_("scohack: for target volume: >%(volume)s<, "
                     "bad connection: >%(info)s<, "
                     "no target_lun")
                   % dict(volume=volume["id"], info=connection_info))
            LOG.error(msg)
            raise Exception(msg)

#         msg = _("scohack: for target volume: >%s<, connection: >%s<")
#         msg = msg % (volume["id"], connection_info,)
#         LOG.info(msg)

        lua = connection_info['data']['target_lun']
        lua += "000000000000"

        # extract wwpn
        if len(connection_info['data']['target_wwn']) == 0:
            msg = (_("scohack: for target volume: >%(volume)s<, "
                     "no target wwpn "
                     "found in connection: >%(info)s< ")
                   % dict(volume=volume["id"], info=connection_info))
            LOG.error(msg)
            raise Exception(msg)
        t_wwpn = connection_info['data']['target_wwn'][0]

        ports = connector.get('wwpns')

        itls = []
        for iwwpn in ports:
            itls.append((iwwpn, t_wwpn, lua))

        metadata = paxes_db_api.\
            volume_restricted_metadata_get(context, volume['id'])

        # obtain page 83
        if not 'scsi_inquiry_83' in metadata:
            msg = (_("scohack: target volume: >%(volume)s<, does "
                     "not have page83 data")
                   % dict(volume=volume["id"]))
            LOG.error(msg)
            raise Exception(msg)

        deviceid = metadata['scsi_inquiry_83']

        msg = (_("scohack: start luarecovery: deviceid: >%(id)s< , "
                 "itls: >%(itls)s<")
               % dict(id=deviceid, itls=itls))
        LOG.info(msg)

        vendor = "IBM"
        try:
            result = k2aclient.virtualioserver.\
                lua_recovery(vios, vendor, deviceid, itls)
        except Exception:
            with excutils.save_and_reraise_exception():
                LOG.error(_("scohack: lua_recovery job failed for "
                            "target volume: >%(volume)s<")
                          % dict(volume=volume["id"]))

        # note that luarecovery result is in form:
        #    (k2_job_status, version, [(status, pv_name, unique_id, job_id)])

        LOG.debug("scohack: luarecovery complete: result: >%s<", result)
        k2_job_status = result[0]
        lua_device_list = result[2]
        dev_name = None

        if k2_job_status != "COMPLETED_OK":
            LOG.warn(_("scohack: luarcovery job status: >%(status)s<, "
                       "result: >%(res)s<")
                     % dict(status=k2_job_status, res=result))

        if (lua_device_list is None or len(lua_device_list) == 0 or
                lua_device_list[0][0] is None):
            msg = (_("scohack: lua_recovery job internal error, "
                     "device_list is invalid "
                     "device list: >%(lua_list)s<")
                   % dict(lua_list=lua_device_list))
            LOG.error(msg)
            raise Exception(msg)

        if len(lua_device_list) > 1:
            msg = (_("scohack: lua_recovery job "
                     "returned multiple devices "
                     "device list: >%(lua_list)s<, will select first ...")
                   % dict(lua_list=lua_device_list))
            LOG.warning(msg)

        device = lua_device_list[0]
        device_status = device[0]

        if device_status == "1":
            msg = (_("This means that a device was found from an ITL nexus "
                     "and it was determined to be in use by the VIOS. The "
                     "most likely cause is that a virtual device was not "
                     "removed from a previous deploy. The VIOS took no action "
                     "in this case. device: >%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        elif device_status == "2":
            msg = (_("This means that the ITL nexus is not consider reliable "
                     "and some error occurred that prevents the VIOS from "
                     "determining making a decision on safely removing a "
                     "device. The VIOS took no action in this case. Perhaps "
                     "try to remove the offending hdisk from the VIOS, with "
                     "rmdev -d -l hdiskx. "
                     "device: >%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        elif device_status == "3":
            dev_name = device[1]
            msg = (_("This means the information provided and action taken by "
                     "the VIOS was sufficient to find the storage. "
                     "pvName, and uniqueID elements will follow in the "
                     "data stream. device: >%(dev)s<")
                   % dict(dev=device))
            LOG.debug(msg)

        elif device_status == "4":
            msg = (_("This means some new storage element was found at the "
                     "ITL nexus but VIOS could not determine if it is the "
                     "storage of interest to the management tool. "
                     "device: >%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        elif device_status == "5":
            msg = (_("The VIOS could not determine if this is logical unit "
                     "of interest to the management tool however did "
                     "find a device from the ITL nexus list. device: "
                     ">%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        elif device_status == "6":
            msg = (_("The VIOS could not find a device from the itl "
                     "nexus list. "
                     "It could be some SCSI or transport error occurred "
                     "during configuration or the ITL nexus list was "
                     "incorrect. "
                     "device: >%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        else:
            msg = (_("Unknown device status. "
                     "Severe internal error contact I. "
                     "device: >%(dev)s<")
                   % dict(dev=device))
            LOG.error(msg)
            raise Exception(msg)

        hdisk_uuid = None

        vios = k2aclient.virtualioserver.getasroot(vios.id)
        for volume in vios.physical_volumes.physical_volume:
            if volume.volume_name == dev_name:
                hdisk_name = dev_name
                hdisk_uuid = volume.unique_device_id

        if hdisk_uuid is None:
            msg = (_("scohack: failed to find device name: >%(dev)s<")
                   % dict(dev=dev_name))
            LOG.error(msg)
            raise Exception(msg)

        msg = (_("scohack: found device name: >%(dev)s<")
               % dict(dev=dev_name))
        LOG.info(msg)

        return hdisk_name, hdisk_uuid, vios

    def _upload(self, context, k2aclient, managementconsole,
                meta_data, flike,
                virtualioserver, hdisk_name, hdisk_uuid):

        if meta_data.get("size") > 0:
            sizeset = True
        # create the k2 web file
        try:
            webfile = k2web.File()
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
            webfile.filename = "IMGUPLOAD_" + st
            webfile.internet_media_type = 'application/octet-stream'
            if meta_data.get("checksum"):
                webfile.sha256 = meta_data["checksum"]
            else:
                msg = (_("scohack: hdisk_uuid: >%(hdisk)s<, "
                         "checksum not specified")
                       % dict(hdisk=hdisk_uuid))
                LOG.info(msg)
            if sizeset:
                webfile.expected_file_size_in_bytes = meta_data["size"]
            else:
                msg = (_("scohack: hdisk_uuid: >%(hdisk)s<, "
                         "size not specified")
                       % dict(hdisk=hdisk_uuid))
                LOG.info(msg)
            webfile.target_virtual_io_server_uuid = virtualioserver.id
            webfile.target_device_unique_device_id = hdisk_uuid
            webfile.file_enum_type = 'BROKERED_DISK_IMAGE'
            webfile = k2aclient.web_file.create(webfile)

            LOG.debug("scohack: begin image upload for hdisk_uuid: >%s<",
                      hdisk_uuid)

            start = time.time()
            webfile.upload(flike)
            webfile = k2aclient.web_file.get(webfile.id)
            upload_time = time.time() - start

            fsize = webfile.current_file_size_in_bytes
            giga = float(fsize) / 1024. / 1024. / 1024.
            minu = float(upload_time) / 60.0
            rate = minu / giga

            msg = (_("scohack: image upload complete for hdisk_uuid: "
                     ">%(hdisk)s<, "
                     "webfile id: >%(wid)s<, "
                     "actual size: >%(size)s< bytes, "
                     "elapsed time: >%(time)d< seconds, "
                     "rate: >%(rate)f< minutes/GB")
                   % dict(hdisk=hdisk_uuid,
                          wid=webfile.id,
                          size=fsize,
                          time=upload_time,
                          rate=rate))
            LOG.info(msg)

            if sizeset and int(webfile.expected_file_size_in_bytes) != \
                    int(webfile.current_file_size_in_bytes):
                raise Exception(_("scohack:  mismatch: "
                                "expected_file_size_in_bytes: >%e_size)d<, "
                                "current_file_size_in_bytes: >%(c_size)d<") %
                                dict(e_size=int(webfile.
                                                expected_file_size_in_bytes),
                                     c_size=int(webfile.
                                                current_file_size_in_bytes)))

            if not sizeset:
                meta_data["size"] = int(webfile.current_file_size_in_bytes)

            # clean up
            try:
                # delete webfile
                k2aclient.web_file.delete(webfile)

                # cleanup hdisk
                if managementconsole is not None:
                    ams = virtualioserver.associated_managed_system.split('/')
                    ams = ams[-1]
                    jresponse = k2aclient.managementconsole.run_vios_cmd(
                        managementconsole,
                        ams,
                        virtualioserver,
                        "rmdev -dev %s -ucfg" % (hdisk_name,))

                    if jresponse.status != "COMPLETED_OK":
                        response = json.dumps(
                            jresponse,
                            sort_keys=True,
                            cls=K2Encoder)
                        LOG.warn(_("scohack: "
                                   "cleanup failure for: "
                                   ">%(hdisk)s<, "
                                   "job status: "
                                   ">%(status)s<, "
                                   "response: >%(res)s< "
                                   "continuing ...")
                                 % dict(hdisk=hdisk_name,
                                        status=jresponse.status,
                                        res=response))

                else:
                    LOG.warn(_("scohack: for hdisk_uuid: >%(hdisk)s< "
                               " no managementconsole,"
                               " hisks will not be cleaned up")
                             % dict(hdisk=hdisk_uuid,))

            except Exception as e:
                LOG.warn(_("scohack: for hdisk_uuid: >%(hdisk)s< "
                           "cleanup failed, msg: >%(ex)s<")
                         % dict(hdisk=hdisk_uuid,
                                ex=e))

        except Exception:
            with excutils.save_and_reraise_exception():
                try:
                    k2aclient.web_file.delete(webfile)
                except Exception as e:
                    LOG.warn(_("scohack: for hdisk_uuid: >%(hdisk)s< "
                               "cleanup failed, msg: >%(ex)s<")
                             % dict(hdisk=hdisk_uuid,
                                    ex=e))
                LOG.error(_("scohack: upload failed for hdisk_uuid: >%(dsk)s<")
                          % dict(dsk=hdisk_uuid))

        return webfile
