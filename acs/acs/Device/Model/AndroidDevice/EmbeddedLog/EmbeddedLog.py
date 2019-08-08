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

import os
import re
import shutil
from threading import Timer
import time

from datetime import datetime
from acs_test_scripts.Device.UECmd.UECmdTypes import BPLOG_LOC
from acs.ErrorHandling.DeviceException import DeviceException
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.UtilitiesFWK.Utilities import Global, str_to_bool

try:
    _SysErrors = WindowsError, OSError, IOError
except NameError:
    _SysErrors = OSError, IOError

# Pattern :     checksum  aplogsize aplogname
APLOG_PATTERN_DEVICE = "(\d+) (\d+) .*aplog\.(\d+)$"
# Pattern :     aploggroup.aplogname.checksum
APLOG_PATTERN_HOST = "(\d+)\.aplog\.(\d+)\.(\d+)$"

# The list of folder to create in the campaign report tree
LOG_SUBFOLDERS = ["AP_LOGS", "MODEM_LOGS", "PTI", "SERIAL"]

# List of keys to get access to Serial Configurations
ENABLE = "ENABLE_"
PORT = "PORT_"
PORT_NAME = "PORT_MANE_"
BAUDRATE = "BAUDRATE_"
HWCTRLFLOW = "HWCTRLFLOW_"
SERIAL_LOGGER = "SERIAL_LOGGER_"
SERIAL_LOG_FILE = "SERIAL_LOG_FILE_"
TMP_FOLDER = "tmp"


