#
#
# =================================================================
# =================================================================
#
#

import json

# from v1k2utils import K2Node


class K2Resource(object):
    def __init__(self):
        # keep track of user-modified attributes
        self._modified_attrs = set()
        # keep track XAG (currently uom only)
        self.group = None

    @property
    def modified_attrs(self):
        return self._modified_attrs


class Atom(K2Resource):
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


class BasePartition(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allow_performance_data_collection = None
        self._pattr_associated_managed_system = None
        self._pattr_associated_partition_profile = None
        self._pattr_availability_priority = None
        self._pattr_client_network_adapters = None
        self._pattr_current_allocated_barrier_synchronization_register_arrays = None
        self._pattr_current_processor_compatibility_mode = None
        self._pattr_current_profile_sync = None
        self._pattr_host_ethernet_adapter_logical_ports = None
        self._pattr_hostname = None
        self._pattr_is_call_home_enabled = None
        self._pattr_is_connection_monitoring_enabled = None
        self._pattr_is_operation_in_progress = None
        self._pattr_is_redundant_error_path_reporting_enabled = None
        self._pattr_is_service_partition = None
        self._pattr_is_time_reference_partition = None
        self._pattr_is_virtual_service_attention_led_on = None
        self._pattr_is_virtual_trusted_platform_module_enabled = None
        self._pattr_keylock_position = None
        self._pattr_logical_serial_number = None
        self._pattr_mac_address_prefix = None
        self._pattr_operating_system_version = None
        self._pattr_partition_capabilities = None
        self._pattr_partition_id = None
        self._pattr_partition_io_configuration = None
        self._pattr_partition_memory_configuration = None
        self._pattr_partition_name = None
        self._pattr_partition_processor_configuration = None
        self._pattr_partition_profiles = None
        self._pattr_partition_state = None
        self._pattr_partition_type = None
        self._pattr_partition_uuid = None
        self._pattr_pending_processor_compatibility_mode = None
        self._pattr_processor_pool = None
        self._pattr_progress_partition_data_remaining = None
        self._pattr_progress_partition_data_total = None
        self._pattr_progress_state = None
        self._pattr_reference_code = None
        self._pattr_resource_monitoring_control_state = None
        self._pattr_resource_monitoring_ip_address = None
        self._pattr_sriov_ethernet_logical_ports = None
        self._pattr_sriov_fibre_channel_over_ethernet_logical_ports = None
        self._pattr_valid_interactive_performance = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(BasePartition,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def allow_performance_data_collection(self):
        return self._pattr_allow_performance_data_collection
    @allow_performance_data_collection.setter
    def allow_performance_data_collection(self, value):
        self._modified_attrs.add("allow_performance_data_collection")
        self._pattr_allow_performance_data_collection = value

    @property
    def associated_managed_system(self):
        return self._pattr_associated_managed_system
    @associated_managed_system.setter
    def associated_managed_system(self, value):
        self._modified_attrs.add("associated_managed_system")
        self._pattr_associated_managed_system = value

    @property
    def associated_partition_profile(self):
        return self._pattr_associated_partition_profile
    @associated_partition_profile.setter
    def associated_partition_profile(self, value):
        self._modified_attrs.add("associated_partition_profile")
        self._pattr_associated_partition_profile = value

    @property
    def availability_priority(self):
        return self._pattr_availability_priority
    @availability_priority.setter
    def availability_priority(self, value):
        self._modified_attrs.add("availability_priority")
        self._pattr_availability_priority = value

    @property
    def client_network_adapters(self):
        return self._pattr_client_network_adapters
    @client_network_adapters.setter
    def client_network_adapters(self, value):
        self._modified_attrs.add("client_network_adapters")
        self._pattr_client_network_adapters = value

    @property
    def current_allocated_barrier_synchronization_register_arrays(self):
        return self._pattr_current_allocated_barrier_synchronization_register_arrays

    @property
    def current_processor_compatibility_mode(self):
        return self._pattr_current_processor_compatibility_mode

    @property
    def current_profile_sync(self):
        return self._pattr_current_profile_sync
    @current_profile_sync.setter
    def current_profile_sync(self, value):
        self._modified_attrs.add("current_profile_sync")
        self._pattr_current_profile_sync = value

    @property
    def host_ethernet_adapter_logical_ports(self):
        return self._pattr_host_ethernet_adapter_logical_ports
    @host_ethernet_adapter_logical_ports.setter
    def host_ethernet_adapter_logical_ports(self, value):
        self._modified_attrs.add("host_ethernet_adapter_logical_ports")
        self._pattr_host_ethernet_adapter_logical_ports = value

    @property
    def hostname(self):
        return self._pattr_hostname
    @hostname.setter
    def hostname(self, value):
        self._modified_attrs.add("hostname")
        self._pattr_hostname = value

    @property
    def is_call_home_enabled(self):
        return self._pattr_is_call_home_enabled
    @is_call_home_enabled.setter
    def is_call_home_enabled(self, value):
        self._modified_attrs.add("is_call_home_enabled")
        self._pattr_is_call_home_enabled = value

    @property
    def is_connection_monitoring_enabled(self):
        return self._pattr_is_connection_monitoring_enabled
    @is_connection_monitoring_enabled.setter
    def is_connection_monitoring_enabled(self, value):
        self._modified_attrs.add("is_connection_monitoring_enabled")
        self._pattr_is_connection_monitoring_enabled = value

    @property
    def is_operation_in_progress(self):
        return self._pattr_is_operation_in_progress

    @property
    def is_redundant_error_path_reporting_enabled(self):
        return self._pattr_is_redundant_error_path_reporting_enabled
    @is_redundant_error_path_reporting_enabled.setter
    def is_redundant_error_path_reporting_enabled(self, value):
        self._modified_attrs.add("is_redundant_error_path_reporting_enabled")
        self._pattr_is_redundant_error_path_reporting_enabled = value

    @property
    def is_service_partition(self):
        return self._pattr_is_service_partition
    @is_service_partition.setter
    def is_service_partition(self, value):
        self._modified_attrs.add("is_service_partition")
        self._pattr_is_service_partition = value

    @property
    def is_time_reference_partition(self):
        return self._pattr_is_time_reference_partition
    @is_time_reference_partition.setter
    def is_time_reference_partition(self, value):
        self._modified_attrs.add("is_time_reference_partition")
        self._pattr_is_time_reference_partition = value

    @property
    def is_virtual_service_attention_led_on(self):
        return self._pattr_is_virtual_service_attention_led_on

    @property
    def is_virtual_trusted_platform_module_enabled(self):
        return self._pattr_is_virtual_trusted_platform_module_enabled
    @is_virtual_trusted_platform_module_enabled.setter
    def is_virtual_trusted_platform_module_enabled(self, value):
        self._modified_attrs.add("is_virtual_trusted_platform_module_enabled")
        self._pattr_is_virtual_trusted_platform_module_enabled = value

    @property
    def keylock_position(self):
        return self._pattr_keylock_position
    @keylock_position.setter
    def keylock_position(self, value):
        self._modified_attrs.add("keylock_position")
        self._pattr_keylock_position = value

    @property
    def logical_serial_number(self):
        return self._pattr_logical_serial_number

    @property
    def mac_address_prefix(self):
        return self._pattr_mac_address_prefix

    @property
    def operating_system_version(self):
        return self._pattr_operating_system_version

    @property
    def partition_capabilities(self):
        return self._pattr_partition_capabilities

    @property
    def partition_id(self):
        return self._pattr_partition_id
    @partition_id.setter
    def partition_id(self, value):
        self._modified_attrs.add("partition_id")
        self._pattr_partition_id = value

    @property
    def partition_io_configuration(self):
        return self._pattr_partition_io_configuration
    @partition_io_configuration.setter
    def partition_io_configuration(self, value):
        self._modified_attrs.add("partition_io_configuration")
        self._pattr_partition_io_configuration = value

    @property
    def partition_memory_configuration(self):
        return self._pattr_partition_memory_configuration
    @partition_memory_configuration.setter
    def partition_memory_configuration(self, value):
        self._modified_attrs.add("partition_memory_configuration")
        self._pattr_partition_memory_configuration = value

    @property
    def partition_name(self):
        return self._pattr_partition_name
    @partition_name.setter
    def partition_name(self, value):
        self._modified_attrs.add("partition_name")
        self._pattr_partition_name = value

    @property
    def partition_processor_configuration(self):
        return self._pattr_partition_processor_configuration
    @partition_processor_configuration.setter
    def partition_processor_configuration(self, value):
        self._modified_attrs.add("partition_processor_configuration")
        self._pattr_partition_processor_configuration = value

    @property
    def partition_profiles(self):
        return self._pattr_partition_profiles
    @partition_profiles.setter
    def partition_profiles(self, value):
        self._modified_attrs.add("partition_profiles")
        self._pattr_partition_profiles = value

    @property
    def partition_state(self):
        return self._pattr_partition_state

    @property
    def partition_type(self):
        return self._pattr_partition_type
    @partition_type.setter
    def partition_type(self, value):
        self._modified_attrs.add("partition_type")
        self._pattr_partition_type = value

    @property
    def partition_uuid(self):
        return self._pattr_partition_uuid

    @property
    def pending_processor_compatibility_mode(self):
        return self._pattr_pending_processor_compatibility_mode
    @pending_processor_compatibility_mode.setter
    def pending_processor_compatibility_mode(self, value):
        self._modified_attrs.add("pending_processor_compatibility_mode")
        self._pattr_pending_processor_compatibility_mode = value

    @property
    def processor_pool(self):
        return self._pattr_processor_pool
    @processor_pool.setter
    def processor_pool(self, value):
        self._modified_attrs.add("processor_pool")
        self._pattr_processor_pool = value

    @property
    def progress_partition_data_remaining(self):
        return self._pattr_progress_partition_data_remaining

    @property
    def progress_partition_data_total(self):
        return self._pattr_progress_partition_data_total

    @property
    def progress_state(self):
        return self._pattr_progress_state

    @property
    def reference_code(self):
        return self._pattr_reference_code

    @property
    def resource_monitoring_control_state(self):
        return self._pattr_resource_monitoring_control_state

    @property
    def resource_monitoring_ip_address(self):
        return self._pattr_resource_monitoring_ip_address
    @resource_monitoring_ip_address.setter
    def resource_monitoring_ip_address(self, value):
        self._modified_attrs.add("resource_monitoring_ip_address")
        self._pattr_resource_monitoring_ip_address = value

    @property
    def sriov_ethernet_logical_ports(self):
        return self._pattr_sriov_ethernet_logical_ports
    @sriov_ethernet_logical_ports.setter
    def sriov_ethernet_logical_ports(self, value):
        self._modified_attrs.add("sriov_ethernet_logical_ports")
        self._pattr_sriov_ethernet_logical_ports = value

    @property
    def sriov_fibre_channel_over_ethernet_logical_ports(self):
        return self._pattr_sriov_fibre_channel_over_ethernet_logical_ports
    @sriov_fibre_channel_over_ethernet_logical_ports.setter
    def sriov_fibre_channel_over_ethernet_logical_ports(self, value):
        self._modified_attrs.add("sriov_fibre_channel_over_ethernet_logical_ports")
        self._pattr_sriov_fibre_channel_over_ethernet_logical_ports = value

    @property
    def valid_interactive_performance(self):
        return self._pattr_valid_interactive_performance
    @valid_interactive_performance.setter
    def valid_interactive_performance(self, value):
        self._modified_attrs.add("valid_interactive_performance")
        self._pattr_valid_interactive_performance = value


class BasePartition_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(BasePartition_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class Cage(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_cage_id = None
        self._pattr_cage_location = None
        self._pattr_frame_location = None
        self._pattr_io_units = None
        self._pattr_machine_type_model_and_serial_number = None
        self._pattr_managed_systems = None
        self._pattr_owner_location = None
        self._pattr_owner_machine_type_model_and_serial_number = None
        super(Cage,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def cage_id(self):
        return self._pattr_cage_id

    @property
    def cage_location(self):
        return self._pattr_cage_location

    @property
    def frame_location(self):
        return self._pattr_frame_location

    @property
    def io_units(self):
        return self._pattr_io_units

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number

    @property
    def managed_systems(self):
        return self._pattr_managed_systems

    @property
    def owner_location(self):
        return self._pattr_owner_location

    @property
    def owner_machine_type_model_and_serial_number(self):
        return self._pattr_owner_machine_type_model_and_serial_number


class Cage_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_cage = []
        super(Cage_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def cage(self):
        return self._pattr_cage
    @cage.setter
    def cage(self, value):
        self._modified_attrs.add("cage")
        self._pattr_cage = value


class VirtualIOAdapter(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_type = None
        self._pattr_dynamic_reconfiguration_connector_name = None
        self._pattr_local_partition_id = None
        self._pattr_location_code = None
        self._pattr_required_adapter = None
        self._pattr_use_next_available_slot_id = None
        self._pattr_varied_on = None
        self._pattr_virtual_slot_number = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualIOAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def adapter_type(self):
        return self._pattr_adapter_type

    @property
    def dynamic_reconfiguration_connector_name(self):
        return self._pattr_dynamic_reconfiguration_connector_name
    @dynamic_reconfiguration_connector_name.setter
    def dynamic_reconfiguration_connector_name(self, value):
        self._modified_attrs.add("dynamic_reconfiguration_connector_name")
        self._pattr_dynamic_reconfiguration_connector_name = value

    @property
    def local_partition_id(self):
        return self._pattr_local_partition_id
    @local_partition_id.setter
    def local_partition_id(self, value):
        self._modified_attrs.add("local_partition_id")
        self._pattr_local_partition_id = value

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def required_adapter(self):
        return self._pattr_required_adapter
    @required_adapter.setter
    def required_adapter(self, value):
        self._modified_attrs.add("required_adapter")
        self._pattr_required_adapter = value

    @property
    def use_next_available_slot_id(self):
        return self._pattr_use_next_available_slot_id
    @use_next_available_slot_id.setter
    def use_next_available_slot_id(self, value):
        self._modified_attrs.add("use_next_available_slot_id")
        self._pattr_use_next_available_slot_id = value

    @property
    def varied_on(self):
        return self._pattr_varied_on
    @varied_on.setter
    def varied_on(self, value):
        self._modified_attrs.add("varied_on")
        self._pattr_varied_on = value

    @property
    def virtual_slot_number(self):
        return self._pattr_virtual_slot_number
    @virtual_slot_number.setter
    def virtual_slot_number(self, value):
        self._modified_attrs.add("virtual_slot_number")
        self._pattr_virtual_slot_number = value


class VirtualEthernetAdapter(VirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_operating_system_mac_addresses = None
        self._pattr_associated_virtual_switch = None
        self._pattr_device_name = None
        self._pattr_mac_address = None
        self._pattr_port_vlan_id = None
        self._pattr_quality_of_service_priority = None
        self._pattr_quality_of_service_priority_enabled = None
        self._pattr_tagged_vlan_ids = None
        self._pattr_tagged_vlan_supported = None
        self._pattr_virtual_station_interface_manager_id = None
        self._pattr_virtual_station_interface_type_id = None
        self._pattr_virtual_station_interface_type_version = None
        self._pattr_virtual_switch_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualEthernetAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def allowed_operating_system_mac_addresses(self):
        return self._pattr_allowed_operating_system_mac_addresses
    @allowed_operating_system_mac_addresses.setter
    def allowed_operating_system_mac_addresses(self, value):
        self._modified_attrs.add("allowed_operating_system_mac_addresses")
        self._pattr_allowed_operating_system_mac_addresses = value

    @property
    def associated_virtual_switch(self):
        return self._pattr_associated_virtual_switch
    @associated_virtual_switch.setter
    def associated_virtual_switch(self, value):
        self._modified_attrs.add("associated_virtual_switch")
        self._pattr_associated_virtual_switch = value

    @property
    def device_name(self):
        return self._pattr_device_name

    @property
    def mac_address(self):
        return self._pattr_mac_address
    @mac_address.setter
    def mac_address(self, value):
        self._modified_attrs.add("mac_address")
        self._pattr_mac_address = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def quality_of_service_priority(self):
        return self._pattr_quality_of_service_priority
    @quality_of_service_priority.setter
    def quality_of_service_priority(self, value):
        self._modified_attrs.add("quality_of_service_priority")
        self._pattr_quality_of_service_priority = value

    @property
    def quality_of_service_priority_enabled(self):
        return self._pattr_quality_of_service_priority_enabled
    @quality_of_service_priority_enabled.setter
    def quality_of_service_priority_enabled(self, value):
        self._modified_attrs.add("quality_of_service_priority_enabled")
        self._pattr_quality_of_service_priority_enabled = value

    @property
    def tagged_vlan_ids(self):
        return self._pattr_tagged_vlan_ids
    @tagged_vlan_ids.setter
    def tagged_vlan_ids(self, value):
        self._modified_attrs.add("tagged_vlan_ids")
        self._pattr_tagged_vlan_ids = value

    @property
    def tagged_vlan_supported(self):
        return self._pattr_tagged_vlan_supported
    @tagged_vlan_supported.setter
    def tagged_vlan_supported(self, value):
        self._modified_attrs.add("tagged_vlan_supported")
        self._pattr_tagged_vlan_supported = value

    @property
    def virtual_station_interface_manager_id(self):
        return self._pattr_virtual_station_interface_manager_id
    @virtual_station_interface_manager_id.setter
    def virtual_station_interface_manager_id(self, value):
        self._modified_attrs.add("virtual_station_interface_manager_id")
        self._pattr_virtual_station_interface_manager_id = value

    @property
    def virtual_station_interface_type_id(self):
        return self._pattr_virtual_station_interface_type_id
    @virtual_station_interface_type_id.setter
    def virtual_station_interface_type_id(self, value):
        self._modified_attrs.add("virtual_station_interface_type_id")
        self._pattr_virtual_station_interface_type_id = value

    @property
    def virtual_station_interface_type_version(self):
        return self._pattr_virtual_station_interface_type_version
    @virtual_station_interface_type_version.setter
    def virtual_station_interface_type_version(self, value):
        self._modified_attrs.add("virtual_station_interface_type_version")
        self._pattr_virtual_station_interface_type_version = value

    @property
    def virtual_switch_id(self):
        return self._pattr_virtual_switch_id


class ClientNetworkAdapter(VirtualEthernetAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_networks = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(ClientNetworkAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def virtual_networks(self):
        return self._pattr_virtual_networks
    @virtual_networks.setter
    def virtual_networks(self, value):
        self._modified_attrs.add("virtual_networks")
        self._pattr_virtual_networks = value


class ClientNetworkAdapter_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(ClientNetworkAdapter_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class Cluster(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_cluster_id = None
        self._pattr_cluster_name = None
        self._pattr_cluster_shared_storage_pool = None
        self._pattr_node = None
        self._pattr_repository_disk = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(Cluster,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def cluster_id(self):
        return self._pattr_cluster_id
    @cluster_id.setter
    def cluster_id(self, value):
        self._modified_attrs.add("cluster_id")
        self._pattr_cluster_id = value

    @property
    def cluster_name(self):
        return self._pattr_cluster_name
    @cluster_name.setter
    def cluster_name(self, value):
        self._modified_attrs.add("cluster_name")
        self._pattr_cluster_name = value

    @property
    def cluster_shared_storage_pool(self):
        return self._pattr_cluster_shared_storage_pool
    @cluster_shared_storage_pool.setter
    def cluster_shared_storage_pool(self, value):
        self._modified_attrs.add("cluster_shared_storage_pool")
        self._pattr_cluster_shared_storage_pool = value

    @property
    def node(self):
        return self._pattr_node
    @node.setter
    def node(self, value):
        self._modified_attrs.add("node")
        self._pattr_node = value

    @property
    def repository_disk(self):
        return self._pattr_repository_disk
    @repository_disk.setter
    def repository_disk(self, value):
        self._modified_attrs.add("repository_disk")
        self._pattr_repository_disk = value

    def sharedstoragepool_id(self):
        return self.cluster_shared_storage_pool.split("/")[-1]

    def lu_linked_clone(self, source_lu_udid, dest_lu_udid, xa=None):
        """Clone the source logicalunit to the dest logicalunit.

        See :class: ClusterManager for details.
        """

        return self.api.lu_linked_clone(self,
                                        source_lu_udid,
                                        dest_lu_udid,
                                        xa=xa)

    def lu_linked_clone_of_lu_bp(
        self,
        ssp,
        source_lu_udid,
        dest_lu_unit_name,
        dest_lu_unit_capacity=None,
        dest_lu_thin_device=None,
        dest_lu_logical_unit_type="VirtualIO_Disk",
        xa=None):
        """Create a new destination LU and linked_clone the source to it.

        See :class: ClusterManager for details."""

        return self.api.lu_linked_clone_of_lu_bp(
            self,
            ssp,
            source_lu_udid,
            dest_lu_unit_name,
            dest_lu_unit_capacity=dest_lu_unit_capacity,
            dest_lu_thin_device=dest_lu_thin_device,
            dest_lu_logical_unit_type=dest_lu_logical_unit_type,
            xa=xa)

    def lu_linked_clone_of_lu_bj(
        self,
        source_lu,
        dest_lu_unit_name,
        dest_lu_unit_capacity=None,
        dest_lu_thin_device=None,
        dest_lu_logical_unit_type="VirtualIO_Disk",
        xa=None):
        """Create a new destination LU cloned from existing source_lu_udid.

        See :class: ClusterManager for details."""

        return self.api.lu_linked_clone_of_lu_bj(
            self,
            source_lu,
            dest_lu_unit_name,
            dest_lu_unit_capacity=dest_lu_unit_capacity,
            dest_lu_thin_device=dest_lu_thin_device,
            dest_lu_logical_unit_type=dest_lu_logical_unit_type,
            xa=xa)

    def lu_create(self,
                  lu_unit_name,
                  lu_unit_capacity,
                  thin=True,
                  logicalunittype="VirtualIO_Disk",
                  clonedfrom=None,
                  xa=None):
        """Create a new logicalunit.

        See :class: ClusterManager for details.
        """

        return self.api.lu_create(self,
                                  lu_unit_name,
                                  lu_unit_capacity,
                                  thin=thin,
                                  logicalunittype=logicalunittype,
                                  clonedfrom=clonedfrom,
                                  xa=xa)


class IOAdapter(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_id = None
        self._pattr_description = None
        self._pattr_device_name = None
        self._pattr_device_type = None
        self._pattr_dynamic_reconfiguration_connector_name = None
        self._pattr_physical_location = None
        self._pattr_unique_device_id = None
        super(IOAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def adapter_id(self):
        return self._pattr_adapter_id

    @property
    def description(self):
        return self._pattr_description
    @description.setter
    def description(self, value):
        self._modified_attrs.add("description")
        self._pattr_description = value

    @property
    def device_name(self):
        return self._pattr_device_name

    @property
    def device_type(self):
        return self._pattr_device_type

    @property
    def dynamic_reconfiguration_connector_name(self):
        return self._pattr_dynamic_reconfiguration_connector_name
    @dynamic_reconfiguration_connector_name.setter
    def dynamic_reconfiguration_connector_name(self, value):
        self._modified_attrs.add("dynamic_reconfiguration_connector_name")
        self._pattr_dynamic_reconfiguration_connector_name = value

    @property
    def physical_location(self):
        return self._pattr_physical_location

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id


class EthernetBackingDevice(IOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        self._pattr_ip_interface = None
        super(EthernetBackingDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value

    @property
    def ip_interface(self):
        return self._pattr_ip_interface
    @ip_interface.setter
    def ip_interface(self, value):
        self._modified_attrs.add("ip_interface")
        self._pattr_ip_interface = value


class Event(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_event_data = None
        self._pattr_event_detail = None
        self._pattr_event_id = None
        self._pattr_event_type = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(Event,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def event_data(self):
        return self._pattr_event_data

    @property
    def event_detail(self):
        return self._pattr_event_detail

    @property
    def event_id(self):
        return self._pattr_event_id

    @property
    def event_type(self):
        return self._pattr_event_type


class HostChannelAdapter(IOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allocation_allowed = None
        self._pattr_assigned_uui_ds = None
        self._pattr_cable_type = None
        self._pattr_capability = None
        self._pattr_is_functional = None
        self._pattr_physical_location_code = None
        self._pattr_unassigned_gui_ds = None
        self._pattr_uuid_list_sequential = None
        super(HostChannelAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allocation_allowed(self):
        return self._pattr_allocation_allowed
    @allocation_allowed.setter
    def allocation_allowed(self, value):
        self._modified_attrs.add("allocation_allowed")
        self._pattr_allocation_allowed = value

    @property
    def assigned_uui_ds(self):
        return self._pattr_assigned_uui_ds
    @assigned_uui_ds.setter
    def assigned_uui_ds(self, value):
        self._modified_attrs.add("assigned_uui_ds")
        self._pattr_assigned_uui_ds = value

    @property
    def cable_type(self):
        return self._pattr_cable_type

    @property
    def capability(self):
        return self._pattr_capability
    @capability.setter
    def capability(self, value):
        self._modified_attrs.add("capability")
        self._pattr_capability = value

    @property
    def is_functional(self):
        return self._pattr_is_functional

    @property
    def physical_location_code(self):
        return self._pattr_physical_location_code

    @property
    def unassigned_gui_ds(self):
        return self._pattr_unassigned_gui_ds
    @unassigned_gui_ds.setter
    def unassigned_gui_ds(self, value):
        self._modified_attrs.add("unassigned_gui_ds")
        self._pattr_unassigned_gui_ds = value

    @property
    def uuid_list_sequential(self):
        return self._pattr_uuid_list_sequential


class HostChannelAdapterBandwidthCapability(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_high_percentage = None
        self._pattr_low_percentage = None
        self._pattr_medium_percentage = None
        super(HostChannelAdapterBandwidthCapability,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def high_percentage(self):
        return self._pattr_high_percentage
    @high_percentage.setter
    def high_percentage(self, value):
        self._modified_attrs.add("high_percentage")
        self._pattr_high_percentage = value

    @property
    def low_percentage(self):
        return self._pattr_low_percentage
    @low_percentage.setter
    def low_percentage(self, value):
        self._modified_attrs.add("low_percentage")
        self._pattr_low_percentage = value

    @property
    def medium_percentage(self):
        return self._pattr_medium_percentage
    @medium_percentage.setter
    def medium_percentage(self, value):
        self._modified_attrs.add("medium_percentage")
        self._pattr_medium_percentage = value


class HostChannelAdapter_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_host_channel_adapter = []
        super(HostChannelAdapter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def host_channel_adapter(self):
        return self._pattr_host_channel_adapter
    @host_channel_adapter.setter
    def host_channel_adapter(self, value):
        self._modified_attrs.add("host_channel_adapter")
        self._pattr_host_channel_adapter = value


class HostEthernetAdapter(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_id = None
        self._pattr_adapter_state = None
        self._pattr_physical_location_code = None
        self._pattr_port_groups = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(HostEthernetAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def adapter_id(self):
        return self._pattr_adapter_id

    @property
    def adapter_state(self):
        return self._pattr_adapter_state

    @property
    def physical_location_code(self):
        return self._pattr_physical_location_code

    @property
    def port_groups(self):
        return self._pattr_port_groups
    @port_groups.setter
    def port_groups(self, value):
        self._modified_attrs.add("port_groups")
        self._pattr_port_groups = value


class HostEthernetAdapterLogicalPort(EthernetBackingDevice):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_osmac_addresses = None
        self._pattr_allowed_vlani_ds = None
        self._pattr_hea_logical_port_physical_location = None
        self._pattr_logical_port_id = None
        self._pattr_mac_address = None
        self._pattr_mac_address_directives = None
        self._pattr_partition_link = None
        self._pattr_physical_port_id = None
        self._pattr_port_group_id = None
        self._pattr_port_state = None
        super(HostEthernetAdapterLogicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allowed_osmac_addresses(self):
        return self._pattr_allowed_osmac_addresses
    @allowed_osmac_addresses.setter
    def allowed_osmac_addresses(self, value):
        self._modified_attrs.add("allowed_osmac_addresses")
        self._pattr_allowed_osmac_addresses = value

    @property
    def allowed_vlani_ds(self):
        return self._pattr_allowed_vlani_ds
    @allowed_vlani_ds.setter
    def allowed_vlani_ds(self, value):
        self._modified_attrs.add("allowed_vlani_ds")
        self._pattr_allowed_vlani_ds = value

    @property
    def hea_logical_port_physical_location(self):
        return self._pattr_hea_logical_port_physical_location

    @property
    def logical_port_id(self):
        return self._pattr_logical_port_id
    @logical_port_id.setter
    def logical_port_id(self, value):
        self._modified_attrs.add("logical_port_id")
        self._pattr_logical_port_id = value

    @property
    def mac_address(self):
        return self._pattr_mac_address
    @mac_address.setter
    def mac_address(self, value):
        self._modified_attrs.add("mac_address")
        self._pattr_mac_address = value

    @property
    def mac_address_directives(self):
        return self._pattr_mac_address_directives
    @mac_address_directives.setter
    def mac_address_directives(self, value):
        self._modified_attrs.add("mac_address_directives")
        self._pattr_mac_address_directives = value

    @property
    def partition_link(self):
        return self._pattr_partition_link
    @partition_link.setter
    def partition_link(self, value):
        self._modified_attrs.add("partition_link")
        self._pattr_partition_link = value

    @property
    def physical_port_id(self):
        return self._pattr_physical_port_id

    @property
    def port_group_id(self):
        return self._pattr_port_group_id
    @port_group_id.setter
    def port_group_id(self, value):
        self._modified_attrs.add("port_group_id")
        self._pattr_port_group_id = value

    @property
    def port_state(self):
        return self._pattr_port_state


class HostEthernetAdapterLogicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_host_ethernet_adapter_logical_port = []
        super(HostEthernetAdapterLogicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def host_ethernet_adapter_logical_port(self):
        return self._pattr_host_ethernet_adapter_logical_port
    @host_ethernet_adapter_logical_port.setter
    def host_ethernet_adapter_logical_port(self, value):
        self._modified_attrs.add("host_ethernet_adapter_logical_port")
        self._pattr_host_ethernet_adapter_logical_port = value


class HostEthernetAdapterPhysicalPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_connection_speed = None
        self._pattr_current_duplex_mode = None
        self._pattr_dedicated = None
        self._pattr_link_up = None
        self._pattr_maximum_receive_packet_size = None
        self._pattr_owner = None
        self._pattr_partition_link = None
        self._pattr_pending_connection_speed = None
        self._pattr_pending_duplex_mode = None
        self._pattr_pending_flow_control_enabled = None
        self._pattr_physical_port_id = None
        self._pattr_physical_port_location_code = None
        self._pattr_physical_port_state = None
        self._pattr_physical_port_type = None
        self._pattr_receive_flow_control_enabled = None
        self._pattr_transmit_flow_control_enabled = None
        super(HostEthernetAdapterPhysicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_connection_speed(self):
        return self._pattr_current_connection_speed
    @current_connection_speed.setter
    def current_connection_speed(self, value):
        self._modified_attrs.add("current_connection_speed")
        self._pattr_current_connection_speed = value

    @property
    def current_duplex_mode(self):
        return self._pattr_current_duplex_mode
    @current_duplex_mode.setter
    def current_duplex_mode(self, value):
        self._modified_attrs.add("current_duplex_mode")
        self._pattr_current_duplex_mode = value

    @property
    def dedicated(self):
        return self._pattr_dedicated
    @dedicated.setter
    def dedicated(self, value):
        self._modified_attrs.add("dedicated")
        self._pattr_dedicated = value

    @property
    def link_up(self):
        return self._pattr_link_up

    @property
    def maximum_receive_packet_size(self):
        return self._pattr_maximum_receive_packet_size
    @maximum_receive_packet_size.setter
    def maximum_receive_packet_size(self, value):
        self._modified_attrs.add("maximum_receive_packet_size")
        self._pattr_maximum_receive_packet_size = value

    @property
    def owner(self):
        return self._pattr_owner
    @owner.setter
    def owner(self, value):
        self._modified_attrs.add("owner")
        self._pattr_owner = value

    @property
    def partition_link(self):
        return self._pattr_partition_link
    @partition_link.setter
    def partition_link(self, value):
        self._modified_attrs.add("partition_link")
        self._pattr_partition_link = value

    @property
    def pending_connection_speed(self):
        return self._pattr_pending_connection_speed
    @pending_connection_speed.setter
    def pending_connection_speed(self, value):
        self._modified_attrs.add("pending_connection_speed")
        self._pattr_pending_connection_speed = value

    @property
    def pending_duplex_mode(self):
        return self._pattr_pending_duplex_mode
    @pending_duplex_mode.setter
    def pending_duplex_mode(self, value):
        self._modified_attrs.add("pending_duplex_mode")
        self._pattr_pending_duplex_mode = value

    @property
    def pending_flow_control_enabled(self):
        return self._pattr_pending_flow_control_enabled
    @pending_flow_control_enabled.setter
    def pending_flow_control_enabled(self, value):
        self._modified_attrs.add("pending_flow_control_enabled")
        self._pattr_pending_flow_control_enabled = value

    @property
    def physical_port_id(self):
        return self._pattr_physical_port_id
    @physical_port_id.setter
    def physical_port_id(self, value):
        self._modified_attrs.add("physical_port_id")
        self._pattr_physical_port_id = value

    @property
    def physical_port_location_code(self):
        return self._pattr_physical_port_location_code
    @physical_port_location_code.setter
    def physical_port_location_code(self, value):
        self._modified_attrs.add("physical_port_location_code")
        self._pattr_physical_port_location_code = value

    @property
    def physical_port_state(self):
        return self._pattr_physical_port_state
    @physical_port_state.setter
    def physical_port_state(self, value):
        self._modified_attrs.add("physical_port_state")
        self._pattr_physical_port_state = value

    @property
    def physical_port_type(self):
        return self._pattr_physical_port_type
    @physical_port_type.setter
    def physical_port_type(self, value):
        self._modified_attrs.add("physical_port_type")
        self._pattr_physical_port_type = value

    @property
    def receive_flow_control_enabled(self):
        return self._pattr_receive_flow_control_enabled

    @property
    def transmit_flow_control_enabled(self):
        return self._pattr_transmit_flow_control_enabled


class HostEthernetAdapterPhysicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_host_ethernet_adapter_physical_port = []
        super(HostEthernetAdapterPhysicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def host_ethernet_adapter_physical_port(self):
        return self._pattr_host_ethernet_adapter_physical_port
    @host_ethernet_adapter_physical_port.setter
    def host_ethernet_adapter_physical_port(self, value):
        self._modified_attrs.add("host_ethernet_adapter_physical_port")
        self._pattr_host_ethernet_adapter_physical_port = value


class HostEthernetAdapterPortGroup(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_multi_core_scaling = None
        self._pattr_logical_ports = None
        self._pattr_pending_multi_core_scaling = None
        self._pattr_physical_ports = None
        self._pattr_port_group_id = None
        self._pattr_supported_multi_core_scaling_values = None
        super(HostEthernetAdapterPortGroup,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_multi_core_scaling(self):
        return self._pattr_current_multi_core_scaling

    @property
    def logical_ports(self):
        return self._pattr_logical_ports
    @logical_ports.setter
    def logical_ports(self, value):
        self._modified_attrs.add("logical_ports")
        self._pattr_logical_ports = value

    @property
    def pending_multi_core_scaling(self):
        return self._pattr_pending_multi_core_scaling
    @pending_multi_core_scaling.setter
    def pending_multi_core_scaling(self, value):
        self._modified_attrs.add("pending_multi_core_scaling")
        self._pattr_pending_multi_core_scaling = value

    @property
    def physical_ports(self):
        return self._pattr_physical_ports
    @physical_ports.setter
    def physical_ports(self, value):
        self._modified_attrs.add("physical_ports")
        self._pattr_physical_ports = value

    @property
    def port_group_id(self):
        return self._pattr_port_group_id
    @port_group_id.setter
    def port_group_id(self, value):
        self._modified_attrs.add("port_group_id")
        self._pattr_port_group_id = value

    @property
    def supported_multi_core_scaling_values(self):
        return self._pattr_supported_multi_core_scaling_values


class HostEthernetAdapterPortGroup_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_host_ethernet_adapter_port_group = []
        super(HostEthernetAdapterPortGroup_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def host_ethernet_adapter_port_group(self):
        return self._pattr_host_ethernet_adapter_port_group
    @host_ethernet_adapter_port_group.setter
    def host_ethernet_adapter_port_group(self, value):
        self._modified_attrs.add("host_ethernet_adapter_port_group")
        self._pattr_host_ethernet_adapter_port_group = value


class HostEthernetAdapter_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(HostEthernetAdapter_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class IBMiIOSlot(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_alternate_load_source_attached = None
        self._pattr_console_capable = None
        self._pattr_direct_operations_console_capable = None
        self._pattr_io_pool_id = None
        self._pattr_iop = None
        self._pattr_iop_info_stale = None
        self._pattr_lan_console_capable = None
        self._pattr_load_source_attached = None
        self._pattr_load_source_capable = None
        self._pattr_operations_console_attached = None
        self._pattr_operations_console_capable = None
        super(IBMiIOSlot,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def alternate_load_source_attached(self):
        return self._pattr_alternate_load_source_attached

    @property
    def console_capable(self):
        return self._pattr_console_capable

    @property
    def direct_operations_console_capable(self):
        return self._pattr_direct_operations_console_capable

    @property
    def io_pool_id(self):
        return self._pattr_io_pool_id

    @property
    def iop(self):
        return self._pattr_iop

    @property
    def iop_info_stale(self):
        return self._pattr_iop_info_stale

    @property
    def lan_console_capable(self):
        return self._pattr_lan_console_capable

    @property
    def load_source_attached(self):
        return self._pattr_load_source_attached

    @property
    def load_source_capable(self):
        return self._pattr_load_source_capable

    @property
    def operations_console_attached(self):
        return self._pattr_operations_console_attached

    @property
    def operations_console_capable(self):
        return self._pattr_operations_console_capable


class IBMiProfileTaggedIO(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_alternate_console = None
        self._pattr_alternate_load_source = None
        self._pattr_console = None
        self._pattr_load_source = None
        self._pattr_operations_console = None
        super(IBMiProfileTaggedIO,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def alternate_console(self):
        return self._pattr_alternate_console
    @alternate_console.setter
    def alternate_console(self, value):
        self._modified_attrs.add("alternate_console")
        self._pattr_alternate_console = value

    @property
    def alternate_load_source(self):
        return self._pattr_alternate_load_source
    @alternate_load_source.setter
    def alternate_load_source(self, value):
        self._modified_attrs.add("alternate_load_source")
        self._pattr_alternate_load_source = value

    @property
    def console(self):
        return self._pattr_console
    @console.setter
    def console(self, value):
        self._modified_attrs.add("console")
        self._pattr_console = value

    @property
    def load_source(self):
        return self._pattr_load_source
    @load_source.setter
    def load_source(self, value):
        self._modified_attrs.add("load_source")
        self._pattr_load_source = value

    @property
    def operations_console(self):
        return self._pattr_operations_console
    @operations_console.setter
    def operations_console(self, value):
        self._modified_attrs.add("operations_console")
        self._pattr_operations_console = value


class IOAdapterChoiceCollection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_io_adapter_choice = []
        super(IOAdapterChoiceCollection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def io_adapter_choice(self):
        return self._pattr_io_adapter_choice
    @io_adapter_choice.setter
    def io_adapter_choice(self, value):
        self._modified_attrs.add("io_adapter_choice")
        self._pattr_io_adapter_choice = value


class IOBus(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_backplane_physical_location = None
        self._pattr_bus_dynamic_reconfiguration_connector_index = None
        self._pattr_bus_dynamic_reconfiguration_connector_name = None
        self._pattr_io_bus_id = None
        self._pattr_io_slots = None
        super(IOBus,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def backplane_physical_location(self):
        return self._pattr_backplane_physical_location

    @property
    def bus_dynamic_reconfiguration_connector_index(self):
        return self._pattr_bus_dynamic_reconfiguration_connector_index

    @property
    def bus_dynamic_reconfiguration_connector_name(self):
        return self._pattr_bus_dynamic_reconfiguration_connector_name

    @property
    def io_bus_id(self):
        return self._pattr_io_bus_id

    @property
    def io_slots(self):
        return self._pattr_io_slots


class IOBus_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_io_bus = []
        super(IOBus_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def io_bus(self):
        return self._pattr_io_bus
    @io_bus.setter
    def io_bus(self, value):
        self._modified_attrs.add("io_bus")
        self._pattr_io_bus = value


class IOSlot(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_bus_grouping_required = None
        self._pattr_description = None
        self._pattr_feature_codes = []
        self._pattr_io_unit_physical_location = None
        self._pattr_parent_slot_dynamic_reconfiguration_connector_index = None
        self._pattr_pc_adapter_id = None
        self._pattr_pci_class = None
        self._pattr_pci_device_id = None
        self._pattr_pci_manufacturer_id = None
        self._pattr_pci_revision_id = None
        self._pattr_pci_subsystem_device_id = None
        self._pattr_pci_subsystem_vendor_id = None
        self._pattr_pci_vendor_id = None
        self._pattr_related_ibm_i_io_slot = None
        self._pattr_related_io_adapter = None
        self._pattr_slot_dynamic_reconfiguration_connector_index = None
        self._pattr_slot_dynamic_reconfiguration_connector_name = None
        self._pattr_slot_physical_location_code = None
        self._pattr_twinaxial_attached = None
        self._pattr_twinaxial_capable = None
        self._pattr_vital_product_data_model = None
        self._pattr_vital_product_data_serial_number = None
        self._pattr_vital_product_data_stale = None
        self._pattr_vital_product_data_type = None
        super(IOSlot,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def bus_grouping_required(self):
        return self._pattr_bus_grouping_required
    @bus_grouping_required.setter
    def bus_grouping_required(self, value):
        self._modified_attrs.add("bus_grouping_required")
        self._pattr_bus_grouping_required = value

    @property
    def description(self):
        return self._pattr_description
    @description.setter
    def description(self, value):
        self._modified_attrs.add("description")
        self._pattr_description = value

    @property
    def feature_codes(self):
        return self._pattr_feature_codes

    @property
    def io_unit_physical_location(self):
        return self._pattr_io_unit_physical_location

    @property
    def parent_slot_dynamic_reconfiguration_connector_index(self):
        return self._pattr_parent_slot_dynamic_reconfiguration_connector_index

    @property
    def pc_adapter_id(self):
        return self._pattr_pc_adapter_id

    @property
    def pci_class(self):
        return self._pattr_pci_class

    @property
    def pci_device_id(self):
        return self._pattr_pci_device_id

    @property
    def pci_manufacturer_id(self):
        return self._pattr_pci_manufacturer_id

    @property
    def pci_revision_id(self):
        return self._pattr_pci_revision_id

    @property
    def pci_subsystem_device_id(self):
        return self._pattr_pci_subsystem_device_id

    @property
    def pci_subsystem_vendor_id(self):
        return self._pattr_pci_subsystem_vendor_id

    @property
    def pci_vendor_id(self):
        return self._pattr_pci_vendor_id

    @property
    def related_ibm_i_io_slot(self):
        return self._pattr_related_ibm_i_io_slot
    @related_ibm_i_io_slot.setter
    def related_ibm_i_io_slot(self, value):
        self._modified_attrs.add("related_ibm_i_io_slot")
        self._pattr_related_ibm_i_io_slot = value

    @property
    def related_io_adapter(self):
        return self._pattr_related_io_adapter
    @related_io_adapter.setter
    def related_io_adapter(self, value):
        self._modified_attrs.add("related_io_adapter")
        self._pattr_related_io_adapter = value

    @property
    def slot_dynamic_reconfiguration_connector_index(self):
        return self._pattr_slot_dynamic_reconfiguration_connector_index

    @property
    def slot_dynamic_reconfiguration_connector_name(self):
        return self._pattr_slot_dynamic_reconfiguration_connector_name
    @slot_dynamic_reconfiguration_connector_name.setter
    def slot_dynamic_reconfiguration_connector_name(self, value):
        self._modified_attrs.add("slot_dynamic_reconfiguration_connector_name")
        self._pattr_slot_dynamic_reconfiguration_connector_name = value

    @property
    def slot_physical_location_code(self):
        return self._pattr_slot_physical_location_code

    @property
    def twinaxial_attached(self):
        return self._pattr_twinaxial_attached

    @property
    def twinaxial_capable(self):
        return self._pattr_twinaxial_capable

    @property
    def vital_product_data_model(self):
        return self._pattr_vital_product_data_model

    @property
    def vital_product_data_serial_number(self):
        return self._pattr_vital_product_data_serial_number

    @property
    def vital_product_data_stale(self):
        return self._pattr_vital_product_data_stale

    @property
    def vital_product_data_type(self):
        return self._pattr_vital_product_data_type


class IOSlot_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_io_slot = []
        super(IOSlot_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def io_slot(self):
        return self._pattr_io_slot
    @io_slot.setter
    def io_slot(self, value):
        self._modified_attrs.add("io_slot")
        self._pattr_io_slot = value


class IOUnit(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_io_buses = None
        self._pattr_io_unit_id = None
        self._pattr_io_unit_physical_location = None
        self._pattr_io_unit_system_power_control_network_id = None
        self._pattr_machine_type_model_and_serial_number = None
        super(IOUnit,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def io_buses(self):
        return self._pattr_io_buses

    @property
    def io_unit_id(self):
        return self._pattr_io_unit_id

    @property
    def io_unit_physical_location(self):
        return self._pattr_io_unit_physical_location

    @property
    def io_unit_system_power_control_network_id(self):
        return self._pattr_io_unit_system_power_control_network_id

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number


class IOUnit_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_io_unit = []
        super(IOUnit_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def io_unit(self):
        return self._pattr_io_unit
    @io_unit.setter
    def io_unit(self, value):
        self._modified_attrs.add("io_unit")
        self._pattr_io_unit = value


class IPInterface(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_gateway = None
        self._pattr_host_name = None
        self._pattr_interface_name = None
        self._pattr_ip_address = None
        self._pattr_ipv6_prefix = None
        self._pattr_state = None
        self._pattr_subnet_mask = None
        super(IPInterface,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def gateway(self):
        return self._pattr_gateway
    @gateway.setter
    def gateway(self, value):
        self._modified_attrs.add("gateway")
        self._pattr_gateway = value

    @property
    def host_name(self):
        return self._pattr_host_name
    @host_name.setter
    def host_name(self, value):
        self._modified_attrs.add("host_name")
        self._pattr_host_name = value

    @property
    def interface_name(self):
        return self._pattr_interface_name
    @interface_name.setter
    def interface_name(self, value):
        self._modified_attrs.add("interface_name")
        self._pattr_interface_name = value

    @property
    def ip_address(self):
        return self._pattr_ip_address
    @ip_address.setter
    def ip_address(self, value):
        self._modified_attrs.add("ip_address")
        self._pattr_ip_address = value

    @property
    def ipv6_prefix(self):
        return self._pattr_ipv6_prefix
    @ipv6_prefix.setter
    def ipv6_prefix(self, value):
        self._modified_attrs.add("ipv6_prefix")
        self._pattr_ipv6_prefix = value

    @property
    def state(self):
        return self._pattr_state
    @state.setter
    def state(self, value):
        self._modified_attrs.add("state")
        self._pattr_state = value

    @property
    def subnet_mask(self):
        return self._pattr_subnet_mask
    @subnet_mask.setter
    def subnet_mask(self, value):
        self._modified_attrs.add("subnet_mask")
        self._pattr_subnet_mask = value


class IPLConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_manufacturing_defaul_configurationt_boot_mode = None
        self._pattr_current_power_on_side = None
        self._pattr_current_system_keylock = None
        self._pattr_current_turbocore_enabled = None
        self._pattr_major_boot_type = None
        self._pattr_minor_boot_type = None
        self._pattr_pending_manufacturing_defaul_configurationt_boot_mode = None
        self._pattr_pending_power_on_side = None
        self._pattr_pending_system_keylock = None
        self._pattr_pending_turbocore_enabled = None
        self._pattr_power_off_when_last_logical_partition_is_shutdown = None
        self._pattr_power_on_logical_partition_start_policy = None
        self._pattr_power_on_option = None
        self._pattr_power_on_speed = None
        self._pattr_power_on_speed_override = None
        super(IPLConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_manufacturing_defaul_configurationt_boot_mode(self):
        return self._pattr_current_manufacturing_defaul_configurationt_boot_mode

    @property
    def current_power_on_side(self):
        return self._pattr_current_power_on_side

    @property
    def current_system_keylock(self):
        return self._pattr_current_system_keylock

    @property
    def current_turbocore_enabled(self):
        return self._pattr_current_turbocore_enabled

    @property
    def major_boot_type(self):
        return self._pattr_major_boot_type
    @major_boot_type.setter
    def major_boot_type(self, value):
        self._modified_attrs.add("major_boot_type")
        self._pattr_major_boot_type = value

    @property
    def minor_boot_type(self):
        return self._pattr_minor_boot_type
    @minor_boot_type.setter
    def minor_boot_type(self, value):
        self._modified_attrs.add("minor_boot_type")
        self._pattr_minor_boot_type = value

    @property
    def pending_manufacturing_defaul_configurationt_boot_mode(self):
        return self._pattr_pending_manufacturing_defaul_configurationt_boot_mode
    @pending_manufacturing_defaul_configurationt_boot_mode.setter
    def pending_manufacturing_defaul_configurationt_boot_mode(self, value):
        self._modified_attrs.add("pending_manufacturing_defaul_configurationt_boot_mode")
        self._pattr_pending_manufacturing_defaul_configurationt_boot_mode = value

    @property
    def pending_power_on_side(self):
        return self._pattr_pending_power_on_side
    @pending_power_on_side.setter
    def pending_power_on_side(self, value):
        self._modified_attrs.add("pending_power_on_side")
        self._pattr_pending_power_on_side = value

    @property
    def pending_system_keylock(self):
        return self._pattr_pending_system_keylock
    @pending_system_keylock.setter
    def pending_system_keylock(self, value):
        self._modified_attrs.add("pending_system_keylock")
        self._pattr_pending_system_keylock = value

    @property
    def pending_turbocore_enabled(self):
        return self._pattr_pending_turbocore_enabled
    @pending_turbocore_enabled.setter
    def pending_turbocore_enabled(self, value):
        self._modified_attrs.add("pending_turbocore_enabled")
        self._pattr_pending_turbocore_enabled = value

    @property
    def power_off_when_last_logical_partition_is_shutdown(self):
        return self._pattr_power_off_when_last_logical_partition_is_shutdown
    @power_off_when_last_logical_partition_is_shutdown.setter
    def power_off_when_last_logical_partition_is_shutdown(self, value):
        self._modified_attrs.add("power_off_when_last_logical_partition_is_shutdown")
        self._pattr_power_off_when_last_logical_partition_is_shutdown = value

    @property
    def power_on_logical_partition_start_policy(self):
        return self._pattr_power_on_logical_partition_start_policy
    @power_on_logical_partition_start_policy.setter
    def power_on_logical_partition_start_policy(self, value):
        self._modified_attrs.add("power_on_logical_partition_start_policy")
        self._pattr_power_on_logical_partition_start_policy = value

    @property
    def power_on_option(self):
        return self._pattr_power_on_option
    @power_on_option.setter
    def power_on_option(self, value):
        self._modified_attrs.add("power_on_option")
        self._pattr_power_on_option = value

    @property
    def power_on_speed(self):
        return self._pattr_power_on_speed
    @power_on_speed.setter
    def power_on_speed(self, value):
        self._modified_attrs.add("power_on_speed")
        self._pattr_power_on_speed = value

    @property
    def power_on_speed_override(self):
        return self._pattr_power_on_speed_override
    @power_on_speed_override.setter
    def power_on_speed_override(self, value):
        self._modified_attrs.add("power_on_speed_override")
        self._pattr_power_on_speed_override = value


class LinkAggregation(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_alternate_address = None
        self._pattr_auto_recovery_enabled = None
        self._pattr_backup_adapter = None
        self._pattr_description = None
        self._pattr_device_id = None
        self._pattr_device_name = None
        self._pattr_hash_mode = None
        self._pattr_io_adapters = None
        self._pattr_ip_address_to_ping = None
        self._pattr_ip_interface = None
        self._pattr_jumbo_frame_enabled = None
        self._pattr_mode = None
        self._pattr_no_loss_failover_enabled = None
        self._pattr_retry_count = None
        self._pattr_retry_time = None
        self._pattr_use_alternate_address = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(LinkAggregation,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def alternate_address(self):
        return self._pattr_alternate_address
    @alternate_address.setter
    def alternate_address(self, value):
        self._modified_attrs.add("alternate_address")
        self._pattr_alternate_address = value

    @property
    def auto_recovery_enabled(self):
        return self._pattr_auto_recovery_enabled
    @auto_recovery_enabled.setter
    def auto_recovery_enabled(self, value):
        self._modified_attrs.add("auto_recovery_enabled")
        self._pattr_auto_recovery_enabled = value

    @property
    def backup_adapter(self):
        return self._pattr_backup_adapter
    @backup_adapter.setter
    def backup_adapter(self, value):
        self._modified_attrs.add("backup_adapter")
        self._pattr_backup_adapter = value

    @property
    def description(self):
        return self._pattr_description
    @description.setter
    def description(self, value):
        self._modified_attrs.add("description")
        self._pattr_description = value

    @property
    def device_id(self):
        return self._pattr_device_id

    @property
    def device_name(self):
        return self._pattr_device_name
    @device_name.setter
    def device_name(self, value):
        self._modified_attrs.add("device_name")
        self._pattr_device_name = value

    @property
    def hash_mode(self):
        return self._pattr_hash_mode
    @hash_mode.setter
    def hash_mode(self, value):
        self._modified_attrs.add("hash_mode")
        self._pattr_hash_mode = value

    @property
    def io_adapters(self):
        return self._pattr_io_adapters
    @io_adapters.setter
    def io_adapters(self, value):
        self._modified_attrs.add("io_adapters")
        self._pattr_io_adapters = value

    @property
    def ip_address_to_ping(self):
        return self._pattr_ip_address_to_ping
    @ip_address_to_ping.setter
    def ip_address_to_ping(self, value):
        self._modified_attrs.add("ip_address_to_ping")
        self._pattr_ip_address_to_ping = value

    @property
    def ip_interface(self):
        return self._pattr_ip_interface
    @ip_interface.setter
    def ip_interface(self, value):
        self._modified_attrs.add("ip_interface")
        self._pattr_ip_interface = value

    @property
    def jumbo_frame_enabled(self):
        return self._pattr_jumbo_frame_enabled
    @jumbo_frame_enabled.setter
    def jumbo_frame_enabled(self, value):
        self._modified_attrs.add("jumbo_frame_enabled")
        self._pattr_jumbo_frame_enabled = value

    @property
    def mode(self):
        return self._pattr_mode
    @mode.setter
    def mode(self, value):
        self._modified_attrs.add("mode")
        self._pattr_mode = value

    @property
    def no_loss_failover_enabled(self):
        return self._pattr_no_loss_failover_enabled
    @no_loss_failover_enabled.setter
    def no_loss_failover_enabled(self, value):
        self._modified_attrs.add("no_loss_failover_enabled")
        self._pattr_no_loss_failover_enabled = value

    @property
    def retry_count(self):
        return self._pattr_retry_count
    @retry_count.setter
    def retry_count(self, value):
        self._modified_attrs.add("retry_count")
        self._pattr_retry_count = value

    @property
    def retry_time(self):
        return self._pattr_retry_time
    @retry_time.setter
    def retry_time(self, value):
        self._modified_attrs.add("retry_time")
        self._pattr_retry_time = value

    @property
    def use_alternate_address(self):
        return self._pattr_use_alternate_address
    @use_alternate_address.setter
    def use_alternate_address(self, value):
        self._modified_attrs.add("use_alternate_address")
        self._pattr_use_alternate_address = value


class LinkAggregation_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(LinkAggregation_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class LoadGroup(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_port_vlan_id = None
        self._pattr_trunk_adapters = None
        self._pattr_unique_device_id = None
        self._pattr_virtual_networks = None
        super(LoadGroup,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def trunk_adapters(self):
        return self._pattr_trunk_adapters
    @trunk_adapters.setter
    def trunk_adapters(self, value):
        self._modified_attrs.add("trunk_adapters")
        self._pattr_trunk_adapters = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def virtual_networks(self):
        return self._pattr_virtual_networks
    @virtual_networks.setter
    def virtual_networks(self, value):
        self._modified_attrs.add("virtual_networks")
        self._pattr_virtual_networks = value


class LoadGroup_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_load_group = []
        super(LoadGroup_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def load_group(self):
        return self._pattr_load_group
    @load_group.setter
    def load_group(self, value):
        self._modified_attrs.add("load_group")
        self._pattr_load_group = value


class LogicalPartition(BasePartition):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_designated_ipl_source = None
        self._pattr_has_dedicated_processors_for_migration = None
        self._pattr_is_restricted_io_partition = None
        self._pattr_migration_state = None
        self._pattr_power_management_mode = None
        self._pattr_remote_restart_capable = None
        self._pattr_remote_restart_state = None
        self._pattr_storage_device_unique_device_id = None
        self._pattr_suspend_capable = None
        self._pattr_uses_high_speed_link_opticonnect = None
        self._pattr_uses_virtual_opticonnect = None
        self._pattr_virtual_fibre_channel_client_adapters = None
        self._pattr_virtual_scsi_client_adapters = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(LogicalPartition,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def designated_ipl_source(self):
        return self._pattr_designated_ipl_source
    @designated_ipl_source.setter
    def designated_ipl_source(self, value):
        self._modified_attrs.add("designated_ipl_source")
        self._pattr_designated_ipl_source = value

    @property
    def has_dedicated_processors_for_migration(self):
        return self._pattr_has_dedicated_processors_for_migration

    @property
    def is_restricted_io_partition(self):
        return self._pattr_is_restricted_io_partition
    @is_restricted_io_partition.setter
    def is_restricted_io_partition(self, value):
        self._modified_attrs.add("is_restricted_io_partition")
        self._pattr_is_restricted_io_partition = value

    @property
    def migration_state(self):
        return self._pattr_migration_state

    @property
    def power_management_mode(self):
        return self._pattr_power_management_mode
    @power_management_mode.setter
    def power_management_mode(self, value):
        self._modified_attrs.add("power_management_mode")
        self._pattr_power_management_mode = value

    @property
    def remote_restart_capable(self):
        return self._pattr_remote_restart_capable
    @remote_restart_capable.setter
    def remote_restart_capable(self, value):
        self._modified_attrs.add("remote_restart_capable")
        self._pattr_remote_restart_capable = value

    @property
    def remote_restart_state(self):
        return self._pattr_remote_restart_state

    @property
    def storage_device_unique_device_id(self):
        return self._pattr_storage_device_unique_device_id

    @property
    def suspend_capable(self):
        return self._pattr_suspend_capable
    @suspend_capable.setter
    def suspend_capable(self, value):
        self._modified_attrs.add("suspend_capable")
        self._pattr_suspend_capable = value

    @property
    def uses_high_speed_link_opticonnect(self):
        return self._pattr_uses_high_speed_link_opticonnect
    @uses_high_speed_link_opticonnect.setter
    def uses_high_speed_link_opticonnect(self, value):
        self._modified_attrs.add("uses_high_speed_link_opticonnect")
        self._pattr_uses_high_speed_link_opticonnect = value

    @property
    def uses_virtual_opticonnect(self):
        return self._pattr_uses_virtual_opticonnect
    @uses_virtual_opticonnect.setter
    def uses_virtual_opticonnect(self, value):
        self._modified_attrs.add("uses_virtual_opticonnect")
        self._pattr_uses_virtual_opticonnect = value

    @property
    def virtual_fibre_channel_client_adapters(self):
        return self._pattr_virtual_fibre_channel_client_adapters
    @virtual_fibre_channel_client_adapters.setter
    def virtual_fibre_channel_client_adapters(self, value):
        self._modified_attrs.add("virtual_fibre_channel_client_adapters")
        self._pattr_virtual_fibre_channel_client_adapters = value

    @property
    def virtual_scsi_client_adapters(self):
        return self._pattr_virtual_scsi_client_adapters
    @virtual_scsi_client_adapters.setter
    def virtual_scsi_client_adapters(self, value):
        self._modified_attrs.add("virtual_scsi_client_adapters")
        self._pattr_virtual_scsi_client_adapters = value


class LogicalPartitionCapabilities(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dynamic_logical_partition_io_capable = None
        self._pattr_dynamic_logical_partition_memory_capable = None
        self._pattr_dynamic_logical_partition_processor_capable = None
        self._pattr_internal_and_external_intrusion_detection_capable = None
        self._pattr_resource_monitoring_control_operating_system_shutdown_capable = None
        super(LogicalPartitionCapabilities,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dynamic_logical_partition_io_capable(self):
        return self._pattr_dynamic_logical_partition_io_capable

    @property
    def dynamic_logical_partition_memory_capable(self):
        return self._pattr_dynamic_logical_partition_memory_capable

    @property
    def dynamic_logical_partition_processor_capable(self):
        return self._pattr_dynamic_logical_partition_processor_capable

    @property
    def internal_and_external_intrusion_detection_capable(self):
        return self._pattr_internal_and_external_intrusion_detection_capable
    @internal_and_external_intrusion_detection_capable.setter
    def internal_and_external_intrusion_detection_capable(self, value):
        self._modified_attrs.add("internal_and_external_intrusion_detection_capable")
        self._pattr_internal_and_external_intrusion_detection_capable = value

    @property
    def resource_monitoring_control_operating_system_shutdown_capable(self):
        return self._pattr_resource_monitoring_control_operating_system_shutdown_capable
    @resource_monitoring_control_operating_system_shutdown_capable.setter
    def resource_monitoring_control_operating_system_shutdown_capable(self, value):
        self._modified_attrs.add("resource_monitoring_control_operating_system_shutdown_capable")
        self._pattr_resource_monitoring_control_operating_system_shutdown_capable = value


class LogicalPartitionDedicatedProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_maximum_processors = None
        self._pattr_current_minimum_processors = None
        self._pattr_current_processors = None
        self._pattr_run_processors = None
        super(LogicalPartitionDedicatedProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_maximum_processors(self):
        return self._pattr_current_maximum_processors

    @property
    def current_minimum_processors(self):
        return self._pattr_current_minimum_processors

    @property
    def current_processors(self):
        return self._pattr_current_processors

    @property
    def run_processors(self):
        return self._pattr_run_processors


class LogicalPartitionProfileIOConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_high_speed_link_opticonnect_pool = None
        self._pattr_host_channel_adapters = None
        self._pattr_maximum_virtual_io_slots = None
        self._pattr_pool_i_ds = []
        self._pattr_profile_io_slots = None
        self._pattr_profile_virtual_io_adapters = None
        self._pattr_tagged_io = None
        self._pattr_virtual_opticonnect_pool = None
        super(LogicalPartitionProfileIOConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def high_speed_link_opticonnect_pool(self):
        return self._pattr_high_speed_link_opticonnect_pool
    @high_speed_link_opticonnect_pool.setter
    def high_speed_link_opticonnect_pool(self, value):
        self._modified_attrs.add("high_speed_link_opticonnect_pool")
        self._pattr_high_speed_link_opticonnect_pool = value

    @property
    def host_channel_adapters(self):
        return self._pattr_host_channel_adapters

    @property
    def maximum_virtual_io_slots(self):
        return self._pattr_maximum_virtual_io_slots
    @maximum_virtual_io_slots.setter
    def maximum_virtual_io_slots(self, value):
        self._modified_attrs.add("maximum_virtual_io_slots")
        self._pattr_maximum_virtual_io_slots = value

    @property
    def pool_i_ds(self):
        return self._pattr_pool_i_ds
    @pool_i_ds.setter
    def pool_i_ds(self, value):
        self._modified_attrs.add("pool_i_ds")
        self._pattr_pool_i_ds = value

    @property
    def profile_io_slots(self):
        return self._pattr_profile_io_slots
    @profile_io_slots.setter
    def profile_io_slots(self, value):
        self._modified_attrs.add("profile_io_slots")
        self._pattr_profile_io_slots = value

    @property
    def profile_virtual_io_adapters(self):
        return self._pattr_profile_virtual_io_adapters
    @profile_virtual_io_adapters.setter
    def profile_virtual_io_adapters(self, value):
        self._modified_attrs.add("profile_virtual_io_adapters")
        self._pattr_profile_virtual_io_adapters = value

    @property
    def tagged_io(self):
        return self._pattr_tagged_io
    @tagged_io.setter
    def tagged_io(self, value):
        self._modified_attrs.add("tagged_io")
        self._pattr_tagged_io = value

    @property
    def virtual_opticonnect_pool(self):
        return self._pattr_virtual_opticonnect_pool
    @virtual_opticonnect_pool.setter
    def virtual_opticonnect_pool(self, value):
        self._modified_attrs.add("virtual_opticonnect_pool")
        self._pattr_virtual_opticonnect_pool = value


class LogicalPartitionIOConfiguration(LogicalPartitionProfileIOConfiguration):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_maximum_virtual_io_slots = None
        super(LogicalPartitionIOConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_maximum_virtual_io_slots(self):
        return self._pattr_current_maximum_virtual_io_slots


class LogicalPartitionProfileMemoryConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_active_memory_expansion_enabled = None
        self._pattr_active_memory_sharing_enabled = None
        self._pattr_barrier_synchronization_register_array_count = None
        self._pattr_desired_entitled_memory = None
        self._pattr_desired_huge_page_count = None
        self._pattr_desired_memory = None
        self._pattr_expansion_factor = None
        self._pattr_hardware_page_table_ratio = None
        self._pattr_manual_entitled_mode_enabled = None
        self._pattr_maximum_huge_page_count = None
        self._pattr_maximum_memory = None
        self._pattr_memory_weight = None
        self._pattr_minimum_huge_page_count = None
        self._pattr_minimum_memory = None
        self._pattr_primary_paging_service_partition = None
        self._pattr_secondary_paging_service_partition = None
        super(LogicalPartitionProfileMemoryConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def active_memory_expansion_enabled(self):
        return self._pattr_active_memory_expansion_enabled
    @active_memory_expansion_enabled.setter
    def active_memory_expansion_enabled(self, value):
        self._modified_attrs.add("active_memory_expansion_enabled")
        self._pattr_active_memory_expansion_enabled = value

    @property
    def active_memory_sharing_enabled(self):
        return self._pattr_active_memory_sharing_enabled
    @active_memory_sharing_enabled.setter
    def active_memory_sharing_enabled(self, value):
        self._modified_attrs.add("active_memory_sharing_enabled")
        self._pattr_active_memory_sharing_enabled = value

    @property
    def barrier_synchronization_register_array_count(self):
        return self._pattr_barrier_synchronization_register_array_count
    @barrier_synchronization_register_array_count.setter
    def barrier_synchronization_register_array_count(self, value):
        self._modified_attrs.add("barrier_synchronization_register_array_count")
        self._pattr_barrier_synchronization_register_array_count = value

    @property
    def desired_entitled_memory(self):
        return self._pattr_desired_entitled_memory
    @desired_entitled_memory.setter
    def desired_entitled_memory(self, value):
        self._modified_attrs.add("desired_entitled_memory")
        self._pattr_desired_entitled_memory = value

    @property
    def desired_huge_page_count(self):
        return self._pattr_desired_huge_page_count
    @desired_huge_page_count.setter
    def desired_huge_page_count(self, value):
        self._modified_attrs.add("desired_huge_page_count")
        self._pattr_desired_huge_page_count = value

    @property
    def desired_memory(self):
        return self._pattr_desired_memory
    @desired_memory.setter
    def desired_memory(self, value):
        self._modified_attrs.add("desired_memory")
        self._pattr_desired_memory = value

    @property
    def expansion_factor(self):
        return self._pattr_expansion_factor
    @expansion_factor.setter
    def expansion_factor(self, value):
        self._modified_attrs.add("expansion_factor")
        self._pattr_expansion_factor = value

    @property
    def hardware_page_table_ratio(self):
        return self._pattr_hardware_page_table_ratio
    @hardware_page_table_ratio.setter
    def hardware_page_table_ratio(self, value):
        self._modified_attrs.add("hardware_page_table_ratio")
        self._pattr_hardware_page_table_ratio = value

    @property
    def manual_entitled_mode_enabled(self):
        return self._pattr_manual_entitled_mode_enabled

    @property
    def maximum_huge_page_count(self):
        return self._pattr_maximum_huge_page_count
    @maximum_huge_page_count.setter
    def maximum_huge_page_count(self, value):
        self._modified_attrs.add("maximum_huge_page_count")
        self._pattr_maximum_huge_page_count = value

    @property
    def maximum_memory(self):
        return self._pattr_maximum_memory
    @maximum_memory.setter
    def maximum_memory(self, value):
        self._modified_attrs.add("maximum_memory")
        self._pattr_maximum_memory = value

    @property
    def memory_weight(self):
        return self._pattr_memory_weight
    @memory_weight.setter
    def memory_weight(self, value):
        self._modified_attrs.add("memory_weight")
        self._pattr_memory_weight = value

    @property
    def minimum_huge_page_count(self):
        return self._pattr_minimum_huge_page_count
    @minimum_huge_page_count.setter
    def minimum_huge_page_count(self, value):
        self._modified_attrs.add("minimum_huge_page_count")
        self._pattr_minimum_huge_page_count = value

    @property
    def minimum_memory(self):
        return self._pattr_minimum_memory
    @minimum_memory.setter
    def minimum_memory(self, value):
        self._modified_attrs.add("minimum_memory")
        self._pattr_minimum_memory = value

    @property
    def primary_paging_service_partition(self):
        return self._pattr_primary_paging_service_partition
    @primary_paging_service_partition.setter
    def primary_paging_service_partition(self, value):
        self._modified_attrs.add("primary_paging_service_partition")
        self._pattr_primary_paging_service_partition = value

    @property
    def secondary_paging_service_partition(self):
        return self._pattr_secondary_paging_service_partition
    @secondary_paging_service_partition.setter
    def secondary_paging_service_partition(self, value):
        self._modified_attrs.add("secondary_paging_service_partition")
        self._pattr_secondary_paging_service_partition = value


class LogicalPartitionMemoryConfiguration(LogicalPartitionProfileMemoryConfiguration):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_auto_entitled_memory_enabled = None
        self._pattr_current_barrier_synchronization_register_arrays = None
        self._pattr_current_entitled_memory = None
        self._pattr_current_expansion_factor = None
        self._pattr_current_hardware_page_table_ratio = None
        self._pattr_current_huge_page_count = None
        self._pattr_current_maximum_huge_page_count = None
        self._pattr_current_maximum_memory = None
        self._pattr_current_memory = None
        self._pattr_current_memory_weight = None
        self._pattr_current_minimum_huge_page_count = None
        self._pattr_current_minimum_memory = None
        self._pattr_current_paging_service_partition = None
        self._pattr_memory_encryption_hardware_access_enabled = None
        self._pattr_memory_expansion_enabled = None
        self._pattr_memory_expansion_hardware_access_enabled = None
        self._pattr_memory_releaseable = None
        self._pattr_memory_to_release = None
        self._pattr_redundant_error_path_reporting_enabled = None
        self._pattr_required_minimum_for_maximum = None
        self._pattr_runtime_entitled_memory = None
        self._pattr_runtime_expansion_factor = None
        self._pattr_runtime_huge_page_count = None
        self._pattr_runtime_memory = None
        self._pattr_runtime_memory_weight = None
        self._pattr_runtime_minimum_memory = None
        self._pattr_shared_memory_enabled = None
        super(LogicalPartitionMemoryConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def auto_entitled_memory_enabled(self):
        return self._pattr_auto_entitled_memory_enabled
    @auto_entitled_memory_enabled.setter
    def auto_entitled_memory_enabled(self, value):
        self._modified_attrs.add("auto_entitled_memory_enabled")
        self._pattr_auto_entitled_memory_enabled = value

    @property
    def current_barrier_synchronization_register_arrays(self):
        return self._pattr_current_barrier_synchronization_register_arrays

    @property
    def current_entitled_memory(self):
        return self._pattr_current_entitled_memory

    @property
    def current_expansion_factor(self):
        return self._pattr_current_expansion_factor

    @property
    def current_hardware_page_table_ratio(self):
        return self._pattr_current_hardware_page_table_ratio

    @property
    def current_huge_page_count(self):
        return self._pattr_current_huge_page_count

    @property
    def current_maximum_huge_page_count(self):
        return self._pattr_current_maximum_huge_page_count

    @property
    def current_maximum_memory(self):
        return self._pattr_current_maximum_memory

    @property
    def current_memory(self):
        return self._pattr_current_memory

    @property
    def current_memory_weight(self):
        return self._pattr_current_memory_weight

    @property
    def current_minimum_huge_page_count(self):
        return self._pattr_current_minimum_huge_page_count

    @property
    def current_minimum_memory(self):
        return self._pattr_current_minimum_memory

    @property
    def current_paging_service_partition(self):
        return self._pattr_current_paging_service_partition

    @property
    def memory_encryption_hardware_access_enabled(self):
        return self._pattr_memory_encryption_hardware_access_enabled

    @property
    def memory_expansion_enabled(self):
        return self._pattr_memory_expansion_enabled

    @property
    def memory_expansion_hardware_access_enabled(self):
        return self._pattr_memory_expansion_hardware_access_enabled

    @property
    def memory_releaseable(self):
        return self._pattr_memory_releaseable

    @property
    def memory_to_release(self):
        return self._pattr_memory_to_release
    @memory_to_release.setter
    def memory_to_release(self, value):
        self._modified_attrs.add("memory_to_release")
        self._pattr_memory_to_release = value

    @property
    def redundant_error_path_reporting_enabled(self):
        return self._pattr_redundant_error_path_reporting_enabled

    @property
    def required_minimum_for_maximum(self):
        return self._pattr_required_minimum_for_maximum

    @property
    def runtime_entitled_memory(self):
        return self._pattr_runtime_entitled_memory

    @property
    def runtime_expansion_factor(self):
        return self._pattr_runtime_expansion_factor

    @property
    def runtime_huge_page_count(self):
        return self._pattr_runtime_huge_page_count

    @property
    def runtime_memory(self):
        return self._pattr_runtime_memory

    @property
    def runtime_memory_weight(self):
        return self._pattr_runtime_memory_weight

    @property
    def runtime_minimum_memory(self):
        return self._pattr_runtime_minimum_memory

    @property
    def shared_memory_enabled(self):
        return self._pattr_shared_memory_enabled
    @shared_memory_enabled.setter
    def shared_memory_enabled(self, value):
        self._modified_attrs.add("shared_memory_enabled")
        self._pattr_shared_memory_enabled = value


class LogicalPartitionProfileProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dedicated_processor_configuration = None
        self._pattr_has_dedicated_processors = None
        self._pattr_shared_processor_configuration = None
        self._pattr_sharing_mode = None
        super(LogicalPartitionProfileProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dedicated_processor_configuration(self):
        return self._pattr_dedicated_processor_configuration
    @dedicated_processor_configuration.setter
    def dedicated_processor_configuration(self, value):
        self._modified_attrs.add("dedicated_processor_configuration")
        self._pattr_dedicated_processor_configuration = value

    @property
    def has_dedicated_processors(self):
        return self._pattr_has_dedicated_processors
    @has_dedicated_processors.setter
    def has_dedicated_processors(self, value):
        self._modified_attrs.add("has_dedicated_processors")
        self._pattr_has_dedicated_processors = value

    @property
    def shared_processor_configuration(self):
        return self._pattr_shared_processor_configuration
    @shared_processor_configuration.setter
    def shared_processor_configuration(self, value):
        self._modified_attrs.add("shared_processor_configuration")
        self._pattr_shared_processor_configuration = value

    @property
    def sharing_mode(self):
        return self._pattr_sharing_mode
    @sharing_mode.setter
    def sharing_mode(self, value):
        self._modified_attrs.add("sharing_mode")
        self._pattr_sharing_mode = value


class LogicalPartitionProcessorConfiguration(LogicalPartitionProfileProcessorConfiguration):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_dedicated_processor_configuration = None
        self._pattr_current_has_dedicated_processors = None
        self._pattr_current_shared_processor_configuration = None
        self._pattr_current_sharing_mode = None
        self._pattr_runtime_has_dedicated_processors = None
        self._pattr_runtime_sharing_mode = None
        super(LogicalPartitionProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def current_dedicated_processor_configuration(self):
        return self._pattr_current_dedicated_processor_configuration

    @property
    def current_has_dedicated_processors(self):
        return self._pattr_current_has_dedicated_processors

    @property
    def current_shared_processor_configuration(self):
        return self._pattr_current_shared_processor_configuration

    @property
    def current_sharing_mode(self):
        return self._pattr_current_sharing_mode

    @property
    def runtime_has_dedicated_processors(self):
        return self._pattr_runtime_has_dedicated_processors

    @property
    def runtime_sharing_mode(self):
        return self._pattr_runtime_sharing_mode


class LogicalPartitionProfile(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_affinity_group_id = None
        self._pattr_assign_all_resources = None
        self._pattr_associated_partition = None
        self._pattr_auto_start = None
        self._pattr_boot_mode = None
        self._pattr_connection_monitoring_enabled = None
        self._pattr_desired_processor_compatibility_mode = None
        self._pattr_electronic_error_reporting_enabled = None
        self._pattr_host_ethernet_adapter_logical_ports = None
        self._pattr_io_configuration_instance = None
        self._pattr_power_control_partitions = None
        self._pattr_processor_attributes = None
        self._pattr_profile_memory = None
        self._pattr_profile_name = None
        self._pattr_profile_sriov_ethernet_logical_ports = None
        self._pattr_profile_type = None
        self._pattr_redundant_error_path_reporting_enabled = None
        self._pattr_setting_id = None
        self._pattr_switch_network_interface_device_id = []

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(LogicalPartitionProfile,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def affinity_group_id(self):
        return self._pattr_affinity_group_id
    @affinity_group_id.setter
    def affinity_group_id(self, value):
        self._modified_attrs.add("affinity_group_id")
        self._pattr_affinity_group_id = value

    @property
    def assign_all_resources(self):
        return self._pattr_assign_all_resources
    @assign_all_resources.setter
    def assign_all_resources(self, value):
        self._modified_attrs.add("assign_all_resources")
        self._pattr_assign_all_resources = value

    @property
    def associated_partition(self):
        return self._pattr_associated_partition

    @property
    def auto_start(self):
        return self._pattr_auto_start
    @auto_start.setter
    def auto_start(self, value):
        self._modified_attrs.add("auto_start")
        self._pattr_auto_start = value

    @property
    def boot_mode(self):
        return self._pattr_boot_mode
    @boot_mode.setter
    def boot_mode(self, value):
        self._modified_attrs.add("boot_mode")
        self._pattr_boot_mode = value

    @property
    def connection_monitoring_enabled(self):
        return self._pattr_connection_monitoring_enabled
    @connection_monitoring_enabled.setter
    def connection_monitoring_enabled(self, value):
        self._modified_attrs.add("connection_monitoring_enabled")
        self._pattr_connection_monitoring_enabled = value

    @property
    def desired_processor_compatibility_mode(self):
        return self._pattr_desired_processor_compatibility_mode
    @desired_processor_compatibility_mode.setter
    def desired_processor_compatibility_mode(self, value):
        self._modified_attrs.add("desired_processor_compatibility_mode")
        self._pattr_desired_processor_compatibility_mode = value

    @property
    def electronic_error_reporting_enabled(self):
        return self._pattr_electronic_error_reporting_enabled
    @electronic_error_reporting_enabled.setter
    def electronic_error_reporting_enabled(self, value):
        self._modified_attrs.add("electronic_error_reporting_enabled")
        self._pattr_electronic_error_reporting_enabled = value

    @property
    def host_ethernet_adapter_logical_ports(self):
        return self._pattr_host_ethernet_adapter_logical_ports
    @host_ethernet_adapter_logical_ports.setter
    def host_ethernet_adapter_logical_ports(self, value):
        self._modified_attrs.add("host_ethernet_adapter_logical_ports")
        self._pattr_host_ethernet_adapter_logical_ports = value

    @property
    def io_configuration_instance(self):
        return self._pattr_io_configuration_instance
    @io_configuration_instance.setter
    def io_configuration_instance(self, value):
        self._modified_attrs.add("io_configuration_instance")
        self._pattr_io_configuration_instance = value

    @property
    def power_control_partitions(self):
        return self._pattr_power_control_partitions
    @power_control_partitions.setter
    def power_control_partitions(self, value):
        self._modified_attrs.add("power_control_partitions")
        self._pattr_power_control_partitions = value

    @property
    def processor_attributes(self):
        return self._pattr_processor_attributes
    @processor_attributes.setter
    def processor_attributes(self, value):
        self._modified_attrs.add("processor_attributes")
        self._pattr_processor_attributes = value

    @property
    def profile_memory(self):
        return self._pattr_profile_memory
    @profile_memory.setter
    def profile_memory(self, value):
        self._modified_attrs.add("profile_memory")
        self._pattr_profile_memory = value

    @property
    def profile_name(self):
        return self._pattr_profile_name
    @profile_name.setter
    def profile_name(self, value):
        self._modified_attrs.add("profile_name")
        self._pattr_profile_name = value

    @property
    def profile_sriov_ethernet_logical_ports(self):
        return self._pattr_profile_sriov_ethernet_logical_ports
    @profile_sriov_ethernet_logical_ports.setter
    def profile_sriov_ethernet_logical_ports(self, value):
        self._modified_attrs.add("profile_sriov_ethernet_logical_ports")
        self._pattr_profile_sriov_ethernet_logical_ports = value

    @property
    def profile_type(self):
        return self._pattr_profile_type

    @property
    def redundant_error_path_reporting_enabled(self):
        return self._pattr_redundant_error_path_reporting_enabled
    @redundant_error_path_reporting_enabled.setter
    def redundant_error_path_reporting_enabled(self, value):
        self._modified_attrs.add("redundant_error_path_reporting_enabled")
        self._pattr_redundant_error_path_reporting_enabled = value

    @property
    def setting_id(self):
        return self._pattr_setting_id

    @property
    def switch_network_interface_device_id(self):
        return self._pattr_switch_network_interface_device_id
    @switch_network_interface_device_id.setter
    def switch_network_interface_device_id(self, value):
        self._modified_attrs.add("switch_network_interface_device_id")
        self._pattr_switch_network_interface_device_id = value


class LogicalPartitionProfileDedicatedProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_desired_processors = None
        self._pattr_maximum_processors = None
        self._pattr_minimum_processors = None
        super(LogicalPartitionProfileDedicatedProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def desired_processors(self):
        return self._pattr_desired_processors
    @desired_processors.setter
    def desired_processors(self, value):
        self._modified_attrs.add("desired_processors")
        self._pattr_desired_processors = value

    @property
    def maximum_processors(self):
        return self._pattr_maximum_processors
    @maximum_processors.setter
    def maximum_processors(self, value):
        self._modified_attrs.add("maximum_processors")
        self._pattr_maximum_processors = value

    @property
    def minimum_processors(self):
        return self._pattr_minimum_processors
    @minimum_processors.setter
    def minimum_processors(self, value):
        self._modified_attrs.add("minimum_processors")
        self._pattr_minimum_processors = value


class LogicalPartitionProfileSharedProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_desired_processing_units = None
        self._pattr_desired_virtual_processors = None
        self._pattr_maximum_processing_units = None
        self._pattr_maximum_virtual_processors = None
        self._pattr_minimum_processing_units = None
        self._pattr_minimum_virtual_processors = None
        self._pattr_shared_processor_pool_id = None
        self._pattr_uncapped_weight = None
        super(LogicalPartitionProfileSharedProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def desired_processing_units(self):
        return self._pattr_desired_processing_units
    @desired_processing_units.setter
    def desired_processing_units(self, value):
        self._modified_attrs.add("desired_processing_units")
        self._pattr_desired_processing_units = value

    @property
    def desired_virtual_processors(self):
        return self._pattr_desired_virtual_processors
    @desired_virtual_processors.setter
    def desired_virtual_processors(self, value):
        self._modified_attrs.add("desired_virtual_processors")
        self._pattr_desired_virtual_processors = value

    @property
    def maximum_processing_units(self):
        return self._pattr_maximum_processing_units
    @maximum_processing_units.setter
    def maximum_processing_units(self, value):
        self._modified_attrs.add("maximum_processing_units")
        self._pattr_maximum_processing_units = value

    @property
    def maximum_virtual_processors(self):
        return self._pattr_maximum_virtual_processors
    @maximum_virtual_processors.setter
    def maximum_virtual_processors(self, value):
        self._modified_attrs.add("maximum_virtual_processors")
        self._pattr_maximum_virtual_processors = value

    @property
    def minimum_processing_units(self):
        return self._pattr_minimum_processing_units
    @minimum_processing_units.setter
    def minimum_processing_units(self, value):
        self._modified_attrs.add("minimum_processing_units")
        self._pattr_minimum_processing_units = value

    @property
    def minimum_virtual_processors(self):
        return self._pattr_minimum_virtual_processors
    @minimum_virtual_processors.setter
    def minimum_virtual_processors(self, value):
        self._modified_attrs.add("minimum_virtual_processors")
        self._pattr_minimum_virtual_processors = value

    @property
    def shared_processor_pool_id(self):
        return self._pattr_shared_processor_pool_id
    @shared_processor_pool_id.setter
    def shared_processor_pool_id(self, value):
        self._modified_attrs.add("shared_processor_pool_id")
        self._pattr_shared_processor_pool_id = value

    @property
    def uncapped_weight(self):
        return self._pattr_uncapped_weight
    @uncapped_weight.setter
    def uncapped_weight(self, value):
        self._modified_attrs.add("uncapped_weight")
        self._pattr_uncapped_weight = value


class LogicalPartitionProfile_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(LogicalPartitionProfile_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class LogicalPartitionSharedProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allocated_virtual_processors = None
        self._pattr_current_maximum_processing_units = None
        self._pattr_current_maximum_virtual_processors = None
        self._pattr_current_minimum_processing_units = None
        self._pattr_current_minimum_virtual_processors = None
        self._pattr_current_processing_units = None
        self._pattr_current_shared_processor_pool_id = None
        self._pattr_current_uncapped_weight = None
        self._pattr_runtime_processing_units = None
        self._pattr_runtime_uncapped_weight = None
        super(LogicalPartitionSharedProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allocated_virtual_processors(self):
        return self._pattr_allocated_virtual_processors

    @property
    def current_maximum_processing_units(self):
        return self._pattr_current_maximum_processing_units

    @property
    def current_maximum_virtual_processors(self):
        return self._pattr_current_maximum_virtual_processors

    @property
    def current_minimum_processing_units(self):
        return self._pattr_current_minimum_processing_units

    @property
    def current_minimum_virtual_processors(self):
        return self._pattr_current_minimum_virtual_processors

    @property
    def current_processing_units(self):
        return self._pattr_current_processing_units

    @property
    def current_shared_processor_pool_id(self):
        return self._pattr_current_shared_processor_pool_id

    @property
    def current_uncapped_weight(self):
        return self._pattr_current_uncapped_weight

    @property
    def runtime_processing_units(self):
        return self._pattr_runtime_processing_units

    @property
    def runtime_uncapped_weight(self):
        return self._pattr_runtime_uncapped_weight


class LogicalPartition_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(LogicalPartition_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VirtualSCSIStorage(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(VirtualSCSIStorage,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class LogicalUnit(VirtualSCSIStorage):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_cloned_from = None
        self._pattr_in_use = None
        self._pattr_logical_unit_type = None
        self._pattr_thin_device = None
        self._pattr_unique_device_id = None
        self._pattr_unit_capacity = None
        self._pattr_unit_name = None
        super(LogicalUnit,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def cloned_from(self):
        return self._pattr_cloned_from
    @cloned_from.setter
    def cloned_from(self, value):
        self._modified_attrs.add("cloned_from")
        self._pattr_cloned_from = value

    @property
    def in_use(self):
        return self._pattr_in_use

    @property
    def logical_unit_type(self):
        return self._pattr_logical_unit_type
    @logical_unit_type.setter
    def logical_unit_type(self, value):
        self._modified_attrs.add("logical_unit_type")
        self._pattr_logical_unit_type = value

    @property
    def thin_device(self):
        return self._pattr_thin_device
    @thin_device.setter
    def thin_device(self, value):
        self._modified_attrs.add("thin_device")
        self._pattr_thin_device = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def unit_capacity(self):
        return self._pattr_unit_capacity
    @unit_capacity.setter
    def unit_capacity(self, value):
        self._modified_attrs.add("unit_capacity")
        self._pattr_unit_capacity = value

    @property
    def unit_name(self):
        return self._pattr_unit_name
    @unit_name.setter
    def unit_name(self, value):
        self._modified_attrs.add("unit_name")
        self._pattr_unit_name = value


class LogicalUnit_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_logical_unit = []
        super(LogicalUnit_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def logical_unit(self):
        return self._pattr_logical_unit
    @logical_unit.setter
    def logical_unit(self, value):
        self._modified_attrs.add("logical_unit")
        self._pattr_logical_unit = value


class VirtualTargetDevice(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_logical_unit_address = None
        self._pattr_parent_name = None
        self._pattr_target_name = None
        self._pattr_unique_device_id = None
        super(VirtualTargetDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def logical_unit_address(self):
        return self._pattr_logical_unit_address
    @logical_unit_address.setter
    def logical_unit_address(self, value):
        self._modified_attrs.add("logical_unit_address")
        self._pattr_logical_unit_address = value

    @property
    def parent_name(self):
        return self._pattr_parent_name
    @parent_name.setter
    def parent_name(self, value):
        self._modified_attrs.add("parent_name")
        self._pattr_parent_name = value

    @property
    def target_name(self):
        return self._pattr_target_name
    @target_name.setter
    def target_name(self, value):
        self._modified_attrs.add("target_name")
        self._pattr_target_name = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id


class LogicalVolumeVirtualTargetDevice(VirtualTargetDevice):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(LogicalVolumeVirtualTargetDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class MachineTypeModelSerialNumber(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_machine_type = None
        self._pattr_model = None
        self._pattr_serial_number = None
        super(MachineTypeModelSerialNumber,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def machine_type(self):
        return self._pattr_machine_type
    @machine_type.setter
    def machine_type(self, value):
        self._modified_attrs.add("machine_type")
        self._pattr_machine_type = value

    @property
    def model(self):
        return self._pattr_model
    @model.setter
    def model(self, value):
        self._modified_attrs.add("model")
        self._pattr_model = value

    @property
    def serial_number(self):
        return self._pattr_serial_number
    @serial_number.setter
    def serial_number(self, value):
        self._modified_attrs.add("serial_number")
        self._pattr_serial_number = value


class ManagedFrame(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_activated_service_pack_and_level = None
        self._pattr_cages = None
        self._pattr_engineering_change_number = None
        self._pattr_frame_capability = None
        self._pattr_frame_name = None
        self._pattr_frame_number = None
        self._pattr_frame_state = None
        self._pattr_frame_type = None
        self._pattr_is_power6_frame = None
        self._pattr_machine_type_model_and_serial_number = None
        self._pattr_slave_bulk_power_controller_exists = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(ManagedFrame,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def activated_service_pack_and_level(self):
        return self._pattr_activated_service_pack_and_level

    @property
    def cages(self):
        return self._pattr_cages

    @property
    def engineering_change_number(self):
        return self._pattr_engineering_change_number

    @property
    def frame_capability(self):
        return self._pattr_frame_capability

    @property
    def frame_name(self):
        return self._pattr_frame_name
    @frame_name.setter
    def frame_name(self, value):
        self._modified_attrs.add("frame_name")
        self._pattr_frame_name = value

    @property
    def frame_number(self):
        return self._pattr_frame_number
    @frame_number.setter
    def frame_number(self, value):
        self._modified_attrs.add("frame_number")
        self._pattr_frame_number = value

    @property
    def frame_state(self):
        return self._pattr_frame_state

    @property
    def frame_type(self):
        return self._pattr_frame_type

    @property
    def is_power6_frame(self):
        return self._pattr_is_power6_frame

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number

    @property
    def slave_bulk_power_controller_exists(self):
        return self._pattr_slave_bulk_power_controller_exists


class ManagedFrame_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(ManagedFrame_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class ManagedSystem(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_activated_level = None
        self._pattr_associated_ipl_configuration = None
        self._pattr_associated_logical_partitions = None
        self._pattr_associated_power_enterprise_pool = None
        self._pattr_associated_reserved_storage_device_pool = None
        self._pattr_associated_system_capabilities = None
        self._pattr_associated_system_io_configuration = None
        self._pattr_associated_system_memory_configuration = None
        self._pattr_associated_system_processor_configuration = None
        self._pattr_associated_system_security = None
        self._pattr_associated_system_virtual_storage = None
        self._pattr_associated_virtual_environment_configuration = None
        self._pattr_associated_virtual_io_servers = None
        self._pattr_current_maximum_partitions_per_host_channel_adapter = None
        self._pattr_detailed_state = None
        self._pattr_machine_type_model_and_serial_number = None
        self._pattr_manufacturing_default_configuration_enabled = None
        self._pattr_maximum_partitions = None
        self._pattr_maximum_partitions_per_host_channel_adapter = None
        self._pattr_maximum_power_control_partitions = None
        self._pattr_maximum_remote_restart_partitions = None
        self._pattr_maximum_shared_processor_capable_partition_id = None
        self._pattr_maximum_suspendable_partitions = None
        self._pattr_pending_maximum_partitions_per_host_channel_adapter = None
        self._pattr_physical_system_attention_led_state = None
        self._pattr_primary_ip_address = None
        self._pattr_reference_code = None
        self._pattr_secondary_ip_address = None
        self._pattr_service_partition = None
        self._pattr_service_processor_failover_enabled = None
        self._pattr_service_processor_failover_reason = None
        self._pattr_service_processor_failover_state = None
        self._pattr_service_processor_version = None
        self._pattr_state = None
        self._pattr_system_migration_information = None
        self._pattr_system_name = None
        self._pattr_system_placement = None
        self._pattr_system_time = None
        self._pattr_virtual_system_attention_led_state = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(ManagedSystem,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def activated_level(self):
        return self._pattr_activated_level

    @property
    def associated_ipl_configuration(self):
        return self._pattr_associated_ipl_configuration
    @associated_ipl_configuration.setter
    def associated_ipl_configuration(self, value):
        self._modified_attrs.add("associated_ipl_configuration")
        self._pattr_associated_ipl_configuration = value

    @property
    def associated_logical_partitions(self):
        return self._pattr_associated_logical_partitions
    @associated_logical_partitions.setter
    def associated_logical_partitions(self, value):
        self._modified_attrs.add("associated_logical_partitions")
        self._pattr_associated_logical_partitions = value

    @property
    def associated_power_enterprise_pool(self):
        return self._pattr_associated_power_enterprise_pool
    @associated_power_enterprise_pool.setter
    def associated_power_enterprise_pool(self, value):
        self._modified_attrs.add("associated_power_enterprise_pool")
        self._pattr_associated_power_enterprise_pool = value

    @property
    def associated_reserved_storage_device_pool(self):
        return self._pattr_associated_reserved_storage_device_pool
    @associated_reserved_storage_device_pool.setter
    def associated_reserved_storage_device_pool(self, value):
        self._modified_attrs.add("associated_reserved_storage_device_pool")
        self._pattr_associated_reserved_storage_device_pool = value

    @property
    def associated_system_capabilities(self):
        return self._pattr_associated_system_capabilities
    @associated_system_capabilities.setter
    def associated_system_capabilities(self, value):
        self._modified_attrs.add("associated_system_capabilities")
        self._pattr_associated_system_capabilities = value

    @property
    def associated_system_io_configuration(self):
        return self._pattr_associated_system_io_configuration
    @associated_system_io_configuration.setter
    def associated_system_io_configuration(self, value):
        self._modified_attrs.add("associated_system_io_configuration")
        self._pattr_associated_system_io_configuration = value

    @property
    def associated_system_memory_configuration(self):
        return self._pattr_associated_system_memory_configuration
    @associated_system_memory_configuration.setter
    def associated_system_memory_configuration(self, value):
        self._modified_attrs.add("associated_system_memory_configuration")
        self._pattr_associated_system_memory_configuration = value

    @property
    def associated_system_processor_configuration(self):
        return self._pattr_associated_system_processor_configuration
    @associated_system_processor_configuration.setter
    def associated_system_processor_configuration(self, value):
        self._modified_attrs.add("associated_system_processor_configuration")
        self._pattr_associated_system_processor_configuration = value

    @property
    def associated_system_security(self):
        return self._pattr_associated_system_security
    @associated_system_security.setter
    def associated_system_security(self, value):
        self._modified_attrs.add("associated_system_security")
        self._pattr_associated_system_security = value

    @property
    def associated_system_virtual_storage(self):
        return self._pattr_associated_system_virtual_storage
    @associated_system_virtual_storage.setter
    def associated_system_virtual_storage(self, value):
        self._modified_attrs.add("associated_system_virtual_storage")
        self._pattr_associated_system_virtual_storage = value

    @property
    def associated_virtual_environment_configuration(self):
        return self._pattr_associated_virtual_environment_configuration
    @associated_virtual_environment_configuration.setter
    def associated_virtual_environment_configuration(self, value):
        self._modified_attrs.add("associated_virtual_environment_configuration")
        self._pattr_associated_virtual_environment_configuration = value

    @property
    def associated_virtual_io_servers(self):
        return self._pattr_associated_virtual_io_servers
    @associated_virtual_io_servers.setter
    def associated_virtual_io_servers(self, value):
        self._modified_attrs.add("associated_virtual_io_servers")
        self._pattr_associated_virtual_io_servers = value

    @property
    def current_maximum_partitions_per_host_channel_adapter(self):
        return self._pattr_current_maximum_partitions_per_host_channel_adapter

    @property
    def detailed_state(self):
        return self._pattr_detailed_state

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number

    @property
    def manufacturing_default_configuration_enabled(self):
        return self._pattr_manufacturing_default_configuration_enabled

    @property
    def maximum_partitions(self):
        return self._pattr_maximum_partitions
    @maximum_partitions.setter
    def maximum_partitions(self, value):
        self._modified_attrs.add("maximum_partitions")
        self._pattr_maximum_partitions = value

    @property
    def maximum_partitions_per_host_channel_adapter(self):
        return self._pattr_maximum_partitions_per_host_channel_adapter
    @maximum_partitions_per_host_channel_adapter.setter
    def maximum_partitions_per_host_channel_adapter(self, value):
        self._modified_attrs.add("maximum_partitions_per_host_channel_adapter")
        self._pattr_maximum_partitions_per_host_channel_adapter = value

    @property
    def maximum_power_control_partitions(self):
        return self._pattr_maximum_power_control_partitions
    @maximum_power_control_partitions.setter
    def maximum_power_control_partitions(self, value):
        self._modified_attrs.add("maximum_power_control_partitions")
        self._pattr_maximum_power_control_partitions = value

    @property
    def maximum_remote_restart_partitions(self):
        return self._pattr_maximum_remote_restart_partitions
    @maximum_remote_restart_partitions.setter
    def maximum_remote_restart_partitions(self, value):
        self._modified_attrs.add("maximum_remote_restart_partitions")
        self._pattr_maximum_remote_restart_partitions = value

    @property
    def maximum_shared_processor_capable_partition_id(self):
        return self._pattr_maximum_shared_processor_capable_partition_id
    @maximum_shared_processor_capable_partition_id.setter
    def maximum_shared_processor_capable_partition_id(self, value):
        self._modified_attrs.add("maximum_shared_processor_capable_partition_id")
        self._pattr_maximum_shared_processor_capable_partition_id = value

    @property
    def maximum_suspendable_partitions(self):
        return self._pattr_maximum_suspendable_partitions
    @maximum_suspendable_partitions.setter
    def maximum_suspendable_partitions(self, value):
        self._modified_attrs.add("maximum_suspendable_partitions")
        self._pattr_maximum_suspendable_partitions = value

    @property
    def pending_maximum_partitions_per_host_channel_adapter(self):
        return self._pattr_pending_maximum_partitions_per_host_channel_adapter
    @pending_maximum_partitions_per_host_channel_adapter.setter
    def pending_maximum_partitions_per_host_channel_adapter(self, value):
        self._modified_attrs.add("pending_maximum_partitions_per_host_channel_adapter")
        self._pattr_pending_maximum_partitions_per_host_channel_adapter = value

    @property
    def physical_system_attention_led_state(self):
        return self._pattr_physical_system_attention_led_state

    @property
    def primary_ip_address(self):
        return self._pattr_primary_ip_address
    @primary_ip_address.setter
    def primary_ip_address(self, value):
        self._modified_attrs.add("primary_ip_address")
        self._pattr_primary_ip_address = value

    @property
    def reference_code(self):
        return self._pattr_reference_code

    @property
    def secondary_ip_address(self):
        return self._pattr_secondary_ip_address
    @secondary_ip_address.setter
    def secondary_ip_address(self, value):
        self._modified_attrs.add("secondary_ip_address")
        self._pattr_secondary_ip_address = value

    @property
    def service_partition(self):
        return self._pattr_service_partition
    @service_partition.setter
    def service_partition(self, value):
        self._modified_attrs.add("service_partition")
        self._pattr_service_partition = value

    @property
    def service_processor_failover_enabled(self):
        return self._pattr_service_processor_failover_enabled
    @service_processor_failover_enabled.setter
    def service_processor_failover_enabled(self, value):
        self._modified_attrs.add("service_processor_failover_enabled")
        self._pattr_service_processor_failover_enabled = value

    @property
    def service_processor_failover_reason(self):
        return self._pattr_service_processor_failover_reason

    @property
    def service_processor_failover_state(self):
        return self._pattr_service_processor_failover_state

    @property
    def service_processor_version(self):
        return self._pattr_service_processor_version

    @property
    def state(self):
        return self._pattr_state

    @property
    def system_migration_information(self):
        return self._pattr_system_migration_information

    @property
    def system_name(self):
        return self._pattr_system_name
    @system_name.setter
    def system_name(self, value):
        self._modified_attrs.add("system_name")
        self._pattr_system_name = value

    @property
    def system_placement(self):
        return self._pattr_system_placement
    @system_placement.setter
    def system_placement(self, value):
        self._modified_attrs.add("system_placement")
        self._pattr_system_placement = value

    @property
    def system_time(self):
        return self._pattr_system_time

    @property
    def virtual_system_attention_led_state(self):
        return self._pattr_virtual_system_attention_led_state
    @virtual_system_attention_led_state.setter
    def virtual_system_attention_led_state(self, value):
        self._modified_attrs.add("virtual_system_attention_led_state")
        self._pattr_virtual_system_attention_led_state = value


class ManagedSystem_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(ManagedSystem_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class ManagementConsole(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_local_virtual_io_server_image_names = None
        self._pattr_machine_type_model_and_serial_number = None
        self._pattr_managed_frames = None
        self._pattr_managed_systems = None
        self._pattr_management_console_name = None
        self._pattr_network_interfaces = None
        self._pattr_power_enterprise_pools = None
        self._pattr_template_object_model_version = None
        self._pattr_user_object_model_version = None
        self._pattr_version_info = None
        self._pattr_web_object_model_version = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(ManagementConsole,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def local_virtual_io_server_image_names(self):
        return self._pattr_local_virtual_io_server_image_names

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number

    @property
    def managed_frames(self):
        return self._pattr_managed_frames
    @managed_frames.setter
    def managed_frames(self, value):
        self._modified_attrs.add("managed_frames")
        self._pattr_managed_frames = value

    @property
    def managed_systems(self):
        return self._pattr_managed_systems
    @managed_systems.setter
    def managed_systems(self, value):
        self._modified_attrs.add("managed_systems")
        self._pattr_managed_systems = value

    @property
    def management_console_name(self):
        return self._pattr_management_console_name
    @management_console_name.setter
    def management_console_name(self, value):
        self._modified_attrs.add("management_console_name")
        self._pattr_management_console_name = value

    @property
    def network_interfaces(self):
        return self._pattr_network_interfaces
    @network_interfaces.setter
    def network_interfaces(self, value):
        self._modified_attrs.add("network_interfaces")
        self._pattr_network_interfaces = value

    @property
    def power_enterprise_pools(self):
        return self._pattr_power_enterprise_pools
    @power_enterprise_pools.setter
    def power_enterprise_pools(self, value):
        self._modified_attrs.add("power_enterprise_pools")
        self._pattr_power_enterprise_pools = value

    @property
    def template_object_model_version(self):
        return self._pattr_template_object_model_version

    @property
    def user_object_model_version(self):
        return self._pattr_user_object_model_version

    @property
    def version_info(self):
        return self._pattr_version_info

    @property
    def web_object_model_version(self):
        return self._pattr_web_object_model_version


class ManagementConsoleNetworkInterface(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_interface_name = None
        self._pattr_network_address = None
        super(ManagementConsoleNetworkInterface,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def interface_name(self):
        return self._pattr_interface_name
    @interface_name.setter
    def interface_name(self, value):
        self._modified_attrs.add("interface_name")
        self._pattr_interface_name = value

    @property
    def network_address(self):
        return self._pattr_network_address
    @network_address.setter
    def network_address(self, value):
        self._modified_attrs.add("network_address")
        self._pattr_network_address = value


class ManagementConsoleNetworkInterface_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_management_console_network_interface = []
        super(ManagementConsoleNetworkInterface_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def management_console_network_interface(self):
        return self._pattr_management_console_network_interface
    @management_console_network_interface.setter
    def management_console_network_interface(self, value):
        self._modified_attrs.add("management_console_network_interface")
        self._pattr_management_console_network_interface = value


class Metadata(K2Resource):
    def __init__(self):

        self._pattr_atom = None
        super(Metadata,
              self).__init__()

    @property
    def atom(self):
        return self._pattr_atom


class NetworkBootDevice(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_boot_device = None
        self._pattr_is_physical_device = None
        self._pattr_location_code = None
        self._pattr_mac_address_value = None
        super(NetworkBootDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def boot_device(self):
        return self._pattr_boot_device

    @property
    def is_physical_device(self):
        return self._pattr_is_physical_device

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def mac_address_value(self):
        return self._pattr_mac_address_value


class NetworkBootDevice_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_network_boot_device = []
        super(NetworkBootDevice_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def network_boot_device(self):
        return self._pattr_network_boot_device
    @network_boot_device.setter
    def network_boot_device(self, value):
        self._modified_attrs.add("network_boot_device")
        self._pattr_network_boot_device = value


class NetworkBridge(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_control_channel_id = None
        self._pattr_failover_enabled = None
        self._pattr_load_balancing_enabled = None
        self._pattr_load_groups = None
        self._pattr_port_vlan_id = None
        self._pattr_shared_ethernet_adapters = None
        self._pattr_unique_device_id = None
        self._pattr_virtual_networks = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(NetworkBridge,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def control_channel_id(self):
        return self._pattr_control_channel_id
    @control_channel_id.setter
    def control_channel_id(self, value):
        self._modified_attrs.add("control_channel_id")
        self._pattr_control_channel_id = value

    @property
    def failover_enabled(self):
        return self._pattr_failover_enabled
    @failover_enabled.setter
    def failover_enabled(self, value):
        self._modified_attrs.add("failover_enabled")
        self._pattr_failover_enabled = value

    @property
    def load_balancing_enabled(self):
        return self._pattr_load_balancing_enabled
    @load_balancing_enabled.setter
    def load_balancing_enabled(self, value):
        self._modified_attrs.add("load_balancing_enabled")
        self._pattr_load_balancing_enabled = value

    @property
    def load_groups(self):
        return self._pattr_load_groups
    @load_groups.setter
    def load_groups(self, value):
        self._modified_attrs.add("load_groups")
        self._pattr_load_groups = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def shared_ethernet_adapters(self):
        return self._pattr_shared_ethernet_adapters
    @shared_ethernet_adapters.setter
    def shared_ethernet_adapters(self, value):
        self._modified_attrs.add("shared_ethernet_adapters")
        self._pattr_shared_ethernet_adapters = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def virtual_networks(self):
        return self._pattr_virtual_networks


class NetworkBridge_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(NetworkBridge_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class Node(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_host_name = None
        self._pattr_ip_address = None
        self._pattr_machine_type_model_and_serial_number = None
        self._pattr_partition_id = None
        self._pattr_partition_name = None
        self._pattr_virtual_io_server = None
        self._pattr_virtual_io_server_level = None
        super(Node,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def host_name(self):
        return self._pattr_host_name
    @host_name.setter
    def host_name(self, value):
        self._modified_attrs.add("host_name")
        self._pattr_host_name = value

    @property
    def ip_address(self):
        return self._pattr_ip_address
    @ip_address.setter
    def ip_address(self, value):
        self._modified_attrs.add("ip_address")
        self._pattr_ip_address = value

    @property
    def machine_type_model_and_serial_number(self):
        return self._pattr_machine_type_model_and_serial_number
    @machine_type_model_and_serial_number.setter
    def machine_type_model_and_serial_number(self, value):
        self._modified_attrs.add("machine_type_model_and_serial_number")
        self._pattr_machine_type_model_and_serial_number = value

    @property
    def partition_id(self):
        return self._pattr_partition_id
    @partition_id.setter
    def partition_id(self, value):
        self._modified_attrs.add("partition_id")
        self._pattr_partition_id = value

    @property
    def partition_name(self):
        return self._pattr_partition_name
    @partition_name.setter
    def partition_name(self, value):
        self._modified_attrs.add("partition_name")
        self._pattr_partition_name = value

    @property
    def virtual_io_server(self):
        return self._pattr_virtual_io_server
    @virtual_io_server.setter
    def virtual_io_server(self, value):
        self._modified_attrs.add("virtual_io_server")
        self._pattr_virtual_io_server = value

    @property
    def virtual_io_server_level(self):
        return self._pattr_virtual_io_server_level
    @virtual_io_server_level.setter
    def virtual_io_server_level(self, value):
        self._modified_attrs.add("virtual_io_server_level")
        self._pattr_virtual_io_server_level = value


class Node_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_node = []
        super(Node_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def node(self):
        return self._pattr_node
    @node.setter
    def node(self, value):
        self._modified_attrs.add("node")
        self._pattr_node = value


class PhysicalFibreChannelAdapter(IOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_physical_fibre_channel_ports = None
        super(PhysicalFibreChannelAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def physical_fibre_channel_ports(self):
        return self._pattr_physical_fibre_channel_ports
    @physical_fibre_channel_ports.setter
    def physical_fibre_channel_ports(self, value):
        self._modified_attrs.add("physical_fibre_channel_ports")
        self._pattr_physical_fibre_channel_ports = value


class PhysicalFibreChannelPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_available_ports = None
        self._pattr_location_code = None
        self._pattr_physical_volumes = None
        self._pattr_port_name = None
        self._pattr_total_ports = None
        self._pattr_unique_device_id = None
        self._pattr_wwpn = None
        super(PhysicalFibreChannelPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def available_ports(self):
        return self._pattr_available_ports

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def physical_volumes(self):
        return self._pattr_physical_volumes
    @physical_volumes.setter
    def physical_volumes(self, value):
        self._modified_attrs.add("physical_volumes")
        self._pattr_physical_volumes = value

    @property
    def port_name(self):
        return self._pattr_port_name
    @port_name.setter
    def port_name(self, value):
        self._modified_attrs.add("port_name")
        self._pattr_port_name = value

    @property
    def total_ports(self):
        return self._pattr_total_ports

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def wwpn(self):
        return self._pattr_wwpn
    @wwpn.setter
    def wwpn(self, value):
        self._modified_attrs.add("wwpn")
        self._pattr_wwpn = value


class PhysicalFibreChannelPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_physical_fibre_channel_port = []
        super(PhysicalFibreChannelPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def physical_fibre_channel_port(self):
        return self._pattr_physical_fibre_channel_port
    @physical_fibre_channel_port.setter
    def physical_fibre_channel_port(self, value):
        self._modified_attrs.add("physical_fibre_channel_port")
        self._pattr_physical_fibre_channel_port = value


class PhysicalVolume(VirtualSCSIStorage):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_available_for_usage = None
        self._pattr_available_physical_partitions = None
        self._pattr_description = None
        self._pattr_is_fibre_channel_backed = None
        self._pattr_location_code = None
        self._pattr_persistent_reserve_key_value = None
        self._pattr_reserve_policy = None
        self._pattr_reserve_policy_algorithm = None
        self._pattr_total_physical_partitions = None
        self._pattr_unique_device_id = None
        self._pattr_volume_capacity = None
        self._pattr_volume_name = None
        self._pattr_volume_state = None
        self._pattr_volume_unique_id = None
        super(PhysicalVolume,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def available_for_usage(self):
        return self._pattr_available_for_usage
    @available_for_usage.setter
    def available_for_usage(self, value):
        self._modified_attrs.add("available_for_usage")
        self._pattr_available_for_usage = value

    @property
    def available_physical_partitions(self):
        return self._pattr_available_physical_partitions

    @property
    def description(self):
        return self._pattr_description
    @description.setter
    def description(self, value):
        self._modified_attrs.add("description")
        self._pattr_description = value

    @property
    def is_fibre_channel_backed(self):
        return self._pattr_is_fibre_channel_backed

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def persistent_reserve_key_value(self):
        return self._pattr_persistent_reserve_key_value

    @property
    def reserve_policy(self):
        return self._pattr_reserve_policy
    @reserve_policy.setter
    def reserve_policy(self, value):
        self._modified_attrs.add("reserve_policy")
        self._pattr_reserve_policy = value

    @property
    def reserve_policy_algorithm(self):
        return self._pattr_reserve_policy_algorithm
    @reserve_policy_algorithm.setter
    def reserve_policy_algorithm(self, value):
        self._modified_attrs.add("reserve_policy_algorithm")
        self._pattr_reserve_policy_algorithm = value

    @property
    def total_physical_partitions(self):
        return self._pattr_total_physical_partitions

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def volume_capacity(self):
        return self._pattr_volume_capacity
    @volume_capacity.setter
    def volume_capacity(self, value):
        self._modified_attrs.add("volume_capacity")
        self._pattr_volume_capacity = value

    @property
    def volume_name(self):
        return self._pattr_volume_name
    @volume_name.setter
    def volume_name(self, value):
        self._modified_attrs.add("volume_name")
        self._pattr_volume_name = value

    @property
    def volume_state(self):
        return self._pattr_volume_state

    @property
    def volume_unique_id(self):
        return self._pattr_volume_unique_id


class PhysicalVolumeVirtualTargetDevice(VirtualTargetDevice):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(PhysicalVolumeVirtualTargetDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class PhysicalVolume_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_physical_volume = []
        super(PhysicalVolume_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def physical_volume(self):
        return self._pattr_physical_volume
    @physical_volume.setter
    def physical_volume(self, value):
        self._modified_attrs.add("physical_volume")
        self._pattr_physical_volume = value


class PowerEnterprisePool(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_available_mobile_co_d_memory = None
        self._pattr_available_mobile_co_d_proc_units = None
        self._pattr_compliance_remaining_hours = None
        self._pattr_compliance_state = None
        self._pattr_pool_id = None
        self._pattr_pool_name = None
        self._pattr_power_enterprise_pool_management_consoles = None
        self._pattr_power_enterprise_pool_master_management_console = None
        self._pattr_power_enterprise_pool_members = None
        self._pattr_sequence_number = None
        self._pattr_total_mobile_co_d_memory = None
        self._pattr_total_mobile_co_d_proc_units = None
        self._pattr_unreturned_mobile_co_d_memory = None
        self._pattr_unreturned_mobile_co_d_proc_units = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(PowerEnterprisePool,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def available_mobile_co_d_memory(self):
        return self._pattr_available_mobile_co_d_memory

    @property
    def available_mobile_co_d_proc_units(self):
        return self._pattr_available_mobile_co_d_proc_units

    @property
    def compliance_remaining_hours(self):
        return self._pattr_compliance_remaining_hours

    @property
    def compliance_state(self):
        return self._pattr_compliance_state

    @property
    def pool_id(self):
        return self._pattr_pool_id

    @property
    def pool_name(self):
        return self._pattr_pool_name
    @pool_name.setter
    def pool_name(self, value):
        self._modified_attrs.add("pool_name")
        self._pattr_pool_name = value

    @property
    def power_enterprise_pool_management_consoles(self):
        return self._pattr_power_enterprise_pool_management_consoles

    @property
    def power_enterprise_pool_master_management_console(self):
        return self._pattr_power_enterprise_pool_master_management_console
    @power_enterprise_pool_master_management_console.setter
    def power_enterprise_pool_master_management_console(self, value):
        self._modified_attrs.add("power_enterprise_pool_master_management_console")
        self._pattr_power_enterprise_pool_master_management_console = value

    @property
    def power_enterprise_pool_members(self):
        return self._pattr_power_enterprise_pool_members

    @property
    def sequence_number(self):
        return self._pattr_sequence_number

    @property
    def total_mobile_co_d_memory(self):
        return self._pattr_total_mobile_co_d_memory

    @property
    def total_mobile_co_d_proc_units(self):
        return self._pattr_total_mobile_co_d_proc_units

    @property
    def unreturned_mobile_co_d_memory(self):
        return self._pattr_unreturned_mobile_co_d_memory

    @property
    def unreturned_mobile_co_d_proc_units(self):
        return self._pattr_unreturned_mobile_co_d_proc_units


class PowerEnterprisePoolManagementConsole(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_is_backup_master_console = None
        self._pattr_is_master_console = None
        self._pattr_management_console_machine_type_model_serial_number = None
        self._pattr_management_console_name = None
        super(PowerEnterprisePoolManagementConsole,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def is_backup_master_console(self):
        return self._pattr_is_backup_master_console
    @is_backup_master_console.setter
    def is_backup_master_console(self, value):
        self._modified_attrs.add("is_backup_master_console")
        self._pattr_is_backup_master_console = value

    @property
    def is_master_console(self):
        return self._pattr_is_master_console
    @is_master_console.setter
    def is_master_console(self, value):
        self._modified_attrs.add("is_master_console")
        self._pattr_is_master_console = value

    @property
    def management_console_machine_type_model_serial_number(self):
        return self._pattr_management_console_machine_type_model_serial_number
    @management_console_machine_type_model_serial_number.setter
    def management_console_machine_type_model_serial_number(self, value):
        self._modified_attrs.add("management_console_machine_type_model_serial_number")
        self._pattr_management_console_machine_type_model_serial_number = value

    @property
    def management_console_name(self):
        return self._pattr_management_console_name
    @management_console_name.setter
    def management_console_name(self, value):
        self._modified_attrs.add("management_console_name")
        self._pattr_management_console_name = value


class PowerEnterprisePoolManagementConsole_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_power_enterprise_pool_management_console = []
        super(PowerEnterprisePoolManagementConsole_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def power_enterprise_pool_management_console(self):
        return self._pattr_power_enterprise_pool_management_console
    @power_enterprise_pool_management_console.setter
    def power_enterprise_pool_management_console(self, value):
        self._modified_attrs.add("power_enterprise_pool_management_console")
        self._pattr_power_enterprise_pool_management_console = value


class PowerEnterprisePoolMember(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_managed_system = None
        self._pattr_inactive_memory = None
        self._pattr_inactive_proc_units = None
        self._pattr_managed_system_installed_memory = None
        self._pattr_managed_system_installed_proc_units = None
        self._pattr_managed_system_machine_type_model_serial_number = None
        self._pattr_managed_system_name = None
        self._pattr_mem_compliance_remaining_hours = None
        self._pattr_mobile_co_d_memory = None
        self._pattr_mobile_co_d_proc_units = None
        self._pattr_proc_compliance_remaining_hours = None
        self._pattr_unreturned_mobile_co_d_memory = None
        self._pattr_unreturned_mobile_co_d_proc_units = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(PowerEnterprisePoolMember,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def associated_managed_system(self):
        return self._pattr_associated_managed_system

    @property
    def inactive_memory(self):
        return self._pattr_inactive_memory

    @property
    def inactive_proc_units(self):
        return self._pattr_inactive_proc_units

    @property
    def managed_system_installed_memory(self):
        return self._pattr_managed_system_installed_memory

    @property
    def managed_system_installed_proc_units(self):
        return self._pattr_managed_system_installed_proc_units

    @property
    def managed_system_machine_type_model_serial_number(self):
        return self._pattr_managed_system_machine_type_model_serial_number

    @property
    def managed_system_name(self):
        return self._pattr_managed_system_name

    @property
    def mem_compliance_remaining_hours(self):
        return self._pattr_mem_compliance_remaining_hours

    @property
    def mobile_co_d_memory(self):
        return self._pattr_mobile_co_d_memory
    @mobile_co_d_memory.setter
    def mobile_co_d_memory(self, value):
        self._modified_attrs.add("mobile_co_d_memory")
        self._pattr_mobile_co_d_memory = value

    @property
    def mobile_co_d_proc_units(self):
        return self._pattr_mobile_co_d_proc_units
    @mobile_co_d_proc_units.setter
    def mobile_co_d_proc_units(self, value):
        self._modified_attrs.add("mobile_co_d_proc_units")
        self._pattr_mobile_co_d_proc_units = value

    @property
    def proc_compliance_remaining_hours(self):
        return self._pattr_proc_compliance_remaining_hours

    @property
    def unreturned_mobile_co_d_memory(self):
        return self._pattr_unreturned_mobile_co_d_memory

    @property
    def unreturned_mobile_co_d_proc_units(self):
        return self._pattr_unreturned_mobile_co_d_proc_units


class PowerEnterprisePoolMember_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(PowerEnterprisePoolMember_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class PowerEnterprisePool_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(PowerEnterprisePool_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class ProfileVirtualIOAdapter(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_type = None
        self._pattr_is_required = None
        self._pattr_local_partition_id = None
        self._pattr_virtual_slot_number = None
        super(ProfileVirtualIOAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def adapter_type(self):
        return self._pattr_adapter_type
    @adapter_type.setter
    def adapter_type(self, value):
        self._modified_attrs.add("adapter_type")
        self._pattr_adapter_type = value

    @property
    def is_required(self):
        return self._pattr_is_required
    @is_required.setter
    def is_required(self, value):
        self._modified_attrs.add("is_required")
        self._pattr_is_required = value

    @property
    def local_partition_id(self):
        return self._pattr_local_partition_id
    @local_partition_id.setter
    def local_partition_id(self, value):
        self._modified_attrs.add("local_partition_id")
        self._pattr_local_partition_id = value

    @property
    def virtual_slot_number(self):
        return self._pattr_virtual_slot_number
    @virtual_slot_number.setter
    def virtual_slot_number(self, value):
        self._modified_attrs.add("virtual_slot_number")
        self._pattr_virtual_slot_number = value


class ProfileVirtualEthernetAdapter(ProfileVirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_operating_system_mac_addresses = None
        self._pattr_is_quality_of_service_priority_enabled = None
        self._pattr_is_tagged_vlan_supported = None
        self._pattr_ma_c_address_value = None
        self._pattr_port_vlan_id = None
        self._pattr_quality_of_service_priority = None
        self._pattr_tagged_vlan_ids = None
        self._pattr_virtual_switch_id = None
        self._pattr_virtual_switch_interface_manager_id = None
        self._pattr_virtual_switch_interface_type = None
        self._pattr_virtual_switch_interface_type_version = None
        self._pattr_virtual_switch_name = None
        super(ProfileVirtualEthernetAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allowed_operating_system_mac_addresses(self):
        return self._pattr_allowed_operating_system_mac_addresses
    @allowed_operating_system_mac_addresses.setter
    def allowed_operating_system_mac_addresses(self, value):
        self._modified_attrs.add("allowed_operating_system_mac_addresses")
        self._pattr_allowed_operating_system_mac_addresses = value

    @property
    def is_quality_of_service_priority_enabled(self):
        return self._pattr_is_quality_of_service_priority_enabled
    @is_quality_of_service_priority_enabled.setter
    def is_quality_of_service_priority_enabled(self, value):
        self._modified_attrs.add("is_quality_of_service_priority_enabled")
        self._pattr_is_quality_of_service_priority_enabled = value

    @property
    def is_tagged_vlan_supported(self):
        return self._pattr_is_tagged_vlan_supported
    @is_tagged_vlan_supported.setter
    def is_tagged_vlan_supported(self, value):
        self._modified_attrs.add("is_tagged_vlan_supported")
        self._pattr_is_tagged_vlan_supported = value

    @property
    def ma_c_address_value(self):
        return self._pattr_ma_c_address_value
    @ma_c_address_value.setter
    def ma_c_address_value(self, value):
        self._modified_attrs.add("ma_c_address_value")
        self._pattr_ma_c_address_value = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def quality_of_service_priority(self):
        return self._pattr_quality_of_service_priority
    @quality_of_service_priority.setter
    def quality_of_service_priority(self, value):
        self._modified_attrs.add("quality_of_service_priority")
        self._pattr_quality_of_service_priority = value

    @property
    def tagged_vlan_ids(self):
        return self._pattr_tagged_vlan_ids
    @tagged_vlan_ids.setter
    def tagged_vlan_ids(self, value):
        self._modified_attrs.add("tagged_vlan_ids")
        self._pattr_tagged_vlan_ids = value

    @property
    def virtual_switch_id(self):
        return self._pattr_virtual_switch_id

    @property
    def virtual_switch_interface_manager_id(self):
        return self._pattr_virtual_switch_interface_manager_id
    @virtual_switch_interface_manager_id.setter
    def virtual_switch_interface_manager_id(self, value):
        self._modified_attrs.add("virtual_switch_interface_manager_id")
        self._pattr_virtual_switch_interface_manager_id = value

    @property
    def virtual_switch_interface_type(self):
        return self._pattr_virtual_switch_interface_type
    @virtual_switch_interface_type.setter
    def virtual_switch_interface_type(self, value):
        self._modified_attrs.add("virtual_switch_interface_type")
        self._pattr_virtual_switch_interface_type = value

    @property
    def virtual_switch_interface_type_version(self):
        return self._pattr_virtual_switch_interface_type_version
    @virtual_switch_interface_type_version.setter
    def virtual_switch_interface_type_version(self, value):
        self._modified_attrs.add("virtual_switch_interface_type_version")
        self._pattr_virtual_switch_interface_type_version = value

    @property
    def virtual_switch_name(self):
        return self._pattr_virtual_switch_name
    @virtual_switch_name.setter
    def virtual_switch_name(self, value):
        self._modified_attrs.add("virtual_switch_name")
        self._pattr_virtual_switch_name = value


class ProfileClientNetworkAdapter(ProfileVirtualEthernetAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(ProfileClientNetworkAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class ProfileIOSlot(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_io_slot = None
        self._pattr_is_required = None
        super(ProfileIOSlot,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def associated_io_slot(self):
        return self._pattr_associated_io_slot
    @associated_io_slot.setter
    def associated_io_slot(self, value):
        self._modified_attrs.add("associated_io_slot")
        self._pattr_associated_io_slot = value

    @property
    def is_required(self):
        return self._pattr_is_required
    @is_required.setter
    def is_required(self, value):
        self._modified_attrs.add("is_required")
        self._pattr_is_required = value


class ProfileIOSlot_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_profile_io_slot = []
        super(ProfileIOSlot_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def profile_io_slot(self):
        return self._pattr_profile_io_slot
    @profile_io_slot.setter
    def profile_io_slot(self, value):
        self._modified_attrs.add("profile_io_slot")
        self._pattr_profile_io_slot = value


class ProfileSRIOVConfiguredLogicalPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_id = None
        self._pattr_configuration_id = None
        self._pattr_configured_capacity = None
        self._pattr_is_debug = None
        self._pattr_is_diagnostic = None
        self._pattr_is_huge_dma = None
        self._pattr_is_promiscous = None
        self._pattr_location_code = None
        self._pattr_logical_port_id = None
        self._pattr_physical_port_id = None
        self._pattr_port_vlan_id = None
        self._pattr_tuning_buffer_id = None
        super(ProfileSRIOVConfiguredLogicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def adapter_id(self):
        return self._pattr_adapter_id
    @adapter_id.setter
    def adapter_id(self, value):
        self._modified_attrs.add("adapter_id")
        self._pattr_adapter_id = value

    @property
    def configuration_id(self):
        return self._pattr_configuration_id
    @configuration_id.setter
    def configuration_id(self, value):
        self._modified_attrs.add("configuration_id")
        self._pattr_configuration_id = value

    @property
    def configured_capacity(self):
        return self._pattr_configured_capacity
    @configured_capacity.setter
    def configured_capacity(self, value):
        self._modified_attrs.add("configured_capacity")
        self._pattr_configured_capacity = value

    @property
    def is_debug(self):
        return self._pattr_is_debug
    @is_debug.setter
    def is_debug(self, value):
        self._modified_attrs.add("is_debug")
        self._pattr_is_debug = value

    @property
    def is_diagnostic(self):
        return self._pattr_is_diagnostic
    @is_diagnostic.setter
    def is_diagnostic(self, value):
        self._modified_attrs.add("is_diagnostic")
        self._pattr_is_diagnostic = value

    @property
    def is_huge_dma(self):
        return self._pattr_is_huge_dma
    @is_huge_dma.setter
    def is_huge_dma(self, value):
        self._modified_attrs.add("is_huge_dma")
        self._pattr_is_huge_dma = value

    @property
    def is_promiscous(self):
        return self._pattr_is_promiscous
    @is_promiscous.setter
    def is_promiscous(self, value):
        self._modified_attrs.add("is_promiscous")
        self._pattr_is_promiscous = value

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def logical_port_id(self):
        return self._pattr_logical_port_id
    @logical_port_id.setter
    def logical_port_id(self, value):
        self._modified_attrs.add("logical_port_id")
        self._pattr_logical_port_id = value

    @property
    def physical_port_id(self):
        return self._pattr_physical_port_id
    @physical_port_id.setter
    def physical_port_id(self, value):
        self._modified_attrs.add("physical_port_id")
        self._pattr_physical_port_id = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def tuning_buffer_id(self):
        return self._pattr_tuning_buffer_id
    @tuning_buffer_id.setter
    def tuning_buffer_id(self, value):
        self._modified_attrs.add("tuning_buffer_id")
        self._pattr_tuning_buffer_id = value


class ProfileSRIOVEthernetLogicalPort(ProfileSRIOVConfiguredLogicalPort):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_mac_addresses = None
        self._pattr_allowed_vla_ns = None
        self._pattr_ieee8021_q_allowable_priorities = None
        self._pattr_ieee8021_q_priority = None
        self._pattr_mac_address = None
        self._pattr_mac_address_flags = None
        self._pattr_number_of_allowed_vla_ns = None
        super(ProfileSRIOVEthernetLogicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allowed_mac_addresses(self):
        return self._pattr_allowed_mac_addresses
    @allowed_mac_addresses.setter
    def allowed_mac_addresses(self, value):
        self._modified_attrs.add("allowed_mac_addresses")
        self._pattr_allowed_mac_addresses = value

    @property
    def allowed_vla_ns(self):
        return self._pattr_allowed_vla_ns
    @allowed_vla_ns.setter
    def allowed_vla_ns(self, value):
        self._modified_attrs.add("allowed_vla_ns")
        self._pattr_allowed_vla_ns = value

    @property
    def ieee8021_q_allowable_priorities(self):
        return self._pattr_ieee8021_q_allowable_priorities
    @ieee8021_q_allowable_priorities.setter
    def ieee8021_q_allowable_priorities(self, value):
        self._modified_attrs.add("ieee8021_q_allowable_priorities")
        self._pattr_ieee8021_q_allowable_priorities = value

    @property
    def ieee8021_q_priority(self):
        return self._pattr_ieee8021_q_priority
    @ieee8021_q_priority.setter
    def ieee8021_q_priority(self, value):
        self._modified_attrs.add("ieee8021_q_priority")
        self._pattr_ieee8021_q_priority = value

    @property
    def mac_address(self):
        return self._pattr_mac_address
    @mac_address.setter
    def mac_address(self, value):
        self._modified_attrs.add("mac_address")
        self._pattr_mac_address = value

    @property
    def mac_address_flags(self):
        return self._pattr_mac_address_flags
    @mac_address_flags.setter
    def mac_address_flags(self, value):
        self._modified_attrs.add("mac_address_flags")
        self._pattr_mac_address_flags = value

    @property
    def number_of_allowed_vla_ns(self):
        return self._pattr_number_of_allowed_vla_ns
    @number_of_allowed_vla_ns.setter
    def number_of_allowed_vla_ns(self, value):
        self._modified_attrs.add("number_of_allowed_vla_ns")
        self._pattr_number_of_allowed_vla_ns = value


class ProfileSRIOVEthernetLogicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_profile_sriov_ethernet_logical_port = []
        super(ProfileSRIOVEthernetLogicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def profile_sriov_ethernet_logical_port(self):
        return self._pattr_profile_sriov_ethernet_logical_port
    @profile_sriov_ethernet_logical_port.setter
    def profile_sriov_ethernet_logical_port(self, value):
        self._modified_attrs.add("profile_sriov_ethernet_logical_port")
        self._pattr_profile_sriov_ethernet_logical_port = value


class ProfileTrunkAdapter(ProfileVirtualEthernetAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_interface_name = None
        self._pattr_trunk_priority = None
        super(ProfileTrunkAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def interface_name(self):
        return self._pattr_interface_name
    @interface_name.setter
    def interface_name(self, value):
        self._modified_attrs.add("interface_name")
        self._pattr_interface_name = value

    @property
    def trunk_priority(self):
        return self._pattr_trunk_priority
    @trunk_priority.setter
    def trunk_priority(self, value):
        self._modified_attrs.add("trunk_priority")
        self._pattr_trunk_priority = value


class ProfileVirtualFibreChannelAdapter(ProfileVirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_connecting_partition_id = None
        self._pattr_connecting_virtual_slot_number = None
        super(ProfileVirtualFibreChannelAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def connecting_partition_id(self):
        return self._pattr_connecting_partition_id
    @connecting_partition_id.setter
    def connecting_partition_id(self, value):
        self._modified_attrs.add("connecting_partition_id")
        self._pattr_connecting_partition_id = value

    @property
    def connecting_virtual_slot_number(self):
        return self._pattr_connecting_virtual_slot_number
    @connecting_virtual_slot_number.setter
    def connecting_virtual_slot_number(self, value):
        self._modified_attrs.add("connecting_virtual_slot_number")
        self._pattr_connecting_virtual_slot_number = value


class ProfileVirtualFibreChannelClientAdapter(ProfileVirtualFibreChannelAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_wwp_ns = None
        super(ProfileVirtualFibreChannelClientAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def wwp_ns(self):
        return self._pattr_wwp_ns
    @wwp_ns.setter
    def wwp_ns(self, value):
        self._modified_attrs.add("wwp_ns")
        self._pattr_wwp_ns = value


class ProfileVirtualFibreChannelServerAdapter(ProfileVirtualFibreChannelAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(ProfileVirtualFibreChannelServerAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class ProfileVirtualIOAdapterChoiceCollection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_profile_virtual_io_adapter_choice = []
        super(ProfileVirtualIOAdapterChoiceCollection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def profile_virtual_io_adapter_choice(self):
        return self._pattr_profile_virtual_io_adapter_choice
    @profile_virtual_io_adapter_choice.setter
    def profile_virtual_io_adapter_choice(self, value):
        self._modified_attrs.add("profile_virtual_io_adapter_choice")
        self._pattr_profile_virtual_io_adapter_choice = value


class ProfileVirtualSCSIAdapter(ProfileVirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_backing_device_name = None
        self._pattr_remote_backing_device_name = None
        self._pattr_remote_partition_id = None
        self._pattr_remote_slot_number = None
        super(ProfileVirtualSCSIAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def backing_device_name(self):
        return self._pattr_backing_device_name
    @backing_device_name.setter
    def backing_device_name(self, value):
        self._modified_attrs.add("backing_device_name")
        self._pattr_backing_device_name = value

    @property
    def remote_backing_device_name(self):
        return self._pattr_remote_backing_device_name
    @remote_backing_device_name.setter
    def remote_backing_device_name(self, value):
        self._modified_attrs.add("remote_backing_device_name")
        self._pattr_remote_backing_device_name = value

    @property
    def remote_partition_id(self):
        return self._pattr_remote_partition_id
    @remote_partition_id.setter
    def remote_partition_id(self, value):
        self._modified_attrs.add("remote_partition_id")
        self._pattr_remote_partition_id = value

    @property
    def remote_slot_number(self):
        return self._pattr_remote_slot_number
    @remote_slot_number.setter
    def remote_slot_number(self, value):
        self._modified_attrs.add("remote_slot_number")
        self._pattr_remote_slot_number = value


class ProfileVirtualSCSIClientAdapter(ProfileVirtualSCSIAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(ProfileVirtualSCSIClientAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class ProfileVirtualSCSIServerAdapter(ProfileVirtualSCSIAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None
        super(ProfileVirtualSCSIServerAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class ReservedStorageDevice(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_logical_partition = None
        self._pattr_device_name = None
        self._pattr_device_selection_type = None
        self._pattr_device_size = None
        self._pattr_device_state = None
        self._pattr_device_type = None
        self._pattr_is_redundant = None
        self._pattr_location_code = None
        self._pattr_redundancy_capable = None
        self._pattr_redundant_device_name = None
        self._pattr_redundant_device_state = None
        self._pattr_redundant_location_code = None
        self._pattr_unique_device_id = None
        super(ReservedStorageDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def associated_logical_partition(self):
        return self._pattr_associated_logical_partition

    @property
    def device_name(self):
        return self._pattr_device_name
    @device_name.setter
    def device_name(self, value):
        self._modified_attrs.add("device_name")
        self._pattr_device_name = value

    @property
    def device_selection_type(self):
        return self._pattr_device_selection_type

    @property
    def device_size(self):
        return self._pattr_device_size
    @device_size.setter
    def device_size(self, value):
        self._modified_attrs.add("device_size")
        self._pattr_device_size = value

    @property
    def device_state(self):
        return self._pattr_device_state

    @property
    def device_type(self):
        return self._pattr_device_type

    @property
    def is_redundant(self):
        return self._pattr_is_redundant

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def redundancy_capable(self):
        return self._pattr_redundancy_capable

    @property
    def redundant_device_name(self):
        return self._pattr_redundant_device_name
    @redundant_device_name.setter
    def redundant_device_name(self, value):
        self._modified_attrs.add("redundant_device_name")
        self._pattr_redundant_device_name = value

    @property
    def redundant_device_state(self):
        return self._pattr_redundant_device_state

    @property
    def redundant_location_code(self):
        return self._pattr_redundant_location_code

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id


class SharedMemoryPool(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_current_available_pool_memory = None
        self._pattr_current_maximum_pool_memory = None
        self._pattr_current_pool_memory = None
        self._pattr_free_memory_devices_from_paging_service_partition_one = None
        self._pattr_free_memory_devices_from_paging_service_partition_two = None
        self._pattr_free_redundant_memory_devices = None
        self._pattr_hardware_page_table_ratio = None
        self._pattr_memory_deduplication_enabled = None
        self._pattr_memory_deduplication_table_ratio = None
        self._pattr_page_size = None
        self._pattr_paging_devices = None
        self._pattr_paging_service_partition_one = None
        self._pattr_paging_service_partition_two = None
        self._pattr_pending_available_pool_memory = None
        self._pattr_pending_maximum_pool_memory = None
        self._pattr_pending_pool_memory = None
        self._pattr_pool_id = None
        self._pattr_pool_size = None
        self._pattr_system_firmware_pool_memory = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SharedMemoryPool,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def current_available_pool_memory(self):
        return self._pattr_current_available_pool_memory

    @property
    def current_maximum_pool_memory(self):
        return self._pattr_current_maximum_pool_memory

    @property
    def current_pool_memory(self):
        return self._pattr_current_pool_memory

    @property
    def free_memory_devices_from_paging_service_partition_one(self):
        return self._pattr_free_memory_devices_from_paging_service_partition_one

    @property
    def free_memory_devices_from_paging_service_partition_two(self):
        return self._pattr_free_memory_devices_from_paging_service_partition_two

    @property
    def free_redundant_memory_devices(self):
        return self._pattr_free_redundant_memory_devices

    @property
    def hardware_page_table_ratio(self):
        return self._pattr_hardware_page_table_ratio
    @hardware_page_table_ratio.setter
    def hardware_page_table_ratio(self, value):
        self._modified_attrs.add("hardware_page_table_ratio")
        self._pattr_hardware_page_table_ratio = value

    @property
    def memory_deduplication_enabled(self):
        return self._pattr_memory_deduplication_enabled
    @memory_deduplication_enabled.setter
    def memory_deduplication_enabled(self, value):
        self._modified_attrs.add("memory_deduplication_enabled")
        self._pattr_memory_deduplication_enabled = value

    @property
    def memory_deduplication_table_ratio(self):
        return self._pattr_memory_deduplication_table_ratio
    @memory_deduplication_table_ratio.setter
    def memory_deduplication_table_ratio(self, value):
        self._modified_attrs.add("memory_deduplication_table_ratio")
        self._pattr_memory_deduplication_table_ratio = value

    @property
    def page_size(self):
        return self._pattr_page_size

    @property
    def paging_devices(self):
        return self._pattr_paging_devices
    @paging_devices.setter
    def paging_devices(self, value):
        self._modified_attrs.add("paging_devices")
        self._pattr_paging_devices = value

    @property
    def paging_service_partition_one(self):
        return self._pattr_paging_service_partition_one
    @paging_service_partition_one.setter
    def paging_service_partition_one(self, value):
        self._modified_attrs.add("paging_service_partition_one")
        self._pattr_paging_service_partition_one = value

    @property
    def paging_service_partition_two(self):
        return self._pattr_paging_service_partition_two
    @paging_service_partition_two.setter
    def paging_service_partition_two(self, value):
        self._modified_attrs.add("paging_service_partition_two")
        self._pattr_paging_service_partition_two = value

    @property
    def pending_available_pool_memory(self):
        return self._pattr_pending_available_pool_memory
    @pending_available_pool_memory.setter
    def pending_available_pool_memory(self, value):
        self._modified_attrs.add("pending_available_pool_memory")
        self._pattr_pending_available_pool_memory = value

    @property
    def pending_maximum_pool_memory(self):
        return self._pattr_pending_maximum_pool_memory
    @pending_maximum_pool_memory.setter
    def pending_maximum_pool_memory(self, value):
        self._modified_attrs.add("pending_maximum_pool_memory")
        self._pattr_pending_maximum_pool_memory = value

    @property
    def pending_pool_memory(self):
        return self._pattr_pending_pool_memory
    @pending_pool_memory.setter
    def pending_pool_memory(self, value):
        self._modified_attrs.add("pending_pool_memory")
        self._pattr_pending_pool_memory = value

    @property
    def pool_id(self):
        return self._pattr_pool_id

    @property
    def pool_size(self):
        return self._pattr_pool_size
    @pool_size.setter
    def pool_size(self, value):
        self._modified_attrs.add("pool_size")
        self._pattr_pool_size = value

    @property
    def system_firmware_pool_memory(self):
        return self._pattr_system_firmware_pool_memory


class ReservedStorageDevicePool(SharedMemoryPool):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(ReservedStorageDevicePool,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class ReservedStorageDevicePool_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(ReservedStorageDevicePool_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class ReservedStorageDevice_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_reserved_storage_device = []
        super(ReservedStorageDevice_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def reserved_storage_device(self):
        return self._pattr_reserved_storage_device
    @reserved_storage_device.setter
    def reserved_storage_device(self, value):
        self._modified_attrs.add("reserved_storage_device")
        self._pattr_reserved_storage_device = value


class SRIOVAdapter(IOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_mode = None
        self._pattr_adapter_state = None
        self._pattr_converged_ethernet_physical_ports = None
        self._pattr_ethernet_logical_ports = None
        self._pattr_ethernet_physical_ports = None
        self._pattr_fibre_channel_over_ethernet_logical_ports = None
        self._pattr_is_functional = None
        self._pattr_maximum_huge_dma_logical_ports = None
        self._pattr_maximum_logical_ports_supported = None
        self._pattr_sriov_adapter_id = None
        self._pattr_unconfigured_logical_ports = None
        super(SRIOVAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def adapter_mode(self):
        return self._pattr_adapter_mode
    @adapter_mode.setter
    def adapter_mode(self, value):
        self._modified_attrs.add("adapter_mode")
        self._pattr_adapter_mode = value

    @property
    def adapter_state(self):
        return self._pattr_adapter_state

    @property
    def converged_ethernet_physical_ports(self):
        return self._pattr_converged_ethernet_physical_ports

    @property
    def ethernet_logical_ports(self):
        return self._pattr_ethernet_logical_ports

    @property
    def ethernet_physical_ports(self):
        return self._pattr_ethernet_physical_ports

    @property
    def fibre_channel_over_ethernet_logical_ports(self):
        return self._pattr_fibre_channel_over_ethernet_logical_ports

    @property
    def is_functional(self):
        return self._pattr_is_functional

    @property
    def maximum_huge_dma_logical_ports(self):
        return self._pattr_maximum_huge_dma_logical_ports

    @property
    def maximum_logical_ports_supported(self):
        return self._pattr_maximum_logical_ports_supported

    @property
    def sriov_adapter_id(self):
        return self._pattr_sriov_adapter_id
    @sriov_adapter_id.setter
    def sriov_adapter_id(self, value):
        self._modified_attrs.add("sriov_adapter_id")
        self._pattr_sriov_adapter_id = value

    @property
    def unconfigured_logical_ports(self):
        return self._pattr_unconfigured_logical_ports


class SRIOVConfiguredLogicalPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_id = None
        self._pattr_configuration_id = None
        self._pattr_configured_capacity = None
        self._pattr_device_name = None
        self._pattr_dynamic_reconfiguration_connector_name = None
        self._pattr_is_debug = None
        self._pattr_is_diagnostic = None
        self._pattr_is_functional = None
        self._pattr_is_huge_dma = None
        self._pattr_is_promiscous = None
        self._pattr_location_code = None
        self._pattr_logical_port_id = None
        self._pattr_physical_port_id = None
        self._pattr_port_vlan_id = None
        self._pattr_tuning_buffer_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SRIOVConfiguredLogicalPort,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def adapter_id(self):
        return self._pattr_adapter_id
    @adapter_id.setter
    def adapter_id(self, value):
        self._modified_attrs.add("adapter_id")
        self._pattr_adapter_id = value

    @property
    def configuration_id(self):
        return self._pattr_configuration_id
    @configuration_id.setter
    def configuration_id(self, value):
        self._modified_attrs.add("configuration_id")
        self._pattr_configuration_id = value

    @property
    def configured_capacity(self):
        return self._pattr_configured_capacity
    @configured_capacity.setter
    def configured_capacity(self, value):
        self._modified_attrs.add("configured_capacity")
        self._pattr_configured_capacity = value

    @property
    def device_name(self):
        return self._pattr_device_name

    @property
    def dynamic_reconfiguration_connector_name(self):
        return self._pattr_dynamic_reconfiguration_connector_name

    @property
    def is_debug(self):
        return self._pattr_is_debug
    @is_debug.setter
    def is_debug(self, value):
        self._modified_attrs.add("is_debug")
        self._pattr_is_debug = value

    @property
    def is_diagnostic(self):
        return self._pattr_is_diagnostic
    @is_diagnostic.setter
    def is_diagnostic(self, value):
        self._modified_attrs.add("is_diagnostic")
        self._pattr_is_diagnostic = value

    @property
    def is_functional(self):
        return self._pattr_is_functional

    @property
    def is_huge_dma(self):
        return self._pattr_is_huge_dma
    @is_huge_dma.setter
    def is_huge_dma(self, value):
        self._modified_attrs.add("is_huge_dma")
        self._pattr_is_huge_dma = value

    @property
    def is_promiscous(self):
        return self._pattr_is_promiscous
    @is_promiscous.setter
    def is_promiscous(self, value):
        self._modified_attrs.add("is_promiscous")
        self._pattr_is_promiscous = value

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def logical_port_id(self):
        return self._pattr_logical_port_id
    @logical_port_id.setter
    def logical_port_id(self, value):
        self._modified_attrs.add("logical_port_id")
        self._pattr_logical_port_id = value

    @property
    def physical_port_id(self):
        return self._pattr_physical_port_id
    @physical_port_id.setter
    def physical_port_id(self, value):
        self._modified_attrs.add("physical_port_id")
        self._pattr_physical_port_id = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id
    @port_vlan_id.setter
    def port_vlan_id(self, value):
        self._modified_attrs.add("port_vlan_id")
        self._pattr_port_vlan_id = value

    @property
    def tuning_buffer_id(self):
        return self._pattr_tuning_buffer_id
    @tuning_buffer_id.setter
    def tuning_buffer_id(self, value):
        self._modified_attrs.add("tuning_buffer_id")
        self._pattr_tuning_buffer_id = value


class SRIOVPhysicalPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_configured_connection_speed = None
        self._pattr_configured_mtu = None
        self._pattr_configured_options = []
        self._pattr_current_connection_speed = None
        self._pattr_current_options = []
        self._pattr_label = None
        self._pattr_link_status = None
        self._pattr_location_code = None
        self._pattr_maximum_diagnostics_logical_ports = None
        self._pattr_maximum_promiscuous_logical_ports = None
        self._pattr_physical_port_id = None
        self._pattr_port_capabilities = []
        self._pattr_port_logical_port_limit = None
        self._pattr_port_type = None
        self._pattr_sub_label = None
        self._pattr_supported_connection_speeds = []
        self._pattr_supported_mt_us = []
        self._pattr_supported_options = []
        self._pattr_supported_priority_access_control_list = None
        super(SRIOVPhysicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def configured_connection_speed(self):
        return self._pattr_configured_connection_speed
    @configured_connection_speed.setter
    def configured_connection_speed(self, value):
        self._modified_attrs.add("configured_connection_speed")
        self._pattr_configured_connection_speed = value

    @property
    def configured_mtu(self):
        return self._pattr_configured_mtu
    @configured_mtu.setter
    def configured_mtu(self, value):
        self._modified_attrs.add("configured_mtu")
        self._pattr_configured_mtu = value

    @property
    def configured_options(self):
        return self._pattr_configured_options
    @configured_options.setter
    def configured_options(self, value):
        self._modified_attrs.add("configured_options")
        self._pattr_configured_options = value

    @property
    def current_connection_speed(self):
        return self._pattr_current_connection_speed

    @property
    def current_options(self):
        return self._pattr_current_options

    @property
    def label(self):
        return self._pattr_label
    @label.setter
    def label(self, value):
        self._modified_attrs.add("label")
        self._pattr_label = value

    @property
    def link_status(self):
        return self._pattr_link_status

    @property
    def location_code(self):
        return self._pattr_location_code

    @property
    def maximum_diagnostics_logical_ports(self):
        return self._pattr_maximum_diagnostics_logical_ports

    @property
    def maximum_promiscuous_logical_ports(self):
        return self._pattr_maximum_promiscuous_logical_ports

    @property
    def physical_port_id(self):
        return self._pattr_physical_port_id

    @property
    def port_capabilities(self):
        return self._pattr_port_capabilities

    @property
    def port_logical_port_limit(self):
        return self._pattr_port_logical_port_limit

    @property
    def port_type(self):
        return self._pattr_port_type

    @property
    def sub_label(self):
        return self._pattr_sub_label
    @sub_label.setter
    def sub_label(self, value):
        self._modified_attrs.add("sub_label")
        self._pattr_sub_label = value

    @property
    def supported_connection_speeds(self):
        return self._pattr_supported_connection_speeds

    @property
    def supported_mt_us(self):
        return self._pattr_supported_mt_us

    @property
    def supported_options(self):
        return self._pattr_supported_options

    @property
    def supported_priority_access_control_list(self):
        return self._pattr_supported_priority_access_control_list


class SRIOVEthernetPhysicalPort(SRIOVPhysicalPort):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allocated_capacity = None
        self._pattr_configured_ethernet_logical_ports = None
        self._pattr_configured_max_ethernet_logical_ports = None
        self._pattr_max_supported_ethernet_logical_ports = None
        self._pattr_maximum_port_vlanid = None
        self._pattr_maximum_vlanid = None
        self._pattr_minimum_ethernet_capacity_granularity = None
        self._pattr_minimum_port_vlanid = None
        self._pattr_minimum_vlanid = None
        super(SRIOVEthernetPhysicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allocated_capacity(self):
        return self._pattr_allocated_capacity

    @property
    def configured_ethernet_logical_ports(self):
        return self._pattr_configured_ethernet_logical_ports

    @property
    def configured_max_ethernet_logical_ports(self):
        return self._pattr_configured_max_ethernet_logical_ports
    @configured_max_ethernet_logical_ports.setter
    def configured_max_ethernet_logical_ports(self, value):
        self._modified_attrs.add("configured_max_ethernet_logical_ports")
        self._pattr_configured_max_ethernet_logical_ports = value

    @property
    def max_supported_ethernet_logical_ports(self):
        return self._pattr_max_supported_ethernet_logical_ports

    @property
    def maximum_port_vlanid(self):
        return self._pattr_maximum_port_vlanid

    @property
    def maximum_vlanid(self):
        return self._pattr_maximum_vlanid

    @property
    def minimum_ethernet_capacity_granularity(self):
        return self._pattr_minimum_ethernet_capacity_granularity

    @property
    def minimum_port_vlanid(self):
        return self._pattr_minimum_port_vlanid

    @property
    def minimum_vlanid(self):
        return self._pattr_minimum_vlanid


class SRIOVConvergedNetworkAdapterPhysicalPort(SRIOVEthernetPhysicalPort):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_configured_fiber_channel_over_ethernet_logical_ports = None
        self._pattr_configured_max_fiber_channel_over_ethernet_logical_ports = None
        self._pattr_default_fiber_channel_targets_for_backing_device = None
        self._pattr_default_fiber_channel_targets_for_non_backing_device = None
        self._pattr_fiber_channel_targets_rounding_value = None
        self._pattr_max_supported_fiber_channel_over_ethernet_logical_ports = None
        self._pattr_maximum_fiber_channel_targets = None
        self._pattr_minimum_f_co_e_capacity_granularity = None
        super(SRIOVConvergedNetworkAdapterPhysicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def configured_fiber_channel_over_ethernet_logical_ports(self):
        return self._pattr_configured_fiber_channel_over_ethernet_logical_ports
    @configured_fiber_channel_over_ethernet_logical_ports.setter
    def configured_fiber_channel_over_ethernet_logical_ports(self, value):
        self._modified_attrs.add("configured_fiber_channel_over_ethernet_logical_ports")
        self._pattr_configured_fiber_channel_over_ethernet_logical_ports = value

    @property
    def configured_max_fiber_channel_over_ethernet_logical_ports(self):
        return self._pattr_configured_max_fiber_channel_over_ethernet_logical_ports
    @configured_max_fiber_channel_over_ethernet_logical_ports.setter
    def configured_max_fiber_channel_over_ethernet_logical_ports(self, value):
        self._modified_attrs.add("configured_max_fiber_channel_over_ethernet_logical_ports")
        self._pattr_configured_max_fiber_channel_over_ethernet_logical_ports = value

    @property
    def default_fiber_channel_targets_for_backing_device(self):
        return self._pattr_default_fiber_channel_targets_for_backing_device

    @property
    def default_fiber_channel_targets_for_non_backing_device(self):
        return self._pattr_default_fiber_channel_targets_for_non_backing_device

    @property
    def fiber_channel_targets_rounding_value(self):
        return self._pattr_fiber_channel_targets_rounding_value

    @property
    def max_supported_fiber_channel_over_ethernet_logical_ports(self):
        return self._pattr_max_supported_fiber_channel_over_ethernet_logical_ports

    @property
    def maximum_fiber_channel_targets(self):
        return self._pattr_maximum_fiber_channel_targets

    @property
    def minimum_f_co_e_capacity_granularity(self):
        return self._pattr_minimum_f_co_e_capacity_granularity


class SRIOVConvergedNetworkAdapterPhysicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_sriov_converged_network_adapter_physical_port = []
        super(SRIOVConvergedNetworkAdapterPhysicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def sriov_converged_network_adapter_physical_port(self):
        return self._pattr_sriov_converged_network_adapter_physical_port
    @sriov_converged_network_adapter_physical_port.setter
    def sriov_converged_network_adapter_physical_port(self, value):
        self._modified_attrs.add("sriov_converged_network_adapter_physical_port")
        self._pattr_sriov_converged_network_adapter_physical_port = value


class SRIOVEthernetLogicalPort(SRIOVConfiguredLogicalPort):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_mac_addresses = None
        self._pattr_allowed_vla_ns = None
        self._pattr_current_mac_address = None
        self._pattr_ieee8021_q_allowable_priorities = None
        self._pattr_ieee8021_q_priority = None
        self._pattr_mac_address = None
        self._pattr_mac_address_flags = None
        self._pattr_number_of_allowed_vla_ns = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SRIOVEthernetLogicalPort,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def allowed_mac_addresses(self):
        return self._pattr_allowed_mac_addresses
    @allowed_mac_addresses.setter
    def allowed_mac_addresses(self, value):
        self._modified_attrs.add("allowed_mac_addresses")
        self._pattr_allowed_mac_addresses = value

    @property
    def allowed_vla_ns(self):
        return self._pattr_allowed_vla_ns
    @allowed_vla_ns.setter
    def allowed_vla_ns(self, value):
        self._modified_attrs.add("allowed_vla_ns")
        self._pattr_allowed_vla_ns = value

    @property
    def current_mac_address(self):
        return self._pattr_current_mac_address

    @property
    def ieee8021_q_allowable_priorities(self):
        return self._pattr_ieee8021_q_allowable_priorities
    @ieee8021_q_allowable_priorities.setter
    def ieee8021_q_allowable_priorities(self, value):
        self._modified_attrs.add("ieee8021_q_allowable_priorities")
        self._pattr_ieee8021_q_allowable_priorities = value

    @property
    def ieee8021_q_priority(self):
        return self._pattr_ieee8021_q_priority
    @ieee8021_q_priority.setter
    def ieee8021_q_priority(self, value):
        self._modified_attrs.add("ieee8021_q_priority")
        self._pattr_ieee8021_q_priority = value

    @property
    def mac_address(self):
        return self._pattr_mac_address
    @mac_address.setter
    def mac_address(self, value):
        self._modified_attrs.add("mac_address")
        self._pattr_mac_address = value

    @property
    def mac_address_flags(self):
        return self._pattr_mac_address_flags
    @mac_address_flags.setter
    def mac_address_flags(self, value):
        self._modified_attrs.add("mac_address_flags")
        self._pattr_mac_address_flags = value

    @property
    def number_of_allowed_vla_ns(self):
        return self._pattr_number_of_allowed_vla_ns
    @number_of_allowed_vla_ns.setter
    def number_of_allowed_vla_ns(self, value):
        self._modified_attrs.add("number_of_allowed_vla_ns")
        self._pattr_number_of_allowed_vla_ns = value


class SRIOVEthernetLogicalPort_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(SRIOVEthernetLogicalPort_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class SRIOVEthernetPhysicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_sriov_ethernet_physical_port = []
        super(SRIOVEthernetPhysicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def sriov_ethernet_physical_port(self):
        return self._pattr_sriov_ethernet_physical_port
    @sriov_ethernet_physical_port.setter
    def sriov_ethernet_physical_port(self, value):
        self._modified_attrs.add("sriov_ethernet_physical_port")
        self._pattr_sriov_ethernet_physical_port = value


class SRIOVFibreChannelOverEthernetLogicalPort(SRIOVConfiguredLogicalPort):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_fiber_channel_targets = None
        self._pattr_wwpn1 = None
        self._pattr_wwpn2 = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SRIOVFibreChannelOverEthernetLogicalPort,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def fiber_channel_targets(self):
        return self._pattr_fiber_channel_targets
    @fiber_channel_targets.setter
    def fiber_channel_targets(self, value):
        self._modified_attrs.add("fiber_channel_targets")
        self._pattr_fiber_channel_targets = value

    @property
    def wwpn1(self):
        return self._pattr_wwpn1
    @wwpn1.setter
    def wwpn1(self, value):
        self._modified_attrs.add("wwpn1")
        self._pattr_wwpn1 = value

    @property
    def wwpn2(self):
        return self._pattr_wwpn2
    @wwpn2.setter
    def wwpn2(self, value):
        self._modified_attrs.add("wwpn2")
        self._pattr_wwpn2 = value


class SRIOVFibreChannelOverEthernetLogicalPort_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(SRIOVFibreChannelOverEthernetLogicalPort_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class SRIOVUnconfiguredLogicalPort(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dynamic_reconfiguration_connector_index = None
        self._pattr_dynamic_reconfiguration_connector_name = None
        self._pattr_location_code = None
        super(SRIOVUnconfiguredLogicalPort,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def dynamic_reconfiguration_connector_index(self):
        return self._pattr_dynamic_reconfiguration_connector_index

    @property
    def dynamic_reconfiguration_connector_name(self):
        return self._pattr_dynamic_reconfiguration_connector_name

    @property
    def location_code(self):
        return self._pattr_location_code


class SRIOVUnconfiguredLogicalPort_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_sriov_unconfigured_logical_port = []
        super(SRIOVUnconfiguredLogicalPort_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def sriov_unconfigured_logical_port(self):
        return self._pattr_sriov_unconfigured_logical_port
    @sriov_unconfigured_logical_port.setter
    def sriov_unconfigured_logical_port(self, value):
        self._modified_attrs.add("sriov_unconfigured_logical_port")
        self._pattr_sriov_unconfigured_logical_port = value


class SchemaVersion(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_minor_version = None
        self._pattr_schema_namespace = None
        super(SchemaVersion,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def minor_version(self):
        return self._pattr_minor_version
    @minor_version.setter
    def minor_version(self, value):
        self._modified_attrs.add("minor_version")
        self._pattr_minor_version = value

    @property
    def schema_namespace(self):
        return self._pattr_schema_namespace
    @schema_namespace.setter
    def schema_namespace(self, value):
        self._modified_attrs.add("schema_namespace")
        self._pattr_schema_namespace = value


class SharedEthernetAdapter(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_address_to_ping = None
        self._pattr_assigned_virtual_io_server = None
        self._pattr_backing_device_choice = None
        self._pattr_control_channel_interface_name = None
        self._pattr_device_name = None
        self._pattr_high_availability_mode = None
        self._pattr_iidp_service = None
        self._pattr_ip_interface = None
        self._pattr_is_primary = None
        self._pattr_jumbo_frames_enabled = None
        self._pattr_large_send = None
        self._pattr_port_vlan_id = None
        self._pattr_quality_of_service_mode = None
        self._pattr_queue_size = None
        self._pattr_thread_mode_enabled = None
        self._pattr_trunk_adapters = None
        self._pattr_unique_device_id = None
        super(SharedEthernetAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def address_to_ping(self):
        return self._pattr_address_to_ping
    @address_to_ping.setter
    def address_to_ping(self, value):
        self._modified_attrs.add("address_to_ping")
        self._pattr_address_to_ping = value

    @property
    def assigned_virtual_io_server(self):
        return self._pattr_assigned_virtual_io_server
    @assigned_virtual_io_server.setter
    def assigned_virtual_io_server(self, value):
        self._modified_attrs.add("assigned_virtual_io_server")
        self._pattr_assigned_virtual_io_server = value

    @property
    def backing_device_choice(self):
        return self._pattr_backing_device_choice
    @backing_device_choice.setter
    def backing_device_choice(self, value):
        self._modified_attrs.add("backing_device_choice")
        self._pattr_backing_device_choice = value

    @property
    def control_channel_interface_name(self):
        return self._pattr_control_channel_interface_name
    @control_channel_interface_name.setter
    def control_channel_interface_name(self, value):
        self._modified_attrs.add("control_channel_interface_name")
        self._pattr_control_channel_interface_name = value

    @property
    def device_name(self):
        return self._pattr_device_name
    @device_name.setter
    def device_name(self, value):
        self._modified_attrs.add("device_name")
        self._pattr_device_name = value

    @property
    def high_availability_mode(self):
        return self._pattr_high_availability_mode
    @high_availability_mode.setter
    def high_availability_mode(self, value):
        self._modified_attrs.add("high_availability_mode")
        self._pattr_high_availability_mode = value

    @property
    def iidp_service(self):
        return self._pattr_iidp_service
    @iidp_service.setter
    def iidp_service(self, value):
        self._modified_attrs.add("iidp_service")
        self._pattr_iidp_service = value

    @property
    def ip_interface(self):
        return self._pattr_ip_interface
    @ip_interface.setter
    def ip_interface(self, value):
        self._modified_attrs.add("ip_interface")
        self._pattr_ip_interface = value

    @property
    def is_primary(self):
        return self._pattr_is_primary
    @is_primary.setter
    def is_primary(self, value):
        self._modified_attrs.add("is_primary")
        self._pattr_is_primary = value

    @property
    def jumbo_frames_enabled(self):
        return self._pattr_jumbo_frames_enabled
    @jumbo_frames_enabled.setter
    def jumbo_frames_enabled(self, value):
        self._modified_attrs.add("jumbo_frames_enabled")
        self._pattr_jumbo_frames_enabled = value

    @property
    def large_send(self):
        return self._pattr_large_send
    @large_send.setter
    def large_send(self, value):
        self._modified_attrs.add("large_send")
        self._pattr_large_send = value

    @property
    def port_vlan_id(self):
        return self._pattr_port_vlan_id

    @property
    def quality_of_service_mode(self):
        return self._pattr_quality_of_service_mode
    @quality_of_service_mode.setter
    def quality_of_service_mode(self, value):
        self._modified_attrs.add("quality_of_service_mode")
        self._pattr_quality_of_service_mode = value

    @property
    def queue_size(self):
        return self._pattr_queue_size
    @queue_size.setter
    def queue_size(self, value):
        self._modified_attrs.add("queue_size")
        self._pattr_queue_size = value

    @property
    def thread_mode_enabled(self):
        return self._pattr_thread_mode_enabled
    @thread_mode_enabled.setter
    def thread_mode_enabled(self, value):
        self._modified_attrs.add("thread_mode_enabled")
        self._pattr_thread_mode_enabled = value

    @property
    def trunk_adapters(self):
        return self._pattr_trunk_adapters
    @trunk_adapters.setter
    def trunk_adapters(self, value):
        self._modified_attrs.add("trunk_adapters")
        self._pattr_trunk_adapters = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id


class SharedEthernetAdapter_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_shared_ethernet_adapter = []
        super(SharedEthernetAdapter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def shared_ethernet_adapter(self):
        return self._pattr_shared_ethernet_adapter
    @shared_ethernet_adapter.setter
    def shared_ethernet_adapter(self, value):
        self._modified_attrs.add("shared_ethernet_adapter")
        self._pattr_shared_ethernet_adapter = value


class SharedMemoryPool_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(SharedMemoryPool_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class SharedProcessorPool(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_assigned_partitions = None
        self._pattr_available_proc_units = None
        self._pattr_current_reserved_processing_units = None
        self._pattr_maximum_processing_units = None
        self._pattr_pending_reserved_processing_units = None
        self._pattr_pool_id = None
        self._pattr_pool_name = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SharedProcessorPool,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def assigned_partitions(self):
        return self._pattr_assigned_partitions
    @assigned_partitions.setter
    def assigned_partitions(self, value):
        self._modified_attrs.add("assigned_partitions")
        self._pattr_assigned_partitions = value

    @property
    def available_proc_units(self):
        return self._pattr_available_proc_units
    @available_proc_units.setter
    def available_proc_units(self, value):
        self._modified_attrs.add("available_proc_units")
        self._pattr_available_proc_units = value

    @property
    def current_reserved_processing_units(self):
        return self._pattr_current_reserved_processing_units

    @property
    def maximum_processing_units(self):
        return self._pattr_maximum_processing_units
    @maximum_processing_units.setter
    def maximum_processing_units(self, value):
        self._modified_attrs.add("maximum_processing_units")
        self._pattr_maximum_processing_units = value

    @property
    def pending_reserved_processing_units(self):
        return self._pattr_pending_reserved_processing_units
    @pending_reserved_processing_units.setter
    def pending_reserved_processing_units(self, value):
        self._modified_attrs.add("pending_reserved_processing_units")
        self._pattr_pending_reserved_processing_units = value

    @property
    def pool_id(self):
        return self._pattr_pool_id

    @property
    def pool_name(self):
        return self._pattr_pool_name
    @pool_name.setter
    def pool_name(self, value):
        self._modified_attrs.add("pool_name")
        self._pattr_pool_name = value


class SharedProcessorPool_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(SharedProcessorPool_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class SharedStoragePool(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_alert_threshold = None
        self._pattr_capacity = None
        self._pattr_free_space = None
        self._pattr_logical_units = None
        self._pattr_multi_data_tier_configured = None
        self._pattr_multi_failure_group_configured = None
        self._pattr_over_commit_space = None
        self._pattr_physical_volumes = None
        self._pattr_shared_storage_pool_id = None
        self._pattr_storage_pool_name = None
        self._pattr_total_logical_unit_size = None
        self._pattr_unique_device_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(SharedStoragePool,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def alert_threshold(self):
        return self._pattr_alert_threshold
    @alert_threshold.setter
    def alert_threshold(self, value):
        self._modified_attrs.add("alert_threshold")
        self._pattr_alert_threshold = value

    @property
    def capacity(self):
        return self._pattr_capacity
    @capacity.setter
    def capacity(self, value):
        self._modified_attrs.add("capacity")
        self._pattr_capacity = value

    @property
    def free_space(self):
        return self._pattr_free_space
    @free_space.setter
    def free_space(self, value):
        self._modified_attrs.add("free_space")
        self._pattr_free_space = value

    @property
    def logical_units(self):
        return self._pattr_logical_units
    @logical_units.setter
    def logical_units(self, value):
        self._modified_attrs.add("logical_units")
        self._pattr_logical_units = value

    @property
    def multi_data_tier_configured(self):
        return self._pattr_multi_data_tier_configured
    @multi_data_tier_configured.setter
    def multi_data_tier_configured(self, value):
        self._modified_attrs.add("multi_data_tier_configured")
        self._pattr_multi_data_tier_configured = value

    @property
    def multi_failure_group_configured(self):
        return self._pattr_multi_failure_group_configured
    @multi_failure_group_configured.setter
    def multi_failure_group_configured(self, value):
        self._modified_attrs.add("multi_failure_group_configured")
        self._pattr_multi_failure_group_configured = value

    @property
    def over_commit_space(self):
        return self._pattr_over_commit_space
    @over_commit_space.setter
    def over_commit_space(self, value):
        self._modified_attrs.add("over_commit_space")
        self._pattr_over_commit_space = value

    @property
    def physical_volumes(self):
        return self._pattr_physical_volumes
    @physical_volumes.setter
    def physical_volumes(self, value):
        self._modified_attrs.add("physical_volumes")
        self._pattr_physical_volumes = value

    @property
    def shared_storage_pool_id(self):
        return self._pattr_shared_storage_pool_id
    @shared_storage_pool_id.setter
    def shared_storage_pool_id(self, value):
        self._modified_attrs.add("shared_storage_pool_id")
        self._pattr_shared_storage_pool_id = value

    @property
    def storage_pool_name(self):
        return self._pattr_storage_pool_name
    @storage_pool_name.setter
    def storage_pool_name(self, value):
        self._modified_attrs.add("storage_pool_name")
        self._pattr_storage_pool_name = value

    @property
    def total_logical_unit_size(self):
        return self._pattr_total_logical_unit_size
    @total_logical_unit_size.setter
    def total_logical_unit_size(self, value):
        self._modified_attrs.add("total_logical_unit_size")
        self._pattr_total_logical_unit_size = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    def update_append_lus(self, inlus, xa=None):
        """For specified sharedstoragepool, add logicalunits.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_append_lus(self, inlus, xa=xa)

    def update_del_lus(self, lu_udids, xa=None):
        """Delete logicalunits.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_del_lus(self, lu_udids, xa=xa)

    def update_append_lu(self, unitname, unitcapacity, thin=True,
                         logicalunittype="VirtualIO_Disk",
                         clonedfrom=None,
                         xa=None):
        """Add a logicalunit.

        See :class: SharedStoragePoolManager for details.
        """

        return self.api.update_append_lu(self,
                                         unitname,
                                         unitcapacity,
                                         thin=thin,
                                         logicalunittype=logicalunittype,
                                         clonedfrom=clonedfrom,
                                         xa=xa)


class SharedStoragePoolLogicalUnitVirtualTargetDevice(VirtualTargetDevice):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_cluster_id = None
        self._pattr_path_name = None
        self._pattr_raid_level = None
        super(SharedStoragePoolLogicalUnitVirtualTargetDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def cluster_id(self):
        return self._pattr_cluster_id
    @cluster_id.setter
    def cluster_id(self, value):
        self._modified_attrs.add("cluster_id")
        self._pattr_cluster_id = value

    @property
    def path_name(self):
        return self._pattr_path_name
    @path_name.setter
    def path_name(self, value):
        self._modified_attrs.add("path_name")
        self._pattr_path_name = value

    @property
    def raid_level(self):
        return self._pattr_raid_level
    @raid_level.setter
    def raid_level(self, value):
        self._modified_attrs.add("raid_level")
        self._pattr_raid_level = value


class SharedStoragePool_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(SharedStoragePool_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class SystemCapabilities(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_active_logical_partition_mobility_capable = None
        self._pattr_active_logical_partition_shared_ide_processors_capable = None
        self._pattr_active_memory_deduplication_capable = None
        self._pattr_active_memory_expansion_capable = None
        self._pattr_active_memory_mirroring_capable = None
        self._pattr_active_memory_sharing_capable = None
        self._pattr_active_system_optimizer_capable = None
        self._pattr_address_broadcast_policy_capable = None
        self._pattr_aix_capable = None
        self._pattr_autorecovery_power_on_capable = None
        self._pattr_barrier_synchronization_register_capable = None
        self._pattr_capacity_on_demand_memory_capable = None
        self._pattr_capacity_on_demand_processor_capable = None
        self._pattr_custom_logical_partition_placement_capable = None
        self._pattr_custom_maximum_processes_per_logical_partition_capable = None
        self._pattr_custom_system_placement_capable = None
        self._pattr_electronic_error_reporting_capable = None
        self._pattr_external_intrusion_detection_capable = None
        self._pattr_firmware_power_saver_capable = None
        self._pattr_hardware_discovery_capable = None
        self._pattr_hardware_memory_compression_capable = None
        self._pattr_hardware_memory_encryption_capable = None
        self._pattr_hardware_power_saver_capable = None
        self._pattr_host_channel_adapter_capable = None
        self._pattr_huge_page_memory_capable = None
        self._pattr_huge_page_memory_override_capable = None
        self._pattr_ibm_i_capable = None
        self._pattr_ibm_i_logical_partition_mobility_capable = None
        self._pattr_ibm_i_logical_partition_suspend_capable = None
        self._pattr_ibm_i_network_install_capable = None
        self._pattr_ibm_i_restricted_io_mode_capable = None
        self._pattr_inactive_logical_partition_mobility_capable = None
        self._pattr_intelligent_platform_management_interface_capable = None
        self._pattr_linux_capable = None
        self._pattr_logical_host_ethernet_adapter_capable = None
        self._pattr_logical_partition_affinity_group_capable = None
        self._pattr_logical_partition_availability_priority_capable = None
        self._pattr_logical_partition_energy_management_capable = None
        self._pattr_logical_partition_processor_compatibility_mode_capable = None
        self._pattr_logical_partition_remote_restart_capable = None
        self._pattr_logical_partition_suspend_capable = None
        self._pattr_management_vlan_for_control_channel_capable = None
        self._pattr_memory_mirroring_capable = None
        self._pattr_micro_logical_partition_capable = None
        self._pattr_redundant_error_path_reporting_capable = None
        self._pattr_remote_restart_toggle_capable = None
        self._pattr_service_processor_concurrent_maintenance_capable = None
        self._pattr_service_processor_failover_capable = None
        self._pattr_shared_ethernet_failover_capable = None
        self._pattr_shared_processor_pool_capable = None
        self._pattr_sriov_capable = None
        self._pattr_switch_network_interface_message_passing_capable = None
        self._pattr_telnet5250_application_capable = None
        self._pattr_turbo_core_capable = None
        self._pattr_virtual_ethernet_adapter_dynamic_logical_partition_capable = None
        self._pattr_virtual_ethernet_custom_mac_address_capable = None
        self._pattr_virtual_ethernet_quality_of_service_capable = None
        self._pattr_virtual_fiber_channel_capable = None
        self._pattr_virtual_io_server_capable = None
        self._pattr_virtual_server_networking_phase2_capable = None
        self._pattr_virtual_server_protection_capable = None
        self._pattr_virtual_switch_capable = None
        self._pattr_virtual_trusted_platform_module_capable = None
        self._pattr_virtualization_engine_technologies_activation_capable = None
        self._pattr_vlan_statistics_capable = None
        super(SystemCapabilities,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def active_logical_partition_mobility_capable(self):
        return self._pattr_active_logical_partition_mobility_capable

    @property
    def active_logical_partition_shared_ide_processors_capable(self):
        return self._pattr_active_logical_partition_shared_ide_processors_capable

    @property
    def active_memory_deduplication_capable(self):
        return self._pattr_active_memory_deduplication_capable

    @property
    def active_memory_expansion_capable(self):
        return self._pattr_active_memory_expansion_capable

    @property
    def active_memory_mirroring_capable(self):
        return self._pattr_active_memory_mirroring_capable

    @property
    def active_memory_sharing_capable(self):
        return self._pattr_active_memory_sharing_capable

    @property
    def active_system_optimizer_capable(self):
        return self._pattr_active_system_optimizer_capable

    @property
    def address_broadcast_policy_capable(self):
        return self._pattr_address_broadcast_policy_capable

    @property
    def aix_capable(self):
        return self._pattr_aix_capable

    @property
    def autorecovery_power_on_capable(self):
        return self._pattr_autorecovery_power_on_capable

    @property
    def barrier_synchronization_register_capable(self):
        return self._pattr_barrier_synchronization_register_capable

    @property
    def capacity_on_demand_memory_capable(self):
        return self._pattr_capacity_on_demand_memory_capable

    @property
    def capacity_on_demand_processor_capable(self):
        return self._pattr_capacity_on_demand_processor_capable

    @property
    def custom_logical_partition_placement_capable(self):
        return self._pattr_custom_logical_partition_placement_capable

    @property
    def custom_maximum_processes_per_logical_partition_capable(self):
        return self._pattr_custom_maximum_processes_per_logical_partition_capable

    @property
    def custom_system_placement_capable(self):
        return self._pattr_custom_system_placement_capable

    @property
    def electronic_error_reporting_capable(self):
        return self._pattr_electronic_error_reporting_capable

    @property
    def external_intrusion_detection_capable(self):
        return self._pattr_external_intrusion_detection_capable

    @property
    def firmware_power_saver_capable(self):
        return self._pattr_firmware_power_saver_capable

    @property
    def hardware_discovery_capable(self):
        return self._pattr_hardware_discovery_capable

    @property
    def hardware_memory_compression_capable(self):
        return self._pattr_hardware_memory_compression_capable

    @property
    def hardware_memory_encryption_capable(self):
        return self._pattr_hardware_memory_encryption_capable

    @property
    def hardware_power_saver_capable(self):
        return self._pattr_hardware_power_saver_capable

    @property
    def host_channel_adapter_capable(self):
        return self._pattr_host_channel_adapter_capable

    @property
    def huge_page_memory_capable(self):
        return self._pattr_huge_page_memory_capable

    @property
    def huge_page_memory_override_capable(self):
        return self._pattr_huge_page_memory_override_capable

    @property
    def ibm_i_capable(self):
        return self._pattr_ibm_i_capable

    @property
    def ibm_i_logical_partition_mobility_capable(self):
        return self._pattr_ibm_i_logical_partition_mobility_capable

    @property
    def ibm_i_logical_partition_suspend_capable(self):
        return self._pattr_ibm_i_logical_partition_suspend_capable

    @property
    def ibm_i_network_install_capable(self):
        return self._pattr_ibm_i_network_install_capable

    @property
    def ibm_i_restricted_io_mode_capable(self):
        return self._pattr_ibm_i_restricted_io_mode_capable

    @property
    def inactive_logical_partition_mobility_capable(self):
        return self._pattr_inactive_logical_partition_mobility_capable

    @property
    def intelligent_platform_management_interface_capable(self):
        return self._pattr_intelligent_platform_management_interface_capable

    @property
    def linux_capable(self):
        return self._pattr_linux_capable

    @property
    def logical_host_ethernet_adapter_capable(self):
        return self._pattr_logical_host_ethernet_adapter_capable

    @property
    def logical_partition_affinity_group_capable(self):
        return self._pattr_logical_partition_affinity_group_capable

    @property
    def logical_partition_availability_priority_capable(self):
        return self._pattr_logical_partition_availability_priority_capable

    @property
    def logical_partition_energy_management_capable(self):
        return self._pattr_logical_partition_energy_management_capable

    @property
    def logical_partition_processor_compatibility_mode_capable(self):
        return self._pattr_logical_partition_processor_compatibility_mode_capable

    @property
    def logical_partition_remote_restart_capable(self):
        return self._pattr_logical_partition_remote_restart_capable

    @property
    def logical_partition_suspend_capable(self):
        return self._pattr_logical_partition_suspend_capable

    @property
    def management_vlan_for_control_channel_capable(self):
        return self._pattr_management_vlan_for_control_channel_capable

    @property
    def memory_mirroring_capable(self):
        return self._pattr_memory_mirroring_capable

    @property
    def micro_logical_partition_capable(self):
        return self._pattr_micro_logical_partition_capable

    @property
    def redundant_error_path_reporting_capable(self):
        return self._pattr_redundant_error_path_reporting_capable

    @property
    def remote_restart_toggle_capable(self):
        return self._pattr_remote_restart_toggle_capable

    @property
    def service_processor_concurrent_maintenance_capable(self):
        return self._pattr_service_processor_concurrent_maintenance_capable

    @property
    def service_processor_failover_capable(self):
        return self._pattr_service_processor_failover_capable

    @property
    def shared_ethernet_failover_capable(self):
        return self._pattr_shared_ethernet_failover_capable

    @property
    def shared_processor_pool_capable(self):
        return self._pattr_shared_processor_pool_capable

    @property
    def sriov_capable(self):
        return self._pattr_sriov_capable

    @property
    def switch_network_interface_message_passing_capable(self):
        return self._pattr_switch_network_interface_message_passing_capable

    @property
    def telnet5250_application_capable(self):
        return self._pattr_telnet5250_application_capable

    @property
    def turbo_core_capable(self):
        return self._pattr_turbo_core_capable

    @property
    def virtual_ethernet_adapter_dynamic_logical_partition_capable(self):
        return self._pattr_virtual_ethernet_adapter_dynamic_logical_partition_capable

    @property
    def virtual_ethernet_custom_mac_address_capable(self):
        return self._pattr_virtual_ethernet_custom_mac_address_capable

    @property
    def virtual_ethernet_quality_of_service_capable(self):
        return self._pattr_virtual_ethernet_quality_of_service_capable

    @property
    def virtual_fiber_channel_capable(self):
        return self._pattr_virtual_fiber_channel_capable

    @property
    def virtual_io_server_capable(self):
        return self._pattr_virtual_io_server_capable

    @property
    def virtual_server_networking_phase2_capable(self):
        return self._pattr_virtual_server_networking_phase2_capable

    @property
    def virtual_server_protection_capable(self):
        return self._pattr_virtual_server_protection_capable

    @property
    def virtual_switch_capable(self):
        return self._pattr_virtual_switch_capable

    @property
    def virtual_trusted_platform_module_capable(self):
        return self._pattr_virtual_trusted_platform_module_capable

    @property
    def virtualization_engine_technologies_activation_capable(self):
        return self._pattr_virtualization_engine_technologies_activation_capable

    @property
    def vlan_statistics_capable(self):
        return self._pattr_vlan_statistics_capable


class SystemIOConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_system_virtual_network = None
        self._pattr_available_wwp_ns = None
        self._pattr_host_channel_adapters = None
        self._pattr_host_ethernet_adapters = None
        self._pattr_io_adapters = None
        self._pattr_io_buses = None
        self._pattr_io_slots = None
        self._pattr_maximum_io_pools = None
        self._pattr_sriov_adapters = None
        self._pattr_wwpn_prefix = None
        super(SystemIOConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def associated_system_virtual_network(self):
        return self._pattr_associated_system_virtual_network
    @associated_system_virtual_network.setter
    def associated_system_virtual_network(self, value):
        self._modified_attrs.add("associated_system_virtual_network")
        self._pattr_associated_system_virtual_network = value

    @property
    def available_wwp_ns(self):
        return self._pattr_available_wwp_ns
    @available_wwp_ns.setter
    def available_wwp_ns(self, value):
        self._modified_attrs.add("available_wwp_ns")
        self._pattr_available_wwp_ns = value

    @property
    def host_channel_adapters(self):
        return self._pattr_host_channel_adapters
    @host_channel_adapters.setter
    def host_channel_adapters(self, value):
        self._modified_attrs.add("host_channel_adapters")
        self._pattr_host_channel_adapters = value

    @property
    def host_ethernet_adapters(self):
        return self._pattr_host_ethernet_adapters
    @host_ethernet_adapters.setter
    def host_ethernet_adapters(self, value):
        self._modified_attrs.add("host_ethernet_adapters")
        self._pattr_host_ethernet_adapters = value

    @property
    def io_adapters(self):
        return self._pattr_io_adapters
    @io_adapters.setter
    def io_adapters(self, value):
        self._modified_attrs.add("io_adapters")
        self._pattr_io_adapters = value

    @property
    def io_buses(self):
        return self._pattr_io_buses
    @io_buses.setter
    def io_buses(self, value):
        self._modified_attrs.add("io_buses")
        self._pattr_io_buses = value

    @property
    def io_slots(self):
        return self._pattr_io_slots
    @io_slots.setter
    def io_slots(self, value):
        self._modified_attrs.add("io_slots")
        self._pattr_io_slots = value

    @property
    def maximum_io_pools(self):
        return self._pattr_maximum_io_pools
    @maximum_io_pools.setter
    def maximum_io_pools(self, value):
        self._modified_attrs.add("maximum_io_pools")
        self._pattr_maximum_io_pools = value

    @property
    def sriov_adapters(self):
        return self._pattr_sriov_adapters
    @sriov_adapters.setter
    def sriov_adapters(self, value):
        self._modified_attrs.add("sriov_adapters")
        self._pattr_sriov_adapters = value

    @property
    def wwpn_prefix(self):
        return self._pattr_wwpn_prefix
    @wwpn_prefix.setter
    def wwpn_prefix(self, value):
        self._modified_attrs.add("wwpn_prefix")
        self._pattr_wwpn_prefix = value


class SystemMemoryConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_allowed_hardware_page_table_rations = []
        self._pattr_allowed_memory_deduplication_table_ratios = None
        self._pattr_allowed_memory_region_size = None
        self._pattr_available_barrier_synchronization_register_arrays = None
        self._pattr_barrier_synchronization_register_array_size = None
        self._pattr_configurable_huge_pages = None
        self._pattr_configurable_system_memory = None
        self._pattr_configured_mirrored_memory = None
        self._pattr_current_address_broadcast_policy = None
        self._pattr_current_available_huge_pages = None
        self._pattr_current_available_mirrored_memory = None
        self._pattr_current_available_system_memory = None
        self._pattr_current_logical_memory_block_size = None
        self._pattr_current_memory_mirroring_mode = None
        self._pattr_current_mirrored_memory = None
        self._pattr_deconfigured_system_memory = None
        self._pattr_default_hardware_page_table_ratio = None
        self._pattr_default_hardware_paging_table_ratio_for_dedicated_memory_partition = None
        self._pattr_default_memory_deduplication_table_ratio = None
        self._pattr_huge_page_count = None
        self._pattr_huge_page_size = None
        self._pattr_installed_system_memory = None
        self._pattr_maximum_huge_pages = None
        self._pattr_maximum_memory_pool_count = None
        self._pattr_maximum_mirrored_memory_defragmented = None
        self._pattr_maximum_paging_virtual_io_servers_per_shared_memory_pool = None
        self._pattr_memory_defragmentation_state = None
        self._pattr_memory_mirroring_state = None
        self._pattr_memory_region_size = None
        self._pattr_memory_used_by_hypervisor = None
        self._pattr_minimum_memory_pool_size = None
        self._pattr_minimum_required_memory_for_aix_and_linux = None
        self._pattr_minimum_required_memory_for_ibm_i = None
        self._pattr_minimum_required_memory_for_virtual_io_server = None
        self._pattr_mirrorable_memory_with_defragmentation = None
        self._pattr_mirrorable_memory_without_defragmentation = None
        self._pattr_mirrored_memory_used_by_hypervisor = None
        self._pattr_partition_maximum_memory_lower_limit = None
        self._pattr_pending_address_broadcast_policy = None
        self._pattr_pending_available_huge_pages = None
        self._pattr_pending_available_system_memory = None
        self._pattr_pending_logical_memory_block_size = None
        self._pattr_pending_memory_mirroring_mode = None
        self._pattr_pending_memory_region_size = None
        self._pattr_requested_huge_pages = None
        self._pattr_shared_memory_pool = None
        self._pattr_temporary_memory_for_logical_partition_mobility_in_use = None
        self._pattr_total_barrier_synchronization_register_arrays = None
        super(SystemMemoryConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def allowed_hardware_page_table_rations(self):
        return self._pattr_allowed_hardware_page_table_rations

    @property
    def allowed_memory_deduplication_table_ratios(self):
        return self._pattr_allowed_memory_deduplication_table_ratios

    @property
    def allowed_memory_region_size(self):
        return self._pattr_allowed_memory_region_size

    @property
    def available_barrier_synchronization_register_arrays(self):
        return self._pattr_available_barrier_synchronization_register_arrays

    @property
    def barrier_synchronization_register_array_size(self):
        return self._pattr_barrier_synchronization_register_array_size
    @barrier_synchronization_register_array_size.setter
    def barrier_synchronization_register_array_size(self, value):
        self._modified_attrs.add("barrier_synchronization_register_array_size")
        self._pattr_barrier_synchronization_register_array_size = value

    @property
    def configurable_huge_pages(self):
        return self._pattr_configurable_huge_pages

    @property
    def configurable_system_memory(self):
        return self._pattr_configurable_system_memory

    @property
    def configured_mirrored_memory(self):
        return self._pattr_configured_mirrored_memory
    @configured_mirrored_memory.setter
    def configured_mirrored_memory(self, value):
        self._modified_attrs.add("configured_mirrored_memory")
        self._pattr_configured_mirrored_memory = value

    @property
    def current_address_broadcast_policy(self):
        return self._pattr_current_address_broadcast_policy

    @property
    def current_available_huge_pages(self):
        return self._pattr_current_available_huge_pages

    @property
    def current_available_mirrored_memory(self):
        return self._pattr_current_available_mirrored_memory

    @property
    def current_available_system_memory(self):
        return self._pattr_current_available_system_memory

    @property
    def current_logical_memory_block_size(self):
        return self._pattr_current_logical_memory_block_size

    @property
    def current_memory_mirroring_mode(self):
        return self._pattr_current_memory_mirroring_mode

    @property
    def current_mirrored_memory(self):
        return self._pattr_current_mirrored_memory

    @property
    def deconfigured_system_memory(self):
        return self._pattr_deconfigured_system_memory
    @deconfigured_system_memory.setter
    def deconfigured_system_memory(self, value):
        self._modified_attrs.add("deconfigured_system_memory")
        self._pattr_deconfigured_system_memory = value

    @property
    def default_hardware_page_table_ratio(self):
        return self._pattr_default_hardware_page_table_ratio
    @default_hardware_page_table_ratio.setter
    def default_hardware_page_table_ratio(self, value):
        self._modified_attrs.add("default_hardware_page_table_ratio")
        self._pattr_default_hardware_page_table_ratio = value

    @property
    def default_hardware_paging_table_ratio_for_dedicated_memory_partition(self):
        return self._pattr_default_hardware_paging_table_ratio_for_dedicated_memory_partition
    @default_hardware_paging_table_ratio_for_dedicated_memory_partition.setter
    def default_hardware_paging_table_ratio_for_dedicated_memory_partition(self, value):
        self._modified_attrs.add("default_hardware_paging_table_ratio_for_dedicated_memory_partition")
        self._pattr_default_hardware_paging_table_ratio_for_dedicated_memory_partition = value

    @property
    def default_memory_deduplication_table_ratio(self):
        return self._pattr_default_memory_deduplication_table_ratio
    @default_memory_deduplication_table_ratio.setter
    def default_memory_deduplication_table_ratio(self, value):
        self._modified_attrs.add("default_memory_deduplication_table_ratio")
        self._pattr_default_memory_deduplication_table_ratio = value

    @property
    def huge_page_count(self):
        return self._pattr_huge_page_count
    @huge_page_count.setter
    def huge_page_count(self, value):
        self._modified_attrs.add("huge_page_count")
        self._pattr_huge_page_count = value

    @property
    def huge_page_size(self):
        return self._pattr_huge_page_size
    @huge_page_size.setter
    def huge_page_size(self, value):
        self._modified_attrs.add("huge_page_size")
        self._pattr_huge_page_size = value

    @property
    def installed_system_memory(self):
        return self._pattr_installed_system_memory

    @property
    def maximum_huge_pages(self):
        return self._pattr_maximum_huge_pages

    @property
    def maximum_memory_pool_count(self):
        return self._pattr_maximum_memory_pool_count

    @property
    def maximum_mirrored_memory_defragmented(self):
        return self._pattr_maximum_mirrored_memory_defragmented
    @maximum_mirrored_memory_defragmented.setter
    def maximum_mirrored_memory_defragmented(self, value):
        self._modified_attrs.add("maximum_mirrored_memory_defragmented")
        self._pattr_maximum_mirrored_memory_defragmented = value

    @property
    def maximum_paging_virtual_io_servers_per_shared_memory_pool(self):
        return self._pattr_maximum_paging_virtual_io_servers_per_shared_memory_pool

    @property
    def memory_defragmentation_state(self):
        return self._pattr_memory_defragmentation_state
    @memory_defragmentation_state.setter
    def memory_defragmentation_state(self, value):
        self._modified_attrs.add("memory_defragmentation_state")
        self._pattr_memory_defragmentation_state = value

    @property
    def memory_mirroring_state(self):
        return self._pattr_memory_mirroring_state
    @memory_mirroring_state.setter
    def memory_mirroring_state(self, value):
        self._modified_attrs.add("memory_mirroring_state")
        self._pattr_memory_mirroring_state = value

    @property
    def memory_region_size(self):
        return self._pattr_memory_region_size
    @memory_region_size.setter
    def memory_region_size(self, value):
        self._modified_attrs.add("memory_region_size")
        self._pattr_memory_region_size = value

    @property
    def memory_used_by_hypervisor(self):
        return self._pattr_memory_used_by_hypervisor

    @property
    def minimum_memory_pool_size(self):
        return self._pattr_minimum_memory_pool_size

    @property
    def minimum_required_memory_for_aix_and_linux(self):
        return self._pattr_minimum_required_memory_for_aix_and_linux

    @property
    def minimum_required_memory_for_ibm_i(self):
        return self._pattr_minimum_required_memory_for_ibm_i

    @property
    def minimum_required_memory_for_virtual_io_server(self):
        return self._pattr_minimum_required_memory_for_virtual_io_server

    @property
    def mirrorable_memory_with_defragmentation(self):
        return self._pattr_mirrorable_memory_with_defragmentation

    @property
    def mirrorable_memory_without_defragmentation(self):
        return self._pattr_mirrorable_memory_without_defragmentation

    @property
    def mirrored_memory_used_by_hypervisor(self):
        return self._pattr_mirrored_memory_used_by_hypervisor

    @property
    def partition_maximum_memory_lower_limit(self):
        return self._pattr_partition_maximum_memory_lower_limit

    @property
    def pending_address_broadcast_policy(self):
        return self._pattr_pending_address_broadcast_policy
    @pending_address_broadcast_policy.setter
    def pending_address_broadcast_policy(self, value):
        self._modified_attrs.add("pending_address_broadcast_policy")
        self._pattr_pending_address_broadcast_policy = value

    @property
    def pending_available_huge_pages(self):
        return self._pattr_pending_available_huge_pages
    @pending_available_huge_pages.setter
    def pending_available_huge_pages(self, value):
        self._modified_attrs.add("pending_available_huge_pages")
        self._pattr_pending_available_huge_pages = value

    @property
    def pending_available_system_memory(self):
        return self._pattr_pending_available_system_memory
    @pending_available_system_memory.setter
    def pending_available_system_memory(self, value):
        self._modified_attrs.add("pending_available_system_memory")
        self._pattr_pending_available_system_memory = value

    @property
    def pending_logical_memory_block_size(self):
        return self._pattr_pending_logical_memory_block_size
    @pending_logical_memory_block_size.setter
    def pending_logical_memory_block_size(self, value):
        self._modified_attrs.add("pending_logical_memory_block_size")
        self._pattr_pending_logical_memory_block_size = value

    @property
    def pending_memory_mirroring_mode(self):
        return self._pattr_pending_memory_mirroring_mode
    @pending_memory_mirroring_mode.setter
    def pending_memory_mirroring_mode(self, value):
        self._modified_attrs.add("pending_memory_mirroring_mode")
        self._pattr_pending_memory_mirroring_mode = value

    @property
    def pending_memory_region_size(self):
        return self._pattr_pending_memory_region_size
    @pending_memory_region_size.setter
    def pending_memory_region_size(self, value):
        self._modified_attrs.add("pending_memory_region_size")
        self._pattr_pending_memory_region_size = value

    @property
    def requested_huge_pages(self):
        return self._pattr_requested_huge_pages
    @requested_huge_pages.setter
    def requested_huge_pages(self, value):
        self._modified_attrs.add("requested_huge_pages")
        self._pattr_requested_huge_pages = value

    @property
    def shared_memory_pool(self):
        return self._pattr_shared_memory_pool
    @shared_memory_pool.setter
    def shared_memory_pool(self, value):
        self._modified_attrs.add("shared_memory_pool")
        self._pattr_shared_memory_pool = value

    @property
    def temporary_memory_for_logical_partition_mobility_in_use(self):
        return self._pattr_temporary_memory_for_logical_partition_mobility_in_use
    @temporary_memory_for_logical_partition_mobility_in_use.setter
    def temporary_memory_for_logical_partition_mobility_in_use(self, value):
        self._modified_attrs.add("temporary_memory_for_logical_partition_mobility_in_use")
        self._pattr_temporary_memory_for_logical_partition_mobility_in_use = value

    @property
    def total_barrier_synchronization_register_arrays(self):
        return self._pattr_total_barrier_synchronization_register_arrays


class SystemMigrationInformation(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_maximum_active_migrations = None
        self._pattr_maximum_firmware_active_migrations = None
        self._pattr_maximum_inactive_migrations = None
        self._pattr_number_of_active_migrations_in_progress = None
        self._pattr_number_of_inactive_migrations_in_progress = None
        super(SystemMigrationInformation,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def maximum_active_migrations(self):
        return self._pattr_maximum_active_migrations

    @property
    def maximum_firmware_active_migrations(self):
        return self._pattr_maximum_firmware_active_migrations

    @property
    def maximum_inactive_migrations(self):
        return self._pattr_maximum_inactive_migrations

    @property
    def number_of_active_migrations_in_progress(self):
        return self._pattr_number_of_active_migrations_in_progress

    @property
    def number_of_inactive_migrations_in_progress(self):
        return self._pattr_number_of_inactive_migrations_in_progress


class SystemProcessorConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_configurable_system_processor_units = None
        self._pattr_current_available_system_processor_units = None
        self._pattr_current_maximum_allowed_processors_per_partition = None
        self._pattr_current_maximum_processors_per_aix_or_linux_partition = None
        self._pattr_current_maximum_processors_per_ibm_i_partition = None
        self._pattr_current_maximum_processors_per_virtual_io_server_partition = None
        self._pattr_current_maximum_virtual_processors_per_aix_or_linux_partition = None
        self._pattr_current_maximum_virtual_processors_per_ibm_i_partition = None
        self._pattr_current_maximum_virtual_processors_per_virtual_io_server_partition = None
        self._pattr_deconfigured_system_processor_units = None
        self._pattr_installed_system_processor_units = None
        self._pattr_maximum_allowed_virtual_processors_per_partition = None
        self._pattr_maximum_processor_units_per_ibm_i_partition = None
        self._pattr_minimum_processor_units_per_virtual_processor = None
        self._pattr_number_of_all_os_processor_units = None
        self._pattr_number_of_linux_only_processor_units = None
        self._pattr_number_of_virtual_io_server_processor_units = None
        self._pattr_pending_available_system_processor_units = None
        self._pattr_shared_processor_pool = None
        self._pattr_shared_processor_pool_count = None
        self._pattr_supported_partition_processor_compatibility_modes = []
        self._pattr_temporary_processor_units_for_logical_partition_mobility_in_use = None
        self._pattr_turbo_core_support = None
        super(SystemProcessorConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def configurable_system_processor_units(self):
        return self._pattr_configurable_system_processor_units

    @property
    def current_available_system_processor_units(self):
        return self._pattr_current_available_system_processor_units

    @property
    def current_maximum_allowed_processors_per_partition(self):
        return self._pattr_current_maximum_allowed_processors_per_partition

    @property
    def current_maximum_processors_per_aix_or_linux_partition(self):
        return self._pattr_current_maximum_processors_per_aix_or_linux_partition

    @property
    def current_maximum_processors_per_ibm_i_partition(self):
        return self._pattr_current_maximum_processors_per_ibm_i_partition

    @property
    def current_maximum_processors_per_virtual_io_server_partition(self):
        return self._pattr_current_maximum_processors_per_virtual_io_server_partition

    @property
    def current_maximum_virtual_processors_per_aix_or_linux_partition(self):
        return self._pattr_current_maximum_virtual_processors_per_aix_or_linux_partition

    @property
    def current_maximum_virtual_processors_per_ibm_i_partition(self):
        return self._pattr_current_maximum_virtual_processors_per_ibm_i_partition

    @property
    def current_maximum_virtual_processors_per_virtual_io_server_partition(self):
        return self._pattr_current_maximum_virtual_processors_per_virtual_io_server_partition

    @property
    def deconfigured_system_processor_units(self):
        return self._pattr_deconfigured_system_processor_units

    @property
    def installed_system_processor_units(self):
        return self._pattr_installed_system_processor_units

    @property
    def maximum_allowed_virtual_processors_per_partition(self):
        return self._pattr_maximum_allowed_virtual_processors_per_partition

    @property
    def maximum_processor_units_per_ibm_i_partition(self):
        return self._pattr_maximum_processor_units_per_ibm_i_partition

    @property
    def minimum_processor_units_per_virtual_processor(self):
        return self._pattr_minimum_processor_units_per_virtual_processor

    @property
    def number_of_all_os_processor_units(self):
        return self._pattr_number_of_all_os_processor_units

    @property
    def number_of_linux_only_processor_units(self):
        return self._pattr_number_of_linux_only_processor_units

    @property
    def number_of_virtual_io_server_processor_units(self):
        return self._pattr_number_of_virtual_io_server_processor_units

    @property
    def pending_available_system_processor_units(self):
        return self._pattr_pending_available_system_processor_units
    @pending_available_system_processor_units.setter
    def pending_available_system_processor_units(self, value):
        self._modified_attrs.add("pending_available_system_processor_units")
        self._pattr_pending_available_system_processor_units = value

    @property
    def shared_processor_pool(self):
        return self._pattr_shared_processor_pool
    @shared_processor_pool.setter
    def shared_processor_pool(self, value):
        self._modified_attrs.add("shared_processor_pool")
        self._pattr_shared_processor_pool = value

    @property
    def shared_processor_pool_count(self):
        return self._pattr_shared_processor_pool_count

    @property
    def supported_partition_processor_compatibility_modes(self):
        return self._pattr_supported_partition_processor_compatibility_modes

    @property
    def temporary_processor_units_for_logical_partition_mobility_in_use(self):
        return self._pattr_temporary_processor_units_for_logical_partition_mobility_in_use

    @property
    def turbo_core_support(self):
        return self._pattr_turbo_core_support


class SystemSecurity(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_trusted_platform_module_key_length = None
        self._pattr_virtual_trusted_platform_module_key_status = None
        self._pattr_virtual_trusted_platform_module_key_status_flags = None
        self._pattr_virtual_trusted_platform_module_version = None
        super(SystemSecurity,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_trusted_platform_module_key_length(self):
        return self._pattr_virtual_trusted_platform_module_key_length

    @property
    def virtual_trusted_platform_module_key_status(self):
        return self._pattr_virtual_trusted_platform_module_key_status

    @property
    def virtual_trusted_platform_module_key_status_flags(self):
        return self._pattr_virtual_trusted_platform_module_key_status_flags

    @property
    def virtual_trusted_platform_module_version(self):
        return self._pattr_virtual_trusted_platform_module_version


class SystemVirtualNetwork(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_maximum_vla_ns_per_port = None
        self._pattr_network_bridges = None
        self._pattr_virtual_ethernet_adapter_mac_address_prefix = None
        self._pattr_virtual_networks = None
        self._pattr_virtual_switches = None
        super(SystemVirtualNetwork,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def maximum_vla_ns_per_port(self):
        return self._pattr_maximum_vla_ns_per_port
    @maximum_vla_ns_per_port.setter
    def maximum_vla_ns_per_port(self, value):
        self._modified_attrs.add("maximum_vla_ns_per_port")
        self._pattr_maximum_vla_ns_per_port = value

    @property
    def network_bridges(self):
        return self._pattr_network_bridges
    @network_bridges.setter
    def network_bridges(self, value):
        self._modified_attrs.add("network_bridges")
        self._pattr_network_bridges = value

    @property
    def virtual_ethernet_adapter_mac_address_prefix(self):
        return self._pattr_virtual_ethernet_adapter_mac_address_prefix
    @virtual_ethernet_adapter_mac_address_prefix.setter
    def virtual_ethernet_adapter_mac_address_prefix(self, value):
        self._modified_attrs.add("virtual_ethernet_adapter_mac_address_prefix")
        self._pattr_virtual_ethernet_adapter_mac_address_prefix = value

    @property
    def virtual_networks(self):
        return self._pattr_virtual_networks
    @virtual_networks.setter
    def virtual_networks(self, value):
        self._modified_attrs.add("virtual_networks")
        self._pattr_virtual_networks = value

    @property
    def virtual_switches(self):
        return self._pattr_virtual_switches
    @virtual_switches.setter
    def virtual_switches(self, value):
        self._modified_attrs.add("virtual_switches")
        self._pattr_virtual_switches = value


class SystemVirtualStorage(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_shared_storage_pools = None
        self._pattr_storage_pools = None
        self._pattr_virtual_media_repositories = None
        self._pattr_virtual_optical_devices = None
        super(SystemVirtualStorage,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def shared_storage_pools(self):
        return self._pattr_shared_storage_pools
    @shared_storage_pools.setter
    def shared_storage_pools(self, value):
        self._modified_attrs.add("shared_storage_pools")
        self._pattr_shared_storage_pools = value

    @property
    def storage_pools(self):
        return self._pattr_storage_pools
    @storage_pools.setter
    def storage_pools(self, value):
        self._modified_attrs.add("storage_pools")
        self._pattr_storage_pools = value

    @property
    def virtual_media_repositories(self):
        return self._pattr_virtual_media_repositories
    @virtual_media_repositories.setter
    def virtual_media_repositories(self, value):
        self._modified_attrs.add("virtual_media_repositories")
        self._pattr_virtual_media_repositories = value

    @property
    def virtual_optical_devices(self):
        return self._pattr_virtual_optical_devices
    @virtual_optical_devices.setter
    def virtual_optical_devices(self, value):
        self._modified_attrs.add("virtual_optical_devices")
        self._pattr_virtual_optical_devices = value


class SystemVirtualStorage_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_system_virtual_storage = []
        super(SystemVirtualStorage_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def system_virtual_storage(self):
        return self._pattr_system_virtual_storage
    @system_virtual_storage.setter
    def system_virtual_storage(self, value):
        self._modified_attrs.add("system_virtual_storage")
        self._pattr_system_virtual_storage = value


class TrunkAdapter(VirtualEthernetAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_trunk_priority = None
        super(TrunkAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def trunk_priority(self):
        return self._pattr_trunk_priority
    @trunk_priority.setter
    def trunk_priority(self, value):
        self._modified_attrs.add("trunk_priority")
        self._pattr_trunk_priority = value


class TrunkAdapter_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_trunk_adapter = []
        super(TrunkAdapter_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def trunk_adapter(self):
        return self._pattr_trunk_adapter
    @trunk_adapter.setter
    def trunk_adapter(self, value):
        self._modified_attrs.add("trunk_adapter")
        self._pattr_trunk_adapter = value


class VersionReleaseMaintenance(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_build_level = None
        self._pattr_maintenance = None
        self._pattr_minor = None
        self._pattr_release = None
        self._pattr_service_pack_name = None
        self._pattr_version = None
        self._pattr_version_date = None
        super(VersionReleaseMaintenance,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def build_level(self):
        return self._pattr_build_level
    @build_level.setter
    def build_level(self, value):
        self._modified_attrs.add("build_level")
        self._pattr_build_level = value

    @property
    def maintenance(self):
        return self._pattr_maintenance
    @maintenance.setter
    def maintenance(self, value):
        self._modified_attrs.add("maintenance")
        self._pattr_maintenance = value

    @property
    def minor(self):
        return self._pattr_minor
    @minor.setter
    def minor(self, value):
        self._modified_attrs.add("minor")
        self._pattr_minor = value

    @property
    def release(self):
        return self._pattr_release
    @release.setter
    def release(self, value):
        self._modified_attrs.add("release")
        self._pattr_release = value

    @property
    def service_pack_name(self):
        return self._pattr_service_pack_name
    @service_pack_name.setter
    def service_pack_name(self, value):
        self._modified_attrs.add("service_pack_name")
        self._pattr_service_pack_name = value

    @property
    def version(self):
        return self._pattr_version
    @version.setter
    def version(self, value):
        self._modified_attrs.add("version")
        self._pattr_version = value

    @property
    def version_date(self):
        return self._pattr_version_date
    @version_date.setter
    def version_date(self, value):
        self._modified_attrs.add("version_date")
        self._pattr_version_date = value


class VirtualDisk(VirtualSCSIStorage):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_disk_capacity = None
        self._pattr_disk_label = None
        self._pattr_disk_name = None
        self._pattr_max_logical_volumes = None
        self._pattr_partition_size = None
        self._pattr_unique_device_id = None
        self._pattr_volume_group = None
        super(VirtualDisk,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def disk_capacity(self):
        return self._pattr_disk_capacity
    @disk_capacity.setter
    def disk_capacity(self, value):
        self._modified_attrs.add("disk_capacity")
        self._pattr_disk_capacity = value

    @property
    def disk_label(self):
        return self._pattr_disk_label
    @disk_label.setter
    def disk_label(self, value):
        self._modified_attrs.add("disk_label")
        self._pattr_disk_label = value

    @property
    def disk_name(self):
        return self._pattr_disk_name
    @disk_name.setter
    def disk_name(self, value):
        self._modified_attrs.add("disk_name")
        self._pattr_disk_name = value

    @property
    def max_logical_volumes(self):
        return self._pattr_max_logical_volumes
    @max_logical_volumes.setter
    def max_logical_volumes(self, value):
        self._modified_attrs.add("max_logical_volumes")
        self._pattr_max_logical_volumes = value

    @property
    def partition_size(self):
        return self._pattr_partition_size
    @partition_size.setter
    def partition_size(self, value):
        self._modified_attrs.add("partition_size")
        self._pattr_partition_size = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def volume_group(self):
        return self._pattr_volume_group


class VirtualDisk_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_disk = []
        super(VirtualDisk_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_disk(self):
        return self._pattr_virtual_disk
    @virtual_disk.setter
    def virtual_disk(self, value):
        self._modified_attrs.add("virtual_disk")
        self._pattr_virtual_disk = value


class VirtualEnvironmentConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_active_memory_sharing = None
        self._pattr_partition_mobility = None
        self._pattr_remote_restart = None
        self._pattr_suspend_resume = None
        self._pattr_uses_shared_storage_pool = None
        super(VirtualEnvironmentConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def active_memory_sharing(self):
        return self._pattr_active_memory_sharing
    @active_memory_sharing.setter
    def active_memory_sharing(self, value):
        self._modified_attrs.add("active_memory_sharing")
        self._pattr_active_memory_sharing = value

    @property
    def partition_mobility(self):
        return self._pattr_partition_mobility
    @partition_mobility.setter
    def partition_mobility(self, value):
        self._modified_attrs.add("partition_mobility")
        self._pattr_partition_mobility = value

    @property
    def remote_restart(self):
        return self._pattr_remote_restart
    @remote_restart.setter
    def remote_restart(self, value):
        self._modified_attrs.add("remote_restart")
        self._pattr_remote_restart = value

    @property
    def suspend_resume(self):
        return self._pattr_suspend_resume
    @suspend_resume.setter
    def suspend_resume(self, value):
        self._modified_attrs.add("suspend_resume")
        self._pattr_suspend_resume = value

    @property
    def uses_shared_storage_pool(self):
        return self._pattr_uses_shared_storage_pool
    @uses_shared_storage_pool.setter
    def uses_shared_storage_pool(self, value):
        self._modified_attrs.add("uses_shared_storage_pool")
        self._pattr_uses_shared_storage_pool = value


class VirtualFibreChannelAdapter(VirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_name = None
        self._pattr_connecting_partition = None
        self._pattr_connecting_partition_id = None
        self._pattr_connecting_virtual_slot_number = None
        self._pattr_unique_device_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualFibreChannelAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def adapter_name(self):
        return self._pattr_adapter_name
    @adapter_name.setter
    def adapter_name(self, value):
        self._modified_attrs.add("adapter_name")
        self._pattr_adapter_name = value

    @property
    def connecting_partition(self):
        return self._pattr_connecting_partition
    @connecting_partition.setter
    def connecting_partition(self, value):
        self._modified_attrs.add("connecting_partition")
        self._pattr_connecting_partition = value

    @property
    def connecting_partition_id(self):
        return self._pattr_connecting_partition_id
    @connecting_partition_id.setter
    def connecting_partition_id(self, value):
        self._modified_attrs.add("connecting_partition_id")
        self._pattr_connecting_partition_id = value

    @property
    def connecting_virtual_slot_number(self):
        return self._pattr_connecting_virtual_slot_number
    @connecting_virtual_slot_number.setter
    def connecting_virtual_slot_number(self, value):
        self._modified_attrs.add("connecting_virtual_slot_number")
        self._pattr_connecting_virtual_slot_number = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id
    @unique_device_id.setter
    def unique_device_id(self, value):
        self._modified_attrs.add("unique_device_id")
        self._pattr_unique_device_id = value


class VirtualFibreChannelClientAdapter(VirtualFibreChannelAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_nport_logged_in_status = None
        self._pattr_server_adapter = None
        self._pattr_wwp_ns = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualFibreChannelClientAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def nport_logged_in_status(self):
        return self._pattr_nport_logged_in_status
    @nport_logged_in_status.setter
    def nport_logged_in_status(self, value):
        self._modified_attrs.add("nport_logged_in_status")
        self._pattr_nport_logged_in_status = value

    @property
    def server_adapter(self):
        return self._pattr_server_adapter
    @server_adapter.setter
    def server_adapter(self, value):
        self._modified_attrs.add("server_adapter")
        self._pattr_server_adapter = value

    @property
    def wwp_ns(self):
        return self._pattr_wwp_ns
    @wwp_ns.setter
    def wwp_ns(self, value):
        self._modified_attrs.add("wwp_ns")
        self._pattr_wwp_ns = value


class VirtualFibreChannelClientAdapter_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VirtualFibreChannelClientAdapter_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VirtualFibreChannelMapping(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_logical_partition = None
        self._pattr_client_adapter = None
        self._pattr_port = None
        self._pattr_server_adapter = None
        super(VirtualFibreChannelMapping,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def associated_logical_partition(self):
        return self._pattr_associated_logical_partition
    @associated_logical_partition.setter
    def associated_logical_partition(self, value):
        self._modified_attrs.add("associated_logical_partition")
        self._pattr_associated_logical_partition = value

    @property
    def client_adapter(self):
        return self._pattr_client_adapter
    @client_adapter.setter
    def client_adapter(self, value):
        self._modified_attrs.add("client_adapter")
        self._pattr_client_adapter = value

    @property
    def port(self):
        return self._pattr_port
    @port.setter
    def port(self, value):
        self._modified_attrs.add("port")
        self._pattr_port = value

    @property
    def server_adapter(self):
        return self._pattr_server_adapter
    @server_adapter.setter
    def server_adapter(self, value):
        self._modified_attrs.add("server_adapter")
        self._pattr_server_adapter = value


class VirtualFibreChannelMapping_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_fibre_channel_mapping = []
        super(VirtualFibreChannelMapping_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_fibre_channel_mapping(self):
        return self._pattr_virtual_fibre_channel_mapping
    @virtual_fibre_channel_mapping.setter
    def virtual_fibre_channel_mapping(self, value):
        self._modified_attrs.add("virtual_fibre_channel_mapping")
        self._pattr_virtual_fibre_channel_mapping = value


class VirtualFibreChannelNPortLoginStatus(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_logged_in_by = None
        self._pattr_status_reason = None
        self._pattr_wwpn = None
        self._pattr_wwpn_status = None
        super(VirtualFibreChannelNPortLoginStatus,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def logged_in_by(self):
        return self._pattr_logged_in_by

    @property
    def status_reason(self):
        return self._pattr_status_reason

    @property
    def wwpn(self):
        return self._pattr_wwpn

    @property
    def wwpn_status(self):
        return self._pattr_wwpn_status
    @wwpn_status.setter
    def wwpn_status(self, value):
        self._modified_attrs.add("wwpn_status")
        self._pattr_wwpn_status = value


class VirtualFibreChannelNPortLoginStatus_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_fibre_channel_n_port_login_status = []
        super(VirtualFibreChannelNPortLoginStatus_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_fibre_channel_n_port_login_status(self):
        return self._pattr_virtual_fibre_channel_n_port_login_status
    @virtual_fibre_channel_n_port_login_status.setter
    def virtual_fibre_channel_n_port_login_status(self, value):
        self._modified_attrs.add("virtual_fibre_channel_n_port_login_status")
        self._pattr_virtual_fibre_channel_n_port_login_status = value


class VirtualFibreChannelServerAdapter(VirtualFibreChannelAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_map_port = None
        self._pattr_physical_port = None
        super(VirtualFibreChannelServerAdapter,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def map_port(self):
        return self._pattr_map_port
    @map_port.setter
    def map_port(self, value):
        self._modified_attrs.add("map_port")
        self._pattr_map_port = value

    @property
    def physical_port(self):
        return self._pattr_physical_port
    @physical_port.setter
    def physical_port(self, value):
        self._modified_attrs.add("physical_port")
        self._pattr_physical_port = value


class VirtualIOServer(BasePartition):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_api_capable = None
        self._pattr_free_ethenet_backing_devices_for_sea = None
        self._pattr_free_io_adapters_for_link_aggregation = None
        self._pattr_link_aggregations = None
        self._pattr_manager_passthrough_capable = None
        self._pattr_media_repositories = None
        self._pattr_mover_service_partition = None
        self._pattr_network_boot_devices = None
        self._pattr_paging_service_partition = None
        self._pattr_physical_volumes = None
        self._pattr_server_install_configuration = None
        self._pattr_shared_ethernet_adapters = None
        self._pattr_shared_storage_pool_capable = None
        self._pattr_shared_storage_pool_version = None
        self._pattr_storage_pools = None
        self._pattr_trunk_adapters = None
        self._pattr_virtual_fibre_channel_mappings = None
        self._pattr_virtual_io_server_license = None
        self._pattr_virtual_io_server_license_accepted = None
        self._pattr_virtual_scsi_mappings = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualIOServer,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def api_capable(self):
        return self._pattr_api_capable
    @api_capable.setter
    def api_capable(self, value):
        self._modified_attrs.add("api_capable")
        self._pattr_api_capable = value

    @property
    def free_ethenet_backing_devices_for_sea(self):
        return self._pattr_free_ethenet_backing_devices_for_sea

    @property
    def free_io_adapters_for_link_aggregation(self):
        return self._pattr_free_io_adapters_for_link_aggregation

    @property
    def link_aggregations(self):
        return self._pattr_link_aggregations
    @link_aggregations.setter
    def link_aggregations(self, value):
        self._modified_attrs.add("link_aggregations")
        self._pattr_link_aggregations = value

    @property
    def manager_passthrough_capable(self):
        return self._pattr_manager_passthrough_capable
    @manager_passthrough_capable.setter
    def manager_passthrough_capable(self, value):
        self._modified_attrs.add("manager_passthrough_capable")
        self._pattr_manager_passthrough_capable = value

    @property
    def media_repositories(self):
        return self._pattr_media_repositories
    @media_repositories.setter
    def media_repositories(self, value):
        self._modified_attrs.add("media_repositories")
        self._pattr_media_repositories = value

    @property
    def mover_service_partition(self):
        return self._pattr_mover_service_partition
    @mover_service_partition.setter
    def mover_service_partition(self, value):
        self._modified_attrs.add("mover_service_partition")
        self._pattr_mover_service_partition = value

    @property
    def network_boot_devices(self):
        return self._pattr_network_boot_devices
    @network_boot_devices.setter
    def network_boot_devices(self, value):
        self._modified_attrs.add("network_boot_devices")
        self._pattr_network_boot_devices = value

    @property
    def paging_service_partition(self):
        return self._pattr_paging_service_partition
    @paging_service_partition.setter
    def paging_service_partition(self, value):
        self._modified_attrs.add("paging_service_partition")
        self._pattr_paging_service_partition = value

    @property
    def physical_volumes(self):
        return self._pattr_physical_volumes
    @physical_volumes.setter
    def physical_volumes(self, value):
        self._modified_attrs.add("physical_volumes")
        self._pattr_physical_volumes = value

    @property
    def server_install_configuration(self):
        return self._pattr_server_install_configuration
    @server_install_configuration.setter
    def server_install_configuration(self, value):
        self._modified_attrs.add("server_install_configuration")
        self._pattr_server_install_configuration = value

    @property
    def shared_ethernet_adapters(self):
        return self._pattr_shared_ethernet_adapters
    @shared_ethernet_adapters.setter
    def shared_ethernet_adapters(self, value):
        self._modified_attrs.add("shared_ethernet_adapters")
        self._pattr_shared_ethernet_adapters = value

    @property
    def shared_storage_pool_capable(self):
        return self._pattr_shared_storage_pool_capable
    @shared_storage_pool_capable.setter
    def shared_storage_pool_capable(self, value):
        self._modified_attrs.add("shared_storage_pool_capable")
        self._pattr_shared_storage_pool_capable = value

    @property
    def shared_storage_pool_version(self):
        return self._pattr_shared_storage_pool_version
    @shared_storage_pool_version.setter
    def shared_storage_pool_version(self, value):
        self._modified_attrs.add("shared_storage_pool_version")
        self._pattr_shared_storage_pool_version = value

    @property
    def storage_pools(self):
        return self._pattr_storage_pools
    @storage_pools.setter
    def storage_pools(self, value):
        self._modified_attrs.add("storage_pools")
        self._pattr_storage_pools = value

    @property
    def trunk_adapters(self):
        return self._pattr_trunk_adapters
    @trunk_adapters.setter
    def trunk_adapters(self, value):
        self._modified_attrs.add("trunk_adapters")
        self._pattr_trunk_adapters = value

    @property
    def virtual_fibre_channel_mappings(self):
        return self._pattr_virtual_fibre_channel_mappings
    @virtual_fibre_channel_mappings.setter
    def virtual_fibre_channel_mappings(self, value):
        self._modified_attrs.add("virtual_fibre_channel_mappings")
        self._pattr_virtual_fibre_channel_mappings = value

    @property
    def virtual_io_server_license(self):
        return self._pattr_virtual_io_server_license

    @property
    def virtual_io_server_license_accepted(self):
        return self._pattr_virtual_io_server_license_accepted
    @virtual_io_server_license_accepted.setter
    def virtual_io_server_license_accepted(self, value):
        self._modified_attrs.add("virtual_io_server_license_accepted")
        self._pattr_virtual_io_server_license_accepted = value

    @property
    def virtual_scsi_mappings(self):
        return self._pattr_virtual_scsi_mappings
    @virtual_scsi_mappings.setter
    def virtual_scsi_mappings(self, value):
        self._modified_attrs.add("virtual_scsi_mappings")
        self._pattr_virtual_scsi_mappings = value


class VirtualIOServerInstallConfiguration(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_address = None
        self._pattr_boot_device = None
        self._pattr_boot_mac_address = None
        self._pattr_configured_duplex_mode = None
        self._pattr_configured_speed = None
        self._pattr_gateway = None
        self._pattr_image_source = None
        self._pattr_installation_type = None
        self._pattr_management_console_nic = None
        self._pattr_network_install_manager_address = None
        self._pattr_subnet_mask = None
        super(VirtualIOServerInstallConfiguration,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def address(self):
        return self._pattr_address
    @address.setter
    def address(self, value):
        self._modified_attrs.add("address")
        self._pattr_address = value

    @property
    def boot_device(self):
        return self._pattr_boot_device
    @boot_device.setter
    def boot_device(self, value):
        self._modified_attrs.add("boot_device")
        self._pattr_boot_device = value

    @property
    def boot_mac_address(self):
        return self._pattr_boot_mac_address
    @boot_mac_address.setter
    def boot_mac_address(self, value):
        self._modified_attrs.add("boot_mac_address")
        self._pattr_boot_mac_address = value

    @property
    def configured_duplex_mode(self):
        return self._pattr_configured_duplex_mode
    @configured_duplex_mode.setter
    def configured_duplex_mode(self, value):
        self._modified_attrs.add("configured_duplex_mode")
        self._pattr_configured_duplex_mode = value

    @property
    def configured_speed(self):
        return self._pattr_configured_speed
    @configured_speed.setter
    def configured_speed(self, value):
        self._modified_attrs.add("configured_speed")
        self._pattr_configured_speed = value

    @property
    def gateway(self):
        return self._pattr_gateway
    @gateway.setter
    def gateway(self, value):
        self._modified_attrs.add("gateway")
        self._pattr_gateway = value

    @property
    def image_source(self):
        return self._pattr_image_source
    @image_source.setter
    def image_source(self, value):
        self._modified_attrs.add("image_source")
        self._pattr_image_source = value

    @property
    def installation_type(self):
        return self._pattr_installation_type
    @installation_type.setter
    def installation_type(self, value):
        self._modified_attrs.add("installation_type")
        self._pattr_installation_type = value

    @property
    def management_console_nic(self):
        return self._pattr_management_console_nic
    @management_console_nic.setter
    def management_console_nic(self, value):
        self._modified_attrs.add("management_console_nic")
        self._pattr_management_console_nic = value

    @property
    def network_install_manager_address(self):
        return self._pattr_network_install_manager_address
    @network_install_manager_address.setter
    def network_install_manager_address(self, value):
        self._modified_attrs.add("network_install_manager_address")
        self._pattr_network_install_manager_address = value

    @property
    def subnet_mask(self):
        return self._pattr_subnet_mask
    @subnet_mask.setter
    def subnet_mask(self, value):
        self._modified_attrs.add("subnet_mask")
        self._pattr_subnet_mask = value


class VirtualIOServer_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VirtualIOServer_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VirtualMediaRepository(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_optical_media = None
        self._pattr_repository_name = None
        self._pattr_repository_size = None
        super(VirtualMediaRepository,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def optical_media(self):
        return self._pattr_optical_media
    @optical_media.setter
    def optical_media(self, value):
        self._modified_attrs.add("optical_media")
        self._pattr_optical_media = value

    @property
    def repository_name(self):
        return self._pattr_repository_name
    @repository_name.setter
    def repository_name(self, value):
        self._modified_attrs.add("repository_name")
        self._pattr_repository_name = value

    @property
    def repository_size(self):
        return self._pattr_repository_size
    @repository_size.setter
    def repository_size(self, value):
        self._modified_attrs.add("repository_size")
        self._pattr_repository_size = value


class VirtualMediaRepository_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_media_repository = []
        super(VirtualMediaRepository_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_media_repository(self):
        return self._pattr_virtual_media_repository
    @virtual_media_repository.setter
    def virtual_media_repository(self, value):
        self._modified_attrs.add("virtual_media_repository")
        self._pattr_virtual_media_repository = value


class VirtualNetwork(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_switch = None
        self._pattr_network_name = None
        self._pattr_network_vlan_id = None
        self._pattr_tagged_network = None
        self._pattr_vswitch_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualNetwork,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def associated_switch(self):
        return self._pattr_associated_switch
    @associated_switch.setter
    def associated_switch(self, value):
        self._modified_attrs.add("associated_switch")
        self._pattr_associated_switch = value

    @property
    def network_name(self):
        return self._pattr_network_name
    @network_name.setter
    def network_name(self, value):
        self._modified_attrs.add("network_name")
        self._pattr_network_name = value

    @property
    def network_vlan_id(self):
        return self._pattr_network_vlan_id
    @network_vlan_id.setter
    def network_vlan_id(self, value):
        self._modified_attrs.add("network_vlan_id")
        self._pattr_network_vlan_id = value

    @property
    def tagged_network(self):
        return self._pattr_tagged_network
    @tagged_network.setter
    def tagged_network(self, value):
        self._modified_attrs.add("tagged_network")
        self._pattr_tagged_network = value

    @property
    def vswitch_id(self):
        return self._pattr_vswitch_id


class VirtualNetwork_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VirtualNetwork_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VirtualOpticalMedia(VirtualSCSIStorage):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_media_name = None
        self._pattr_media_udid = None
        self._pattr_mount_type = None
        self._pattr_size = None
        super(VirtualOpticalMedia,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def media_name(self):
        return self._pattr_media_name
    @media_name.setter
    def media_name(self, value):
        self._modified_attrs.add("media_name")
        self._pattr_media_name = value

    @property
    def media_udid(self):
        return self._pattr_media_udid

    @property
    def mount_type(self):
        return self._pattr_mount_type
    @mount_type.setter
    def mount_type(self, value):
        self._modified_attrs.add("mount_type")
        self._pattr_mount_type = value

    @property
    def size(self):
        return self._pattr_size
    @size.setter
    def size(self, value):
        self._modified_attrs.add("size")
        self._pattr_size = value


class VirtualOpticalMedia_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_optical_media = []
        super(VirtualOpticalMedia_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_optical_media(self):
        return self._pattr_virtual_optical_media
    @virtual_optical_media.setter
    def virtual_optical_media(self, value):
        self._modified_attrs.add("virtual_optical_media")
        self._pattr_virtual_optical_media = value


class VirtualOpticalTargetDevice(VirtualTargetDevice):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_optical_media = None
        super(VirtualOpticalTargetDevice,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_optical_media(self):
        return self._pattr_virtual_optical_media
    @virtual_optical_media.setter
    def virtual_optical_media(self, value):
        self._modified_attrs.add("virtual_optical_media")
        self._pattr_virtual_optical_media = value


class VirtualOpticalTargetDevice_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_optical_target_device = []
        super(VirtualOpticalTargetDevice_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_optical_target_device(self):
        return self._pattr_virtual_optical_target_device
    @virtual_optical_target_device.setter
    def virtual_optical_target_device(self, value):
        self._modified_attrs.add("virtual_optical_target_device")
        self._pattr_virtual_optical_target_device = value


class VirtualSCSIAdapter(VirtualIOAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_adapter_name = None
        self._pattr_backing_device_name = None
        self._pattr_remote_backing_device_name = None
        self._pattr_remote_logical_partition_id = None
        self._pattr_remote_slot_number = None
        self._pattr_server_location_code = None
        self._pattr_unique_device_id = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualSCSIAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def adapter_name(self):
        return self._pattr_adapter_name
    @adapter_name.setter
    def adapter_name(self, value):
        self._modified_attrs.add("adapter_name")
        self._pattr_adapter_name = value

    @property
    def backing_device_name(self):
        return self._pattr_backing_device_name
    @backing_device_name.setter
    def backing_device_name(self, value):
        self._modified_attrs.add("backing_device_name")
        self._pattr_backing_device_name = value

    @property
    def remote_backing_device_name(self):
        return self._pattr_remote_backing_device_name
    @remote_backing_device_name.setter
    def remote_backing_device_name(self, value):
        self._modified_attrs.add("remote_backing_device_name")
        self._pattr_remote_backing_device_name = value

    @property
    def remote_logical_partition_id(self):
        return self._pattr_remote_logical_partition_id
    @remote_logical_partition_id.setter
    def remote_logical_partition_id(self, value):
        self._modified_attrs.add("remote_logical_partition_id")
        self._pattr_remote_logical_partition_id = value

    @property
    def remote_slot_number(self):
        return self._pattr_remote_slot_number
    @remote_slot_number.setter
    def remote_slot_number(self, value):
        self._modified_attrs.add("remote_slot_number")
        self._pattr_remote_slot_number = value

    @property
    def server_location_code(self):
        return self._pattr_server_location_code
    @server_location_code.setter
    def server_location_code(self, value):
        self._modified_attrs.add("server_location_code")
        self._pattr_server_location_code = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id


class VirtualSCSIClientAdapter(VirtualSCSIAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_server_adapter = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualSCSIClientAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def server_adapter(self):
        return self._pattr_server_adapter
    @server_adapter.setter
    def server_adapter(self, value):
        self._modified_attrs.add("server_adapter")
        self._pattr_server_adapter = value


class VirtualSCSIClientAdapter_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VirtualSCSIClientAdapter_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VirtualSCSIMapping(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_associated_logical_partition = None
        self._pattr_client_adapter = None
        self._pattr_server_adapter = None
        self._pattr_storage = None
        self._pattr_target_device = None
        super(VirtualSCSIMapping,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def associated_logical_partition(self):
        return self._pattr_associated_logical_partition
    @associated_logical_partition.setter
    def associated_logical_partition(self, value):
        self._modified_attrs.add("associated_logical_partition")
        self._pattr_associated_logical_partition = value

    @property
    def client_adapter(self):
        return self._pattr_client_adapter
    @client_adapter.setter
    def client_adapter(self, value):
        self._modified_attrs.add("client_adapter")
        self._pattr_client_adapter = value

    @property
    def server_adapter(self):
        return self._pattr_server_adapter
    @server_adapter.setter
    def server_adapter(self, value):
        self._modified_attrs.add("server_adapter")
        self._pattr_server_adapter = value

    @property
    def storage(self):
        return self._pattr_storage
    @storage.setter
    def storage(self, value):
        self._modified_attrs.add("storage")
        self._pattr_storage = value

    @property
    def target_device(self):
        return self._pattr_target_device
    @target_device.setter
    def target_device(self, value):
        self._modified_attrs.add("target_device")
        self._pattr_target_device = value


class VirtualSCSIMapping_Collection(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_virtual_scsi_mapping = []
        super(VirtualSCSIMapping_Collection,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def virtual_scsi_mapping(self):
        return self._pattr_virtual_scsi_mapping
    @virtual_scsi_mapping.setter
    def virtual_scsi_mapping(self, value):
        self._modified_attrs.add("virtual_scsi_mapping")
        self._pattr_virtual_scsi_mapping = value


class VirtualSCSIServerAdapter(VirtualSCSIAdapter):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_dummy = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualSCSIServerAdapter,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def dummy(self):
        return self._pattr_dummy
    @dummy.setter
    def dummy(self, value):
        self._modified_attrs.add("dummy")
        self._pattr_dummy = value


class VirtualSwitch(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_switch_id = None
        self._pattr_switch_mode = None
        self._pattr_switch_name = None
        self._pattr_virtual_networks = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VirtualSwitch,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def switch_id(self):
        return self._pattr_switch_id

    @property
    def switch_mode(self):
        return self._pattr_switch_mode
    @switch_mode.setter
    def switch_mode(self, value):
        self._modified_attrs.add("switch_mode")
        self._pattr_switch_mode = value

    @property
    def switch_name(self):
        return self._pattr_switch_name
    @switch_name.setter
    def switch_name(self, value):
        self._modified_attrs.add("switch_name")
        self._pattr_switch_name = value

    @property
    def virtual_networks(self):
        return self._pattr_virtual_networks
    @virtual_networks.setter
    def virtual_networks(self, value):
        self._modified_attrs.add("virtual_networks")
        self._pattr_virtual_networks = value


class VirtualSwitch_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VirtualSwitch_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value


class VolumeGroup(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_available_size = None
        self._pattr_backing_device_count = None
        self._pattr_free_space = None
        self._pattr_group_capacity = None
        self._pattr_group_name = None
        self._pattr_group_serial_id = None
        self._pattr_group_state = None
        self._pattr_maximum_logical_volumes = None
        self._pattr_media_repositories = None
        self._pattr_minimum_allocation_size = None
        self._pattr_physical_volumes = None
        self._pattr_unique_device_id = None
        self._pattr_virtual_disks = None

        # root-specific
        self._id = None
        self._api = None
        self._k2entry = None
        self._k2resp = None
        self._k2resp_isfor_k2entry = None
        super(VolumeGroup,
              self).__init__()

    def loadAsRoot(self, manager, k2entry, k2resp, k2resp_isfor_k2entry):
        self._api = manager
        self._k2entry = k2entry
        self._k2resp = k2resp
        self._k2resp_isfor_k2entry = k2resp_isfor_k2entry
        manager.api.k2loader.process_root("uom", self, k2entry.element)
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
    def available_size(self):
        return self._pattr_available_size

    @property
    def backing_device_count(self):
        return self._pattr_backing_device_count
    @backing_device_count.setter
    def backing_device_count(self, value):
        self._modified_attrs.add("backing_device_count")
        self._pattr_backing_device_count = value

    @property
    def free_space(self):
        return self._pattr_free_space

    @property
    def group_capacity(self):
        return self._pattr_group_capacity
    @group_capacity.setter
    def group_capacity(self, value):
        self._modified_attrs.add("group_capacity")
        self._pattr_group_capacity = value

    @property
    def group_name(self):
        return self._pattr_group_name
    @group_name.setter
    def group_name(self, value):
        self._modified_attrs.add("group_name")
        self._pattr_group_name = value

    @property
    def group_serial_id(self):
        return self._pattr_group_serial_id

    @property
    def group_state(self):
        return self._pattr_group_state

    @property
    def maximum_logical_volumes(self):
        return self._pattr_maximum_logical_volumes

    @property
    def media_repositories(self):
        return self._pattr_media_repositories
    @media_repositories.setter
    def media_repositories(self, value):
        self._modified_attrs.add("media_repositories")
        self._pattr_media_repositories = value

    @property
    def minimum_allocation_size(self):
        return self._pattr_minimum_allocation_size
    @minimum_allocation_size.setter
    def minimum_allocation_size(self, value):
        self._modified_attrs.add("minimum_allocation_size")
        self._pattr_minimum_allocation_size = value

    @property
    def physical_volumes(self):
        return self._pattr_physical_volumes
    @physical_volumes.setter
    def physical_volumes(self, value):
        self._modified_attrs.add("physical_volumes")
        self._pattr_physical_volumes = value

    @property
    def unique_device_id(self):
        return self._pattr_unique_device_id

    @property
    def virtual_disks(self):
        return self._pattr_virtual_disks
    @virtual_disks.setter
    def virtual_disks(self, value):
        self._modified_attrs.add("virtual_disks")
        self._pattr_virtual_disks = value


class VolumeGroup_Links(K2Resource):
    def __init__(self):

        self._pattr_metadata = None

        self._pattr_link = []
        super(VolumeGroup_Links,
              self).__init__()

    @property
    def metadata(self):
        return self._pattr_metadata

    @property
    def link(self):
        return self._pattr_link
    @link.setter
    def link(self, value):
        self._modified_attrs.add("link")
        self._pattr_link = value

_k2dict_json = """{
    "BasePartition": {
        "ClientNetworkAdapters": "ClientNetworkAdapter_Links",
        "HostEthernetAdapterLogicalPorts": "HostEthernetAdapterLogicalPort_Collection",
        "PartitionCapabilities": "LogicalPartitionCapabilities",
        "PartitionIOConfiguration": "LogicalPartitionIOConfiguration",
        "PartitionMemoryConfiguration": "LogicalPartitionMemoryConfiguration",
        "PartitionProcessorConfiguration": "LogicalPartitionProcessorConfiguration",
        "PartitionProfiles": "LogicalPartitionProfile_Links",
        "SRIOVEthernetLogicalPorts": "SRIOVEthernetLogicalPort_Links",
        "SRIOVFibreChannelOverEthernetLogicalPorts": "SRIOVFibreChannelOverEthernetLogicalPort_Links"
    },
    "Cage": {
        "IOUnits": "IOUnit_Collection",
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber",
        "ManagedSystems": "ManagedSystem_Links",
        "OwnerMachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber"
    },
    "ClientNetworkAdapter": {
        "AssociatedVirtualSwitch": "VirtualSwitch_Links",
        "VirtualNetworks": "VirtualNetwork_Links"
    },
    "Cluster": {
        "Node": "Node_Collection",
        "RepositoryDisk": "PhysicalVolume_Collection"
    },
    "EthernetBackingDevice": {
        "IPInterface": "IPInterface"
    },
    "Event": {},
    "HostChannelAdapter": {
        "Capability": "HostChannelAdapterBandwidthCapability"
    },
    "HostChannelAdapterBandwidthCapability": {},
    "HostEthernetAdapter": {
        "PortGroups": "HostEthernetAdapterPortGroup_Collection"
    },
    "HostEthernetAdapterLogicalPort": {
        "IPInterface": "IPInterface"
    },
    "HostEthernetAdapterPhysicalPort": {},
    "HostEthernetAdapterPortGroup": {
        "LogicalPorts": "HostEthernetAdapterLogicalPort_Collection",
        "PhysicalPorts": "HostEthernetAdapterPhysicalPort_Collection"
    },
    "IBMiIOSlot": {},
    "IBMiProfileTaggedIO": {},
    "IOAdapter": {},
    "IOBus": {
        "IOSlots": "IOSlot_Collection"
    },
    "IOSlot": {
        "RelatedIBMiIOSlot": "IBMiIOSlot"
    },
    "IOUnit": {
        "IOBuses": "IOBus_Collection",
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber"
    },
    "IPInterface": {},
    "IPLConfiguration": {},
    "LinkAggregation": {
        "IOAdapters": "IOAdapterChoiceCollection",
        "IPInterface": "IPInterface"
    },
    "LoadGroup": {
        "TrunkAdapters": "TrunkAdapter_Collection",
        "VirtualNetworks": "VirtualNetwork_Links"
    },
    "LogicalPartition": {
        "ClientNetworkAdapters": "ClientNetworkAdapter_Links",
        "HostEthernetAdapterLogicalPorts": "HostEthernetAdapterLogicalPort_Collection",
        "PartitionCapabilities": "LogicalPartitionCapabilities",
        "PartitionIOConfiguration": "LogicalPartitionIOConfiguration",
        "PartitionMemoryConfiguration": "LogicalPartitionMemoryConfiguration",
        "PartitionProcessorConfiguration": "LogicalPartitionProcessorConfiguration",
        "PartitionProfiles": "LogicalPartitionProfile_Links",
        "SRIOVEthernetLogicalPorts": "SRIOVEthernetLogicalPort_Links",
        "SRIOVFibreChannelOverEthernetLogicalPorts": "SRIOVFibreChannelOverEthernetLogicalPort_Links",
        "VirtualFibreChannelClientAdapters": "VirtualFibreChannelClientAdapter_Links",
        "VirtualSCSIClientAdapters": "VirtualSCSIClientAdapter_Links"
    },
    "LogicalPartitionCapabilities": {},
    "LogicalPartitionDedicatedProcessorConfiguration": {},
    "LogicalPartitionIOConfiguration": {
        "HostChannelAdapters": "HostChannelAdapter_Collection",
        "ProfileIOSlots": "ProfileIOSlot_Collection",
        "ProfileVirtualIOAdapters": "ProfileVirtualIOAdapterChoiceCollection",
        "TaggedIO": "IBMiProfileTaggedIO"
    },
    "LogicalPartitionMemoryConfiguration": {},
    "LogicalPartitionProcessorConfiguration": {
        "CurrentDedicatedProcessorConfiguration": "LogicalPartitionDedicatedProcessorConfiguration",
        "CurrentSharedProcessorConfiguration": "LogicalPartitionSharedProcessorConfiguration",
        "DedicatedProcessorConfiguration": "LogicalPartitionProfileDedicatedProcessorConfiguration",
        "SharedProcessorConfiguration": "LogicalPartitionProfileSharedProcessorConfiguration"
    },
    "LogicalPartitionProfile": {
        "HostEthernetAdapterLogicalPorts": "HostEthernetAdapterLogicalPort_Collection",
        "IOConfigurationInstance": "LogicalPartitionProfileIOConfiguration",
        "PowerControlPartitions": "BasePartition_Links",
        "ProcessorAttributes": "LogicalPartitionProfileProcessorConfiguration",
        "ProfileMemory": "LogicalPartitionProfileMemoryConfiguration",
        "ProfileSRIOVEthernetLogicalPorts": "ProfileSRIOVEthernetLogicalPort_Collection"
    },
    "LogicalPartitionProfileDedicatedProcessorConfiguration": {},
    "LogicalPartitionProfileIOConfiguration": {
        "HostChannelAdapters": "HostChannelAdapter_Collection",
        "ProfileIOSlots": "ProfileIOSlot_Collection",
        "ProfileVirtualIOAdapters": "ProfileVirtualIOAdapterChoiceCollection",
        "TaggedIO": "IBMiProfileTaggedIO"
    },
    "LogicalPartitionProfileMemoryConfiguration": {},
    "LogicalPartitionProfileProcessorConfiguration": {
        "DedicatedProcessorConfiguration": "LogicalPartitionProfileDedicatedProcessorConfiguration",
        "SharedProcessorConfiguration": "LogicalPartitionProfileSharedProcessorConfiguration"
    },
    "LogicalPartitionProfileSharedProcessorConfiguration": {},
    "LogicalPartitionSharedProcessorConfiguration": {},
    "LogicalUnit": {},
    "LogicalVolumeVirtualTargetDevice": {},
    "MachineTypeModelSerialNumber": {},
    "ManagedFrame": {
        "Cages": "Cage_Collection",
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber"
    },
    "ManagedSystem": {
        "AssociatedIPLConfiguration": "IPLConfiguration",
        "AssociatedLogicalPartitions": "LogicalPartition_Links",
        "AssociatedReservedStorageDevicePool": "ReservedStorageDevicePool_Links",
        "AssociatedSystemCapabilities": "SystemCapabilities",
        "AssociatedSystemIOConfiguration": "SystemIOConfiguration",
        "AssociatedSystemMemoryConfiguration": "SystemMemoryConfiguration",
        "AssociatedSystemProcessorConfiguration": "SystemProcessorConfiguration",
        "AssociatedSystemSecurity": "SystemSecurity",
        "AssociatedSystemVirtualStorage": "SystemVirtualStorage_Collection",
        "AssociatedVirtualEnvironmentConfiguration": "VirtualEnvironmentConfiguration",
        "AssociatedVirtualIOServers": "VirtualIOServer_Links",
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber",
        "SystemMigrationInformation": "SystemMigrationInformation"
    },
    "ManagementConsole": {
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber",
        "ManagedFrames": "ManagedFrame_Links",
        "ManagedSystems": "ManagedSystem_Links",
        "NetworkInterfaces": "ManagementConsoleNetworkInterface_Collection",
        "PowerEnterprisePools": "PowerEnterprisePool_Links",
        "TemplateObjectModelVersion": "SchemaVersion",
        "UserObjectModelVersion": "SchemaVersion",
        "VersionInfo": "VersionReleaseMaintenance",
        "WebObjectModelVersion": "SchemaVersion"
    },
    "ManagementConsoleNetworkInterface": {},
    "NetworkBootDevice": {},
    "NetworkBridge": {
        "LoadGroups": "LoadGroup_Collection",
        "SharedEthernetAdapters": "SharedEthernetAdapter_Collection",
        "VirtualNetworks": "VirtualNetwork_Links"
    },
    "Node": {
        "MachineTypeModelAndSerialNumber": "MachineTypeModelSerialNumber"
    },
    "PhysicalFibreChannelAdapter": {
        "PhysicalFibreChannelPorts": "PhysicalFibreChannelPort_Collection"
    },
    "PhysicalFibreChannelPort": {
        "PhysicalVolumes": "PhysicalVolume_Collection"
    },
    "PhysicalVolume": {},
    "PhysicalVolumeVirtualTargetDevice": {},
    "PowerEnterprisePool": {
        "PowerEnterprisePoolManagementConsoles": "PowerEnterprisePoolManagementConsole_Collection",
        "PowerEnterprisePoolMembers": "PowerEnterprisePoolMember_Links"
    },
    "PowerEnterprisePoolManagementConsole": {
        "ManagementConsoleMachineTypeModelSerialNumber": "MachineTypeModelSerialNumber"
    },
    "PowerEnterprisePoolMember": {
        "ManagedSystemMachineTypeModelSerialNumber": "MachineTypeModelSerialNumber"
    },
    "ProfileClientNetworkAdapter": {},
    "ProfileIOSlot": {
        "AssociatedIOSlot": "IOSlot"
    },
    "ProfileSRIOVConfiguredLogicalPort": {},
    "ProfileSRIOVEthernetLogicalPort": {},
    "ProfileTrunkAdapter": {},
    "ProfileVirtualEthernetAdapter": {},
    "ProfileVirtualFibreChannelAdapter": {},
    "ProfileVirtualFibreChannelClientAdapter": {},
    "ProfileVirtualFibreChannelServerAdapter": {},
    "ProfileVirtualIOAdapter": {},
    "ProfileVirtualSCSIAdapter": {},
    "ProfileVirtualSCSIClientAdapter": {},
    "ProfileVirtualSCSIServerAdapter": {},
    "ReservedStorageDevice": {},
    "ReservedStorageDevicePool": {
        "FreeMemoryDevicesFromPagingServicePartitionOne": "ReservedStorageDevice_Collection",
        "FreeMemoryDevicesFromPagingServicePartitionTwo": "ReservedStorageDevice_Collection",
        "FreeRedundantMemoryDevices": "ReservedStorageDevice_Collection",
        "PagingDevices": "ReservedStorageDevice_Collection"
    },
    "SRIOVAdapter": {
        "ConvergedEthernetPhysicalPorts": "SRIOVConvergedNetworkAdapterPhysicalPort_Collection",
        "EthernetLogicalPorts": "SRIOVEthernetLogicalPort_Links",
        "EthernetPhysicalPorts": "SRIOVEthernetPhysicalPort_Collection",
        "FibreChannelOverEthernetLogicalPorts": "SRIOVFibreChannelOverEthernetLogicalPort_Links",
        "UnconfiguredLogicalPorts": "SRIOVUnconfiguredLogicalPort_Collection"
    },
    "SRIOVConfiguredLogicalPort": {},
    "SRIOVConvergedNetworkAdapterPhysicalPort": {},
    "SRIOVEthernetLogicalPort": {},
    "SRIOVEthernetPhysicalPort": {},
    "SRIOVFibreChannelOverEthernetLogicalPort": {},
    "SRIOVPhysicalPort": {},
    "SRIOVUnconfiguredLogicalPort": {},
    "SchemaVersion": {},
    "SharedEthernetAdapter": {
        "IPInterface": "IPInterface",
        "TrunkAdapters": "TrunkAdapter_Collection"
    },
    "SharedMemoryPool": {
        "FreeMemoryDevicesFromPagingServicePartitionOne": "ReservedStorageDevice_Collection",
        "FreeMemoryDevicesFromPagingServicePartitionTwo": "ReservedStorageDevice_Collection",
        "FreeRedundantMemoryDevices": "ReservedStorageDevice_Collection",
        "PagingDevices": "ReservedStorageDevice_Collection"
    },
    "SharedProcessorPool": {
        "AssignedPartitions": "BasePartition_Links"
    },
    "SharedStoragePool": {
        "LogicalUnits": "LogicalUnit_Collection",
        "PhysicalVolumes": "PhysicalVolume_Collection"
    },
    "SharedStoragePoolLogicalUnitVirtualTargetDevice": {},
    "SystemCapabilities": {},
    "SystemIOConfiguration": {
        "AssociatedSystemVirtualNetwork": "SystemVirtualNetwork",
        "HostChannelAdapters": "HostChannelAdapter_Collection",
        "HostEthernetAdapters": "HostEthernetAdapter_Links",
        "IOAdapters": "IOAdapterChoiceCollection",
        "IOBuses": "IOBus_Collection",
        "IOSlots": "IOSlot_Collection",
        "SRIOVAdapters": "IOAdapterChoiceCollection"
    },
    "SystemMemoryConfiguration": {
        "SharedMemoryPool": "SharedMemoryPool_Links"
    },
    "SystemMigrationInformation": {},
    "SystemProcessorConfiguration": {
        "SharedProcessorPool": "SharedProcessorPool_Links"
    },
    "SystemSecurity": {},
    "SystemVirtualNetwork": {
        "NetworkBridges": "NetworkBridge_Links",
        "VirtualNetworks": "VirtualNetwork_Links",
        "VirtualSwitches": "VirtualSwitch_Links"
    },
    "SystemVirtualStorage": {
        "SharedStoragePools": "SharedStoragePool_Links",
        "StoragePools": "VolumeGroup_Links",
        "VirtualMediaRepositories": "VirtualMediaRepository_Collection",
        "VirtualOpticalDevices": "VirtualOpticalTargetDevice_Collection"
    },
    "TrunkAdapter": {
        "AssociatedVirtualSwitch": "VirtualSwitch_Links"
    },
    "VersionReleaseMaintenance": {},
    "VirtualDisk": {},
    "VirtualEnvironmentConfiguration": {},
    "VirtualEthernetAdapter": {
        "AssociatedVirtualSwitch": "VirtualSwitch_Links"
    },
    "VirtualFibreChannelAdapter": {},
    "VirtualFibreChannelClientAdapter": {
        "NportLoggedInStatus": "VirtualFibreChannelNPortLoginStatus_Collection",
        "ServerAdapter": "VirtualFibreChannelServerAdapter"
    },
    "VirtualFibreChannelMapping": {
        "ClientAdapter": "VirtualFibreChannelClientAdapter",
        "Port": "PhysicalFibreChannelPort",
        "ServerAdapter": "VirtualFibreChannelServerAdapter"
    },
    "VirtualFibreChannelNPortLoginStatus": {},
    "VirtualFibreChannelServerAdapter": {
        "PhysicalPort": "PhysicalFibreChannelPort"
    },
    "VirtualIOAdapter": {},
    "VirtualIOServer": {
        "ClientNetworkAdapters": "ClientNetworkAdapter_Links",
        "FreeEthenetBackingDevicesForSEA": "IOAdapterChoiceCollection",
        "FreeIOAdaptersForLinkAggregation": "IOAdapterChoiceCollection",
        "HostEthernetAdapterLogicalPorts": "HostEthernetAdapterLogicalPort_Collection",
        "LinkAggregations": "LinkAggregation_Links",
        "MediaRepositories": "VirtualMediaRepository_Collection",
        "NetworkBootDevices": "NetworkBootDevice_Collection",
        "PartitionCapabilities": "LogicalPartitionCapabilities",
        "PartitionIOConfiguration": "LogicalPartitionIOConfiguration",
        "PartitionMemoryConfiguration": "LogicalPartitionMemoryConfiguration",
        "PartitionProcessorConfiguration": "LogicalPartitionProcessorConfiguration",
        "PartitionProfiles": "LogicalPartitionProfile_Links",
        "PhysicalVolumes": "PhysicalVolume_Collection",
        "SRIOVEthernetLogicalPorts": "SRIOVEthernetLogicalPort_Links",
        "SRIOVFibreChannelOverEthernetLogicalPorts": "SRIOVFibreChannelOverEthernetLogicalPort_Links",
        "ServerInstallConfiguration": "VirtualIOServerInstallConfiguration",
        "SharedEthernetAdapters": "SharedEthernetAdapter_Collection",
        "SharedStoragePoolVersion": "VersionReleaseMaintenance",
        "StoragePools": "VolumeGroup_Links",
        "TrunkAdapters": "TrunkAdapter_Collection",
        "VirtualFibreChannelMappings": "VirtualFibreChannelMapping_Collection",
        "VirtualSCSIMappings": "VirtualSCSIMapping_Collection"
    },
    "VirtualIOServerInstallConfiguration": {},
    "VirtualMediaRepository": {
        "OpticalMedia": "VirtualOpticalMedia_Collection"
    },
    "VirtualNetwork": {},
    "VirtualOpticalMedia": {},
    "VirtualOpticalTargetDevice": {
        "VirtualOpticalMedia": "VirtualOpticalMedia_Collection"
    },
    "VirtualSCSIAdapter": {},
    "VirtualSCSIClientAdapter": {
        "ServerAdapter": "VirtualSCSIServerAdapter"
    },
    "VirtualSCSIMapping": {
        "ClientAdapter": "VirtualSCSIClientAdapter",
        "ServerAdapter": "VirtualSCSIServerAdapter"
    },
    "VirtualSCSIServerAdapter": {},
    "VirtualSCSIStorage": {},
    "VirtualSwitch": {
        "VirtualNetworks": "VirtualNetwork_Links"
    },
    "VirtualTargetDevice": {},
    "VolumeGroup": {
        "MediaRepositories": "VirtualMediaRepository_Collection",
        "PhysicalVolumes": "PhysicalVolume_Collection",
        "VirtualDisks": "VirtualDisk_Collection"
    }
}"""
k2dict = json.loads(_k2dict_json)
_k2attr_json = """{
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
    "BasePartition": [
        null,
        [
            [
                "allow_performance_data_collection",
                "AllowPerformanceDataCollection",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_partition_profile",
                "AssociatedPartitionProfile",
                "link rel=LogicalPartitionProfile",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "availability_priority",
                "AvailabilityPriority",
                "int",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "current_allocated_barrier_synchronization_register_arrays",
                "CurrentAllocatedBarrierSynchronizationRegisterArrays",
                "int",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "current_processor_compatibility_mode",
                "CurrentProcessorCompatibilityMode",
                "LogicalPartitionProcessorCompatibilityMode.Enum",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "current_profile_sync",
                "CurrentProfileSync",
                "CurrentProfileSync.Enum",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "hostname",
                "Hostname",
                "string",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "is_call_home_enabled",
                "IsCallHomeEnabled",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "is_connection_monitoring_enabled",
                "IsConnectionMonitoringEnabled",
                "boolean",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "is_operation_in_progress",
                "IsOperationInProgress",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "is_redundant_error_path_reporting_enabled",
                "IsRedundantErrorPathReportingEnabled",
                "boolean",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "is_time_reference_partition",
                "IsTimeReferencePartition",
                "boolean",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "is_virtual_service_attention_led_on",
                "IsVirtualServiceAttentionLEDOn",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "is_virtual_trusted_platform_module_enabled",
                "IsVirtualTrustedPlatformModuleEnabled",
                "boolean",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "keylock_position",
                "KeylockPosition",
                "KeylockPosition.Enum",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "logical_serial_number",
                "LogicalSerialNumber",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "operating_system_version",
                "OperatingSystemVersion",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "partition_capabilities",
                "PartitionCapabilities",
                "LogicalPartitionCapabilities.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "partition_id",
                "PartitionID",
                "int",
                "co",
                "d",
                "R",
                ""
            ],
            [
                "partition_io_configuration",
                "PartitionIOConfiguration",
                "LogicalPartitionIOConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "partition_memory_configuration",
                "PartitionMemoryConfiguration",
                "LogicalPartitionMemoryConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "partition_name",
                "PartitionName",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "partition_processor_configuration",
                "PartitionProcessorConfiguration",
                "LogicalPartitionProcessorConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "partition_profiles",
                "PartitionProfiles",
                "LogicalPartitionProfile_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "partition_state",
                "PartitionState",
                "LogicalPartitionState.Enum",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "partition_type",
                "PartitionType",
                "LogicalPartitionEnvironment.Enum",
                "co",
                "d",
                "R",
                ""
            ],
            [
                "partition_uuid",
                "PartitionUUID",
                "UUID.Pattern",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "pending_processor_compatibility_mode",
                "PendingProcessorCompatibilityMode",
                "LogicalPartitionProcessorCompatibilityMode.Enum",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "processor_pool",
                "ProcessorPool",
                "link rel=SharedProcessorPool",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "progress_partition_data_remaining",
                "ProgressPartitionDataRemaining",
                "Megabyte.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "progress_partition_data_total",
                "ProgressPartitionDataTotal",
                "Megabyte.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "progress_state",
                "ProgressState",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "resource_monitoring_control_state",
                "ResourceMonitoringControlState",
                "ResourceMonitoringControlState.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "resource_monitoring_ip_address",
                "ResourceMonitoringIPAddress",
                "IPAddress.Union",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "valid_interactive_performance",
                "ValidInteractivePerformance",
                "Range.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_managed_system",
                "AssociatedManagedSystem",
                "link rel=ManagedSystem",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "sriov_ethernet_logical_ports",
                "SRIOVEthernetLogicalPorts",
                "SRIOVEthernetLogicalPort_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "sriov_fibre_channel_over_ethernet_logical_ports",
                "SRIOVFibreChannelOverEthernetLogicalPorts",
                "SRIOVFibreChannelOverEthernetLogicalPort_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "client_network_adapters",
                "ClientNetworkAdapters",
                "ClientNetworkAdapter_Links.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "host_ethernet_adapter_logical_ports",
                "HostEthernetAdapterLogicalPorts",
                "HostEthernetAdapterLogicalPort_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "mac_address_prefix",
                "MACAddressPrefix",
                "MACAddress.Pattern",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "is_service_partition",
                "IsServicePartition",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "reference_code",
                "ReferenceCode",
                "string",
                "ro",
                "o",
                "R",
                ""
            ]
        ]
    ],
    "BasePartition_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "Cage": [
        null,
        [
            [
                "cage_id",
                "CageID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "cage_location",
                "CageLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "frame_location",
                "FrameLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_units",
                "IOUnits",
                "IOUnit_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "managed_systems",
                "ManagedSystems",
                "ManagedSystem_Links.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "owner_location",
                "OwnerLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "owner_machine_type_model_and_serial_number",
                "OwnerMachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "Cage_Collection": [
        null,
        [
            [
                "cage",
                "Cage",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ClientNetworkAdapter": [
        "VirtualEthernetAdapter",
        [
            [
                "virtual_networks",
                "VirtualNetworks",
                "VirtualNetwork_Links.Type",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "ClientNetworkAdapter_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "Cluster": [
        null,
        [
            [
                "cluster_name",
                "ClusterName",
                "string",
                "co",
                "r",
                "R",
                ""
            ],
            [
                "cluster_id",
                "ClusterID",
                "UDID.Pattern",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "repository_disk",
                "RepositoryDisk",
                "PhysicalVolume_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "cluster_shared_storage_pool",
                "ClusterSharedStoragePool",
                "link rel=SharedStoragePool",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "node",
                "Node",
                "Node_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ]
        ]
    ],
    "EthernetBackingDevice": [
        "IOAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ip_interface",
                "IPInterface",
                "IPInterface.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "Event": [
        null,
        [
            [
                "event_type",
                "EventType",
                "EventType.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "event_id",
                "EventID",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "event_data",
                "EventData",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "event_detail",
                "EventDetail",
                "string",
                "ro",
                "r",
                "R",
                ""
            ]
        ]
    ],
    "HostChannelAdapter": [
        "IOAdapter",
        [
            [
                "allocation_allowed",
                "AllocationAllowed",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "assigned_uui_ds",
                "AssignedUUIDs",
                "HCAGuid.List",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "cable_type",
                "CableType",
                "HostChannelAdapterCableType.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "capability",
                "Capability",
                "HostChannelAdapterBandwidthCapability.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_functional",
                "IsFunctional",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "physical_location_code",
                "PhysicalLocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unassigned_gui_ds",
                "UnassignedGUIDs",
                "HCAGuid.List",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "uuid_list_sequential",
                "UUIDListSequential",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "HostChannelAdapterBandwidthCapability": [
        null,
        [
            [
                "high_percentage",
                "HighPercentage",
                "float",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "low_percentage",
                "LowPercentage",
                "float",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "medium_percentage",
                "MediumPercentage",
                "float",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "HostChannelAdapter_Collection": [
        null,
        [
            [
                "host_channel_adapter",
                "HostChannelAdapter",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "HostEthernetAdapter": [
        null,
        [
            [
                "adapter_id",
                "AdapterID",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "adapter_state",
                "AdapterState",
                "FunctionalState.Enum",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "physical_location_code",
                "PhysicalLocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "port_groups",
                "PortGroups",
                "HostEthernetAdapterPortGroup_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterLogicalPort": [
        "EthernetBackingDevice",
        [
            [
                "allowed_osmac_addresses",
                "AllowedOSMACAddresses",
                "AllowedMACAddresses.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "allowed_vlani_ds",
                "AllowedVLANIDs",
                "AllowedVLANIDs.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "logical_port_id",
                "LogicalPortID",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "mac_address",
                "MACAddress",
                "MACAddress.Pattern",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "mac_address_directives",
                "MACAddressDirectives",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "partition_link",
                "PartitionLink",
                "link rel=BasePartition",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_id",
                "PhysicalPortID",
                "HostEthernetPhysicalPortID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "port_group_id",
                "PortGroupID",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "port_state",
                "PortState",
                "HostEthernetAdapterLogicalPortState.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "hea_logical_port_physical_location",
                "HEALogicalPortPhysicalLocation",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterLogicalPort_Collection": [
        null,
        [
            [
                "host_ethernet_adapter_logical_port",
                "HostEthernetAdapterLogicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterPhysicalPort": [
        null,
        [
            [
                "current_connection_speed",
                "CurrentConnectionSpeed",
                "ConnectionSpeed.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "current_duplex_mode",
                "CurrentDuplexMode",
                "DuplexMode.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "link_up",
                "LinkUp",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_receive_packet_size",
                "MaximumReceivePacketSize",
                "EthernetFrameSize.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "pending_connection_speed",
                "PendingConnectionSpeed",
                "ConnectionSpeed.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_duplex_mode",
                "PendingDuplexMode",
                "DuplexMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_flow_control_enabled",
                "PendingFlowControlEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "physical_port_id",
                "PhysicalPortID",
                "HostEthernetPhysicalPortID.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_location_code",
                "PhysicalPortLocationCode",
                "PhysicalLocation.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_state",
                "PhysicalPortState",
                "FunctionalState.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_type",
                "PhysicalPortType",
                "HostEthernetAdapterPhysicalPortType.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "receive_flow_control_enabled",
                "ReceiveFlowControlEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "transmit_flow_control_enabled",
                "TransmitFlowControlEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "dedicated",
                "Dedicated",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "owner",
                "Owner",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "partition_link",
                "PartitionLink",
                "link rel=BasePartition",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterPhysicalPort_Collection": [
        null,
        [
            [
                "host_ethernet_adapter_physical_port",
                "HostEthernetAdapterPhysicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterPortGroup": [
        null,
        [
            [
                "port_group_id",
                "PortGroupID",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "current_multi_core_scaling",
                "CurrentMultiCoreScaling",
                "MultiCoreScalingValue.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "pending_multi_core_scaling",
                "PendingMultiCoreScaling",
                "MultiCoreScalingValue.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "supported_multi_core_scaling_values",
                "SupportedMultiCoreScalingValues",
                "MultiCoreScalingValue.List",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "logical_ports",
                "LogicalPorts",
                "HostEthernetAdapterLogicalPort_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "physical_ports",
                "PhysicalPorts",
                "HostEthernetAdapterPhysicalPort_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "HostEthernetAdapterPortGroup_Collection": [
        null,
        [
            [
                "host_ethernet_adapter_port_group",
                "HostEthernetAdapterPortGroup",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "HostEthernetAdapter_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "IBMiIOSlot": [
        null,
        [
            [
                "alternate_load_source_attached",
                "AlternateLoadSourceAttached",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "console_capable",
                "ConsoleCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "direct_operations_console_capable",
                "DirectOperationsConsoleCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "iop",
                "IOP",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "iop_info_stale",
                "IOPInfoStale",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_pool_id",
                "IOPoolID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "lan_console_capable",
                "LANConsoleCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "load_source_attached",
                "LoadSourceAttached",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "load_source_capable",
                "LoadSourceCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "operations_console_attached",
                "OperationsConsoleAttached",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "operations_console_capable",
                "OperationsConsoleCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "IBMiProfileTaggedIO": [
        null,
        [
            [
                "alternate_console",
                "AlternateConsole",
                "DynamicReconfigurationConnectorIndex.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "alternate_load_source",
                "AlternateLoadSource",
                "OptionalPhysicalOrVirtualSlotIndex.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "console",
                "Console",
                "ConsolePhysicalOrVirtualSlotIndex.Union",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "load_source",
                "LoadSource",
                "RequiredPhysicalOrVirtualSlotIndex.Union",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "operations_console",
                "OperationsConsole",
                "DynamicReconfigurationConnectorIndex.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "IOAdapter": [
        null,
        [
            [
                "adapter_id",
                "AdapterID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "description",
                "Description",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "device_type",
                "DeviceType",
                "IOAdapterType.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "dynamic_reconfiguration_connector_name",
                "DynamicReconfigurationConnectorName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "physical_location",
                "PhysicalLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "IOAdapterChoiceCollection": [
        null,
        [
            [
                "io_adapter_choice",
                "IOAdapterChoice",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "IOBus": [
        null,
        [
            [
                "backplane_physical_location",
                "BackplanePhysicalLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "bus_dynamic_reconfiguration_connector_index",
                "BusDynamicReconfigurationConnectorIndex",
                "DynamicReconfigurationConnectorIndex.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "bus_dynamic_reconfiguration_connector_name",
                "BusDynamicReconfigurationConnectorName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_bus_id",
                "IOBusID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_slots",
                "IOSlots",
                "IOSlot_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "IOBus_Collection": [
        null,
        [
            [
                "io_bus",
                "IOBus",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "IOSlot": [
        null,
        [
            [
                "bus_grouping_required",
                "BusGroupingRequired",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "description",
                "Description",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "feature_codes",
                "FeatureCodes",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "io_unit_physical_location",
                "IOUnitPhysicalLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "parent_slot_dynamic_reconfiguration_connector_index",
                "ParentSlotDynamicReconfigurationConnectorIndex",
                "DynamicReconfigurationConnectorIndex.Type",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pc_adapter_id",
                "PCAdapterID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_class",
                "PCIClass",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_device_id",
                "PCIDeviceID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_subsystem_device_id",
                "PCISubsystemDeviceID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_manufacturer_id",
                "PCIManufacturerID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_revision_id",
                "PCIRevisionID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_vendor_id",
                "PCIVendorID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "pci_subsystem_vendor_id",
                "PCISubsystemVendorID",
                "int",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "related_ibm_i_io_slot",
                "RelatedIBMiIOSlot",
                "IBMiIOSlot.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "related_io_adapter",
                "RelatedIOAdapter",
                "IOAdapterChoice.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "slot_dynamic_reconfiguration_connector_index",
                "SlotDynamicReconfigurationConnectorIndex",
                "DynamicReconfigurationConnectorIndex.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "slot_dynamic_reconfiguration_connector_name",
                "SlotDynamicReconfigurationConnectorName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "slot_physical_location_code",
                "SlotPhysicalLocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "twinaxial_attached",
                "TwinaxialAttached",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "twinaxial_capable",
                "TwinaxialCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "vital_product_data_model",
                "VitalProductDataModel",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "vital_product_data_serial_number",
                "VitalProductDataSerialNumber",
                "string",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "vital_product_data_stale",
                "VitalProductDataStale",
                "VitalProductDataStale.Enum",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "vital_product_data_type",
                "VitalProductDataType",
                "string",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "IOSlot_Collection": [
        null,
        [
            [
                "io_slot",
                "IOSlot",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "IOUnit": [
        null,
        [
            [
                "io_buses",
                "IOBuses",
                "IOBus_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_unit_id",
                "IOUnitID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_unit_physical_location",
                "IOUnitPhysicalLocation",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "io_unit_system_power_control_network_id",
                "IOUnitSystemPowerControlNetworkID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "IOUnit_Collection": [
        null,
        [
            [
                "io_unit",
                "IOUnit",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "IPInterface": [
        null,
        [
            [
                "interface_name",
                "InterfaceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ip_address",
                "IPAddress",
                "IPAddress.List",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "subnet_mask",
                "SubnetMask",
                "IPAddress.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "state",
                "State",
                "IPInterfaceState.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ipv6_prefix",
                "IPV6Prefix",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "gateway",
                "Gateway",
                "IPAddress.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "host_name",
                "HostName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "IPLConfiguration": [
        null,
        [
            [
                "current_manufacturing_defaul_configurationt_boot_mode",
                "CurrentManufacturingDefaulConfigurationtBootMode",
                "PartitionBootMode.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_power_on_side",
                "CurrentPowerOnSide",
                "ServiceProcessorSide.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_system_keylock",
                "CurrentSystemKeylock",
                "KeylockPosition.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_turbocore_enabled",
                "CurrentTurbocoreEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "major_boot_type",
                "MajorBootType",
                "MajorBootType.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minor_boot_type",
                "MinorBootType",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_manufacturing_defaul_configurationt_boot_mode",
                "PendingManufacturingDefaulConfigurationtBootMode",
                "PartitionBootMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_power_on_side",
                "PendingPowerOnSide",
                "ServiceProcessorSide.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_system_keylock",
                "PendingSystemKeylock",
                "KeylockPosition.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "power_on_logical_partition_start_policy",
                "PowerOnLogicalPartitionStartPolicy",
                "PowerOnStartPolicy.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "power_on_option",
                "PowerOnOption",
                "PowerOnOption.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "power_on_speed",
                "PowerOnSpeed",
                "PowerOnSpeed.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "power_on_speed_override",
                "PowerOnSpeedOverride",
                "PowerOnSpeedOverride.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "power_off_when_last_logical_partition_is_shutdown",
                "PowerOffWhenLastLogicalPartitionIsShutdown",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_turbocore_enabled",
                "PendingTurbocoreEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LinkAggregation": [
        null,
        [
            [
                "alternate_address",
                "AlternateAddress",
                "MACAddress.Pattern",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "auto_recovery_enabled",
                "AutoRecoveryEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "backup_adapter",
                "BackupAdapter",
                "string",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "io_adapters",
                "IOAdapters",
                "IOAdapterChoiceCollection.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "ip_address_to_ping",
                "IPAddressToPing",
                "IPAddress.Union",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "jumbo_frame_enabled",
                "JumboFrameEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "mode",
                "Mode",
                "LinkAggregationMode.Enum",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "hash_mode",
                "HashMode",
                "LinkAggregationHashMode.Enum",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "no_loss_failover_enabled",
                "NoLossFailoverEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "retry_count",
                "RetryCount",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "retry_time",
                "RetryTime",
                "long",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "device_id",
                "DeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "use_alternate_address",
                "UseAlternateAddress",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "ip_interface",
                "IPInterface",
                "IPInterface.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "description",
                "Description",
                "string",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "LinkAggregation_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "LoadGroup": [
        null,
        [
            [
                "port_vlan_id",
                "PortVLANID",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "trunk_adapters",
                "TrunkAdapters",
                "TrunkAdapter_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UUID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "virtual_networks",
                "VirtualNetworks",
                "VirtualNetwork_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LoadGroup_Collection": [
        null,
        [
            [
                "load_group",
                "LoadGroup",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "LogicalPartition": [
        "BasePartition",
        [
            [
                "remote_restart_capable",
                "RemoteRestartCapable",
                "boolean",
                "cu",
                "a",
                "R",
                ""
            ],
            [
                "has_dedicated_processors_for_migration",
                "HasDedicatedProcessorsForMigration",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "suspend_capable",
                "SuspendCapable",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "migration_state",
                "MigrationState",
                "PartitionMigrationState.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "remote_restart_state",
                "RemoteRestartState",
                "PartitionRemoteRestart.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "power_management_mode",
                "PowerManagementMode",
                "PartitionPowerManagementMode.Enum",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "uses_high_speed_link_opticonnect",
                "UsesHighSpeedLinkOpticonnect",
                "boolean",
                "cu",
                "a",
                "R",
                ""
            ],
            [
                "uses_virtual_opticonnect",
                "UsesVirtualOpticonnect",
                "boolean",
                "cu",
                "a",
                "R",
                ""
            ],
            [
                "virtual_fibre_channel_client_adapters",
                "VirtualFibreChannelClientAdapters",
                "VirtualFibreChannelClientAdapter_Links.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "virtual_scsi_client_adapters",
                "VirtualSCSIClientAdapters",
                "VirtualSCSIClientAdapter_Links.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "is_restricted_io_partition",
                "IsRestrictedIOPartition",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "storage_device_unique_device_id",
                "StorageDeviceUniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "R",
                "Advanced"
            ],
            [
                "designated_ipl_source",
                "DesignatedIPLSource",
                "IPLSource.Enum",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionCapabilities": [
        null,
        [
            [
                "dynamic_logical_partition_io_capable",
                "DynamicLogicalPartitionIOCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "dynamic_logical_partition_memory_capable",
                "DynamicLogicalPartitionMemoryCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "dynamic_logical_partition_processor_capable",
                "DynamicLogicalPartitionProcessorCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "internal_and_external_intrusion_detection_capable",
                "InternalAndExternalIntrusionDetectionCapable",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "resource_monitoring_control_operating_system_shutdown_capable",
                "ResourceMonitoringControlOperatingSystemShutdownCapable",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionDedicatedProcessorConfiguration": [
        null,
        [
            [
                "current_maximum_processors",
                "CurrentMaximumProcessors",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_minimum_processors",
                "CurrentMinimumProcessors",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_processors",
                "CurrentProcessors",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "run_processors",
                "RunProcessors",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionIOConfiguration": [
        "LogicalPartitionProfileIOConfiguration",
        [
            [
                "current_maximum_virtual_io_slots",
                "CurrentMaximumVirtualIOSlots",
                "int",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionMemoryConfiguration": [
        "LogicalPartitionProfileMemoryConfiguration",
        [
            [
                "auto_entitled_memory_enabled",
                "AutoEntitledMemoryEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "current_barrier_synchronization_register_arrays",
                "CurrentBarrierSynchronizationRegisterArrays",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_entitled_memory",
                "CurrentEntitledMemory",
                "EntitledIOMegabyte.Union",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_expansion_factor",
                "CurrentExpansionFactor",
                "float",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_hardware_page_table_ratio",
                "CurrentHardwarePageTableRatio",
                "HardwarePageTableRatioExponent.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_huge_page_count",
                "CurrentHugePageCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_huge_page_count",
                "CurrentMaximumHugePageCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_memory",
                "CurrentMaximumMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_memory",
                "CurrentMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_memory_weight",
                "CurrentMemoryWeight",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_minimum_huge_page_count",
                "CurrentMinimumHugePageCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_minimum_memory",
                "CurrentMinimumMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_paging_service_partition",
                "CurrentPagingServicePartition",
                "link rel=VirtualIOServer",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_expansion_hardware_access_enabled",
                "MemoryExpansionHardwareAccessEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_encryption_hardware_access_enabled",
                "MemoryEncryptionHardwareAccessEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_expansion_enabled",
                "MemoryExpansionEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_releaseable",
                "MemoryReleaseable",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_to_release",
                "MemoryToRelease",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "redundant_error_path_reporting_enabled",
                "RedundantErrorPathReportingEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "required_minimum_for_maximum",
                "RequiredMinimumForMaximum",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_entitled_memory",
                "RuntimeEntitledMemory",
                "EntitledIOMegabyte.Union",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_expansion_factor",
                "RuntimeExpansionFactor",
                "float",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_huge_page_count",
                "RuntimeHugePageCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_memory",
                "RuntimeMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_memory_weight",
                "RuntimeMemoryWeight",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_minimum_memory",
                "RuntimeMinimumMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "shared_memory_enabled",
                "SharedMemoryEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProcessorConfiguration": [
        "LogicalPartitionProfileProcessorConfiguration",
        [
            [
                "current_has_dedicated_processors",
                "CurrentHasDedicatedProcessors",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_sharing_mode",
                "CurrentSharingMode",
                "LogicalPartitionProcessorSharingMode.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_dedicated_processor_configuration",
                "CurrentDedicatedProcessorConfiguration",
                "LogicalPartitionDedicatedProcessorConfiguration.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_has_dedicated_processors",
                "RuntimeHasDedicatedProcessors",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_sharing_mode",
                "RuntimeSharingMode",
                "LogicalPartitionProcessorSharingMode.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_shared_processor_configuration",
                "CurrentSharedProcessorConfiguration",
                "LogicalPartitionSharedProcessorConfiguration.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfile": [
        null,
        [
            [
                "affinity_group_id",
                "AffinityGroupID",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "assign_all_resources",
                "AssignAllResources",
                "boolean",
                "co",
                "d",
                "I",
                ""
            ],
            [
                "associated_partition",
                "AssociatedPartition",
                "link rel=BasePartition",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "auto_start",
                "AutoStart",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "boot_mode",
                "BootMode",
                "PartitionBootMode.Enum",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "connection_monitoring_enabled",
                "ConnectionMonitoringEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "desired_processor_compatibility_mode",
                "DesiredProcessorCompatibilityMode",
                "LogicalPartitionProcessorCompatibilityMode.Enum",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "electronic_error_reporting_enabled",
                "ElectronicErrorReportingEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "host_ethernet_adapter_logical_ports",
                "HostEthernetAdapterLogicalPorts",
                "HostEthernetAdapterLogicalPort_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "io_configuration_instance",
                "IOConfigurationInstance",
                "LogicalPartitionProfileIOConfiguration.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "power_control_partitions",
                "PowerControlPartitions",
                "BasePartition_Links.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "processor_attributes",
                "ProcessorAttributes",
                "LogicalPartitionProfileProcessorConfiguration.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "profile_memory",
                "ProfileMemory",
                "LogicalPartitionProfileMemoryConfiguration.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "profile_name",
                "ProfileName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "profile_type",
                "ProfileType",
                "ProfileType.Enum",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "redundant_error_path_reporting_enabled",
                "RedundantErrorPathReportingEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "switch_network_interface_device_id",
                "SwitchNetworkInterfaceDeviceID",
                "string",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "setting_id",
                "SettingID",
                "string",
                "ro",
                "o",
                "I",
                ""
            ],
            [
                "profile_sriov_ethernet_logical_ports",
                "ProfileSRIOVEthernetLogicalPorts",
                "ProfileSRIOVEthernetLogicalPort_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfileDedicatedProcessorConfiguration": [
        null,
        [
            [
                "desired_processors",
                "DesiredProcessors",
                "UINT16.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_processors",
                "MaximumProcessors",
                "UINT16.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minimum_processors",
                "MinimumProcessors",
                "UINT16.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfileIOConfiguration": [
        null,
        [
            [
                "high_speed_link_opticonnect_pool",
                "HighSpeedLinkOpticonnectPool",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "host_channel_adapters",
                "HostChannelAdapters",
                "HostChannelAdapter_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_virtual_io_slots",
                "MaximumVirtualIOSlots",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pool_i_ds",
                "PoolIDs",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "profile_io_slots",
                "ProfileIOSlots",
                "ProfileIOSlot_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "tagged_io",
                "TaggedIO",
                "IBMiProfileTaggedIO.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "profile_virtual_io_adapters",
                "ProfileVirtualIOAdapters",
                "ProfileVirtualIOAdapterChoiceCollection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_opticonnect_pool",
                "VirtualOpticonnectPool",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfileMemoryConfiguration": [
        null,
        [
            [
                "active_memory_expansion_enabled",
                "ActiveMemoryExpansionEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "active_memory_sharing_enabled",
                "ActiveMemorySharingEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "barrier_synchronization_register_array_count",
                "BarrierSynchronizationRegisterArrayCount",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "desired_entitled_memory",
                "DesiredEntitledMemory",
                "EntitledIOMegabyte.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "desired_huge_page_count",
                "DesiredHugePageCount",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "desired_memory",
                "DesiredMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "expansion_factor",
                "ExpansionFactor",
                "float",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "hardware_page_table_ratio",
                "HardwarePageTableRatio",
                "HardwarePageTableRatioExponent.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "manual_entitled_mode_enabled",
                "ManualEntitledModeEnabled",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_huge_page_count",
                "MaximumHugePageCount",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_memory",
                "MaximumMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "memory_weight",
                "MemoryWeight",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minimum_huge_page_count",
                "MinimumHugePageCount",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minimum_memory",
                "MinimumMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "primary_paging_service_partition",
                "PrimaryPagingServicePartition",
                "link rel=VirtualIOServer",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "secondary_paging_service_partition",
                "SecondaryPagingServicePartition",
                "link rel=VirtualIOServer",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfileProcessorConfiguration": [
        null,
        [
            [
                "dedicated_processor_configuration",
                "DedicatedProcessorConfiguration",
                "LogicalPartitionProfileDedicatedProcessorConfiguration.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "has_dedicated_processors",
                "HasDedicatedProcessors",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "shared_processor_configuration",
                "SharedProcessorConfiguration",
                "LogicalPartitionProfileSharedProcessorConfiguration.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "sharing_mode",
                "SharingMode",
                "LogicalPartitionProcessorSharingMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfileSharedProcessorConfiguration": [
        null,
        [
            [
                "desired_processing_units",
                "DesiredProcessingUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "desired_virtual_processors",
                "DesiredVirtualProcessors",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_processing_units",
                "MaximumProcessingUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_virtual_processors",
                "MaximumVirtualProcessors",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minimum_processing_units",
                "MinimumProcessingUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minimum_virtual_processors",
                "MinimumVirtualProcessors",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "shared_processor_pool_id",
                "SharedProcessorPoolID",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "uncapped_weight",
                "UncappedWeight",
                "MemoryWeight.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartitionProfile_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "LogicalPartitionSharedProcessorConfiguration": [
        null,
        [
            [
                "allocated_virtual_processors",
                "AllocatedVirtualProcessors",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_processing_units",
                "CurrentMaximumProcessingUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_minimum_processing_units",
                "CurrentMinimumProcessingUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_processing_units",
                "CurrentProcessingUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_shared_processor_pool_id",
                "CurrentSharedProcessorPoolID",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_uncapped_weight",
                "CurrentUncappedWeight",
                "MemoryWeight.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_minimum_virtual_processors",
                "CurrentMinimumVirtualProcessors",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_virtual_processors",
                "CurrentMaximumVirtualProcessors",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_processing_units",
                "RuntimeProcessingUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "runtime_uncapped_weight",
                "RuntimeUncappedWeight",
                "MemoryWeight.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalPartition_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "LogicalUnit": [
        "VirtualSCSIStorage",
        [
            [
                "thin_device",
                "ThinDevice",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unit_capacity",
                "UnitCapacity",
                "Gigabyte.Type",
                "co",
                "r",
                "D",
                ""
            ],
            [
                "logical_unit_type",
                "LogicalUnitType",
                "LogicalUnitType.Enum",
                "co",
                "r",
                "D",
                ""
            ],
            [
                "cloned_from",
                "ClonedFrom",
                "UDID.Pattern",
                "co",
                "d",
                "D",
                ""
            ],
            [
                "in_use",
                "InUse",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unit_name",
                "UnitName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "LogicalUnit_Collection": [
        null,
        [
            [
                "logical_unit",
                "LogicalUnit",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "LogicalVolumeVirtualTargetDevice": [
        "VirtualTargetDevice",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "MachineTypeModelSerialNumber": [
        null,
        [
            [
                "machine_type",
                "MachineType",
                "MachineType.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "model",
                "Model",
                "MachineModel.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "serial_number",
                "SerialNumber",
                "SerialNumber.Pattern",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ManagedFrame": [
        null,
        [
            [
                "activated_service_pack_and_level",
                "ActivatedServicePackAndLevel",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "cages",
                "Cages",
                "Cage_Collection.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "engineering_change_number",
                "EngineeringChangeNumber",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "frame_capability",
                "FrameCapability",
                "ManagedFrameCapability.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "frame_name",
                "FrameName",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "frame_number",
                "FrameNumber",
                "int",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "frame_state",
                "FrameState",
                "ManagedFrameState.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "frame_type",
                "FrameType",
                "ManagedFrameType.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "is_power6_frame",
                "IsPower6Frame",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "slave_bulk_power_controller_exists",
                "SlaveBulkPowerControllerExists",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ]
        ]
    ],
    "ManagedFrame_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ManagedSystem": [
        null,
        [
            [
                "activated_level",
                "ActivatedLevel",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "associated_ipl_configuration",
                "AssociatedIPLConfiguration",
                "IPLConfiguration.Type",
                "cu",
                "d",
                "R",
                "Hypervisor"
            ],
            [
                "associated_logical_partitions",
                "AssociatedLogicalPartitions",
                "LogicalPartition_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_reserved_storage_device_pool",
                "AssociatedReservedStorageDevicePool",
                "ReservedStorageDevicePool_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_capabilities",
                "AssociatedSystemCapabilities",
                "SystemCapabilities.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_io_configuration",
                "AssociatedSystemIOConfiguration",
                "SystemIOConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_memory_configuration",
                "AssociatedSystemMemoryConfiguration",
                "SystemMemoryConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_processor_configuration",
                "AssociatedSystemProcessorConfiguration",
                "SystemProcessorConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_security",
                "AssociatedSystemSecurity",
                "SystemSecurity.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_system_virtual_storage",
                "AssociatedSystemVirtualStorage",
                "SystemVirtualStorage_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_virtual_environment_configuration",
                "AssociatedVirtualEnvironmentConfiguration",
                "VirtualEnvironmentConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "associated_virtual_io_servers",
                "AssociatedVirtualIOServers",
                "VirtualIOServer_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "current_maximum_partitions_per_host_channel_adapter",
                "CurrentMaximumPartitionsPerHostChannelAdapter",
                "int",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "detailed_state",
                "DetailedState",
                "DetailedState.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "manufacturing_default_configuration_enabled",
                "ManufacturingDefaultConfigurationEnabled",
                "boolean",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "maximum_partitions",
                "MaximumPartitions",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "maximum_partitions_per_host_channel_adapter",
                "MaximumPartitionsPerHostChannelAdapter",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "maximum_power_control_partitions",
                "MaximumPowerControlPartitions",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "maximum_remote_restart_partitions",
                "MaximumRemoteRestartPartitions",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "maximum_shared_processor_capable_partition_id",
                "MaximumSharedProcessorCapablePartitionID",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "maximum_suspendable_partitions",
                "MaximumSuspendablePartitions",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "pending_maximum_partitions_per_host_channel_adapter",
                "PendingMaximumPartitionsPerHostChannelAdapter",
                "int",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "physical_system_attention_led_state",
                "PhysicalSystemAttentionLEDState",
                "boolean",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "primary_ip_address",
                "PrimaryIPAddress",
                "IPAddress.Union",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "secondary_ip_address",
                "SecondaryIPAddress",
                "IPAddress.Union",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "service_processor_failover_enabled",
                "ServiceProcessorFailoverEnabled",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "service_processor_failover_reason",
                "ServiceProcessorFailoverReason",
                "string",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "service_processor_failover_state",
                "ServiceProcessorFailoverState",
                "ServiceProcessorFailoverState.Enum",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "service_processor_version",
                "ServiceProcessorVersion",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "state",
                "State",
                "SystemState.Enum",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "system_placement",
                "SystemPlacement",
                "int",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "system_name",
                "SystemName",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "system_time",
                "SystemTime",
                "long",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "virtual_system_attention_led_state",
                "VirtualSystemAttentionLEDState",
                "boolean",
                "uo",
                "d",
                "R",
                ""
            ],
            [
                "associated_power_enterprise_pool",
                "AssociatedPowerEnterprisePool",
                "link rel=PowerEnterprisePool",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "system_migration_information",
                "SystemMigrationInformation",
                "SystemMigrationInformation.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "service_partition",
                "ServicePartition",
                "link rel=LogicalPartition",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "reference_code",
                "ReferenceCode",
                "string",
                "ro",
                "o",
                "R",
                ""
            ]
        ]
    ],
    "ManagedSystem_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ManagementConsole": [
        null,
        [
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "managed_frames",
                "ManagedFrames",
                "ManagedFrame_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "managed_systems",
                "ManagedSystems",
                "ManagedSystem_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "management_console_name",
                "ManagementConsoleName",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "network_interfaces",
                "NetworkInterfaces",
                "ManagementConsoleNetworkInterface_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "template_object_model_version",
                "TemplateObjectModelVersion",
                "SchemaVersion.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "user_object_model_version",
                "UserObjectModelVersion",
                "SchemaVersion.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "version_info",
                "VersionInfo",
                "VersionReleaseMaintenance.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "local_virtual_io_server_image_names",
                "LocalVirtualIOServerImageNames",
                "string",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "web_object_model_version",
                "WebObjectModelVersion",
                "SchemaVersion.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "power_enterprise_pools",
                "PowerEnterprisePools",
                "PowerEnterprisePool_Links.Type",
                "cu",
                "d",
                "R",
                ""
            ]
        ]
    ],
    "ManagementConsoleNetworkInterface": [
        null,
        [
            [
                "interface_name",
                "InterfaceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "network_address",
                "NetworkAddress",
                "IPAddress.List",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ManagementConsoleNetworkInterface_Collection": [
        null,
        [
            [
                "management_console_network_interface",
                "ManagementConsoleNetworkInterface",
                "_Collection.Type",
                "cu",
                "r",
                "",
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
    "NetworkBootDevice": [
        null,
        [
            [
                "boot_device",
                "BootDevice",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "is_physical_device",
                "IsPhysicalDevice",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "mac_address_value",
                "MACAddressValue",
                "MACAddress.Pattern",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "NetworkBootDevice_Collection": [
        null,
        [
            [
                "network_boot_device",
                "NetworkBootDevice",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "NetworkBridge": [
        null,
        [
            [
                "control_channel_id",
                "ControlChannelID",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "failover_enabled",
                "FailoverEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "load_balancing_enabled",
                "LoadBalancingEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "load_groups",
                "LoadGroups",
                "LoadGroup_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "int",
                "co",
                "r",
                "I",
                ""
            ],
            [
                "shared_ethernet_adapters",
                "SharedEthernetAdapters",
                "SharedEthernetAdapter_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "virtual_networks",
                "VirtualNetworks",
                "VirtualNetwork_Links.Type",
                "ro",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "NetworkBridge_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "Node": [
        null,
        [
            [
                "host_name",
                "HostName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "partition_id",
                "PartitionID",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "partition_name",
                "PartitionName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "machine_type_model_and_serial_number",
                "MachineTypeModelAndSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_io_server_level",
                "VirtualIOServerLevel",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_io_server",
                "VirtualIOServer",
                "link rel=VirtualIOServer",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ip_address",
                "IPAddress",
                "IPAddress.Union",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "Node_Collection": [
        null,
        [
            [
                "node",
                "Node",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "PhysicalFibreChannelAdapter": [
        "IOAdapter",
        [
            [
                "physical_fibre_channel_ports",
                "PhysicalFibreChannelPorts",
                "PhysicalFibreChannelPort_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "PhysicalFibreChannelPort": [
        null,
        [
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "physical_volumes",
                "PhysicalVolumes",
                "PhysicalVolume_Collection.Type",
                "cu",
                "d",
                "D",
                "ViosStorage"
            ],
            [
                "port_name",
                "PortName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "wwpn",
                "WWPN",
                "WWPN.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "available_ports",
                "AvailablePorts",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "total_ports",
                "TotalPorts",
                "int",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "PhysicalFibreChannelPort_Collection": [
        null,
        [
            [
                "physical_fibre_channel_port",
                "PhysicalFibreChannelPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "PhysicalVolume": [
        "VirtualSCSIStorage",
        [
            [
                "available_physical_partitions",
                "AvailablePhysicalPartitions",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "description",
                "Description",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "persistent_reserve_key_value",
                "PersistentReserveKeyValue",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "reserve_policy",
                "ReservePolicy",
                "PhysicalVolumeReservePolicy.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "reserve_policy_algorithm",
                "ReservePolicyAlgorithm",
                "SCSIReservePolicyAlgorithm.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "total_physical_partitions",
                "TotalPhysicalPartitions",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "available_for_usage",
                "AvailableForUsage",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "volume_capacity",
                "VolumeCapacity",
                "Megabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "volume_name",
                "VolumeName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "volume_state",
                "VolumeState",
                "PhysicalVolumeState.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "volume_unique_id",
                "VolumeUniqueID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "is_fibre_channel_backed",
                "IsFibreChannelBacked",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "PhysicalVolumeVirtualTargetDevice": [
        "VirtualTargetDevice",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "PhysicalVolume_Collection": [
        null,
        [
            [
                "physical_volume",
                "PhysicalVolume",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "PowerEnterprisePool": [
        null,
        [
            [
                "pool_id",
                "PoolID",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "pool_name",
                "PoolName",
                "string",
                "uo",
                "r",
                "R",
                ""
            ],
            [
                "sequence_number",
                "SequenceNumber",
                "int",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "total_mobile_co_d_proc_units",
                "TotalMobileCoDProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "total_mobile_co_d_memory",
                "TotalMobileCoDMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "available_mobile_co_d_proc_units",
                "AvailableMobileCoDProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "available_mobile_co_d_memory",
                "AvailableMobileCoDMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "unreturned_mobile_co_d_proc_units",
                "UnreturnedMobileCoDProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "unreturned_mobile_co_d_memory",
                "UnreturnedMobileCoDMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "compliance_state",
                "ComplianceState",
                "",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "compliance_remaining_hours",
                "ComplianceRemainingHours",
                "Hours.Type",
                "ro",
                "o",
                "R",
                ""
            ],
            [
                "power_enterprise_pool_master_management_console",
                "PowerEnterprisePoolMasterManagementConsole",
                "link rel=ManagementConsole",
                "uo",
                "r",
                "R",
                ""
            ],
            [
                "power_enterprise_pool_members",
                "PowerEnterprisePoolMembers",
                "PowerEnterprisePoolMember_Links.Type",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "power_enterprise_pool_management_consoles",
                "PowerEnterprisePoolManagementConsoles",
                "PowerEnterprisePoolManagementConsole_Collection.Type",
                "ro",
                "r",
                "R",
                ""
            ]
        ]
    ],
    "PowerEnterprisePoolManagementConsole": [
        null,
        [
            [
                "management_console_name",
                "ManagementConsoleName",
                "string",
                "uo",
                "r",
                "D",
                ""
            ],
            [
                "management_console_machine_type_model_serial_number",
                "ManagementConsoleMachineTypeModelSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "uo",
                "r",
                "D",
                ""
            ],
            [
                "is_master_console",
                "IsMasterConsole",
                "boolean",
                "uo",
                "r",
                "D",
                ""
            ],
            [
                "is_backup_master_console",
                "IsBackupMasterConsole",
                "boolean",
                "uo",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "PowerEnterprisePoolManagementConsole_Collection": [
        null,
        [
            [
                "power_enterprise_pool_management_console",
                "PowerEnterprisePoolManagementConsole",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "PowerEnterprisePoolMember": [
        null,
        [
            [
                "mobile_co_d_proc_units",
                "MobileCoDProcUnits",
                "UINT16.Type",
                "uo",
                "r",
                "I",
                ""
            ],
            [
                "mobile_co_d_memory",
                "MobileCoDMemory",
                "Megabyte.Type",
                "uo",
                "r",
                "I",
                ""
            ],
            [
                "inactive_proc_units",
                "InactiveProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "inactive_memory",
                "InactiveMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "unreturned_mobile_co_d_proc_units",
                "UnreturnedMobileCoDProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "unreturned_mobile_co_d_memory",
                "UnreturnedMobileCoDMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "proc_compliance_remaining_hours",
                "ProcComplianceRemainingHours",
                "Hours.Type",
                "ro",
                "o",
                "I",
                ""
            ],
            [
                "mem_compliance_remaining_hours",
                "MemComplianceRemainingHours",
                "Hours.Type",
                "ro",
                "o",
                "I",
                ""
            ],
            [
                "managed_system_name",
                "ManagedSystemName",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "managed_system_installed_proc_units",
                "ManagedSystemInstalledProcUnits",
                "UINT16.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "managed_system_installed_memory",
                "ManagedSystemInstalledMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "managed_system_machine_type_model_serial_number",
                "ManagedSystemMachineTypeModelSerialNumber",
                "MachineTypeModelSerialNumber.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "associated_managed_system",
                "AssociatedManagedSystem",
                "link rel=ManagedSystem",
                "ro",
                "o",
                "I",
                ""
            ]
        ]
    ],
    "PowerEnterprisePoolMember_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "PowerEnterprisePool_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ProfileClientNetworkAdapter": [
        "ProfileVirtualEthernetAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileIOSlot": [
        null,
        [
            [
                "associated_io_slot",
                "AssociatedIOSlot",
                "IOSlot.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "is_required",
                "IsRequired",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileIOSlot_Collection": [
        null,
        [
            [
                "profile_io_slot",
                "ProfileIOSlot",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ProfileSRIOVConfiguredLogicalPort": [
        null,
        [
            [
                "configuration_id",
                "ConfigurationID",
                "short",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "logical_port_id",
                "LogicalPortID",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "adapter_id",
                "AdapterID",
                "short",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_promiscous",
                "IsPromiscous",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_diagnostic",
                "IsDiagnostic",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_debug",
                "IsDebug",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_huge_dma",
                "IsHugeDMA",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "configured_capacity",
                "ConfiguredCapacity",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_id",
                "PhysicalPortID",
                "byte",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "tuning_buffer_id",
                "TuningBufferID",
                "byte",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileSRIOVEthernetLogicalPort": [
        "ProfileSRIOVConfiguredLogicalPort",
        [
            [
                "allowed_mac_addresses",
                "AllowedMACAddresses",
                "AllowedMACAddresses.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "mac_address",
                "MACAddress",
                "MACAddress.Pattern",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ieee8021_q_allowable_priorities",
                "IEEE8021QAllowablePriorities",
                "byte",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ieee8021_q_priority",
                "IEEE8021QPriority",
                "byte",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "mac_address_flags",
                "MACAddressFlags",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "number_of_allowed_vla_ns",
                "NumberOfAllowedVLANs",
                "byte",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "allowed_vla_ns",
                "AllowedVLANs",
                "AllowedVLANIDs.Union",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileSRIOVEthernetLogicalPort_Collection": [
        null,
        [
            [
                "profile_sriov_ethernet_logical_port",
                "ProfileSRIOVEthernetLogicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ProfileTrunkAdapter": [
        "ProfileVirtualEthernetAdapter",
        [
            [
                "trunk_priority",
                "TrunkPriority",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "interface_name",
                "InterfaceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualEthernetAdapter": [
        "ProfileVirtualIOAdapter",
        [
            [
                "is_tagged_vlan_supported",
                "IsTaggedVLANSupported",
                "boolean",
                "cu",
                "a",
                "D",
                ""
            ],
            [
                "ma_c_address_value",
                "MaCAddressValue",
                "MACAddress.Pattern",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "VLANID.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "tagged_vlan_ids",
                "TaggedVLANIDs",
                "VLANID.List",
                "cu",
                "a",
                "D",
                ""
            ],
            [
                "allowed_operating_system_mac_addresses",
                "AllowedOperatingSystemMACAddresses",
                "AllowedMACAddresses.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "quality_of_service_priority",
                "QualityOfServicePriority",
                "QualityOfServicePriority.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switch_interface_manager_id",
                "VirtualSwitchInterfaceManagerID",
                "PositiveInteger.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switch_interface_type",
                "VirtualSwitchInterfaceType",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switch_interface_type_version",
                "VirtualSwitchInterfaceTypeVersion",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "is_quality_of_service_priority_enabled",
                "IsQualityOfServicePriorityEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switch_name",
                "VirtualSwitchName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switch_id",
                "VirtualSwitchID",
                "short",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualFibreChannelAdapter": [
        "ProfileVirtualIOAdapter",
        [
            [
                "connecting_virtual_slot_number",
                "ConnectingVirtualSlotNumber",
                "VirtualIOSlotIndex.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "connecting_partition_id",
                "ConnectingPartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualFibreChannelClientAdapter": [
        "ProfileVirtualFibreChannelAdapter",
        [
            [
                "wwp_ns",
                "WWPNs",
                "WWPN2.List",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualFibreChannelServerAdapter": [
        "ProfileVirtualFibreChannelAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualIOAdapter": [
        null,
        [
            [
                "virtual_slot_number",
                "VirtualSlotNumber",
                "VirtualIOSlotIndex.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "is_required",
                "IsRequired",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "adapter_type",
                "AdapterType",
                "VirtualIOAdapterType.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "local_partition_id",
                "LocalPartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualIOAdapterChoiceCollection": [
        null,
        [
            [
                "profile_virtual_io_adapter_choice",
                "ProfileVirtualIOAdapterChoice",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ProfileVirtualSCSIAdapter": [
        "ProfileVirtualIOAdapter",
        [
            [
                "remote_slot_number",
                "RemoteSlotNumber",
                "VirtualIOSlotIndex.Type",
                "cu",
                "a",
                "D",
                ""
            ],
            [
                "backing_device_name",
                "BackingDeviceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "remote_backing_device_name",
                "RemoteBackingDeviceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "remote_partition_id",
                "RemotePartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualSCSIClientAdapter": [
        "ProfileVirtualSCSIAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ProfileVirtualSCSIServerAdapter": [
        "ProfileVirtualSCSIAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "ReservedStorageDevice": [
        null,
        [
            [
                "associated_logical_partition",
                "AssociatedLogicalPartition",
                "link rel=LogicalPartition",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "device_selection_type",
                "DeviceSelectionType",
                "string",
                "ro",
                "a",
                "D",
                ""
            ],
            [
                "device_size",
                "DeviceSize",
                "Gigabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "device_state",
                "DeviceState",
                "StorageDeviceState.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "device_type",
                "DeviceType",
                "StorageDeviceType.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "is_redundant",
                "IsRedundant",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "redundancy_capable",
                "RedundancyCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "redundant_device_name",
                "RedundantDeviceName",
                "string",
                "cu",
                "a",
                "D",
                ""
            ],
            [
                "redundant_device_state",
                "RedundantDeviceState",
                "StorageDeviceState.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "redundant_location_code",
                "RedundantLocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "a",
                "D",
                ""
            ]
        ]
    ],
    "ReservedStorageDevicePool": [
        "SharedMemoryPool",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "ReservedStorageDevicePool_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "ReservedStorageDevice_Collection": [
        null,
        [
            [
                "reserved_storage_device",
                "ReservedStorageDevice",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SRIOVAdapter": [
        "IOAdapter",
        [
            [
                "sriov_adapter_id",
                "SRIOVAdapterID",
                "int",
                "co",
                "d",
                "D",
                ""
            ],
            [
                "adapter_state",
                "AdapterState",
                "SRIOVAdapterState.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "adapter_mode",
                "AdapterMode",
                "SRIOVAdapterMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "converged_ethernet_physical_ports",
                "ConvergedEthernetPhysicalPorts",
                "SRIOVConvergedNetworkAdapterPhysicalPort_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "ethernet_logical_ports",
                "EthernetLogicalPorts",
                "SRIOVEthernetLogicalPort_Links.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "ethernet_physical_ports",
                "EthernetPhysicalPorts",
                "SRIOVEthernetPhysicalPort_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "fibre_channel_over_ethernet_logical_ports",
                "FibreChannelOverEthernetLogicalPorts",
                "SRIOVFibreChannelOverEthernetLogicalPort_Links.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "is_functional",
                "IsFunctional",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_huge_dma_logical_ports",
                "MaximumHugeDMALogicalPorts",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_logical_ports_supported",
                "MaximumLogicalPortsSupported",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unconfigured_logical_ports",
                "UnconfiguredLogicalPorts",
                "SRIOVUnconfiguredLogicalPort_Collection.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SRIOVConfiguredLogicalPort": [
        null,
        [
            [
                "configuration_id",
                "ConfigurationID",
                "short",
                "co",
                "d",
                "I",
                ""
            ],
            [
                "logical_port_id",
                "LogicalPortID",
                "int",
                "co",
                "d",
                "I",
                ""
            ],
            [
                "adapter_id",
                "AdapterID",
                "short",
                "co",
                "r",
                "I",
                ""
            ],
            [
                "dynamic_reconfiguration_connector_name",
                "DynamicReconfigurationConnectorName",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "is_functional",
                "IsFunctional",
                "boolean",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "is_promiscous",
                "IsPromiscous",
                "boolean",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "is_diagnostic",
                "IsDiagnostic",
                "boolean",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "is_debug",
                "IsDebug",
                "boolean",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "is_huge_dma",
                "IsHugeDMA",
                "boolean",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "configured_capacity",
                "ConfiguredCapacity",
                "Percent.Pattern",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "physical_port_id",
                "PhysicalPortID",
                "byte",
                "co",
                "r",
                "I",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "tuning_buffer_id",
                "TuningBufferID",
                "byte",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "SRIOVConvergedNetworkAdapterPhysicalPort": [
        "SRIOVEthernetPhysicalPort",
        [
            [
                "configured_max_fiber_channel_over_ethernet_logical_ports",
                "ConfiguredMaxFiberChannelOverEthernetLogicalPorts",
                "int",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "default_fiber_channel_targets_for_backing_device",
                "DefaultFiberChannelTargetsForBackingDevice",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "default_fiber_channel_targets_for_non_backing_device",
                "DefaultFiberChannelTargetsForNonBackingDevice",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "configured_fiber_channel_over_ethernet_logical_ports",
                "ConfiguredFiberChannelOverEthernetLogicalPorts",
                "short",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "minimum_f_co_e_capacity_granularity",
                "MinimumFCoECapacityGranularity",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "fiber_channel_targets_rounding_value",
                "FiberChannelTargetsRoundingValue",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "max_supported_fiber_channel_over_ethernet_logical_ports",
                "MaxSupportedFiberChannelOverEthernetLogicalPorts",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_fiber_channel_targets",
                "MaximumFiberChannelTargets",
                "int",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SRIOVConvergedNetworkAdapterPhysicalPort_Collection": [
        null,
        [
            [
                "sriov_converged_network_adapter_physical_port",
                "SRIOVConvergedNetworkAdapterPhysicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SRIOVEthernetLogicalPort": [
        "SRIOVConfiguredLogicalPort",
        [
            [
                "allowed_mac_addresses",
                "AllowedMACAddresses",
                "AllowedMACAddresses.Union",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "mac_address",
                "MACAddress",
                "MACAddress.Pattern",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "current_mac_address",
                "CurrentMACAddress",
                "MACAddress.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "ieee8021_q_allowable_priorities",
                "IEEE8021QAllowablePriorities",
                "byte",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "ieee8021_q_priority",
                "IEEE8021QPriority",
                "byte",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "mac_address_flags",
                "MACAddressFlags",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "number_of_allowed_vla_ns",
                "NumberOfAllowedVLANs",
                "byte",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "allowed_vla_ns",
                "AllowedVLANs",
                "AllowedVLANIDs.Union",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "SRIOVEthernetLogicalPort_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SRIOVEthernetPhysicalPort": [
        "SRIOVPhysicalPort",
        [
            [
                "allocated_capacity",
                "AllocatedCapacity",
                "Percent.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "configured_max_ethernet_logical_ports",
                "ConfiguredMaxEthernetLogicalPorts",
                "short",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "configured_ethernet_logical_ports",
                "ConfiguredEthernetLogicalPorts",
                "short",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_port_vlanid",
                "MaximumPortVLANID",
                "SRIOVVLANID.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_vlanid",
                "MaximumVLANID",
                "SRIOVVLANID.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_ethernet_capacity_granularity",
                "MinimumEthernetCapacityGranularity",
                "long",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_port_vlanid",
                "MinimumPortVLANID",
                "SRIOVVLANID.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_vlanid",
                "MinimumVLANID",
                "SRIOVVLANID.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "max_supported_ethernet_logical_ports",
                "MaxSupportedEthernetLogicalPorts",
                "short",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SRIOVEthernetPhysicalPort_Collection": [
        null,
        [
            [
                "sriov_ethernet_physical_port",
                "SRIOVEthernetPhysicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SRIOVFibreChannelOverEthernetLogicalPort": [
        "SRIOVConfiguredLogicalPort",
        [
            [
                "fiber_channel_targets",
                "FiberChannelTargets",
                "short",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "wwpn1",
                "WWPN1",
                "WWPN.Pattern",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "wwpn2",
                "WWPN2",
                "WWPN.Pattern",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "SRIOVFibreChannelOverEthernetLogicalPort_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SRIOVPhysicalPort": [
        null,
        [
            [
                "configured_connection_speed",
                "ConfiguredConnectionSpeed",
                "SRIOVConnectionSpeed.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "configured_mtu",
                "ConfiguredMTU",
                "SRIOVPhysicalPortMTU.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "configured_options",
                "ConfiguredOptions",
                "SRIOVPhysicalPortOptions.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "current_connection_speed",
                "CurrentConnectionSpeed",
                "SRIOVConnectionSpeed.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_options",
                "CurrentOptions",
                "SRIOVPhysicalPortOptions.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "label",
                "Label",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_diagnostics_logical_ports",
                "MaximumDiagnosticsLogicalPorts",
                "byte",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_promiscuous_logical_ports",
                "MaximumPromiscuousLogicalPorts",
                "byte",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "physical_port_id",
                "PhysicalPortID",
                "byte",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "port_capabilities",
                "PortCapabilities",
                "SRIOVPortCapability.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "port_type",
                "PortType",
                "SRIOVPhysicalPortType.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "port_logical_port_limit",
                "PortLogicalPortLimit",
                "short",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "sub_label",
                "SubLabel",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "supported_connection_speeds",
                "SupportedConnectionSpeeds",
                "SRIOVConnectionSpeed.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "supported_mt_us",
                "SupportedMTUs",
                "SRIOVPhysicalPortMTU.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "supported_options",
                "SupportedOptions",
                "SRIOVPhysicalPortOptions.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "supported_priority_access_control_list",
                "SupportedPriorityAccessControlList",
                "byte",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "link_status",
                "LinkStatus",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SRIOVUnconfiguredLogicalPort": [
        null,
        [
            [
                "dynamic_reconfiguration_connector_index",
                "DynamicReconfigurationConnectorIndex",
                "DynamicReconfigurationConnectorIndex.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "dynamic_reconfiguration_connector_name",
                "DynamicReconfigurationConnectorName",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SRIOVUnconfiguredLogicalPort_Collection": [
        null,
        [
            [
                "sriov_unconfigured_logical_port",
                "SRIOVUnconfiguredLogicalPort",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SchemaVersion": [
        null,
        [
            [
                "minor_version",
                "MinorVersion",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "schema_namespace",
                "SchemaNamespace",
                "string",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SharedEthernetAdapter": [
        null,
        [
            [
                "assigned_virtual_io_server",
                "AssignedVirtualIOServer",
                "link rel=VirtualIOServer",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "control_channel_interface_name",
                "ControlChannelInterfaceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "backing_device_choice",
                "BackingDeviceChoice",
                "IOAdapterChoice.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "high_availability_mode",
                "HighAvailabilityMode",
                "SharedEthernetAdapterHighAvailabilityMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "jumbo_frames_enabled",
                "JumboFramesEnabled",
                "boolean",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "VLANID.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "quality_of_service_mode",
                "QualityOfServiceMode",
                "SharedEthernetAdapterQualityOfServiceMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "queue_size",
                "QueueSize",
                "int",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "thread_mode_enabled",
                "ThreadModeEnabled",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "trunk_adapters",
                "TrunkAdapters",
                "TrunkAdapter_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "is_primary",
                "IsPrimary",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "ip_interface",
                "IPInterface",
                "IPInterface.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "large_send",
                "LargeSend",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "address_to_ping",
                "AddressToPing",
                "IPAddress.Union",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "iidp_service",
                "IIDPService",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SharedEthernetAdapter_Collection": [
        null,
        [
            [
                "shared_ethernet_adapter",
                "SharedEthernetAdapter",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SharedMemoryPool": [
        null,
        [
            [
                "current_available_pool_memory",
                "CurrentAvailablePoolMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "current_maximum_pool_memory",
                "CurrentMaximumPoolMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "current_pool_memory",
                "CurrentPoolMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "hardware_page_table_ratio",
                "HardwarePageTableRatio",
                "HardwarePageTableRatioExponent.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "memory_deduplication_enabled",
                "MemoryDeduplicationEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "memory_deduplication_table_ratio",
                "MemoryDeduplicationTableRatio",
                "HardwarePageTableRatioExponent.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "page_size",
                "PageSize",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "paging_devices",
                "PagingDevices",
                "ReservedStorageDevice_Collection.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "free_memory_devices_from_paging_service_partition_one",
                "FreeMemoryDevicesFromPagingServicePartitionOne",
                "ReservedStorageDevice_Collection.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "free_memory_devices_from_paging_service_partition_two",
                "FreeMemoryDevicesFromPagingServicePartitionTwo",
                "ReservedStorageDevice_Collection.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "free_redundant_memory_devices",
                "FreeRedundantMemoryDevices",
                "ReservedStorageDevice_Collection.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "pending_available_pool_memory",
                "PendingAvailablePoolMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pending_maximum_pool_memory",
                "PendingMaximumPoolMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pending_pool_memory",
                "PendingPoolMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pool_id",
                "PoolID",
                "int",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "pool_size",
                "PoolSize",
                "Megabyte.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "paging_service_partition_one",
                "PagingServicePartitionOne",
                "link rel=VirtualIOServer",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "paging_service_partition_two",
                "PagingServicePartitionTwo",
                "link rel=VirtualIOServer",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "system_firmware_pool_memory",
                "SystemFirmwarePoolMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "SharedMemoryPool_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SharedProcessorPool": [
        null,
        [
            [
                "assigned_partitions",
                "AssignedPartitions",
                "BasePartition_Links.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "current_reserved_processing_units",
                "CurrentReservedProcessingUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "maximum_processing_units",
                "MaximumProcessingUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pending_reserved_processing_units",
                "PendingReservedProcessingUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pool_id",
                "PoolID",
                "int",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "available_proc_units",
                "AvailableProcUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "pool_name",
                "PoolName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "SharedProcessorPool_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SharedStoragePool": [
        null,
        [
            [
                "logical_units",
                "LogicalUnits",
                "LogicalUnit_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "multi_data_tier_configured",
                "MultiDataTierConfigured",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "shared_storage_pool_id",
                "SharedStoragePoolID",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "multi_failure_group_configured",
                "MultiFailureGroupConfigured",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "physical_volumes",
                "PhysicalVolumes",
                "PhysicalVolume_Collection.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "capacity",
                "Capacity",
                "Gigabyte.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "free_space",
                "FreeSpace",
                "Gigabyte.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "over_commit_space",
                "OverCommitSpace",
                "Gigabyte.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "total_logical_unit_size",
                "TotalLogicalUnitSize",
                "Gigabyte.Type",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "alert_threshold",
                "AlertThreshold",
                "Percent.Pattern",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "storage_pool_name",
                "StoragePoolName",
                "string",
                "cu",
                "r",
                "R",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "R",
                ""
            ]
        ]
    ],
    "SharedStoragePoolLogicalUnitVirtualTargetDevice": [
        "VirtualTargetDevice",
        [
            [
                "cluster_id",
                "ClusterID",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "path_name",
                "PathName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "raid_level",
                "RAIDLevel",
                "string",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SharedStoragePool_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "SystemCapabilities": [
        null,
        [
            [
                "active_logical_partition_mobility_capable",
                "ActiveLogicalPartitionMobilityCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_logical_partition_shared_ide_processors_capable",
                "ActiveLogicalPartitionSharedIdeProcessorsCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_memory_deduplication_capable",
                "ActiveMemoryDeduplicationCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_memory_expansion_capable",
                "ActiveMemoryExpansionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_memory_mirroring_capable",
                "ActiveMemoryMirroringCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_memory_sharing_capable",
                "ActiveMemorySharingCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "active_system_optimizer_capable",
                "ActiveSystemOptimizerCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "address_broadcast_policy_capable",
                "AddressBroadcastPolicyCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "aix_capable",
                "AIXCapable",
                "AIXCapability.Enum",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "autorecovery_power_on_capable",
                "AutorecoveryPowerOnCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "barrier_synchronization_register_capable",
                "BarrierSynchronizationRegisterCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "capacity_on_demand_memory_capable",
                "CapacityOnDemandMemoryCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "capacity_on_demand_processor_capable",
                "CapacityOnDemandProcessorCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "custom_logical_partition_placement_capable",
                "CustomLogicalPartitionPlacementCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "custom_maximum_processes_per_logical_partition_capable",
                "CustomMaximumProcessesPerLogicalPartitionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "custom_system_placement_capable",
                "CustomSystemPlacementCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "electronic_error_reporting_capable",
                "ElectronicErrorReportingCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "external_intrusion_detection_capable",
                "ExternalIntrusionDetectionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "firmware_power_saver_capable",
                "FirmwarePowerSaverCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "hardware_discovery_capable",
                "HardwareDiscoveryCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "hardware_memory_compression_capable",
                "HardwareMemoryCompressionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "hardware_memory_encryption_capable",
                "HardwareMemoryEncryptionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "hardware_power_saver_capable",
                "HardwarePowerSaverCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "host_channel_adapter_capable",
                "HostChannelAdapterCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "huge_page_memory_capable",
                "HugePageMemoryCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "huge_page_memory_override_capable",
                "HugePageMemoryOverrideCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "ibm_i_capable",
                "IBMiCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "ibm_i_logical_partition_mobility_capable",
                "IBMiLogicalPartitionMobilityCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "ibm_i_logical_partition_suspend_capable",
                "IBMiLogicalPartitionSuspendCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "ibm_i_network_install_capable",
                "IBMiNetworkInstallCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "ibm_i_restricted_io_mode_capable",
                "IBMiRestrictedIOModeCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "inactive_logical_partition_mobility_capable",
                "InactiveLogicalPartitionMobilityCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "intelligent_platform_management_interface_capable",
                "IntelligentPlatformManagementInterfaceCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "linux_capable",
                "LinuxCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_host_ethernet_adapter_capable",
                "LogicalHostEthernetAdapterCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_affinity_group_capable",
                "LogicalPartitionAffinityGroupCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_availability_priority_capable",
                "LogicalPartitionAvailabilityPriorityCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_energy_management_capable",
                "LogicalPartitionEnergyManagementCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_processor_compatibility_mode_capable",
                "LogicalPartitionProcessorCompatibilityModeCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_remote_restart_capable",
                "LogicalPartitionRemoteRestartCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "logical_partition_suspend_capable",
                "LogicalPartitionSuspendCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "memory_mirroring_capable",
                "MemoryMirroringCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "micro_logical_partition_capable",
                "MicroLogicalPartitionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "redundant_error_path_reporting_capable",
                "RedundantErrorPathReportingCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "remote_restart_toggle_capable",
                "RemoteRestartToggleCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "service_processor_concurrent_maintenance_capable",
                "ServiceProcessorConcurrentMaintenanceCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "service_processor_failover_capable",
                "ServiceProcessorFailoverCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "shared_ethernet_failover_capable",
                "SharedEthernetFailoverCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "shared_processor_pool_capable",
                "SharedProcessorPoolCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "sriov_capable",
                "SRIOVCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "switch_network_interface_message_passing_capable",
                "SwitchNetworkInterfaceMessagePassingCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "telnet5250_application_capable",
                "Telnet5250ApplicationCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "turbo_core_capable",
                "TurboCoreCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_ethernet_adapter_dynamic_logical_partition_capable",
                "VirtualEthernetAdapterDynamicLogicalPartitionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_ethernet_quality_of_service_capable",
                "VirtualEthernetQualityOfServiceCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_fiber_channel_capable",
                "VirtualFiberChannelCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_io_server_capable",
                "VirtualIOServerCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtualization_engine_technologies_activation_capable",
                "VirtualizationEngineTechnologiesActivationCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_server_networking_phase2_capable",
                "VirtualServerNetworkingPhase2Capable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_server_protection_capable",
                "VirtualServerProtectionCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_switch_capable",
                "VirtualSwitchCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_trusted_platform_module_capable",
                "VirtualTrustedPlatformModuleCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "vlan_statistics_capable",
                "VLANStatisticsCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ],
            [
                "virtual_ethernet_custom_mac_address_capable",
                "VirtualEthernetCustomMACAddressCapable",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "management_vlan_for_control_channel_capable",
                "ManagementVLANForControlChannelCapable",
                "boolean",
                "ro",
                "o",
                "D",
                ""
            ]
        ]
    ],
    "SystemIOConfiguration": [
        null,
        [
            [
                "available_wwp_ns",
                "AvailableWWPNs",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "host_channel_adapters",
                "HostChannelAdapters",
                "HostChannelAdapter_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "host_ethernet_adapters",
                "HostEthernetAdapters",
                "HostEthernetAdapter_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "io_adapters",
                "IOAdapters",
                "IOAdapterChoiceCollection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "io_buses",
                "IOBuses",
                "IOBus_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "io_slots",
                "IOSlots",
                "IOSlot_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_io_pools",
                "MaximumIOPools",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "sriov_adapters",
                "SRIOVAdapters",
                "IOAdapterChoiceCollection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "associated_system_virtual_network",
                "AssociatedSystemVirtualNetwork",
                "SystemVirtualNetwork.Type",
                "cu",
                "d",
                "D",
                "SystemNetwork"
            ],
            [
                "wwpn_prefix",
                "WWPNPrefix",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SystemMemoryConfiguration": [
        null,
        [
            [
                "allowed_hardware_page_table_rations",
                "AllowedHardwarePageTableRations",
                "HardwarePageTableRatioExponent.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "allowed_memory_deduplication_table_ratios",
                "AllowedMemoryDeduplicationTableRatios",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "allowed_memory_region_size",
                "AllowedMemoryRegionSize",
                "string",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "available_barrier_synchronization_register_arrays",
                "AvailableBarrierSynchronizationRegisterArrays",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "barrier_synchronization_register_array_size",
                "BarrierSynchronizationRegisterArraySize",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "configurable_huge_pages",
                "ConfigurableHugePages",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "configurable_system_memory",
                "ConfigurableSystemMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "configured_mirrored_memory",
                "ConfiguredMirroredMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "current_address_broadcast_policy",
                "CurrentAddressBroadcastPolicy",
                "AddressBroadcastPerformancePolicy.Enum",
                "ro",
                "r",
                "D",
                "Hypervisor"
            ],
            [
                "current_available_huge_pages",
                "CurrentAvailableHugePages",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_available_mirrored_memory",
                "CurrentAvailableMirroredMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_available_system_memory",
                "CurrentAvailableSystemMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_logical_memory_block_size",
                "CurrentLogicalMemoryBlockSize",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_memory_mirroring_mode",
                "CurrentMemoryMirroringMode",
                "MemoryMirroringMode.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_mirrored_memory",
                "CurrentMirroredMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "deconfigured_system_memory",
                "DeconfiguredSystemMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "default_hardware_page_table_ratio",
                "DefaultHardwarePageTableRatio",
                "HardwarePageTableRatioExponent.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "default_hardware_paging_table_ratio_for_dedicated_memory_partition",
                "DefaultHardwarePagingTableRatioForDedicatedMemoryPartition",
                "HardwarePageTableRatioExponent.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "default_memory_deduplication_table_ratio",
                "DefaultMemoryDeduplicationTableRatio",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "huge_page_count",
                "HugePageCount",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "huge_page_size",
                "HugePageSize",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "installed_system_memory",
                "InstalledSystemMemory",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_huge_pages",
                "MaximumHugePages",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_memory_pool_count",
                "MaximumMemoryPoolCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_mirrored_memory_defragmented",
                "MaximumMirroredMemoryDefragmented",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maximum_paging_virtual_io_servers_per_shared_memory_pool",
                "MaximumPagingVirtualIOServersPerSharedMemoryPool",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "memory_defragmentation_state",
                "MemoryDefragmentationState",
                "MemoryDefragStatus.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "memory_mirroring_state",
                "MemoryMirroringState",
                "MemoryMirroringState.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "memory_region_size",
                "MemoryRegionSize",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "memory_used_by_hypervisor",
                "MemoryUsedByHypervisor",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_memory_pool_size",
                "MinimumMemoryPoolSize",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_required_memory_for_aix_and_linux",
                "MinimumRequiredMemoryForAIXAndLinux",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_required_memory_for_ibm_i",
                "MinimumRequiredMemoryForIBMi",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_required_memory_for_virtual_io_server",
                "MinimumRequiredMemoryForVirtualIOServer",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "mirrorable_memory_with_defragmentation",
                "MirrorableMemoryWithDefragmentation",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "mirrorable_memory_without_defragmentation",
                "MirrorableMemoryWithoutDefragmentation",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "mirrored_memory_used_by_hypervisor",
                "MirroredMemoryUsedByHypervisor",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "partition_maximum_memory_lower_limit",
                "PartitionMaximumMemoryLowerLimit",
                "Megabyte.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "pending_address_broadcast_policy",
                "PendingAddressBroadcastPolicy",
                "AddressBroadcastPerformancePolicy.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_available_huge_pages",
                "PendingAvailableHugePages",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_available_system_memory",
                "PendingAvailableSystemMemory",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_logical_memory_block_size",
                "PendingLogicalMemoryBlockSize",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_memory_mirroring_mode",
                "PendingMemoryMirroringMode",
                "MemoryMirroringMode.Enum",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "pending_memory_region_size",
                "PendingMemoryRegionSize",
                "Megabyte.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "requested_huge_pages",
                "RequestedHugePages",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "temporary_memory_for_logical_partition_mobility_in_use",
                "TemporaryMemoryForLogicalPartitionMobilityInUse",
                "boolean",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "total_barrier_synchronization_register_arrays",
                "TotalBarrierSynchronizationRegisterArrays",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "shared_memory_pool",
                "SharedMemoryPool",
                "SharedMemoryPool_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SystemMigrationInformation": [
        null,
        [
            [
                "maximum_inactive_migrations",
                "MaximumInactiveMigrations",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_active_migrations",
                "MaximumActiveMigrations",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "number_of_inactive_migrations_in_progress",
                "NumberOfInactiveMigrationsInProgress",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "number_of_active_migrations_in_progress",
                "NumberOfActiveMigrationsInProgress",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_firmware_active_migrations",
                "MaximumFirmwareActiveMigrations",
                "UINT16.Type",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SystemProcessorConfiguration": [
        null,
        [
            [
                "configurable_system_processor_units",
                "ConfigurableSystemProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_available_system_processor_units",
                "CurrentAvailableSystemProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_processors_per_aix_or_linux_partition",
                "CurrentMaximumProcessorsPerAIXOrLinuxPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_processors_per_ibm_i_partition",
                "CurrentMaximumProcessorsPerIBMiPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_allowed_processors_per_partition",
                "CurrentMaximumAllowedProcessorsPerPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_processors_per_virtual_io_server_partition",
                "CurrentMaximumProcessorsPerVirtualIOServerPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_virtual_processors_per_aix_or_linux_partition",
                "CurrentMaximumVirtualProcessorsPerAIXOrLinuxPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_virtual_processors_per_ibm_i_partition",
                "CurrentMaximumVirtualProcessorsPerIBMiPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "current_maximum_virtual_processors_per_virtual_io_server_partition",
                "CurrentMaximumVirtualProcessorsPerVirtualIOServerPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "deconfigured_system_processor_units",
                "DeconfiguredSystemProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                "Hypervisor"
            ],
            [
                "installed_system_processor_units",
                "InstalledSystemProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_processor_units_per_ibm_i_partition",
                "MaximumProcessorUnitsPerIBMiPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "maximum_allowed_virtual_processors_per_partition",
                "MaximumAllowedVirtualProcessorsPerPartition",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "minimum_processor_units_per_virtual_processor",
                "MinimumProcessorUnitsPerVirtualProcessor",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "number_of_all_os_processor_units",
                "NumberOfAllOSProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "number_of_linux_only_processor_units",
                "NumberOfLinuxOnlyProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "number_of_virtual_io_server_processor_units",
                "NumberOfVirtualIOServerProcessorUnits",
                "ProcessorUnit.Type",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "pending_available_system_processor_units",
                "PendingAvailableSystemProcessorUnits",
                "ProcessorUnit.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "shared_processor_pool_count",
                "SharedProcessorPoolCount",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "supported_partition_processor_compatibility_modes",
                "SupportedPartitionProcessorCompatibilityModes",
                "LogicalPartitionProcessorCompatibilityMode.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "temporary_processor_units_for_logical_partition_mobility_in_use",
                "TemporaryProcessorUnitsForLogicalPartitionMobilityInUse",
                "boolean",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "turbo_core_support",
                "TurboCoreSupport",
                "TurboCoreSupport.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "shared_processor_pool",
                "SharedProcessorPool",
                "SharedProcessorPool_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SystemSecurity": [
        null,
        [
            [
                "virtual_trusted_platform_module_key_length",
                "VirtualTrustedPlatformModuleKeyLength",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "virtual_trusted_platform_module_key_status",
                "VirtualTrustedPlatformModuleKeyStatus",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "virtual_trusted_platform_module_key_status_flags",
                "VirtualTrustedPlatformModuleKeyStatusFlags",
                "int",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "virtual_trusted_platform_module_version",
                "VirtualTrustedPlatformModuleVersion",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "SystemVirtualNetwork": [
        null,
        [
            [
                "maximum_vla_ns_per_port",
                "MaximumVLANsPerPort",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "network_bridges",
                "NetworkBridges",
                "NetworkBridge_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_ethernet_adapter_mac_address_prefix",
                "VirtualEthernetAdapterMACAddressPrefix",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_networks",
                "VirtualNetworks",
                "VirtualNetwork_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_switches",
                "VirtualSwitches",
                "VirtualSwitch_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SystemVirtualStorage": [
        null,
        [
            [
                "shared_storage_pools",
                "SharedStoragePools",
                "SharedStoragePool_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "storage_pools",
                "StoragePools",
                "VolumeGroup_Links.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_media_repositories",
                "VirtualMediaRepositories",
                "VirtualMediaRepository_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "virtual_optical_devices",
                "VirtualOpticalDevices",
                "VirtualOpticalTargetDevice_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "SystemVirtualStorage_Collection": [
        null,
        [
            [
                "system_virtual_storage",
                "SystemVirtualStorage",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "TrunkAdapter": [
        "VirtualEthernetAdapter",
        [
            [
                "trunk_priority",
                "TrunkPriority",
                "int",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "TrunkAdapter_Collection": [
        null,
        [
            [
                "trunk_adapter",
                "TrunkAdapter",
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
                "build_level",
                "BuildLevel",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "maintenance",
                "Maintenance",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "minor",
                "Minor",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "release",
                "Release",
                "int",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "service_pack_name",
                "ServicePackName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "version",
                "Version",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "version_date",
                "VersionDate",
                "long",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "VirtualDisk": [
        "VirtualSCSIStorage",
        [
            [
                "disk_capacity",
                "DiskCapacity",
                "Gigabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "disk_label",
                "DiskLabel",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "disk_name",
                "DiskName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "max_logical_volumes",
                "MaxLogicalVolumes",
                "int",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "partition_size",
                "PartitionSize",
                "Gigabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "volume_group",
                "VolumeGroup",
                "link rel=VolumeGroup",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualDisk_Collection": [
        null,
        [
            [
                "virtual_disk",
                "VirtualDisk",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualEnvironmentConfiguration": [
        null,
        [
            [
                "active_memory_sharing",
                "ActiveMemorySharing",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "partition_mobility",
                "PartitionMobility",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "remote_restart",
                "RemoteRestart",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "suspend_resume",
                "SuspendResume",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "uses_shared_storage_pool",
                "UsesSharedStoragePool",
                "boolean",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualEthernetAdapter": [
        "VirtualIOAdapter",
        [
            [
                "allowed_operating_system_mac_addresses",
                "AllowedOperatingSystemMACAddresses",
                "AllowedMACAddresses.Union",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "mac_address",
                "MACAddress",
                "MACAddress.Pattern",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "port_vlan_id",
                "PortVLANID",
                "VLANID.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "quality_of_service_priority",
                "QualityOfServicePriority",
                "QualityOfServicePriority.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "quality_of_service_priority_enabled",
                "QualityOfServicePriorityEnabled",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "tagged_vlan_ids",
                "TaggedVLANIDs",
                "VLANID.List",
                "cu",
                "a",
                "I",
                ""
            ],
            [
                "tagged_vlan_supported",
                "TaggedVLANSupported",
                "boolean",
                "cu",
                "a",
                "I",
                ""
            ],
            [
                "virtual_station_interface_manager_id",
                "VirtualStationInterfaceManagerID",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "virtual_station_interface_type_id",
                "VirtualStationInterfaceTypeID",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "associated_virtual_switch",
                "AssociatedVirtualSwitch",
                "VirtualSwitch_Links.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "virtual_switch_id",
                "VirtualSwitchID",
                "short",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "virtual_station_interface_type_version",
                "VirtualStationInterfaceTypeVersion",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "device_name",
                "DeviceName",
                "string",
                "ro",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelAdapter": [
        "VirtualIOAdapter",
        [
            [
                "adapter_name",
                "AdapterName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "connecting_partition",
                "ConnectingPartition",
                "link rel=BasePartition",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "connecting_partition_id",
                "ConnectingPartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "connecting_virtual_slot_number",
                "ConnectingVirtualSlotNumber",
                "VirtualIOSlotIndex.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelClientAdapter": [
        "VirtualFibreChannelAdapter",
        [
            [
                "server_adapter",
                "ServerAdapter",
                "VirtualFibreChannelServerAdapter.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "wwp_ns",
                "WWPNs",
                "WWPN2.List",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "nport_logged_in_status",
                "NportLoggedInStatus",
                "VirtualFibreChannelNPortLoginStatus_Collection.Type",
                "uo",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelClientAdapter_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelMapping": [
        null,
        [
            [
                "associated_logical_partition",
                "AssociatedLogicalPartition",
                "link rel=LogicalPartition",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "client_adapter",
                "ClientAdapter",
                "VirtualFibreChannelClientAdapter.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "port",
                "Port",
                "PhysicalFibreChannelPort.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "server_adapter",
                "ServerAdapter",
                "VirtualFibreChannelServerAdapter.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelMapping_Collection": [
        null,
        [
            [
                "virtual_fibre_channel_mapping",
                "VirtualFibreChannelMapping",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelNPortLoginStatus": [
        null,
        [
            [
                "wwpn",
                "WWPN",
                "WWPN.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "wwpn_status",
                "WWPNStatus",
                "WWPNStatus.Enum",
                "uo",
                "d",
                "D",
                ""
            ],
            [
                "logged_in_by",
                "LoggedInBy",
                "WWPNLoggedInBy.Enum",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "status_reason",
                "StatusReason",
                "string",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelNPortLoginStatus_Collection": [
        null,
        [
            [
                "virtual_fibre_channel_n_port_login_status",
                "VirtualFibreChannelNPortLoginStatus",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualFibreChannelServerAdapter": [
        "VirtualFibreChannelAdapter",
        [
            [
                "map_port",
                "MapPort",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "physical_port",
                "PhysicalPort",
                "PhysicalFibreChannelPort.Type",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "VirtualIOAdapter": [
        null,
        [
            [
                "adapter_type",
                "AdapterType",
                "VirtualIOAdapterType.Enum",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "dynamic_reconfiguration_connector_name",
                "DynamicReconfigurationConnectorName",
                "string",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "location_code",
                "LocationCode",
                "PhysicalLocation.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "local_partition_id",
                "LocalPartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "required_adapter",
                "RequiredAdapter",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "varied_on",
                "VariedOn",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "use_next_available_slot_id",
                "UseNextAvailableSlotID",
                "boolean",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "virtual_slot_number",
                "VirtualSlotNumber",
                "VirtualIOSlotIndex.Type",
                "cu",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "VirtualIOServer": [
        "BasePartition",
        [
            [
                "api_capable",
                "APICapable",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "server_install_configuration",
                "ServerInstallConfiguration",
                "VirtualIOServerInstallConfiguration.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "link_aggregations",
                "LinkAggregations",
                "LinkAggregation_Links.Type",
                "cu",
                "d",
                "R",
                "ViosNetwork"
            ],
            [
                "manager_passthrough_capable",
                "ManagerPassthroughCapable",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "media_repositories",
                "MediaRepositories",
                "VirtualMediaRepository_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosStorage"
            ],
            [
                "mover_service_partition",
                "MoverServicePartition",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "network_boot_devices",
                "NetworkBootDevices",
                "NetworkBootDevice_Collection.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "paging_service_partition",
                "PagingServicePartition",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "physical_volumes",
                "PhysicalVolumes",
                "PhysicalVolume_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosStorage"
            ],
            [
                "shared_ethernet_adapters",
                "SharedEthernetAdapters",
                "SharedEthernetAdapter_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosNetwork"
            ],
            [
                "shared_storage_pool_capable",
                "SharedStoragePoolCapable",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "shared_storage_pool_version",
                "SharedStoragePoolVersion",
                "VersionReleaseMaintenance.Type",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "storage_pools",
                "StoragePools",
                "VolumeGroup_Links.Type",
                "cu",
                "d",
                "R",
                "ViosStorage"
            ],
            [
                "trunk_adapters",
                "TrunkAdapters",
                "TrunkAdapter_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosNetwork"
            ],
            [
                "virtual_io_server_license",
                "VirtualIOServerLicense",
                "string",
                "ro",
                "r",
                "R",
                ""
            ],
            [
                "virtual_io_server_license_accepted",
                "VirtualIOServerLicenseAccepted",
                "boolean",
                "cu",
                "d",
                "R",
                ""
            ],
            [
                "virtual_fibre_channel_mappings",
                "VirtualFibreChannelMappings",
                "VirtualFibreChannelMapping_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosFCMapping"
            ],
            [
                "virtual_scsi_mappings",
                "VirtualSCSIMappings",
                "VirtualSCSIMapping_Collection.Type",
                "cu",
                "d",
                "R",
                "ViosSCSIMapping"
            ],
            [
                "free_io_adapters_for_link_aggregation",
                "FreeIOAdaptersForLinkAggregation",
                "IOAdapterChoiceCollection.Type",
                "ro",
                "r",
                "R",
                "ViosNetwork"
            ],
            [
                "free_ethenet_backing_devices_for_sea",
                "FreeEthenetBackingDevicesForSEA",
                "IOAdapterChoiceCollection.Type",
                "ro",
                "r",
                "R",
                "ViosNetwork"
            ]
        ]
    ],
    "VirtualIOServerInstallConfiguration": [
        null,
        [
            [
                "address",
                "Address",
                "IPAddress.Union",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "boot_device",
                "BootDevice",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "boot_mac_address",
                "BootMACAddress",
                "MACAddress.Pattern",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "configured_duplex_mode",
                "ConfiguredDuplexMode",
                "DuplexMode.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "configured_speed",
                "ConfiguredSpeed",
                "ConnectionSpeed.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "gateway",
                "Gateway",
                "IPAddress.Union",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "image_source",
                "ImageSource",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "installation_type",
                "InstallationType",
                "InstallationType.Enum",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "management_console_nic",
                "ManagementConsoleNIC",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "network_install_manager_address",
                "NetworkInstallManagerAddress",
                "IPAddress.Union",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "subnet_mask",
                "SubnetMask",
                "IPAddress.Union",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualIOServer_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualMediaRepository": [
        null,
        [
            [
                "optical_media",
                "OpticalMedia",
                "VirtualOpticalMedia_Collection.Type",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "repository_name",
                "RepositoryName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "repository_size",
                "RepositorySize",
                "Gigabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualMediaRepository_Collection": [
        null,
        [
            [
                "virtual_media_repository",
                "VirtualMediaRepository",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualNetwork": [
        null,
        [
            [
                "associated_switch",
                "AssociatedSwitch",
                "link rel=VirtualSwitch",
                "co",
                "d",
                "I",
                ""
            ],
            [
                "network_name",
                "NetworkName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "network_vlan_id",
                "NetworkVLANID",
                "VLANID.Type",
                "co",
                "d",
                "I",
                ""
            ],
            [
                "vswitch_id",
                "VswitchID",
                "int",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "tagged_network",
                "TaggedNetwork",
                "boolean",
                "co",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VirtualNetwork_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualOpticalMedia": [
        "VirtualSCSIStorage",
        [
            [
                "media_name",
                "MediaName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "media_udid",
                "MediaUDID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ],
            [
                "mount_type",
                "MountType",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "size",
                "Size",
                "Gigabyte.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualOpticalMedia_Collection": [
        null,
        [
            [
                "virtual_optical_media",
                "VirtualOpticalMedia",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualOpticalTargetDevice": [
        "VirtualTargetDevice",
        [
            [
                "virtual_optical_media",
                "VirtualOpticalMedia",
                "VirtualOpticalMedia_Collection.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualOpticalTargetDevice_Collection": [
        null,
        [
            [
                "virtual_optical_target_device",
                "VirtualOpticalTargetDevice",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualSCSIAdapter": [
        "VirtualIOAdapter",
        [
            [
                "adapter_name",
                "AdapterName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "backing_device_name",
                "BackingDeviceName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "remote_backing_device_name",
                "RemoteBackingDeviceName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "remote_logical_partition_id",
                "RemoteLogicalPartitionID",
                "PartitionID.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "remote_slot_number",
                "RemoteSlotNumber",
                "int",
                "cu",
                "a",
                "I",
                ""
            ],
            [
                "server_location_code",
                "ServerLocationCode",
                "PhysicalLocation.Pattern",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "I",
                ""
            ]
        ]
    ],
    "VirtualSCSIClientAdapter": [
        "VirtualSCSIAdapter",
        [
            [
                "server_adapter",
                "ServerAdapter",
                "VirtualSCSIServerAdapter.Type",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VirtualSCSIClientAdapter_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualSCSIMapping": [
        null,
        [
            [
                "associated_logical_partition",
                "AssociatedLogicalPartition",
                "link rel=LogicalPartition",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "client_adapter",
                "ClientAdapter",
                "VirtualSCSIClientAdapter.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "server_adapter",
                "ServerAdapter",
                "VirtualSCSIServerAdapter.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "storage",
                "Storage",
                "VirtualSCSIStorageChoice.Type",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "target_device",
                "TargetDevice",
                "VirtualTargetDeviceChoice.Type",
                "cu",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VirtualSCSIMapping_Collection": [
        null,
        [
            [
                "virtual_scsi_mapping",
                "VirtualSCSIMapping",
                "_Collection.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualSCSIServerAdapter": [
        "VirtualSCSIAdapter",
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VirtualSCSIStorage": [
        null,
        [
            [
                "dummy",
                "Dummy",
                "string",
                "cu",
                "d",
                "D",
                ""
            ]
        ]
    ],
    "VirtualSwitch": [
        null,
        [
            [
                "switch_id",
                "SwitchID",
                "short",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "switch_mode",
                "SwitchMode",
                "VirtualSwitchMode.Enum",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "switch_name",
                "SwitchName",
                "string",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "virtual_networks",
                "VirtualNetworks",
                "VirtualNetwork_Links.Type",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VirtualSwitch_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ],
    "VirtualTargetDevice": [
        null,
        [
            [
                "logical_unit_address",
                "LogicalUnitAddress",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "parent_name",
                "ParentName",
                "string",
                "cu",
                "d",
                "D",
                ""
            ],
            [
                "target_name",
                "TargetName",
                "string",
                "cu",
                "r",
                "D",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "D",
                ""
            ]
        ]
    ],
    "VolumeGroup": [
        null,
        [
            [
                "available_size",
                "AvailableSize",
                "Gigabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "backing_device_count",
                "BackingDeviceCount",
                "int",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "free_space",
                "FreeSpace",
                "Gigabyte.Type",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "group_capacity",
                "GroupCapacity",
                "Gigabyte.Type",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "group_name",
                "GroupName",
                "string",
                "cu",
                "r",
                "I",
                ""
            ],
            [
                "group_serial_id",
                "GroupSerialID",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "group_state",
                "GroupState",
                "string",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "maximum_logical_volumes",
                "MaximumLogicalVolumes",
                "int",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "media_repositories",
                "MediaRepositories",
                "VirtualMediaRepository_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "minimum_allocation_size",
                "MinimumAllocationSize",
                "Gigabyte.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "physical_volumes",
                "PhysicalVolumes",
                "PhysicalVolume_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ],
            [
                "unique_device_id",
                "UniqueDeviceID",
                "UDID.Pattern",
                "ro",
                "r",
                "I",
                ""
            ],
            [
                "virtual_disks",
                "VirtualDisks",
                "VirtualDisk_Collection.Type",
                "cu",
                "d",
                "I",
                ""
            ]
        ]
    ],
    "VolumeGroup_Links": [
        null,
        [
            [
                "link",
                "link",
                "_Links.Type",
                "cu",
                "r",
                "",
                ""
            ]
        ]
    ]
}"""
k2attr = json.loads(_k2attr_json)
_k2choice_json = """{
    "IOAdapterChoiceCollection": [
        "IOAdapterChoice"
    ],
    "IOSlot": [
        "RelatedIOAdapter"
    ],
    "ProfileVirtualIOAdapterChoiceCollection": [
        "ProfileVirtualIOAdapterChoice"
    ],
    "SharedEthernetAdapter": [
        "BackingDeviceChoice"
    ],
    "VirtualSCSIMapping": [
        "Storage",
        "TargetDevice"
    ]
}"""
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

typeset = set([_class_for_name("paxes_cinder.k2aclient.v1.k2uom",k)
    for k in k2attr.keys()])
_attr_cc_to_us_json = """{
    "AIXCapable": "aix_capable",
    "APICapable": "api_capable",
    "ActivatedLevel": "activated_level",
    "ActivatedServicePackAndLevel": "activated_service_pack_and_level",
    "ActiveLogicalPartitionMobilityCapable": "active_logical_partition_mobility_capable",
    "ActiveLogicalPartitionSharedIdeProcessorsCapable": "active_logical_partition_shared_ide_processors_capable",
    "ActiveMemoryDeduplicationCapable": "active_memory_deduplication_capable",
    "ActiveMemoryExpansionCapable": "active_memory_expansion_capable",
    "ActiveMemoryExpansionEnabled": "active_memory_expansion_enabled",
    "ActiveMemoryMirroringCapable": "active_memory_mirroring_capable",
    "ActiveMemorySharing": "active_memory_sharing",
    "ActiveMemorySharingCapable": "active_memory_sharing_capable",
    "ActiveMemorySharingEnabled": "active_memory_sharing_enabled",
    "ActiveSystemOptimizerCapable": "active_system_optimizer_capable",
    "AdapterID": "adapter_id",
    "AdapterMode": "adapter_mode",
    "AdapterName": "adapter_name",
    "AdapterState": "adapter_state",
    "AdapterType": "adapter_type",
    "Address": "address",
    "AddressBroadcastPolicyCapable": "address_broadcast_policy_capable",
    "AddressToPing": "address_to_ping",
    "AffinityGroupID": "affinity_group_id",
    "AlertThreshold": "alert_threshold",
    "AllocatedCapacity": "allocated_capacity",
    "AllocatedVirtualProcessors": "allocated_virtual_processors",
    "AllocationAllowed": "allocation_allowed",
    "AllowPerformanceDataCollection": "allow_performance_data_collection",
    "AllowedHardwarePageTableRations": "allowed_hardware_page_table_rations",
    "AllowedMACAddresses": "allowed_mac_addresses",
    "AllowedMemoryDeduplicationTableRatios": "allowed_memory_deduplication_table_ratios",
    "AllowedMemoryRegionSize": "allowed_memory_region_size",
    "AllowedOSMACAddresses": "allowed_osmac_addresses",
    "AllowedOperatingSystemMACAddresses": "allowed_operating_system_mac_addresses",
    "AllowedVLANIDs": "allowed_vlani_ds",
    "AllowedVLANs": "allowed_vla_ns",
    "AlternateAddress": "alternate_address",
    "AlternateConsole": "alternate_console",
    "AlternateLoadSource": "alternate_load_source",
    "AlternateLoadSourceAttached": "alternate_load_source_attached",
    "AssignAllResources": "assign_all_resources",
    "AssignedPartitions": "assigned_partitions",
    "AssignedUUIDs": "assigned_uui_ds",
    "AssignedVirtualIOServer": "assigned_virtual_io_server",
    "AssociatedIOSlot": "associated_io_slot",
    "AssociatedIPLConfiguration": "associated_ipl_configuration",
    "AssociatedLogicalPartition": "associated_logical_partition",
    "AssociatedLogicalPartitions": "associated_logical_partitions",
    "AssociatedManagedSystem": "associated_managed_system",
    "AssociatedPartition": "associated_partition",
    "AssociatedPartitionProfile": "associated_partition_profile",
    "AssociatedPowerEnterprisePool": "associated_power_enterprise_pool",
    "AssociatedReservedStorageDevicePool": "associated_reserved_storage_device_pool",
    "AssociatedSwitch": "associated_switch",
    "AssociatedSystemCapabilities": "associated_system_capabilities",
    "AssociatedSystemIOConfiguration": "associated_system_io_configuration",
    "AssociatedSystemMemoryConfiguration": "associated_system_memory_configuration",
    "AssociatedSystemProcessorConfiguration": "associated_system_processor_configuration",
    "AssociatedSystemSecurity": "associated_system_security",
    "AssociatedSystemVirtualNetwork": "associated_system_virtual_network",
    "AssociatedSystemVirtualStorage": "associated_system_virtual_storage",
    "AssociatedVirtualEnvironmentConfiguration": "associated_virtual_environment_configuration",
    "AssociatedVirtualIOServers": "associated_virtual_io_servers",
    "AssociatedVirtualSwitch": "associated_virtual_switch",
    "Atom": "atom",
    "AtomCreated": "atom_created",
    "AtomID": "atom_id",
    "AutoEntitledMemoryEnabled": "auto_entitled_memory_enabled",
    "AutoRecoveryEnabled": "auto_recovery_enabled",
    "AutoStart": "auto_start",
    "AutorecoveryPowerOnCapable": "autorecovery_power_on_capable",
    "AvailabilityPriority": "availability_priority",
    "AvailableBarrierSynchronizationRegisterArrays": "available_barrier_synchronization_register_arrays",
    "AvailableForUsage": "available_for_usage",
    "AvailableMobileCoDMemory": "available_mobile_co_d_memory",
    "AvailableMobileCoDProcUnits": "available_mobile_co_d_proc_units",
    "AvailablePhysicalPartitions": "available_physical_partitions",
    "AvailablePorts": "available_ports",
    "AvailableProcUnits": "available_proc_units",
    "AvailableSize": "available_size",
    "AvailableWWPNs": "available_wwp_ns",
    "BackingDeviceChoice": "backing_device_choice",
    "BackingDeviceCount": "backing_device_count",
    "BackingDeviceName": "backing_device_name",
    "BackplanePhysicalLocation": "backplane_physical_location",
    "BackupAdapter": "backup_adapter",
    "BarrierSynchronizationRegisterArrayCount": "barrier_synchronization_register_array_count",
    "BarrierSynchronizationRegisterArraySize": "barrier_synchronization_register_array_size",
    "BarrierSynchronizationRegisterCapable": "barrier_synchronization_register_capable",
    "BootDevice": "boot_device",
    "BootMACAddress": "boot_mac_address",
    "BootMode": "boot_mode",
    "BuildLevel": "build_level",
    "BusDynamicReconfigurationConnectorIndex": "bus_dynamic_reconfiguration_connector_index",
    "BusDynamicReconfigurationConnectorName": "bus_dynamic_reconfiguration_connector_name",
    "BusGroupingRequired": "bus_grouping_required",
    "CableType": "cable_type",
    "Cage": "cage",
    "CageID": "cage_id",
    "CageLocation": "cage_location",
    "Cages": "cages",
    "Capability": "capability",
    "Capacity": "capacity",
    "CapacityOnDemandMemoryCapable": "capacity_on_demand_memory_capable",
    "CapacityOnDemandProcessorCapable": "capacity_on_demand_processor_capable",
    "ClientAdapter": "client_adapter",
    "ClientNetworkAdapters": "client_network_adapters",
    "ClonedFrom": "cloned_from",
    "ClusterID": "cluster_id",
    "ClusterName": "cluster_name",
    "ClusterSharedStoragePool": "cluster_shared_storage_pool",
    "ComplianceRemainingHours": "compliance_remaining_hours",
    "ComplianceState": "compliance_state",
    "ConfigurableHugePages": "configurable_huge_pages",
    "ConfigurableSystemMemory": "configurable_system_memory",
    "ConfigurableSystemProcessorUnits": "configurable_system_processor_units",
    "ConfigurationID": "configuration_id",
    "ConfiguredCapacity": "configured_capacity",
    "ConfiguredConnectionSpeed": "configured_connection_speed",
    "ConfiguredDuplexMode": "configured_duplex_mode",
    "ConfiguredEthernetLogicalPorts": "configured_ethernet_logical_ports",
    "ConfiguredFiberChannelOverEthernetLogicalPorts": "configured_fiber_channel_over_ethernet_logical_ports",
    "ConfiguredMTU": "configured_mtu",
    "ConfiguredMaxEthernetLogicalPorts": "configured_max_ethernet_logical_ports",
    "ConfiguredMaxFiberChannelOverEthernetLogicalPorts": "configured_max_fiber_channel_over_ethernet_logical_ports",
    "ConfiguredMirroredMemory": "configured_mirrored_memory",
    "ConfiguredOptions": "configured_options",
    "ConfiguredSpeed": "configured_speed",
    "ConnectingPartition": "connecting_partition",
    "ConnectingPartitionID": "connecting_partition_id",
    "ConnectingVirtualSlotNumber": "connecting_virtual_slot_number",
    "ConnectionMonitoringEnabled": "connection_monitoring_enabled",
    "Console": "console",
    "ConsoleCapable": "console_capable",
    "ControlChannelID": "control_channel_id",
    "ControlChannelInterfaceName": "control_channel_interface_name",
    "ConvergedEthernetPhysicalPorts": "converged_ethernet_physical_ports",
    "CurrentAddressBroadcastPolicy": "current_address_broadcast_policy",
    "CurrentAllocatedBarrierSynchronizationRegisterArrays": "current_allocated_barrier_synchronization_register_arrays",
    "CurrentAvailableHugePages": "current_available_huge_pages",
    "CurrentAvailableMirroredMemory": "current_available_mirrored_memory",
    "CurrentAvailablePoolMemory": "current_available_pool_memory",
    "CurrentAvailableSystemMemory": "current_available_system_memory",
    "CurrentAvailableSystemProcessorUnits": "current_available_system_processor_units",
    "CurrentBarrierSynchronizationRegisterArrays": "current_barrier_synchronization_register_arrays",
    "CurrentConnectionSpeed": "current_connection_speed",
    "CurrentDedicatedProcessorConfiguration": "current_dedicated_processor_configuration",
    "CurrentDuplexMode": "current_duplex_mode",
    "CurrentEntitledMemory": "current_entitled_memory",
    "CurrentExpansionFactor": "current_expansion_factor",
    "CurrentHardwarePageTableRatio": "current_hardware_page_table_ratio",
    "CurrentHasDedicatedProcessors": "current_has_dedicated_processors",
    "CurrentHugePageCount": "current_huge_page_count",
    "CurrentLogicalMemoryBlockSize": "current_logical_memory_block_size",
    "CurrentMACAddress": "current_mac_address",
    "CurrentManufacturingDefaulConfigurationtBootMode": "current_manufacturing_defaul_configurationt_boot_mode",
    "CurrentMaximumAllowedProcessorsPerPartition": "current_maximum_allowed_processors_per_partition",
    "CurrentMaximumHugePageCount": "current_maximum_huge_page_count",
    "CurrentMaximumMemory": "current_maximum_memory",
    "CurrentMaximumPartitionsPerHostChannelAdapter": "current_maximum_partitions_per_host_channel_adapter",
    "CurrentMaximumPoolMemory": "current_maximum_pool_memory",
    "CurrentMaximumProcessingUnits": "current_maximum_processing_units",
    "CurrentMaximumProcessors": "current_maximum_processors",
    "CurrentMaximumProcessorsPerAIXOrLinuxPartition": "current_maximum_processors_per_aix_or_linux_partition",
    "CurrentMaximumProcessorsPerIBMiPartition": "current_maximum_processors_per_ibm_i_partition",
    "CurrentMaximumProcessorsPerVirtualIOServerPartition": "current_maximum_processors_per_virtual_io_server_partition",
    "CurrentMaximumVirtualIOSlots": "current_maximum_virtual_io_slots",
    "CurrentMaximumVirtualProcessors": "current_maximum_virtual_processors",
    "CurrentMaximumVirtualProcessorsPerAIXOrLinuxPartition": "current_maximum_virtual_processors_per_aix_or_linux_partition",
    "CurrentMaximumVirtualProcessorsPerIBMiPartition": "current_maximum_virtual_processors_per_ibm_i_partition",
    "CurrentMaximumVirtualProcessorsPerVirtualIOServerPartition": "current_maximum_virtual_processors_per_virtual_io_server_partition",
    "CurrentMemory": "current_memory",
    "CurrentMemoryMirroringMode": "current_memory_mirroring_mode",
    "CurrentMemoryWeight": "current_memory_weight",
    "CurrentMinimumHugePageCount": "current_minimum_huge_page_count",
    "CurrentMinimumMemory": "current_minimum_memory",
    "CurrentMinimumProcessingUnits": "current_minimum_processing_units",
    "CurrentMinimumProcessors": "current_minimum_processors",
    "CurrentMinimumVirtualProcessors": "current_minimum_virtual_processors",
    "CurrentMirroredMemory": "current_mirrored_memory",
    "CurrentMultiCoreScaling": "current_multi_core_scaling",
    "CurrentOptions": "current_options",
    "CurrentPagingServicePartition": "current_paging_service_partition",
    "CurrentPoolMemory": "current_pool_memory",
    "CurrentPowerOnSide": "current_power_on_side",
    "CurrentProcessingUnits": "current_processing_units",
    "CurrentProcessorCompatibilityMode": "current_processor_compatibility_mode",
    "CurrentProcessors": "current_processors",
    "CurrentProfileSync": "current_profile_sync",
    "CurrentReservedProcessingUnits": "current_reserved_processing_units",
    "CurrentSharedProcessorConfiguration": "current_shared_processor_configuration",
    "CurrentSharedProcessorPoolID": "current_shared_processor_pool_id",
    "CurrentSharingMode": "current_sharing_mode",
    "CurrentSystemKeylock": "current_system_keylock",
    "CurrentTurbocoreEnabled": "current_turbocore_enabled",
    "CurrentUncappedWeight": "current_uncapped_weight",
    "CustomLogicalPartitionPlacementCapable": "custom_logical_partition_placement_capable",
    "CustomMaximumProcessesPerLogicalPartitionCapable": "custom_maximum_processes_per_logical_partition_capable",
    "CustomSystemPlacementCapable": "custom_system_placement_capable",
    "DeconfiguredSystemMemory": "deconfigured_system_memory",
    "DeconfiguredSystemProcessorUnits": "deconfigured_system_processor_units",
    "Dedicated": "dedicated",
    "DedicatedProcessorConfiguration": "dedicated_processor_configuration",
    "DefaultFiberChannelTargetsForBackingDevice": "default_fiber_channel_targets_for_backing_device",
    "DefaultFiberChannelTargetsForNonBackingDevice": "default_fiber_channel_targets_for_non_backing_device",
    "DefaultHardwarePageTableRatio": "default_hardware_page_table_ratio",
    "DefaultHardwarePagingTableRatioForDedicatedMemoryPartition": "default_hardware_paging_table_ratio_for_dedicated_memory_partition",
    "DefaultMemoryDeduplicationTableRatio": "default_memory_deduplication_table_ratio",
    "Description": "description",
    "DesignatedIPLSource": "designated_ipl_source",
    "DesiredEntitledMemory": "desired_entitled_memory",
    "DesiredHugePageCount": "desired_huge_page_count",
    "DesiredMemory": "desired_memory",
    "DesiredProcessingUnits": "desired_processing_units",
    "DesiredProcessorCompatibilityMode": "desired_processor_compatibility_mode",
    "DesiredProcessors": "desired_processors",
    "DesiredVirtualProcessors": "desired_virtual_processors",
    "DetailedState": "detailed_state",
    "DeviceID": "device_id",
    "DeviceName": "device_name",
    "DeviceSelectionType": "device_selection_type",
    "DeviceSize": "device_size",
    "DeviceState": "device_state",
    "DeviceType": "device_type",
    "DirectOperationsConsoleCapable": "direct_operations_console_capable",
    "DiskCapacity": "disk_capacity",
    "DiskLabel": "disk_label",
    "DiskName": "disk_name",
    "Dummy": "dummy",
    "DynamicLogicalPartitionIOCapable": "dynamic_logical_partition_io_capable",
    "DynamicLogicalPartitionMemoryCapable": "dynamic_logical_partition_memory_capable",
    "DynamicLogicalPartitionProcessorCapable": "dynamic_logical_partition_processor_capable",
    "DynamicReconfigurationConnectorIndex": "dynamic_reconfiguration_connector_index",
    "DynamicReconfigurationConnectorName": "dynamic_reconfiguration_connector_name",
    "ElectronicErrorReportingCapable": "electronic_error_reporting_capable",
    "ElectronicErrorReportingEnabled": "electronic_error_reporting_enabled",
    "EngineeringChangeNumber": "engineering_change_number",
    "EthernetLogicalPorts": "ethernet_logical_ports",
    "EthernetPhysicalPorts": "ethernet_physical_ports",
    "EventData": "event_data",
    "EventDetail": "event_detail",
    "EventID": "event_id",
    "EventType": "event_type",
    "ExpansionFactor": "expansion_factor",
    "ExternalIntrusionDetectionCapable": "external_intrusion_detection_capable",
    "FailoverEnabled": "failover_enabled",
    "FeatureCodes": "feature_codes",
    "FiberChannelTargets": "fiber_channel_targets",
    "FiberChannelTargetsRoundingValue": "fiber_channel_targets_rounding_value",
    "FibreChannelOverEthernetLogicalPorts": "fibre_channel_over_ethernet_logical_ports",
    "FirmwarePowerSaverCapable": "firmware_power_saver_capable",
    "FrameCapability": "frame_capability",
    "FrameLocation": "frame_location",
    "FrameName": "frame_name",
    "FrameNumber": "frame_number",
    "FrameState": "frame_state",
    "FrameType": "frame_type",
    "FreeEthenetBackingDevicesForSEA": "free_ethenet_backing_devices_for_sea",
    "FreeIOAdaptersForLinkAggregation": "free_io_adapters_for_link_aggregation",
    "FreeMemoryDevicesFromPagingServicePartitionOne": "free_memory_devices_from_paging_service_partition_one",
    "FreeMemoryDevicesFromPagingServicePartitionTwo": "free_memory_devices_from_paging_service_partition_two",
    "FreeRedundantMemoryDevices": "free_redundant_memory_devices",
    "FreeSpace": "free_space",
    "Gateway": "gateway",
    "GroupCapacity": "group_capacity",
    "GroupName": "group_name",
    "GroupSerialID": "group_serial_id",
    "GroupState": "group_state",
    "HEALogicalPortPhysicalLocation": "hea_logical_port_physical_location",
    "HardwareDiscoveryCapable": "hardware_discovery_capable",
    "HardwareMemoryCompressionCapable": "hardware_memory_compression_capable",
    "HardwareMemoryEncryptionCapable": "hardware_memory_encryption_capable",
    "HardwarePageTableRatio": "hardware_page_table_ratio",
    "HardwarePowerSaverCapable": "hardware_power_saver_capable",
    "HasDedicatedProcessors": "has_dedicated_processors",
    "HasDedicatedProcessorsForMigration": "has_dedicated_processors_for_migration",
    "HashMode": "hash_mode",
    "HighAvailabilityMode": "high_availability_mode",
    "HighPercentage": "high_percentage",
    "HighSpeedLinkOpticonnectPool": "high_speed_link_opticonnect_pool",
    "HostChannelAdapter": "host_channel_adapter",
    "HostChannelAdapterCapable": "host_channel_adapter_capable",
    "HostChannelAdapters": "host_channel_adapters",
    "HostEthernetAdapterLogicalPort": "host_ethernet_adapter_logical_port",
    "HostEthernetAdapterLogicalPorts": "host_ethernet_adapter_logical_ports",
    "HostEthernetAdapterPhysicalPort": "host_ethernet_adapter_physical_port",
    "HostEthernetAdapterPortGroup": "host_ethernet_adapter_port_group",
    "HostEthernetAdapters": "host_ethernet_adapters",
    "HostName": "host_name",
    "Hostname": "hostname",
    "HugePageCount": "huge_page_count",
    "HugePageMemoryCapable": "huge_page_memory_capable",
    "HugePageMemoryOverrideCapable": "huge_page_memory_override_capable",
    "HugePageSize": "huge_page_size",
    "IBMiCapable": "ibm_i_capable",
    "IBMiLogicalPartitionMobilityCapable": "ibm_i_logical_partition_mobility_capable",
    "IBMiLogicalPartitionSuspendCapable": "ibm_i_logical_partition_suspend_capable",
    "IBMiNetworkInstallCapable": "ibm_i_network_install_capable",
    "IBMiRestrictedIOModeCapable": "ibm_i_restricted_io_mode_capable",
    "IEEE8021QAllowablePriorities": "ieee8021_q_allowable_priorities",
    "IEEE8021QPriority": "ieee8021_q_priority",
    "IIDPService": "iidp_service",
    "IOAdapterChoice": "io_adapter_choice",
    "IOAdapters": "io_adapters",
    "IOBus": "io_bus",
    "IOBusID": "io_bus_id",
    "IOBuses": "io_buses",
    "IOConfigurationInstance": "io_configuration_instance",
    "IOP": "iop",
    "IOPInfoStale": "iop_info_stale",
    "IOPoolID": "io_pool_id",
    "IOSlot": "io_slot",
    "IOSlots": "io_slots",
    "IOUnit": "io_unit",
    "IOUnitID": "io_unit_id",
    "IOUnitPhysicalLocation": "io_unit_physical_location",
    "IOUnitSystemPowerControlNetworkID": "io_unit_system_power_control_network_id",
    "IOUnits": "io_units",
    "IPAddress": "ip_address",
    "IPAddressToPing": "ip_address_to_ping",
    "IPInterface": "ip_interface",
    "IPV6Prefix": "ipv6_prefix",
    "ImageSource": "image_source",
    "InUse": "in_use",
    "InactiveLogicalPartitionMobilityCapable": "inactive_logical_partition_mobility_capable",
    "InactiveMemory": "inactive_memory",
    "InactiveProcUnits": "inactive_proc_units",
    "InstallationType": "installation_type",
    "InstalledSystemMemory": "installed_system_memory",
    "InstalledSystemProcessorUnits": "installed_system_processor_units",
    "IntelligentPlatformManagementInterfaceCapable": "intelligent_platform_management_interface_capable",
    "InterfaceName": "interface_name",
    "InternalAndExternalIntrusionDetectionCapable": "internal_and_external_intrusion_detection_capable",
    "IsBackupMasterConsole": "is_backup_master_console",
    "IsCallHomeEnabled": "is_call_home_enabled",
    "IsConnectionMonitoringEnabled": "is_connection_monitoring_enabled",
    "IsDebug": "is_debug",
    "IsDiagnostic": "is_diagnostic",
    "IsFibreChannelBacked": "is_fibre_channel_backed",
    "IsFunctional": "is_functional",
    "IsHugeDMA": "is_huge_dma",
    "IsMasterConsole": "is_master_console",
    "IsOperationInProgress": "is_operation_in_progress",
    "IsPhysicalDevice": "is_physical_device",
    "IsPower6Frame": "is_power6_frame",
    "IsPrimary": "is_primary",
    "IsPromiscous": "is_promiscous",
    "IsQualityOfServicePriorityEnabled": "is_quality_of_service_priority_enabled",
    "IsRedundant": "is_redundant",
    "IsRedundantErrorPathReportingEnabled": "is_redundant_error_path_reporting_enabled",
    "IsRequired": "is_required",
    "IsRestrictedIOPartition": "is_restricted_io_partition",
    "IsServicePartition": "is_service_partition",
    "IsTaggedVLANSupported": "is_tagged_vlan_supported",
    "IsTimeReferencePartition": "is_time_reference_partition",
    "IsVirtualServiceAttentionLEDOn": "is_virtual_service_attention_led_on",
    "IsVirtualTrustedPlatformModuleEnabled": "is_virtual_trusted_platform_module_enabled",
    "JumboFrameEnabled": "jumbo_frame_enabled",
    "JumboFramesEnabled": "jumbo_frames_enabled",
    "KeylockPosition": "keylock_position",
    "LANConsoleCapable": "lan_console_capable",
    "Label": "label",
    "LargeSend": "large_send",
    "LinkAggregations": "link_aggregations",
    "LinkStatus": "link_status",
    "LinkUp": "link_up",
    "LinuxCapable": "linux_capable",
    "LoadBalancingEnabled": "load_balancing_enabled",
    "LoadGroup": "load_group",
    "LoadGroups": "load_groups",
    "LoadSource": "load_source",
    "LoadSourceAttached": "load_source_attached",
    "LoadSourceCapable": "load_source_capable",
    "LocalPartitionID": "local_partition_id",
    "LocalVirtualIOServerImageNames": "local_virtual_io_server_image_names",
    "LocationCode": "location_code",
    "LoggedInBy": "logged_in_by",
    "LogicalHostEthernetAdapterCapable": "logical_host_ethernet_adapter_capable",
    "LogicalPartitionAffinityGroupCapable": "logical_partition_affinity_group_capable",
    "LogicalPartitionAvailabilityPriorityCapable": "logical_partition_availability_priority_capable",
    "LogicalPartitionEnergyManagementCapable": "logical_partition_energy_management_capable",
    "LogicalPartitionProcessorCompatibilityModeCapable": "logical_partition_processor_compatibility_mode_capable",
    "LogicalPartitionRemoteRestartCapable": "logical_partition_remote_restart_capable",
    "LogicalPartitionSuspendCapable": "logical_partition_suspend_capable",
    "LogicalPortID": "logical_port_id",
    "LogicalPorts": "logical_ports",
    "LogicalSerialNumber": "logical_serial_number",
    "LogicalUnit": "logical_unit",
    "LogicalUnitAddress": "logical_unit_address",
    "LogicalUnitType": "logical_unit_type",
    "LogicalUnits": "logical_units",
    "LowPercentage": "low_percentage",
    "MACAddress": "mac_address",
    "MACAddressDirectives": "mac_address_directives",
    "MACAddressFlags": "mac_address_flags",
    "MACAddressPrefix": "mac_address_prefix",
    "MACAddressValue": "mac_address_value",
    "MaCAddressValue": "ma_c_address_value",
    "MachineType": "machine_type",
    "MachineTypeModelAndSerialNumber": "machine_type_model_and_serial_number",
    "Maintenance": "maintenance",
    "MajorBootType": "major_boot_type",
    "ManagedFrames": "managed_frames",
    "ManagedSystemInstalledMemory": "managed_system_installed_memory",
    "ManagedSystemInstalledProcUnits": "managed_system_installed_proc_units",
    "ManagedSystemMachineTypeModelSerialNumber": "managed_system_machine_type_model_serial_number",
    "ManagedSystemName": "managed_system_name",
    "ManagedSystems": "managed_systems",
    "ManagementConsoleMachineTypeModelSerialNumber": "management_console_machine_type_model_serial_number",
    "ManagementConsoleNIC": "management_console_nic",
    "ManagementConsoleName": "management_console_name",
    "ManagementConsoleNetworkInterface": "management_console_network_interface",
    "ManagementVLANForControlChannelCapable": "management_vlan_for_control_channel_capable",
    "ManagerPassthroughCapable": "manager_passthrough_capable",
    "ManualEntitledModeEnabled": "manual_entitled_mode_enabled",
    "ManufacturingDefaultConfigurationEnabled": "manufacturing_default_configuration_enabled",
    "MapPort": "map_port",
    "MaxLogicalVolumes": "max_logical_volumes",
    "MaxSupportedEthernetLogicalPorts": "max_supported_ethernet_logical_ports",
    "MaxSupportedFiberChannelOverEthernetLogicalPorts": "max_supported_fiber_channel_over_ethernet_logical_ports",
    "MaximumActiveMigrations": "maximum_active_migrations",
    "MaximumAllowedVirtualProcessorsPerPartition": "maximum_allowed_virtual_processors_per_partition",
    "MaximumDiagnosticsLogicalPorts": "maximum_diagnostics_logical_ports",
    "MaximumFiberChannelTargets": "maximum_fiber_channel_targets",
    "MaximumFirmwareActiveMigrations": "maximum_firmware_active_migrations",
    "MaximumHugeDMALogicalPorts": "maximum_huge_dma_logical_ports",
    "MaximumHugePageCount": "maximum_huge_page_count",
    "MaximumHugePages": "maximum_huge_pages",
    "MaximumIOPools": "maximum_io_pools",
    "MaximumInactiveMigrations": "maximum_inactive_migrations",
    "MaximumLogicalPortsSupported": "maximum_logical_ports_supported",
    "MaximumLogicalVolumes": "maximum_logical_volumes",
    "MaximumMemory": "maximum_memory",
    "MaximumMemoryPoolCount": "maximum_memory_pool_count",
    "MaximumMirroredMemoryDefragmented": "maximum_mirrored_memory_defragmented",
    "MaximumPagingVirtualIOServersPerSharedMemoryPool": "maximum_paging_virtual_io_servers_per_shared_memory_pool",
    "MaximumPartitions": "maximum_partitions",
    "MaximumPartitionsPerHostChannelAdapter": "maximum_partitions_per_host_channel_adapter",
    "MaximumPortVLANID": "maximum_port_vlanid",
    "MaximumPowerControlPartitions": "maximum_power_control_partitions",
    "MaximumProcessingUnits": "maximum_processing_units",
    "MaximumProcessorUnitsPerIBMiPartition": "maximum_processor_units_per_ibm_i_partition",
    "MaximumProcessors": "maximum_processors",
    "MaximumPromiscuousLogicalPorts": "maximum_promiscuous_logical_ports",
    "MaximumReceivePacketSize": "maximum_receive_packet_size",
    "MaximumRemoteRestartPartitions": "maximum_remote_restart_partitions",
    "MaximumSharedProcessorCapablePartitionID": "maximum_shared_processor_capable_partition_id",
    "MaximumSuspendablePartitions": "maximum_suspendable_partitions",
    "MaximumVLANID": "maximum_vlanid",
    "MaximumVLANsPerPort": "maximum_vla_ns_per_port",
    "MaximumVirtualIOSlots": "maximum_virtual_io_slots",
    "MaximumVirtualProcessors": "maximum_virtual_processors",
    "MediaName": "media_name",
    "MediaRepositories": "media_repositories",
    "MediaUDID": "media_udid",
    "MediumPercentage": "medium_percentage",
    "MemComplianceRemainingHours": "mem_compliance_remaining_hours",
    "MemoryDeduplicationEnabled": "memory_deduplication_enabled",
    "MemoryDeduplicationTableRatio": "memory_deduplication_table_ratio",
    "MemoryDefragmentationState": "memory_defragmentation_state",
    "MemoryEncryptionHardwareAccessEnabled": "memory_encryption_hardware_access_enabled",
    "MemoryExpansionEnabled": "memory_expansion_enabled",
    "MemoryExpansionHardwareAccessEnabled": "memory_expansion_hardware_access_enabled",
    "MemoryMirroringCapable": "memory_mirroring_capable",
    "MemoryMirroringState": "memory_mirroring_state",
    "MemoryRegionSize": "memory_region_size",
    "MemoryReleaseable": "memory_releaseable",
    "MemoryToRelease": "memory_to_release",
    "MemoryUsedByHypervisor": "memory_used_by_hypervisor",
    "MemoryWeight": "memory_weight",
    "Metadata": "metadata",
    "MicroLogicalPartitionCapable": "micro_logical_partition_capable",
    "MigrationState": "migration_state",
    "MinimumAllocationSize": "minimum_allocation_size",
    "MinimumEthernetCapacityGranularity": "minimum_ethernet_capacity_granularity",
    "MinimumFCoECapacityGranularity": "minimum_f_co_e_capacity_granularity",
    "MinimumHugePageCount": "minimum_huge_page_count",
    "MinimumMemory": "minimum_memory",
    "MinimumMemoryPoolSize": "minimum_memory_pool_size",
    "MinimumPortVLANID": "minimum_port_vlanid",
    "MinimumProcessingUnits": "minimum_processing_units",
    "MinimumProcessorUnitsPerVirtualProcessor": "minimum_processor_units_per_virtual_processor",
    "MinimumProcessors": "minimum_processors",
    "MinimumRequiredMemoryForAIXAndLinux": "minimum_required_memory_for_aix_and_linux",
    "MinimumRequiredMemoryForIBMi": "minimum_required_memory_for_ibm_i",
    "MinimumRequiredMemoryForVirtualIOServer": "minimum_required_memory_for_virtual_io_server",
    "MinimumVLANID": "minimum_vlanid",
    "MinimumVirtualProcessors": "minimum_virtual_processors",
    "Minor": "minor",
    "MinorBootType": "minor_boot_type",
    "MinorVersion": "minor_version",
    "MirrorableMemoryWithDefragmentation": "mirrorable_memory_with_defragmentation",
    "MirrorableMemoryWithoutDefragmentation": "mirrorable_memory_without_defragmentation",
    "MirroredMemoryUsedByHypervisor": "mirrored_memory_used_by_hypervisor",
    "MobileCoDMemory": "mobile_co_d_memory",
    "MobileCoDProcUnits": "mobile_co_d_proc_units",
    "Mode": "mode",
    "Model": "model",
    "MountType": "mount_type",
    "MoverServicePartition": "mover_service_partition",
    "MultiDataTierConfigured": "multi_data_tier_configured",
    "MultiFailureGroupConfigured": "multi_failure_group_configured",
    "NetworkAddress": "network_address",
    "NetworkBootDevice": "network_boot_device",
    "NetworkBootDevices": "network_boot_devices",
    "NetworkBridges": "network_bridges",
    "NetworkInstallManagerAddress": "network_install_manager_address",
    "NetworkInterfaces": "network_interfaces",
    "NetworkName": "network_name",
    "NetworkVLANID": "network_vlan_id",
    "NoLossFailoverEnabled": "no_loss_failover_enabled",
    "Node": "node",
    "NportLoggedInStatus": "nport_logged_in_status",
    "NumberOfActiveMigrationsInProgress": "number_of_active_migrations_in_progress",
    "NumberOfAllOSProcessorUnits": "number_of_all_os_processor_units",
    "NumberOfAllowedVLANs": "number_of_allowed_vla_ns",
    "NumberOfInactiveMigrationsInProgress": "number_of_inactive_migrations_in_progress",
    "NumberOfLinuxOnlyProcessorUnits": "number_of_linux_only_processor_units",
    "NumberOfVirtualIOServerProcessorUnits": "number_of_virtual_io_server_processor_units",
    "OperatingSystemVersion": "operating_system_version",
    "OperationsConsole": "operations_console",
    "OperationsConsoleAttached": "operations_console_attached",
    "OperationsConsoleCapable": "operations_console_capable",
    "OpticalMedia": "optical_media",
    "OverCommitSpace": "over_commit_space",
    "Owner": "owner",
    "OwnerLocation": "owner_location",
    "OwnerMachineTypeModelAndSerialNumber": "owner_machine_type_model_and_serial_number",
    "PCAdapterID": "pc_adapter_id",
    "PCIClass": "pci_class",
    "PCIDeviceID": "pci_device_id",
    "PCIManufacturerID": "pci_manufacturer_id",
    "PCIRevisionID": "pci_revision_id",
    "PCISubsystemDeviceID": "pci_subsystem_device_id",
    "PCISubsystemVendorID": "pci_subsystem_vendor_id",
    "PCIVendorID": "pci_vendor_id",
    "PageSize": "page_size",
    "PagingDevices": "paging_devices",
    "PagingServicePartition": "paging_service_partition",
    "PagingServicePartitionOne": "paging_service_partition_one",
    "PagingServicePartitionTwo": "paging_service_partition_two",
    "ParentName": "parent_name",
    "ParentSlotDynamicReconfigurationConnectorIndex": "parent_slot_dynamic_reconfiguration_connector_index",
    "PartitionCapabilities": "partition_capabilities",
    "PartitionID": "partition_id",
    "PartitionIOConfiguration": "partition_io_configuration",
    "PartitionLink": "partition_link",
    "PartitionMaximumMemoryLowerLimit": "partition_maximum_memory_lower_limit",
    "PartitionMemoryConfiguration": "partition_memory_configuration",
    "PartitionMobility": "partition_mobility",
    "PartitionName": "partition_name",
    "PartitionProcessorConfiguration": "partition_processor_configuration",
    "PartitionProfiles": "partition_profiles",
    "PartitionSize": "partition_size",
    "PartitionState": "partition_state",
    "PartitionType": "partition_type",
    "PartitionUUID": "partition_uuid",
    "PathName": "path_name",
    "PendingAddressBroadcastPolicy": "pending_address_broadcast_policy",
    "PendingAvailableHugePages": "pending_available_huge_pages",
    "PendingAvailablePoolMemory": "pending_available_pool_memory",
    "PendingAvailableSystemMemory": "pending_available_system_memory",
    "PendingAvailableSystemProcessorUnits": "pending_available_system_processor_units",
    "PendingConnectionSpeed": "pending_connection_speed",
    "PendingDuplexMode": "pending_duplex_mode",
    "PendingFlowControlEnabled": "pending_flow_control_enabled",
    "PendingLogicalMemoryBlockSize": "pending_logical_memory_block_size",
    "PendingManufacturingDefaulConfigurationtBootMode": "pending_manufacturing_defaul_configurationt_boot_mode",
    "PendingMaximumPartitionsPerHostChannelAdapter": "pending_maximum_partitions_per_host_channel_adapter",
    "PendingMaximumPoolMemory": "pending_maximum_pool_memory",
    "PendingMemoryMirroringMode": "pending_memory_mirroring_mode",
    "PendingMemoryRegionSize": "pending_memory_region_size",
    "PendingMultiCoreScaling": "pending_multi_core_scaling",
    "PendingPoolMemory": "pending_pool_memory",
    "PendingPowerOnSide": "pending_power_on_side",
    "PendingProcessorCompatibilityMode": "pending_processor_compatibility_mode",
    "PendingReservedProcessingUnits": "pending_reserved_processing_units",
    "PendingSystemKeylock": "pending_system_keylock",
    "PendingTurbocoreEnabled": "pending_turbocore_enabled",
    "PersistentReserveKeyValue": "persistent_reserve_key_value",
    "PhysicalFibreChannelPort": "physical_fibre_channel_port",
    "PhysicalFibreChannelPorts": "physical_fibre_channel_ports",
    "PhysicalLocation": "physical_location",
    "PhysicalLocationCode": "physical_location_code",
    "PhysicalPort": "physical_port",
    "PhysicalPortID": "physical_port_id",
    "PhysicalPortLocationCode": "physical_port_location_code",
    "PhysicalPortState": "physical_port_state",
    "PhysicalPortType": "physical_port_type",
    "PhysicalPorts": "physical_ports",
    "PhysicalSystemAttentionLEDState": "physical_system_attention_led_state",
    "PhysicalVolume": "physical_volume",
    "PhysicalVolumes": "physical_volumes",
    "PoolID": "pool_id",
    "PoolIDs": "pool_i_ds",
    "PoolName": "pool_name",
    "PoolSize": "pool_size",
    "Port": "port",
    "PortCapabilities": "port_capabilities",
    "PortGroupID": "port_group_id",
    "PortGroups": "port_groups",
    "PortLogicalPortLimit": "port_logical_port_limit",
    "PortName": "port_name",
    "PortState": "port_state",
    "PortType": "port_type",
    "PortVLANID": "port_vlan_id",
    "PowerControlPartitions": "power_control_partitions",
    "PowerEnterprisePoolManagementConsole": "power_enterprise_pool_management_console",
    "PowerEnterprisePoolManagementConsoles": "power_enterprise_pool_management_consoles",
    "PowerEnterprisePoolMasterManagementConsole": "power_enterprise_pool_master_management_console",
    "PowerEnterprisePoolMembers": "power_enterprise_pool_members",
    "PowerEnterprisePools": "power_enterprise_pools",
    "PowerManagementMode": "power_management_mode",
    "PowerOffWhenLastLogicalPartitionIsShutdown": "power_off_when_last_logical_partition_is_shutdown",
    "PowerOnLogicalPartitionStartPolicy": "power_on_logical_partition_start_policy",
    "PowerOnOption": "power_on_option",
    "PowerOnSpeed": "power_on_speed",
    "PowerOnSpeedOverride": "power_on_speed_override",
    "PrimaryIPAddress": "primary_ip_address",
    "PrimaryPagingServicePartition": "primary_paging_service_partition",
    "ProcComplianceRemainingHours": "proc_compliance_remaining_hours",
    "ProcessorAttributes": "processor_attributes",
    "ProcessorPool": "processor_pool",
    "ProfileIOSlot": "profile_io_slot",
    "ProfileIOSlots": "profile_io_slots",
    "ProfileMemory": "profile_memory",
    "ProfileName": "profile_name",
    "ProfileSRIOVEthernetLogicalPort": "profile_sriov_ethernet_logical_port",
    "ProfileSRIOVEthernetLogicalPorts": "profile_sriov_ethernet_logical_ports",
    "ProfileType": "profile_type",
    "ProfileVirtualIOAdapterChoice": "profile_virtual_io_adapter_choice",
    "ProfileVirtualIOAdapters": "profile_virtual_io_adapters",
    "ProgressPartitionDataRemaining": "progress_partition_data_remaining",
    "ProgressPartitionDataTotal": "progress_partition_data_total",
    "ProgressState": "progress_state",
    "QualityOfServiceMode": "quality_of_service_mode",
    "QualityOfServicePriority": "quality_of_service_priority",
    "QualityOfServicePriorityEnabled": "quality_of_service_priority_enabled",
    "QueueSize": "queue_size",
    "RAIDLevel": "raid_level",
    "ReceiveFlowControlEnabled": "receive_flow_control_enabled",
    "RedundancyCapable": "redundancy_capable",
    "RedundantDeviceName": "redundant_device_name",
    "RedundantDeviceState": "redundant_device_state",
    "RedundantErrorPathReportingCapable": "redundant_error_path_reporting_capable",
    "RedundantErrorPathReportingEnabled": "redundant_error_path_reporting_enabled",
    "RedundantLocationCode": "redundant_location_code",
    "ReferenceCode": "reference_code",
    "RelatedIBMiIOSlot": "related_ibm_i_io_slot",
    "RelatedIOAdapter": "related_io_adapter",
    "Release": "release",
    "RemoteBackingDeviceName": "remote_backing_device_name",
    "RemoteLogicalPartitionID": "remote_logical_partition_id",
    "RemotePartitionID": "remote_partition_id",
    "RemoteRestart": "remote_restart",
    "RemoteRestartCapable": "remote_restart_capable",
    "RemoteRestartState": "remote_restart_state",
    "RemoteRestartToggleCapable": "remote_restart_toggle_capable",
    "RemoteSlotNumber": "remote_slot_number",
    "RepositoryDisk": "repository_disk",
    "RepositoryName": "repository_name",
    "RepositorySize": "repository_size",
    "RequestedHugePages": "requested_huge_pages",
    "RequiredAdapter": "required_adapter",
    "RequiredMinimumForMaximum": "required_minimum_for_maximum",
    "ReservePolicy": "reserve_policy",
    "ReservePolicyAlgorithm": "reserve_policy_algorithm",
    "ReservedStorageDevice": "reserved_storage_device",
    "ResourceMonitoringControlOperatingSystemShutdownCapable": "resource_monitoring_control_operating_system_shutdown_capable",
    "ResourceMonitoringControlState": "resource_monitoring_control_state",
    "ResourceMonitoringIPAddress": "resource_monitoring_ip_address",
    "RetryCount": "retry_count",
    "RetryTime": "retry_time",
    "RunProcessors": "run_processors",
    "RuntimeEntitledMemory": "runtime_entitled_memory",
    "RuntimeExpansionFactor": "runtime_expansion_factor",
    "RuntimeHasDedicatedProcessors": "runtime_has_dedicated_processors",
    "RuntimeHugePageCount": "runtime_huge_page_count",
    "RuntimeMemory": "runtime_memory",
    "RuntimeMemoryWeight": "runtime_memory_weight",
    "RuntimeMinimumMemory": "runtime_minimum_memory",
    "RuntimeProcessingUnits": "runtime_processing_units",
    "RuntimeSharingMode": "runtime_sharing_mode",
    "RuntimeUncappedWeight": "runtime_uncapped_weight",
    "SRIOVAdapterID": "sriov_adapter_id",
    "SRIOVAdapters": "sriov_adapters",
    "SRIOVCapable": "sriov_capable",
    "SRIOVConvergedNetworkAdapterPhysicalPort": "sriov_converged_network_adapter_physical_port",
    "SRIOVEthernetLogicalPorts": "sriov_ethernet_logical_ports",
    "SRIOVEthernetPhysicalPort": "sriov_ethernet_physical_port",
    "SRIOVFibreChannelOverEthernetLogicalPorts": "sriov_fibre_channel_over_ethernet_logical_ports",
    "SRIOVUnconfiguredLogicalPort": "sriov_unconfigured_logical_port",
    "SchemaNamespace": "schema_namespace",
    "SecondaryIPAddress": "secondary_ip_address",
    "SecondaryPagingServicePartition": "secondary_paging_service_partition",
    "SequenceNumber": "sequence_number",
    "SerialNumber": "serial_number",
    "ServerAdapter": "server_adapter",
    "ServerInstallConfiguration": "server_install_configuration",
    "ServerLocationCode": "server_location_code",
    "ServicePackName": "service_pack_name",
    "ServicePartition": "service_partition",
    "ServiceProcessorConcurrentMaintenanceCapable": "service_processor_concurrent_maintenance_capable",
    "ServiceProcessorFailoverCapable": "service_processor_failover_capable",
    "ServiceProcessorFailoverEnabled": "service_processor_failover_enabled",
    "ServiceProcessorFailoverReason": "service_processor_failover_reason",
    "ServiceProcessorFailoverState": "service_processor_failover_state",
    "ServiceProcessorVersion": "service_processor_version",
    "SettingID": "setting_id",
    "SharedEthernetAdapter": "shared_ethernet_adapter",
    "SharedEthernetAdapters": "shared_ethernet_adapters",
    "SharedEthernetFailoverCapable": "shared_ethernet_failover_capable",
    "SharedMemoryEnabled": "shared_memory_enabled",
    "SharedMemoryPool": "shared_memory_pool",
    "SharedProcessorConfiguration": "shared_processor_configuration",
    "SharedProcessorPool": "shared_processor_pool",
    "SharedProcessorPoolCapable": "shared_processor_pool_capable",
    "SharedProcessorPoolCount": "shared_processor_pool_count",
    "SharedProcessorPoolID": "shared_processor_pool_id",
    "SharedStoragePoolCapable": "shared_storage_pool_capable",
    "SharedStoragePoolID": "shared_storage_pool_id",
    "SharedStoragePoolVersion": "shared_storage_pool_version",
    "SharedStoragePools": "shared_storage_pools",
    "SharingMode": "sharing_mode",
    "Size": "size",
    "SlaveBulkPowerControllerExists": "slave_bulk_power_controller_exists",
    "SlotDynamicReconfigurationConnectorIndex": "slot_dynamic_reconfiguration_connector_index",
    "SlotDynamicReconfigurationConnectorName": "slot_dynamic_reconfiguration_connector_name",
    "SlotPhysicalLocationCode": "slot_physical_location_code",
    "State": "state",
    "StatusReason": "status_reason",
    "Storage": "storage",
    "StorageDeviceUniqueDeviceID": "storage_device_unique_device_id",
    "StoragePoolName": "storage_pool_name",
    "StoragePools": "storage_pools",
    "SubLabel": "sub_label",
    "SubnetMask": "subnet_mask",
    "SupportedConnectionSpeeds": "supported_connection_speeds",
    "SupportedMTUs": "supported_mt_us",
    "SupportedMultiCoreScalingValues": "supported_multi_core_scaling_values",
    "SupportedOptions": "supported_options",
    "SupportedPartitionProcessorCompatibilityModes": "supported_partition_processor_compatibility_modes",
    "SupportedPriorityAccessControlList": "supported_priority_access_control_list",
    "SuspendCapable": "suspend_capable",
    "SuspendResume": "suspend_resume",
    "SwitchID": "switch_id",
    "SwitchMode": "switch_mode",
    "SwitchName": "switch_name",
    "SwitchNetworkInterfaceDeviceID": "switch_network_interface_device_id",
    "SwitchNetworkInterfaceMessagePassingCapable": "switch_network_interface_message_passing_capable",
    "SystemFirmwarePoolMemory": "system_firmware_pool_memory",
    "SystemMigrationInformation": "system_migration_information",
    "SystemName": "system_name",
    "SystemPlacement": "system_placement",
    "SystemTime": "system_time",
    "SystemVirtualStorage": "system_virtual_storage",
    "TaggedIO": "tagged_io",
    "TaggedNetwork": "tagged_network",
    "TaggedVLANIDs": "tagged_vlan_ids",
    "TaggedVLANSupported": "tagged_vlan_supported",
    "TargetDevice": "target_device",
    "TargetName": "target_name",
    "Telnet5250ApplicationCapable": "telnet5250_application_capable",
    "TemplateObjectModelVersion": "template_object_model_version",
    "TemporaryMemoryForLogicalPartitionMobilityInUse": "temporary_memory_for_logical_partition_mobility_in_use",
    "TemporaryProcessorUnitsForLogicalPartitionMobilityInUse": "temporary_processor_units_for_logical_partition_mobility_in_use",
    "ThinDevice": "thin_device",
    "ThreadModeEnabled": "thread_mode_enabled",
    "TotalBarrierSynchronizationRegisterArrays": "total_barrier_synchronization_register_arrays",
    "TotalLogicalUnitSize": "total_logical_unit_size",
    "TotalMobileCoDMemory": "total_mobile_co_d_memory",
    "TotalMobileCoDProcUnits": "total_mobile_co_d_proc_units",
    "TotalPhysicalPartitions": "total_physical_partitions",
    "TotalPorts": "total_ports",
    "TransmitFlowControlEnabled": "transmit_flow_control_enabled",
    "TrunkAdapter": "trunk_adapter",
    "TrunkAdapters": "trunk_adapters",
    "TrunkPriority": "trunk_priority",
    "TuningBufferID": "tuning_buffer_id",
    "TurboCoreCapable": "turbo_core_capable",
    "TurboCoreSupport": "turbo_core_support",
    "TwinaxialAttached": "twinaxial_attached",
    "TwinaxialCapable": "twinaxial_capable",
    "UUIDListSequential": "uuid_list_sequential",
    "UnassignedGUIDs": "unassigned_gui_ds",
    "UncappedWeight": "uncapped_weight",
    "UnconfiguredLogicalPorts": "unconfigured_logical_ports",
    "UniqueDeviceID": "unique_device_id",
    "UnitCapacity": "unit_capacity",
    "UnitName": "unit_name",
    "UnreturnedMobileCoDMemory": "unreturned_mobile_co_d_memory",
    "UnreturnedMobileCoDProcUnits": "unreturned_mobile_co_d_proc_units",
    "UseAlternateAddress": "use_alternate_address",
    "UseNextAvailableSlotID": "use_next_available_slot_id",
    "UserObjectModelVersion": "user_object_model_version",
    "UsesHighSpeedLinkOpticonnect": "uses_high_speed_link_opticonnect",
    "UsesSharedStoragePool": "uses_shared_storage_pool",
    "UsesVirtualOpticonnect": "uses_virtual_opticonnect",
    "VLANStatisticsCapable": "vlan_statistics_capable",
    "ValidInteractivePerformance": "valid_interactive_performance",
    "VariedOn": "varied_on",
    "Version": "version",
    "VersionDate": "version_date",
    "VersionInfo": "version_info",
    "VirtualDisk": "virtual_disk",
    "VirtualDisks": "virtual_disks",
    "VirtualEthernetAdapterDynamicLogicalPartitionCapable": "virtual_ethernet_adapter_dynamic_logical_partition_capable",
    "VirtualEthernetAdapterMACAddressPrefix": "virtual_ethernet_adapter_mac_address_prefix",
    "VirtualEthernetCustomMACAddressCapable": "virtual_ethernet_custom_mac_address_capable",
    "VirtualEthernetQualityOfServiceCapable": "virtual_ethernet_quality_of_service_capable",
    "VirtualFiberChannelCapable": "virtual_fiber_channel_capable",
    "VirtualFibreChannelClientAdapters": "virtual_fibre_channel_client_adapters",
    "VirtualFibreChannelMapping": "virtual_fibre_channel_mapping",
    "VirtualFibreChannelMappings": "virtual_fibre_channel_mappings",
    "VirtualFibreChannelNPortLoginStatus": "virtual_fibre_channel_n_port_login_status",
    "VirtualIOServer": "virtual_io_server",
    "VirtualIOServerCapable": "virtual_io_server_capable",
    "VirtualIOServerLevel": "virtual_io_server_level",
    "VirtualIOServerLicense": "virtual_io_server_license",
    "VirtualIOServerLicenseAccepted": "virtual_io_server_license_accepted",
    "VirtualMediaRepositories": "virtual_media_repositories",
    "VirtualMediaRepository": "virtual_media_repository",
    "VirtualNetworks": "virtual_networks",
    "VirtualOpticalDevices": "virtual_optical_devices",
    "VirtualOpticalMedia": "virtual_optical_media",
    "VirtualOpticalTargetDevice": "virtual_optical_target_device",
    "VirtualOpticonnectPool": "virtual_opticonnect_pool",
    "VirtualSCSIClientAdapters": "virtual_scsi_client_adapters",
    "VirtualSCSIMapping": "virtual_scsi_mapping",
    "VirtualSCSIMappings": "virtual_scsi_mappings",
    "VirtualServerNetworkingPhase2Capable": "virtual_server_networking_phase2_capable",
    "VirtualServerProtectionCapable": "virtual_server_protection_capable",
    "VirtualSlotNumber": "virtual_slot_number",
    "VirtualStationInterfaceManagerID": "virtual_station_interface_manager_id",
    "VirtualStationInterfaceTypeID": "virtual_station_interface_type_id",
    "VirtualStationInterfaceTypeVersion": "virtual_station_interface_type_version",
    "VirtualSwitchCapable": "virtual_switch_capable",
    "VirtualSwitchID": "virtual_switch_id",
    "VirtualSwitchInterfaceManagerID": "virtual_switch_interface_manager_id",
    "VirtualSwitchInterfaceType": "virtual_switch_interface_type",
    "VirtualSwitchInterfaceTypeVersion": "virtual_switch_interface_type_version",
    "VirtualSwitchName": "virtual_switch_name",
    "VirtualSwitches": "virtual_switches",
    "VirtualSystemAttentionLEDState": "virtual_system_attention_led_state",
    "VirtualTrustedPlatformModuleCapable": "virtual_trusted_platform_module_capable",
    "VirtualTrustedPlatformModuleKeyLength": "virtual_trusted_platform_module_key_length",
    "VirtualTrustedPlatformModuleKeyStatus": "virtual_trusted_platform_module_key_status",
    "VirtualTrustedPlatformModuleKeyStatusFlags": "virtual_trusted_platform_module_key_status_flags",
    "VirtualTrustedPlatformModuleVersion": "virtual_trusted_platform_module_version",
    "VirtualizationEngineTechnologiesActivationCapable": "virtualization_engine_technologies_activation_capable",
    "VitalProductDataModel": "vital_product_data_model",
    "VitalProductDataSerialNumber": "vital_product_data_serial_number",
    "VitalProductDataStale": "vital_product_data_stale",
    "VitalProductDataType": "vital_product_data_type",
    "VolumeCapacity": "volume_capacity",
    "VolumeGroup": "volume_group",
    "VolumeName": "volume_name",
    "VolumeState": "volume_state",
    "VolumeUniqueID": "volume_unique_id",
    "VswitchID": "vswitch_id",
    "WWPN": "wwpn",
    "WWPN1": "wwpn1",
    "WWPN2": "wwpn2",
    "WWPNPrefix": "wwpn_prefix",
    "WWPNStatus": "wwpn_status",
    "WWPNs": "wwp_ns",
    "WebObjectModelVersion": "web_object_model_version",
    "link": "link"
}"""
attr_cc_to_us = json.loads(_attr_cc_to_us_json)
