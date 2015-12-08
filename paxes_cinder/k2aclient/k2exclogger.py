#
#
# =================================================================
# =================================================================

from paxes_cinder.k2aclient import _

import json
import traceback
import time
import datetime
import glob
import os
import errno
import logging
import xml.dom.minidom as minidom

_logger = logging.getLogger(__name__)

_lastseq = 0
_lastst = None


class K2Response(object):
    def __init__(self, msg, k2resp):
        self._msg = msg
        self._k2resp = k2resp

    @property
    def msg(self):
        return self._msg

    @property
    def k2resp(self):
        return self._k2resp


def _dump_k2resp(msg, trcbak, exc, k2resp, fspec_out):

    with open(fspec_out, 'w') as fout:
        fout.write("\n********************************"
                   "***********************\n")
        if msg is not None:
            fout.write(msg)
        fout.write("\n********\nexception:\n")
        if exc is not None:
            fout.write(_("%s") % exc)
        else:
            fout.write("No exception")
        fout.write("\n********\ntraceback:\n")
        fout.write(trcbak)
        if k2resp is not None:
            fout.write("\n********\nrequest:\n")
            request = {}
            request["method"] = k2resp.reqmethod
            request["path"] = k2resp.reqpath
            request["headers"] = k2resp.reqheaders
    #                     request["body"] = k2r.reqbody
            json.dump(request, fout, sort_keys=True, indent=4)
            fout.write("\n****\nrequest.body:\n")
            try:
                try:
                    xml = minidom.parseString(k2resp.reqbody)
                    fout.write(xml.toprettyxml(indent=' ' * 4))
                except:
                    fout.write(k2resp.reqbody)
            except Exception as e:
                fout.write("Cant output request.body, because: >%s<" % e)
            fout.write("\n********\nresponse:\n")
            response = {}
            response["status_code"] = k2resp.status
            response["reason"] = k2resp.reason
            response["headers"] = dict(k2resp.headers)
    #                     response["body"] = k2r.body
            json.dump(response, fout, sort_keys=True, indent=4)
            fout.write("\n****\nresponse.body:\n")
            fout.write(k2resp.body)


class K2ResponseLogger(object):

    def __init__(self, logbasedir, max_number_of_files=1000):
        self._logdir = os.path.join(logbasedir, "k2aexc")
        self._lastst = 0
        self._lastseq = None
        self._max_number_of_files = max_number_of_files
        self._broken = False

    @property
    def max_number_of_files(self):
        return self._max_number_of_files

    @max_number_of_files.setter
    def max_number_of_files(self, value):
        self._max_number_of_files = value

    def emit(self, category, msg, k2response, exc=None):
        if self._broken:
            return "BROKEN"

        trcbak = traceback.format_exc()
        try:
            os.makedirs(self._logdir)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(self._logdir):
                pass
            else:
                msg = _("k2aclient:"
                        " during FFDC,"
                        " cant create k2 exception log directory:"
                        " >%s<, will disable k2 exception logging ..")
                _logger.warn(msg % self._logdir)
                self._broken = True
                return "BROKEN"

        if not os.access(self._logdir, os.W_OK):
            msg = _("k2aclient:"
                    " during FFDC,"
                    " cant write to k2 exception log directory:"
                    " >%s<, will disable k2 exception logging ..")
            _logger.warn(msg % self._logdir)
            self._broken = True
            return "BROKEN"

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        if st == self._lastst:
            self._lastseq += 1
        else:
            self._lastseq = 0
        self._lastst = st

        fn = "%s_%s-%05d" % (category, st, self._lastseq,) + ".k2r"
        diagfspec = os.path.join(self._logdir, fn)

        try:
            _dump_k2resp(msg, trcbak, exc, k2response, diagfspec)
        except Exception:
            self._broken = True
            msg = _("k2aclient:"
                    " during FFDC, "
                    " caught an exception while writing to log"
                    " directory:"
                    " >%s<, will disable k2 exception logging ..")
            _logger.exception(msg % self._logdir)
            return "BROKEN"

        self.prune()

        return diagfspec

    def prune(self):
        if self._broken:
            return 0
        filemap = {}
        globspec = os.path.join(self._logdir, "*_*.k2r")
        k2rs = glob.glob(globspec)
        if len(k2rs) <= self._max_number_of_files:
            return 0

        for k2r in k2rs:
            (noext, _) = os.path.splitext(k2r)
            key = noext.split("_")[-1]
            if not key in filemap:
                filemap[key] = k2r

        numtodel = len(filemap.keys()) - self._max_number_of_files
        for i, key in enumerate(sorted(filemap.keys())):
            if i >= numtodel:
                break
            try:
                os.remove(filemap[key])
            except:
                msg = ("k2aclient:"
                       " during FFDC,"
                       " during log cleanup,"
                       " couldnt remove:"
                       " >%s<, proceeding ...")
                _logger.debug(msg % filemap[key])

        return numtodel

if __name__ == '__main__':
    logging.basicConfig()
    k2rl = K2ResponseLogger("/tmp/dmdm", 5)
    for i in xrange(10):
        k2rl.emit("500", None, None)
        time.sleep(1)
