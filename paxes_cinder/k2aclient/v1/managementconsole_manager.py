#
#
# =================================================================
# =================================================================

"""MangementConsole interface."""

from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.exceptions import K2JobFailure
from eventlet import greenthread


class ManagementConsoleManager(base.ManagerWithFind):
    """Manage :class:`ManagementConsole` resources."""
    resource_class = k2uom.ManagementConsole

    def list(self, xa=None):
        """Get a list of all ManagementConsoles.

        :rtype: list of :class:`ManagementConsole`.
        """
        return self._list("/rest/api/uom/ManagementConsole", xa=xa)

    def get(self, managementconsole, xa=None):
        """Get a specific ManagementConsole.

        :param managementconsole: The ID of the :class:`ManagementConsole`
            to get.
        :rtype: :class:`ManagementConsole`
        """
        return self._get("/rest/api/uom/ManagementConsole/%s" %
                         managementconsole,
                         xa=xa)

    def run_cmd(self, mc, cmd, xa=None):
        jpc = k2web.JobParameter_Collection()

        jp = k2web.JobParameter()
        jp.parameter_name = "cmd"
        jp.parameter_value = cmd
        jpc.job_parameter.append(jp)

        jp = k2web.JobParameter()
        jp.parameter_name = "acknowledgeThisAPIMayGoAwayInTheFuture"
        jp.parameter_value = 'true'
        jpc.job_parameter.append(jp)

        jrequest = self.api.web_job.getjob(mc, 'CLIRunner',
                                           xa=xa)
        jrequest.job_parameters = jpc

        jresponse = self.api.web_job.runjob(mc, jrequest,
                                            xa=xa)
        k2respi = jresponse._k2resp

        while jresponse.status == 'NOT_STARTED' or \
                jresponse.status == 'RUNNING':

            greenthread.sleep(1)
            jresponse = self.api.web_job.readjob(jresponse.job_id,
                                                 xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "CLIRunner",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "CLIRunner",
                                                jresponse._k2resp)

            msg = _("CLIRunner: ManagementConsole: >%(mc.id)s<, "
                    "failed to run cmd: >%(cmd)s< due to"
                    " job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<, "
                    " response k2 job diagnostics have been"
                    " written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"mc.id": mc.id, "cmd": cmd,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        return jresponse

    def run_vios_cmd(self, mc, ms, vios, cmd, xa=None):
        """Blah blah blah

        :param cluster: The id of the :class:`Cluster` where the
                        logicalunits reside.
        :param source: The id of the source :class:`LogicalUnit`.
        :param destination: The id of the target :class:`LogicalUnit`.

        """

        # viosvrcmd -m <managed-system> --id <partition-ID> \
        #    -c "rmdev -dev HDISKX"

        # https://pic.dhe.ibm.com/infocenter/powersys/v3r1m5/index.jsp
        #   ?topic=%2Fp7ha1%2Fviosvrcmd.htm

        # tttt-mmm*ssssssss
        mtm_and_sn = ms.machine_type_model_and_serial_number
        mt = mtm_and_sn.machine_type
        m = mtm_and_sn.model
        sn = mtm_and_sn.serial_number
        managed_system = "%s-%s*%s" % (mt, m, sn,)

        viosvrcmd = ('viosvrcmd -m %s --id %s -c "%s"' %
                     (managed_system, vios.partition_id, cmd,))

        return self.run_cmd(mc, viosvrcmd, xa=xa)
