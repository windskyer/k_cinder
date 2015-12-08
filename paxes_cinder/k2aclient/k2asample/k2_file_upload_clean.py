# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================

from __future__ import print_function

# from paxes_cinder.k2aclient.v1 import k2web
# from paxes_cinder.k2aclient.v1 import k2uom

import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

if __name__ == '__main__':

    k2acfg = k2asample.getk2acfg(cfgfile="my_sadek_k2a.cfg")
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

        wfs = cs.web_file.list()
        for wf in wfs:
            print("webfile.name: >%s<" % (wf.filename,))

        for wf in wfs:
            if (wf.filename == "scohack_file" or
                    wf.filename == "IMGUPLOAD_FILE"):
                print("deleting webfile.name: >%s<, ..." % (wf.filename,))
                cs.web_file.delete(wf)
        # delete
#         cs.web_file.delete(webfile)
#         print ("deleted")

    except Exception as e:
        logging.exception(e)
