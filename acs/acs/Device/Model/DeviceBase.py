"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

:organization: INTEL MCG PSI
:summary: This file expose the device base
:since: 03/08/2011
:author: ssavrimoutou
"""
import os
import time
import yaml

from acs.Core.PathManager import Paths
from acs.Device.Common import Common
from acs.Device import DeviceManager
from acs.Device.Model.IDevice import IDevice
from acs.Device.Module.DeviceModuleFactory import DeviceModuleFactory
from acs.Device.DeviceProperties import DeviceProperties
from acs.Device.FlashDeviceProperties import FlashDeviceProperties
from acs.Device.DeviceCapability.DeviceCapabilityManager import DeviceCapabilityManager as DCManager
from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.Utilities import AcsConstants
from acs.UtilitiesFWK.Utilities import Verdict
from acs.ErrorHandling.DeviceException import DeviceException
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class DeviceBase(IDevice):

    """
    Class that implements common devices methods
    """
    # Log prefix key class attribute
    _LOG_PREFIX_KEY = 'device'
    # type of os installed on the device
    OS_TYPE = 'UNDEFINED'

    def __init__(self, config, logger):
        """
        Constructor

        :type  config: dict
        :param config: Device configuration to use

        :type  logger: logger
        :param logger: Logger to use
        """
        device_man = DeviceManager.DeviceManager()
        self._global_config = device_man.get_global_config()
        self._device_config = config
        self._uecmd_path = self._device_config.UECmd
        self._device_model_name = self._device_config.Name
        self._wait_btwn_cmd = self.get_config("waitBetweenCmd", 5, float)
        self._min_file_install_timeout = self.get_config("minFileInstallTimeout", 30, int)
        self._device_name = config.device_name
        self._acs_agent = None
        self._userdata_path = None
        self.uecommands = {}
        self._device_capabilities = []
        self._logger = logger
        self.__uecmd_instances = {}
        self.retrieve_tc_debug_log = None

        self._module_instances = AttributeDict()
        self._device_properties = DeviceProperties()
        self._flash_device_properties = FlashDeviceProperties()
        self._device_capabilities = DCManager.load_device_capabilities(self._device_config.deviceCapabilities,
                                                                       self._logger)
        campaign_report_tree = self._global_config.campaignConfig["campaignReportTree"]
        campaign_report_tree.set_hw_variant_name(self.hw_variant_name)
        campaign_report_tree.create_report_folder()

    @property
    def device_modules(self):
        """
        Return device modules
        :rtype list
        :return: List of device modules
        """
        return self._module_instances

    @property
    def device_capabilities(self):
        """
        Return device capabilities
        :rtype list
        :return: List of device capabilities
        """
        return self._device_capabilities

    @property
    def hw_variant_name(self):
        """
        Return hw variant name
        :rtype str
        :return: Hardware variant name
        """
        variant = "Unknown"
        if self._device_model_name:
            variant = self._device_model_name.split("-")[0]
        return variant

    @property
    def config(self):
        """
        Return device configuration
        :rtype: AttributeDict
        :return: device configuration
        """
        return self._device_config

    @property
    def logger(self):
        """
        Retrieve the logger associated to that device
        """
        return self._logger

    def retrieve_os_version(self):
        """
        Retrieve all available OS version for this OS
        :rtype: list
        :return: list of available os version
        """
        os_version_path = os.path.join(Paths.DEVICE_CATALOG, "os_version.yaml")
        with open(os_version_path, 'r') as f:
            all_version = yaml.load(f)
        return all_version.get(self.get_config("OS"), [])

    def whoami(self):
        """
        Use the bench configuration name and the model of the device to build
        a unique identification string for the device
        :rtype: dict
        :return: a unique identification string for the equipment
        """
        return {"device": self._device_name}

    def get_phone_model(self):
        """
        Return the phone model name
        """
        return self._device_model_name

    def get_ftpdir_path(self):
        """
        Return the path to the local FTP files
        :rtype: str
        :return: local FTP directory
        """
        self.get_logger().warning("device.get_ftp_dir_path() is deprecated. Please use device.multimedia_path instead")
        return self._userdata_path

    @property
    def multimedia_path(self):
        """
        Return the path to the local multimedia files
        :rtype: str
        :return: local multimedia directory
        """
        return self._userdata_path

    @property
    def binaries_path(self):
        """
        Return the path to the local binaries folder
        :rtype: str
        :return: local binaries directory
        """
        return self._binaries_path

    def get_logger(self):
        """
        Return the logger instance of the device

        :rtype: logger
        :return: device logger
        """
        return self._logger

    def init_device_connection(self, skip_boot_required, first_power_cycle, power_cycle_retry_number):
        """
        Init the device connection.

        Call for first device connection attempt or to restart device before test case execution
        """
        return True, "", 1, 0, 0

    def init_acs_agent(self):
        """
        Init ACS agent for the device
        """
        return

    def get_acs_agent(self):
        """
        Get the ACS Agent Version of the device.

        :rtype: AcsAgent
        :return: ACS Agent or None if no agent
        """
        return None

    def is_rooted(self):
        """
        Check if the device has root rights

        :rtype: bool
        :return: True if device is rooted, False otherwise
        """
        return False

    def has_intel_os(self):
        """
        Check if the device os is compiled by Intel.
        An os that is not 'Intel' is a reference os (compiled by a thirdparty).
        For example, on Android, this means that the os image is signed with Intel's key, and
        thus ACS will have extended permissions.

        :rtype: bool
        :return: True if os is compiled by Intel, False otherwise
        """
        return False

    def retrieve_debug_data(self, verdict=None, tc_debug_data_dir=None):
        """
        Retrieve debug log.
        Usually call after a critical failure & reboot

        :param verdict: Verdict of the test case
        :param tc_debug_data_dir: Directory where data will be stored
        """
        return

    def get_crash_events_data(self, tc_name):
        """
        Return debug log of corresponding failed/blocked TC

        :type tc_name: str
        :type logs: str

        :return: additional logs
        :rtype: str array

        .. attention:: Currently stubbed
        """
        return list()

    def get_reporting_device_info(self):
        """
        Collect all device/build info available on the device for reporting


        :return: Verdict for device info retrieval, device and build infos
        :rtype: tuple enum("PASS", "FAIL", "BLOCKED", "INTERRUPTED"), dict
        """

        # Add device / build information for ACS Live Reporting tool
        return Verdict.PASS, {"ALR": {"device_id": self.device_properties.device_id,
                                      "sw_release": self.device_properties.sw_release
                                      }
                              }

    def get_uecmd(self, uecmd_domain, reuse_existing_object_if_possible=False):
        """
        Get uecmd layer for this phone.

        :type uecmd_domain: String
        :param uecmd_domain: Domain of UeCmd where to find it.

        :type reuse_existing_object_if_possible: boolean
        :param reuse_existing_object_if_possible: if set to True it
        will try to check if there is not already instanciated uecmd class
        instead of creating one.

        :rtype: UECmd
        :return: uecmd instance
        """
        factory_path = "%s.Factory.Factory" % self._uecmd_path
        factory = Common.get_class(factory_path)(self)

        if factory:
            # if uecmd already exist and we want to reuse it them search for it
            # from the dict
            if reuse_existing_object_if_possible and uecmd_domain.upper() in self.uecommands.keys():
                uecmd_inst = self.uecommands.get(uecmd_domain.upper())
            # else generate a new one and store it on the list
            else:
                uecmd_inst = factory.get_uecmd(uecmd_domain)
                self.uecommands[uecmd_domain.upper()] = uecmd_inst
        else:
            raise DeviceException("%s %s" % (DeviceException.INSTANTIATION_ERROR, self._uecmd_path))

        return uecmd_inst

    @property
    def flash_device_properties(self):
        """
        Get the properties of the device.

        :rtype: acs.Device.FlashDeviceProperties.FlashDeviceProperties
        :return: Flash Device properties
        """
        return self._flash_device_properties

    @property
    def device_properties(self):
        """
        Get the properties of the device.

        :rtype: acs.Device.DeviceProperties.DeviceProperties
        :return: Device properties
        """
        return self._device_properties

    def stop_connection_server(self):
        """
        Stop the server used for device connection
        """
        return

    def retrieve_properties(self):
        """
        Retrieve full device information as dictionary of
        property name and its value

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        return {}

    def get_tc_acceptance_criteria(self):
        """
        Get the device acceptance criteria for any UC.

        :rtype: tuple (int, int)
        :return: tuple (max attempt, acceptance)
        """

        # Store acceptance criteria value
        acceptance = self.get_config("TcAcceptanceCriteria", 1, int)

        # Backward compatibility on Max retry
        tc_max_retry = self.get_config("TcMaxRetry", None, int)
        tc_max_attempt = self.get_config("TcMaxAttempt", None, int)

        if tc_max_retry is not None and tc_max_attempt is not None:
            # Store TcMaxAttempt in priority if both parameters exist
            max_attempt = tc_max_attempt
        elif tc_max_retry is not None:
            # Store TcMaxRetry if exists
            max_attempt = tc_max_retry
        elif tc_max_attempt is not None:
            # Store TcMaxAttempt if exists
            max_attempt = tc_max_attempt
        else:
            # Return default value for Tc max attempt
            max_attempt = 1

        return max_attempt, acceptance

    def retrieve_device_info(self):
        """
        Retrieve device information in order to fill related global
        parameters.
        Retrieved values will be accessible through its getter.

            - Build number (SwRelease)
            - Device IMEI
            - Model number
            - Baseband version
            - Kernel version
            - Firmware version
            - acs agent version

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        self.get_logger().debug("Retrieve device info from device not implemented")
        return {}

    def retrieve_serial_number(self):
        """
        Retrieve the serial number of the device, used when communicating with it.

        :rtype: str
        :return: serial number of the device, or None if unknown
        """
        return AcsConstants.NOT_AVAILABLE

    def get_report_tree(self):
        """
        Return the instance of CampaignReportTree which give access to specific report path
        :rtype: CampaignReportTree object
        :return: the instance of the campaign report tree
        """
        return self._global_config.campaignConfig.get("campaignReportTree")

    def get_config(self, config_name, default_value=None, default_cast_type=str):
        """
        Return the value of the given device config name
        The type of the value can be checked before assignment
        A default value can be given in case the config name does not exist

        :type config_name: string
        :param config_name: name of the property value to retrieve

        :type default_value: object
        :param default_value: default_value of the property

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: string or type of default_cast_type
        :return: config value
        """

        return self._device_config.get_value(config_name, default_value, default_cast_type)

    @property
    def min_file_install_timeout(self):
        """
        Return the minimum timeout to set when pushing files on device

        :rtype: int
        :return: minimum timeout (in sec)
        """
        return self._min_file_install_timeout

    def get_device_module(self, module_name):
        """
        Instantiate the specified module

        :type module_name: str
        :param module_name: the module name to instantiate

        :rtype: obj
        :return: the specified module instance

        """
        modules = self.get_device_modules(module_name)
        if not modules:
            raise AcsConfigException("Cannot load \"{0}\" device module".format(module_name),
                                     "Cannot find the module name in the device configuration.")
        return modules[0]

    def get_device_modules(self, module_name):
        """
        Instantiate the specified module(s)

        :type module_name: str
        :param module_name: the module name to instantiate

        :rtype: obj
        :return: list of the specified module instance

        """
        if module_name not in self._module_instances:
            self._module_instances[module_name] = DeviceModuleFactory.create(module_name, self, self._global_config)
        return self.device_modules[module_name]

    def start_device_log(self, log_path):
        """
        Starts a device logging session and record log in a file.

        :type log_path: str
        :param log_path: path to create log file
        :return:
        """
        self._logger.warning("start_device_log is not implemented for this device, log file won't be created")

    def stop_device_log(self):
        """
        Stops a device logging session
        """
        pass

    def setup(self):
        """
        Set up the environment of the target after connecting to it

        :rtype: (bool, str)
        :return: status and message
        """
        status, message = True, ""
        return status, message

    def cleanup(self, campaing_error):
        """
        Clean up the environment of the target.

        :type campaing_error: boolean
        :param campaing_error: Notify if errors occured

        :rtype: tuple of int and str
        :return: verdict and final dut state
        """
        status, message = 0, ""
        return status, message

    def clean_debug_data(self):
        """
        Remove intermediate debug log files and folders that should not be
        present in the final report folder
        """
        return True

    def is_capable(self, capability):
        """
        This method check if the requested capabilities is inside a capability list
        The requested capabilities can be :
            - a capability name
            - a list of capability name separated by 'or' keyword. This method will implement the 'or' logical
              method will return true if at least of capability is in the capability list
              example: 'cap1 or cap2 or cap3'
            - a list of capability name separated by 'and' keyword. This method will implement the 'and' logical
              method will return true if all capabilities are in the capability list
              example: 'cap1 and cap2 and cap3'

        :param capability: a request capability
        :type capability: string

        :return a boolean
        """
        return DCManager.is_capable(capability, self.device_capabilities)

    def _settledown(self, settledown_duration):
        """
        Do device settle down

        :param settledown_duration: settle down
        :type settledown_duration: int

        :return None
        """
        # if no output for x seconds, print an info every 5mn
        refresh_stdout_in_sec = 300

        if settledown_duration:
            self._logger.debug("Wait settle down duration (%ds) before continue", settledown_duration)

            div_duration_by_refresh, remainder = divmod(settledown_duration,
                                                        refresh_stdout_in_sec)
            # duration_in_sec = refresh_stdout_in_sec * div_duration_by_refresh + remainder
            for i in range(1, int(div_duration_by_refresh) + 1):
                elapsed_time = i * refresh_stdout_in_sec
                time.sleep(refresh_stdout_in_sec)
                self._logger.info("Suspend execution since {0} seconds".format(elapsed_time))
            time.sleep(remainder)

    def reboot(self):
        """
        Soft reboot implementation
        """
        return True
