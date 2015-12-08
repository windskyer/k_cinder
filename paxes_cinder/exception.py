#
#
# =================================================================
# =================================================================

from cinder.exception import *


class ZoneManagerException(CinderException):
    message = _("Connection control failure: %(reason)s")


class FCZoneDriverException(CinderException):
    message = _("Zone operation failed: %(reason)s")


class FCSanLookupServiceException(CinderException):
    message = _("FC SAN Lookup failure: %(reason)s")


class ZoneManagerMisconfig(CinderException):
    """
    Exception representing misconfigurations in the fabric zoning configuration
    that are not specific to any one switch.
    """
    message = _("Internal Misconfiguration detected: %(reason)s")


class FabricDescriptor():
    """
    This class captures enough information to describe a fabric.  It is passed
    to fabric-related exceptions (FabricException subclasses), so that the
    consumers of the exception can easily tell which fabric the exception
    originated from.

    It is particularly important because we issue commands to all fabrics in
    parallel, so any exceptions that are raised must be wrapped or translated
    into a FabricException that includes a FabricDescriptor for the failing
    switch to be effectively indicated in error reports.
    """
    def __init__(self, name, display_name, username, ip, port):
        self.name = name
        self.display_name = display_name
        self.username = username
        self.ip = ip
        self.port = port

    def __str__(self):
        """
        Returns a one-line string representation of the passed-in properties
        """
        return _("Fabric '%(display_name)s' (%(username)s@%(ip)s:%(port)s)") \
            % {'display_name': self.display_name,
               'username': self.username,
               'ip': self.ip,
               'port': self.port
               }


class ZoneManagerParallel(Exception):
    """
    This Exception is used to wrap all of the exceptions that may have occurred
    across a range of fabrics.  We need this because we execute operations in
    parallel across all fabrics, and want to raise a single exception that
    shows how all fabrics failed, rather than just picking the first failing
    fabric and throwing away the rest of the exceptions.

    The passed-in list of exceptions should ideally all be subclasses of
    FabricException, which means that they contain identifying information
    about the fabric, but we tolerate cases where they are not.
    """
    def __init__(self, exceptions):
        """
        Pass in a list of exceptions, ideally FabricException subclasses.
        """
        self.exceptions = exceptions

    def to_string_list(self):
        """
        Returns a list containing one string per Exception.
        If the exception is a FabricException, we include the FabricDescriptor
        in our output.
        If not, then we just return a string representation of the exception.
        """
        def to_string(exception):
            if isinstance(exception, FabricException):
                return _("%(descriptor)s: %(message)s") % \
                    {'descriptor': exception.descriptor,
                     'message': exception.msg}
            else:
                return (_("%s") % exception)

        return map(to_string, self.exceptions)

    def __str__(self):
        """
        Returns a string containing a semicolon-separated list of exceptions.
        """
        return '; '.join(self.to_string_list())


class FabricException(CinderException):
    """
    This is the base exception class for exceptions originating from fabrics.
    They must include a FabricDescriptor, which identifies the fabric on which
    the exception occurred.
    """

    # Subclasses should set to False if there is no point in retrying the
    # operation.
    attempt_retry = True

    # Subclasses should set to False if backtrace is not useful.
    # e.g. If we had an authentication failure, it is pretty obvious what went
    # wrong without cluttering up the logs with a backtrace.
    backtrace_needed = True

    def __init__(self, descriptor, **kwargs):
        """
        Descriptor is a FabricDescriptor
        """
        self.descriptor = descriptor
        super(FabricException, self).__init__(**kwargs)


class FabricUnknownException(FabricException):
    """
    This is a generic exception for cases where a specific exception was not
    identified.  As well as the FabricDescriptor required by the superclass,
    this also takes a 'problem' string, and the original exception.

    The 'problem' string should be an indication of what the code was trying to
    achieve when the exception was raised, in terms that a PowerVC user would
    understand, e.g. "Could not create zones".
    """
    message = _("%(problem)s: %(err)s")

    def __init__(self, descriptor, problem, e):
        self.exception = e

        # Emit the original exception to the log files
        LOG.exception(e)

        super(FabricUnknownException, self).__init__(descriptor,
                                                     problem=problem,
                                                     err=(_("%s") % e))


class FabricAuthException(FabricException):
    """
    This exception is raised when we can't log onto a fabric because of
    invalid username/password.
    """

    backtrace_needed = False
    attempt_retry = False

    message = _("Could not authenticate with the specified credentials")


# Timeout exceptions occur when we can't connect to the switch in a specified
# timeframe
class FabricTimeoutException(FabricException):
    """
    This exception is raised when we get a timeout when trying to connect to
    the fabric.  It displays the timeout that was in place on the fabric.
    """
    message = _("Timeout (%(timeout)s seconds) when attempting to connect")


# Command timeout exceptions occur when an individual command takes too long
# to execute.
class FabricCommandTimeoutException(FabricException):
    """
    This exception is raised when we get a timeout when trying to connect to
    the fabric.  It displays the timeout that was in place on the fabric.
    """
    message = _("Timeout (%(timeout)s seconds) when executing command %(cmd)s")


class FabricConnectionException(FabricException):
    """
    This exception is raised when something happens during socket connection.
    The (error) is an error code, and (details) is a human-readable
    description.
    """
    message = _("Could not connect: %(error)s %(detail)s")


