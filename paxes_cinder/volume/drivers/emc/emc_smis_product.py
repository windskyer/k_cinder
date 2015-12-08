# vim: tabstop=4 shiftwidth=4 softtabstop=4

# All Rights Reserved.
#
# Copyright (c) 2012 EMC Corporation.
# Copyright (c) 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from cinder.volume.drivers.emc import emc_smis_iscsi
from cinder.volume.drivers.emc.emc_smis_iscsi import *
from cinder import context
from cinder.volume import volume_types
from paxes_cinder.volume import discovery_driver
from paxes_cinder.volume.drivers.emc import emc_common_product
from paxes_cinder import _


#element_type 5 = Thin Provisioning
#element_type 2 = Thick Provisioning
supported_element_types = {'thick': 2,
                           'thin': 5}


class EMCSMISProductDriver(
        discovery_driver.VolumeDiscoveryDriver,
        emc_smis_iscsi.EMCSMISISCSIDriver):
    """EMC ISCSI Product Driver for VMAX and VNX using SMI-S."""

    def __init__(self, *args, **kwargs):
        super(EMCSMISProductDriver, self).__init__(*args, **kwargs)
        self.common =\
            emc_common_product.EMCCommonProductDriver('iSCSI',
                                                      configuration=
                                                      self.configuration)

    def _build_default_opts(self):
        #Define any default options that should be used.
        #element_type 5 = Thin Provisioning
        #element_type 2 = Thick Provisioning
        default_opts = {'element_type': supported_element_types['thin'],
                        'storage_pool': self.common._get_storage_type()}
        return default_opts

    def _get_volume_params(self, type_id):
        #Get the default values
        opts = self._build_default_opts()

        if type_id:
            ctxt = context.get_admin_context()
            volume_type = volume_types.get_volume_type(ctxt, type_id)

            #Get the extra-specs
            specs = volume_type.get('extra_specs')
            for k, value in specs.iteritems():
                # Get the scope, if using scope format
                key_split = k.split(':')
                if len(key_split) == 1:
                    scope = None
                    key = key_split[0]
                else:
                    scope = key_split[0]
                    key = key_split[1]

                # We generally do not look at capabilities in the driver, but
                # protocol is a special case where the user asks for a given
                # protocol and we want both the scheduler and the driver to act
                # on the value.
                if scope == 'capabilities' and key == 'storage_protocol':
                    scope = None
                    key = 'protocol'
                    words = value.split()
                    self._driver_assert(words and
                                        len(words) == 2 and
                                        words[0] == '<in>',
                                        _('protocol must be specified as '
                                          '\'<in> iSCSI\' or \'<in> FC\''))
                    del words[0]
                    value = words[0]

                # Any keys that the driver should look at should have the
                # 'drivers' scope.
                if scope and scope != "drivers":
                    continue

                #Check for the element_type extra-spec.
                if key == 'element_type':
                    #Check if the user specified by name.
                    if value in supported_element_types.keys():
                        #Convert the name to the matching value.
                        #Otherwise the expected data-type won't match.
                        value = supported_element_types[value]

                if key in opts:
                    this_type = type(opts[key]).__name__
                    if this_type == 'int':
                        value = int(value)
                    elif this_type == 'bool':
                        value = strutils.bool_from_string(value)
                    opts[key] = value
        return opts

    def create_volume(self, volume):
        opts = self._get_volume_params(volume['volume_type_id'])
        return self._create_volume(volume, opts)

    def _create_volume(self, volume, opts):
        """Creates a EMC(VMAX/VNX) volume."""

        LOG.debug(_('Entering create_volume.'))
        volumesize = int(volume['size']) * 1073741824
        volumename = volume['name']

        LOG.info(_('Create Volume: %(volume)s  Size: %(size)lu')
                 % {'volume': volumename,
                    'size': volumesize})

        self.conn = self.common._get_ecom_connection()

        #Get the storage pool from the config file.
        storage_type = self.common._get_storage_type()

        #The element_type determines the type of provisioning.
        element_type = supported_element_types['thin']

        #Iterate through the extra-spec options
        for opt, val in opts.iteritems():
            #Override the storage pool, if specified.
            if opt == 'storage_pool':
                storage_type = val
            #Override the element_type, if specified.
            if opt == 'element_type':
                element_type = val

                #Check if the user supplied the element_type by it's name.
                if val in supported_element_types.keys():
                    #The user supplied the element_type by it's name.
                    #Get the associated value.
                    element_type = supported_element_types[val]
                #Check if the user supplied the element_type by it's value.
                elif val not in supported_element_types.values():
                    #The value was not in the supported_element_types list.
                    #Throw an exception.
                    errordesc = (_('Unsupported element_type value '
                                 '%(element_type)s.  Specify a supported '
                                 'element_type value and resubmit the '
                                 'request.')
                                 % {'element_type': element_type})
                    raise exception.VolumeBackendAPIException(data=errordesc)

        LOG.debug(_('Create Volume: %(volume)s  '
                  'Storage type: %(storage_type)s')
                  % {'volume': volumename,
                     'storage_type': storage_type})

        pool, storage_system = self.common._find_pool(storage_type)

        LOG.debug(_('Create Volume: %(volume)s  Pool: %(pool)s,  '
                  'Element Type: %(element_type)s, '
                  'Storage System: %(storage_system)s')
                  % {'volume': volumename,
                     'pool': str(pool),
                     'element_type': element_type,
                     'storage_system': storage_system})

        configservice = self.common._find_storage_configuration_service(
            storage_system)
        if configservice is None:
            exception_message = (_("Error Create Volume: %(volumename)s. "
                                 "Storage Configuration Service not found for "
                                 "pool %(storage_type)s.")
                                 % {'volumename': volumename,
                                    'storage_type': storage_type})
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)

        LOG.debug(_('Create Volume: %(name)s  Method: '
                  'CreateOrModifyElementFromStoragePool  ConfigServicie: '
                  '%(service)s  ElementName: %(name)s  InPool: %(pool)s  '
                  'ElementType: %(element_type)s  Size: %(size)lu')
                  % {'service': str(configservice),
                     'name': volumename,
                     'pool': str(pool),
                     'element_type': element_type,
                     'size': volumesize})

        rc, job = self.conn.InvokeMethod(
            'CreateOrModifyElementFromStoragePool',
            configservice, ElementName=volumename, InPool=pool,
            ElementType=self.common._getnum(element_type, '16'),
            Size=self.common._getnum(volumesize, '64'))

        LOG.debug(_('Create Volume: %(volumename)s  Return code: %(rc)lu')
                  % {'volumename': volumename,
                     'rc': rc})

        if rc != 0L:
            rc, errordesc = self.common._wait_for_job_complete(job)
            if rc != 0L:
                LOG.error(_('Error Create Volume: %(volumename)s.  '
                          'Return code: %(rc)lu.  Error: %(error)s')
                          % {'volumename': volumename,
                             'rc': rc,
                             'error': errordesc})
                raise exception.VolumeBackendAPIException(data=errordesc)

        LOG.debug(_('Leaving create_volume: %(volumename)s  '
                  'Return code: %(rc)lu')
                  % {'volumename': volumename,
                     'rc': rc})

    def get_default_vol_type(self):
        """Returns the default volume type from the emc's .conf file"""
        vtn = self.common.configuration.default_volume_type
        return vtn.decode('utf-8') if vtn else vtn

    def get_storage_metadata(self):
        volume_pools = []
        try:
            connection = self.common._get_ecom_connection()
        except:
            exception_message = (_("Could not establish ecom connection"))
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)
        upools = connection.EnumerateInstances(
            'EMC_UnifiedStoragePool')
        # Example: of upools
        #(u'EMCTotalRawCapacity', 864590287872L),
        #(u'StatusDescriptions', [u'OK', u'ONLINE']),
        #(u'EMCLUNsSubscribedCapacity', 0L),
        #(u'EMCMetaDataSubscribedCapacity', 0L),
        #(u'RemainingManagedSpace', 560512106496L),
        #(u'EMCRemainingRawCapacity', 845225143296L),
        #(u'PoolID', u'emc_pool1')
        #(u'variable, u'value')...
        volume_pools.append(upools)
        return {'volume_pools': volume_pools}

    def discover_volumes(self, context, filters=None):
        volume_l = []
        #1 GB = 1073741824 Bytes
        bytesPerGigaByte = 1073741824
        try:
            connection = self.common._get_ecom_connection()
        except:
            exception_message = (_("Could not establish ecom connection"))
            LOG.error(exception_message)
            raise exception.VolumeBackendAPIException(data=exception_message)
        volumes = connection.EnumerateInstances(
            'EMC_StorageVolume')
        for v in volumes:
            volume_d = {}
            numBlocks = v['NumberOfBlocks']
            blockSize = v['BlockSize']
            size = int((numBlocks*blockSize)/bytesPerGigaByte)
            statuses = v['StatusDescriptions']
            status = 'available' if 'ONLINE' in statuses else 'error'
            volume_d['name'] = v['ElementName']
            volume_d['size'] = size
            volume_d['restricted_metadata'] = {"vdisk_id": v['DeviceID'],
                                               "vdisk_name":
                                               v['ElementName']}
            volume_d['status'] = status
            volume_d['support'] = {"status": "supported"}
            volume_l.append(volume_d)
        return volume_l
