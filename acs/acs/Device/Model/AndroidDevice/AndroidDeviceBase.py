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


import imp
import os
import re
import posixpath
import socket
import threading
import time
import string

from datetime import datetime
from os import path

import acs.UtilitiesFWK.Utilities as Util
from acs.Core.CampaignMetrics import CampaignMetrics
from acs.Device.DeviceLogger.LogCatLogger.LogCatLogger import LogCatLogger
from acs.Device.DeviceManager import DeviceManager
from acs.Device.Model.DeviceBase import DeviceBase
from acs.UtilitiesFWK.ADBUtilities import ADBSocket
from acs.UtilitiesFWK.Utilities import AcsConstants, Global, run_local_command, internal_shell_exec
from acs.UtilitiesFWK.CommandLine import CommandLine
# import acs.UtilitiesFWK.DateUtilities as DateUtil
from acs.Device.Model.AndroidDevice.Agent.Factory import get_acs_agent_instance
from acs.ErrorHandling.AcsBaseException import AcsBaseException
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.DeviceException import DeviceException
from acs.Device.DeviceController import DeviceController
from acs.Core.Report.ACSLogging import LOGGER_WD
from acs.Core.PathManager import Paths

ADB_CMD_NAME = "adb"
FASTBOOT_CMD_NAME = "fastboot"

ADB_SOCK_CMDS_LIST = ["get-state",
                      "install",
                      "uninstall",
                      "push",
                      "pull",
                      "wait-for-device",
                      "mount",
                      "remount",
                      "reboot bootloader",
                      "reboot recovery",
                      "gtester",
                      "mmgr-test",
                      "shell am instrument",
                      "shell getprop",
                      "shell nohup"]


