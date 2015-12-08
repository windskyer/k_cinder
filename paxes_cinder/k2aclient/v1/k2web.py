#
#
# =================================================================
# =================================================================
#
#

import json

# from v1k2utils import K2Node


class K2WebResource(object):
    def __init__(self):
        # keep track of user-modified attributes
        self._modified_attrs = set()
        # keep track XAG (currently uom only)
        self.group = None

    @property
    def modified_attrs(self):
        return self._modified_attrs


class APIVersion(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_schema_namespace_of_templates = None
        self._pattr_schema_namespace_of_uom = None
        self._pattr_schema_namespace_of_web = None
        self._pattr_schema_version_of_templates = None
        self._pattr_schema_version_of_uom = None
        self._pattr_schema_version_of_web = None
        self._pattr_version_string_of_management_console = None
        self._pattr_vrm_of_mc = None
        super(APIVersion,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def schema_namespace_of_templates(self):
        return self._pattr_schema_namespace_of_templates

    @property
    def schema_namespace_of_uom(self):
        return self._pattr_schema_namespace_of_uom

    @property
    def schema_namespace_of_web(self):
        return self._pattr_schema_namespace_of_web

    @property
    def schema_version_of_templates(self):
        return self._pattr_schema_version_of_templates

    @property
    def schema_version_of_uom(self):
        return self._pattr_schema_version_of_uom

    @property
    def schema_version_of_web(self):
        return self._pattr_schema_version_of_web

    @property
    def version_string_of_management_console(self):
        return self._pattr_version_string_of_management_console

    @property
    def vrm_of_mc(self):
        return self._pattr_vrm_of_mc


class Atom(K2WebResource):
    def __init__(self):

        self._pattr_atom_created = None
        self._pattr_atom_id = None
        super(Atom,
              self).__init__()

    @property
    def atom_created(self):
        return self._pattr_atom_created

    @property
    def atom_id(self):
        return self._pattr_atom_id


class DiscreteProgressResponse(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_completed_states = None
        self._pattr_current_state = None
        super(DiscreteProgressResponse,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def completed_states(self):
        return self._pattr_completed_states

    @property
    def current_state(self):
        return self._pattr_current_state


class File(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_asset_link = None
        self._pattr_current_file_size_in_bytes = None
        self._pattr_date_modified = None
        self._pattr_expected_file_size_in_bytes = None
        self._pattr_file_enum_type = None
        self._pattr_file_uuid = None
        self._pattr_filename = None
        self._pattr_internet_media_type = None
        self._pattr_sha256 = None
        self._pattr_target_device_unique_device_id = None
        self._pattr_target_virtual_io_server_uuid = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(File,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("web", self, k2entry.element)
        self._id = self.metadata.atom.atom_id
        if hasattr(self, 'id') and len(self.id) == 36:
            manager.write_to_completion_cache('uuid', self.id)
        return self

    @property
    def id(self):
        return self._id

    @property
    def api(self):
        return self._api

    @property
    def k2entry(self):
        return self._k2entry

    @property
    def k2resp(self):
        return self._k2resp

    @property
    def k2resp_isfor_k2entry(self):
        return self._k2resp_isfor_k2entry

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def asset_link(self):
        return self._pattr_asset_link

    @property
    def current_file_size_in_bytes(self):
        return self._pattr_current_file_size_in_bytes

    @property
    def date_modified(self):
        return self._pattr_date_modified

    @property
    def expected_file_size_in_bytes(self):
        return self._pattr_expected_file_size_in_bytes
    @expected_file_size_in_bytes.setter
    def expected_file_size_in_bytes(self, value):
        self._modified_attrs.add("expected_file_size_in_bytes")
        self._pattr_expected_file_size_in_bytes = value

    @property
    def file_enum_type(self):
        return self._pattr_file_enum_type
    @file_enum_type.setter
    def file_enum_type(self, value):
        self._modified_attrs.add("file_enum_type")
        self._pattr_file_enum_type = value

    @property
    def file_uuid(self):
        return self._pattr_file_uuid

    @property
    def filename(self):
        return self._pattr_filename
    @filename.setter
    def filename(self, value):
        self._modified_attrs.add("filename")
        self._pattr_filename = value

    @property
    def internet_media_type(self):
        return self._pattr_internet_media_type
    @internet_media_type.setter
    def internet_media_type(self, value):
        self._modified_attrs.add("internet_media_type")
        self._pattr_internet_media_type = value

    @property
    def sha256(self):
        return self._pattr_sha256
    @sha256.setter
    def sha256(self, value):
        self._modified_attrs.add("sha256")
        self._pattr_sha256 = value

    @property
    def target_device_unique_device_id(self):
        return self._pattr_target_device_unique_device_id
    @target_device_unique_device_id.setter
    def target_device_unique_device_id(self, value):
        self._modified_attrs.add("target_device_unique_device_id")
        self._pattr_target_device_unique_device_id = value

    @property
    def target_virtual_io_server_uuid(self):
        return self._pattr_target_virtual_io_server_uuid
    @target_virtual_io_server_uuid.setter
    def target_virtual_io_server_uuid(self, value):
        self._modified_attrs.add("target_virtual_io_server_uuid")
        self._pattr_target_virtual_io_server_uuid = value

    def upload(self,
               filelike,
               xa=None):
        """Upload a file to the HMC.

        filelike  a file-like object."""

        return self.api.upload(self, filelike, xa=xa)


class HttpErrorResponse(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_http_status = None
        self._pattr_message = None
        self._pattr_reason_code = None
        self._pattr_request_body = None
        self._pattr_request_headers = None
        self._pattr_request_uri = None
        self._pattr_stack_trace = None
        super(HttpErrorResponse,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def http_status(self):
        return self._pattr_http_status

    @property
    def message(self):
        return self._pattr_message

    @property
    def reason_code(self):
        return self._pattr_reason_code

    @property
    def request_body(self):
        return self._pattr_request_body

    @property
    def request_headers(self):
        return self._pattr_request_headers

    @property
    def request_uri(self):
        return self._pattr_request_uri

    @property
    def stack_trace(self):
        return self._pattr_stack_trace


class JobException(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_message = None
        self._pattr_stack_trace = None
        super(JobException,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def message(self):
        return self._pattr_message

    @property
    def stack_trace(self):
        return self._pattr_stack_trace


class OperationParameter(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_parameter_name = None
        super(OperationParameter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def parameter_name(self):
        return self._pattr_parameter_name
    @parameter_name.setter
    def parameter_name(self, value):
        self._modified_attrs.add("parameter_name")
        self._pattr_parameter_name = value


class JobParameter(OperationParameter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_parameter_value = None
        super(JobParameter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def parameter_value(self):
        return self._pattr_parameter_value
    @parameter_value.setter
    def parameter_value(self, value):
        self._modified_attrs.add("parameter_value")
        self._pattr_parameter_value = value


class JobParameter_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_job_parameter = []
        super(JobParameter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def job_parameter(self):
        return self._pattr_job_parameter
    @job_parameter.setter
    def job_parameter(self, value):
        self._modified_attrs.add("job_parameter")
        self._pattr_job_parameter = value


class JobRequest(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_job_parameters = None
        self._pattr_requested_operation = None
        super(JobRequest,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def job_parameters(self):
        return self._pattr_job_parameters
    @job_parameters.setter
    def job_parameters(self, value):
        self._modified_attrs.add("job_parameters")
        self._pattr_job_parameters = value

    @property
    def requested_operation(self):
        return self._pattr_requested_operation
    @requested_operation.setter
    def requested_operation(self, value):
        self._modified_attrs.add("requested_operation")
        self._pattr_requested_operation = value


class JobResponse(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_job_id = None
        self._pattr_job_request_instance = None
        self._pattr_progress = None
        self._pattr_request_url = None
        self._pattr_response_exception = None
        self._pattr_results = None
        self._pattr_status = None
        self._pattr_target_uuid = None
        self._pattr_time_completed = None
        self._pattr_time_started = None
        super(JobResponse,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def job_id(self):
        return self._pattr_job_id

    @property
    def job_request_instance(self):
        return self._pattr_job_request_instance

    @property
    def progress(self):
        return self._pattr_progress

    @property
    def request_url(self):
        return self._pattr_request_url

    @property
    def response_exception(self):
        return self._pattr_response_exception

    @property
    def results(self):
        return self._pattr_results

    @property
    def status(self):
        return self._pattr_status

    @property
    def target_uuid(self):
        return self._pattr_target_uuid

    @property
    def time_completed(self):
        return self._pattr_time_completed

    @property
    def time_started(self):
        return self._pattr_time_started


class LogonRequest(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_change_password1 = None
        self._pattr_change_password2 = None
        self._pattr_password = None
        self._pattr_user_id = None
        super(LogonRequest,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def change_password1(self):
        return self._pattr_change_password1
    @change_password1.setter
    def change_password1(self, value):
        self._modified_attrs.add("change_password1")
        self._pattr_change_password1 = value

    @property
    def change_password2(self):
        return self._pattr_change_password2
    @change_password2.setter
    def change_password2(self, value):
        self._modified_attrs.add("change_password2")
        self._pattr_change_password2 = value

    @property
    def password(self):
        return self._pattr_password
    @password.setter
    def password(self, value):
        self._modified_attrs.add("password")
        self._pattr_password = value

    @property
    def user_id(self):
        return self._pattr_user_id
    @user_id.setter
    def user_id(self, value):
        self._modified_attrs.add("user_id")
        self._pattr_user_id = value


class LogonResponse(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_x_api__session = None
        super(LogonResponse,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def x_api__session(self):
        return self._pattr_x_api__session


class Metadata(K2WebResource):
    def __init__(self):

        self._pattr_atom = None
        super(Metadata,
              self).__init__()

    @property
    def atom(self):
        return self._pattr_atom


class NLSStaticMessage(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_message_key = None
        self._pattr_untranslated_message = None
        super(NLSStaticMessage,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def message_key(self):
        return self._pattr_message_key

    @property
    def untranslated_message(self):
        return self._pattr_untranslated_message


class NLSMessage(NLSStaticMessage):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_positional_parameter = []
        super(NLSMessage,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def positional_parameter(self):
        return self._pattr_positional_parameter


class NLSMessage_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_nls_message = []
        super(NLSMessage_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def nls_message(self):
        return self._pattr_nls_message
    @nls_message.setter
    def nls_message(self, value):
        self._modified_attrs.add("nls_message")
        self._pattr_nls_message = value


class NLSStaticMessage_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_nls_static_message = []
        super(NLSStaticMessage_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def nls_static_message(self):
        return self._pattr_nls_static_message
    @nls_static_message.setter
    def nls_static_message(self, value):
        self._modified_attrs.add("nls_static_message")
        self._pattr_nls_static_message = value


class Operation(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_all_discrete_states = None
        self._pattr_all_possible_parameters = None
        self._pattr_all_possible_results = None
        self._pattr_group_name = None
        self._pattr_operation_name = None
        self._pattr_progress_type = None
        super(Operation,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def all_discrete_states(self):
        return self._pattr_all_discrete_states

    @property
    def all_possible_parameters(self):
        return self._pattr_all_possible_parameters

    @property
    def all_possible_results(self):
        return self._pattr_all_possible_results

    @property
    def group_name(self):
        return self._pattr_group_name

    @property
    def operation_name(self):
        return self._pattr_operation_name

    @property
    def progress_type(self):
        return self._pattr_progress_type


class OperationParameter_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_operation_parameter = []
        super(OperationParameter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def operation_parameter(self):
        return self._pattr_operation_parameter
    @operation_parameter.setter
    def operation_parameter(self, value):
        self._modified_attrs.add("operation_parameter")
        self._pattr_operation_parameter = value


class OperationSet(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_defined_operations = None
        self._pattr_set_name = None
        super(OperationSet,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def defined_operations(self):
        return self._pattr_defined_operations

    @property
    def set_name(self):
        return self._pattr_set_name


class Operation_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_operation = []
        super(Operation_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def operation(self):
        return self._pattr_operation
    @operation.setter
    def operation(self, value):
        self._modified_attrs.add("operation")
        self._pattr_operation = value


class ProgressResponse(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_completed_tasks = None
        self._pattr_current_task = None
        self._pattr_discrete_progress = None
        self._pattr_linear_progress = None
        super(ProgressResponse,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def completed_tasks(self):
        return self._pattr_completed_tasks

    @property
    def current_task(self):
        return self._pattr_current_task

    @property
    def discrete_progress(self):
        return self._pattr_discrete_progress

    @property
    def linear_progress(self):
        return self._pattr_linear_progress


class QuickProperty(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_description = None
        self._pattr_nickname = None
        self._pattr_rest_element = None
        super(QuickProperty,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def description(self):
        return self._pattr_description

    @property
    def nickname(self):
        return self._pattr_nickname

    @property
    def rest_element(self):
        return self._pattr_rest_element


class SearchParameter(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_comparator = None
        self._pattr_parameter_name = None
        self._pattr_x_path = None
        super(SearchParameter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def comparator(self):
        return self._pattr_comparator

    @property
    def parameter_name(self):
        return self._pattr_parameter_name

    @property
    def x_path(self):
        return self._pattr_x_path


class SearchParameterSet(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_element_name = None
        self._pattr_search_parameters = None
        super(SearchParameterSet,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def element_name(self):
        return self._pattr_element_name

    @property
    def search_parameters(self):
        return self._pattr_search_parameters


class SearchParameter_Collection(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_search_parameter = []
        super(SearchParameter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def search_parameter(self):
        return self._pattr_search_parameter
    @search_parameter.setter
    def search_parameter(self, value):
        self._modified_attrs.add("search_parameter")
        self._pattr_search_parameter = value


class VersionReleaseMaintenance(K2WebResource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_maintenance = None
        self._pattr_release = None
        self._pattr_version = None
        super(VersionReleaseMaintenance,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def maintenance(self):
        return self._pattr_maintenance

    @property
    def release(self):
        return self._pattr_release

    @property
    def version(self):
        return self._pattr_version

_k2dict_json = """{
    "APIVersion": {
        "VRMOfMC": "VersionReleaseMaintenance"
    },
    "DiscreteProgressResponse": {
        "CompletedStates": "NLSStaticMessage_Collection",
        "CurrentState": "NLSStaticMessage"
    },
    "File": {},
    "HttpErrorResponse": {},
    "JobException": {},
    "JobParameter": {},
    "JobRequest": {
        "JobParameters": "JobParameter_Collection",
        "RequestedOperation": "Operation"
    },
    "JobResponse": {
        "JobRequestInstance": "JobRequest",
        "Progress": "ProgressResponse",
        "ResponseException": "JobException",
        "Results": "JobParameter_Collection"
    },
    "LogonRequest": {},
    "LogonResponse": {},
    "NLSMessage": {},
    "NLSStaticMessage": {},
    "Operation": {
        "AllDiscreteStates": "NLSStaticMessage_Collection",
        "AllPossibleParameters": "OperationParameter_Collection",
        "AllPossibleResults": "OperationParameter_Collection"
    },
    "OperationParameter": {},
    "OperationSet": {
        "DefinedOperations": "Operation_Collection"
    },
    "ProgressResponse": {
        "CompletedTasks": "NLSMessage_Collection",
        "CurrentTask": "NLSMessage",
        "DiscreteProgress": "DiscreteProgressResponse"
    },
    "QuickProperty": {},
    "SearchParameter": {},
    "SearchParameterSet": {
        "SearchParameters": "SearchParameter_Collection"
    },
    "VersionReleaseMaintenance": {}
}"""
k2dict = json.loads(_k2dict_json)
_k2attr_json = """{
    "APIVersion": [
        null,
        [
            [
                "version_string_of_management_console",
                "VersionStringOfManagementConsole",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_namespace_of_uom",
                "SchemaNamespaceOfUOM",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_version_of_uom",
                "SchemaVersionOfUOM",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_namespace_of_web",
                "SchemaNamespaceOfWeb",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_version_of_web",
                "SchemaVersionOfWeb",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_namespace_of_templates",
                "SchemaNamespaceOfTemplates",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "schema_version_of_templates",
                "SchemaVersionOfTemplates",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "vrm_of_mc",
                "VRMOfMC",
                "VersionReleaseMaintenance.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "Atom": [
        null,
        [
            [
                "atom_created",
                "AtomCreated",
                "_Undefined.Type",
                "ro",
                "r",
                "",
                ""
            ],
            [
                "atom_id",
                "AtomID",
                "_Undefined.Type",
                "ro",
                "r",
                "",
                ""
            ]
        ]
    ],
    "DiscreteProgressResponse": [
        null,
        [
            [
                "current_state",
                "CurrentState",
                "NLSStaticMessage.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "completed_states",
                "CompletedStates",
                "NLSStaticMessage_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "File": [
        null,
        [
            [
                "filename",
                "Filename",
                "FileName.Pattern",
                "co",
                "r",
                "R",
                ""
            ],
            [
                "date_modified",
                "DateModified",
                "long",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "internet_media_type",
                "InternetMediaType",
                "string",
                "co",
                "r",
                "R",
                ""
            ],
            [
                "file_uuid",
                "FileUUID",
                "UUID.Pattern",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "asset_link",
                "AssetLink",
                "link rel=asset",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "sha256",
                "SHA256",
                "string",
                "co",
                "d",
                "R",
                ""
            ],
            [
                "expected_file_size_in_bytes",
                "ExpectedFileSizeInBytes",
                "long",
                "co",
                "d",
                "R",
                ""
            ],
            [
                "current_file_size_in_bytes",
                "CurrentFileSizeInBytes",
                "long",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "file_enum_type",
                "FileEnumType",
                "FileType.Enum",
                "co",
                "r",
                "R",
                ""
            ],
            [
                "target_virtual_io_server_uuid",
                "TargetVirtualIOServerUUID",
                "UUID.Pattern",
                "co",
                "r",
                "R",
                ""
            ],
            [
                "target_device_unique_device_id",
                "TargetDeviceUniqueDeviceID",
                "UDID.Pattern",
                "co",
                "r",
                "R",
                ""
            ]
        ]
    ],
    "HttpErrorResponse": [
        null,
        [
            [
                "http_status",
                "HTTPStatus",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "request_uri",
                "RequestURI",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "reason_code",
                "ReasonCode",
                "HttpReasonCodes.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "message",
                "Message",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "stack_trace",
                "StackTrace",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "request_body",
                "RequestBody",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "request_headers",
                "RequestHeaders",
                "string",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "JobException": [
        null,
        [
            [
                "message",
                "Message",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "stack_trace",
                "StackTrace",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "JobParameter": [
        "OperationParameter",
        [
            [
                "parameter_value",
                "ParameterValue",
                "string",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "JobParameter_Collection": [
        null,
        [
            [
                "job_parameter",
                "JobParameter",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "JobRequest": [
        null,
        [
            [
                "requested_operation",
                "RequestedOperation",
                "Operation.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "job_parameters",
                "JobParameters",
                "JobParameter_Collection.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "JobResponse": [
        null,
        [
            [
                "request_url",
                "RequestURL",
                "link rel=parent",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "target_uuid",
                "TargetUuid",
                "UUID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "job_id",
                "JobID",
                "long",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "time_started",
                "TimeStarted",
                "long",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "time_completed",
                "TimeCompleted",
                "long",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "status",
                "Status",
                "JobStatus.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "response_exception",
                "ResponseException",
                "JobException.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "job_request_instance",
                "JobRequestInstance",
                "JobRequest.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "progress",
                "Progress",
                "ProgressResponse.Type",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "results",
                "Results",
                "JobParameter_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogonRequest": [
        null,
        [
            [
                "user_id",
                "UserID",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "password",
                "Password",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "change_password1",
                "ChangePassword1",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "change_password2",
                "ChangePassword2",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogonResponse": [
        null,
        [
            [
                "x_api__session",
                "X_API_Session",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "Metadata": [
        null,
        [
            [
                "atom",
                "Atom",
                "_Undefined.Type",
                "ro",
                "r",
                "",
                ""
            ]
        ]
    ],
    "NLSMessage": [
        "NLSStaticMessage",
        [
            [
                "positional_parameter",
                "PositionalParameter",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "NLSMessage_Collection": [
        null,
        [
            [
                "nls_message",
                "NLSMessage",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "NLSStaticMessage": [
        null,
        [
            [
                "untranslated_message",
                "UntranslatedMessage",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "message_key",
                "MessageKey",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "NLSStaticMessage_Collection": [
        null,
        [
            [
                "nls_static_message",
                "NLSStaticMessage",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "Operation": [
        null,
        [
            [
                "operation_name",
                "OperationName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "group_name",
                "GroupName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "progress_type",
                "ProgressType",
                "JobProgressType.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "all_possible_parameters",
                "AllPossibleParameters",
                "OperationParameter_Collection.Type",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "all_possible_results",
                "AllPossibleResults",
                "OperationParameter_Collection.Type",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "all_discrete_states",
                "AllDiscreteStates",
                "NLSStaticMessage_Collection.Type",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "OperationParameter": [
        null,
        [
            [
                "parameter_name",
                "ParameterName",
                "string",
                "co",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "OperationParameter_Collection": [
        null,
        [
            [
                "operation_parameter",
                "OperationParameter",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "OperationSet": [
        null,
        [
            [
                "set_name",
                "SetName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "defined_operations",
                "DefinedOperations",
                "Operation_Collection.Type",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "Operation_Collection": [
        null,
        [
            [
                "operation",
                "Operation",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ProgressResponse": [
        null,
        [
            [
                "current_task",
                "CurrentTask",
                "NLSMessage.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "completed_tasks",
                "CompletedTasks",
                "NLSMessage_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "linear_progress",
                "LinearProgress",
                "float",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "discrete_progress",
                "DiscreteProgress",
                "DiscreteProgressResponse.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "QuickProperty": [
        null,
        [
            [
                "rest_element",
                "RESTElement",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "nickname",
                "Nickname",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "description",
                "Description",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SearchParameter": [
        null,
        [
            [
                "parameter_name",
                "ParameterName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "x_path",
                "XPath",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "comparator",
                "Comparator",
                "SearchComparator.Enum",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SearchParameterSet": [
        null,
        [
            [
                "element_name",
                "ElementName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "search_parameters",
                "SearchParameters",
                "SearchParameter_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SearchParameter_Collection": [
        null,
        [
            [
                "search_parameter",
                "SearchParameter",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VersionReleaseMaintenance": [
        null,
        [
            [
                "version",
                "Version",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "release",
                "Release",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maintenance",
                "Maintenance",
                "int",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ]
}"""
k2attr = json.loads(_k2attr_json)
_k2choice_json = """{}"""
k2choice = json.loads(_k2choice_json)



def _class_for_name(module_name, class_name):

#     import importlib
#     # load the module, will raise ImportError if module cannot be loaded
#     m = importlib.import_module(module_name)
#     # get the class, will raise AttributeError if class cannot be found
#     c = getattr(m, class_name)
#     return c

    # load the module, will raise ImportError if module cannot be loaded
    m = __import__(module_name, globals(), locals(), class_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

typeset = set([_class_for_name("paxes_cinder.k2aclient.v1.k2web",k)
    for k in k2attr.keys()])
_attr_cc_to_us_json = """{
    "AllDiscreteStates": "all_discrete_states",
    "AllPossibleParameters": "all_possible_parameters",
    "AllPossibleResults": "all_possible_results",
    "AssetLink": "asset_link",
    "Atom": "atom",
    "AtomCreated": "atom_created",
    "AtomID": "atom_id",
    "ChangePassword1": "change_password1",
    "ChangePassword2": "change_password2",
    "Comparator": "comparator",
    "CompletedStates": "completed_states",
    "CompletedTasks": "completed_tasks",
    "CurrentFileSizeInBytes": "current_file_size_in_bytes",
    "CurrentState": "current_state",
    "CurrentTask": "current_task",
    "DateModified": "date_modified",
    "DefinedOperations": "defined_operations",
    "Description": "description",
    "DiscreteProgress": "discrete_progress",
    "ElementName": "element_name",
    "ExpectedFileSizeInBytes": "expected_file_size_in_bytes",
    "FileEnumType": "file_enum_type",
    "FileUUID": "file_uuid",
    "Filename": "filename",
    "GroupName": "group_name",
    "HTTPStatus": "http_status",
    "InternetMediaType": "internet_media_type",
    "JobID": "job_id",
    "JobParameter": "job_parameter",
    "JobParameters": "job_parameters",
    "JobRequestInstance": "job_request_instance",
    "LinearProgress": "linear_progress",
    "Maintenance": "maintenance",
    "Message": "message",
    "MessageKey": "message_key",
    "Metadata": "metadata",
    "NLSMessage": "nls_message",
    "NLSStaticMessage": "nls_static_message",
    "Nickname": "nickname",
    "Operation": "operation",
    "OperationName": "operation_name",
    "OperationParameter": "operation_parameter",
    "ParameterName": "parameter_name",
    "ParameterValue": "parameter_value",
    "Password": "password",
    "PositionalParameter": "positional_parameter",
    "Progress": "progress",
    "ProgressType": "progress_type",
    "RESTElement": "rest_element",
    "ReasonCode": "reason_code",
    "Release": "release",
    "RequestBody": "request_body",
    "RequestHeaders": "request_headers",
    "RequestURI": "request_uri",
    "RequestURL": "request_url",
    "RequestedOperation": "requested_operation",
    "ResponseException": "response_exception",
    "Results": "results",
    "SHA256": "sha256",
    "SchemaNamespaceOfTemplates": "schema_namespace_of_templates",
    "SchemaNamespaceOfUOM": "schema_namespace_of_uom",
    "SchemaNamespaceOfWeb": "schema_namespace_of_web",
    "SchemaVersionOfTemplates": "schema_version_of_templates",
    "SchemaVersionOfUOM": "schema_version_of_uom",
    "SchemaVersionOfWeb": "schema_version_of_web",
    "SearchParameter": "search_parameter",
    "SearchParameters": "search_parameters",
    "SetName": "set_name",
    "StackTrace": "stack_trace",
    "Status": "status",
    "TargetDeviceUniqueDeviceID": "target_device_unique_device_id",
    "TargetUuid": "target_uuid",
    "TargetVirtualIOServerUUID": "target_virtual_io_server_uuid",
    "TimeCompleted": "time_completed",
    "TimeStarted": "time_started",
    "UntranslatedMessage": "untranslated_message",
    "UserID": "user_id",
    "VRMOfMC": "vrm_of_mc",
    "Version": "version",
    "VersionStringOfManagementConsole": "version_string_of_management_console",
    "X-API-Session": "x-api-_session",
    "XPath": "x_path",
    "X_API_Session": "x_api__session"
}"""
attr_cc_to_us = json.loads(_attr_cc_to_us_json)
