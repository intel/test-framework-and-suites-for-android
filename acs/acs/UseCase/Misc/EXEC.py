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


import platform
import os.path
import re
import subprocess
import tempfile
import time
import shlex
import sys
import json

from acs.UseCase.UseCaseBase import UseCaseBase
from acs.UtilitiesFWK.Utilities import Global


class Exec(UseCaseBase):

    """
    Generic use case that run shell commands and extract the verdict
    from the exec return code or by parsing the stdout
    """

    def __init__(self, tc_name, global_config):
        """
        Constructor
        """
        UseCaseBase.__init__(self, tc_name, global_config)

        self._global_config = global_config
        self._run_from_tc_directory = self._tc_parameters.get_param_value("RUN_FROM_TCDIRECTORY", default_value="False",
                                                                          default_cast_type="str_to_bool")

    def initialize(self):
        """
        Process the **<Initialize>** section of the XML file and execute defined test steps.
        """
        UseCaseBase.initialize(self)
        verdict, msg = Global.SUCCESS, ""

        # Export all ACS Global parameters as an JSON object into ACS_GLOBAL_PARAMETERS
        # environment variable so that user can access them from inside the
        # script that is being executed
        device_cfg_dict = self._global_conf.benchConfig.get_dict()
        dc_l = len(self._global_conf.deviceConfig)
        for x in range(1, dc_l + 1):
            device_cfg_dict['PHONE%s' % x] = self._global_conf.deviceConfig['PHONE%s' % x]
        device_cfg_dict['PHONE1']['serialNumber'] = self._device.retrieve_serial_number()
        os.environ['ACS_GLOBAL_PARAMETERS'] = json.dumps(device_cfg_dict)

        return verdict, msg

    def __internal_exec(self, command, timeout, expected_result):
        """
        Execute the command and return the result
        :type command: string
        :param command: command to be executed
        :type timeout: int
        :param timeout: command timeout (in second)
        :type expected_result: int or string
        :param expected_result: if int, it will check exec return code
        and compare it. If string, it will check the stdout to find the
        expected string
        :rtype: tuple
        :return: execution status (FAILURE or SUCCESS), stdout
        """

        f_stdout = tempfile.TemporaryFile()
        proc = None
        expected_triglog = None
        exec_status = Global.FAILURE
        current_dir = os.getcwd()

        try:
            if self._run_from_tc_directory:
                execution_path = os.path.join(self._execution_config_path,
                                              os.path.dirname(self._name))
                os.chdir(execution_path)
            if expected_result is None:
                expected_result = 0

            # Check that expected result is trigger message from device log
            if str(expected_result).startswith("[TRIG_LOG]"):
                expected_triglog = str(expected_result).replace("[TRIG_LOG]", "").strip()
                self._device.get_device_logger().add_trigger_message(expected_triglog)

            if timeout is None:
                timeout = 5
            exec_timeout = float(timeout)

            args = list()
            if not isinstance(command, list):
                if "Windows" in platform.system():
                    command = str(command).split()
                else:
                    command = shlex.split(command)

            for item in command:
                args.append(item)

            proc = subprocess.Popen(args,
                                    stdout=f_stdout,
                                    stderr=subprocess.STDOUT)

            timeout = float(timeout)
            while timeout > 0 and proc.poll() is None:
                # Agree to keep t0 & t1 variable names
                t0 = time.time()
                time.sleep(0.2)
                t1 = time.time()
                timeout -= (t1 - t0)

            # Process or timeout terminated
            # Get return code
            return_code = proc.poll()
            # Get stdout & stderr
            f_stdout.seek(0)
            stdout = f_stdout.read()

            exec_status = Global.FAILURE
            if return_code is not None:
                # Check if triggering Device log
                if expected_triglog is not None:
                    # Get triggered messages from device log
                    start_time = time.time()
                    triglog_found = False

                    while not triglog_found and \
                            ((time.time() - start_time) < exec_timeout):
                        # Get triggered messages from device log
                        messages = self._device.get_device_logger().\
                            get_message_triggered_status(expected_triglog)

                        if isinstance(messages, list) and (len(messages) > 0):
                            triglog_found = True

                    if triglog_found:
                        exec_status = Global.SUCCESS
                    else:
                        exec_status = Global.FAILURE
                        self._logger.error("Did not find trigger \"%s\","
                                           " in device log." % expected_triglog)

                    # Remove triggered messages from device log
                    self._device.get_device_logger().\
                        remove_trigger_message(expected_triglog)

                # In that condition, isdigit is called on string
                elif isinstance(expected_result, int) or\
                    ((isinstance(expected_result, str) or
                        isinstance(expected_result, unicode))
                        and expected_result.isdigit()):
                    if int(expected_result) == return_code:
                        # If expected_result is an integer
                        # and if it's equal to the return code then
                        exec_status = Global.SUCCESS
                    else:
                        self._logger.error("Expected \"%s\", got \"%s\""
                                           % (expected_result, return_code))
                elif expected_result in stdout:
                    # Expected result is a string, search for this pattern
                    # in the output
                    exec_status = Global.SUCCESS
                else:
                    self._logger.error("Did not find trigger \"%s\", in stdout."
                                       % expected_result)
            else:
                # Timeout !!
                self._logger.error("Timeout !")

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            stdout = str(ex)
        finally:
            if proc is not None and not proc.terminate:  # pylint: disable=E1101
                # pylint: disable=E1101
                proc.terminate()

            f_stdout.close()
            os.chdir(current_dir)

        return exec_status, stdout

    def __run_cmd(self, command, timeout, expected_result):
        """
        Execute the command and return the result
        :type command: string
        :param command: command to be executed
        :type timeout: int
        :param timeout: command timeout (in second)
        :type expected_result: int or string
        :param expected_result: if int, it will check exec return code
        and compare it. If string, it will check the stdout to find the
        expected string
        :rtype: tuple
        :return: execution status (FAILURE or SUCCESS), output
        """
        if command.strip().lower().find("[sleep(") != -1:
            command = command.strip().lower().replace("[sleep(", "")
            command = command.replace(")]", "")
            sleep_time = float(command)
            time.sleep(sleep_time)
            status = Global.SUCCESS
            output = "Success"
        elif command.strip().lower().find("[usb_plug]") != -1:
            if self._device is not None and self._io_card is not None:
                self._io_card.usb_host_pc_connector(True)
                self._device.connect_board()
                status = Global.SUCCESS
                output = "Success"
            else:
                self._logger.error("Cannot execute usb_plug, no io card configured.")
                status = Global.FAILURE
                output = "Cannot execute usb_plug, no io card configured."
        elif command.strip().lower().find("[usb_unplug]") != -1:
            if self._device is not None and self._io_card is not None:
                self._device.disconnect_board()
                self._io_card.usb_host_pc_connector(False)
                status = Global.SUCCESS
                output = "Success"
            else:
                self._logger.error("Cannot execute usb_unplug, no io card configured.")
                status = Global.FAILURE
                output = "Cannot execute usb_unplug, no io card configured."
        elif command.strip().lower().find("[press_power_button(") != -1:
            command = command.strip().lower().replace("[press_power_button(", "")
            command = command.replace(")]", "")
            press_button_time = float(command)

            if self._io_card is not None:
                self._io_card.press_power_button(press_button_time)
                status = Global.SUCCESS
                output = "Success"
            else:
                self._logger.error("Cannot execute press_power_button, no io card configured.")
                status = Global.FAILURE
                output = "Cannot execute press_power_button, no io card configured."
        elif command.strip().lower().find("[control_relay(") != -1:
            command = command.strip().lower().replace("[control_relay(", "")
            command = command.replace(")]", "")
            relay_nbr = int(command.split(",")[0].strip())
            state = command.split(",")[1].strip().lower()

            if self._io_card is not None:
                if state == "on":
                    self._io_card.enable_line(relay_nbr)
                elif state == "off":
                    self._io_card.disable_line(relay_nbr)
                status = Global.SUCCESS
                output = "Success"
            else:
                self._logger.error("Cannot execute press_relay, no io card configured.")
                status = Global.FAILURE
                output = "Cannot execute press_relay, no io card configured."
        else:
            # Handle multi phone, if we issue adb command, add serial number if we have it
            if "adb" in command.lower():
                command = self._device.format_cmd(command)

            # If curlUtilities is called add the path to Campaign_report
            elif command.strip().lower().find("curlutilities") != -1:
                # Add path to campaign report in CurlUtilities command
                report_tree = \
                    self._global_config.campaignConfig.get("campaignReportTree")
                command += \
                    " --output=%s" % report_tree.get_report_path()

            if "[MY_PATH]" in command:
                command = command.replace("[MY_PATH]",
                                          os.path.dirname(
                                              os.path.abspath(
                                                  self._tc_parameters.get_file_path()))
                                          + os.sep)

            if "[MY_DEVICE_MODEL]" in command:
                command = command.replace("[MY_DEVICE_MODEL]", self._device.get_phone_model())

            # We use the same python that ACS
            if "python" in command:
                command_list = command.split(" ")
                # pyc replacement instead of py curently only works if RUN_FROM_TCDIRECTORY
                # is set to true
                if self._run_from_tc_directory:
                    execution_path = os.path.join(self._execution_config_path,
                                                  os.path.dirname(self._name))
                    for index, command_element in enumerate(command_list):
                        if command_element.endswith(".py"):
                            if os.path.isfile(os.path.join(execution_path, command_element)) is False:
                                pyc_cmd = command_element[:-2] + "pyc"
                                if os.path.isfile(os.path.join(execution_path, pyc_cmd)):
                                    command_list[index] = pyc_cmd

                    command = " ".join(command_list)
                python_path = sys.executable
                command = command.replace("python", python_path)
                self._logger.info("Using python: %s" % python_path)

            if any("acs.py" in cmd.lower() for cmd in command):
                # Put report into sub folder for analysis in case of error
                report_path = self._global_config.campaignConfig.get("campaignReportTree").get_report_path()
                report_subfolder = os.path.join(report_path, os.path.basename(self._name))
                self._logger.info("Detailed results will be found at: {0}".format(report_subfolder))
                command = "{0} --report_folder={1}".format(command, report_subfolder)

                status, _ = \
                    self.__internal_exec(command, timeout, expected_result)
                if status == Global.SUCCESS:
                    output = "Success"
                else:
                    output = "Did not found expected result: {0}".format(expected_result)

            else:
                status, stdout = \
                    self.__internal_exec(command, timeout, expected_result)
                output = "output: {0}".format(stdout.rstrip("\r\n"))
                self._logger.info(output)

        # Remove special characters which could be stored in output message
        allowed_characters = '[^a-zA-Z0-9\-\+\=\'\.\:\,\;\!\?\%\(\)\#\*\@\_\n\t]'
        parsed_output = re.sub(allowed_characters, ' ', output)

        return status, parsed_output

    def __run_cmds(self, cmd_key, timeout_key, expected_value_key):
        """
        Execute a set of command and return the result
        :type cmd_key: string
        :param cmd_key: command key to look for in use case parameter
        :type timeout_key: string
        :param timeout_key: timeout key to look for in use case parameter
        :type expected_value_key: string
        :param expected_value_key: expected value key to look for in use case parameter
        :rtype: tuple
        :return: execution status (FAILURE or SUCCESS), output
        """
        # Check if we have a set of cmd to run
        index = 0
        continue_loop = True
        result = Global.SUCCESS
        output = "No errors"

        while continue_loop:
            if index == 0:
                cmd = "%s" % cmd_key
                timeout = "%s" % timeout_key
                expect_result = "%s" % expected_value_key
            else:
                cmd = "%s%d" % (cmd_key, index)
                timeout = "%s%d" % (timeout_key, index)
                expect_result = "%s%d" % (expected_value_key, index)

            cmd = self._tc_parameters.get_param_value(cmd)
            if cmd is not None:
                timeout = self._tc_parameters.get_param_value(timeout)
                expected_result = self._tc_parameters.get_param_value(expect_result)

                self._logger.info("")
                self._logger.info("Executing: %s" % cmd)
                (result, output) = self.__run_cmd(cmd, timeout, expected_result)

                if result != Global.SUCCESS:
                    continue_loop = False
            else:
                if index != 0:
                    continue_loop = False
            index += 1

        return result, output

    def set_up(self):
        UseCaseBase.set_up(self)
        return self.__run_cmds("SETUP_CMD",
                               "SETUP_TIMEOUT",
                               "SETUP_EXPECT_RESULT")

    def run_test(self):
        UseCaseBase.run_test(self)
        return self.__run_cmds("RUN_CMD",
                               "RUN_TIMEOUT",
                               "RUN_EXPECT_RESULT")

    def tear_down(self):
        UseCaseBase.tear_down(self)
        return self.__run_cmds("TEAR_DOWN_CMD",
                               "TEAR_DOWN_TIMEOUT",
                               "TEAR_DOWN_EXPECT_RESULT")
