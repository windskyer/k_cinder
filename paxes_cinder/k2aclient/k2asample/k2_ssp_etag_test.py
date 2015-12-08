#
#
# =================================================================
# =================================================================

from __future__ import print_function

import logging
import paramiko
import os
import errno

try:
    from scp import SCPClient
except ImportError:
    scp_installed = False
else:
    scp_installed = True

import paxes_cinder.k2aclient.k2asample as k2asample
import paxes_cinder.k2aclient.openstack.common.procutils as procutils
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient.openstack.common import lockutils

LOG = logging.getLogger(__name__)


def ssp_etag_test(
        cs,
        cluster,
        basedir,
        password="passw0rd"):

#     cluster = cs.cluster.get(cluster_id)

    for node in cluster.node.node:
        if not node.virtual_io_server:
            LOG.error(_("Node: >%s<,"
                        " has no virtual_io_server,"
                        " continuing ...") % node.partition_name)

        ms_id, vios_id = _parse_vios(node.virtual_io_server)
        try:
            vios = cs.\
                virtualioserver.get(ms_id,
                                    vios_id,
                                    xag=["None"])
        except Exception as e:
            msg = _("Failed to retrieve"
                    " node: >%s<,"
                    " msg: >%s<,"
                    " continuing ...")
            LOG.error(msg % (node.partition_name, e))

        ip = vios.resource_monitoring_ip_address
        print (ip)

        # paths
        tarfname = "home-ios-logs.tar"
        srcdir = "/tmp"
        srcpath = os.path.join(srcdir, tarfname)

        # create the tar
        cmd = ('print '
               ' "(cd /home/ios;'
               ' tar -cf %s logs;'
               ' chmod 777 %s)"'
               ' | oem_setup_env') % (srcpath, srcpath)

#         cmd = "tar -cf /tmp/testscp.tar /home/padmin/testscp"
        sshrun(
            ip,
            cmd,
            password=password)

        # move tar to local dir
        tgtdir = os.path.join(basedir, ip)
        _prepdir(tgtdir)
        tgtpath = os.path.join(tgtdir, tarfname)
        sshscpget(
            ip,
            srcpath,
            tgtpath,
            username="padmin",
            password=password)


def vios_snap(vios_ips,
              basedir,
              password="passw0rd"):

    if not scp_installed:
        msg = [
            "# scp.py not installed",
            "git clone https://github.com/jbardin/scp.py.git",
            "cd scp.py"
            "python setup.py install"]
        raise Exception("\n" + "\n".join(msg))

    for ip in vios_ips:

        # paths
        tarfname = "home-ios-logs.tar"
        srcdir = "/tmp"
        srcpath = os.path.join(srcdir, tarfname)

        # create the tar
        cmd = ('print '
               ' "(cd /home/ios;'
               ' tar -cf %s logs;'
               ' chmod 777 %s)"'
               ' | oem_setup_env') % (srcpath, srcpath)

#         cmd = "tar -cf /tmp/testscp.tar /home/padmin/testscp"
        sshrun(
            ip,
            cmd,
            password=password)

        # move tar to local dir
        tgtdir = os.path.join(basedir, ip)
        _prepdir(tgtdir)
        tgtpath = os.path.join(tgtdir, tarfname)
        sshscpget(
            ip,
            srcpath,
            tgtpath,
            username="padmin",
            password=password)

if __name__ == '__main__':
    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
#     cs = client.Client(k2acfg['api_version'],
#                        "9.114.181.229",  # k2acfg['k2_url'],
#                        k2acfg['k2_username'],
#                        "Passw0rd",  # k2acfg['k2_password'],
#                        k2_auditmemento=k2acfg['k2_auditmemento'],
#                        k2_certpath=k2acfg['k2_certpath'],
#                        retries=k2acfg['retries'],
#                        timeout=k2acfg['timeout'],
#                        excdir=k2acfg['excdir'])

#     # N7
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "fe3fbe0f-5ba8-3374-ab75-7b653c9a57ff"  # cluster-b

#     # gerald 168
#     k2_url = "9.114.181.168"
#     k2_password = "passw0rd"
#     cluster_id = "02803f50-7063-3602-a304-fb54e4ca2d44"  # p730_810_A

    # N23 / N24
    k2_url = "hmc5.watson.ibm.com"
    k2_password = k2acfg['k2_password']
    cluster_id = "ea1b0b5f-3b3a-39dc-bade-6e9cebd18bb2"  # cluster-a

# #     N8
#     k2_url = "hmc5.watson.ibm.com"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "0c737495-d09a-337a-a7e9-6173d4bb6d20"  # cluster-c

# #     REJY
#     k2_url = "9.126.139.241"
#     k2_password = k2acfg['k2_password']
#     cluster_id = "c43fbdcd-95f2-3b4a-b643-234ff00eded4"  # TestCluster

#     # gerald_225
#     k2_url = "9.114.181.225"
#     k2_password = "Passw0rd"
# #     cluster_id = "04628d39-67df-3047-b90e-c4d9b4057267"  # p730_810_A
#     cluster_id = "f598ac8f-c644-36c0-8a4c-1c58809527e0"  # p730_810_B

#     # Gerald
#     k2_url = "9.114.181.238"
#     k2_password = "Passw0rd"
#     cluster_id = "04628d39-67df-3047-b90e-c4d9b4057267"  # carl's new cluster

    cs = client.Client(k2acfg['api_version'],
                       k2_url,  # k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2_password,  # k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    # sde-power clustercd79f607-671e-3a80-9862-63d48702729e
#     cluster_id = 'c38db666-ba8c-35d0-9fa6-d2bf0cc5ea4b'  # cluster-e
#     cluster_id = '6a948d4c-000f-3219-8972-818c37a94d97'  # cluster-d
#     cluster_id = 'cd79f607-671e-3a80-9862-63d48702729e'  # carl's cluster
#     cluster_id = "ea1b0b5f-3b3a-39dc-bade-6e9cebd18bb2"  # cluster-a
    try:
        cluster = cs.cluster.get(cluster_id)
        ssp_etag_test(
            cs,
            cluster,
            "/tmp/cluster-snap",
            password="sde2013")
    except Exception as e:
        logging.exception(e)
