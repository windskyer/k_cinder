#
#
# =================================================================
# =================================================================


import ConfigParser
import logging
import logging.handlers
import os
import time

import json


def timer(laps):
    """ if laps is None, initialize
    otherwise return time since last lap."""
    if laps is None:
        return [time.time()]
    laps.append(time.time())
    return laps[-1] - laps[-2]


def getk2acfg(cfgfile="k2a.cfg"):

    config = ConfigParser.ConfigParser({'api_version': '1',
                                        'k2_username': 'hscroot',
                                        'k2_auditmemento': 'k2asample',
                                        'k2_certpath': None,
                                        'retries': '30',
                                        'timeout': None,
                                        'loglevel': 'WARN',
                                        'excdir': "/tmp/k2asample"
                                        })

    config.readfp(open(cfgfile))
    k2acfg = {}
    k2acfg['api_version'] = config.get('DEFAULT', 'api_version')
    k2acfg['k2_url'] = config.get('DEFAULT', 'k2_url')
    k2acfg['k2_username'] = config.get('DEFAULT', 'k2_username')
    k2acfg['k2_password'] = config.get('DEFAULT', 'k2_password')
    k2acfg['k2_auditmemento'] = config.get('DEFAULT', 'k2_auditmemento')
    k2acfg['k2_certpath'] = config.get('DEFAULT', 'k2_certpath')
    k2acfg['timeout'] = config.get('DEFAULT', 'timeout')
    k2acfg['retries'] = config.getint('DEFAULT', 'retries')
    k2acfg['loglevel'] = config.get('DEFAULT', 'loglevel')
    k2acfg['excdir'] = config.get('DEFAULT', 'excdir')
    return k2acfg


def configure_logging(console_loglevel,
                      k2_loglevel=None,
                      file_loglevel=None,
                      logdir=None):
    """logging for samples"""
    if file_loglevel is None:
        file_loglevel = console_loglevel

    # for k2
    if k2_loglevel is not None:
        logging.getLogger('paxes_k2.k2operator').setLevel(k2_loglevel)
        x = logging.getLogger('requests.packages.urllib3.connectionpool')
        x.setLevel(k2_loglevel)

    # consistent format
    lf = logging.Formatter
    logformatter = \
        lf('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()

    # File logging
    log_file = None
    if logdir is not None:
        logfn = "ibm-k2a.log"
        rfh = logging.handlers.RotatingFileHandler
        log_file = rfh(os.path.join(logdir, logfn),
                       maxBytes=5 * 1024 * 1024,
                       backupCount=5)
        log_file.setLevel(file_loglevel)
        log_file.setFormatter(logformatter)
#             self._log_varlog = log_file
        root_logger.addHandler(log_file)

    # Console logging to STDERR
    log_console = logging.StreamHandler()
    log_console.setLevel(console_loglevel)
    log_console.setFormatter(logformatter)
#         self._log_console = log_console
    root_logger.addHandler(log_console)

    # let handlers do the filtering
    root_logger.setLevel(logging.DEBUG)
    return (log_console, log_file)

#     def setup_debugging(self, debug):
#         self._log_console.setLevel(logging.DEBUG)
#         self._log_varlog.setLevel(logging.DEBUG)


def dump_k2resp(msg, k2resp, fspec_out):
    with open(fspec_out, 'w') as fout:
        fout.write("\n********************************"
                   "***********************\n")
        fout.write(msg)
        fout.write("\n********\nrequest:\n")
        request = {}
        request["method"] = k2resp.reqmethod
        request["path"] = k2resp.reqpath
        request["headers"] = k2resp.reqheaders
        json.dump(request, fout, sort_keys=True, indent=4)
        fout.write("\n****\nrequest.body:\n")
        try:
            fout.write(k2resp.reqbody)
        except Exception as e:
            fout.write("Cant output request.body, because: >%s<", e)
        fout.write("\n********\nresponse:\n")
        response = {}
        response["status_code"] = k2resp.status
        response["reason"] = k2resp.reason
        response["headers"] = k2resp.headers
#                     response["body"] = k2r.body
        json.dump(response, fout, sort_keys=True, indent=4)
        fout.write("\n****\nresponse.body:\n")
        fout.write(k2resp.body)
