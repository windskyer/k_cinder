# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient import client
import logging
import uuid

from paxes_cinder.k2aclient.v1.k2uom import \
    VirtualSCSIMapping, \
    VirtualSCSIServerAdapter, \
    VirtualSCSIClientAdapter, \
    LogicalPartition, \
    LogicalPartitionProfileDedicatedProcessorConfiguration, \
    LogicalPartitionProcessorConfiguration, \
    LogicalPartitionMemoryConfiguration

CNA_VIRTUAL_SLOT_NUMBER = 3
CNA_PORT_VLAN_ID = "3210"
CNA_QUALITY_OF_SERVICE_PRIORITY_ENABLED = "false"
CNA_TAGGED_VLAN_SUPPORTED = "false"


def clone_logicalunit(cs, cluster, source_logicalunit, dest_lu_unit_name):

    ssp_id = cluster.sharedstoragepool_id()
    ssp = cs.sharedstoragepool.get(ssp_id)
#     # add LogicalUnits
#     (lu, ssp) = ssp.update_append_lu(dest_lu_unit_name, 10, thin=True)
#     return (lu, ssp)

    (status, dest_lu, ssp, job_id) = cluster.api.lu_linked_clone_of_lu_bp(
        cluster,
        ssp,
        source_logicalunit.unique_device_id,
        dest_lu_unit_name)

    if status != "COMPLETED_OK":
        msg = "issue for clone: >%s<, job_id: >%s<, status: >%s<"
        x = msg % (dest_lu_unit_name, job_id, status,)
        raise Exception(x)

    return (dest_lu, ssp)


def provision_lpar(cs, managedsystem, name, proc, mem):

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
    lp.partition_name = name
    lp.partition_processor_configuration = lppc
    lp.partition_type = 'AIX/Linux'

    logicalpartition = cs.managedsystem.create(managedsystem, child=lp)
#     print ("new logicalpartition: >%s<" % (logicalpartition.id,))

    return logicalpartition


def create_virtual_scsi_mapping(logicalunit,
                                logicalpartition):
    """create vio scsi pair"""

    # create the link to the LogicalPartition
    alp = "%s/LogicalPartition/%s" % (cs.client.getserviceurl("uom"),
                                      logicalpartition.id)

    # the server adapter
    vssa = VirtualSCSIServerAdapter()
#     vssa.adapter_type = 'Server'
    vssa.use_next_available_slot_id = 'true'

    # the client adapter
    vsca = VirtualSCSIClientAdapter()
#     vsca.adapter_type = 'Client'
    vsca.use_next_available_slot_id = 'true'

    # the map
    vsm = VirtualSCSIMapping()
    vsm.associated_logical_partition = alp
    vsm.server_adapter = vssa
    vsm.client_adapter = vsca

    # storage
    vsm.storage_type = "LOGICAL_UNIT"
    vsm.storage = logicalunit

    return vsm


def delete_virtual_scsi_mapping(ms_id,
                                vios_id,
                                lpar_id):
    # get the vios
    ms = cs.managedsystem.get(ms_id)
    vios = cs.virtualioserver.get(ms_id,
                                  vios_id)
    new_virtual_scsi_mapping = []
    for vsm in vios.virtual_scsi_mappings.virtual_scsi_mapping:

        keep = True

        if vsm.associated_logical_partition is not None:
            parts = vsm.associated_logical_partition.split('/')
            cur_ms_id = parts[-3]
            cur_lpar_id = parts[-1]
            if cur_ms_id == ms_id and cur_lpar_id == lpar_id:
                keep = False

        if keep:
            new_virtual_scsi_mapping.append(vsm)

    vios.virtual_scsi_mappings.virtual_scsi_mapping = \
        new_virtual_scsi_mapping
    cs.managedsystem.update(ms, vios)


def retrieve_image_lu(image_lu_name):
    image_lu = None
    for lu in ssp.logical_units.logical_unit:
        if lu.unit_name == image_lu_name:
            image_lu = lu
            break

    if image_lu is None:
        raise Exception("Can't find lu named: >%s<" % (image_lu_name, ))

    return image_lu


def provision_storage(cluster, ssp, image_lu):
    """create an ephemeral LU"""

    dest_lu_unit_name = \
        cs.sharedstoragepool.create_unique_name("P2Z-PROVISION-LU")
    (dest_logicalunit, ssp) = clone_logicalunit(cs,
                                                cluster,
                                                image_lu,
                                                dest_lu_unit_name)

    return ssp, dest_logicalunit


def deletelpar(cs, ms_id, lpar_id):
    cs.managedsystem.deletebyid(ms_id, "LogicalPartition", lpar_id)
    print ("SUCCESS")


