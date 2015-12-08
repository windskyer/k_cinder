#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client

from paxes_cinder.k2aclient.v1.k2uom import \
    LogicalUnit

import logging


def ssp_lu_clone_new(cs, ssp_id):
    """lu_clone sample for k2aclient"""
    ssp = cs.sharedstoragepool.get(ssp_id)
    lu = LogicalUnit()
    lu.unit_name = "P2Z-NEW"
    lu.unit_capacity = "10"
    lu.thin_device = "true"
    ssp.logical_units.logical_unit.append(lu)
    cs.sharedstoragepool.update(ssp)


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

    ssp_id = 'e9b6b0fa-62c1-3d35-806b-63be1ff10b00'
    try:
        ssp_lu_clone_new(cs, ssp_id)
    except Exception as e:
        logging.exception(e)
