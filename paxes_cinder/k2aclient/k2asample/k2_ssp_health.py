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


def ssp_health_check(cs):

    check_results = cs.paxes.check_ssp_conf("/etc/cinder")
    check_results_for_json = cs.paxes.result_output_as_dict(check_results)
    json.dump(check_results_for_json, sys.stdout, sort_keys=True, indent=4)

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
        ssp_health_check(cs)
    except Exception as e:
        logging.exception(e)
