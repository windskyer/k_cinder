# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import sys
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient.k2asample import dump_k2resp

from paxes_cinder.k2aclient.v1.shell import K2Encoder
import json

import logging

from paxes_cinder.k2aclient.v1.k2uom import \
    VirtualSCSIMapping, \
    VirtualSCSIServerAdapter, \
    VirtualSCSIClientAdapter, \
    LogicalPartition, \
    LogicalPartitionProfileDedicatedProcessorConfiguration, \
    LogicalPartitionProcessorConfiguration, \
    LogicalPartitionMemoryConfiguration

from eventlet import greenthread


def clean_orphan_mapping_by_vhost(managedsystem_id,
                                  virtualioserver_id,
                                  vhost_name,
                                  doit=False):
    # get the vios
    managedsystem = cs.managedsystem.get(managedsystem_id)
    virtualioserver = cs.virtualioserver.get(managedsystem_id,
                                             virtualioserver_id)

    new_virtual_scsi_mapping = []
    print ("Current VSM:")
    for vsm in virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping:
        if vsm.server_adapter.adapter_name == vhost_name:
            print ("  will delete: vsm.server_adapter.adapter_name: >%s<" %
                   (vsm.server_adapter.adapter_name,))
        else:
            print ("  will keep: vsm.server_adapter.adapter_name: >%s<" %
                   (vsm.server_adapter.adapter_name,))
            new_virtual_scsi_mapping.append(vsm)

    print ("Updated VSM:")
    for vsm in new_virtual_scsi_mapping:
        print ("  vsm.server_adapter.adapter_name: >%s<" %
               (vsm.server_adapter.adapter_name,))

    if doit:
        virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping = \
            new_virtual_scsi_mapping
        cs.managedsystem.update(managedsystem, virtualioserver)


# USE ME!!!!
def clean_orphan_mapping_by_partition_id(managedsystem_id,
                                         virtualioserver_id,
                                         partition_id,
                                         doit=False):
    # get the vios
    managedsystem = cs.managedsystem.get(managedsystem_id)
    virtualioserver = cs.virtualioserver.get(managedsystem_id,
                                             virtualioserver_id)

    new_virtual_scsi_mapping = []
    print ("VSM edits:")
    for vsm in virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping:

        if (vsm.client_adapter is not None and
                vsm.client_adapter.local_partition_id == partition_id):
            msg = "  will delete: vsm.server_adapter.adapter_name: >%s<"
            print (msg % (vsm.server_adapter.adapter_name,))
        else:
            new_virtual_scsi_mapping.append(vsm)
            msg = "  will keep: vsm.server_adapter.adapter_name: >%s<"
            print (msg % (vsm.server_adapter.adapter_name,))

    print ("Updated VSM will be:")
    for vsm in new_virtual_scsi_mapping:
        msg = "  vsm.server_adapter.adapter_name: >%s<"
        print (msg % (vsm.server_adapter.adapter_name,))

    if doit:
        virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping = \
            new_virtual_scsi_mapping
        cs.managedsystem.update(managedsystem, virtualioserver)


def clean_orphan_mapping_by_partition_id_on_server(managedsystem_id,
                                                   virtualioserver_id,
                                                   partition_id,
                                                   doit=False):
    # get the vios
    managedsystem = cs.managedsystem.get(managedsystem_id)
    virtualioserver = cs.virtualioserver.get(managedsystem_id,
                                             virtualioserver_id)

    new_virtual_scsi_mapping = []
    print ("VSM edits:")
    for vsm in virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping:

        if (vsm.server_adapter is not None and
                vsm.server_adapter.remote_logical_partition_id
                == partition_id):
            msg = "  will delete: vsm.server_adapter.adapter_name: >%s<"
            print (msg % (vsm.server_adapter.adapter_name,))
        else:
            new_virtual_scsi_mapping.append(vsm)
            msg = "  will keep: vsm.server_adapter.adapter_name: >%s<"
            print (msg % (vsm.server_adapter.adapter_name,))

    print ("Updated VSM will be:")
    for vsm in new_virtual_scsi_mapping:
        msg = "  vsm.server_adapter.adapter_name: >%s<"
        print (msg % (vsm.server_adapter.adapter_name,))

    if doit:
        if len(new_virtual_scsi_mapping) != \
                len(virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping
                    ):
            virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping = \
                new_virtual_scsi_mapping
            cs.managedsystem.update(managedsystem, virtualioserver)


# USE ME!!!!
def clean_orphan_mapping_by_lpar_id(ms_id,
                                    vios_id,
                                    lpar_id,
                                    doit=False):
    # get the vios
    managedsystem = cs.managedsystem.get(ms_id)
    virtualioserver = cs.virtualioserver.get(ms_id,
                                             vios_id)

    new_virtual_scsi_mapping = []
    print ("VSM edits:")
    for vsm in virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping:

        ####
