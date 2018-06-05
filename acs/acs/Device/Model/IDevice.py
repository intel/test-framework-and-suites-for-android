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
:summary: This file expose the device interface IDevice
:since: 09/03/2011
:author: sfusilie
"""

from acs.ErrorHandling.DeviceException import DeviceException


class IDevice():

    """
    Abstract class that defines the interface to be implemented
    by a device.
    """
    # pylint: disable=W0232
    # pylint: disable=W0613

    def initialize(self):
        """Initialize the environment of the target.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def setup(self):
        """
        Set up the environment of the target after connecting to it

        :rtype: (bool, str)
        :return: status and message
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def cleanup(self, campaing_error):
        """
        Clean up the environment of the target.

        :type campaing_error: boolean
        :param campaing_error: Notify if errors occured

        :rtype: tuple of int and str
        :return: verdict and final dut state
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def remove_device_files(self, device_directory, filename_regex):
        """
        Remove file on the device

        :type device_directory: str
        :param device_directory: directory on the device

        :type  filename_regex: str
        :param filename_regex: regex to identify file to remove

        :rtype: list
        :return: Output status and output log
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def install_file(self, file_path):
        """
        Depreccated function push applications onto target from a given folder$

        :type file_path: str
        :param file_path: the app to install

        :rtype: list
        :return: Output status and output log
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def switch_on(self, boot_timeout=None, settledown_duration=None,
                  simple_switch_mode=False):
        """
        Switch ON the board

        :param boot_timeout: Total time to wait for booting
        :param settledown_duration: Time to wait until start to count for timeout,
                                    Period during which the device must have started.
        :rtype: list
        :return: Output status and output log
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def switch_off(self):
        """
        Switch OFF the board

        :rtype: list
        :return: Output status and output log
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def connect_board(self):
        """
        Open connection to the board
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def disconnect_board(self):
        """
        Disconnect the board.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def stop_connection_server(self):
        """
        Stop the server used for device connection
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def run_cmd(self, cmd, timeout,
                force_execution=False,
                wait_for_response=True,
                silent_mode=False):
        """
        Execute the input command and return the result message
        If the timeout is reached, return an exception

        :type  cmd: string
        :param cmd: cmd to be run
        :type  timeout: integer
        :type force_execution: Boolean
        :param timeout: Script execution timeout in ms
        :param force_execution: Force execution of command
                    without check phone connected (dangerous)
        :param wait_for_response: Wait response from adb before
                                        stating on command

        :return: Execution status & output string
        :rtype: Integer & String
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def screenshot(self, prefix, filename):
        """
        Take a screenshot of the board

        :type prefix: str
        :type filename: str

        :param prefix: Prefix to use before device name
        :param filename: Filename to use

        :return: None
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def pull(self, remotepath, localpath, timeout=None):
        """
        Pull a file from remote path to local path

        :type remotepath: str
        :param remotepath: the remote path , eg /acs/scripts/from.txt

        :type localpath: str
        :param localpath: the local path , eg /to.txt

        :type timeout: float or None
        :param timeout: Set a timeout in seconds on blocking read/write operations.
                        timeout=0.0 is equivalent to set the channel into a no blocking mode.
                        timeout=None is equivalent to set the channel into blocking mode.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def push(self, localpath, remotepath, timeout=None):
        """
        Push a file from local path to remote path

        :type remotepath: str
        :param remotepath: the remote path , eg /acs/scripts/to.txt

        :type localpath: str
        :param localpath: the local path , eg /from.txt

        :type timeout: float or None
        :param timeout: Set a timeout in seconds on blocking read/write operations.
                        timeout=0.0 is equivalent to set the channel into a no blocking mode.
                        timeout=None is equivalent to set the channel into blocking mode.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_uecmd(self, uecmd_domain):
        """
        Get uecmd layer for this device.

        :type uecmd_domain: str
        :param uecmd_domain: Domain of UeCmd where to find it.

        :rtype: UECmd
        :return: uecmd instance
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_logger(self):
        """
        Return the logger instance of the device

        :rtype: logger
        :return: Device logger
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def is_available(self):
        """
        Check if the board can be used.

        :rtype: bool
        :return: availability status
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def is_booted(self):
        """
        Check if the board has booted successfully.

        :rtype: bool
        :return: boot status
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def is_rooted(self):
        """
        Check if the device has root rights

        :rtype: bool
        :return: True if device is rooted, False otherwise
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def has_intel_os(self):
        """
        Check if the device os is compiled by Intel.
        An os that is not 'Intel' is a reference os (compiled by a thirdparty).
        For example, on Android, this means that the os image is signed with Intel's key, and
        thus ACS will have extended permissions.

        :rtype: bool
        :return: True if os is compiled by Intel, False otherwise
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def device_modules(self):
        """
        Return device modules
        :rtype list
        :return: List of device modules
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def device_capabilities(self):
        """
        Return device capabilities
        :rtype list
        :return: List of device capabilities
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def device_properties(self):
        """
        Get the properties of the device.

        :rtype: acs.Device.DeviceProperties.DeviceProperties
        :return: Device properties
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def logger(self):
        """
        Retrieve the logger associated to that device
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_name(self):
        """
        Get the device model name.

        :return: device model name
        :rtype: str
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_serial_number(self):
        """
        Get the device's serial number, used when communicating with it

        :return: device serial number
        :rtype: str
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_device_id(self):
        """
        Get the device's unique id

        :return: device unique id
        :rtype: str
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_model_number(self):
        """
        Get the Model Number of the device.

        :rtype: str
        :return: Model Number
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def model_number(self):
        """
        Get the Model Number of the device.

        :rtype: str
        :return: Model Number
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_baseband_version(self):
        """
        Get the Baseband Version of the device.
        (Modem sw release)

        :rtype: str
        :return: Baseband Version
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_kernel_version(self):
        """
        Get the Kernel Version of the device.

        :rtype: str
        :return: Kernel Version
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_imei(self):
        """
        Get the IMEI of the device.
        (International Mobile Equipment Identity)

        :rtype: str
        :return: Imei number
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_fw_version(self):
        """
        Get the Firware Version of the device.
        (International Mobile Equipment Identity)

        :rtype: str
        :return: Firmware version
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_os_version_name(self):
        """
        Get the version's name of the os.

        :rtype: str
        :return: os version's name
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_acs_agent(self):
        """
        Get the ACS Agent Version of the device.

        :rtype: AcsAgent
        :return: ACS Agent or None if no agent
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_ui_type_timeout(self):
        """
        Get the timeout for type from UI.

        :return: device type timeout from ui
        :rtype: str
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_debug_data(self, verdict=None, tc_debug_data_dir=None):
        """
        Usually call after a critical failure & reboot
        It will fetch all debug data.
        :param verdict: Verdict of the test case
        :param tc_debug_data_dir: Directory where data will be stored
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_crash_events_data(self, tc_name):
        """
        Request the device to get failure logs

        :type tc_name: str
        :param tc_name: Test Case name

        :return: additional logs
        :rtype: str array
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_reporting_device_info(self):
        """
        Collect all device build info on the device for reporting

        :return: device and build infos
        :rtype: dict
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def inject_device_log(self, priority, tag, message):
        """
        Logs to device log
        .. note:: This method is Android-related,
                backport to other OS should be studied

        :type priority: str
        :type tag: str
        :type message: str

        :param priority: Priority of og message, should be:
                         v: verbose
                         d: debug
                         i: info
                         w: warning
                         e: error
        .. seealso:: http://developer.android.com/guide/developing/tools/adb.html#logcat

        :param tag: Tag to be used to identify the log onto logcat
        :param message: Message to be writed on log.

        :return: command status
        :rtype: bool
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_state(self):
        """
        Gets the device state

        :rtype: str
        :return: device state : alive, unknown, offline
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def close_connection(self):
        """
        stop the process that communicate with the board
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def start_connection(self):
        """
        start the process that communicate with the board
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_boot_timeout(self):
        """
        Return the boot timeout set in catalog.

        :rtype: int
        :return: boot time in seconds.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def set_filesystem_rw(self):
        """
        Set the file system in read/write mode.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_sw_release(self):
        """
        Get the SW release of the device.

        :rtype: str
        :return: SW release
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_serial_number(self):
        """
        Retrieve the serial number of the device, used when communicating with it.

        :rtype: str
        :return: serial number of the device, or None if unknown
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_device_id(self):
        """
        Retrieve the unique id of the device.

        :rtype: str
        :return: unique id of the device, or None if unknown
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def reboot(self, mode="MOS", wait_for_transition=True,
               transition_timeout=None, skip_failure=False,
               wait_settle_down_duration=False):
        """
        Perform a software reboot on the board.
        By default will bring you to MOS and connect acs once MOS is seen.
        this reboot require that you are in a state where adb command can be run.

        :type mode: str or list
        :param mode: mode to reboot in, support MOS, COS, POS, ROS. It can be a list of these modes
               (ie ("COS","MOS"))
               .. warning:: it is not always possible to reboot in a mode from another mode
                eg: not possible to switch from ROS to COS

        :type wait_for_transition: boolean
        :param wait_for_transition: if set to true,
                                    it will wait until the wanted mode is reached

        :type transition_timeout: int
        :param transition_timeout: timeout for reaching the wanted mode
                                    by default will be equal to boot timeout set on
                                    device catalog

        :type skip_failure: boolean
        :param skip_failure: skip the failure, avoiding raising execption, using
                                this option block the returned value when it is equal to False

        :type wait_settle_down_duration: boolean
        :param wait_settle_down_duration: if set to True, it will wait settleDownDuration seconds
                                          after reboot for Main OS only.

        :rtype: boolean
        :return: return True if reboot action succeed depending of the option used, False otherwise
                 - if wait_for_transition not used, it will return True if the reboot action has been seen
                   by the board
                 - if wait_for_transition used , it will return True if the reboot action has been seen
                   by the board and the wanted reboot mode reached.
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def soft_shutdown_cmd(self):
        """
        Soft Shutdown command, if permissions are ok (rooted)
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def soft_shutdown(self, wait_for_board_off=False):
        """
        Soft Shutdown the board, if permissions are ok (rooted)

        :type wait_for_board_off: boolean
        :param wait_for_board_off: Wait for device is off or not after soft shutdown

        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_soft_shutdown_settle_down_duration(self):
        """
        return the value of soft shutdown settle down duration from catalog
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def hard_shutdown(self, wait_for_board_off=False):
        """
        Soft Shutdown the board, if permissions are ok (rooted)

        :type wait_for_board_off: boolean
        :param wait_for_board_off: Wait for device is off or not after soft shutdown

        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_properties(self):
        """
        Retrieve full device information as dictionary of
        property name and its value

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_device_info(self):
        """
        Retrieve device information in order to fill related global parameters.
        Retrieved values will be accessible through its getter.

            - Build number (SwRelease)
            - Device IMEI
            - Model number
            - Baseband version
            - Kernel version
            - Firmware version
            - acs agent version

        :rtype: None
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_device_info(self):
        """
        Get device information.

        :rtype: dict
        :return a dictionnary containing device info
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_application_logs(self, destination, tag=None):
        """
        retrieve application logs from the board.

        :type destination: string
        :param destination: destination folder to be finished by an /

        :type tag: string
        :param tag: if tag is not None then it will retrieve all applog since more recent occurence of tag

        :rtype: list of string
        :return: return the list of pulled file
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_sdcard_path(self):
        """
        Return the path to the external sdcard
        :rtype: str
        :return: sdcard path
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_usbdrive_path(self):
        """
        Return the path to the external USB drive
        :rtype: str
        :return: USB drive path
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_provisioning_method(self):
        """
        Return the provisioning method
        :rtype: str
        :return: provisioning method
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_provisioning_data_path(self):
        """
        Return the path to data file used by address provisioning
        :rtype: str
        :return: provisioning data path
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def config(self):
        """
        Return device configuration
        :rtype: AttributeDict
        :return: device configuration
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def binaries_path(self):
        """
        Return the path to the local binaries folder
        :rtype: str
        :return: local binaries directory
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def multimedia_path(self):
        """
        Return the path to the local multimedia files
        :rtype: str
        :return: local multimedia directory
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_ftpdir_path(self):
        """
        Return the path to the local FTP files
        :rtype: str
        :return: local FTP directory
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_tc_acceptance_criteria(self):
        """
        Get the device acceptance criteria for any UC.

        :rtype: tuple (int, int)
        :return: tuple (max attempt, acceptance)
        """
        raise DeviceException(
            DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_time_before_wifi_sleep(self):
        """
        Get the time to wait for Wifi networks to be disconnected.

        :rtype: int
        :return: time in seconds to wait for Wifi disconnection
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_default_wall_charger(self):
        """
        Get the default wall charger name for this device.
        Usefull to connect the right charger for a device.

        :rtype: str
        :return: wall charger name ( DCP, AC_CHGR),
                must match with IO CARD charger name
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_boot_mode(self):
        """
        get the boot mode from adb

        :rtype: string
        :return: phone state : MOS, ROS, COS or UNKNOWN
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_config(self, config_name, default_value=None, default_cast_type=str):
        """
        get the device config value

        :type config_name: string
        :param config_name: name of the property value to retrieve

        :type default_value: string
        :param default_value: default_value of the property

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: string
        :return: config value
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def synchronyze_board_and_host_time(self):
        """make the board time and the acs host time to be the same"""
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_application_instance(self, app_name):
        """
        Get instance of application to be managed on this phone

        :type app_name: String
        :param app_name: Name of the application.

        :rtype: Application
        :return: application instance
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def send_at_command(self, at_command, timeout, com_port):
        """
        send at command to modem via com_port, this method is IMC modem only!
        user should be very careful when they choose the com port, it may have
        the collision risks with other app as Ril, Modem manager

        :param at_command: at command to send to modem
        :type at_command: str

        :param timeout: timeout of modem response
        :type timeout: int

        :param com_port: the port which modem_test use to send AT command.
        If the value is None, use the default port definied in Device_Catalog.xml
        :type com_port: str

        :return: Execution status & output string
        :rtype: Integer & String
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_em_parameters(self):
        """
        return energy management paramater declared on device_catalog for your current device.
        there are on the <EM> </EM>
        only paramter that are use on usecase will be return like threshold or supported feature.
        :rtype : dict
        :return: return a dictionnary where key are the parameter name and value the parameter value
                 an empty field will be set to a default value
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_cellular_network_interface(self):
        """
        Return the ip interface of celluar network

        this interface can be obtained from the command "busybox ifconfig"
        :rtype: str
        :return: telephony ip interface
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def init_acs_agent(self):
        """
        Init ACS agent for the device
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_device_os_path(self):
        """
        Get a module to manipulate path on device.

        :rtype:  path
        :return: a module to manipulate device path
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    @property
    def min_file_install_timeout(self):
        """
        Return the minimum timeout to set when pushing files on device

        :rtype: int
        :return: minimum timeout (in sec)
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def use_ethernet_connection(self):
        """
        get if we want to use an ethernet connection to
        communicate with the device.

        :rtype: bool
        :returns: true if the option as be set to true on device catalog, false otherwise
        """
        raise DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def get_device_module(self, module_name):
        """
        Instantiate the specified module

        :type module_name: str
        :param module_name: the module name to instantiate

        :rtype: obj
        :return: the specified module instance

        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def start_device_log(self, log_path):
        """
        Starts a device logcat thread

        :type log_path: str
        :param log_path: path to logcat extract
        :return:
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def stop_device_log(self):
        """
        Stops a device logcat thread

        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

    def retrieve_os_version(self):
        """
        Retrieve all available OS version for this OS
        :rtype: list
        :return: list of available os version
        """
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)

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
        return DeviceException(DeviceException.FEATURE_NOT_IMPLEMENTED)
