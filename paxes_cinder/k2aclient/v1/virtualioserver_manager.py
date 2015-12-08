#
#
# =================================================================
# =================================================================

"""VirtualIOServer interface."""

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import Element
from eventlet import greenthread
import os
import errno

from paxes_cinder.k2aclient import _
from paxes_cinder.k2aclient import base
from paxes_cinder.k2aclient.v1 import k2uom
from paxes_cinder.k2aclient.v1 import k2web
from paxes_cinder.k2aclient.exceptions import K2JobFailure


def _create_luarecovery_doc(device_list,
                            ireliableITL=True,
                            iversion="1"):
    """Create an luarecovery_doc

        :param devlice_list: a list of (ivendor, ideviceID, itls)
        :param ivendor: This string must be upper case.
                        The following are expected vendor strings:
                        all other cases the attribute should be
                        set to "OTHER":
                        1. IBM
                        2. EMC
                        3. NETAPP
                        4. HDS
                        5. HP

        :param ideviceID: a valid page 83h descriptor of the
                          storage appliance

        :param device_list: a list of (iwwpn, twwpn, lua)
            :param iwwpn: world wide port name of a VIOS initiator
            :param twwpn: world wide port name of a target port on
                          storage appliance WWPN
            :param lua: Logical unit address of a particular piece of
                        storage (device) that can be accessed from the
                        target port.
        :param ireliableITL: False if the ITL nexus is based on a current
                             VIOS adapter inventory and True if its based
                             on an ITL nexus at the time the logical unit
                             was created.
        :param version: string containing requested version of the xml doc,
                        must be "1"
    """

    root = Element("XML_LIST")
    # general
    general = Element("general")
    root.append(general)
    version = Element("version")
    version.text = iversion
    general.append(version)

    # reliableITL
    reliableITL = Element("reliableITL")
    reliableITL.text = "false"
    if ireliableITL:
        reliableITL.text = "true"
    root.append(reliableITL)

    # deviceList
    deviceList = Element("deviceList")
    root.append(deviceList)

    for idevice in device_list:
        (ivendor, ideviceID, itls) = idevice

        device = Element("device")
        deviceList.append(device)

        # vendor
        vendor = Element("vendor")
        vendor.text = ivendor
        device.append(vendor)

        # deviceID
        deviceID = Element("deviceID")
        deviceID.text = ideviceID
        device.append(deviceID)

        itlList = Element("itlList")
        device.append(itlList)

        first = True
        for itl in itls:
            if first:
                number = Element("number")
                number.text = "%d" % (len(itls))
                itlList.append(number)
                first = False

            (iIwwpn, iTwwpn, ilua) = itl

            itl = Element("itl")
            itlList.append(itl)

            # Iwwpn
            Iwwpn = Element("Iwwpn")
            Iwwpn.text = iIwwpn
            itl.append(Iwwpn)

            # Twwpn
            Twwpn = Element("Twwpn")
            Twwpn.text = iTwwpn
            itl.append(Twwpn)

            # Lua
            lua = Element("lua")
            lua.text = ilua
            itl.append(lua)

    return root


def _prepdir(targetdir):
    try:
        os.makedirs(targetdir)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(targetdir):
            pass
        else:
            msg = _("during directory preparation,"
                    " cant create directory: "
                    " >%s<") % targetdir
            raise Exception(msg)

    if not os.access(targetdir, os.W_OK):
        msg = _("during directory preparation,"
                " cant write to directory: "
                " >%s<") % targetdir
        raise Exception(msg)


class VirtualIOServerManager(base.ManagerWithFind):
    """Manage :class:`VirtualIOServer` resources."""
    resource_class = k2uom.VirtualIOServer

    def list(self, managedsystem, xa=None):
        """Get a list of all VirtualIOServers for a
        particular ManagedSystem accessed through a
        particular hmc.

        :rtype: list of :class:`VirtualIOServer`.
        """
        return self._list("/rest/api/uom/ManagedSystem/%s/VirtualIOServer" %
                          managedsystem, xa=xa)

    def listasroot(self, xa=None):
        """Get a list of all LogicalPartitions
        accessed through a particular hmc.

        :rtype: list of :class:`LogicalPartition`.
        """
        return self._list("/rest/api/uom/VirtualIOServer", xa=xa)

    def get(self, managedsystem, virtualioserver, xag=[], xa=None):
        """Get a specific VirtualIOServer.

        :param virtualioserver: The ID of the :class:`VirtualIOServer` to get.
        :rtype: :class:`VirtualIOServer`
        """
        return self._get("/rest/api/uom/ManagedSystem/%s/VirtualIOServer/%s" %
                         (managedsystem, virtualioserver,), xag=xag, xa=xa)

    def getasroot(self, virtualioserver, xag=[], xa=None):
        """Get a specific VirtualIOServer.

        :param virtualioserver: The ID of the :class:`VirtualIOServer`.
        :rtype: :class:`VirtualIOServer`
        """
        return self._get("/rest/api/uom/VirtualIOServer/%s" %
                         virtualioserver, xag=xag, xa=xa)

