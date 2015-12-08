#
#
# =================================================================
# =================================================================

"""LogicalPartition interface."""

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient.v1 import k2web

from paxes_cinder.k2aclient.exceptions import K2JobFailure

from eventlet import greenthread


class LogicalPartitionManager(base.ManagerWithFind):
    """Manage :class:`LogicalPartition` resources."""
    resource_class = k2uom.LogicalPartition

    def new(self):
        return self.resource_class(self, None)

    def list(self, managedsystem, xa=None):
        """Get a list of all LogicalPartitions for a particular
        ManagedSystem accessed through a particular hmc.

        :rtype: list of :class:`LogicalPartition`.
        """
        return self._list("/rest/api/uom/ManagedSystem/%s/LogicalPartition"
                          % managedsystem,
                          xa=xa)

    def listasroot(self, xa=None):
        """Get a list of all LogicalPartitions
        accessed through a particular hmc.

        :rtype: list of :class:`LogicalPartition`.
        """
        return self._list("/rest/api/uom/LogicalPartition", xa=xa)

    def get(self, managedsystem, logicalpartition, xa=None):
        """Given managedsytem, get a specific LogicalPartition.

        :param logicalpartition: The ID of the :class:`LogicalPartition`.
        :rtype: :class:`LogicalPartition`
        """
        return self._get("/rest/api/uom/ManagedSystem/%s/LogicalPartition/%s"
                         % (managedsystem, logicalpartition,),
                         xa=xa)

    def getasroot(self, logicalpartition, xa=None):
        """Get a specific LogicalPartition.

        :param logicalpartition: The ID of the :class:`LogicalPartition`.
        :rtype: :class:`LogicalPartition`
        """
        return self._get("/rest/api/uom/LogicalPartition/%s" %
                         logicalpartition,
                         xa=xa)

    def create(self, logicalpartition, child=None, xa=None):
        """Create the specified instance
        """
        return self._create("uom", logicalpartition,
                            child=child,
                            xa=xa)

    def delete(self, logicalpartition, child=None, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom", logicalpartition,
                            child=child,
                            xa=xa)

    def deletebyid(self, logicalpartition_id,
                   child_type=None, child_id=None, xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom", "LogicalPartition", logicalpartition_id,
                                child_type=child_type,
                                child_id=child_id,
                                xa=xa)

########

    def power_on(self, logicalpartition, xa=None):
        """For specified logicalpartition, power it on

        :param logicalpartition_id: Instance of the :class:`LogicalPartition`

        """

        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        jpc = k2web.JobParameter_Collection()

        jrequest = self.api.web_job.getjob(logicalpartition, 'PowerOn',
                                           xa=xa)
        jrequest.job_parameters = jpc

        jresponse = self.api.web_job.runjob(logicalpartition, jrequest,
                                            xa=xa)
        k2respi = jresponse._k2resp

        while jresponse.status == 'NOT_STARTED' or \
                jresponse.status == 'RUNNING':

            greenthread.sleep(1)
            jresponse = self.api.web_job.readjob(jresponse.job_id,
                                                 xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "power_on",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "power_on",
                                                jresponse._k2resp)
            msg = _("k2aclient:"
                    " during power_on,"
                    " for LogicalPartition: >%(logicalpartition.id)s<,"
                    " failed to power on due to"
                    " job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<,"
                    " response k2 job diagnostics have been"
                    " written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"logicalpartition.id": logicalpartition.id,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        return jresponse.status, jresponse.job_id

    def power_off(self, logicalpartition, xa=None):
        """For specified logicalpartition, power it on

        :param logicalpartition_id: Instance of the :class:`LogicalPartition`

        """

        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        jpc = k2web.JobParameter_Collection()

        jp = k2web.JobParameter()
        jp.parameter_name = "operation"
        jp.parameter_value = "shutdown"
        jpc.job_parameter.append(jp)

        jp = k2web.JobParameter()
        jp.parameter_name = "immediate"
        jp.parameter_value = "true"
        jpc.job_parameter.append(jp)

        jrequest = self.api.web_job.getjob(logicalpartition, 'PowerOff',
                                           xa=xa)
        jrequest.job_parameters = jpc

        jresponse = self.api.web_job.runjob(logicalpartition, jrequest,
                                            xa=xa)
        k2respi = jresponse._k2resp

        while jresponse.status == 'NOT_STARTED' or \
                jresponse.status == 'RUNNING':

            greenthread.sleep(1)
            jresponse = self.api.web_job.readjob(jresponse.job_id,
                                                 xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "power_off",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "power_off",
                                                jresponse._k2resp)
            msg = _("k2aclient:"
                    " during power_on,"
                    " for LogicalPartition: >%(logicalpartition.id)s<,"
                    " failed to power on due to"
                    " job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<,"
                    " response k2 job diagnostics have been"
                    " written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"logicalpartition.id": logicalpartition.id,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        return jresponse.status, jresponse.job_id
