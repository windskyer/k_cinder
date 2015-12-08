#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

from tempfile import NamedTemporaryFile

from paxes_cinder.k2aclient.v1.k2web import File

import os
import hashlib


def parse_scg_vios_id(scg_vios_id):

#     scg_vios_id = "789542X_066B1FB##1"

    if (len(scg_vios_id) != 18 or
            scg_vios_id[7] != "_"):
        msg = "x-scg-vios-id: >%s< not of form 'ttttmmm_sssssssnnn'"
        msg = msg % (scg_vios_id,)
        raise ValueError(msg)

    (pt1, pt2) = scg_vios_id.split("_", 1)
    input_machine_type = pt1[:4]
    input_machine_model = pt1[-3:]
    input_serial_number = pt2[:-3]
    input_partition_id = str(int(pt2[-3:].replace("#", "0")))

#     print (input_machine_type)
#     print (input_machine_model)
#     print (input_serial_number)
#     print (input_partition_id)
    try:
        mss = cs.managedsystem.list()
    except Exception as e:
        msg = "scohack: x-scg-vios-id: cant list ManagedSystem: >%s<"
        msg = msg % (e,)
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
        msg = "scohack: x-scg-vios-id: cant find ManagedSystem for: >%s<"
        msg = msg % (scg_vios_id,)
        raise Exception(msg)

    vios_found = None
    try:
        vioss = cs.virtualioserver.list(ms_found.id)
    except Exception as e:
        msg = "scohack: x-scg-vios-id: cant list VirtualIoServer: >%s<"
        msg = msg % (e,)
        raise Exception(msg)

    for vios in vioss:
        if input_partition_id == vios.partition_id:
            vios_found = vios
            break

    if vios_found is None:
        msg = "scohack: x-scg-vios-id: cant find VirtualIOServer for: >%s<"
        msg = msg % (scg_vios_id,)
        raise Exception(msg)

    return (ms_found, vios_found)


if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
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

#     test = x-imgupload-scg-vios-id: 9117MMD_1034E07##2
#     scg_vios_id = "9117MMD_1034E07##2"

    # for ms_id = b4397413-6927-3d01-9db7-872757515ce6
#         "machine_type_model_and_serial_number": {
#         "machine_type": "7895",
#         "model": "42X",
#         "serial_number": "066B1FB"
#     },

# partition_name  : 06-6B1FB
# id              : 2B74BDF1-7CC8-439E-A7D7-15C2B5864DA8
# partition_type  : Virtual IO Server
# partition_id    : 1
# partition_state : running

#     "partition_id": "1",
    scg_vios_id = "789542X_066B1FB##1"

    try:
        (ms, vios) = parse_scg_vios_id(scg_vios_id)
        print ("Found: ManagedSystem: >%s<, VirtualIOServer: >%s<" %
               (ms.id, vios.id))
    except Exception as e:
        logging.exception(e)
