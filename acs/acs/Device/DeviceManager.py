"""
Copyright (C) 2018 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.


SPDX-License-Identifier: Apache-2.0
"""

import logging

from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.DeviceException import DeviceException
from acs.Core.Report.ACSLogging import LOGGER_FWK, LOGGER_DEVICE_STATS
from acs.UtilitiesFWK.Utilities import get_class
from DeviceConfig.DeviceConfigLoader import DeviceConfigLoader
from acs.Core.Report.ACSLogging import ACS_LOGGER_NAME


class DeviceManager(object):

    """
    DeviceManager class: this class is a singleton
    and manages all instantiated devices
    """

    """
    The singleton instance
    """
    __instance = None

    """
    Dictionary of all devices instances. The key is the name
    of the device
    """
    _device_instances = {}

    """
    Dictionary of all devices properties. The key is the name
    of the device. Each device will have its own dictionary of properties
    """
    _device_properties = {}

    """
    The global configuration
    """
    __global_cfg = None

    """
    Logger
    """
    __logger = LOGGER_FWK

    def __new__(cls):
        """
        Constructor that always returns the same instance of EquipmentManager
        """

        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def set_global_config(cls, global_config):
        """
        Sets the global configuration to use
        :type global_config: global configuration
        :param global_config: the global configuration to use
        """
        cls.__global_cfg = global_config

    @classmethod
    def get_global_config(cls):
        """
        Gets global configuration
        :rtype: global configuration
        :return: the global configuration if it has been set before
        :raise AcsConfigException if global configuration has not been set yet
        """
        if cls.__global_cfg is None:
            msg = "Global configuration should be set before using DeviceManager"
            raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR, msg)

        else:
            return cls.__global_cfg

    @classmethod
    def get_logger(cls):
        """
        Gets the equipment manager logger
        :rtype: logger
        :return: the logger of the DeviceManager instance
        """
        return cls.__logger

    # Device specific functions
    def load(self, device_name, device_parameters):
        """
        Load and instantiate device configured on the cmd line and those define in bench config.

        :type device_name: str
        :param device_name: Device model to instantiate (if specify from the command line, else None)

        :type device_parameters: list
        :param device_parameters: Device parameters to overload (if specify from the command line)
        """
        # Load device(s) configuration
        device_cfg_loader = DeviceConfigLoader(self.get_global_config())
        device_configs = device_cfg_loader.load(device_name, device_parameters)

        for device_name in sorted(device_configs.keys()):
            device = self._instantiate_device(device_name, device_configs[device_name])
            self.get_logger().debug("Creating Device with parameters: {0}".format(device_configs[device_name]))
            LOGGER_DEVICE_STATS.info("Create device_model={0}".format(device.get_phone_model()))
            self._device_instances[device_name] = device

        if not self._device_instances:
            msg = "No Devices configured, please specify one on the command line or in the bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        return self._device_instances

    def _instantiate_device(self, device_name, device_config):
        """
        Instantiate a device according to the classname found in config

        :type   device_name: str
        :param  device_name: Device name to instantiate (e.g.: PHONE1)

        :type   device_config: AttributeDict
        :param  device_config: Configuration of the device to instantiate

        :rtype:     device
        :return:    Instance of the device
        """
        # Instantiate the device
        if device_config.get("ClassName"):
            device_model_class = get_class(device_config.ClassName)

            if device_model_class is not None:
                device_logger = logging.getLogger("%s.DEVICE.%s" % (ACS_LOGGER_NAME, device_name,))
                device_config.device_name = device_name
                device = device_model_class(device_config, device_logger)
            else:
                error_msg = "Class name %s not found!" % (str(device_config.ClassName),)
                self.get_logger().error(error_msg)
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)
        else:
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                     "Cannot instantiate \"{0}\", class name is missing in the configuration:\n {1}"
                                     .format(device_name, device_config))

        # Raise an error if the instance is none
        if device is None:
            msg = "Unable to instantiate device %s" % (str(device_config.Name),)
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INSTANTIATION_ERROR, msg)

        # Setup environment of the board
        device.initialize()
        return device

    def get_device(self, device_name):
        """
        Gets the instance of a device if it exists.

        :type   device_name: string
        :param  device_name: name of the device (e.g. PHONE1)
        """
        return self._device_instances.get(device_name)

    def get_all_devices(self):
        """
          Gets the list of devices instance sorted by device name.
        """
        return [self.get_device(device_name) for device_name in sorted(self._device_instances.keys())]

    def get_device_config(self, device_name):
        """
        Gets the instance of an equipment if it exists.
        :rtype: object
        :return: the instance of the equipment if it exists,
        else returns None
        """

        if device_name in self._device_instances:
            device_config = self._device_instances[device_name].config

        # No device are defines in the BenchConfig
        else:
            msg = "Device config for %s not found!" % str(device_name)
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.DATA_STORAGE_ERROR, msg)

        return device_config

    def boot_device(self, device_name):
        """
        Perform boot sequence of the current device

        :return: the instance of the equipment if it exists,
        else returns None
        """
        dut_instance = self.get_device(device_name)

        if dut_instance:
            # Try a number of time to switch ON & boot CDK
            dut_instance.switch_on()
            if dut_instance.is_booted():
                # The device has booted on time
                # Reconnect the DUT
                if not dut_instance.is_available():
                    dut_instance.connect_board()
            else:
                # The board has failed to boot several
                # attempts
                msg = "Device has failed to boot, abort!"
                self.get_logger().error(msg)
                raise DeviceException(DeviceException.DUT_BOOT_ERROR, msg)
        else:
            self.get_logger().error("Cannot boot device '{0}', it is not available.".format(device_name))

    def get_device_properties(self, device_name):
        """
        Gets the properties of a device if it exists.

        :type   device_name: string
        :param  device_name: name of the device (e.g. PHONE1)

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        return self._device_properties.get(device_name, {})

    def update_device_properties(self, device_name, properties=None):
        """
        Update the properties dictionary of a device if it exists.
        Warning the device must be booted and connected to update values !
        (For Android phone it will corresponds to adb shell getprop)

        :type   device_name: string
        :param  device_name: name of the device (e.g. PHONE1)

        :param properties: set of properties and their associated values
        :type properties: dict

        :rtype: dict
        :return: Dict of properties and their associated values
        """

        # Try to retrieve/update device properties
        try:
            if device_name in [None, ""]:
                msg = "Device name is empty or None, cannot update device properties !"
                self.get_logger().warning(msg)
                return {}

            # Initialize device properties if not exists
            if self._device_properties.get(device_name) is None:
                self._device_properties[device_name] = {}

            # In case properties parameter is not None the dictionary will be updated with given values
            if properties and isinstance(properties, dict):
                for property_name in properties.keys():
                    property_value = properties.get(property_name)
                    if property_value not in ["", None]:
                        self._device_properties[device_name].update({property_name: property_value})

            else:
                # In other case ACS will try to get all the properties from the device
                dut_instance = self.get_device(device_name)

                if dut_instance is not None:
                    if dut_instance.is_available():
                        # Update device info for campaign results
                        device_properties = dut_instance.retrieve_device_info()

                        # use device properties to update the DeviceManager dictionary,
                        # related to device properties
                        for device_property_name in device_properties.keys():
                            device_property_value = device_properties.get(device_property_name)
                            if device_property_value not in ["", None]:
                                self._device_properties[device_name].update(
                                    {device_property_name: device_property_value})

                    else:
                        msg = "Device %s not booted/connected, cannot update device properties !" % str(device_name)
                        self.get_logger().warning(msg)

                # Device instance not found
                else:
                    msg = "Device instance for %s not found, cannot update device properties !" % str(device_name)
                    self.get_logger().warning(msg)
        except Exception as ex:
            self.get_logger().warning("Error occured when updating device properties ! (%s)" % str(ex))

        # Retrieved updated properties
        return self._device_properties.get(device_name)

    def release_all_devices(self):
        """
        Disconnects and releases all device instances
        """
        self.get_logger().debug("Disconnect all devices")
        for device in self.get_all_devices():
            device.disconnect_board()
            device.stop_connection_server()

        self.get_logger().debug("Delete all devices")
        for name in self._device_instances.keys():
            device_inst = self._device_instances.pop(name)
            del device_inst
            self.get_logger().debug("%s deleted", name)

    def get_devices_number(self):
        """
        Retreive devices number

        :return: number of devices
        """
        return len(self._device_instances)
