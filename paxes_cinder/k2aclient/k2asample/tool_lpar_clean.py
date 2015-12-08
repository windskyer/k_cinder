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


def ssp_lpars_clean(cs, ms_id, *startswith):

    lps = cs.logicalpartition.list(ms_id)
    lp_ids_for_delete = []
    laps = timer(None)
    for lp in lps:
        print (lp.id, lp.partition_name)
        for sw in startswith:
            if lp.partition_name.startswith(sw):
                lp_ids_for_delete.append(lp.id)
                break
    print ("Elapsed time for search: >%f<" %
           (timer(laps),))
    if len(lp_ids_for_delete) == 0:
        x = "For ms_id: >%s<, found no LPARs starting with: >%s<"
        print (x % (ms_id, ",".join(startswith)))
        return

    for lp_id in lp_ids_for_delete:
        cs.managedsystem.deletebyid(ms_id, "LogicalPartition", lp_id)
    x = "For ms_id: >%s<, number of LPARs deleted: >%d<"
    print (x % (ms_id, len(lp_ids_for_delete)))
    print ("Elapsed time for delete: >%f<" %
           (timer(laps),))

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
#     k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    k2asample.configure_logging(logging.DEBUG, k2_loglevel=logging.WARNING)
    cs = client.Client(k2acfg['api_version'],
                       k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=120,  # k2acfg['timeout']
                       excdir=k2acfg['excdir'])

    ms_id = "b4397413-6927-3d01-9db7-872757515ce6"
    try:
        ssp_lpars_clean(cs, ms_id, "P2Z-")
    except Exception as e:
        print ("ERROR: %s" % e, file=sys.stderr)
        print (traceback.format_exc())