class AndroidDeviceBase(DeviceBase):

    """
        Android Phone Base implementation
    """

    OS_TYPE = 'ANDROID'

    def __init__(self, config, logger):
        """
        Constructor

        :type  phone_name: string
        :param phone_name: Name of the current phone(e.g. PHONE1)
        """

        DeviceBase.__init__(self, config, logger)

        # retrieve board type from device parameters given to ACS command line option
        self.device_properties.board_type = self.get_config("boardType", "Not Available", str)
        # device_id is the unique identifier of the device
        self.device_properties.device_id = None

        self._supported_android_versions = self.retrieve_os_version()

        self._android_version = (self.get_config("AndroidVersion") or self.get_config("OSVersion", "Unknown")).title()

        self._android_codeline = self.get_config("AndroidCodeLine", "Default")
        self._prss_pw_btn_time_switch_off = self.get_config("pressPowerBtnTimeSwitchOff", 10, int)
        self._prss_pwr_btn_time_switch_on = self.get_config("pressPowerBtnTimeSwitchOn", 3, int)
        self._call_setup_timeout = self.get_config("callSetupTimeout", 15, int)
        self._uecmd_default_timeout = self.get_config("defaultTimeout", 50, int)
        self._boot_timeout = self.get_config("bootTimeout", 300, int)
        self._settledown_duration = self.get_config("settleDownDuration", 0, int)

        # _serial_number is the identifier used to communicate with the board (serialno if USB, IP if ethernet)
        self._serial_number = self.get_config("serialNumber", "")

        self._my_path = path.dirname(path.abspath(__file__))

        # By default we use adb socket
        self._phone_handle = None
        self._adb_server_port = self.get_config("adbServerPort", 5037, int)
        self._use_adb_socket = self.get_config("useAdbSocket", "False", "str_to_bool")
        self._enableAdbRoot = self.get_config("enableAdbRoot", "False", "str_to_bool")
        self._adb_root_timeout = self.get_config("adbRootTimeout", 10.0, float)
        self._adb_root_cmd_timeout = self.get_config("adbRootCmdTimeout", 2, float)
        # adb connect timeout will be used as timeout for adb connect and adb start server cmds
        self._adb_connect_timeout = self.get_config("adbConnectTimeout", 10, float)
        self._enableIntelImage = self.get_config("enableIntelImage", "False", "str_to_bool")
        self._binaries_path = self.get_config("binPath", "/system/bin/")
        self._userdata_path = self.get_config("userdataPath", "/sdcard/acs_files/")
        self._ext_sdcard_path = self.get_config("sdcard_ext", "/sdcard/")
        self._screen_resolution = self.get_config("screenResolution", "480x854")

        self._wlan_device = self.get_config("wlanDevice", "wlan0:0")
        self._gps_property_key = self.get_config("gpsPropertyKey", "gps.serial.interface")
        self._wlan_phy_device = self.get_config("wlanPhyDevice", "phy0")

        self._prov_method = self.get_config("provisioningMethod", "")
        self._prov_data_path = self.get_config("provisioningPath", "")

        self._ui_dictionary_name = self.get_config("uiDictionnaryName")
        self._ui_type_timeout = self.get_config("uiTypeTimeout", 5, float)
        self._monkey_port = self.get_config("monkeyPort", 8080, int)
        self._sc_repo = self.get_config("scRepo")

        self._screenshot_enable = self.get_config("takeScreenshot", "False", "str_to_bool")
        self._handle_adb_restart = self.get_config("handleAdbRestart", "False", "str_to_bool")
        self._usb_sleep_duration = self.get_config("usbSleep", 10, int)
        self._fw_boot_time = self.get_config("fwBootTime", 10, int)
        self._phone_number = self.get_config("phoneNumber", "")
        # Secondary phone number
        self._phone_number2 = self.get_config("phoneNumber2", "")

        self._time_before_wifi_sleep = self.get_config("timeBeforeWifiSleep", 1200, int)

        self._use_adb_over_ethernet = self.get_config("adbOverEthernet", "False", "str_to_bool")
        self._do_adb_disconnect = self.get_config("adbDisconnect", "True", "str_to_bool")
        self._reboot_on_retry_on_setup = self.get_config("rebootOnRetryOnSetup", "False", "str_to_bool")
        self._ip_address = self.get_config("ipAddress", "192.168.42.1")
        self._pos_ip_adress = self.get_config("POSipAddress", "192.168.42.1")
        self._adb_port = self.get_config("adbPort", 5555, int)
        self._adb_connect_retries_nb = self.get_config("ADBConnectRetriesNb", 3, int)
        self._tcp_connect_retries_nb = self.get_config("TCPConnectRetriesNb", 3, int)
        # EM parameter
        self._default_wall_charger = self.get_config("defaultWallCharger", "")

        # Shutdown management
        self._hard_shutdown_duration = self.get_config("hardShutdownDuration", 20, int)
        self._soft_shutdown_duration = self.get_config("softShutdownDuration", 30, int)
        self._soft_shutdown_settle_down_duration = self.get_config("softShutdownSettleDownDuration", 20.0, float)
        # Block until adb reboot command returns or not (in some cases, the command is blocked whereas reboot is
        # correctly done
        self._wait_reboot_cmd_returns = self.get_config("waitSoftRebootCmdReturns", "True", "str_to_bool")

        # Telephony parameter
        self.__at_com_port = self.get_config("ATComPort")
        self.__default_pin_code = self.get_config("defaultPINCode", None)
        self.__sim_puk_code = self.get_config("simPUKCode", None)

        # PUPDR parameter
        self._soft_shutdown_cmd = "adb shell am start -a android.intent.action.ACTION_REQUEST_SHUTDOWN"

        # Get flash paths
        self._acs_flash_file_path = Paths.FLASH_FILES

        # Watchdog
        self.__watchdog_errors_nb = self.get_config("WatchDogMaxErrorNb", 10, int)
        self.__watchdog_errors_nb_before_adb_retry = int(self.__watchdog_errors_nb / 2)
        self.__watchdog_sleep_time = self.get_config("WatchDogSleepTime", 1, int)
        self.__is_up = False

        # Device log file for individual tests
        self._device_log_file = None

        if not self._use_adb_over_ethernet:

            if self._serial_number and self._serial_number != "":
                # Socket between ACS and ADB SERVER
                self._phone_handle = ADBSocket(logger=self.get_logger(), serial=self._serial_number,
                                               port=self._adb_server_port)
            else:
                # Socket between ACS and ADB SERVER
                self._phone_handle = ADBSocket(logger=self.get_logger(), port=self._adb_server_port)
            self.device_properties.device_id = self._serial_number

        else:
            self._serial_number = "%s:%d" % (self._ip_address, self._adb_port)

            # Socket between ACS and ADB SERVER
            self._phone_handle = ADBSocket(self.get_logger(), self._serial_number, self._use_adb_over_ethernet,
                                           self._ip_address, self._adb_port)

        # Default target sim is the first one
        self._target_sim = 1
        self._connection_lock = threading.Lock()
        self._device_logger = None
        self.__log_file_name = ""
        self._screenshot_count = 0
        self.__watchdog_thread = None
        self._is_device_connected = False
        self._is_phone_booted = False

        # loggers
        self._init_logger()
        self._current_time = datetime.now().strftime("%Y-%m-%d_%Hh%M.%S")

        # Watchdog variables
        self.__watchdog_stop_event = threading.Event()
        self.__watchdog_stop_event.set()

        self._acs_agent = get_acs_agent_instance(self, self._android_version)
        self._phone_handle.adb_start(self._adb_connect_timeout)
        self._eqts_controller = DeviceController.DeviceController(config.device_name, self._device_config,
                                                                  self.get_em_parameters(), self.get_logger())

    @property
    def write_logcat_enabled(self):
        """
        Do we need to write logcat from device to local host
        :return: Boolean
        """
        return self.get_config("writeLogcat", "True", "str_to_bool")

    def stop_connection_server(self):
        """
        Stop the server used for device connection
        """
        if self._phone_handle is not None and self._phone_handle._adb_server_is_running:
            self._phone_handle.adb_stop()

    def get_device_os_path(self):
        """
        get a module to manipulate device path

        :rtype:  path
        :return: a module to manipulate device path
        """
        return posixpath

    def _init_logger(self):
        """
         Initialize loggers
        """
        # Logcat init
        self.__log_file_name = None
        self._device_logger = LogCatLogger(self, self.write_logcat_enabled)
        # Watchod init
        self.__logger_wd = LOGGER_WD

    def init_device_connection(self, skip_boot_required, first_power_cycle, power_cycle_retry_number):
        """
        Init the device connection.

        Call for first device connection attempt or to restart device before test case execution
        """

        error_msg = ""
        connection_status = False
        power_cycle_occurence = 0
        boot_failure_occurence = 0
        connection_failure_occurence = 0

        # Perform boot sequence only if it is required
        if not skip_boot_required:

            # No need to switch off the board if ACS is just started
            # We switch off between each test cases, but not for the first test case in campaign
            if not first_power_cycle:
                # Switch off the device
                self.switch_off()

            # Loop as long as power cycle phase (boot + connect board) is failed according to power_cycle_retry_number
            while not connection_status and power_cycle_occurence < power_cycle_retry_number:
                # Try to switch ON : boot board + connect board
                # It consists in doing hardware power up + software boot + connection to device
                error_code, error_msg = self.switch_on()

                # We have done one extra power cycle occurence
                power_cycle_occurence += 1

                # if Boot has failed, redo a complete power cycle phase (switch on +
                # connect board) and before switch off the DUT
                if error_code != Global.SUCCESS:
                    error_msg = "Device has failed to boot ! "
                    self.get_logger().error(error_msg)

                    # Increment tracking variable with number of boot failure attempts
                    boot_failure_occurence += 1
                else:
                    # Check if the connection attempt is OK when boot procedure succeeds
                    # connect_board() is called inside switch_on method only when device is booted
                    if not self.is_available():
                        # Last connection attempt fails
                        # if connection has failed, redo a complete power cycle phase
                        # (switch on + connect board) and before switch off the DUT
                        # Increment tracking variable with number of connection failure attempts
                        connection_failure_occurence += 1

                        error_msg = ("Host has failed to connect "
                                     "to the device : failure occurence = %s ! " % connection_failure_occurence)
                        self.get_logger().error(error_msg)
                    else:
                        # Whole power cycle phase has succeeded, go out the current method
                        connection_status = True

                # First issue in the power cycle phase (either during boot phase or board connection)
                if not connection_status:
                    # If next power cycle occurence is the last boot procedure retry, try a hard switch off
                    # else do a normal switch off
                    if power_cycle_occurence > 1:
                        # Hard shutdown the device
                        self.hard_shutdown(wait_for_board_off=True)
                    else:
                        # Switch off the device
                        self.switch_off()
        else:
            # if boot is not required and device is booted then try to connect to the
            # device and update device information (SSN ...)
            if self.get_state() == "alive":
                self.connect_board()
                connection_status = True
            else:
                error_msg = ("[skipBootOnPowerCycle] option set in "
                             "Campaign Config file and device not seen connected to host PC")
                self.get_logger().warning(error_msg)
                # WARNING: We are not sure of the connection but we do not change existing behavior
                connection_status = True

        return connection_status, error_msg, power_cycle_occurence, boot_failure_occurence, connection_failure_occurence

    def init_acs_agent(self):
        """
        Check ACS agent version, and start it if needed
        """
        is_started = False

        acs_agent_version = self._check_acs_agent_version()

        if acs_agent_version and acs_agent_version != AcsConstants.NOT_INSTALLED:
            is_started = self._acs_agent.is_started

            if not is_started:
                # Start acs agent
                self._acs_agent.start()

                # Wait for acs agent started
                is_started = \
                    self._acs_agent.wait_for_agent_started(self.get_config("acsAgentStartTimeout", 60.0, float))

                if not is_started:
                    self.get_logger().warning("Unable to start ACS Agent ...")
                else:
                    self.get_logger().info("ACS Agent is started")
            else:
                self.get_logger().info("ACS Agent is already started")
        else:
            self.get_logger().info("ACS Agent is not installed")

        return is_started

    def _check_acs_agent_version(self):
        """
        Check if acs agent version matches with the acs release
        :rtype: string
        :return: Current ACS Agent Version
        """
        acs_agent_version = ""
        # Get acs release version
        acs_release_version = str(Util.get_acs_release_version())
        # Get acs agent version
        self.device_properties.acs_agent_version = self._acs_agent.version
        raw_agent_version = str(self.device_properties.acs_agent_version)

        # extract acs agent version from raw version
        expr = ".*ACS (?P<acs_version>([ -\\.a-zA-Z0-9]*))$"
        result = re.match(expr, raw_agent_version)

        if result is not None:
            acs_agent_version = str(result.group("acs_version"))
            if acs_agent_version in [None, ""]:
                self.get_logger().warning("Unable to parse acs agent version ! (%s)" % raw_agent_version)
                acs_agent_version = raw_agent_version
        else:
            self.get_logger().warning("Unable to get acs agent version ! (%s)" % raw_agent_version)
            acs_agent_version = raw_agent_version

        if acs_release_version != acs_agent_version:
            warning_msg = \
                "Acs agent version (%s) does not match with Acs framework version (%s)" \
                % (acs_agent_version, acs_release_version)
            self.get_logger().warning(warning_msg)

        return acs_agent_version

    def _start_extra_threads(self):
        """
        Starts extra threads required by ACS
        like logger & watchdog
        :return: None
        """
        # Start logging thread required for UECmd response
        self._start_logging()

        # Start watchdog threads for monitoring link to DUT
        self._start_watchdog()

    def _stop_extra_threads(self):
        """
        Stops extra threads required by ACS
        like logger & watchdog
        :return: None
        """
        # Stop logging thread required for UECmd response
        self._stop_logging()

        # Stop watchdog threads for monitoring link to DUT
        self._stop_watchdog()

    def _start_logging(self):
        """
        Starts logging required by ACS for UECmd response
        :return: None
        """
        # Start logging thread required for UECmd response
        file_path = ""
        if self.write_logcat_enabled or self.get_config("writeAcsLogcat", "False", "str_to_bool"):
            timestamp = Util.get_timestamp()
            if self._serial_number not in ["", None]:
                file_name = "%s_%s_%s_logcat.log" % (self.get_phone_model(),
                                                     re.sub(':', '_', self._serial_number), timestamp,)
            else:
                file_name = "%s_%s_logcat.log" % (self.get_phone_model(), timestamp,)

            file_path = os.path.join(self.get_report_tree().get_subfolder_path(subfolder_name="LOGCAT",
                                                                               device_name=self._device_name),
                                     file_name)
        self.__log_file_name = file_path
        self._device_logger.set_output_file(self.__log_file_name)

        self._device_logger.start()

    def _stop_logging(self):
        """
        Stops logging required by ACS for UECmd response
        :return: None
        """
        # Stopping reader and analyser & writer threads
        self._device_logger.stop()

    def _start_watchdog(self):
        """
        Start the thread that will track adb lost cases.
        """
        if self.__watchdog_stop_event.is_set():
            self.__watchdog_thread = threading.Thread(target=self._run_watchdog)
            self.__watchdog_thread.name = "WatchDogThread_" + self.get_phone_model()

            self.__watchdog_stop_event.clear()
            self.get_logger().debug("Starting watchdog...")
            self.__watchdog_thread.start()
            self.get_logger().debug("Watchdog started")

    def _stop_watchdog(self):
        """
        Stop the watchdog thread.
        """
        if not self.__watchdog_stop_event.is_set():
            # pylint: disable=W0702
            self.get_logger().debug("Stopping watchdog...")
            self.__watchdog_stop_event.set()

            if self.__watchdog_thread is not None:
                try:
                    self.__watchdog_thread.join(5)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception:
                    pass
                finally:
                    del self.__watchdog_thread
                    self.__watchdog_thread = None

    def get_watchdog_log_time(self):
        return self.get_config("WatchDogLogCycle", 5, float)

    @property
    def is_up(self):
        """
            Give the state of the device up or down
        :rtype: bool
        :return: device state
        """
        return self.__is_up

    def _update_device_up_state(self, previous_uptime):
        """
            Update the up state of the device by scanning /proc/time
        :type: float
        :param previous_uptime: uptime from last update
        :rtype: bool, float
        :return: uptime is updated, uptime value
        """
        updated = False
        uptime = 0.0
        adb_status, data = self.run_cmd("adb shell cat /proc/uptime", 5, silent_mode=True)
        if adb_status == Global.SUCCESS:
            updated = True
            if data:
                # ``data`` variable has to be 2 valid digits separated by a space (60.25 95.26)
                data = [str(el).replace('.', '') for el in data.split(' ')]  # we split on space
                if len(data) == 2 and data[0].isdigit() and data[1].isdigit():
                    uptime, real_time = data
                    self.__is_up = float(uptime) > float(previous_uptime)
            else:
                self.__logger_wd.warning("No data retreived from /proc/time")
        else:
            # Unable to update up status of the device
            # because adb connection is not available
            pass

        return updated, uptime

    def _manage_watchdog_errors(self, error_nb, exceptions):
        """
            Manage errors of watchdog mechanism
            Try to reconnect adb if lost
        :type: int
        :param error_nb: adb connections number
        :type: list
        :param exceptions: exceptions during adb connection
        :rtype: (bool, int)
        :return: order of terminating watchodg and updated error number (reset if adb retry succeed)
        """
        terminate_watchdog = False
        if error_nb >= self.__watchdog_errors_nb:
            self.__logger_wd.critical("Connection with the device was lost! "
                                      "Putting the device in disconnected state")
            if exceptions:
                self.__logger_wd.exception("Following error messages occurred : (%s)",
                                           "; ".join(exceptions))
            self.disconnect_board()
            # Device is disconnected, we can restart ADB server if needed
            # Be careful when you use several device with ACS
            if self._handle_adb_restart:
                self._phone_handle.adb_restart(self._adb_connect_timeout)
                # Terminate watchdog process
            terminate_watchdog = True
        elif error_nb >= self.__watchdog_errors_nb_before_adb_retry:
            self.__logger_wd.warning("Connection with the device was lost! "
                                     "Trying to reconnect ADB")
            if self._connect_adb()[0]:
                error_nb = 0

        return terminate_watchdog, error_nb

    def _run_watchdog(self):
        """
        Watchdog running thread.
        Get the Device's uptime, if the new uptime is lower than the previous stored,
        Device did reboot.

        Put the device in disconnect mode if we don't have answer x times
        (configurable using WatchDogMaxErrorNb option) consecutively
        """
        # pylint: disable=W0212
        # pylint: disable=W0702
        error_nb = 0
        exceptions = []
        previous_uptime = uptime = 0.0
        updated = False

        wd_log_time = self.get_watchdog_log_time()
        while not self.__watchdog_stop_event.is_set():
            t0 = time.time()
            # Execute shell command to check adb is available
            try:
                updated, uptime = self._update_device_up_state(previous_uptime)
                # adb connection is ok, and uptime has been updated from device
                if updated:
                    previous_uptime = uptime
                    error_nb = 0
                    exceptions = []
                else:
                    error_nb += 1
                # device is down and uptime is updated (no error on data retreive by adb)
                if not self.__is_up and uptime != 0:
                    self.__logger_wd.error("***** UNEXPECTED DEVICE REBOOT! *****")
                    CampaignMetrics.instance().unexpected_reboot_count += 1  # Incrementing Metrics count
                    previous_uptime = uptime = 0.0
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as cmd_exception:
                updated = False
                error_nb += 1
                error = str(cmd_exception)
                if error not in exceptions:
                    exceptions.append(error)

            self.__watchdog_stop_event.wait(self.__watchdog_sleep_time)
            if not self.__watchdog_stop_event.is_set():
                terminate_watchdog, error_nb = self._manage_watchdog_errors(error_nb, exceptions)
                if terminate_watchdog:
                    break
                # We inject a log if we are sure adb server is replying
                t1 = time.time()
                wd_log_time -= (t1 - t0)
                if wd_log_time < 0 and updated:
                    wd_log_time = self.get_watchdog_log_time()
                    self.inject_device_log("i", "ACS_WD", "Alive")

        self.__logger_wd.debug("Watchdog stopped")

    def _get_status_output(self, cmd):
        """
        Return (status, output) of executing cmd in a shell.

        :type cmd: str
        :param cmd: Shell command to run

        :rtype: list
        :return: Output status and output print
        """
        if os.name in ['nt', 'dos', 'os2']:
            # use Dos style command shell for NT, DOS and OS/2
            pipe = os.popen(cmd + ' 2>&1', 'r')
        else:
            # use Unix style for all others
            pipe = os.popen('{ ' + cmd + '; } 2>&1', 'r')
        text = pipe.read()
        sts = pipe.close()
        if sts is None:
            sts = 0
        if text[-1:] == '\n':
            text = text[:-1]
        return sts, text

    def _finalize_os_boot(self, timer, boot_timeout, settledown_duration):
        """
            After connection to the device, define actions that need to be done to declare device as booted
            :type timer: int
            :param timer: time already spent to boot device (in seconds)
            :type  boot_timeout: int
            :param boot_timeout: boot timeout maximum value (in seconds)
            :type settledown_duration: int
            :param settledown_duration: time to wait after boot procedure to have device ready (in seconds)
            :rtype: int
            :return: result of the flash procedure (Global.SUCCESS, Global.FAILURE, Global.BLOCKED)
            :rtype: str
            :return: Output message status
        """
        # adb is started and functional
        # We can ask its state to the device
        return_code = Global.FAILURE

        begin_time = time.time()
        end_time = begin_time + float(boot_timeout)
        state = self.get_boot_mode()

        while state == "UNKNOWN" and time.time() < end_time:
            state = self.get_boot_mode()

        # Compute time device takes to pass in MOS state
        timer = timer + time.time() - begin_time

        if state == "MOS":
            return_message = "Boot complete in %3.1fs; " % timer
            return_message += "Device is booted and ready to use!"
            self.get_logger().info(return_message)

            self._settledown(settledown_duration)

            if self._screenshot_enable:
                self.screenshot("BOOT")

            return_code = Global.SUCCESS
        else:
            # the device has failed to boot, it is not in MOS state
            return_message = "Device has failed to boot after %d seconds!" % timer
            return_message += "Device is currently in %s mode!" % str(state)
            self.get_logger().warning(return_message)
        return return_code, return_message

    def _check_ethernet_connection_is_available(self):
        """
        How to declare ethernet connection as available
        """
        # FIXME This functions should only check the connection state as done in IntelDeviceBase
        return self._phone_handle.adb_ethernet_start(self._ip_address,
                                                     self._adb_port,
                                                     self._adb_connect_retries_nb,
                                                     self._adb_connect_timeout)

    def _wait_board_is_ready(self, boot_timeout=None, settledown_duration=None):
        """
        Wait until device is ready to be used

        :type boot_timeout: int
        :param boot_timeout: max time in seconds to wait for device

        :type settledown_duration: int
        :param settledown_duration: fixed time waited if requested after boot procedure

        :rtype: int
        :return: Device status - ready to be used (boot procedure OK) or NOT (Global.SUCCESS, Global.FAILURE)

        :rtype: str
        :return: error message
        """
        if boot_timeout is None:
            # Timeout for total boot duration
            boot_timeout = self.get_boot_timeout()

        # By default we do wait settledown_duration after the boot procedure only if required by the user
        # if user needs a settledown duration after boot procedure it shall be set to a value (not None)

        # Loop while boot time not exceeded & read device state
        timer = 0
        status = Global.FAILURE
        return_code = Global.FAILURE
        return_message = ""

        while status == Global.FAILURE and timer < boot_timeout:
            # pylint: disable=W0702
            # at this method, the device is not yet available
            # we can have unexpected behavior on run_cmd
            # agree to catch all exception
            t_0 = time.time()
            try:
                # Break when Global.SUCCESS

                if not self._use_adb_over_ethernet:
                    status, status_msg = self.run_cmd("adb wait-for-device", boot_timeout, force_execution=True)
                    # Check output status and send debug log
                    if status == Global.SUCCESS:
                        self.get_logger().info("Device booted")
                    else:
                        msg = "No boot mode state returned"
                        if status_msg is not None:
                            msg = msg + ", error message: %s" % str(status_msg)
                        self.get_logger().debug(msg)
                # FIXME: the adb connection should be handle outside the check, because this method should only
                # check availability as its name indicate
                elif self._check_ethernet_connection_is_available():
                    status = Global.SUCCESS

            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as error:
                # Inform user of the exception
                self.get_logger().debug("Exception while booting the device : %s", str(error))
                # Wait 1 seconds to avoid relaunching the command multiple times
                time.sleep(1)

            t_1 = time.time()
            timer += t_1 - t_0

        if timer < boot_timeout and status == Global.SUCCESS:
            return_code, return_message = self._finalize_os_boot(timer, boot_timeout, settledown_duration)
        else:
            # Device still not booted
            # Device not connected or adb connection issue
            return_message = "Device has failed to boot after %d seconds! " % boot_timeout
            return_message += "Device not detected or adb connection issue"
            self.get_logger().warning(return_message)

        return return_code, return_message

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
            - serial number
            - board type
            - Store all device properties

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        properties = self.retrieve_properties()

        # retrieve software release if not already done
        self.device_properties.sw_release = self._retrieve_sw_release(properties)

        # retrieve imei if not already done
        self.device_properties.imei = self._retrieve_imei(properties)

        # retrieve model number if not already done
        self.device_properties.model_number = self._retrieve_model_number(properties)

        # retrieve baseband version if not already done
        self.device_properties.baseband_version = self._retrieve_baseband_version(properties)

        # retrieve kernel version if not already done
        self.device_properties.kernel_version = self._retrieve_kernel_version()

        # retrieve firmware version if not already done
        self.device_properties.fw_version = self._retrieve_fw_version(properties)

        if self._acs_agent:
            self.device_properties.acs_agent_version = self._acs_agent.version

        if self._serial_number in (None, "None", ""):
            # Retrieve current value of serial number
            self.retrieve_serial_number()

        # retrieve device unique id (if device is connected over USB, device_id is serial_number)
        if self.device_properties.device_id in (None, "None", ""):
            if self._use_adb_over_ethernet:
                self.device_properties.device_id = self._retrieve_device_id(properties)
            else:
                self.device_properties.device_id = self._serial_number

        # merge device info dict with getprop dict
        properties.update(self.get_device_info())
        return properties

    def get_device_info(self):
        """
        Get device information.

        :rtype: dict
        :return a dictionnary containing following values (key)
            - Build number (SwRelease)
            - Device IMEI (Imei)
            - Model number (ModelNumber)
            - Baseband version (BasebandVersion)
            - Kernel version (KernelVersion)
            - Firmware version (FwVersion)
            - acs agent version (AcsAgentVersion)
            - hardware variant (BoardType)
        """
        self.device_properties.acs_agent_version = self._acs_agent.version
        device_info = \
            {"SwRelease": self.device_properties.sw_release,
             "DeviceId": self.device_properties.device_id,
             "Imei": self.device_properties.imei,
             "ModelNumber": self.device_properties.model_number,
             "FwVersion": self.device_properties.fw_version,
             "BasebandVersion": self.device_properties.baseband_version,
             "KernelVersion": self.device_properties.kernel_version,
             "AcsAgentVersion": self.device_properties.acs_agent_version,
             "BoardType": self.device_properties.board_type}
        return device_info

    def retrieve_properties(self):
        """
        Retrieve full device information as dictionary of
        property name and its value

        :rtype: dict
        :return: Dict of properties and their associated values
        """
        adb_cmd_str = "adb shell getprop"

        status, status_msg = self.run_cmd(cmd=adb_cmd_str,
                                          timeout=self._uecmd_default_timeout,
                                          force_execution=True,
                                          silent_mode=True)

        result = {}
        try:
            if status == Global.SUCCESS:
                splitted_output = status_msg.splitlines()
                key_regex = ".*\[(?P<key>(.*))\]: \[(?P<value>(.*))\].*"

                # for each string (describing a property name and value),
                # we will retrieve name and value for store it into a dictionary
                reg_ex = re.compile(key_regex)
                for entry in splitted_output:
                    entry = entry.rstrip()
                    matches_str = reg_ex.search(entry)
                    if matches_str is not None:
                        # Read found properties
                        key = matches_str.group("key")
                        value = matches_str.group("value")
                        result[key] = value

            else:
                self.get_logger().debug("Unable to retrieve getprop info")
                result = {}

        except Exception as ex:  # pylint: disable=W0703
            self.get_logger().debug("Error occured when parsing getprop info ! (%s)" % str(ex))
            result = {}

        # Returns the dictionary containing all the device properties
        return result

    def soft_shutdown_cmd(self):
        """
        Soft Shutdown the device, if permissions are ok (rooted)
        """

        status = False

        try:
            result, output = self.run_cmd(self._soft_shutdown_cmd,
                                          self._uecmd_default_timeout,
                                          force_execution=True,
                                          wait_for_response=True)

            if result == Global.SUCCESS:
                if any(x in output.lower() for x in ["error", "exception", "unable"]):
                    self.get_logger().error("Soft shutdown command returned an error! (%s)" % (str(output)))
                else:
                    status = True
            else:
                self.get_logger().error("Soft shutdown command failed! (%s)" % (str(output)))

        except Exception as error:  # pylint: disable=W0703
            self.get_logger().debug("Soft shutting down the device failed: %s" % str(error))

        return status

    def use_ethernet_connection(self):
        """
        get if we want to use an ethernet connection to
        communicate with the device

        :rtype: bool
        :returns: true if the option as be set to true on device catalog, false otherwise
        """
        return self._use_adb_over_ethernet

    def get_device_ip(self):
        return self._ip_address

    def get_device_adb_port(self):
        return self._adb_port

    def get_serial_number(self):
        """
        Return the serial number of the device
        """
        return self._serial_number

    def get_device_id(self):
        """
        Return the unique id of the device
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.device_id")
        return self.device_properties.device_id

    def get_ui_type_timeout(self):
        """
        Return the timeout for type command
        """
        return self._ui_type_timeout

    def get_monkey_port(self):
        """
        Return the monkey runner port
        """
        return self._monkey_port

    def get_gps_property_key(self):
        """
        Return the gps property key to use in getprop command
        """
        return self._gps_property_key

    def get_name(self):
        """
        Return the device class name
        """
        return self._device_name

    def get_phone_number(self):
        """
        Return the phone number of the device
        """
        return self._phone_number

    def get_phone_number2(self):
        """
        Return the phone number of the secondary sim of the device
        """
        return self._phone_number2

    def get_target_phone_number(self):
        """
        Return the phone number of the targeted sim of the device, first otherwise

        :rtype: int
        :return: The current phone number corresponding to the current sim
        """
        if self._target_sim in [2, "2"]:
            return self._phone_number2

        return self._phone_number

    def get_touchsreen_event_file(self):
        """
        Accessor to the parameter touchsreenEventFile.
        This parameter should not be accessible from UC,
        so there is no need to add this function in the interface.
        :return: the value of touchsreenEventFile parameter in DeviceCatalog
        """
        return self.get_config("touchsreenEventFile")

    def get_usb_sleep_duration(self):
        """
        Return the duration in seconds to wait after unplugging/plugging USB

        :rtype: int
        :return: the duration in seconds
        """
        return self._usb_sleep_duration

    def initialize(self):
        """
        Initialize the environment of the target.
        """
        # Check the Android Version
        if self._android_version not in self._supported_android_versions:
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                     "Invalid AndroidVersion (" + self._android_version +
                                     "), should be in " + str(self._supported_android_versions))

    def setup(self):
        """
        Setup the environment of the target after connecting to it

        :rtype: (bool, str)
        :return: status and message
        """

        self.get_logger().info("AndroidDeviceBase: Setup device environment")

        status, message = True, ""

        return status, message

    def cleanup(self, campaing_error):
        """
        Clean up the environment of the target.

        :type campaing_error: boolean
        :param campaing_error: Notify if errors occured

        :rtype: tuple of int and str
        :return: status and final dut state
        """

        # In this function the device supports:
        # - ON (MOS) state
        # - OFF state
        # We need to handle all those items

        # Disconnect the DUT

        status = False
        final_dut_state = str(self._global_config.campaignConfig.get("finalDutState"))
        self.get_logger().debug("Try to leave device in following final state : %s" % (final_dut_state,))
        try:
            dut_state = self.cleanup_final_state(final_dut_state, campaing_error)
        except (KeyboardInterrupt, SystemExit):
            raise
        except DeviceException as device_io_exception:
            self.get_logger().error("Error happened when leaving device in %s ! (%s)" %
                                    (final_dut_state, device_io_exception.get_error_message()))
            dut_state = Util.DeviceState.UNKNOWN

        if final_dut_state == Util.DeviceState.UNKNOWN:
            self.get_logger().error("Cannot leave device in following final state : %s" % (final_dut_state,))
        else:
            status = True

        self.get_device_controller().release()

        return status, dut_state

    def cleanup_logs(self, campaing_error):
        """
        clean any log of the device

        :type campaing_error: boolean
        :param campaing_error: Notify if errors occured
        """

        pass

    def cleanup_final_state(self, final_dut_state, campaign_error):
        """
        Set final state of the device
        :param campaign_error:
        :param final_dut_state:
        :return: dut state
        """
        if final_dut_state == Util.DeviceState.ON:
            if self.get_boot_mode() != "MOS":
                # Power on the DUT
                status = (self.switch_on()[0] == Global.SUCCESS)
            else:
                self.get_logger().info("Device already power on")
                status = True
            self.cleanup_logs(campaign_error)
        elif final_dut_state == Util.DeviceState.OFF:
            self.cleanup_logs(campaign_error)
            # Power off the DUT
            status = (self.switch_off()[0] == Global.SUCCESS)
        elif final_dut_state == Util.DeviceState.NC:
            status = True
        else:
            self.cleanup_logs(campaign_error)
            # Charging mode cannot be detected on those devices
            # Just switch it off!
            self.get_logger().warning("Unsupported state for this device "
                                      "Trying to switch it off ...")
            status = (self.switch_off()[0] == Global.SUCCESS)

        if not status:
            final_dut_state = Util.DeviceState.UNKNOWN

        return final_dut_state

    def get_os_version_name(self):
        """
        Get the version's name of the os.

        :rtype: str
        :return: os version's name
        """
        return self._android_version

    def _init_boot_timeout(self, boot_timeout):
        """
        Initialize boot timeout to a valid int and default value
        if not defined by user
        :param boot_timeout: Total time to wait for booting
        :type boot_timeout: object
        :return: boot_timeout
        :rtype: int
        """
        if boot_timeout is None:
            self.get_logger().warning(
                "Boot timeout is not defined, using default value from Device_Catalog (%ds)" % self._boot_timeout)
            boot_timeout = self._boot_timeout
        elif not str(boot_timeout).isdigit() or boot_timeout < 0:
            # Check if we use an integer and check if not a negative value
            self.get_logger().warning(
                "Boot timeout (%s) must be a positive value (take default value from Device_Catalog %ds)" %
                (str(boot_timeout), self._boot_timeout))
            boot_timeout = self._boot_timeout
        else:
            # Value is good: Inform user on boot timeout value taken
            boot_timeout = int(boot_timeout)
            self.get_logger().info(
                "Boot timeout defined by the user: waiting %d seconds for the device ready signal..." %
                boot_timeout)

        return boot_timeout

    def _init_settledown_duration(self, settledown_duration):
        """
        Initialize settledown duration to a valid int and default value
        if not defined by user
        :param settledown_duration: Time to wait until start to count for timeout,
                                    Period during which the device must have started.
        :type settledown_duration: object
        :return: settledown_duration
        :rtype : int
        """
        if settledown_duration is None:
            settledown_duration = self._settledown_duration
        elif not str(settledown_duration).isdigit() or settledown_duration < 0:
            # Check if we use an integer and check if not a negative value
            self.get_logger(
            ).warning(
                "Settle down duration (%s) must be a positive value (take default value from Device_Catalog %ds)" %
                (str(settledown_duration), self._settledown_duration))
            settledown_duration = self._settledown_duration
        else:
            # Value is good: Inform user on boot timeout value taken
            settledown_duration = int(settledown_duration)

        return settledown_duration

    def switch_on(self, boot_timeout=None, settledown_duration=None, simple_switch_mode=False):
        """
        Switch ON the device
        This can be done either via the power supply or via IO card

        :type boot_timeout: int
        :param boot_timeout: Total time to wait for booting (in seconds)

        :type settledown_duration: int
        :param settledown_duration: Time to wait after boot timeout to have device ready to use (in seconds)

        :type simple_switch_mode: bool
        :param simple_switch_mode: a C{boolean} indicating whether we want to perform a simple switch on.

        :rtype: list
        :return: Output status and output log
        """
        return_code = Global.FAILURE
        if self._is_phone_booted:
            return_code = Global.SUCCESS
            return_message = "Device already switched on."
            self.get_logger().info(return_message)
            if not self.is_available():
                self.connect_board()
        else:
            return_message = ""
            self._acs_agent.is_started = False

            self.get_logger().info("Switching on the device...")

            # Handle entry parameter boot_timeout
            boot_timeout = self._init_boot_timeout(boot_timeout)
            # Handle entry parameter settledown_duration
            settledown_duration = self._init_settledown_duration(settledown_duration)

            if not simple_switch_mode:
                if not self._use_adb_over_ethernet:
                    # Reconnect usb cable to detect boot state
                    self._eqts_controller.connect_usb_host_to_dut()
                    time.sleep(5)

            device_state = self.get_state()
            if device_state != "alive":
                if not self._use_adb_over_ethernet:
                    # Unplug the Host PC USB in case it goes into charging mode or flash mode
                    self._eqts_controller.disconnect_usb_host_to_dut()
                    # If the COS was running, we need to wait for its shutdown
                    sleep_time = self.get_config("COSShutdownTimeout", 15, int)
                    time.sleep(sleep_time)

                if device_state == "offline":
                    self.get_logger().info("Device is in offline state")
                    self._eqts_controller.poweroff_device()

                self._eqts_controller.plug_device_power()
                self._eqts_controller.poweron_device()
                time.sleep(15)

                # Insert Host PC USB to enable connection with device
                if not self._use_adb_over_ethernet:
                    time.sleep(10)
                    self._eqts_controller.connect_usb_host_to_dut()

                # Wait for device to be ready
                (return_code, return_message) = self._wait_board_is_ready(boot_timeout=boot_timeout,
                                                                          settledown_duration=settledown_duration)

                if not simple_switch_mode:
                    # Boot failed - If the DUT is reachable (meaning in a defined Boot Mode :
                    # MOS, ROS, POS, COS), try a reboot
                    if return_code != Global.SUCCESS and self.get_boot_mode() != "UNKNOWN":
                        self.get_logger().warning("Device is currently in %s , try a reboot" % self.get_boot_mode())

                        if self.reboot(mode="MOS", wait_for_transition=True, transition_timeout=boot_timeout,
                                       skip_failure=True, wait_settledown_duration=True):
                            return_code = Global.SUCCESS

                if return_code == Global.SUCCESS:
                    # inject logs to track reboot done by acs
                    self.inject_device_log("i", "ACS", "device successfully switched on")
            else:
                # Device already booted
                self.get_logger().info("Device already booted")
                return_code = Global.SUCCESS

            if return_code == Global.SUCCESS:
                self._is_phone_booted = True
                self._is_device_connected = False
                self.connect_board()

        # TODO: return_message is quite never used by switch_on() procedure callers
        # Need to simplify this by only returning return_code = Global.SUCCESS / Global.FAILURE
        return return_code, return_message

    def _is_tcp_port_alive(self, hostname, port, timeout=1, retries=3):
        """
        Connect to hostname tcp port and return error status
        """
        tcp_socket = None
        attempt = 0
        max_retry = retries
        success = False
        error = ""

        self.get_logger().debug("Check device socket connection (IP: %s, Port: %d)..." % (hostname, port))

        while (attempt < max_retry) and not success:
            try:
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if tcp_socket is not None:
                    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    tcp_socket.settimeout(timeout)
                    tcp_socket.connect((hostname, port))
                    success = True

            except socket.error as socket_ex:
                error = str(socket_ex)

            finally:
                # increment the connection retry number
                attempt += 1

                if not success:
                    self.get_logger().debug(
                        "[IP SOCKET TO DUT] Connection error (IP: %s, Port: %s, Error: %s, try: %d)" % (
                            str(hostname), str(port), str(error), attempt))

                if tcp_socket is not None:

                    try:
                        # In all the cases : device socket connection success and failure
                        # Close and shutdown socket connection
                        tcp_socket.shutdown(socket.SHUT_RDWR)
                        tcp_socket.close()
                    except socket.error as socket_ex:
                        self.get_logger().debug("[IP SOCKET TO DUT] Disconnection error (error: %s)" % (str(socket_ex)))

                    # Wait before retry
                    time.sleep(timeout)

                tcp_socket = None

        if not success:
            self.get_logger().error(
                "[IP SOCKET TO DUT] Connection error (IP: %s, Port: %s, Error: %s)" % (
                    str(hostname), str(port), str(error)))

        return success

    def soft_shutdown(self, wait_for_board_off=False):
        """"
        Perform a soft shutdown and wait for the device is off

        :type wait_for_board_off: boolean
        :param wait_for_board_off: Wait for device is off or not after soft shutdown

        :rtype: boolean
        :return: If device is off or not
        """

        msg = "Soft shutting down the device..."
        self.get_logger().info(msg)
        self.inject_device_log("i", "ACS", msg)

        # Initiliaze variable
        device_off = False

        # if device is already OFF do not do soft shutdown procedure
        if self.is_available():
            # Stop extra threads before sending the softshutdown command
            # in case the softshutdown takes effect whereas extra threads are still active
            self._stop_extra_threads()

            # Call device soft shutdown
            if self.soft_shutdown_cmd():
                # Disconnect device before shutting down takes effect
                self.disconnect_board()

                # unplug cable after soft shutdown to avoid COS
                if not self._use_adb_over_ethernet:
                    self._eqts_controller.disconnect_usb_host_to_dut()

                # Wait for device is off
                if wait_for_board_off:
                    # Wait enough time for soft shutdown to have effect
                    self.get_logger().info("Wait soft shutdown duration (%ds)..." % self._soft_shutdown_duration)
                    time.sleep(self._soft_shutdown_duration)

                    if self._check_shutdown(self._use_adb_over_ethernet):
                        # Device is switched off
                        device_off = True
                else:
                    # By pass wait for device off.
                    # We consider that the device is switched off
                    device_off = True

            # Update device boot status according to soft shutdown result
            # Important when this function is called outside switch_off()
            if device_off:
                self._is_phone_booted = False

        return device_off

    def hard_shutdown(self, wait_for_board_off=False):
        """"
        Perform a hard shutdown and wait for the device is off

        :type wait_for_board_off: bool
        :param wait_for_board_off: Wait for device is off or not after soft shutdown

        :rtype: bool
        :return: If device is off or not
        """

        msg = "Hard shutting down the device..."
        self.get_logger().info(msg)

        self.inject_device_log("i", "ACS", msg)

        # Initialize variable
        device_off = False

        # Disconnect device before shutting down takes effect
        self.disconnect_board()

        # unplug cable after soft shutdown to avoid COS
        if not self._use_adb_over_ethernet:
            self._eqts_controller.disconnect_usb_host_to_dut()
            time.sleep(self._usb_sleep_duration)

        status = self._eqts_controller.poweroff_device()
        if status:
            self._eqts_controller.cut_device_power()

            # It should not be needed to wait after hard shutdown request to have effect
            # TO DO: most of the time this time sleep is not needed it shall be tuned in
            # Device_Catalog.xml for every device
            self.get_logger().info("Wait hard shutdown duration (%ds)..." % self._hard_shutdown_duration)
            time.sleep(self._hard_shutdown_duration)

            if wait_for_board_off:
                if self._check_shutdown(self._use_adb_over_ethernet):
                    # Device is switched off
                    device_off = True
            else:
                # By pass wait for device off.
                # We consider that the device is switched off
                device_off = True

            # Update device boot status according to hard shutdown result
            # Important when this function is called outside switch_off()
            if device_off:
                self._is_phone_booted = False
        else:
            self.get_logger().info("Unable to hard shutdown the device.")

        return device_off

    def _check_shutdown(self, use_adb_over_ethernet=False):
        """"
        Check if the shutdown is successfull (soft or hard)

        :rtype use_adb_over_ethernet: boolean
        :param use_adb_over_ethernet: ADB transport mode

        :rtype: boolean
        :return: If device is off or not
        """

        # Initialize variable
        device_off = False

        if not use_adb_over_ethernet:
            # Do not reconnect the USB => it could change the device state (pass in COS or other state)
            # Check device state over ADB
            if self.get_state() != "alive":
                device_off = True
        else:
            if not self._is_tcp_port_alive(self._ip_address, self._adb_port):
                # Device is switched off
                device_off = True

        return device_off

    def switch_off(self):
        """
        Switch OFF the device.

        :rtype: list
        :return: Output status and output log
        """
        self.get_logger().info("Switching off the device...")

        if self._is_phone_booted:
            if self._screenshot_enable:
                self.screenshot("HALT")

            # Initialize variables
            device_off = False
            return_code = Global.FAILURE
            return_msg = ""

            # Let's try to perform a soft shutdown in any case
            # if it fails then try a hard shutdown
            if self.soft_shutdown(True):
                device_off = True
            elif self.hard_shutdown(True):
                device_off = True
            else:
                return_msg = "Failed to shutdown the device (soft or hard) !"
                self.get_logger().error(return_msg)

            if device_off:
                return_code = Global.SUCCESS
                return_msg = "Device successfully switched off"
                self.get_logger().info(return_msg)
        else:
            return_code = Global.SUCCESS
            return_msg = "Device already switched off"
            self.get_logger().info(return_msg)

        return return_code, return_msg

    def _connect_adb(self, tcp_connect_retries_nb=None, adb_connect_retries_nb=None):
        """
        Connect ADB though USB or ETHERNET, ensure adb root connection if set
        :param tcp_connection_retry_nb: allow to override retry nb
        :param adb_connection_retry_nb:  allow to override retry nb
        :rtype: bool, str
        :return: status of ADB connection and status message
        """
        error_msg = "Unknown error while connecting ADB"
        adb_connected = False
        # ETHERNET
        if tcp_connect_retries_nb is not None:
            tcp_retries = tcp_connect_retries_nb
        else:
            tcp_retries = self._tcp_connect_retries_nb
        if adb_connect_retries_nb is not None:
            adb_retries = adb_connect_retries_nb
        else:
            adb_retries = self._adb_connect_retries_nb
        if self._use_adb_over_ethernet:
            if self._is_tcp_port_alive(self._ip_address, self._adb_port, retries=tcp_retries):
                if self._phone_handle.adb_ethernet_start(self._ip_address,
                                                         self._adb_port,
                                                         adb_retries,
                                                         self._adb_connect_timeout):
                    adb_connected = True
                    error_msg = ""
                else:
                    error_msg = "Connected to device over ethernet but unable to connect to adb"
            else:
                error_msg = "Unable to connect to device over ethernet"
        # USB
        else:
            # Wait for connection
            time.sleep(self._usb_sleep_duration)
            # FIXME: no check are done on the USB physical link and adb usb connection is ok
            adb_connected = True

        # ROOT
        if adb_connected and self._enableAdbRoot:
            if self.enable_adb_root():
                adb_connected = True
            else:
                adb_connected = False
                error_msg = "Device failed to enable adb root !"

        return adb_connected, error_msg

    def connect_board(self):
        """
        Connect the device.
        :rtype : bool
        :return: True if device is connected
        """
        error_msg = "Unknown error while connecting device"
        self._connection_lock.acquire()

        try:
            self.get_logger().info("Connecting to the device....")
            if not self._is_device_connected:

                # ADB CONNECTION
                # When connecting device, it may be booting so allow great number of retries
                self._is_device_connected, error_msg = self._connect_adb(tcp_connect_retries_nb=100)

                # DEVICE PREPARATION
                if self._is_device_connected:
                    self._start_extra_threads()
                    # Update time to bench time
                    status, error_msg = self.synchronyze_board_and_host_time()
                    if status == Global.SUCCESS:
                        # Retrieve/update device properties
                        DeviceManager().update_device_properties(self.whoami().get('device'))
                        self.get_logger().info("Device connected !")
                    else:
                        self.get_logger().error("Device failed to synchronize time with host: {0}".format(error_msg))
                else:
                    self.get_logger().error("Unable to connect adb: {0}".format(error_msg))
            else:
                self.get_logger().info("Device already connected !")

        except Exception as error:  # pylint: disable=W0703
            error_msg = str(error)
            self._is_device_connected = False
            self._stop_extra_threads()
        finally:
            if not self._is_device_connected:
                self.get_logger().debug("Error happen during device connection: %s" % error_msg)
            self._connection_lock.release()

        return self._is_device_connected

    def disconnect_board(self):
        """
        Disconnect the device.
        """
        self._connection_lock.acquire()
        try:
            self.get_logger().info("Disconnecting the device...")
            if self.is_available():
                # Stop extra threads
                self._stop_extra_threads()

                if self._use_adb_over_ethernet:
                    if self._do_adb_disconnect:
                        self._is_device_connected = not self._phone_handle.adb_ethernet_stop(self._ip_address,
                                                                                             self._adb_port,
                                                                                             self._adb_connect_timeout)
                    else:
                        self._is_device_connected = False
                else:
                    self._is_device_connected = False
                    # Sleep duration before USB unplug for Power, Sleep, EM
                    time.sleep(self._usb_sleep_duration)

                if not self._is_device_connected:
                    self.get_logger().info("Device disconnected !")
            else:
                self.get_logger().info("Device already disconnected !")

        except Exception as error:  # pylint: disable=W0703
            self.get_logger().debug("Error happen during device disconnection: %s" % str(error))
        finally:
            self._connection_lock.release()

    def enable_adb_root(self):
        """
        Switch adb to adb root
        :rtype: boolean
        :return: true if root is successfully set, false otherwise
        """
        self.get_logger().info("Adb root requested, enabling it ...")
        result, output = self.run_cmd("adb root", self._adb_root_cmd_timeout, force_execution=True)

        end_time = time.time() + self._adb_root_timeout
        while time.time() < end_time and output.find("already running as root") == -1:
            time.sleep(self._adb_root_timeout / 10.0)
            if self._use_adb_over_ethernet:
                # reconnect device, as "adb root" reset adb socket
                self._phone_handle.adb_ethernet_start(self._ip_address, self._adb_port,
                                                      self._adb_connect_retries_nb, self._adb_connect_timeout)
            result, output = self.run_cmd("adb root", self._adb_root_cmd_timeout, force_execution=True)

        return result == Global.SUCCESS and output.find("already running as root") != -1

    def synchronyze_board_and_host_time(self):
        """
        Synchronize the device time and the acs host time
        """
        # FIXME: UECMD will result in errors
        return Global.SUCCESS, ""

        # system_api = self.get_uecmd("System")

        # return_code, return_msg = system_api.set_timezone(DateUtil.timezone())
        # if return_code == Global.SUCCESS:
        #     # Set UTC time in case default timezone is not correct
        #     return_code, return_msg = system_api.set_date_and_time(DateUtil.utctime())
        #     if return_code == Global.SUCCESS:
        #         # Log device time for MPTA sync features
        #         # Please do not erase/change this log message
        #         # w/o informing MPTA dev guys
        #         self.get_logger().info("DeviceTime: %s" % return_msg)
        # return return_code, return_msg

    def format_cmd(self, cmd, silent_mode=False):
        """
        Insert serial number in adb command if needed (multi-device mode)
        :type  cmd: string
        :param cmd: cmd to be run
        :return: modified command
        :rtype: String
        """

        def __which_cmd(cmd_name):
            """
            Retrieve the command path
            :rtype: string
            :return: The full path of the command

            :raise: AcsConfigException in case the command is not found
            """
            if cmd_name in formatted_cmd:
                # Get the full path of the executable
                # which command does raise exception as, we do not necessary need it
                # but in our case, we want to notify the user that adb/fastboot is not set in PATH env
                cmd_full_path = CommandLine.which(cmd_name)
                if cmd_full_path is None:
                    error_msg = "Command %s not found ! Check that it is defined your PATH environment" % (cmd_name,)
                    raise AcsConfigException(AcsConfigException.EXTERNAL_LIBRARY_ERROR, error_msg)
                return cmd_full_path

        # Initialize the formatted command
        formatted_cmd = cmd.strip()

        # In case we launch 'adb' command
        if formatted_cmd.startswith(ADB_CMD_NAME):
            cmd_path = __which_cmd(ADB_CMD_NAME)
            if not formatted_cmd.startswith(ADB_CMD_NAME + " devices") and self._serial_number:
                formatted_cmd = formatted_cmd.replace(ADB_CMD_NAME + " ",
                                                      "{0} -s {1} ".format(ADB_CMD_NAME, self._serial_number), 1)

            # Replace 'adb' command with the full path using regex
            adb_compiled_pattern = re.compile(r'\b({0})\b[^\.\w]'.format(ADB_CMD_NAME), re.IGNORECASE)
            # Fix on Windows machine
            unix_like_cmd_path = ' {0} '.format(cmd_path.replace('\\', '/'))
            formatted_cmd = (re.sub(adb_compiled_pattern, unix_like_cmd_path, formatted_cmd, count=1)).strip()

        # In case we launch 'fastboot' command
        elif formatted_cmd.startswith(FASTBOOT_CMD_NAME):
            cmd_path = __which_cmd(FASTBOOT_CMD_NAME)
            if self._use_adb_over_ethernet:
                # if we use adb over ethernet
                formatted_cmd = formatted_cmd.replace(FASTBOOT_CMD_NAME + " ",
                                                      "{0} -t {1} ".format(FASTBOOT_CMD_NAME, self._pos_ip_adress), 1)
            else:
                if "devices" not in cmd:
                    if self._serial_number is not None and len(self._serial_number) > 0:
                        formatted_cmd = formatted_cmd.replace(FASTBOOT_CMD_NAME + " ",
                                                              "{0} -s {1} ".format(FASTBOOT_CMD_NAME,
                                                                                   self._serial_number), 1)

            # Replace 'fastboot' command with the full path
            formatted_cmd = " ".join([x.replace(FASTBOOT_CMD_NAME, cmd_path)
                                      if x.startswith(FASTBOOT_CMD_NAME) else x for x in formatted_cmd.split()])

        # In case Linux we format adb shell command using simple split
        # FIXME: As in some cases users launch complex unix commands shlex command is limited
        # This work around splits the command in 3 args : ['adb', 'shell', 'args1 args2 ...']
        shell_args = formatted_cmd.split()
        if "shell" in shell_args:
            # Get index of 'shell' key in the command
            idx = shell_args.index("shell") + 1
            cmd_args = shell_args[:idx]
            cmd_params = shell_args[idx:]

            if os.name in ['posix']:
                os_name = "linux"
            else:
                os_name = "windows"
                if cmd_params:
                    # if args start and end with double quotes : remove them
                    if cmd_params[0].startswith('"') and cmd_params[-1].endswith('"'):
                        cmd_params[0] = cmd_params[0][1:]
                        cmd_params[-1] = cmd_params[-1][0:-1]

            # concatenate adb shell args into one string
            cmd_args.append(" ".join(cmd_params))
            formatted_cmd = cmd_args
            if not silent_mode:
                self._logger.debug("Will be executed as {0} format: {1}".format(os_name, str(cmd_args)))

        return formatted_cmd

    def _run_adb_cmd(self, cmd, timeout, silent_mode=False, wait_for_response=True, cancel=None):
        """
        Execute the input adb command and return the result message
        If the timeout is reached, return an exception

        :type  cmd: string
        :param cmd: cmd to be run
        :type  timeout: integer
        :param timeout: Script execution timeout in sec
        :type  cancel: Cancel
        :param cancel: a Cancel object that can be used to stop execution, before completion or timeout(default None)

        :return: Execution status & output string
        :rtype: Integer & String
        """
        # Insert serial number in adb command if needed (multi-device mode)
        cmd = self.format_cmd(cmd, silent_mode)

        if wait_for_response:
            return_code, output = internal_shell_exec(cmd=cmd, timeout=timeout, silent_mode=silent_mode, cancel=cancel)
        else:
            # Async operation is going to be started, we cannot provide a return_code
            # Return SUCCESS by default
            return_code = Global.SUCCESS
            output = ""
            run_local_command(args=cmd, get_stdout=not silent_mode)

        return return_code, output

    def _run_fastboot_cmd(self, cmd, timeout, silent_mode=False, wait_for_response=True, cancel=None):
        """
        Execute the input fastboot command and return the result message
        If the timeout is reached, return an exception

        :type  cmd: str
        :param cmd: cmd to be run
        :type  timeout: int
        :param timeout: Script execution timeout in sec
        :type  cancel: Cancel
        :param cancel: a Cancel object that can be used to stop execution, before completion or timeout(default None)

        :returns: Execution status & output string
        :rtype: int & str
        """

        # Insert serial number in fastboot command if needed (multi-device mode)
        cmd = self.format_cmd(cmd, silent_mode)

        if wait_for_response:
            return_code, output = internal_shell_exec(cmd=cmd, timeout=timeout, silent_mode=silent_mode, cancel=cancel)
            if output.count("usage: fastboot [ <option> ] <command>") > 0:
                output = "Unknown fastboot command : %s" % cmd
        else:
            # Async operation is going to be started, we cannot provide a return_code
            # Return SUCCESS by default
            return_code = Global.SUCCESS
            output = ""
            run_local_command(args=cmd, get_stdout=not silent_mode)

        return return_code, output

    def screenshot(self, prefix="", filename=None):
        """
        Take a screenshot of the device

        :type prefix: str
        :type filename: str

        :param prefix: Prefix to use before device name
        :param filename: Filename to use

        :return: file path to the screenshot
        """
        return_value = None
        if filename is None:
            self._screenshot_count += 1
            filename = os.path.join(self.get_report_tree().get_subfolder_path(subfolder_name="SCREEN",
                                                                              device_name=self._device_name),
                                    str(prefix + "_" + self.get_phone_model()))
            filename += "_" + self._current_time + "_" + str(self._screenshot_count) + ".png"

        self.get_logger().info("Screenshot in %s", str(filename))
        cmd = "adb shell /system/bin/screencap -p /sdcard/screenshot.png"
        status, err_output = self.run_cmd(cmd=cmd, timeout=10, force_execution=True)

        err = re.search("^error ", err_output, re.I)
        if status == Global.SUCCESS and err is None:
            status, _ = self.pull(remotepath="/sdcard/screenshot.png", localpath=filename, timeout=5,
                                  force_execution=True)
            if status == Global.SUCCESS:
                return_value = filename
        return return_value

    def run_cmd(self, cmd, timeout,
                force_execution=False,
                wait_for_response=True,
                silent_mode=False,
                cancel=None):
        """
        Execute the input command and return the result message
        If the timeout is reached, return an exception

        :type  cmd: str
        :param cmd: cmd to be run
        :type  timeout: int
        :type force_execution: bool
        :param timeout: Script execution timeout in ms
        :param force_execution: Force execution of command
                    without check device connected (dangerous)
        :param wait_for_response: Wait response from adb before
                                        stating on command
        :type  cancel: Cancel
        :param cancel: a Cancel object that can be used to stop execution, before timeout or completion (default None).
                       Call cancel.cancel() from another thread to stop command execution immediately.
                       If cancel has defined a callback, it will be called on command thread just after command stopped.

        :return: Execution status & output string
        :rtype: int & str
        """
        result = Global.FAILURE
        msg = "Cannot run the cmd, device not connected!"

        is_adb_cmd = any([cmd.startswith("%s %s" % (ADB_CMD_NAME, x)) for x in ADB_SOCK_CMDS_LIST])

        if self.is_available() or force_execution:
            if cmd.startswith(FASTBOOT_CMD_NAME):
                # run direct shell cmd
                result, msg = self._run_fastboot_cmd(cmd, timeout, silent_mode=silent_mode,
                                                     wait_for_response=wait_for_response,
                                                     cancel=cancel)
            elif not self._use_adb_socket or is_adb_cmd:
                # Cmd not yet supported thru ADBSocket
                # Use std adb cmd (warning as it may leak)
                result, msg = self._run_adb_cmd(cmd, timeout, silent_mode=silent_mode,
                                                wait_for_response=wait_for_response,
                                                cancel=cancel)
            else:
                result, msg = self._phone_handle.run_cmd(cmd, timeout, wait_for_response, silent_mode=silent_mode)

        elif not silent_mode:
            self.get_logger().warning("Cannot run '%s', device not connected!" % (str(cmd),))

        msg = msg.rstrip("\r\n")

        if "- exec '/system/bin/sh' failed:" in msg:
            # Ugly patch
            # Sometime, system partition is not properly mounted and adb answer "succesfully" (!!)
            # a message like "- exec '/system/bin/sh' failed: No such file or directory (2) -"
            # Turn that answer to failure as we have an issue with adb)
            result = Global.FAILURE

        return result, msg

    def get_uecmd_timeout(self):
        """
        Return the UECmd timeout of the device

        :rtype: int
        :return: the UECmd timeout of the device
        """
        return self._uecmd_default_timeout

    def get_call_setup_timeout(self):
        """
        Return the call setup timeout of the device

        :rtype: int
        :return: The call setup timeout of the device
        """
        return self._call_setup_timeout

    def is_available(self):
        """
        Check if the device can be used.

        :return: availability status
        :rtype: Boolean
        """
        return self._is_device_connected

    def is_booted(self):
        """
        Check if the device has booted successfully.

        :return: boot status
        :rtype: Boolean
        """
        return self._is_phone_booted

    def is_rooted(self):
        """
        Check if the device has root rights

        :rtype: bool
        :return: True if device is rooted, False otherwise
        """
        return self._enableAdbRoot

    def has_intel_os(self):
        """
        Check if the device os is compiled by Intel.
        An os that is not 'Intel' is a reference os (compiled by a thirdparty).
        For example, on Android, this means that the os image is signed with Intel's key, and
        thus ACS will have extended permissions.

        :rtype: bool
        :return: True if os is compiled by Intel, False otherwise
        """
        return self._enableIntelImage

    def get_device_logger(self):
        """
        Return device logger

        :rtype: object
        :return: device logger instance.
        """
        return self._device_logger

    def get_ui_dictionary_name(self):
        """
        Return the name of the UI dictionary to use

        :rtype: str
        :return: The name of the UI dict to use.
        """
        return str(self._ui_dictionary_name)

    def _prepare_setup(self):
        """
        Prepare device for setup

        :rtype: str
        :return: The name of the UI dict to use.
        """

        result = False
        msg = "Undefined error in preparing device for setup"

        # Make the device available for setting up
        if not self.is_available():
            device_state = self.get_state()
            if device_state == "alive":
                self.connect_board()
                if not self.is_available():
                    msg = "Device is not ready to be setup after trying connection"
                else:
                    result = True
                    msg = ""
            else:
                msg = "Device is not ready to be setup, state is:%s" % device_state
        else:
            result = True
            msg = ""

        return result, msg

    def install_file(self, app):
        """
        Depreccated function push applications onto target from a given folder$

        :type file_path: str
        :param file_path: the app to install

        :rtype: list
        :return: Output status and output log
        """
        self._logger.error("Deprecated device ACS method 'install_file', Teststep INSTALL_APP should be used instead")
        return self.get_uecmd("AppMgmt").install_device_app(app)

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
        verdict = Global.FAILURE
        msg = "Cannot remove file on device folder {0}".format(device_directory)
        cmd = "adb shell find {0} -maxdepth 1 -type f -name '{1}'".format(device_directory, filename_regex)
        status, output = self.run_cmd(cmd,
                                      self._uecmd_default_timeout,
                                      wait_for_response=True,
                                      silent_mode=True)
        if "/system/bin/sh: find: not found" in output:
            cmd = "adb shell ls {0}/{1} | grep {1}".format(device_directory, filename_regex, filename_regex)
            status, output = self.run_cmd(cmd,
                                          self._uecmd_default_timeout,
                                          wait_for_response=True,
                                          silent_mode=True)
        if status != Global.SUCCESS or "No such file" in output:
            msg += " ({0})".format(output)
            verdict = Global.FAILURE
        elif output:
            cmd = "adb shell rm {0}".format(" ".join(output.split('\n')))
            verdict, msg = self.run_cmd(cmd,
                                        self._uecmd_default_timeout,
                                        wait_for_response=True)
            if verdict == Global.SUCCESS:
                msg = "Files : {0} have been successfully removed from device".format(" ".join(output.split('\n')))

        else:
            verdict = Global.SUCCESS
            msg = "Nothing to remove, no file matching {0} in {1}!".format(filename_regex, device_directory)
        return verdict, msg

    def inject_device_log(self, priority, tag, message):
        """
        Logs to device log

        :type priority: str
        :type tag: str
        :type message: str

        :param priority: Priority of log message, should be:
                         v: verbose
                         d: debug
                         i: info
                         w: warning
                         e: error
        .. seealso:: http://developer.android.com/guide/developing/tools/adb.html#logcat

        :param tag: Tag to be used to identify the log onto logcat
        :param message: Message to be written on log.

        :return: command status
        :rtype: bool
        """
        result = False

        if self.is_available():
            try:
                cmd = "adb shell log -p %s -t %s '%s'" % (priority, tag, message)
                output = self.run_cmd(cmd, self._uecmd_default_timeout,
                                      wait_for_response=True,
                                      silent_mode=True, force_execution=True)
                if output[0] == Global.SUCCESS:
                    result = True
            except AcsBaseException as e:
                self.get_logger().error("inject_device_log: error happen during execution: " + str(e))

        return result

    def close_connection(self):
        """
        kill all adb process
        """
        self._connection_lock.acquire()
        try:
            timer = self._phone_handle.count_adb_instances()
            if self._do_adb_disconnect:
                self._phone_handle.adb_stop()
            time.sleep(timer * 5)
        except Exception as error:  # pylint: disable=W0703
            self.get_logger().debug("error happen during adb stop: %s" % str(error))

        finally:
            self._connection_lock.release()

    def open_connection(self):
        """
        Start adb process and restart them
        """
        self._connection_lock.acquire()
        try:
            self._phone_handle.adb_start(self._adb_connect_timeout)
        except Exception as error:  # pylint: disable=W0703
            self.get_logger().debug("error happen during adb start: %s" % str(error))

        finally:
            self._connection_lock.release()

    def get_state(self, check_shell=True):
        """
        Get the device state from adb

        :type  check_shell: bool
        :param check_shell: test shell activity

        :rtype: str
        :return: device state : alive, unknown, offline
        """
        state = "unknown"

        self.get_logger().info("Getting device state...")

        if self._use_adb_over_ethernet:
            # We can't rely on adb host status ==> check IP connectivity
            # We have 2 TCP ports available: adb and dns
            # if adb_port is down and dns_port is up: device is offline (adb issue)
            # if adb_port is down and dns_port is down: unknown state (acs point of view)
            if self._is_tcp_port_alive(self._ip_address, self._adb_port):
                # IP connection is OK => test adb connection
                self.get_logger().debug("get_state: ip connection with device is OK")
                if self._phone_handle.adb_ethernet_start(self._ip_address, self._adb_port,
                                                         self._adb_connect_retries_nb, self._adb_connect_timeout):
                    self.get_logger().debug("get_state: adb connection with device is OK")
                    state = "alive"
                else:
                    self.get_logger().debug("get_state: adb connection with device is NOK")
                    state = "unknown"
            elif self._is_tcp_port_alive(self._ip_address, 53):
                state = "offline"
            else:
                state = "unknown"
        else:
            # adb_port is up over usb OR over tcp ip
            try:
                retry = 2
                try_index = 0
                # Implement a retry mechanism as on some benches as on first
                # run of adb (if shutdown previously), it always return unknown
                while try_index < retry and state != "alive":
                    try_index += 1
                    output = self.run_cmd("adb get-state", 10, True)
                    if output[0] != Global.FAILURE:
                        state = (output[1].strip()).lower()
                        if state.endswith("device"):
                            state = "alive"
                            if check_shell:
                                if self.run_cmd("adb shell echo", 10, True)[0] == Global.FAILURE:
                                    state = "unknown"
            except Exception as error:  # pylint: disable=W0703
                self.get_logger().debug("get_state: error happened: %s" % str(error))
                state = "unknown"

        self.get_logger().info("Device state is %s" % state)

        return state

    def _get_device_boot_mode(self):
        """
        get the boot mode from adb

        :rtype: string
        :return: device state : MOS or UNKNOWN
        """
        boot_mode = "UNKNOWN"
        value = self.get_property_value("sys.boot_completed")
        if value is not None and value == "1":
            self.get_logger().debug("Device booted in MOS")
            boot_mode = "MOS"
        return boot_mode

    def get_boot_mode(self):
        """
        get the boot mode from adb

        :rtype: string
        :return: device state : MOS or UNKNOWN
        """
        boot_mode = "UNKNOWN"
        try:
            retry = 2
            # Implement a retry mechanism as on some benches as on first
            # run of adb (if shutdown previously), it always return unknown
            while retry > 0:
                boot_mode = self._get_device_boot_mode()
                if boot_mode.lower() != "unknown":
                    break
                retry -= 1
                # Wait 1 second before retrying
                time.sleep(1)
            else:
                self.get_logger().debug("device boot mode is UNKNOWN")

        except Exception as error:  # pylint: disable=W0703
            self.get_logger().debug("get_boot_mode: error happened: %s" % str(error))

        return boot_mode

    def _check_pos_mode(self):
        """
            check if device is in POS

            :rtype: str
            :return: device state is POS or UNKNOWN
        """
        current_state = "UNKNOWN"
        output = self.run_cmd("fastboot devices", 10, True)
        if output[0] != Global.FAILURE:
            mode = (output[1].strip()).lower()
            if mode.endswith("fastboot"):
                current_state = "POS"
                serial = self._ip_address if self._use_adb_over_ethernet else self._serial_number
                if serial:
                    serial = serial.lower()
                    if serial not in mode:
                        current_state = "UNKNOWN"
        return current_state

    def get_sdcard_path(self):
        """
        Return the path to the external sdcard
        :rtype: str
        :return: sdcard path
        """
        return self._ext_sdcard_path

    def get_provisioning_method(self):
        """
        Return the provisioning method
        :rtype: str
        :return: provisioning method
        """
        return self._prov_method

    def get_provisioning_data_path(self):
        """
        Return the path to data file used by address provisioning
        :rtype: str
        :return: provisioning data path
        """
        return self._prov_data_path

    def get_boot_timeout(self):
        """
        Return the boot timeout set in catalog.

        :rtype: int
        :return: boot time needed in seconds.
        """
        return self._boot_timeout

    def pull(self, remotepath, localpath, timeout=0, silent_mode=False, force_execution=False):
        """
        Pull a file from remote path to local path

        :param silent_mode:
        :param force_execution:
        :type remotepath: string
        :param remotepath: the remote path , eg /acs/scripts/from.txt

        :type localpath: string

        :param localpath: the local path , eg /to.txt

        :type timeout: float or None
        :param timeout: Set a timeout in seconds on blocking read/write operations.
                        timeout=0.0 is equivalent to set the channel into a no blocking mode.
                        timeout=None is equivalent to set the channel into blocking mode.
        """
        if not silent_mode:
            self.get_logger().debug("pull file %s from %s" % (localpath, remotepath))
        cmd = 'adb pull "%s" "%s"' % (remotepath, localpath)
        (status, err_msg) = self.run_cmd(cmd=cmd, timeout=timeout, silent_mode=silent_mode,
                                         force_execution=force_execution)

        if status == Global.FAILURE:
            self.get_logger().error("PULL command fails: " + err_msg)
            raise DeviceException(DeviceException.ADB_ERROR, "PULL command fails: " + err_msg)
        return status, err_msg

    def push(self, localpath, remotepath, timeout=0):
        """
        Push a file from local path to remote path

        :type remotepath: string
        :param remotepath: the remote path , eg /acs/scripts/to.txt

        :type localpath: string
        :param localpath: the local path , eg /from.txt

        :type timeout: int
        :param timeout: Set a timeout in seconds.
                        if timeout=0 the timeout will be computed depending on file's size.
                        device config "minFileInstallTimeout" will be used if the file's is too small.
        """
        self.get_logger().info("push file %s to %s" % (localpath, remotepath))

        if not timeout:
            timeout = Util.compute_timeout_from_file_size(localpath, self._min_file_install_timeout)

        cmd = 'adb push "%s" "%s"' % (localpath, remotepath)
        (status, err_msg) = self.run_cmd(cmd, timeout)

        if status == Global.FAILURE:
            self.get_logger().error("PUSH command fails: %s" % err_msg)
            raise DeviceException(DeviceException.ADB_ERROR, "PUSH command fails: %s" % err_msg)
        return status, err_msg

    def set_filesystem_rw(self):
        """
        Set the file system in read/write mode.
        """
        self.get_logger().debug("set filesystem to read/write (/system partition)")
        tries = 0
        status = Global.FAILURE
        err_msg = "FAILURE"

        while tries < 3:
            status, err_msg = self.run_cmd("adb remount", 3, True)
            if status == Global.FAILURE:
                tries += 1
            else:
                break

        if status == Global.FAILURE:
            self.get_logger().error("set_filesystem_rw error: %s" % err_msg)
            raise DeviceException(
                DeviceException.FILE_SYSTEM_ERROR,
                "set_filesystem_rw error: %s" % err_msg)

    def get_property_value(self, key):
        """
        Returns property value by executing "adb shell getprop" command.

        .. attention:: This implementation should prior from one in PhoneSystem UeCmd,
        this last calls should be removed and replaced by this one

        :type key: str
        :param key: Key corresponding to the value you want to retrieve.

        :return: The associated value or None if the key hasn't been found.
        """

        # Try to call getprop, then update the DeviceManager
        property_value = None
        one_word = 1

        adb_cmd_str = "adb shell getprop %s" % key

        status, status_msg = self.run_cmd(adb_cmd_str, self._uecmd_default_timeout, True)

        # Check if status_msg contain only 1 word (ssn valid)
        for char in status_msg:
            if char in string.whitespace:
                one_word = 0
                break
        # ssn not valid, retry to call getprop
        if not one_word:
            status, status_msg = self.run_cmd(adb_cmd_str, self._uecmd_default_timeout, True)

        if status == Global.SUCCESS:
            if status_msg is not None:
                property_value = status_msg.rstrip("\r\n")
                DeviceManager().update_device_properties(self.whoami().get('device'), {key: property_value})
        else:
            self.get_logger().warning("Fail to retrieve " + str(key) + " key")

        return property_value

    def set_property_value(self, key, value):
        """
        Sets property value by executing "adb shell setprop" command.

        :type key: string
        :param key: Key corresponding to the value you want to retrieve.

        :type value: object
        :param value: the property value (will be converted to string).

        :raise DeviceException: if the property could not be changed
        """
        # Convert the value into a string
        value = str(value)
        adb_cmd_str = "adb shell setprop %s %s" % (key, value)
        self.run_cmd(adb_cmd_str, self._uecmd_default_timeout, True)

        # Check that the previous command had the expected effect
        new_value = self.get_property_value(key)
        if value != new_value:
            # Build an error message
            message = "Could not change property %s's values to %s" % (
                key,
                value)
            # Raise an exception
            raise DeviceException(
                DeviceException.OPERATION_FAILED,
                message)

    def _retrieve_sw_release(self, properties):
        """
        Retrieve the software version (from adb shell getprop)
        :type properties: dict
        :param properties: a dictionnary containing all system prop (gotten through getprop)
        :rtype: str
        :return: the sw release, or None if unable to retrieve it
        """
        sw_release = None
        key = "ro.build.description"

        if key in properties:
            sw_release = properties[key]

        if sw_release in (None, ""):
            self.get_logger().warning("Fail to retrieve sw version of the device")
            sw_release = None

        return sw_release

    def _retrieve_model_number(self, properties):
        """
        Retrieve the model number (from adb shell getprop)
        :type properties: dict
        :param properties: a dictionnary containing all system prop (gotten through getprop)
        :rtype: str
        :return: the model number, or None if unable to retrieve it
        """
        model_number = None
        key = "ro.product.name"

        if key in properties:
            model_number = properties[key]

        if model_number in (None, ""):
            self.get_logger().warning("Fail to retrieve model number of the device")
            model_number = None

        return model_number

    def _retrieve_device_id(self, properties):
        """
        Retrieve the unique ID of the device (from adb shell getprop)
        :type properties: dict
        :param properties: a dictionnary containing all system prop (gotten through getprop)
        :rtype: str
        :return: the device unique ID, or None if unable to retrieve it
        """
        device_id = None
        key = "ro.serialno"

        if key in properties:
            device_id = properties[key]

        if device_id in (None, ""):
            self.get_logger().warning("Fail to retrieve model number of the device")
            device_id = None

        return device_id

    def _retrieve_baseband_version(self, properties):
        """
        Retrieve the baseband version (from adb shell getprop)
        :type properties: dict
        :param properties: a dictionnary containing all system prop (gotten through getprop)
        :rtype: str
        :return: the baseband version, or None if unable to retrieve it
        """
        baseband_version = None
        key = "gsm.version.baseband"

        if key in properties:
            baseband_version = properties[key]

        if baseband_version in (None, ""):
            self.get_logger().warning("Fail to retrieve baseband version of the device")
            baseband_version = None

        return baseband_version

    def _retrieve_kernel_version(self):
        """
        Retrieve the kernel version

        :rtype: str
        :return: the kernel version, or AcsConstants.NOT_AVAILABLE if unable to retrieve it
        """
        adb_cmd_str = "adb shell cat /proc/version"
        status, status_msg = self.run_cmd(adb_cmd_str, self._uecmd_default_timeout, True)

        if status == Global.SUCCESS and status_msg:
            # Parsing /proc/version file that shall looks like
            # "Linux version 3.4.43-187987-gd9f6c31 (buildbot@buildbot) (gcc vers..."
            # We have to extract "3.4.43-187987-gd9f6c31"
            reg_result = re.findall(r"(\d+\.\d+\.\d+\S+)", status_msg)
            if reg_result:
                # Extract the version
                kernel_version = reg_result[0]
            else:
                # Don't know how to parse the version
                # Take the information as it is
                kernel_version = status_msg
        else:
            kernel_version = AcsConstants.NOT_AVAILABLE
            self.get_logger().warning("Impossible to retrieve Kernel Version")

        return kernel_version

    def _retrieve_imei(self, properties):
        """
        Retrieve the imei version (from adb shell getprop)

        .. attention:: For NexusS and reference device key is ril.imei
        for Mfld-Android it should be persist.radio.device.imei

        :type properties: dict
        :param properties: a dictionnary containing all system prop (gotten through getprop)
        :rtype: str
        :return: the imei, or None if unable to retrieve it
        """
        imei = None
        key_list = ("persist.radio.device.imei", "ril.IMEI", "ril.barcode")

        key_found = False
        for key in key_list:
            self.get_logger().debug("Checking " + key + " key ...")
            if key in properties:
                imei = properties[key]

            if imei not in (None, ""):
                self.get_logger().debug("Imei found in " + key + " key !")
                key_found = True
                break
            else:
                self.get_logger().debug("Imei not found, checking next key.")

        if not key_found:
            self.get_logger().debug("Impossible to retrieve Imei")
            imei = None

        return imei

    def _retrieve_fw_version(self, properties):  # @UnusedVariable
        """
        Retrieve the firmware version (from adb shell getprop)
        """
        return AcsConstants.NOT_AVAILABLE

    def get_apk_version(self, package_name):
        """
        Retrieve the version of an apk deployed on device
        :type package_name: str
        :param package_name: name of the package to get version from
        :rtype: str
        :return the version as a string, or None if package is not installed
        """
        timeout = self._uecmd_default_timeout
        apk_version = None

        if self.get_state() == "alive":
            cmd = "adb shell dumpsys package %s | grep versionName"
            expr_version = "versionName=(.*)"
            regex = re.compile(expr_version)

            # Get version
            status, output = self.run_cmd(cmd % package_name, timeout)
            if status == Global.SUCCESS and output not in (None, ""):
                matches_str = regex.search(output)
                if matches_str is not None:
                    apk_version = matches_str.group(1)
                    self.get_logger().debug("Version of %s is %s" % (package_name, apk_version))
                else:
                    self.get_logger().info("Unable to get apk version for %s" % package_name)
            else:
                self.get_logger().warning("Application not yet installed: cannot dump apk information for %s" %
                                          package_name)
        else:
            self.get_logger().warning(
                "Device is not connected or adb command issue - Unable to get apk version for %s" % package_name)

        return apk_version

    def get_sw_release(self):
        """
        Get the SW release of the device.

        :rtype: str
        :return: SW release
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.sw_release")
        return self.device_properties.sw_release

    def get_model_number(self):
        """
        Get the Model Number of the device.

        :rtype: str
        :return: Model Number
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.model_number")
        return self.device_properties.model_number

    def get_baseband_version(self):
        """
        Get the Baseband Version of the device.
        (Modem sw release)

        :rtype: str
        :return: Baseband Version
        """
        self.get_logger().warning("Deprecated method, you should use device property : device.baseband_version")
        return self.device_properties.baseband_version

    def get_kernel_version(self):
        """
        Get the Kernel Version of the device.
        (Linux kernel version)

        :rtype: str
        :return: Kernel Version
        """
        return self.device_properties.kernel_version

    def get_imei(self):
        """
        Get the IMEI of the device.
        (International Mobile Equipment Identity)

        :rtype: str
        :return: Imei number
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.imei")
        return self.device_properties.imei

    def get_fw_version(self):
        """
        Get the Firware Version of the device.
        (International Mobile Equipment Identity)

        :rtype: str
        :return: Firmware version
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.fw_version")
        return self.device_properties.fw_version

    def get_acs_agent(self):
        """
        Get the ACS Agent Version of the device.

        :rtype: AcsAgentLegacy
        :return: ACS Agent or None if no agent
        """
        return self._acs_agent

    def retrieve_serial_number(self):
        """
        Retrieve the serial number of the device, returning the value read in
        phone catalog or bench_config files (depending of single or multi
        phones campaign), or in last resort with the "adb get-serialno" command.

        .. attention:: If the parameter is empty, we retrieve it from
        'adb get-serialno' command, assuming that only one device is connected.
        If more than one device or emulator is present, this
        method returns the first serial number.

        :rtype: str
        :return: serial number of the device, or None if unknown
        """
        serial_number = None

        if self._serial_number not in (None, "None", ""):
            # Retrieve current value of serial number
            serial_number = self._serial_number
        else:
            # Try to retrieve serial number from 'adb devices' command
            status, status_msg = self.run_cmd("adb get-serialno", self._uecmd_default_timeout,
                                              force_execution=True, silent_mode=True)

            if status == Global.SUCCESS:
                # retrieve the first serial number
                expr = "(?P<serial>[0-9A-Za-z\-]*).*"
                result = re.match(expr, status_msg)
                # if the result of math method isn't None,
                # it means that we find a serial number
                if result is not None:
                    serial_number = result.group("serial")
                    if serial_number == "unknown":
                        serial_number = None
                else:
                    serial_number = None
            else:
                self.get_logger().warning("Fail to retrieve serial number of the device")
                serial_number = None

            # Store the serial number in globals
            self._serial_number = serial_number

        return serial_number

    def retrieve_device_id(self):
        """
        Retrieve the unique id of the device, returning the serial number
        read in phone catalog or bench_config files
        (depending of single or multi phones campaign),
        or in last resort with "adb shell getprop ro.serialno".

        .. attention:: If the device is connected over ethernet,
            value in phone catalog and bench_config will be ignored.
        .. attention:: If the parameter is empty,
            we retrieve it from 'adb shell getprop ro.serialno' command,
            assuming that only one device is connected.

        If more than one device or emulator is present,
        this method returns the first device id.

        :rtype: str
        :return: unique id of the device, or None if unknown
        """

        if self.device_properties.device_id not in (None, "None", ""):
            # Retrieve current value of device_id
            device_id = self.device_properties.device_id
        else:
            # Try to retrieve device id from props
            device_id = self._retrieve_device_id()

            # Store the device id
            self.device_properties.device_id = device_id

        return device_id

    def reboot(self, mode="MOS", wait_for_transition=True,
               transition_timeout=None, skip_failure=False,
               wait_settledown_duration=False):
        """
        Perform a SOFTWARE reboot on the device.
        By default will bring you to MOS and connect acs once MOS is seen.
        this reboot require that you are in a state where adb or fastboot command can be run.

        :type mode: str or list
        :param mode: mode to reboot in, support MOS, COS, POS, ROS. It can be a list of these modes
               (ie ("COS","MOS"))
               .. warning:: it is not always possible to reboot in a mode from another mode
                eg: not possible to switch from ROS to COS

        :type wait_for_transition: bool
        :param wait_for_transition: if set to true,
                                    it will wait until the wanted mode is reached

        :type transition_timeout: int
        :param transition_timeout: timeout for reaching the wanted mode
                                    by default will be equal to boot timeout set on
                                    device catalog

        :type skip_failure: bool
        :param skip_failure: skip the failure, avoiding raising exception, using
                                this option block the returned value when it is equal to False

        :type wait_settledown_duration: bool
        :param wait_settledown_duration: if set to True, it will wait settleDownDuration seconds
                                          after reboot for Main OS only.

        :rtype: bool
        :return: return True if reboot action succeed depending of the option used, False otherwise
                 - if wait_for_transition not used, it will return True if the reboot action has been seen
                   by the device
                 - if wait_for_transition used , it will return True if the reboot action has been seen
                   by the device and the wanted reboot mode reached.
        """
        rebooted = False
        if not isinstance(mode, (list, tuple, set, frozenset)):
            mode = [mode]

        for os_mode in mode:
            msg = "Undefined error while rebooting"
            output = Global.FAILURE
            transition_timeout = self._init_boot_timeout(transition_timeout)
            transition_timeout_next = 0
            rebooted = False
            os_mode = os_mode.upper()

            # Wait for device to be ready
            if wait_settledown_duration:
                settledown_duration = self._settledown_duration
            else:
                settledown_duration = None

            # List here command and combo list
            reboot_dict = {"MOS": "adb reboot",
                           "POS": "adb reboot bootloader",
                           "ROS": "adb reboot recovery",
                           "COS": self._soft_shutdown_cmd}

            # exist if mode is unknown
            if os_mode not in reboot_dict:
                msg = "unsupported boot mode %s" % str(os_mode)
                self.get_logger().error(msg)
                raise DeviceException(DeviceException.OPERATION_FAILED, msg)

            self.get_logger().info("Trying to reboot device in %s mode" % str(os_mode))
            # get actual boot mode
            actual_state = self.get_boot_mode()
            # boot the device
            if actual_state != "UNKNOWN":
                cmd = reboot_dict[os_mode]
                # inject adb logs
                if actual_state in ["ROS", "MOS", "COS"]:
                    self.inject_device_log("i", "ACS", "Trying to reboot device in %s" % os_mode)

                # disconnect acs only if we was in MOS
                if actual_state == "MOS":
                    # Stop extra threads before sending the reboot command
                    # in case the device reboots whereas extra threads are still active
                    self._stop_extra_threads()

                # overide cmd in case we are in POS
                elif actual_state == "POS" and os_mode == "MOS":
                    cmd = "fastboot reboot"
                # override cmd in case we are in POS and we want to reboot in POS
                elif actual_state == "POS" and os_mode == "POS":
                    cmd = "fastboot reboot-bootloader"

                # Send the reboot cmd
                start_time = time.time()
                output = self.run_cmd(cmd, transition_timeout, force_execution=True,
                                      wait_for_response=self._wait_reboot_cmd_returns)

                if not self._wait_reboot_cmd_returns:
                    self.get_logger().info("Wait soft shutdown settle down duration (%ds)..."
                                           % self._soft_shutdown_settle_down_duration)
                    time.sleep(self._soft_shutdown_settle_down_duration)

                transition_timeout_next = transition_timeout - (time.time() - start_time)

                # Disconnect the board in
                if actual_state == "MOS":
                    # Need to send the reboot cmd before disconnecting in case adb over ethernet
                    self.disconnect_board()

                # Consider after reboot that we shall restart the acs agent
                self._acs_agent.is_started = False

                # check reboot result
                if self._wait_reboot_cmd_returns and output[0] == Global.FAILURE:
                    msg = "error happen during reboot command or no reboot command reply received from the device"
                    # Update actual device state
                    actual_state = self.get_boot_mode()
                else:
                    # waiting for transition
                    if wait_for_transition and transition_timeout_next > 0:
                        # Check that we boot in right mode
                        # Handle MOS state
                        if os_mode == "MOS":
                            return_code, _ = self._wait_board_is_ready(boot_timeout=transition_timeout_next,
                                                                       settledown_duration=settledown_duration)

                            if return_code == Global.SUCCESS:
                                actual_state = "MOS"
                                rebooted = True
                            else:
                                actual_state = self.get_boot_mode()
                        else:  # POS, ROS, COS
                            # some time is always available to finalize boot procedure
                            start_time = time.time()
                            while ((time.time() - start_time) < transition_timeout_next) and not rebooted:
                                actual_state = self.get_boot_mode()
                                if os_mode == actual_state:
                                    self._logger.info("Device has been seen booted in %s after %s seconds" %
                                                      (os_mode, str((time.time() - start_time))))
                                    rebooted = True
                        if rebooted:
                            # inject adb logs
                            self.inject_device_log("i", "ACS", "Device successfully booted in %s" % os_mode)
                        else:
                            # Device fail to reach the wanted mode
                            msg = "Device fail to boot in %s before %d second(s) (current mode = %s)" \
                                  % (os_mode, transition_timeout, actual_state)
                    else:
                        # We do not wait for end of reboot command or time to reboot is already completed
                        # Get the actual state
                        actual_state = self.get_boot_mode()

                        # We do not check the final state but reboot command has succeed
                        rebooted = True

                        msg = "Device reboot command sent (mode requested = %s), " \
                              "we do not wait the end of reboot procedure (current mode = %s)" % (os_mode, actual_state)
                        self.get_logger().warning(msg)

                # Post processing after boot procedure successful or failure
                if actual_state == "MOS":

                    # Ensuring that in all cases, the self._is_phone_booted reflect the reality.
                    # As if we got until here, it means that, we're in MOS,
                    # therefore the self._is_phone_booted must be set to True
                    self._is_phone_booted = True

                    # connect device if mode is MOS
                    if self.connect_board():
                        # If the Agent was previously installed, start it
                        self.init_acs_agent()
                    else:
                        rebooted = False
                        msg = "Device is booted in MOS, but error occurred during device connection."

                elif actual_state in ["ROS", "COS"]:
                    # Try to enable adb root
                    if self._enableAdbRoot:
                        if not self.enable_adb_root():
                            # Only warning message as we are not in MOS
                            self.get_logger().warning(
                                "Device failed to enable adb root, after rebooting in %s" % os_mode)
            else:
                # exist if device state is seen as UNKNOWN
                msg = "Device is in mode %s, cant launch reboot" % actual_state

            if not rebooted:
                self.get_logger().error(msg)
                if not skip_failure:
                    raise DeviceException(DeviceException.OPERATION_FAILED, msg)
                break

        return rebooted

    def get_soft_shutdown_settle_down_duration(self):
        """
        return the value of soft shutdown settle down duration from catalog
        """
        return self._soft_shutdown_settle_down_duration

    def get_application_logs(self, destination, tag=None):
        """
        retrieve application logs from the device.

        :type destination: string
        :param destination: destination folder to be finished by an /

        :type tag: string
        :param tag: if tag is not None then it will retrieve all applog since more recent occurence of tag

        :rtype: list of string
        :return: return the list of pulled file
        """
        # get aplog folder
        potential_folder = ["/logs", "/data/logs"]
        aplog_folder = None
        aplog_num = 0
        files = []
        for folder in potential_folder:
            opt = self.run_cmd("adb shell ls %s/aplog?(.)*([0-9])" % folder,
                               self._uecmd_default_timeout, force_execution=True)
            txt = opt[1].lower()

            # ``in`` operator is much faster/readable than ``find``
            if ("aplog" in txt) and not ("not found" in txt) and not ("no such file" in txt):
                aplog_folder = folder
                break

        if aplog_folder is None:
            msg = "Failed to find aplogs folder"
            self.get_logger().error(msg)
            raise DeviceException(DeviceException.OPERATION_FAILED, msg)

        # case when we parse by tag
        if tag is not None:
            # cast in str to avoid unicode and replace backslash
            tag = str(tag)
            formated_tag = tag.replace("\\", "\\\\")
            # use simple quote to take the litteral slash
            output = self.run_cmd("adb shell grep -l '%s' %s/aplog?(.)*([0-9])" % (formated_tag, aplog_folder),
                                  self._uecmd_default_timeout, force_execution=True)
            # leave function if there is an error during adb cmd execution
            if output[0] == Global.FAILURE:
                self.get_logger().error("error happen during aplog retrievement")
                return

            # compute result to find the recent occurence where tag has been found
            output = output[1].splitlines()
            if len(output) > 0 and output[0] != "":
                # take the recent one
                file_name = output[0].split(".")
                if aplog_folder in file_name[0] and "is a directory" not in file_name[0].lower():
                    if len(file_name) == 1:
                        aplog_num = 1
                    elif len(file_name) > 1:
                        aplog_num = int(file_name[1].strip()) + 1
                else:
                    self.get_logger().error("tag '%s' not found in aplog" % tag)
                    return files

        # if tag option is not used, retrieve all aplogs
        elif tag is None:
            # list all aplog generated
            output = self.run_cmd("adb shell ls %s/aplog?(.)*([0-9])" % aplog_folder,
                                  self._uecmd_default_timeout, force_execution=True)
            # leave function if there is an error during adb cmd execution
            if output[0] == Global.FAILURE:
                self.get_logger().error("error happen during aplog retrievement")
                return files

            # parse result to find the highest iteration of aplog
            output = output[1].splitlines()
            for element in output:
                tmp_aplog_num = 0

                file_name = element.split(".")
                potential_nb = file_name[-1].strip()

                if len(file_name) == 1:
                    tmp_aplog_num = 1
                elif potential_nb.isdigit():
                    tmp_aplog_num = int(potential_nb) + 1

                if aplog_num < tmp_aplog_num:
                    aplog_num = tmp_aplog_num

        if aplog_num != 0:
            # pull the aplogs
            for element in range(aplog_num):
                try:
                    if element == 0:
                        file_name = "aplog"
                    else:
                        file_name = "aplog." + str(element)

                    # you need to ensure that the destination exists, otherwise the pull will fail
                    aplog_dest_path = os.path.join(destination, file_name)
                    origin = "/".join([aplog_folder.rstrip("/"), file_name])
                    self.pull(origin, aplog_dest_path, 120, force_execution=True)
                    files.append(aplog_dest_path)
                except DeviceException as e:
                    self.get_logger().error("error happened during aplog pull: " + str(e))

            if tag is not None and len(files) > 0:
                # take the oldest aplog since test running
                # do not use r+ option to avoid infinite loop
                lines = []
                with open(files[-1], "r") as aplog_file:
                    lines = aplog_file.readlines()
                text = ""
                # find the most recent line with tag
                for aplog_line in reversed(lines):
                    if tag in aplog_line:
                        # if tag found get is index and save it
                        last_tag_index = lines.index(aplog_line)
                        for line_no in range(last_tag_index, len(lines)):
                            # start to write in ouput from tag index
                            if lines.index(aplog_line):
                                text += lines[line_no]

                        # store text
                        if text != "":
                            with open(files[-1], "w") as f:
                                f.write(text)

                        break
        else:
            self.get_logger().error("failed to pull aplog, no logs found")

        return files

    def get_time_before_wifi_sleep(self):
        """
        Get the time to wait for Wifi networks to be disconnected.

        :rtype: int
        :return: time in seconds to wait for Wifi disconnection
        """
        return self._time_before_wifi_sleep

    def get_default_wall_charger(self):
        """
        Get the default wall charger name for this device.
        Usefull to connect the right charger for a device.

        :rtype: str
        :return: wall charger name ( DCP, AC_CHGR) , must match with IO CARD charger name
        """
        return self._default_wall_charger

    def get_application_instance(self, app_name):
        """
        Get instance of application to be managed on this device

        :type app_name: String
        :param app_name: Name of the application.

        :rtype: Application
        :return: application instance
        """

        import acs_test_scripts.Device.Model.AndroidDevice.Application as Application

        module_fullpath = os.path.join(os.path.dirname(Application.__file__),
                                       app_name)
        app = None
        if os.path.isfile(module_fullpath + ".py"):
            app = imp.load_source(app_name, module_fullpath + ".py")
        elif os.path.isfile(module_fullpath + ".pyc"):
            app = imp.load_compiled(app_name, module_fullpath + ".pyc")

        if app:
            app = getattr(app, app_name)(self)
        else:
            raise DeviceException("%s %s" % (DeviceException.INSTANTIATION_ERROR,
                                             app_name))

        return app

    def get_target_sim(self):
        """
        Get the current target sim of the device.

        .. note:: This parameter is useless for non-dual sim device,
                when this parameter is still equal to 1

        :rtype: int
        :return: The current target sim value
        """
        return self._target_sim

    def set_target_sim(self, target_sim):
        """
        Set the current target sim of the device.

        .. attention:: This parameter should not be used on non-dual sim device,
                when this parameter is still equal to 1

        :type target_sim: int
        :param target_sim: The new target sim value.

        :rtype: Application
        :return: application instance
        """
        self._target_sim = target_sim

    def send_at_command(self, at_command, timeout=5, com_port=None):
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

        result = Global.FAILURE

        # Use the default comport define in Device_Catalog.xml
        if self.__at_com_port is None and com_port is None:
            raise AcsConfigException(AcsConfigException.FEATURE_NOT_AVAILABLE,
                                     "Sending AT command feature is not available for this device type")
        elif com_port is not None:
            local_com_port = com_port
        else:
            local_com_port = self.__at_com_port

        read_return_value_command = "adb shell cat %s" % local_com_port
        send_command = "adb shell \"echo -e -r '%s\n' > %s\"" % (at_command, local_com_port)
        response_finish_tag = False
        response = ""
        retry_times = 3

        # We retry 2 times if no response is received
        while not response_finish_tag and retry_times > 0:
            # The thread to get the at_command output
            (process, read_return_value) = run_local_command(read_return_value_command)
            # As we can't control threading priority, we have to
            # sleep main thread 2 seconds, let read_return_value_command start first
            time.sleep(2)
            self.run_cmd(send_command, 2)
            end_timer = time.time() + timeout
            while not response_finish_tag and time.time() <= end_timer:
                while not read_return_value.empty():
                    return_value = read_return_value.get()
                    if return_value not in ["", "\r\n"]:
                        response = response + return_value
                        # Once we recevie OK or ERROR, end of repsonse
                        if "OK" in return_value:
                            response_finish_tag = True
                            result = Global.SUCCESS
                            break
                        elif "ERROR" in return_value:
                            response_finish_tag = True
                            break

            # If process is still alive, kill it to free com port
            if process.poll() is None:
                process.terminate()
            retry_times -= 1

        if not response_finish_tag:
            raise DeviceException(DeviceException.OPERATION_FAILED,
                                  "Can't get the response from Modem for AT command :%s" % str(at_command))

        return result, response

    def get_em_parameters(self):
        """
        return energy management paramater declared on device_catalog for your current device.
        there are on the <EM> </EM>
        only paramter that are used on usecase will be return like threshold or supported feature.
        :rtype : dict
        :return: return a dictionnary where key are the parameter name and value the parameter value
                 an empty field will be set to a default value
        """
        em_phone_param = {}
        em_phone_param["BATTERY"] = {}
        em_phone_param["BATTERY"]["THERMAL_CHARGING_HIGH_LIMIT"] = self.get_config(
            "battThermalChargingHighLim", 45, int)
        em_phone_param["BATTERY"]["THERMAL_CHARGING_LOW_LIMIT"] = self.get_config("battThermalChargingLowLim", 0, int)
        em_phone_param["BATTERY"]["VBATT_MOS_SHUTDOWN"] = self.get_config("minVbattMosShutdown", 3.4, float)
        em_phone_param["BATTERY"]["VBATT_MOS_BOOT"] = self.get_config("minVbattMosBoot", 3.6, float)
        em_phone_param["BATTERY"]["VBATT_COS_BOOT"] = self.get_config("minVbattCosBoot", 3.2, float)
        em_phone_param["BATTERY"]["VBATT_FLASH"] = self.get_config("minVbattFlash", 3.6, float)
        em_phone_param["BATTERY"]["VBATT_FULL"] = self.get_config("vbattFull", 4.3, float)
        em_phone_param["BATTERY"]["VBATT_OVERVOLTAGE"] = self.get_config("minVbattOverVoltage", 4.5, float)
        em_phone_param["BATTERY"]["BATTID_TYPE"] = self.get_config("BattIdType", "ANALOG", str)
        em_phone_param["BATTERY"]["BATT_ID_VALUE"] = self.get_config("BattIdValue", 120000, int)
        em_phone_param["BATTERY"]["BPTHERM_VALUE"] = self.get_config("BpThermValue", 35000, int)

        em_phone_param["GENERAL"] = {}
        em_phone_param["GENERAL"]["DATA_WHILE_CHARGING"] = self.get_config("dataWhileCharging", False, "str_to_bool")
        em_phone_param["GENERAL"]["ADB_AVAILABLE_MODE"] = self.get_config("adbAvailableMode", "MOS", str)
        em_phone_param["GENERAL"]["DISCHARGE_TYPE"] = self.get_config("dischargeType", "hard", str)

        em_phone_param["GENERAL"]["PRESS_HARD_SHUTDOWN"] = self.get_config("pressPowerBtnHardShutdown", 10, float)
        em_phone_param["GENERAL"]["PRESS_SOFT_SHUTDOWN"] = self.get_config("pressPowerBtnSoftShutdown", 6, float)
        em_phone_param["GENERAL"]["PRESS_BOOT"] = self.get_config("pressPowerBtnBoot", 3, float)
        em_phone_param["GENERAL"]["GENERATED_FILE_PATH"] = self.get_config("generatedFilePath", "/sdcard*/")

        # convert fastboot combo
        fastboot_combo = self.get_config("fastbootKeyCombo", [], str)
        if isinstance(fastboot_combo, str):
            fastboot_combo = fastboot_combo.replace(" ", "").split(";")
            # remove empty element in the list
            result = []
            for element in fastboot_combo:
                if element != "":
                    result.append(element)
            fastboot_combo = result
        em_phone_param["GENERAL"]["FASTBOOT_COMBO"] = fastboot_combo

        return em_phone_param

    def get_default_pin_code(self):
        """
        Returns the default PIN code to be used for handling SIM card,
        or None if parameter is not set.

        A None value means that you should not use UECmds related to SIM
         handling, in order to prevent SIM lock (PUK required)

        :rtype: str
        :return: SIM PIN code
        """
        return self.__default_pin_code

    def get_sim_puk_code(self):
        """
        Returns the SIM PUK code to be used for unlocking SIM card that has
        been PIN locked, or the value None.

        A None value means there is a configuration problem : you should not
        use SIM card in order to prevent the DUT to be SIM locked.

        :rtype: str
        :return: SIM PUK code
        """
        return self.__sim_puk_code

    def get_device_controller(self):
        """
        Returns the device controller object of the device model
        :rtype: DeviceController object
        :return: device controller
        """

        return self._eqts_controller

    def start_device_log(self, log_path):
        self._device_log_file = LogCatLogger(self, True)
        if self._device_log_file is not None:
            self._device_log_file.set_output_file(log_path)
            self._device_log_file.start()

    def stop_device_log(self):
        if self._device_log_file:
            self._device_log_file.stop()

    def grant_runtime_permissions(self, package_name):
        """
        Grant all declared permissons of an app to avoid popups displayed to user.

        :param package_name: the package name
        :type package_name: str

        :return: Execution status
        :rtype: Integer
        """
        _, output = self.run_cmd("adb shell dumpsys package %s" % package_name, 5, silent_mode=True)

        # extract everything in the section "requested permissions" of the dumpsys and grant them all
        is_requested = False
        for line in output.splitlines():
            if "requested permissions" in line.lower():
                is_requested = True
            elif "install permissions" in line.lower():  # if contains "install permissions", we must exit
                is_requested = False
            elif line.strip():
                if is_requested:
                    msg = "grant permission %s to package %s" % (line.strip(), package_name)
                    self.get_logger().info(msg)
                    cmd = "adb shell pm grant %s %s" % (package_name, line.strip())
                    self.run_cmd(cmd, 5, silent_mode=True)