#         if vsm.client_adapter\
#                 is not None and\
#                 vsm.client_adapter.associated_logical_partition\
#                 is not None:
        keep = True
        if vsm.associated_logical_partition is not None:
            parts = vsm.associated_logical_partition.split('/')
            cur_ms_id = parts[-3]
            cur_lpar_id = parts[-1]
            if cur_ms_id == ms_id and cur_lpar_id == lpar_id:
                keep = False
                msg = "  will delete: vsm.server_adapter.adapter_name: >%s<"
                print (msg % (vsm.server_adapter.adapter_name,))

        if keep:
            new_virtual_scsi_mapping.append(vsm)
            msg = "  will keep: vsm.server_adapter.adapter_name: >%s<"
            print (msg % (vsm.server_adapter.adapter_name,))

    print ("Updated VSM will be:")
    for vsm in new_virtual_scsi_mapping:
        msg = "  vsm.client_adapter.adapter_name: >%s<"
        print (msg % (vsm.server_adapter.adapter_name,))

    if doit:
        if len(new_virtual_scsi_mapping) != \
                len(virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping
                    ):
            virtualioserver.virtual_scsi_mappings.virtual_scsi_mapping = \
                new_virtual_scsi_mapping
            cs.managedsystem.update(managedsystem, virtualioserver)


def power_off(managedsystem_id, logicalpartition_id, force_immediate=False):
    lp = cs.logicalpartition.get(managedsystem_id, logicalpartition_id)
    jrequest = cs.web_job.getjob(lp, 'PowerOff')
    jpc = k2web.JobParameter_Collection()
    jrequest.job_parameters = jpc

#     # dlpar_capable
#     m_capable = lp.partition_capabilities.\
#         dynamic_logical_partition_memory_capable == "true"
#     p_capable = lp.partition_capabilities.\
#         dynamic_logical_partition_processor_capable == "true"
#     dlpar_capable = m_capable and p_capable

    if force_immediate:
        print ("immediate")
        # shutdown
        jp = k2web.JobParameter()
        jp.parameter_name = 'operation'
        jp.parameter_value = 'shutdown'
        jpc.job_parameter.append(jp)
        # immediate
        jp = k2web.JobParameter()
        jp.parameter_name = 'immediate'
        jp.parameter_value = 'true'
        jpc.job_parameter.append(jp)

    elif lp.resource_monitoring_control_state == "active":
        print ("active")
        # osshutdown
        jp = k2web.JobParameter()
        jp.parameter_name = 'operation'
        jp.parameter_value = 'osshutdown'
        jpc.job_parameter.append(jp)
    else:
        print ("normal")
        # shutdown
        jp = k2web.JobParameter()
        jp.parameter_name = 'operation'
        jp.parameter_value = 'shutdown'
        jpc.job_parameter.append(jp)

    jresponse = cs.web_job.runjob(lp, jrequest)

    while jresponse.status == 'NOT_STARTED' or \
            jresponse.status == 'RUNNING':
        print ("  ... power off job status: >%s<" % (jresponse.status,))
        greenthread.sleep(1)
        jresponse = cs.web_job.readjob(jresponse.job_id)

    dump_k2resp("poweroff", jresponse._k2resp, "/tmp/power_off.k2r")

    print ("Final power_off job status: >%s<" % (jresponse.status,))


def power_on(managedsystem_id, logicalpartition_id):
    logicalpartition = cs.logicalpartition.get(managedsystem_id,
                                               logicalpartition_id)

    jrequest = cs.web_job.getjob(logicalpartition, 'PowerOn')
    jresponse = cs.web_job.runjob(logicalpartition, jrequest)

    while jresponse.status == 'NOT_STARTED' or \
            jresponse.status == 'RUNNING':
        print ("  ... power on job status: >%s<" % (jresponse.status,))
        greenthread.sleep(1)
        jresponse = cs.web_job.readjob(jresponse.job_id)

    print ("Final power_on job status: >%s<" % (jresponse.status,))


if __name__ == '__main__':

    k2_url = "hmc5.watson.ibm.com"

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

