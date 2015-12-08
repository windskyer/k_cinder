# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

from paxes_cinder.k2aclient.v1.k2uom import \
    LogicalPartition, \
    LogicalPartitionProfileDedicatedProcessorConfiguration, \
    LogicalPartitionProcessorConfiguration, \
    LogicalPartitionMemoryConfiguration


def createlpar(cs, managedsystem, proc, mem, lparname):

    # LogicalPartitionProfileDedicatedProcessorConfiguration
    lppdpc = LogicalPartitionProfileDedicatedProcessorConfiguration()
    lppdpc.desired_processors = proc
    lppdpc.maximum_processors = proc
    lppdpc.minimum_processors = proc

    # LogicalPartitionProcessorConfiguration
    lppc = LogicalPartitionProcessorConfiguration()
    lppc.dedicated_processor_configuration = lppdpc
    lppc.has_dedicated_processors = "true"
    lppc.sharing_mode = "sre idle procs always"

    # LogicalPartitionMemoryConfiguration
    lpmc = LogicalPartitionMemoryConfiguration()
    lpmc.desired_memory = mem
    lpmc.maximum_memory = mem
    lpmc.minimum_memory = mem

    # LogicalPartition
    lp = LogicalPartition()
    lp.partition_memory_configuration = lpmc
    lp.partition_name = lparname
    lp.partition_processor_configuration = lppc
    lp.partition_type = 'AIX/Linux'

    newlp = cs.managedsystem.create(managedsystem, child=lp)
    print ("newlp: >%s<" % (newlp.id,))

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

    managedsystem_id = "b4397413-6927-3d01-9db7-872757515ce6"
    managedsystem = cs.managedsystem.get(managedsystem_id)

    lparname = 'P2Z-NEW'
    proc = 1
    mem = 1024

    try:
        createlpar(cs, managedsystem, proc, mem, lparname)
    except Exception as e:
        logging.exception(e)