########
# non CRUD
    def lua_recovery(self, vios, vendor, device_id, itls, xa=None):
        """For the specified device, prep VIOS for file upload.

        :param vios: the target VIOS
        :param vendor: This string must be upper case.
                       The following are expected vendor strings:
                       all other cases the attribute should be
                       set to "OTHER":
                        1. IBM
                        2. EMC
                        3. NETAPP
                        4. HDS
                        5. HP
        :param device_id: a valid page 83h descriptor of the
                          storage appliance
        :param itl_list: a list of (iwwpn, twwpn, lua)
          :param iwwpn: world wide port name of a VIOS initiator
          :param twwpn: world wide port name of a target port on
                        storage appliance WWPN
          :param lua: Logical unit address of a particular piece of
                      storage (device) that can be accessed from the
                      target port.

        :retval a triple - (jobstatus, version, [status, pvName, uniqueID])
          jobstatus: The K2 Job return status
          version: "1"
          status: "1" This means that a device was found from an ITL nexus
                      and it was determined to be in use by the VIOS. The most
                      likely cause is that a virtual device was not removed
                      from a previous deploy. The VIOS took no action in this
                      case.
                  "2" This means that the ITL nexus is not consider reliable
                      and some error occurred that prevents the VIOS from
                      determining making a decision on safely removing a
                      device. The VIOS took no action in this case.
                  "3" This means the information provided and action taken by
                      the VIOS was sufficient to find the storage.
                      pvName, and uniqueID elements will follow in the
                      data stream.
                  "4" This means some new storage element was found at the
                      ITL nexus but VIOS could not determine if it is the
                      storage of interest to the management tool.
                  "5" The VIOS could not determine if this is logical unit
                      of interest to the management tool however did
                      find a device from the ITL nexus list
                  "6" The VIOS could not find a device from the itl nexus list.
                      It could be some SCSI or transport error occurred
                      during configuration or the ITL nexus list was incorrect.
          pvName: If not None this element is the current physical volume name
          uniqueID: If not None, this uniquely identifies storage
                    throughout the SAN and is built based on vendor
                    prescribed method.
        """

        # if  necessary, authenticate
        if self.api.client.k2operator is None:
            self.api.client.authenticate()

        jrequest = self.api.web_job.getjob(vios, 'LUARecovery', xa=xa)

        device_list = [(vendor, device_id, itls)]
        idoc = _create_luarecovery_doc(device_list)
        cdata_template = "<![CDATA[%s]]>"
        inputXML = cdata_template % ElementTree.tostring(idoc)

        jp = k2web.JobParameter()
        jp.parameter_name = "inputXML"
        jp.parameter_value = inputXML
        jpc = k2web.JobParameter_Collection()
        jpc.job_parameter.append(jp)
        jrequest.job_parameters = jpc

    #     for jp in jrequest.job_parameters.job_parameter:
    #         print (jp.parameter_name, jp.parameter_value)

        jresponse = self.api.web_job.runjob(vios, jrequest, xa=xa)
        k2respi = jresponse._k2resp

        while jresponse.status == 'NOT_STARTED' or \
                jresponse.status == 'RUNNING':
            greenthread.sleep(1)
            jresponse = self.api.web_job.readjob(jresponse.job_id, xa=xa)

        if not jresponse.status.startswith("COMPLETED"):
            diagfspeci = self.api.exclogger.emit("JOB", "lua_recovery",
                                                 k2respi)
            diagfspec = self.api.exclogger.emit("JOB", "lua_recovery",
                                                jresponse._k2resp)
            msg = _("k2aclient:"
                    " during lua_recovery,"
                    " for device_id: >%(device_id)s<, experienced"
                    " job failure,"
                    " job_id: >%(jresponse.job_id)s<,"
                    " status: >%(jresponse.status)s<,"
                    " input K2 job diagnostics have been"
                    " written to: >%(diagfspeci)s<,"
                    " response k2 job diagnostics"
                    " have been written to: >%(diagfspec)s<")
            raise K2JobFailure(msg %
                               {"device_id": device_id,
                                "jresponse.job_id": jresponse.job_id,
                                "jresponse.status": jresponse.status,
                                "diagfspeci": diagfspeci,
                                "diagfspec": diagfspec, },
                               jresponse._k2resp,
                               diagfspeci=diagfspeci,
                               diagfspec=diagfspec)

        # find "OutputXML" element
        # note: apparently also "StdError" and "StdOut" entries
        result = None
        for jp in jresponse.results.job_parameter:
            if jp.parameter_name == "OutputXML":
                result = jp.parameter_value
#             print (jp.parameter_name, jp.parameter_value)

        version = None
        device_list = []
        if result is not None:
            root = ElementTree.fromstring(result)
            for child in root:
                if child.tag == "version":
                    version = child.text
                elif child.tag == "deviceList":
                    for gchild in child:
                        status = None
                        pv_name = None
                        unique_id = None
                        for ggchild in gchild:
                            if ggchild.tag == "status":
                                status = ggchild.text
                            elif ggchild.tag == "pvName":
                                pv_name = ggchild.text
                            elif ggchild.tag == "uniqueID":
                                unique_id = ggchild.text
                    device_list.append((status, pv_name, unique_id))

        return (jresponse.status, version, device_list, jresponse.job_id)
