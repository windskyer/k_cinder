#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client

import logging


def ssp_lu_clone_simple(cs, cluster_id):
    """lu_clone sample for k2aclient"""

    cluster = cs.cluster.get(cluster_id)
    ssp_id = cluster.sharedstoragepool_id()
    ssp = cs.sharedstoragepool.get(ssp_id)
    # add LogicalUnits
    n = cs.sharedstoragepool.create_unique_name
    (source_lu, ssp) = ssp.update_append_lu(n("P2Z-SOURCE-DM"),
                                            10,
                                            thin=True,
                                            logicalunittype="VirtualIO_Image")
    cf = source_lu.unique_device_id
    (target_lu, ssp) = ssp.update_append_lu(n("P2Z-TARGET-DM"),
                                            10,
                                            thin=True,
                                            logicalunittype="VirtualIO_Disk",
                                            clonedfrom=cf)

    print ("Created Source LU: >%s< and Cloned Target LU: >%s<" %
           (source_lu.unique_device_id, target_lu.unique_device_id))

    ssp = ssp.update_del_lus([target_lu.unique_device_id,
                              source_lu.unique_device_id])

    print ("Deleted Source LU: >%s< and Target LU: >%s<" %
           (source_lu.unique_device_id, target_lu.unique_device_id))

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
#     cs = client.Client(k2acfg['api_version'],
#                        "9.114.181.229",  # k2acfg['k2_url'],
#                        k2acfg['k2_username'],
#                        "Passw0rd",  # k2acfg['k2_password'],
#                        k2_auditmemento=k2acfg['k2_auditmemento'],
#                        k2_certpath=k2acfg['k2_certpath'],
#                        retries=k2acfg['retries'],
#                        timeout=k2acfg['timeout'],
#                        excdir=k2acfg['excdir'])

#     # N7
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "fe3fbe0f-5ba8-3374-ab75-7b653c9a57ff"  # cluster-b

#     # gerald 168
#     k2_url = "9.114.181.168"
#     k2_password = "passw0rd"
#     cluster_id = "02803f50-7063-3602-a304-fb54e4ca2d44"  # p730_810_A

# #     N8
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "0c737495-d09a-337a-a7e9-6173d4bb6d20"  # cluster-c

#     REJY
    k2_url = "9.126.139.241"
    k2_password = k2acfg['k2_password']
    cluster_id = "c43fbdcd-95f2-3b4a-b643-234ff00eded4"  # TestCluster

#     # gerald_225
#     k2_url = "9.114.181.225"
#     k2_password = "Passw0rd"
# #     cluster_id = "04628d39-67df-3047-b90e-c4d9b4057267"  # p730_810_A
#     cluster_id = "f598ac8f-c644-36c0-8a4c-1c58809527e0"  # p730_810_B

#     # Gerald
#     k2_url = "9.114.181.238"
#     k2_password = "Passw0rd"
#     cluster_id = "04628d39-67df-3047-b90e-c4d9b4057267"  # carl's new cluster

    cs = client.Client(k2acfg['api_version'],
                       k2_url,  # k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2_password,  # k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    # sde-power clustercd79f607-671e-3a80-9862-63d48702729e
#     cluster_id = 'c38db666-ba8c-35d0-9fa6-d2bf0cc5ea4b'  # cluster-e
#     cluster_id = '6a948d4c-000f-3219-8972-818c37a94d97'  # cluster-d
#     cluster_id = 'cd79f607-671e-3a80-9862-63d48702729e'  # carl's cluster
#     cluster_id = "ea1b0b5f-3b3a-39dc-bade-6e9cebd18bb2"  # cluster-a
    try:
        ssp_lu_clone_simple(cs, cluster_id)
    except Exception as e:
        logging.exception(e)
