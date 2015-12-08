# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

from __future__ import print_function

from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.v1 import k2uom
# import xml.etree.ElementTree as ElementTree
# from xml.etree.ElementTree import Element
# from eventlet import greenthread

import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

import os
import hashlib

import json
import time


########
# upload stuff
def _sha256sum(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
        return sha256.hexdigest()


def _createtestfile(fspec='/tmp/testfile.txt',
                    size=1024 * 1024 * 1024 * 3):

    start = "start"
    end = "end"
    with open(fspec, 'wb') as f:
        f.write(start)
        f.seek(size - len(start) + 2)
        f.write(end)

    f.close()

#     statinfo = os.stat(fspec)  # statinfo.st_size

    size = os.path.getsize(fspec)
    sha256 = _sha256sum(fspec)
    print ("Created: >%s<, with size: >%d<, with sha256: >%s<" % (fspec,
                                                                  size,
                                                                  sha256,))

    return (fspec, size, sha256)


def _upload(cs, finfo, virtualioserver, hdisk_uuid):

#     (k2fspec, _) = os.path.splitext(os.path.split(fspec)[1])
#     k2fspec = k2fspec.replace("-", "_")

    (fspec, fsize, sha256) = finfo

    # create the k2 web file
    webfile = k2web.File()
    webfile.filename = "IMGUPLOAD_TEST"
    webfile.internet_media_type = 'application/octet-stream'
    if False:  # TODO
        print ("Xfer w/ sha256 check")
        webfile.sha256 = sha256
    else:
        print ("Xfer w/o sha256 check")
    webfile.expected_file_size_in_bytes = fsize
    webfile.target_virtual_io_server_uuid = virtualioserver
    webfile.target_device_unique_device_id = hdisk_uuid
    webfile.file_enum_type = 'BROKERED_DISK_IMAGE'

    webfile = cs.web_file.create(webfile)

    print ("to monitor: >./my_k2a web-file-show %s | "
           "grep file_size_in_bytes<" % (webfile.id,))

    # Upload file
    start = time.time()
    with open(fspec, 'rb') as flike:
        k2resp = webfile.upload(flike)
    upload_time = time.time() - start
    uploadexc = cs.exclogger.emit("UPLOAD", "k2_file_upload_brokered", k2resp)

    giga = float(fsize) / 1024. / 1024. / 1024.
    minu = float(upload_time) / 60.0
    rate = minu / giga
    webfile = cs.web_file.get(webfile.id)
    print ("upload complete: webfile id: >%s<, expected size: >%d< "
           "bytes, actual size: >%s< bytes, elapsed time: >%d< seconds, "
           "rate: >%f< minutes/GB, k2resp: >%s<" %
           (webfile.id, fsize, webfile.current_file_size_in_bytes,
            upload_time, rate, uploadexc))

    return webfile

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg(cfgfile="k2a.cfg")
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    cs = client.Client(k2acfg['api_version'],
                       k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    try:
        #########
        # Part one get nexus

        ####
        # target vios
        vios_id = "1BC0CB5E-15BF-492A-8D06-25B69833B54E"
        vios = cs.virtualioserver.getasroot(vios_id)

#         ####
#         # vios from list
#         vios_list = cs.virtualioserver.listasroot()
#         #vios = cs.virtualioserver.getasroot(vios_id)
#         #vios = vios_list[0]
#         for vios in vios_list:
#             print (vios.id)
#         vios = vios_list[0]

        if False:
            vendor = "IBM"
            t_wwpn = "500507680245CAC0"
            lua = "6000000000000"
            deviceid = "6005076802810B0FD0000000000004C5"

            ports = []
            for slot in vios.partition_io_configuration.profile_io_slots.\
                    profile_io_slot:
                adapter = slot.associated_io_slot.related_io_adapter
                if isinstance(adapter, k2uom.PhysicalFibreChannelAdapter):
                    for port in adapter.physical_fibre_channel_ports.\
                            physical_fibre_channel_port:
                        ports.append(port.wwpn)
            itls = []
            for iwwpn in ports:
                itls.append((iwwpn, t_wwpn, lua))
            assert len(itls) > 0

            print (itls)
            result = cs.virtualioserver.lua_recovery(vios,  vendor,
                                                     deviceid, itls)

            print ("lua_recovery: result:")
            print (json.dumps(result, indent=4))
            assert result
            dev_name = result[2][0][1]
            print (dev_name)

            vios = cs.virtualioserver.getasroot(vios_id)

            hdisk_uuid = ""
            for volume in vios.physical_volumes.physical_volume:
                if volume.volume_name == dev_name:
                    hdisk_uuid = volume.unique_device_id

            print ("found hdisk_uuid: >%s<" % (hdisk_uuid))
        else:
            hdisk_uuid = ("01M0lCTTIxNDUzMjQ2MDA1MDc2ODAyOD"
                          "EwQjBGRDAwMDAwMDAwMDAwMDRDNQ==")
            print ("using hdisk_uuid: >%s<" % (hdisk_uuid))

#         # 2 MB
#         finfo = _createtestfile(size=1024 * 1024 * 2)
#         ddinfo = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/test.img."
#                   "2MB bs=1048576 count=2")

#         # 1 GB
#         finfo = _createtestfile(size=1024 * 1024 * 1024 * 1)
#         ddinfo = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/test.img."
#                   "1GB bs=1048576 count=1024")

#         # 2 GB
#         finfo = _createtestfile(size=1024 * 1024 * 1024 * 2)
#         ddinfo = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/test.img."
#                   "2GB bs=1048576 count=2048")

        # Pavel's number
        finfo = _createtestfile(size=1024 * 1024 * 2052)
        ddinfo = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/test.img."
                  "PAVEL bs=1048576 count=2051")

#         # 3 GB
#         finfo = _createtestfile(size=1024 * 1024 * 1024 * 3)
#         ddinfo = ("dd if=/dev/hdisk6 of=/UPLOAD-TESTS/test.img."
#                   "3GB bs=1048576 count=3072")

        print ("to dd: >%s<" % (ddinfo,))

        webfile = _upload(cs, finfo, vios_id, hdisk_uuid)

        # delete
        if False:  # TODO
            cs.web_file.delete(webfile)
            print ("deleted webfile: >%s<" % (webfile.id))
        else:
            print ("retained webfile: >%s<" % (webfile.id))

    except Exception as e:
        logging.exception(e)
