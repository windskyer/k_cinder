#
#
# =================================================================
# =================================================================

"""Web File interface."""

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient import exceptions

from paxes_k2.k2operator import K2Error

import hashlib


def _sha256sum(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * sha256.block_size), b''):
            sha256.update(chunk)
        return sha256.hexdigest()


class FileManager(base.ManagerWithFind):
    """Manage :class:`Cluster` resources."""
    resource_class = k2web.File

    def list(self, xa=None):
        """Get a list of all files.

        :rtype: list of :class:`Files`.
        """
        return self._list("/rest/api/web/File", xa=xa)

    def get(self, f, xa=None):
        """Get a specific file.

        :param file: The id of the :class:`file` to get.
        :rtype: :class:`File`
        """
        return self._get("/rest/api/web/File/%s" % f, xa=xa)

    def delete(self, f, xa=None):
        """Delete the specified instance
        """
        return self._delete("web", f, child=None, xa=xa)

    def deletebyid(self, file_id, xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("web", "File", file_id,
                                child_type=None, child_id=None,
                                xa=xa)

    def create(self, f, child=None, xa=None):
        """Create the specified instance
        """
        return self._create("web", f, child, xa=xa)

    #####
    # Non-CRUD
    def upload(self,
               wf,
               filelike,
               xa=None):
        """Upload a file to the HMC.

        filelike  a file-like object."""

        oper = self.api.client.k2operator
        fd = wf.k2resp.entry.element
        try:
            k2resp = oper.uploadfile(fd, filelike, auditmemento=xa)
        except K2Error as e:
            msg = _("k2aclient:"
                    " during file upload,"
                    " filename: >%(wf.filename)s<, id:"
                    " >%(wf.id)s<, file_uuid: >%(wf.file_uuid)s<,"
                    " file_enum_type: >%(wf.file_enum_type)s<")
            addmsg = msg % {"wf.filename": wf.filename, "wf.id": wf.id,
                            "wf.file_uuid": wf.file_uuid,
                            "wf.file_enum_type": wf.file_enum_type, }
            x = exceptions.create_k2a_exception_from_k2o_exception
            raise x(e, addmsg=addmsg, exclogger=self.api.exclogger)
        return k2resp
