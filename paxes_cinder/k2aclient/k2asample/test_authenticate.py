#
#
# =================================================================
# =================================================================


import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))

    print k2acfg['api_version']
    print k2acfg['k2_url']
    print k2acfg['k2_username']
    print k2acfg['k2_password']
    print k2acfg['k2_auditmemento']
    print k2acfg['k2_certpath']
    print logging.getLevelName(k2acfg['loglevel'])
    print k2acfg['timeout']
    print k2acfg['excdir']

    cs = client.Client(k2acfg['api_version'],
                       k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2acfg['timeout'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       excdir=k2acfg['excdir'])

    cs.client.authenticate()
