#
#
# =================================================================
# =================================================================
"""P-specific operations."""

from paxes_cinder.k2aclient import _
import paxes_cinder.k2aclient.exceptions as k2aexc

import glob
import time


def _fvt_hook(test):
    while True:
        try:
            with open('/tmp/fvt-ssp.txt') as f:
                data = f.read()
                if not data.find(test) < 0:
                    time.sleep(2)
                else:
                    return
        except IOError:
            return


def _enum(**enums):
    return type('Enum', (), enums)

# Status of test
Status = _enum(NOT_ATTEMPTED="NOT_ATTEMPTED",
               SUCCESS="SUCCESS",
               FAILED_WITH_EXCEPTION="FAILED_WITH_EXCEPTION",
               FAILED_WITH_UNEXPECTED_RESULT="FAILED_WITH_UNEXPECTED_RESULT")


class PowerVcClusterCheck(object):
    """For tracking a test result"""
    def __init__(self, title, description, cluster_id):
        self._title = title
        self._description = description

        self._cluster_id = cluster_id

        self._status = Status.NOT_ATTEMPTED
        self._message = "MSG500"
        self._params = None
        self._exception = None
        self._response = None

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def cluster_id(self):
        return self._cluster_id

    @property
    def status(self):
        return self._status

    @property
    def message(self):
        return self._message

    @property
    def params(self):
        return self._params

    @property
    def exception(self):
        return self._exception

    @property
    def response(self):
        return self._response

    def setSuccess(self, message, params):
        self._status = Status.SUCCESS
        self._message = message
        self._params = params

    def setFailedWithException(self, exception, message, params, response):
        self._status = Status.FAILED_WITH_EXCEPTION
        self._exception = _("%s") % exception
        self._message = message
        self._params = params
        self._response = response

    def setFailedWithUnexpectedResult(self, message, params, response):
        self._status = Status.FAILED_WITH_UNEXPECTED_RESULT
        self._message = message
        self._params = params
        self._response = response

MESSAGES = {
    "MSG010": _("SharedStoragePool: While attempting to access Cluster: >%s<, "
    "unable to connect to HMC: >%s<"),
    "MSG020": _("Check the HMC and its configuration."),
    "MSG030": _("SharedStoragePool: Able to connect to HMC: >%s< "
    "for Cluster: >%s<"),
    "MSG040": _("SharedStoragePool: Couldn't access Cluster: >%s<"),
    "MSG050": _("Check the PowerVC SharedStoragePool configuration"),
    "MSG060": _("SharedStoragePool: Couldn't access SharedStoragePool "
    "in Cluster: >%s<"),
    "MSG070": _("Diagnose and repair Cluster"),
    "MSG080": _("SharedStoragePool: Successfully accessed SharedStoragePool "
    "in Cluster: >%s<"),
    "MSG090": _("SharedStoragePool: Unable to create LogicalUnits "
    "in Cluster: >%s<"),
    "MSG100": _("Diagnose and repair Cluster"),
    "MSG110": _("SharedStoragePool: LogicalUnit creation functional "
    "in Cluster: >%s<"),
    "MSG120": _("SharedStoragePool: Unable to clone LogicalUnits "
    "in Cluster: >%s<"),
    "MSG130": _("Diagnose and repair Cluster"),
    "MSG140": _("SharedStoragePool: Unable to clone LogicalUnits "
    "in Cluster: >%s<, status: >%s<"),
    "MSG150": _("Clone functional in Cluster: >%s<"),
    "MSG160": _("SharedStoragePool: Unable to delete LogicalUnits "
    "in Cluster: >%s<"),
    "MSG170": _("Diagnose and repair Cluster"),
    "MSG180": _("SharedStoragePool: LogicalUnit deletion functional "
    "in Cluster: >%s<"),
    "MSG500": _("SharedStoragePool: Not Attempted")
}

# Testset is an ordered list of PowerVcClusterCheck, if a test
# fails subsequent tests should have status of Status.NOT_ATTEMPTED
# _TESTS contains order list of PowrVcClusterCheck constructor input
_TESTS = [("connect_to_hmc",
           (_("HMC connectivity"),
            _("Test connection to an HMC managing the SharedStoragePool"))
           ),
          ("access_cluster",
           (_("Cluster and SharedStoragePool accessibility"),
            _("Test the accessibility of a SharedStoragePool"))
           ),
          ("create_logicalunits",
           (_("Create SharedStoragePool LogicalUnits"),
            _("Test the capability to create SharedStoragePool LogicalUnits"))
           ),
          ("clone",
           (_("Clone LogicalUnits"),
            _("Test the capability to perform a clone"))
           ),
          ("delete_logicalunits",
           (_("Delete SharedStoragePool LogicalUnits"),
            _("Test the capability to delete SharedStoragePool LogicalUnits"))
           )]