class FabricTransactionException(FabricException):
    """
    Transaction exceptions occur if we see switch commands fail due to an
    existing transaction already in progress on the switch.
    """
    message = _("Another transaction was already in progress when attempting "
                "to execute command '%(cmd)s'")


class FabricSizeExceededException(FabricException):
    """
    Raise this exception if we see a "Zone DB too large" response to any CLI
    """
    message = _("Zone DB exceeded size limits when executing command "
                "'%(cmd)s', which returned '%(res)s'")


class FabricUnexpectedResponseException(FabricException):
    """
    Raise this exception if we retrieve a nonempty response from any command
    that we don't understand.
    """
    message = _("The CLI command '%(cmd)s' returned an unexpected response "
                "'%(res)s'")


class SVCDescriptor():
    """
    This class captures enough information to describe a SVC/Storwize
    controller.  It is passed to SVC-related exceptions (SVCException
    subclasses), so that the consumers of the exception can easily tell which
    storage provider the exception originated from.
    """
    def __init__(self, name, display_name, username, ip, port):
        self.name = name
        self.display_name = display_name
        self.username = username
        self.ip = ip
        self.port = port

    def __str__(self):
        """
        Returns a one-line string representation of the passed-in properties
        """
        return _("Storage %(display_name)s (%(username)s@%(ip)s:%(port)s)") % \
            {'display_name': self.display_name,
             'username': self.username,
             'ip': self.ip,
             'port': self.port
             }


class SVCException(CinderException):
    """
    This is the base exception class for exceptions originating from
    SVC/Storwize controllers.  They must include a SVCDescriptor, which
    identifies the storage controller on which the exception occurred.
    """

    # Indicates whether or not this exception should cause the associated
    # volume to go into a permanent error state.
    error_volume = False

    def __init__(self, descriptor, **kwargs):
        """
        Descriptor is a SVCDescriptor
        """
        self.descriptor = descriptor
        super(SVCException, self).__init__(**kwargs)


class SVCHostDefsException(SVCException):
    """
    This Exception indicates that we issued a mkhost command and got an error
    back because there were already the maximum number of hosts in existence.
    """
    message = _("No more host definitions can be created")


class SVCFCMapsException(SVCException):
    """
    This Exception indicates that we issued a mkfcmap command and got an error
    back because there were already the maximum number of flashcopy mappings in
    existence.
    """
    message = _("No more flashcopy mappings can be created")


class SVCConnectionException(SVCException):
    """
    This exception indicates that we couldn't connect to the storage provider,
    possibly to due there being two many open SSH connections from elsewhare.
    """
    message = _("Could not connect, possibly due to too many connections.")


class SVCMultiMapException(SVCException):
    """
    This exception indicates that we couldn't map a volume to a host because it
    was already mapped elsewhere.
    """
    message = _("Could not map vdisk %(vdisk_id)s to host %(host)s because it "
                "is already mapped to another host")


class SVCVdiskNotFoundException(SVCException):
    """
    This exception indicates that a particular vdisk could not be found on the
    storage controller.
    """
    error_volume = True

    def __init__(self, descriptor, volume_id, **kwargs):
        self.volume_id = volume_id
        super(SVCVdiskNotFoundException, self).__init__(descriptor, **kwargs)

    message = _("vdisk %(vdisk_id)s does not exist")


class SVCNoZonesException(SVCException):
    """
    This exception is raised when there are no fabrics with at least one
    initiator and at least one target port present - this means that no
    zones will be created and thus there will be no connectivity.
    """

    message = _("No common fabrics between virtual machine and storage")


class SVCVdiskMismatchException(SVCException):
    """
    This exception is raised if the vdisk's UID is not as we expect.  This
    occurs if the vdisk is deleted out-of-band and then recreated, because the
    vdisk ID can be reused, but the UID cannot.

    We mark the disk as being in error if we notice this.
    """
    error_volume = True

    def __init__(self, descriptor, volume_id, **kwargs):
        self.volume_id = volume_id
        super(SVCVdiskMismatchException, self).__init__(descriptor, **kwargs)

    message = _("vdisk %(vdisk_id)s has been deleted and recreated. "
                "Expected UID is %(expected_uid)s, current UID is "
                "%(current_uid)s")


class PVCExpendvdiskCapacityException(CinderException):
    """
    This exception indicates that either the resize request exceeds the
    remaining capacity that storage has or the changed size could exceed
    the support vdisk size.
    """
    message = _("Not enough space left on storage host %(host)s to "
                "extend the volume %(volume_id)s")


class PVCExpendvdiskFCMapException(CinderException):
    """
    When the disk still has the flashcopy map, expend operation will
    fail. Detect such condition and tell the caller the expand
    cannot be done due to flashcopy at this moment.
    """
    message = _("Flashcopy is in progress for boot volume, "
                "volume size didn't change. Please try again later.")


class SVCExtendSnapshotSrcNotAllowed(CinderException):
    """This exception indicates that extension of the vdisk that is the
    source of snapshot flashcopy is not allowed"""
    message = _("vdisk %(vdisk_id)s is source of snapshot flashcopy "
                "and fcmap %(fcmapid)s cannot be removed.")

class SnapshotCreateError(CinderException):
    message = _("Creatting snapshot %(snapshot_name)s is Error ")