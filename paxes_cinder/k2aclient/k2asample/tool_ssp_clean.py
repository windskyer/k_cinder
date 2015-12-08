#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient.k2asample import timer
from paxes_cinder.k2aclient import client
import sys
import logging
import traceback


def _chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def _chunks2(l, cs):
    """ Yield special chunks from l.
    """
    cs = [2, 4, 8, 16, 32, 64]
    ci = 0
    lin = 0
    while True:
        li = lin
        if li > (len(l) - 1):
            break
        lin = li + cs[ci]
        ci = (ci + 1) % len(cs)
        yield l[li:lin]


def ssp_lus_clean(cs, cluster_id, *startswith):

    cluster = cs.cluster.get(cluster_id)

    # the ssp associated with the cluster
    ssp_id = cluster.sharedstoragepool_id()

    laps = timer(None)
    ssp = cs.sharedstoragepool.get(ssp_id)
    lu_udid_for_delete = []
    for lu in ssp.logical_units.logical_unit:
        for sw in startswith:
            if lu.unit_name.startswith(sw):
                lu_udid_for_delete.append(lu.unique_device_id)
                break

    print ("Elapsed time for search: >%f<" %
           (timer(laps),))

    if len(lu_udid_for_delete) == 0:
        x = "For SSP: >%s<, found no LUs starting with: >%s<"
        print (x % (ssp_id, ",".join(startswith)))
    else:
        x = "For SSP: >%s<, found >%d< LUs starting with: >%s<"
        print (x % (ssp_id, len(lu_udid_for_delete), ",".join(startswith)))
        total_deleted = 0
        cur_len = len(lu_udid_for_delete)
        laps2 = timer(None)
        chunksize = 100
        for chunk in _chunks(lu_udid_for_delete, chunksize):
#         chunksizes = [1, 2, 4, 8, 16, 32, 64, 128]
#         for chunk in _chunks2(lu_udid_for_delete, chunksizes):
            ssp = ssp.update_del_lus(chunk)
            laptime = timer(laps2)
            chunklen = len(chunk)
            total_deleted += chunklen
#             print ("Deleted >%d< in >%f< seconds, "
#                    "total deleted: >%d<" %
#                    (chunklen, laptime, total_deleted))
            del_rate = laptime / float(chunklen)
            x = ("Starting at LU >%d<,"
                 " deleted >%d< in >%f< seconds, "
                 " rate: >%f< s/LU,"
                 " total deleted: >%d<")
            print (x % (cur_len, chunklen, laptime, del_rate, total_deleted))

            cur_len -= chunklen

        x = "For SSP: >%s<, number of LUs deleted: >%d<"
        print (x % (ssp_id, len(lu_udid_for_delete)))
    print ("Elapsed time for delete: >%f<" %
           (timer(laps),))

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
#     k2asample.configure_logging(logging.DEBUG, k2_loglevel=logging.WARNING)

#     # gerald
#     k2_url = "9.114.181.238"
#     k2_password = "Passw0rd"
#     cluster_id = "04628d39-67df-3047-b90e-c4d9b4057267"  # p730_810_A

#     # gerald 168
#     k2_url = "9.114.181.168"
#     k2_password = "passw0rd"
#     cluster_id = "02803f50-7063-3602-a304-fb54e4ca2d44"  # p730_810_A

#     # N7
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "fe3fbe0f-5ba8-3374-ab75-7b653c9a57ff"  # cluster-b

#     # N23 / N24
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "ea1b0b5f-3b3a-39dc-bade-6e9cebd18bb2"  # cluster-a

#     # gerald 168
#     k2_url = "9.114.181.168"
#     k2_password = "passw0rd"
#     cluster_id = "02803f50-7063-3602-a304-fb54e4ca2d44"  # p730_810_A

# #     REJY
#     k2_url = "9.126.139.241"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "c43fbdcd-95f2-3b4a-b643-234ff00eded4"  # TestCluster

#     # N8
#     k2_url = "hmc4.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "0c737495-d09a-337a-a7e9-6173d4bb6d20"  # cluster-c

    # N7
    k2_url = "hmc5.watson.ibm.com"
    k2_password = k2acfg['k2_password']
    cluster_id = "fe3fbe0f-5ba8-3374-ab75-7b653c9a57ff"  # cluster-b

    cs = client.Client(k2acfg['api_version'],
                       k2_url,  # k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2_password,  # k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=30,  # k2acfg['retries']
                       timeout=1200,  # k2acfg['timeout']
                       excdir=k2acfg['excdir'])

    try:
        ssp_lus_clean(cs, cluster_id, "P2Z-FAKEIMAGE",
                      "P2Z-DEPLOY", "P2Z-SOURCE", "P2Z-TARGET")
#         ssp_lus_clean(cs, cluster_id, "P2Z-")
    except Exception as e:
        print ("ERROR: %s" % e, file=sys.stderr)
        print (traceback.format_exc())