# _TESTLOOKUP permits accessing ordered list of tests by name
_TESTLOOKUP = {}
for (i, (key, _)) in enumerate(_TESTS):
    _TESTLOOKUP[key] = i


def _perform_test_on_conf(tests, cs, conf, cid, hdn):
    """For a given configuration file perform the tests"""
    # initiate tests
    curtests = []
    for _, (title, descr) in _TESTS:
        curtests.append(PowerVcClusterCheck(title,
                                            descr,
                                            cid))
    tests.append((conf, cs.client.k2_url, hdn, curtests))

    ########
    # test_connect_to_hmc
    _fvt_hook("connect_to_hmc")
    curtest = curtests[_TESTLOOKUP["connect_to_hmc"]]
    failed = None
    try:
        cs.client.authenticate()
    except Exception as failed:
        pass
    if failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG010",
                                       [hdn, cs.client.k2_url],
                                       "MSG020")
        return
    curtest.setSuccess("MSG030",
                       [cs.client.k2_url, hdn])

    ########
    # access_cluster
    _fvt_hook("access_cluster")
    curtest = curtests[_TESTLOOKUP["access_cluster"]]
    failed = None
    try:
        cluster = cs.cluster.get(cid)
    except Exception as failed:
        pass

    if isinstance(failed, k2aexc.K2aK2ErrorNotFound):
        curtest.setFailedWithUnexpectedResult("MSG040",
                                              [hdn],
                                              "MSG050")
        return
    elif failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG040",
                                       [hdn],
                                       "MSG050")

        return
    ssp_id = cluster.cluster_shared_storage_pool.split("/")[-1]
    if len(ssp_id) != 36:
        curtest.setFailedWithUnexpectedResult("MSG040",
                                              [hdn],
                                              "MSG050")
        return

    failed = None
    try:
        ssp = cs.sharedstoragepool.get(ssp_id)
    except Exception as failed:
        pass

    if isinstance(failed, k2aexc.K2aK2ErrorNotFound):
        curtest.setFailedWithUnexpectedResult("MSG040",
                                              [hdn],
                                              "MSG050")
        return
    elif failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG060",
                                       [hdn],
                                       "MSG070")
        return

    curtest.setSuccess("MSG080",
                       [hdn])

    ########
    # create_logicalunits
    _fvt_hook("create_logicalunits")
    curtest = curtests[_TESTLOOKUP["create_logicalunits"]]
    failed = None
    try:
        n = cs.sharedstoragepool.create_unique_name
#         (status, source_udid, job_id) = cluster.lu_create(
#             n("DELETEME-TEST-SOURCE"),
#             "0.001",
#             thin=True)
#         (status, source_udid, job_id) = cluster.lu_create(
#             n("DELETEME-TEST-TARGET"),
#             "0.001",
#             thin=True)
        (source_lus, ssp) = ssp.update_append_lus([(n("DELETEME-TEST-SOURCE"),
                                                  "0.001",
                                                  True)])
        (target_lus, ssp) = ssp.update_append_lus([(n("DELETEME-TEST-TARGET"),
                                                  "0.001",
                                                  True)])
        source_lu = source_lus[0]
        target_lu = target_lus[0]
    except Exception as failed:
        pass
    if failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG090",
                                       [hdn],
                                       "MSG100")
        return
    curtest.setSuccess("MSG110",
                       [hdn])

    ########
    # clone
    _fvt_hook("clone")
    curtest = curtests[_TESTLOOKUP["clone"]]
    failed = None
    try:
        status, job_id = cluster.lu_linked_clone(
            source_lu.unique_device_id,
            target_lu.unique_device_id)
    except Exception as failed:
        pass
    if failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG120",
                                       [hdn],
                                       "MSG130")
        return
    if status != "COMPLETED_OK":
        curtest.setFailedWithUnexpectedResult("MSG140",
                                              [hdn, status],
                                              "MSG130")
        return

    curtest.setSuccess("MSG150",
                       [hdn])

    ########
    # delete_logicalunits
    _fvt_hook("delete_logicalunits")
    curtest = curtests[_TESTLOOKUP["delete_logicalunits"]]
    failed = None
    try:
        ssp = ssp.update_del_lus([target_lu.unique_device_id])
        ssp = ssp.update_del_lus([source_lu.unique_device_id])
    except Exception as failed:
        pass
    if failed is not None:
        curtest.setFailedWithException(failed,
                                       "MSG160",
                                       [hdn],
                                       "MSG170")
        return
    curtest.setSuccess("MSG180",
                       [hdn])

    # append test
