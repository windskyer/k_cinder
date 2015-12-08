#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import json
import sys
import logging


def simple_sample(cs):
    #########
    # CLUSTER READS
    try:
        clusters = cs.cluster.list()
    except:
        raise Exception("K2 failure ...")
    clusterid_to_props = {}
    for cluster in clusters:
        # sspid_to_sspname
        if not cluster.id in clusterid_to_props:
            clusterid_to_props[cluster.id] = {}
        clusterid_to_props[cluster.id] = (
            cluster.cluster_name, cluster.cluster_shared_storage_pool)

    print ("clusterid_to_props:")
    json.dump(clusterid_to_props, sys.stdout, sort_keys=True, indent=4)
    print ("\n\n")

    #########
    # SSP READS
    try:
        ssps = cs.sharedstoragepool.list()
    except:
        raise Exception("K2 failure ...")

    # sspid_to_sspname = {<ssp_id>:<ssp_name>, ...}
    sspid_to_sspname = {}
    # sspid_to_luns = {<ssp_id>: [(<lun_unit_name>,<lun_id>), ...], ...}
    sspid_to_luns = {}

    for ssp in ssps:
        # sspid_to_sspname
        if not ssp.id in sspid_to_sspname:
            sspid_to_sspname[ssp.id] = {}
        sspid_to_sspname[ssp.id] = ssp.storage_pool_name

        # sspid_to_luns
        if not ssp in sspid_to_luns:
            sspid_to_luns[ssp.id] = []
        luns = ssp.logical_units
        for lun in luns.logical_unit:
            sspid_to_luns[ssp.id].append((lun.unit_name, lun.unique_device_id))

    print ("sspid_to_sspname:")
    json.dump(sspid_to_sspname, sys.stdout, sort_keys=True, indent=4)
    print ("\n\n")
    print ("sspid_to_luns:")
    json.dump(sspid_to_luns, sys.stdout, sort_keys=True, indent=4)
    print ("\n")

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    cs = client.Client(k2acfg['api_version'],
                       "9.114.181.225",
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    try:
        simple_sample(cs)
    except Exception as e:
        logging.exception(e)