class EmbeddedLog(object):

    """
        EmbeddedLog implementation
    """

    def __init__(self, device):
        """
        Constructor

        :type  device: object
        :param device: instance of the device
        """

        self._dut_instance = device
        self._current_time = datetime.now().strftime("%Y-%m-%d_%Hh%M.%S")

        # Device general parameters
        self._wait_btwn_cmd = self._dut_instance.get_config("waitBetweenCmd", 5, float)
        self._uecmd_default_timeout = self._dut_instance.get_config("defaultTimeout", 50, int)

        # This option will force to retrieve all embedded logs, to be sure to have crash logs, ap logs ...
        # on critical failures
        retrieve_device_log_on_critical = self._dut_instance.get_config(
            "retrieveDeviceLogOnCriticalFailure", "False", "str_to_bool")

        # Application log parameters
        self._application_log_enable = self._dut_instance.get_config(
            "retrieveApplicationLog", "True", "str_to_bool") or retrieve_device_log_on_critical

        device_name = self._dut_instance.whoami().get("device", "")
        if not device_name:
            error_msg = "Device name cannot be found from device instance!"
            raise AcsConfigException(AcsConfigException.INSTANTIATION_ERROR, error_msg)
        report_tree = self._dut_instance.get_report_tree()
        # Create everything application logging requires only if required
        if self._application_log_enable:
            self._clean_application_logs = self._dut_instance.get_config(
                "cleanApplicationLog", "True", "str_to_bool") or retrieve_device_log_on_critical
            self._application_log_options = self._dut_instance.get_config(
                "applicationLogOptions",
                "pull_timer:60,aplog_pull_timeout:60,log_location:/logs",
                "str_to_dict")
            self._application_log_folder = report_tree.get_subfolder_path(
                subfolder_name=LOG_SUBFOLDERS[0], device_name=device_name)
            self._aplog_reg_device = re.compile(APLOG_PATTERN_DEVICE)
            self._aplog_reg_host = re.compile(APLOG_PATTERN_HOST)
            self._aplog_group_id = 1
            self.__aplog_timer = None
            self.__is_application_logger_started = False

        # Modem log parameters
        self._modem_log_enable = self._dut_instance.get_config("retrieveModemTrace", "False", "str_to_bool")

        # Create everything modem logging requires only if required
        if self._modem_log_enable:
            self._clean_modem_logs = self._dut_instance.get_config("cleanModemTrace", "False", "str_to_bool")
            self._modem_trace_options = self._dut_instance.get_config(
                "modemTraceOptions",
                "hsi_speed:h,trace_level:2,trace_location:emmc,file_size_option:1,pull_timeout:60",
                "str_to_dict")
            self._modem_log_folder = report_tree.get_subfolder_path(subfolder_name=LOG_SUBFOLDERS[1],
                                                                    device_name=device_name)
            self._modem_api = self._dut_instance.get_uecmd("Modem")
            self.__is_modem_logger_started = False

        # PTI log parameters
        self._pti_log_enable = self._dut_instance.get_config("retrievePTITrace", "False", "str_to_bool")

        # Create everything PTI logging requires only if required
        if self._pti_log_enable:
            self._pti_probe = self._dut_instance.get_config("PTIProbe", "FIDO")
            self._pti_cmdline = self._dut_instance.get_config(
                "enableAplogptiCmdLine", "adb shell setprop persist.service.aplogpti.enable 1")
            self._pti_log_folder = report_tree.get_subfolder_path(subfolder_name=LOG_SUBFOLDERS[2],
                                                                  device_name=device_name)
            self._pti_log = None
            self._pti_log_file = None
            self._total_pti_log = 0
            self.__init_pti_log()

        # UART (Serial) log parameters
        # It is possible to log on several serial port at the same time
        # For each port, the user can decide to listen to it or not:
        # Value of retrieveSerialTrace is an ordered list of booleans separated by ;
        self._serial_log_enable_list = self._dut_instance.get_config(
            "retrieveSerialTrace", "False").replace(" ", "").split(";")
        self._num_of_serial_confs = len(self._serial_log_enable_list)

        # Value of serialPort is an ordered list of string separated by ;
        self._serial_port_list = self._dut_instance.get_config(
            "serialPort", "COM1").replace(" ", "").split(";")
        num_of_serial_port_confs = len(self._serial_port_list)

        # Value of serialBaudRate is an ordered list of integers separated by ;
        self._serial_baudrate_list = self._dut_instance.get_config(
            "serialBaudRate", "115200").replace(" ", "").split(";")
        num_of_serial_baud_rate_confs = len(self._serial_baudrate_list)

        # Value of serialHdwFlowControl is an ordered list of integers separated by ;
        self._serial_hw_flow_control_list = self._dut_instance.get_config(
            "serialHdwFlowControl", "False").replace(" ", "").split(";")
        num_of_serial_hw_control_confs = len(self._serial_hw_flow_control_list)

        # Check that confs are complete, no element are missing
        if not all(x == self._num_of_serial_confs for x in (num_of_serial_port_confs,
                                                            num_of_serial_baud_rate_confs,
                                                            num_of_serial_hw_control_confs)):
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, "Missing serial log information")

        # Create everything serial (UART) logging requires only if required, for all ports
        conf_id = 0
        self._serial_confs = {}
        is_serial_conf_enable = False

        # Add all serial configuration to a same dictionary
        while conf_id < self._num_of_serial_confs:
            self._serial_confs[(ENABLE + str(conf_id))] = str_to_bool(self._serial_log_enable_list[conf_id])

            if self._serial_confs[(ENABLE + str(conf_id))]:
                is_serial_conf_enable = True

                if self._serial_port_list[conf_id] is not "":
                    self._serial_confs[PORT + str(conf_id)] = self._serial_port_list[conf_id]
                else:
                    self._serial_confs[PORT + str(conf_id)] = "COM1"

                if self._serial_baudrate_list[conf_id].isdigit():
                    self._serial_confs[BAUDRATE + str(conf_id)] = int(self._serial_baudrate_list[conf_id])
                else:
                    self._serial_confs[BAUDRATE + str(conf_id)] = 115200

                self._serial_confs[HWCTRLFLOW + str(conf_id)] = str_to_bool(self._serial_hw_flow_control_list[conf_id])
            conf_id += 1

        # Create folder for SERIAL only if required
        if is_serial_conf_enable:
            self._serial_log_folder = report_tree.get_subfolder_path(subfolder_name=LOG_SUBFOLDERS[3],
                                                                     device_name=device_name)
            self.__init_serial_log()

        # Callback dictionary
        self.__start_log = {"MODEM": self.__start_modem_log,
                            "APPLICATION": self.__start_application_log,
                            "PTI": self.__start_pti_log,
                            "SERIAL": self.__start_serial_log}

        self.__stop_log = {"MODEM": self.__stop_modem_log,
                           "APPLICATION": self.__stop_application_log,
                           "PTI": self.__stop_pti_log,
                           "SERIAL": self.__stop_serial_log}

        self.__retrieve_log = {"MODEM": self.__retrieve_modem_log,
                               "APPLICATION": self.__retrieve_application_log}

        self.__erase_log = {"APPLICATION": self.__erase_application_log}

    def __init_pti_log(self):
        """
        Depends on device config
            Init logging capabilities: PTI, LTB
        """
        from acs.Device.DeviceLogger.MptaLogger.MptaLogger import MptaLogger

        self._pti_log = MptaLogger(self._pti_probe)
        self._pti_log_file = os.path.join(self._pti_log_folder,
                                          str(self._dut_instance.get_phone_model() + "_" +
                                              self._current_time))

    def __init_serial_log(self):
        """
        Constructor of the logger
        """
        from acs.Device.DeviceLogger.SerialLogger.SerialLogger import SerialLogger

        conf_id = 0
        while conf_id < self._num_of_serial_confs:
            serial_logger = None

            if self._serial_confs[(ENABLE + str(conf_id))]:
                self._serial_confs[PORT_NAME + str(conf_id)] = self._serial_confs[
                    PORT + str(conf_id)].replace(os.sep, "_")

                serial_logger = SerialLogger(self)

                self._serial_confs[SERIAL_LOG_FILE + str(conf_id)] = \
                    os.path.join(self._serial_log_folder,
                                 str(self._dut_instance.get_phone_model() + "_" + self._current_time + "_SERIAL_" +
                                     self._serial_confs[PORT_NAME + str(conf_id)] + ".log"))

                serial_logger.set_output_file(self._serial_confs[SERIAL_LOG_FILE + str(conf_id)])

                if serial_logger.configure(
                    com_port=self._serial_confs[PORT + str(conf_id)],
                    baudrate=self._serial_confs[BAUDRATE + str(conf_id)],
                    hdw_flow_control=self._serial_confs[HWCTRLFLOW + str(conf_id)]) != Global.SUCCESS:
                    serial_logger = None
                else:
                    self._serial_confs[SERIAL_LOGGER + str(conf_id)] = serial_logger
            conf_id += 1

    def __start_application_log_timer(self, timer=None):
        """
        Start the timer to retrieve application logs from the device
        """
        try:
            # Start timer to retrieve application log
            if timer is None:
                aplog_timer = int(self._application_log_options["pull_timer"])
            else:
                aplog_timer = timer
            self.__aplog_timer = Timer(aplog_timer, self.__retrieve_application_log, [True])
            self.__aplog_timer.name = "EmbeddedLog:ApplicationLogTimer"
            self.__aplog_timer.daemon = True
            self.__aplog_timer.start()

            self.__is_application_logger_started = True

        except Exception as ex:  # pylint: disable=W0703
            self._dut_instance.get_logger().debug("Unable to launch aplog timer : %s" % (str(ex),))

    def __start_application_log(self):
        """
        Start the application log for the device.
        Usually call after a first successful connection to the device.
        """
        if self._application_log_enable and not self.__is_application_logger_started:
            if self._dut_instance.get_config("cleanLogcat", "True", "str_to_bool"):
                self.__erase_application_log()

            self._dut_instance.get_logger().debug("Starting application log...")

            if self.__aplog_timer is not None:
                try:
                    if self.__aplog_timer.isAlive():
                        self.__aplog_timer.cancel()
                except Exception as ex:  # pylint: disable=W0703
                    self._dut_instance.get_logger().debug("Unable to initialize aplog timer : %s" % (str(ex),))
                finally:
                    self.__aplog_timer = None

            # Start the application log timer
            self.__start_application_log_timer(1)
            aplog_timer = int(self._application_log_options["pull_timer"])
            self._dut_instance.get_logger().debug(
                "Application log started: retrieving aplog every %d s" % (aplog_timer,))

    def __copy_aplog_files_on_host(self):
        """
        Pull aplogs from device to host as temporary file.
        Those temporary files will be renamed into their final name at the end of the campaign
        """

        # Get aplog options
        pull_timeout = int(self._application_log_options["aplog_pull_timeout"])
        aplog_folder = self._application_log_options["log_location"]

        try:
            # Create temporary folder (if needed) to store aplogs
            tmp_aplog_folder = os.path.join(self._application_log_folder, TMP_FOLDER)
            if not os.path.isdir(tmp_aplog_folder):
                os.makedirs(tmp_aplog_folder)

            # Always retrieve current aplog file
            self._dut_instance.pull(remotepath="{0}/aplog".format(aplog_folder),
                                    localpath=self._application_log_folder,
                                    timeout=pull_timeout,
                                    silent_mode=True,
                                    force_execution=True)
            # List all generated aplog
            # This command will return a list of aplog files with its unique id
            # obtained by checksum algorithm
            # ls aplog.* | xargs cksum
            # 2893497734 5120005 aplog.1
            # 1797278614 5120010 aplog.2
            # 1086330118 5120066 aplog.3
            # 3387085104 5120071 aplog.4
            # 1017804844 5120021 aplog.5
            # 1304156047 5120280 aplog.6
            # 3117525335 5120212 aplog.7
            # checksum   file size file name
            output_cmd = self._dut_instance.run_cmd(
                cmd="adb shell ls %s/aplog.* | xargs cksum" % (aplog_folder,),
                timeout=self._uecmd_default_timeout, silent_mode=True,
                force_execution=True)
            if output_cmd[0] != Global.FAILURE and "No such file" not in output_cmd[1]:
                # List aplog checksum on host
                aplog_checksum_list_on_host = [self._aplog_reg_host.findall(x)[0][2]
                                               for x in os.listdir(tmp_aplog_folder)
                                               if self._aplog_reg_host.findall(x)]
                # List aplog files on device
                # It is a list of tuple of 3 elements : aplog checksum, aplog size and aplog index
                aplog_files_on_device = [tuple(self._aplog_reg_device.findall(x)[0])
                                         for x in output_cmd[1].splitlines()
                                         if self._aplog_reg_device.findall(x)]

                # Pull files which are not on host
                aplog_file_pulled = False
                for aplog_checksum, _, aplog_index in aplog_files_on_device:
                    # If the file does not exists we pull it
                    if aplog_checksum not in aplog_checksum_list_on_host:
                        remote_path = "{0}/aplog.{1}".format(aplog_folder, aplog_index)
                        aplog_file_to_pull = os.path.join(
                            tmp_aplog_folder,
                            "{0}.aplog.{1}.{2}".format(self._aplog_group_id, aplog_index, aplog_checksum))
                        self._dut_instance.pull(remotepath=remote_path,
                                                localpath=aplog_file_to_pull,
                                                timeout=pull_timeout,
                                                silent_mode=True)
                        aplog_file_pulled = True

                if aplog_file_pulled:
                    self._aplog_group_id += 1

        except DeviceException as device_exception:
            error_msg = "Error when retrieving aplog: %s" % (device_exception.get_error_message(),)
            self._dut_instance.get_logger().error(error_msg)

    def __retrieve_application_log(self, relaunch_timer=False):
        """
        Fetch application logs from devices, if any.
        """
        if self._application_log_enable:
            try:
                if self._dut_instance.is_available():
                    self.__copy_aplog_files_on_host()
                else:
                    warning_msg = "Retrieving aplog not possible, no adb connection to the device"
                    self._dut_instance.get_logger().warning(warning_msg)

                # Relaunch timer if needed
                if self.__is_application_logger_started and relaunch_timer:
                    self.__start_application_log_timer()

                elif self.__aplog_timer and self.__aplog_timer.isAlive():
                    self.__aplog_timer.cancel()
                    self.__aplog_timer = None

            except (KeyboardInterrupt, SystemExit):
                # Skip pulling and stop properly the application log mechanism
                self._dut_instance.get_logger().debug("Received ctrl-c when retrieving aplog !")
                self.__stop_application_log()
                raise

    def __rename_tmp_application_log(self):
        """
        Rename aplog located in tmp folder into final name(i.e: aplog.1, aplog.2 ...)
        """
        # Rename aplog files located in temporary folder
        tmp_aplog_folder = os.path.join(self._application_log_folder, TMP_FOLDER)

        if os.path.exists(tmp_aplog_folder):
            try:
                # List and sort application logs
                aplog_index = 1
                for aplog_group_id in range(self._aplog_group_id, 0, -1):
                    # Greater group id contains more recent aplog files
                    aplog_files = sorted([x for x in os.listdir(tmp_aplog_folder)
                                          if x.find("{0}.aplog.".format(aplog_group_id)) != -1])
                    for aplog_file in aplog_files:
                        shutil.copy(os.path.join(tmp_aplog_folder, aplog_file),
                                    os.path.join(self._application_log_folder, "aplog.{0}".format(aplog_index)))
                        aplog_index += 1
                # Remove temporary folder
                shutil.rmtree(tmp_aplog_folder, ignore_errors=True)
            except (shutil.Error, _SysErrors) as shutil_error:
                self._dut_instance.get_logger().debug("Error when formatting aplog: %s" % (str(shutil_error),))

        else:
            self._dut_instance.get_logger().debug("No aplog retrieved")

    def __stop_application_log(self):
        """
        Stop and format the application log of the device.
        """
        if self._application_log_enable and self.__is_application_logger_started:

            self._dut_instance.get_logger().debug("Stopping application log...")

            # Disable timer to retrieve application logs
            try:
                if self.__aplog_timer and self.__aplog_timer.isAlive():
                    self.__aplog_timer.cancel()
                self.__aplog_timer = None
            except Exception as ex:  # pylint: disable=W0703
                self._dut_instance.get_logger().debug("Error occurred when cancelling aplog timer : %s" % (str(ex),))

            # Retrieve application one last time before stopping
            self.__retrieve_application_log()

            self.__is_application_logger_started = False
            self._dut_instance.get_logger().debug("Application log stopped")

    def __erase_application_log(self):
        """
        Erase the application log of the device.
        """
        # Clean application logs
        if self._application_log_enable:

            # Rename application logs
            self.__rename_tmp_application_log()

            if self._clean_application_logs:
                self._dut_instance.get_logger().debug("Erasing application log...")
                if self._dut_instance.is_available():
                    aplog_folder = self._application_log_options["log_location"]
                    self._dut_instance.run_cmd("adb shell rm %s/aplog.*" % (aplog_folder,),
                                               self._uecmd_default_timeout,
                                               silent_mode=True)
                    self._dut_instance.get_logger().debug("Application log erased")
                else:
                    warning_msg = "Erasing aplog not possible, no adb connection to the device"
                    self._dut_instance.get_logger().warning(warning_msg)

    def __start_modem_log(self):
        """
        Starts the modem log for the device.
        Usually call after a first successful connection to the device.
        """
        if self._modem_log_enable and not self.__is_modem_logger_started:

            self._dut_instance.get_logger().debug("Starting modem log...")

            if self._dut_instance.is_available():
                # Retrieve modem trace option
                hsi_speed = self._modem_trace_options["hsi_speed"]
                trace_level = self._modem_trace_options["trace_level"]
                trace_location = self._modem_trace_options["trace_location"]
                file_size_option = self._modem_trace_options["file_size_option"]

                # Configure Modem Trace
                self._modem_api.configure_modem_trace(hsi_speed, int(trace_level))
                # Wait a while
                time.sleep(self._wait_btwn_cmd)
                # Reboot phone
                self._dut_instance.reboot(wait_for_transition=True)

                # Activate trace_modem
                if trace_location.lower() == "sdcard":
                    trace_location = BPLOG_LOC.SDCARD  # pylint:disable=E1101
                else:
                    trace_location = BPLOG_LOC.EMMC  # pylint:disable=E1101

                self._modem_api.activate_modem_trace(trace_location, int(file_size_option))

                self.__is_modem_logger_started = True
                self._dut_instance.get_logger().debug("Modem log started")
            else:
                warning_msg = "Starting modem log not possible, no adb connection to the device"
                self._dut_instance.get_logger().warning(warning_msg)

    def __retrieve_modem_log(self):
        """
        Fetch modem logs from the device, if any.
        """
        if self._modem_log_enable and self.__is_modem_logger_started:

            if self._dut_instance.is_available():
                # Retrieve pull timeout
                pull_timeout = int(self._modem_trace_options["pull_timeout"])
                trace_location = self._modem_trace_options["trace_location"]

                # Retrieve modem logs list
                if trace_location.lower() == "sdcard":
                    modem_log_path = "/sdcard/logs"
                else:
                    modem_log_path = "/logs"
                output_cmd = self._dut_instance.run_cmd("adb shell ls %s/bplog*" % (modem_log_path,),
                                                        self._uecmd_default_timeout,
                                                        silent_mode=True)
                if output_cmd[0] == Global.FAILURE or "No such file" in output_cmd[1]:
                    self._dut_instance.get_logger().debug("Error retrieving modem log: %s" % (output_cmd[1],))
                else:
                    # Fetch all modem logs
                    list_files = [str(x).strip() for x in output_cmd[1].splitlines()]
                    for modem_log_filename in list_files:
                        try:
                            self._dut_instance.get_logger().debug("Retrieving modem log...")
                            self._dut_instance.pull(modem_log_filename, self._modem_log_folder, pull_timeout)
                            self._dut_instance.get_logger().debug("Modem log retrieved")
                        except (KeyboardInterrupt, SystemExit):
                            # Stop properly the modem log mechanism
                            self._dut_instance.get_logger().debug("Received ctrl-c when retrieving modem log !")
                            self.__stop_modem_log()
                            raise
                        except DeviceException as device_exception:
                            self._dut_instance.get_logger().debug("Error when retrieving modem log: %s"
                                                                  % (device_exception.get_error_message(),))
                            break
            else:
                warning_msg = "Retrieving modem log not possible, no adb connection to the device"
                self._dut_instance.get_logger().warning(warning_msg)

    def __stop_modem_log(self):
        """
        Stop the modem log of the device.
        Clean logs if needed
        """
        if self._modem_log_enable and self.__is_modem_logger_started:

            self._dut_instance.get_logger().debug("Stopping modem log...")

            if self._dut_instance.is_available():
                # stopping service
                self._modem_api.deactivate_modem_trace()
                # stop tracing
                self._modem_api.configure_modem_trace("u", 0)

                # Clean modem logs
                if self._clean_modem_logs:
                    trace_location = self._modem_trace_options["trace_location"]
                    if trace_location.lower() == "sdcard":
                        modem_log_path = "/sdcard/logs"
                    else:
                        modem_log_path = "/logs"

                    self._dut_instance.run_cmd("adb shell rm %s/bplog*" % (modem_log_path,),
                                               self._uecmd_default_timeout,
                                               silent_mode=True)

                self.__is_modem_logger_started = False
                self._dut_instance.get_logger().debug("Modem log stopped")
            else:
                warning_msg = "Stopping modem log not possible, no adb connection to the device"
                self._dut_instance.get_logger().warning(warning_msg)

    def __start_pti_log(self):
        """
        Starts the pti log for the device. The probe can be either PTI or LTB.
        """
        if self._pti_log_enable and self._pti_log:
            self._dut_instance.get_logger().debug("Starting PTI log...")
            self._total_pti_log += 1

            # pylint: disable=W0703
            # Agree to catch and report all exceptions
            # while starting pti logger
            try:
                self._pti_log.set_output_file(self._pti_log_file + "_PTI_" + str(self._total_pti_log))
                self._pti_log.start()
                self._dut_instance.get_logger().debug("PTI log started")
            except Exception as exception:
                self._dut_instance.get_logger().error("Exception when starting PTI log [%s]", str(exception))

    def __stop_pti_log(self):
        """
        Stops the pti log for the device.
        """
        if self._pti_log_enable and self._pti_log:
            self._dut_instance.get_logger().debug("Stopping PTI log...")

            # pylint: disable=W0703
            # Agree to catch and report all exceptions
            # while disconnecting the pti
            try:
                self._pti_log.stop()
                self._dut_instance.get_logger().debug("PTI log stopped")
            except Exception as exception:
                self._dut_instance.get_logger().error("Exception when stopping PTI log [%s]", str(exception))

    def __start_serial_log(self):
        """
        Starts the serial (UART) log for the device.
        """

        conf_id = 0
        while conf_id < self._num_of_serial_confs:

            if self._serial_confs[(ENABLE + str(conf_id))] and self._serial_confs[SERIAL_LOGGER + str(conf_id)]:
                self._dut_instance.get_logger().debug("Starting SERIAL (UART) log on port %s ...",
                                                      self._serial_confs[PORT_NAME + str(conf_id)])
                try:
                    if self._serial_confs[SERIAL_LOGGER + str(conf_id)].start() == Global.SUCCESS:
                        self._dut_instance.get_logger().debug("SERIAL (UART) log started on port %s",
                                                              self._serial_confs[PORT_NAME + str(conf_id)])
                except Exception as exception:
                    self._dut_instance.get_logger().error("Exception when starting SERIAL (UART) log on port %s [%s]",
                                                          self._serial_confs[PORT_NAME + str(conf_id)], str(exception))

            conf_id += 1

    def __stop_serial_log(self):
        """
        Stops the serial (UART) log for the device.
        """

        conf_id = 0
        while conf_id < self._num_of_serial_confs:

            if self._serial_confs[(ENABLE + str(conf_id))] and self._serial_confs[SERIAL_LOGGER + str(conf_id)]:
                self._dut_instance.get_logger().debug("Stopping SERIAL (UART) log on port %s ...",
                                                      self._serial_confs[PORT_NAME + str(conf_id)])
                try:
                    self._serial_confs[SERIAL_LOGGER + str(conf_id)].stop()
                    self._dut_instance.get_logger().debug("SERIAL (UART) log stopped on port %s",
                                                          self._serial_confs[PORT_NAME + str(conf_id)])
                except Exception as exception:
                    self._dut_instance.get_logger().error("Exception when stopping SERIAL (UART) log on port % [%s]",
                                                          self._serial_confs[PORT_NAME + str(conf_id)], str(exception))
            conf_id += 1

    def start(self, log_type):
        """
        Start embedded logs

        :type log_type: string
        :param log_type: Log to retrieve
            Possible values: MODEM, APPLICATION, PTI, SERIAL
        """
        dict_key = str(log_type).upper()
        if dict_key not in self.__start_log:
            self._dut_instance.get_logger().debug("Unable to start %s logs ! Feature not implemented."
                                                  % (str(log_type),))
        else:
            # Call method from callback dictionary
            self.__start_log[dict_key]()

    def stop(self, log_type):
        """
        Stop embedded logs

        :type log_type: string
        :param log_type: Log to retrieve
            Possible values: MODEM, APPLICATION, PTI, SERIAL
        """
        dict_key = str(log_type).upper()
        if dict_key not in self.__stop_log:
            self._dut_instance.get_logger().debug("Unable to stop %s logs ! Feature not implemented."
                                                  % (str(log_type),))
        else:
            # Call method from callback dictionary
            self.__stop_log[dict_key]()

    def retrieve_log(self, log_type):
        """
        Retrieve embedded logs

        :type log_type: string
        :param log_type: Log to retrieve
            Possible values: MODEM, APPLICATION
        """
        dict_key = str(log_type).upper()
        if dict_key not in self.__retrieve_log:
            self._dut_instance.get_logger().debug("Unable to retrieve %s logs ! Feature not implemented."
                                                  % (str(log_type),))
        else:
            # Call method from callback dictionary
            self.__retrieve_log[dict_key]()

    def erase_log(self, log_type):
        """
        Erase embedded logs

        :type log_type: string
        :param log_type: Log to erase
            Possible values: APPLICATION
        """
        dict_key = str(log_type).upper()
        if dict_key not in self.__erase_log:
            self._dut_instance.get_logger().debug("Unable to erase %s logs ! Feature not implemented."
                                                  % (str(log_type),))
        else:
            # Call method from callback dictionary
            self.__erase_log[dict_key]()

    def enable_log_on_pti(self):
        """
        Enable pti log
        """
        if self._pti_log_enable:
            self._dut_instance.get_logger().info("Forwarding logcat log to PTI log ...")
            if self._dut_instance.is_available():
                self._dut_instance.run_cmd(self._pti_cmdline, 1)
                self._dut_instance.get_logger().info("Logcat log forwarded to PTI log")
            else:
                warning_msg = "Forwarding logcat log on PTI not possible, no adb connection to the device"
                self._dut_instance.get_logger().warning(warning_msg)
