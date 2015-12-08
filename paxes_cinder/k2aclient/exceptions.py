#
#
# All Rights Reserved.
# Copyright 2010 Jacob Kaplan-Moss
# All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""
Exception definitions.
"""

from paxes_cinder.k2aclient import _
from paxes_k2.k2operator import K2Error
from paxes_k2.k2operator import K2ConnectionError
from paxes_k2.k2operator import K2SSLError
from paxes_k2.k2operator import K2TimeoutError


class K2aException(Exception):
    """Base class for exceptions for all k2aclient exceptions"""
    def __init__(self, msg):
        self.msg = msg
        super(K2aException, self).__init__(msg)

    def __unicode__(self):
        return unicode(self.msg)


class K2aCrudException(K2aException):
    """Exception due to issue with K2 response"""
    def __init__(self, msg, k2resp, exclogger=None):
        diagfspec = None
        if exclogger is not None:
            diagfspec = exclogger.emit("CRUD", msg, k2resp)
            msg = (_("%(msg)s, exception diagnostics have"
                     " been written to: >%(diagfspec)s<") %
                   {"msg": msg,
                    "diagfspec": diagfspec, })

        super(K2aCrudException, self).__init__(msg)
        self.k2resp = k2resp
        self.diagfspec = diagfspec


class K2aK2Other(K2aException):
    def __init__(self, e, addmsg=None):
        msg = _("Other Exception off of K2: >%s<") % e
        if addmsg is not None:
            msg = (_("%(msg)s, during: >%(addmsg)s<") %
                   {"msg": msg,
                    "addmsg": addmsg, })
        super(K2aK2Other, self).__init__(msg)
        self.e = e


class K2aK2SslError(K2aException):
    """Exceptions due to k2 SSL processing"""
    def __init__(self, k2error, addmsg=None):
        msg = _("SSL exception off of K2: >%s<") % k2error
        if addmsg is not None:
            msg = (_("%(msg)s, during: >%(addmsg)s<") %
                   {"msg": msg,
                    "addmsg": addmsg, })
        super(K2aK2SslError, self).__init__(msg)
        self.k2error = k2error


class K2aK2ConnectionError(K2aException):
    """Exceptions due to k2 connection processing"""
    def __init__(self, k2error, addmsg=None):
        msg = _("Connection exception off of K2: >%s<") % k2error
        if addmsg is not None:
            msg = (_("%(msg)s, during: >%(addmsg)s<") %
                   {"msg": msg,
                    "addmsg": addmsg, })
        super(K2aK2ConnectionError, self).__init__(msg)
        self.k2error = k2error


class K2aK2TimeoutError(K2aException):
    """Exceptions due to k2 timeout"""
    def __init__(self, k2error, addmsg=None):
        msg = _("Timeout exception off of K2: >%s<") % k2error
        if addmsg is not None:
            msg = (_("%(msg)s, during: >%(addmsg)s<") %
                   {"msg": msg,
                    "addmsg": addmsg, })
        super(K2aK2TimeoutError, self).__init__(msg)
        self.k2error = k2error


# TODO get list of status codes that can come off of K2
class K2aK2Error(K2aException):
    """
    Base class for K2Error w/ response codes exceptions coming off of K2
    """
    def __init__(self, status, k2error, addmsg=None, k2msg=None,
                 diagfspec=None):
        msg = (_("K2Error off of K2: >%(msg)s<,"
                 " Status: >%(status)d<, k2Error: >%(k2error)s<") %
               {"msg": self.__class__.msg,
                "status": status, "k2error": k2error, })
        if addmsg is not None:
            msg = (_("%(msg)s, during: >%(addmsg)s<") %
                   {"msg": msg,
                    "addmsg": addmsg, })
        super(K2aK2Error, self).__init__(msg)
        self.status = status
        self.k2error = k2error
        self.k2msg = k2msg
        self.diagfspec = diagfspec


class K2aK2ErrorBadRequest(K2aK2Error):
    """
    K2aK2Error HTTP 400 - The request was missing
    required input, had errors in the provided input,
    or included extraneous input. Additional information
    regarding the error is provided in an error response
    body that includes a reason code with additional information.
    """
    http_status = 400
    msg = _("Bad Request")


class K2aK2ErrorUnauthorized(K2aK2Error):
    """
    K2aK2Error HTTP 401 - Unauthorized: bad credentials.
    """
    http_status = 401
    msg = _("Unauthorized")


class K2aK2ErrorForbidden(K2aK2Error):
    """
    K2aK2Error HTTP 403 - Multiple error conditions
    result in this status code:
    - The request requires authentication but no X-API-Session
    header was provided, or one was provided but the session
    ID was invalid.
    - The user under which the API request was authenticated
    is not authorized to perform the requested operation.
    """
    http_status = 403
    msg = _("Forbidden")


class K2aK2ErrorNotFound(K2aK2Error):
    """
    K2aK2Error HTTP 404 - Multiple error conditions result
    in this status code:
    - The URI does not designate an extant resource, or
    designates a resource for which the API user does not
    have object-access permission.
    - The URI designates a resource or operation that is not
    supported by the MC because it is currently the alternate MC.
    """
    http_status = 404
    msg = _("Not Found")


class K2aK2ErrorMethodNotAllowed(K2aK2Error):
    """
    K2aK2Error HTTP 405 - The request specifies an HTTP
    method that is not valid for the designated URI.
    """
    http_status = 405
    msg = _("Method Not Allowed")


class K2aK2ErrorNotAcceptable(K2aK2Error):
    """
    K2aK2Error HTTP 406 - The Accept header for the request
    does not include at least one content representation
    supported by the Web Services API.
    """
    http_status = 406
    msg = _("Not Acceptable")


class K2aK2ErrorConflict(K2aK2Error):
    """
    K2aK2Error HTTP 409 - The managed resource is in an incorrect
    state (status) for performing the requested operation.
    Additional information regarding the error is provided in an error
    response body that includes a reason code with additional
    information.
    """
    http_status = 409
    msg = _("Conflict")


class K2aK2ErrorPreConditionFailed(K2aK2Error):
    """
    K2aK2Error HTTP 412 - PreCondition failed
    """
    http_status = 412
    msg = _("PreCondition failed")


class K2aK2ErrorRequestBodyTooLarge(K2aK2Error):
    """
    K2aK2Error HTTP 413 - The request includes a
    request body that is too large.
    """
    http_status = 413
    msg = _("Request Body Too Large")


class K2aK2ErrorUnsupportedMediaType(K2aK2Error):
    """
    K2aK2Error HTTP 415 - The Content-Type header for
    the request specifies a representation that is
    not supported by the Web Services API.
    """
    http_status = 415
    msg = _("Unsupported Media Type")


class K2aK2ErrorInternaServerError(K2aK2Error):
    """
    K2aK2Error HTTP 500 - A server error occurred
    during processing of the request.
    """
    http_status = 500
    msg = _("Internal Server Error")


class K2aK2ErrorNotImplemented(K2aK2Error):
    """
    K2aK2Error HTTP 501 - The request specifies
    an HTTP method that is not recognized by the
    server (for any resource).
    """
    http_status = 501
    msg = _("Not Implemented")


class K2aK2ServiceUnavailable(K2aK2Error):
    """
    K2aK2Error HTTP 503 - The request could not
    be carried out by the MC due to some
    temporary condition.
    """
    http_status = 503
    msg = _("Service Unavailable")


class K2aK2HttpVersionNotSupported(K2aK2Error):
    """
    K2aK2Error HTTP 505 - The request specifies an HTTP
    protocol version that is not supported by
    the Web Services API.
    """
    http_status = 505
    msg = _("HTTP Version Not Supported")


class K2aK2ErrorUnclassified(K2aK2Error):
    """
    HTTP ??? - Unclassified K2Error
    """
    http_status = -1
    msg = _("Not Classified")

_code_to_exception_map = dict((c.http_status, c)
                              for c in K2aK2Error.__subclasses__())


_EXCLUDED_EXCEPTIONS = [412]


def create_k2a_exception_from_k2o_exception(e, addmsg=None, exclogger=None):
    """
    Return an instance of an K2aK2Error or subclass
    based on an requests response. Optionally add additional message.
    Optionally log details of the exception.
    """

    if not isinstance(e, K2Error):
        return K2aK2Other(e, addmsg)

    if isinstance(e, K2SSLError):
        return K2aK2SslError(e, addmsg)

    if isinstance(e, K2ConnectionError):
        return K2aK2ConnectionError(e, addmsg)

    if isinstance(e, K2TimeoutError):
        return K2aK2TimeoutError(e, addmsg)

    k2response = e.k2response
    # If non status_code then use -1
    status = -1
    if k2response is not None and k2response.status is not None:
        status = k2response.status

    # if activated place k2response in exception log
    diagfspec = None
    if (k2response is not None
            and exclogger is not None
            and status not in _EXCLUDED_EXCEPTIONS):
        category = "UNC"
        if status > -1:
            category = str(status)

        diagfspec = exclogger.emit(category, addmsg, k2response, exc=e)
        addmsg += (_(", exception diagnostics have been written to: >%s<") %
                   diagfspec)

    cls = _code_to_exception_map.get(status, K2aK2ErrorUnclassified)

    k2msg = None
    if hasattr(k2response, 'k2err'):
        m = k2response.k2err.find('./Message')
        if m is not None:
            k2msg = m.text
    return cls(status, e, addmsg, k2msg=k2msg,
               diagfspec=diagfspec)


#################
class K2JobFailure(K2aException):
    """Raised when a K2 Job fails"""
    def __init__(self, msg, k2resp,
                 diagfspeci=None,
                 diagfspec=None):
        super(K2JobFailure, self).__init__(msg)
        self.k2resp = k2resp
        self.diagfspeci = diagfspeci
        self.diagfspec = diagfspec


#################
class UnsupportedVersion(K2aException):
    """Raised whan an unsupported version of the k2aclient
    is requested."""
    pass


class CommandError(K2aException):
    pass


class NotFound(K2aException):
    pass


class NoUniqueMatch(K2aException):
    pass