#     cluster_id = "0e4b8ba2-8bd0-33cf-a077-250a2e194b75"  # cluster-d
#     managedsystem_id = "19cb4aaa-2519-3a3e-838a-0c92a57a1d8a"  # N7
#     virtualioserver_id = "304F7808-3CFD-4866-BD21-861996B50610"

    cluster_id = "c38db666-ba8c-35d0-9fa6-d2bf0cc5ea4b"  # cluster-e
    managedsystem_id = "f9fe01a6-4fae-37fd-a89d-3ec22252de7a"  # N24
    virtualioserver_id = "1BC0CB5E-15BF-492A-8D06-25B69833B54E"  # 06-6B0FB
    logicalpartition_id = "264169B9-1B2A-4C7E-BECA-D9325847BB7B"

    cluster_id = "0e86e492-42eb-32e3-bb11-e8f25d5e6e37"  # cluster-b
    managedsystem_id = "19cb4aaa-2519-3a3e-838a-0c92a57a1d8a"  # N7
    virtualioserver_id = "304F7808-3CFD-4866-BD21-861996B50610"  # 06-6B14B

    logicalunit_id = ("27b3eab938373a11e383980090fa1"
                      "31fae1b2c68635c631ff2d378875caa6671e9")

    logicalpartition_id = "18B0BE21-C130-489C-A13D-4AF78A5EA32F"
    logicalpartition_id = "7E1CC110-9921-4C27-A6E4-2757A946B76D"
    logicalpartition_id = "5005AAA5-C39F-4E09-93DD-71C01777F9AD"

    try:

        ####
        if False:
            power_off(managedsystem_id, logicalpartition_id,
                      force_immediate=True)

        ####
        if False:
            power_on(managedsystem_id, logicalpartition_id)

        ########
        #### Cleanup
        ####
        # based on 1/25/14 review cleanup mapping based on
        #  VIOS's mapping client_adapter.local_partition_id ==
        #  LPAR's partition_id

        if False:
            partition_id = "3"
            clean_orphan_mapping_by_partition_id(managedsystem_id,
                                                 virtualioserver_id,
                                                 partition_id,
                                                 doit=False)
        if False:
            partition_id = "6"
            clean_orphan_mapping_by_partition_id_on_server(managedsystem_id,
                                                           virtualioserver_id,
                                                           partition_id,
                                                           doit=True)
            partition_id = "10"
            clean_orphan_mapping_by_partition_id_on_server(managedsystem_id,
                                                           virtualioserver_id,
                                                           partition_id,
                                                           doit=True)
            partition_id = "14"
            clean_orphan_mapping_by_partition_id_on_server(managedsystem_id,
                                                           virtualioserver_id,
                                                           partition_id,
                                                           doit=True)

        if True:
            # N8
            cluster_id = "0c737495-d09a-337a-a7e9-6173d4bb6d20"  # cluster-c
            managedsystem_id = "3e4a8465-c347-30d0-9efb-0b7acff66411"  # N8
            virtualioserver_id = \
                "5005AAA5-C39F-4E09-93DD-71C01777F9AD"  # 06-6B14B
            logicalpartition_id = "00A9083E-8D39-4D07-B777-9D522B4A8F4B"

#             # N7
#             k2_url = "hmc5.watson.ibm.com"
#             cluster_id = "29915d6b-86af-3fdd-8a8d-fea6cab1dc91"  # cluster-b
#             managedsystem_id = "19cb4aaa-2519-3a3e-838a-0c92a57a1d8a"  # N7
            virtualioserver_id = \
                "304F7808-3CFD-4866-BD21-861996B50610"  # 06-6B14B

            clean_orphan_mapping_by_lpar_id(managedsystem_id,
                                            virtualioserver_id,
                                            logicalpartition_id,
                                            doit=True)

        ####
        if False:
            vhost_name = "vhost24"
            clean_orphan_mapping_by_vhost(managedsystem_id,
                                          virtualioserver_id,
                                          vhost_name,
                                          doit=True)

        if False:
            # find SEAS
            seas = []
            vioss = cs.virtualioserver.list(managedsystem_id)
            assert (len(vioss) == 1)
            for vios in vioss:
                for sea in \
                        vios.shared_ethernet_adapters.shared_ethernet_adapter:
                    seas.append((vios, sea))

            # in our current setup only one sea per cec
            assert (len(seas) == 1)

#             json.dump(seas[0], sys.stdout, sort_keys=True, indent=4,
#                       cls=K2Encoder)

            (vios, sea) = seas[0]
            tas = sea.trunk_adapters.trunk_adapter
            assert (len(tas) == 1)
            ta = tas[0]
#             json.dump(ta, sys.stdout, sort_keys=True, indent=4,
#                       cls=K2Encoder)
            vs_sid = ta.virtual_switch_id

            vss = cs.virtualswitch.list(managedsystem_id)
            for vs in vss:
                if vs.switch_id == vs_sid:
                    vs_id = vs.id

            # create the link to the VirtualSwitch
            x = "%s/ManagedSystem/%s/VirtualSwitch/%s"
            alp = x % (cs.client.getserviceurl("uom"),
                       managedsystem_id,
                       vs_id)

            vsls = k2uom.VirtualSwitch_Links()
            vsls.link = [alp]

            pvid = "3160"
            vsn = "3"
#             "port_vlan_id": "3160",

            cna = k2uom.ClientNetworkAdapter()
            cna.virtual_slot_number = "3"  # hardcoded
            cna.port_vlan_id = "3160"  # hardcoded
            cna.quality_of_service_priority_enabled = "false"
            cna.tagged_vlan_supported = "false"
            cna.associated_virtual_switch = vsls

            # P2Z-PROVISION-LPAR-A
            lpar_id = "208D32BD-334E-4FEE-8264-E424E2DC72D4"
            lpar = cs.logicalpartition.get(managedsystem_id, lpar_id)
            cs.logicalpartition.create(lpar, cna)

    except Exception as e:
        logging.exception(e)