#     tests.append((conf, cs.client.k2_url, curtests))


class PowerVcManager(object):
    """Perform PowerVc-specific operations."""

    def __init__(self, api):
        self.api = api

    def check_ssp_conf(self, confdir):
        """verify ssp is accessible and functional"""

        testset = []
        for conf, cid, hdn in _get_clusters():
            _perform_test_on_conf(testset, self.api, conf, cid, hdn)
        return testset

    @staticmethod
    def result_output_as_dict(testset):
        """return representation of tests suitable for output"""
        #
        # tforj = [{"conf_filespec": "<conf-filespec>",
        #           "tests":
        #             [
        #               {"title": "<title>",
        #                "description": "<description>",
        #                "cluster_id": "<cluster_id>",
        #                "status": "<status>",
        #                "msg": "<msg>",
        #                "exception_msg: "<exception_msg>", (if present)
        #                "response": <response>" (if present)
        #               }
        #             ]
        #          },
        #         ]
        tforj = {}
        for config_file, k2_url, host_display_name, ts in testset:
            cdict = {}
            cdict["configuration_file"] = config_file
            cdict["hmc_ip"] = k2_url
            tlist = []
            for t in ts:
                tdict = {}
                tdict["title"] = t.title
                tdict["description"] = t.description
                tdict["configuration_file"] = config_file
                tdict["hmc_ip"] = k2_url
                tdict["storage_host"] = host_display_name
                tdict["cluster_id"] = t.cluster_id
                tdict["status"] = t.status
                if t.params is not None:
                    tdict["msg"] = MESSAGES[t.message] % tuple(t.params)
                else:
                    tdict["msg"] = MESSAGES[t.message]
                if t.exception is not None:
                    tdict["exception"] = t.exception
                if t.response is not None:
                    tdict["response"] = MESSAGES[t.response]
                tlist.append(tdict)
            cdict["tests"] = tlist
            tforj[config_file] = cdict

        return tforj

    @staticmethod
    def result_output_for_ttv(testset):
        """return representation of tests suitable for ttv"""
        tforj = {}
        for config_file, k2_url, host_display_name, ts in testset:
            cdict = {}
            cdict["configuration_file"] = config_file
            cdict["hmc_ip"] = k2_url
            tlist = []
            for t in ts:
                if t.status is Status.NOT_ATTEMPTED:
                    break
                tdict = {}
                tdict["title"] = t.title
                tdict["description"] = t.description
                tdict["configuration_file"] = config_file
                tdict["hmc_ip"] = k2_url
                tdict["storage_host"] = host_display_name
                tdict["cluster_id"] = t.cluster_id
                tdict["status"] = "SUCCESS"
                if t.status is not Status.SUCCESS:
                    tdict["status"] = "FAIL"
                tdict["message"] = t.message
                tdict["params"] = t.params
                if t.exception is not None:
                    tdict["exception"] = t.exception
                if t.response is not None:
                    tdict["response"] = t.response
                tlist.append(tdict)
            cdict["tests"] = tlist
            tforj[config_file] = cdict

        return tforj


def _get_clusters():
    """Retrieve ssp clusters for health checks
    TODO: TTV Team: Fix this when you port to TTV"""
    # cinder.conf file(s)
    clusters = []
    for conf in glob.glob("/etc/cinder/cinder-*.conf"):
        powervm_mgr_cluster = None
        with open(conf) as f:
            for line in f:
                if line.strip().startswith("powervm_mgr_cluster = "):
                    parts = line.split("=")
                    if len(parts) == 2:
                        powervm_mgr_cluster = parts[1].strip()
                if line.strip().startswith("host_display_name = "):
                    parts = line.split("=")
                    if len(parts) == 2:
                        host_display_name = parts[1].strip()

        if powervm_mgr_cluster is not None and host_display_name is not None:
            clusters.append((conf, powervm_mgr_cluster, host_display_name))

    return clusters

# if __name__ == '__main__':
#     powervm_mgr_clusters = _get_clusters()
#     print powervm_mgr_clusters
