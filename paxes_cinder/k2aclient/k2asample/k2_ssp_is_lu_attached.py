#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient.v1 import k2uom
import logging


def is_lu_attached(cs, cluster_id, lu_udid):

    # cluster is at the root
    cluster = cs.cluster.get(cluster_id)

    # just for fun, verify that lu_udid is in the sharedstoragepool
    ssp_id = cluster.sharedstoragepool_id()
    ssp = cs.sharedstoragepool.get(ssp_id)
    x = k2uom.LogicalUnit()

    found = False
    for lu in ssp.logical_units.logical_unit:
        if lu.unique_device_id == lu_udid:
            found = True
            break
    if not found:
        x = "LU w/ udid: >%s<, not found in cluster: >%s<"
        raise ValueError(x % (lu_udid, cluster_id))

    # enough for fun, now find out if lu has been attached

    for node in cluster.node.node:
        vios_id = node.split("/")[-1]
        vios = cs.virtualioserver.get(vios_id)
        print (vios.id)
        for vsm in vios.virtual_scsi_mappings.virtual_scsi_mapping:
            pass

#             {
#                 "associated_logical_partition":
# "https://10.20.104.150:12443/rest/api/uom/LogicalPartition/
# 1BF2684C-85A8-4F74-B174-D7F66C65B383",
#                 "client_adapter": {
#                     "adapter_type": "Client",
#                     "dynamic_reconfiguration_connector_name":
# "U7895.42X.066B1FB-V5-C2",
#                     "local_partition_id": "5",
#                     "location_code": "U7895.42X.066B1FB-V5-C2",
#                     "remote_logical_partition_id": "3",
#                     "remote_slot_number": "4",
#                     "required_adapter": "true",
#                     "server_location_code": "U7895.42X.066B1FB-V3-C4",
#                     "varied_on": "false",
#                     "virtual_slot_number": "2"
#                 },
#                 "server_adapter": {
#                     "adapter_name": "vhost2",
#                     "adapter_type": "Server",
#                     "backing_device_name": "LU_for_LPAR_1",
#                     "dynamic_reconfiguration_connector_name":
# "U7895.42X.066B1FB-V3-C4",
#                     "local_partition_id": "3",
#                     "location_code": "U7895.42X.066B1FB-V3-C4",
#                     "remote_logical_partition_id": "5",
#                     "remote_slot_number": "65535",
#                     "required_adapter": "false",
#                     "server_location_code": "U7895.42X.066B1FB-V5-C2",
#                     "unique_device_id": "1eU7895.42X.066B1FB-V3-C4",
#                     "varied_on": "true",
#                     "virtual_slot_number": "4"
#                 },
#                 "storage_type": "LOGICAL_UNIT",
#                 "target_device": {
#                     "virtual_target_device": [
#                         {
#                             "logical_unit_address": "0x8100000000000000",
#                             "target_name": "vtscsi2",
#                             "unique_device_id": "0aef15ba89f4dfcbec"
#                         }
#                     ]
#                 }
#             },
#             {
#                 "associated_logical_partition":
# "https://10.20.104.150:12443/rest/api/uom/LogicalPartition/
# 094FFE6F-CCF6-45F0-8D77-5612BC3EE7A7",
#                 "client_adapter": {
#                     "adapter_type": "Client",
#                     "dynamic_reconfiguration_connector_name":
# "U7895.42X.066B1FB-V4-C2",
#                     "local_partition_id": "4",
#                     "location_code": "U7895.42X.066B1FB-V4-C2",
#                     "remote_logical_partition_id": "3",
#                     "remote_slot_number": "3",
#                     "required_adapter": "true",
#                     "server_location_code": "U7895.42X.066B1FB-V3-C3",
#                     "varied_on": "true",
#                     "virtual_slot_number": "2"
#                 },
#                 "server_adapter": {
#                     "adapter_name": "vhost1",
#                     "adapter_type": "Server",
#                     "backing_device_name": "LU_for_LPAR_0",
#                     "dynamic_reconfiguration_connector_name":
# "U7895.42X.066B1FB-V3-C3",
#                     "local_partition_id": "3",
#                     "location_code": "U7895.42X.066B1FB-V3-C3",
#                     "remote_logical_partition_id": "4",
#                     "remote_slot_number": "65535",
#                     "required_adapter": "false",
#                     "server_location_code": "U7895.42X.066B1FB-V4-C2",
#                     "unique_device_id": "1eU7895.42X.066B1FB-V3-C3",
#                     "varied_on": "true",
#                     "virtual_slot_number": "3"
#                 },
#                 "storage_type": "LOGICAL_UNIT",
#                 "target_device": {
#                     "virtual_target_device": [
#                         {
#                             "logical_unit_address": "0x8100000000000000",
#                             "target_name": "vtscsi1",
#                             "unique_device_id": "0ace46446602c8dcc2"
#                         }
#                     ]
#                 }
#             }


#             {
#                 "thin_device": "true",
#                 "unique_device_id": "2701269b89bf13da8c7c11ecbebbc19d58",
#                 "unit_capacity": "20",
#                 "unit_name": "LU_for_LPAR_0"
#             },


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

    try:
        cluster_id = "a9dbe07f-30c4-3788-8f6f-659aa1d66502"
        lu_udid = "277ff7672a46be4c21b180f0aa3d88a4f2"
        is_lu_attached(cs, cluster_id, lu_udid)
    except Exception as e:
        logging.exception(e)
