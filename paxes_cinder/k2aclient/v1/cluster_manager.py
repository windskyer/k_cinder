#
#
# =================================================================
# =================================================================

"""Cluster interface."""

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.openstack.common import lockutils

from paxes_cinder.k2aclient.exceptions import K2JobFailure

from eventlet import greenthread

import time

import logging
LOG = logging.getLogger(__name__)


synchronized = lockutils.synchronized_with_prefix('k2a-')


def _parse_vios(node_vios):
    node_parts = node_vios.split('/')
    ms_id = node_parts[-3]
    vios_id = node_parts[-1]
    return ms_id, vios_id


class ClusterManager(base.ManagerWithFind):
    """Manage :class:`Cluster` resources."""
    resource_class = k2uom.Cluster

    def list(self, xa=None):
        """Get a list of all clusters.

        :rtype: list of :class:`Cluster`.
        """
        return self._list("/rest/api/uom/Cluster", xa=xa)

    def get(self, cluster, xa=None):
        """Get a specific cluster.

        :param Cluster: The id of the :class:`cluster` to get.
        :rtype: :class:`Cluster`
        """
        return self._get("/rest/api/uom/Cluster/%s" % cluster,
                         xa=xa)

    def refresh(self, cluster, xa=None):
        """Refresh specified instance.
        If instance is current return input cluster, otherwise return updated
        cluster.
        :param ssp: An instance of :class:`SharedStoragePool`.
        :rtype: :class:`SharedStoragePool`
        """
        current_cluster = self._refresh("uom",
                                        cluster,
                                        child=None,
                                        xa=xa)
        if current_cluster is not None:
            cluster = current_cluster
        return cluster

    def lu_linked_clone_of_lu_bp(
            self,
            cluster,
            ssp,
            source_lu_udid,
            dest_lu_unit_name,
            dest_lu_unit_capacity=None,
            dest_lu_thin_device=None,
            dest_lu_logical_unit_type="VirtualIO_Disk",
            xa=None,
            times=None):
        """Create a new destination LU and linked_clone the source to it.
        If the underlying K2 linked_clone operation should fail, attempt to
        remove the new destination LU."""

        if times is not None:
            times.append(time.time())

        source_lu = None
        for lu in ssp.logical_units.logical_unit:
            if lu.unique_device_id == source_lu_udid:
                source_lu = lu
        if source_lu is None:
            msg = _("k2aclient:"
                    " during lu_linked_clone_of_lu,"
                    " source_lu_udid: >%(source_lu_udid)s<,"
                    " not in sharedstoragepool: >%(ssp.id)s<")
            raise ValueError(msg %
                             {"source_lu_udid": source_lu_udid,
                              "ssp.id": ssp.id, })
        if dest_lu_unit_capacity is None:
            dest_lu_unit_capacity = source_lu.unit_capacity

        if dest_lu_thin_device is None:
            dest_lu_thin = True
            if source_lu.thin_device == "false":
                dest_lu_thin = False
        elif dest_lu_thin_device:
            dest_lu_thin = True
        else:
            dest_lu_thin = False

        dest_lu, updated_ssp = \
            ssp.update_append_lu(dest_lu_unit_name,
                                 dest_lu_unit_capacity,
                                 dest_lu_thin,
                                 dest_lu_logical_unit_type,
                                 xa=xa)

        if times is not None:
            times.append(time.time())
            times[-2] = times[-1] - times[-2]

        status, job_id = self.lu_linked_clone(
            cluster,
            source_lu_udid,
            dest_lu.unique_device_id,
            xa=xa)
        if status != "COMPLETED_OK":
            dest_lu = None

        if times is not None:
            times[-1] = time.time() - times[-1]

        return status, dest_lu, updated_ssp, job_id

    def lu_linked_clone_of_lu_bj(
            self,
            cluster,
            source_lu,
            dest_lu_unit_name,
            dest_lu_unit_capacity=None,
            dest_lu_thin_device=None,
            dest_lu_logical_unit_type="VirtualIO_Disk",
            xa=None):
        """Create a new destination LU cloned from existing source_lu_udid.
        """

        if dest_lu_unit_capacity is None:
            dest_lu_unit_capacity = source_lu.unit_capacity

        if dest_lu_thin_device is None:
            dest_lu_thin = True
            if source_lu.thin_device == "false":
                dest_lu_thin = False
        elif dest_lu_thin_device:
            dest_lu_thin = True
        else:
            dest_lu_thin = False

        status, dest_lu_udid, job_id = self.lu_create(
            cluster,
            dest_lu_unit_name,
            dest_lu_unit_capacity,
            thin=dest_lu_thin,
            logicalunittype=dest_lu_logical_unit_type,
            clonedfrom=source_lu.unique_device_id,
            xa=xa)
        if status != "COMPLETED_OK":
            dest_lu_udid = None

        return status, dest_lu_udid, job_id

    @synchronized('update_lus')
    def lu_linked_clone(self, cluster, source, destination, xa=None):
        """For specified cluster, clone the source logicalunit
        to the destination logicalunit.

        :param cluster: The id of the :class:`Cluster` where the
                        logicalunits reside.
        :param source: The id of the source :class:`LogicalUnit`.
        :param destination: The id of the target :class:`LogicalUnit`.

        """

        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        sourceUDID = source
        destinationUDID = destination

        jpc = k2web.JobParameter_Collection()

        jp = k2web.JobParameter()
        jp.parameter_name = "SourceUDID"
        jp.parameter_value = sourceUDID
        jpc.job_parameter.append(jp)

        jp = k2web.JobParameter()
        jp.parameter_name = "DestinationUDID"
        jp.parameter_value = destinationUDID
        jpc.job_parameter.append(jp)

        k2respi, jresponse = self.api.web_job.runandpolljob(
            cluster,
            "LULinkedClone",
            jpc=jpc,
            maxretries=3,
            sleepbetweenretries=30,
            xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "lu_linked_clone",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "lu_linked_clone",
                                                jresponse._k2resp)
            msg = _("k2aclient:"
                    " for cluster id : >%(cluster.id)s<, "
                    " during lu_linked_clone,"
                    " for SourceUDID: >%(sourceUDID)s<,"
                    " and DestinationUDID: >%(destinationUDID)s<,"
                    " experienced job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<,"
                    " response k2 job diagnostics have been"
                    " written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"cluster.id": cluster.id,
                                "sourceUDID": sourceUDID,
                                "destinationUDID": destinationUDID,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        return jresponse.status, jresponse.job_id

    @synchronized('update_lus')
    def lu_create(self,
                  cluster,
                  lu_unit_name,
                  lu_unit_capacity,
                  thin=True,
                  logicalunittype="VirtualIO_Disk",
                  clonedfrom=None,
                  xa=None):
        """For specified cluster, create a logicalunit

        :param cluster: The id of the :class:`Cluster` where the
                        logicalunits reside.
        :param lu_unit_name:
            The UnitName of the new :class:`LogicalUnit`
        :param lu_unit_capacity: T
            The UnitCapicty of the new :class:`LogicalUnit`.
            In GB
        :param thin:
            Boolean indicating thin or thick.
        :param logicalunittype:
            String indicating LU type
                VirtualIO_Disk
                VirtualIO_Hibernation
                VirtualIO_Image
                VirtualIO_Active_Memory_Sharing
        :param clonedfrom:
            The udid of the source disk, None if not cloned
        """

        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        jpc = k2web.JobParameter_Collection()

        # LUName
        jp = k2web.JobParameter()
        jp.parameter_name = "LUName"
        jp.parameter_value = lu_unit_name
        jpc.job_parameter.append(jp)

        # LUSize
        jp = k2web.JobParameter()
        jp.parameter_name = "LUSize"
        jp.parameter_value = lu_unit_capacity
        jpc.job_parameter.append(jp)

        # LUType
        jp = k2web.JobParameter()
        jp.parameter_name = "LUType"
        if thin:
            jp.parameter_value = "THIN"  # DEFAULT
        else:
            jp.parameter_value = "THICK"
        jpc.job_parameter.append(jp)

        # DeviceType
        jp = k2web.JobParameter()
        jp.parameter_name = "DeviceType"
        jp.parameter_value = logicalunittype
        jpc.job_parameter.append(jp)

        # ClonedFrom
        if clonedfrom is not None:
            jp = k2web.JobParameter()
            jp.parameter_name = "ClonedFrom"
            jp.parameter_value = clonedfrom
            jpc.job_parameter.append(jp)

#         # TierUDID
#         jp = k2web.JobParameter()
#         jp.parameter_name = "TierUDID"
#         jp.parameter_value = xxxx
#         jpc.job_parameter.append(jp)

        k2respi, jresponse = self.api.web_job.runandpolljob(
            cluster,
            "CreateLogicalUnit",
            jpc=jpc,
            maxretries=3,
            sleepbetweenretries=30,
            xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "lu_create",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "lu_create",
                                                jresponse._k2resp)
            msg = _("k2aclient:"
                    " for cluster id : >%(cluster.id)s<, "
                    " during lu_create,"
                    " for lu_unit_name: >%(lu_unit_name)s<,"
                    " with lu_unit_capacity: >%(lu_unit_capacity)s<,"
                    " experienced job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<,"
                    " response k2 job diagnostics have been"
                    " written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"cluster.id": cluster.id,
                                "lu_unit_name": lu_unit_name,
                                "lu_unit_capacity": lu_unit_capacity,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        lu_new_udid = None
        if jresponse.results and jresponse.results.job_parameter:
            for jp in jresponse.results.job_parameter:
                if jp.parameter_name == "LUCreated":
                    lu_new_udid = jp.parameter_value

        return jresponse.status, lu_new_udid, jresponse.job_id

    @staticmethod
    def extract_vios(cluster):
        """Convenience fundtion, for specified cluster,
        return list of ms and list of vios
        """
        ms_ids = []
        vios_ids = []
        for node in cluster.node.node:
            if not node.virtual_io_server:
                continue
            ms_id, vios_id = _parse_vios(node)
            ms_ids.append(ms_id)
            vios_ids.append(vios_id)

    def extract_vios_ips(self, cluster, xa=None):
        """Convenience function, for specified cluster,
        return list of vios ips
        """

        vios_ips = []
        for node in cluster.node.node:
            if not node.virtual_io_server:
                pass

            ms_id, vios_id = _parse_vios(node.virtual_io_server)
            vios = self.api.\
                virtualioserver.get(ms_id,
                                    vios_id,
                                    xag=["None"],
                                    xa=xa)

            vios_ips.append(vios.resource_monitoring_ip_address)

        return vios_ips
