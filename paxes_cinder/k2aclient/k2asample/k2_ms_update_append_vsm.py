# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
import logging

from paxes_cinder.k2aclient.v1.k2uom import \
    VirtualSCSIMapping, \
    VirtualSCSIServerAdapter, \
    VirtualSCSIClientAdapter


def create_vio_scsi_pair(cs,
                         managedsystem_id,
                         virtualioserver_id,
                         logicalpartition_id):

    # create the link to the LogicalPartition
    alp = "%s/LogicalPartition/%s" % (cs.client.getserviceurl("uom"),
                                      logicalpartition_id)

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

    # add the map to the virtualioserver
    vios = cs.virtualioserver.getasroot(virtualioserver_id)
    vios.virtual_scsi_mappings.virtual_scsi_mapping.append(vsm)

    ms = cs.managedsystem.get(managedsystem_id)
    cs.managedsystem.update(ms, vios)

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
    logicalpartition_id = "16F35FA8-130B-417E-9C61-EEEE080898BC"
    virtualioserver_id = "519F3DBC-074C-4741-9786-4224FF4136BD"

    try:
        create_vio_scsi_pair(cs,
                             managedsystem_id,
                             virtualioserver_id,
                             logicalpartition_id)
    except Exception as e:
        logging.exception(e)
