#
#
# =================================================================
# =================================================================

from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging
import datetime
import time
import paxes_cinder.k2aclient.exceptions as exceptions

#
#
# =================================================================
# =================================================================

import pickle
import json
import traceback


class K2SerializableResponse(object):
    def __init__(self, msg, k2resp):
        self._msg = msg
        self._k2resp = k2resp

    @property
    def msg(self):
        return self._msg

    @property
    def k2resp(self):
        return self._k2resp


def _report_from_k2serializedresponse(fspec_in, fspec_out):

    with open(fspec_out, 'w') as fout:
        with open(fspec_in, "r") as fin:  # pickled
            ksrs = pickle.load(fin)
            for ksr in ksrs:
                fout.write("\n********************************"
                           "***********************\n")
                fout.write(ksr.msg)
                fout.write("\n********\nrequest:\n")
                k2r = ksr.k2resp
                request = {}
                request["method"] = k2r.reqmethod
                request["path"] = k2r.reqpath
                request["headers"] = k2r.reqheaders
#                     request["body"] = k2r.reqbody
                json.dump(request, fout, sort_keys=True, indent=4)
                fout.write("\n****\nrequest.body:\n")
                fout.write(k2r.reqbody)
                fout.write("\n********\nresponse:\n")
                response = {}
                response["status_code"] = k2r.status
                response["reason"] = k2r.reason
                response["headers"] = k2r.headers
#                     response["body"] = k2r.body
                json.dump(response, fout, sort_keys=True, indent=4)
                fout.write("\n****\nresponse.body:\n")
                fout.write(k2r.body)


def k2resp_to_string(k2resp):
    buf = ""
    buf += "\n********************************" +\
        "***********************\n"
    buf += "\n********\nrequest:\n"
    request = {}
    request["method"] = k2resp.reqmethod
    request["path"] = k2resp.reqpath
    request["headers"] = k2resp.reqheaders
#                     request["body"] = k2resp.reqbody
    buf += json.dumps(request, sort_keys=True, indent=4)
    buf += "\n****\nrequest.body:\n"
    buf += k2resp.reqbody
    buf += "\n********\nresponse:\n"
    response = {}
    response["status_code"] = k2resp.status
    response["reason"] = k2resp.reason
    response["headers"] = k2resp.headers
#                     response["body"] = k2resp.body
    buf += json.dumps(response, sort_keys=True, indent=4)
    buf += "\n****\nresponse.body:\n"
    buf += k2resp.body
    return buf


if __name__ == '__main__':
    """Short program to generate input for
    Defect:SW222953 - K2 API:ETAG mechanism failing when
    updating LogicalUnits in a SharedStoragePool. To perform
    test work around in sharedstoragepool_manager needs
    to be disabled"""

    record = False
    if not record:
        fspec_in = "/tmp/tool_test_etag_2013-09-04_23-19-13_00000.pickle"
        fspec_out = '/tmp/tool_test_etag_2013-09-04_23-19-13_00000.txt'
        _report_from_k2serializedresponse(fspec_in, fspec_out)
    else:

        k2acfg = k2asample.getk2acfg()
    #     k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
        k2asample.configure_logging(logging.DEBUG, k2_loglevel=logging.WARNING)
        cs = client.Client(k2acfg['api_version'],
                           k2acfg['k2_url'],
                           k2acfg['k2_username'],
                           k2acfg['k2_password'],
                           k2_auditmemento=k2acfg['k2_auditmemento'],
                           k2_certpath=k2acfg['k2_certpath'],
                           retries=3,  # k2acfg['retries']
                           timeout=120,  # k2acfg['timeout']
                           excdir="/tmp/test_etag")  # k2acfg['excdir']

        cluster_id = "c38db666-ba8c-35d0-9fa6-d2bf0cc5ea4b"  # cluster-e"
        cluster = cs.cluster.get(cluster_id)
        ssp_id = cluster.sharedstoragepool_id()
        # the ssp associated with the cluster
        # responses
        srs = []

        # base SSP
        ssp = cs.sharedstoragepool.get(ssp_id)
        x = "First obtain the current SSP, call it >BASE SSP< ..."
        srs.append(K2SerializableResponse(x, ssp.k2resp))

        # A SSP
        lu1, ssp1 = ssp.update_append_lu("ETAG-LU-01", 1)
        x = "Now add an LU named >ETAG-LU-01< to >BASE SSP< ..."
        srs.append(K2SerializableResponse(x, ssp1.k2resp))

        try:
            lu2, ssp2 = ssp.update_append_lu("ETAG-LU-02", 1)
        except exceptions.K2aCrudException as e:
            x = "Now add a 2nd LU named >ETAG-LU-02< to " +\
                "same >BASE SSP< and note that a 412 is not returned"
            srs.append(K2SerializableResponse(x, e.k2resp))

        ts = time.time()
        _lastseq = 0
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')
        x = '/tmp/tool_test_etag_%s_%05d.pickle'
        with open(x % (st, _lastseq), 'w') as f:
            pickle.dump(srs, f)

    #     etag1 = ssp1.k2resp.headers['etag']
    #     print ("etag1: >%s<" % (etag1,))
    #     etag2 = ssp2.k2resp.headers['etag']
    #     print ("etag2: >%s<" % (etag2,)


def report():
    """Short program to print pickled k2 response"""
    f = "k2a-500-2013-09-05_15-08-14_00000"
    fspec_in = "/tmp/%s.pickle" % (f,)
    fspec_out = "/tmp/%s.txt" % (f,)
    _report_from_k2serializedresponse(fspec_in, fspec_out)
