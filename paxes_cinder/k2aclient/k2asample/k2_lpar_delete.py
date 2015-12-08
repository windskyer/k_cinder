# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging


def deletelpar(cs, managedsystem_id, lpar_id):
    cs.managedsystem.deletebyid(managedsystem_id, "LogicalPartition", lpar_id)
    print ("SUCCESS")

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

    # works for simple lpars backed by an SSP
    managedsystem_id = "b4397413-6927-3d01-9db7-872757515ce6"
    lpar_id = "1C104F67-C2AB-4B21-81B5-6E0414FD16B6"

    try:
        deletelpar(cs, managedsystem_id, lpar_id)
    except Exception as e:
        logging.exception(e)
