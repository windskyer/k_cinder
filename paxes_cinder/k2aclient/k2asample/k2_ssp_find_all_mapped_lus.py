# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# =================================================================
# =================================================================


from __future__ import print_function
import paxes_cinder.k2aclient.k2asample as k2asample
from paxes_cinder.k2aclient import client
from paxes_cinder.k2aclient.v1 import k2uom
import logging

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

    # N7
    cluster_id = "0e86e492-42eb-32e3-bb11-e8f25d5e6e37"  # cluster-b
#     # cluster-b-pool
#     sharedstoragepool_id = "1ce0511b-4b46-3bc7-adfa-4f4e965e1e80"
#     managedsystem_id = "19cb4aaa-2519-3a3e-838a-0c92a57a1d8a"  # N7
#     virtualioserver_id = "304F7808-3CFD-4866-BD21-861996B50610"  # 06-6B14B

    try:
        mapped_lus = []
        cluster = cs.cluster.get(cluster_id)
        for node in cluster.node.node:
            node_parts = node.virtual_io_server.split('/')
            ms_id = node_parts[-3]
            vios_id = node_parts[-1]
            vios = cs.virtualioserver.get(ms_id, vios_id)
            for vsm in vios.virtual_scsi_mappings.virtual_scsi_mapping:
                if ((vsm.storage is not None and
                     isinstance(vsm.storage, k2uom.LogicalUnit) and
                     vsm.storage.logical_unit_type == "VirtualIO_Disk")):
                    mapped_lus.append(vsm.storage.unique_device_id)
        mapped_lus = set(mapped_lus)
        print (len(mapped_lus))

#                         print ("FOUND")
    except Exception as e:
        logging.exception(e)


#     except Exception as e:
#         print ("FIXME: >%s<" % (e,))
