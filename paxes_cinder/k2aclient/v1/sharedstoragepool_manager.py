#
#
# =================================================================
# =================================================================

"""SharedStoragePool interface."""

import uuid
import logging

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient import exceptions
from paxes_cinder.k2aclient.openstack.common import lockutils

_logger = logging.getLogger(__name__)

synchronized = lockutils.synchronized_with_prefix('k2a-')


class SharedStoragePoolManager(base.ManagerWithFind):
    """Manage :class:`SharedStoragePool` resources."""
    resource_class = k2uom.SharedStoragePool

    @staticmethod
    def create_unique_name(name):
        # add uuid to name
        # per SW243522, utility to limit name to 64 characters
        name = name.ljust(32, "-")[:32] + uuid.uuid4().hex
        return name

    def list(self, xa=None):
        """Get a list of all SharedStoragePools.

        :rtype: list of :class:`SharedStoragePool`.
        """
        return self._list("/rest/api/uom/SharedStoragePool", xa=xa)

    def get(self, sharedstoragepool, xa=None):
        """Get a specific SharedStoragePool.

        :param sharedstoragepool: The id of the :class:`SharedStoragePool`.
        :rtype: :class:`SharedStoragePool`
        """
        return self._get("/rest/api/uom/SharedStoragePool/%s" %
                         sharedstoragepool, xa=xa)

    def refresh(self, sharedstoragepool, xa=None):
        """Refresh specified instance.
        If instance is current return input sharedstoragepool,
        otherwise return updated sharedstoragepool.
        :param ssp: An instance of :class:`SharedStoragePool`.
        :rtype: :class:`SharedStoragePool`
        """
        current_ssp = self._refresh("uom",
                                    sharedstoragepool,
                                    child=None,
                                    xa=xa)
        if current_ssp is not None:
            sharedstoragepool = current_ssp
        return sharedstoragepool

    def update(self, sharedstoragepool, child=None, xa=None):
        """Update the specified instance
        """
        return self._update("uom", sharedstoragepool,
                            child=child, xa=xa)

    def delete(self, sharedstoragepool, child=None, xa=None):
        """Delete the specified instance
        """
        return self._delete("uom", sharedstoragepool,
                            child=child, xa=xa)

    def deletebyid(self, sharedstoragepool_id,
                   child_type=None, child_id=None, xa=None):
        """Delete the specified instance
        """
        return self._deletebyid("uom",
                                "SharedStoragePool",
                                sharedstoragepool_id,
                                child_type=child_type,
                                child_id=child_id,
                                xa=xa)

    @synchronized('update_lus')
    def update_append_lus(self, ssp, inlus, xa=None):
        """For specified sharedstoragepool, add logicalunits
        :param ssp: The :class:`SharedStoragePool`.
        :param inlus: One or more tuples (unitname, unitcapacity, thin, type,
                                          clonedfrom)
            :unitname: The UnitName of the new :class:`LogicalUnit`
            :unitcapacity: The UnitCapicty of the new :class:`LogicalUnit`
            :thin: Boolean indicating thin or thick
            :type: String indicating LU type
                VirtualIO_Disk
                VirtualIO_Hibernation
                VirtualIO_Image
                VirtualIO_Active_Memory_Sharing
            :clonedfrom: The udid of the source disk, None if not cloned
        :rtype: (new list of :class:`LogicalUnit, u :class:`SharedStoragePool)
        """

        if not ssp.k2resp_isfor_k2entry:
            msg = _("k2aclient:"
                    " during updated_append_lus,"
                    " cannot update K2 object(s)"
                    " obtained from a list operation,"
                    " for ssp: >%s<")
            raise ValueError(msg % ssp.id)

        # no logical units specified
        if len(inlus) == 0:
            return (ssp, [])

        # check values permitting thin to default
        lus = []
        for inlu in inlus:
            leninlu = len(inlu)
            if leninlu == 2:
                l0 = inlu[0]
                l1 = str(inlu[1])
                l2 = "true"
                l3 = "VirtualIO_Disk"
                l4 = None
            elif leninlu == 3:
                l0 = inlu[0]
                l1 = str(inlu[1])
                l2 = "false"
                if inlu[2]:
                    l2 = "true"
                l3 = "VirtualIO_Disk"
                l4 = None
            elif leninlu == 4:
                l0 = inlu[0]
                l1 = str(inlu[1])
                l2 = "false"
                if inlu[2]:
                    l2 = "true"
                l3 = inlu[3]
                l4 = None
            elif leninlu == 5:
                l0 = inlu[0]
                l1 = str(inlu[1])
                l2 = "false"
                if inlu[2]:
                    l2 = "true"
                l3 = inlu[3]
                l4 = inlu[4]
            else:
                msg = _("k2aclient:"
                        " during updated_append_lus,"
                        " wrong length of lu input tuple: >%d<")
                raise ValueError(msg % len(inlu))
            lus.append((l0, l1, l2, l3, l4))

        # if  necessary, authenticate
        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        # prime the update logic
        prev_ssp = ssp