def provision_vm(ms, vios, lpar, ephemeral_lu):

    # create map between ephemeral_lu and lpar
    vsm = create_virtual_scsi_mapping(ephemeral_lu, lpar)

    # add the map to the vios
    vios.virtual_scsi_mappings.virtual_scsi_mapping.append(vsm)
    vios = cs.managedsystem.update(ms, vios)

    # get a sea from the vios
    seas = vios.shared_ethernet_adapters.shared_ethernet_adapter
    assert (len(seas) > 0)
    sea = seas[0]

    # get the trunk adapter
    tas = sea.trunk_adapters.trunk_adapter
    assert (len(tas) == 1)
    ta = tas[0]

    # use the switch_id on the trunk adapter to retrieve the virtualswitch
    vs_sid = ta.virtual_switch_id
    vss = cs.virtualswitch.list(ms_id)
    vs_id = None
    for vs in vss:
        if vs.switch_id == vs_sid:
            vs_id = vs.id
    assert (vs_id is not None)

    # create a link to the VirtualSwitch
    x = "%s/ManagedSystem/%s/VirtualSwitch/%s"
    alp = x % (cs.client.getserviceurl("uom"),
               ms_id,
               vs_id)
    vsls = k2uom.VirtualSwitch_Links()
    vsls.link = [alp]

    # use VirtualSwitch to create a ClientNetworkAdapter
    cna = k2uom.ClientNetworkAdapter()
    cna.virtual_slot_number = CNA_VIRTUAL_SLOT_NUMBER
    cna.port_vlan_id = CNA_PORT_VLAN_ID
    cna.quality_of_service_priority_enabled = \
        CNA_QUALITY_OF_SERVICE_PRIORITY_ENABLED
    cna.tagged_vlan_supported = CNA_TAGGED_VLAN_SUPPORTED
    cna.associated_virtual_switch = vsls

    # add the ClientNetworkAdapter to the lpar
    cs.logicalpartition.create(lpar, cna)

if __name__ == '__main__':

# #     N24
#     cluster_id = "ea1b0b5f-3b3a-39dc-bade-6e9cebd18bb2"  # cluster-a
#     ms_id = "f9fe01a6-4fae-37fd-a89d-3ec22252de7a"  # N24
#     vios_id = "1BC0CB5E-15BF-492A-8D06-25B69833B54E"  # 06-6B0FB

#     # N7
#     k2_url = "hmc5.watson.ibm.com"
#     cluster_id = "fe3fbe0f-5ba8-3374-ab75-7b653c9a57ff"  # cluster-b
#     ms_id = "19cb4aaa-2519-3a3e-838a-0c92a57a1d8a"  # N7
#     vios_id = "304F7808-3CFD-4866-BD21-861996B50610"  # 06-6B14B

    # N8
    k2_url = "hmc5.watson.ibm.com"
    cluster_id = "0c737495-d09a-337a-a7e9-6173d4bb6d20"  # cluster-c
    ms_id = "3e4a8465-c347-30d0-9efb-0b7acff66411"  # N8
    vios_id = "5005AAA5-C39F-4E09-93DD-71C01777F9AD"  # 06-6B14B

# #     REJY
#     k2_url = "9.126.139.241"
#     cluster_id = "c43fbdcd-95f2-3b4a-b643-234ff00eded4"  #  TestCluster
#     ms_id = "c604de3f-dc70-3f1e-9e10-c80e3b4db90f"  # falcon
#     vios_id = "5CE26080-DBD8-4205-87AA-E8A5E52F6AE5"  # vios1

    image_lu_name = "RHEL64-A"
    image_lu_name = "RHEL64-WORKING"
    image_lu_name = "RHEL64-IMAGE"
    lpar_name = "P2Z-LPAR".ljust(15, "-")[:15] + uuid.uuid4().hex
    lpar_proc = 1
    lpar_mem = 1024

    k2acfg = k2asample.getk2acfg()
    k2asample.configure_logging(logging.getLevelName(k2acfg['loglevel']))
    cs = client.Client(k2acfg['api_version'],
                       k2_url,  # k2acfg['k2_url'],
                       k2acfg['k2_username'],
                       k2acfg['k2_password'],
                       k2_auditmemento=k2acfg['k2_auditmemento'],
                       k2_certpath=k2acfg['k2_certpath'],
                       retries=k2acfg['retries'],
                       timeout=k2acfg['timeout'],
                       excdir=k2acfg['excdir'])

    try:

        ####
        # get the CEC
        ms = cs.managedsystem.get(ms_id)
        vios = cs.virtualioserver.get(ms.id, vios_id)

        ####
        # get the SSP cluster
        cluster = cs.cluster.get(cluster_id)
        ssp_id = cluster.sharedstoragepool_id()
        ssp = cs.sharedstoragepool.get(ssp_id)

        ####
        # retrieve the image lu from the SSP cluster
        image_lu = retrieve_image_lu(image_lu_name)

        ####
        # use image lu to provision ephemeral lu
        ssp, ephemeral_lu = provision_storage(cluster, ssp, image_lu)

        ####
        # provision an lpar (name, processors, memory)
        lpar = provision_lpar(cs,
                              ms,
                              lpar_name,
                              lpar_proc,
                              lpar_mem)

        ####
        # provision vm onto vios
        provision_vm(ms, vios, lpar, ephemeral_lu)

        ####
        # power on the lpar
        cs.logicalpartition.power_on(lpar)

    except Exception as e:
        logging.exception(e)


#     except Exception as e:
#         print ("FIXME: >%s<" % (e,))
