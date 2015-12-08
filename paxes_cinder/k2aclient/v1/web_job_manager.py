#
#
# =================================================================
# =================================================================

"""Web Job interface."""

from eventlet import greenthread
from paxes_cinder.k2aclient import base

import logging
LOG = logging.getLogger(__name__)


class JobManager(base.Manager):
    """Manage web jobs."""
    resource_class = None

    def getjob(self, resource, jobname, xa=None):
        return self._getjob(resource, jobname, xa=xa)

    def runjob(self, resource, jobrequest, xa=None):
        return self._runjob(resource, jobrequest, xa=xa)

    def readjob(self, job_id, xa=None):
        return self._readjob(job_id, xa=xa)

    def runandpolljob(
            self,
            jobhome,
            jobtype,
            jpc=None,
            maxretries=3,
            sleepbetweenretries=10,
            xa=None):

        retries = 0
        retry = True
        while retry:
            jrequest = self.api.web_job.getjob(jobhome,
                                               jobtype,
                                               xa=xa)

            if jpc:
                jrequest.job_parameters = jpc

            jresponse = self.api.web_job.runjob(jobhome,
                                                jrequest,
                                                xa=xa)
            k2respi = jresponse._k2resp
            retry = False
            while (jresponse.status == 'NOT_STARTED' or
                   jresponse.status == 'RUNNING' or
                   jresponse.status == 'FAILED_BEFORE_COMPLETION_RETRY'):

                if jresponse.status == 'FAILED_BEFORE_COMPLETION_RETRY':
                    retries += 1
                    if retries < maxretries:
                        msg = _("k2aclient:"
                                " during %(jobtype)s,"
                                " retry job,"
                                " job_id: >%(job_id)s<,"
                                " status: >%(status)s<,")
                        LOG.warn(msg % {"jobtype": jobtype,
                                        "job_id": jresponse.job_id,
                                        "status": jresponse.status, }
                                 )
                        greenthread.sleep(sleepbetweenretries)
                        retry = True
                    else:
                        msg = _("k2aclient:"
                                " during %(jobtype)s,"
                                " too many retries,"
                                " maximum number of retries: >%(maxretries)d<,"
                                " job_id: >%(job_id)s<,"
                                " status: >%(status)s<,")
                        LOG.error(msg % {"jobtype": jobtype,
                                         "maxretries": maxretries,
                                         "job_id": jresponse.job_id,
                                         "status": jresponse.status, })
                    break  # FAILED_BEFORE_COMPLETION_RETRY

                greenthread.sleep(1)
                jresponse = self.api.web_job.readjob(jresponse.job_id,
                                                     xa=xa)
        return k2respi, jresponse