#         # following line is work around for SW222953 SW239525
#         prev_ssp = self.get(ssp.id)

        attempts = 0
        tryagain = True
        while tryagain:
            tryagain = False
            # function-specific begin
            # track lus to find what was added
            lus_for_update = prev_ssp.logical_units.logical_unit
            existing_unit_names = [lu.unit_name for lu in lus_for_update]

#  SW239525
#             existing_luids = []
#             for lu in prev_ssp.logical_units.logical_unit:
#                 print "XXXX", lu.unit_name, lu.unique_device_id
#                 existing_luids.append(lu.unique_device_id)

            # add new LUs to existing LUs
            new_unit_names = []
            for unitname, unitcapacity, td, lut, cf in lus:
                if unitname in existing_unit_names:
                    msg = _("k2aclient: "
                            " during updated_append_lus,"
                            " request to add LU unit_name: >%s< failed,"
                            " name must be unique")
                    raise ValueError(msg % unitname)
                new_unit_names.append(unitname)

                new_lu = k2uom.LogicalUnit()
                new_lu.unit_name = unitname
                new_lu.unit_capacity = unitcapacity
                new_lu.thin_device = td
                new_lu.logical_unit_type = lut
                if cf is not None:
                    new_lu.cloned_from = cf
                lus_for_update.append(new_lu)

            attempts += 1
            try:
                msg = ("k2aclient:"
                       " during updated_append_lus,"
                       " adding LUs named: >%s<,"
                       " add attempt #: >%d<"
                       " max retries: >%d<")
                _logger.debug(msg,
                              ",".join([lu[0] for lu in lus]),
                              attempts,
                              self.api.retries)
                updated_ssp = self.update(prev_ssp, xa=xa)
#                 print krl.emit("OK", "RETRY", updated_ssp.k2resp)  SW239525

            except exceptions.K2aK2ErrorPreConditionFailed:
                if attempts > self.api.retries:
                    msg = _("k2aclient:"
                            " during updated_append_lus,"
                            " while adding LUs named: >%(lunames)s<, "
                            " # attempts due to HTTP 412 exceeded:"
                            " >%(self.api.retries)d<")
                    _logger.warn(msg % {"lunames": ",".join([lu[0]
                                                             for lu in lus]),
                                        "self.api.retries": self.api.retries, }
                                 )
                    raise
                # get a more recent ssp for retry
                prev_ssp = self.get(prev_ssp.id, xa=xa)
                msg = ("k2aclient:"
                       " during updated_append_lus,"
                       " while adding LUs named: >%s<, "
                       " for attempt #: >%d<, "
                       " received HTTP 412, will retry ...")
                lunames = ",".join([lu[0] for lu in lus])
                _logger.debug(msg, lunames, attempts)
#                 print "SW239525 TRYAGAIN: >%d<" %(attempts,)
                tryagain = True
            except Exception:
                raise

        # compare previous to updated
        new_lus = []
        lustoadd = len(lus)
        for lu in updated_ssp.logical_units.logical_unit:
#             print "YYYY", lu.unit_name, lu.unique_device_id  SW239525
            if lu.unit_name in new_unit_names:
                new_lus.append(lu)
                lustoadd -= 1

        if lustoadd != 0:
            lunames = ",".join(x[0] for x in lus)
            if lustoadd > 0:
                msg = _("k2aclient:"
                        " during updated_append_lus,"
                        " cant handle K2 response,"
                        " K2 reported successful"
                        " creation of >%(lenlus)d< "
                        " lus named: >%(lunames)s<, "
                        " attempts: >%(attempts)d< "
                        " but only >%(lustoadd)d< LUs were found.")
                x = exceptions.K2aCrudException
                raise x(msg
                        % {"lenlus": len(lus), "lunames": lunames,
                           "attempts": attempts,
                           "lustoadd": abs(lustoadd), },
                        updated_ssp.k2resp,
                        exclogger=self.api.exclogger)
            else:
                msg = _("k2aclient:"
                        " during updated_append_lus,"
                        " cant handle K2 response,"
                        " K2 reported successful"
                        " creation of >%(lenlus)d<"
                        " lus named: >%(lunames)s<,"
                        " attempts: >%(attempts)d<"
                        " but >%(lustoadd)d< extra LUs were returned.")
                x = exceptions.K2aCrudException
                raise x(msg %
                        {"lenlus": len(lus), "lunames": lunames,
                         "attempts": attempts, "lustoadd": abs(lustoadd), },
                        updated_ssp.k2resp,
                        exclogger=self.api.exclogger)
        msg = ("k2aclient:"
               " during updated_append_lus,"
               " for LUs named: >%s<"
               " after attempt # >%d<,"
               " success, udids: >%s<")

        _logger.debug(msg % (", ".join(x[0] for x in lus),
                             attempts,
                             ", ".join(lu.unique_device_id
                                       for lu in new_lus),))

        return (new_lus, updated_ssp)

    def update_append_lu(self, ssp, unitname, unitcapacity,
                         thin=True,
                         logicalunittype="VirtualIO_Disk",
                         clonedfrom=None,
                         xa=None):
        """For specified sharedstoragepool, add a logicalunit.

        :param ssp: The :class:`SharedStoragePool`.
        :param unitname: The UnitName of the new :class:`LogicalUnit`.
        :param unitcapacity: The UnitCapicty of the new :class:`LogicalUnit`.
        :param thin: Boolean indicating thin or thick.
        :param logicalunittype: See :method: update_append_lus for types
        :param clonedfrom: The udid of unit that the LU is cloned from
            None if not cloned
        :rtype: (new :class:`LogicalUnit, u :class:`SharedStoragePool)
        """
        (new_lus, updated_ssp) = self.update_append_lus(ssp,
                                                        [(unitname,
                                                         unitcapacity,
                                                         thin,
                                                         logicalunittype,
                                                         clonedfrom)],
                                                        xa=xa)
        return (new_lus[0], updated_ssp)

    @synchronized('update_lus')
    def update_del_lus(self, ssp, lu_udids, xa=None):
        """Delete logicalunits in a sharedstoragepool.

        :param ssp: The id of the :class:`SharedStoragePool`.
        :param lu_udids: The UDIDs of the :class:`LogicalUnit`.
        :rtype: updated :class:`SharedStoragePool
        raises :exc: ValueError if specified lu_udid
                     cannot be found in ssp
        """
        if not ssp.k2resp_isfor_k2entry:
            msg = ("cannot update an object"
                   " obtained from a list operation")
            raise ValueError(msg)
        if len(lu_udids) == 0:
            return ssp
        # if  necessary, authenticate
        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        # prime the update logic
        # we are serialized, so make sure we have the latest
        prev_ssp = self.refresh(ssp, xa=xa)
        # following line is work around for SW222953 SW239525
#nosynch        prev_ssp = self.get(ssp.id)

        updated_ssp = None
        attempts = 0
        tryagain = True
        while tryagain:
            tryagain = False
            # function-specific logic
            updated_ssp_lus = prev_ssp.logical_units.logical_unit
            for lu_udid in lu_udids:
                lu_for_delete = None
                for i, lu in enumerate(updated_ssp_lus):
                    if lu.unique_device_id == lu_udid:
                        lu_for_delete = lu
                        break

                if attempts == 0 and lu_for_delete is None:
                    msg = _("k2aclient:"
                            " during update_append_lu,"
                            " programming error,"
                            " could not find lu_udid: >%(lu_udid)s<,"
                            " in input ssp for:"
                            " >%(pool)s<")
                    raise ValueError(msg %
                                     {"lu_udid": lu_udid,
                                      "pool": prev_ssp.storage_pool_name, })

                # "attempts > 0 and lu_for_delete is None" means LU was
                # deleted by different thread
                elif lu_for_delete is None:
                    return updated_ssp
                del updated_ssp_lus[i]
            # function-specific logic end
            attempts += 1
            try:
                updated_ssp = self.update(prev_ssp, xa=xa)
            except exceptions.K2aK2ErrorPreConditionFailed:
                if attempts > self.api.retries:
                    msg = _("k2aclient:"
                            " during update_append_lu,"
                            " while deleting LUs w/ udids: >%(lu_udids)s<,"
                            " # attempts due to HTTP 412 exceeded:"
                            " >%(retries)d<")
                    _logger.warn(msg % {"lu_udids": ",".join(lu_udids),
                                        "retries": self.api.retries, })
                    raise
                # get a more recent ssp for retry
                prev_ssp = self.get(prev_ssp.id, xa=xa)
                msg = ("k2aclient:"
                       " during update_append_lu,"
                       " while deleting LUs named: >%s<, "
                       " for attempt #: >%d<, "
                       " received HTTP 412, will retry ...")
                _logger.debug(msg, ",".join(lu_udids), attempts)
#                 print "SW239525 TRYAGAIN: >%d<" %(attempts,)
                tryagain = True
            except Exception:
                raise

        return updated_ssp
