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
# pylint: disable=unused-argument

from acs.UtilitiesFWK.Utilities import AcsConstants, Global
from acs.Device.Model.DeviceBase import DeviceBase
from acs.Device.DeviceManager import DeviceManager


class Dummy(DeviceBase):

    """
    Class that dummy phone
    """

    OS_TYPE = 'DUMMY'

    def __init__(self, config, logger):
        """
        Constructor

        :type  phone_name: string
        :param phone_name: Name of the current phone(e.g. PHONE1)
        """
        # Create empty UECmd section
        config["UECmd"] = ""

        DeviceBase.__init__(self, config, logger)

        # Is phone connected for UECmd?
        self._is_phone_connected = False

        # Is phone booted (ready to be connected)?
        self._is_phone_booted = False

        # set device number to not available
        self._serial_number = AcsConstants.NOT_AVAILABLE

    def get_device_logger(self):
        """
        Get device logger instance.

        :rtype: object
        :return a logger instance
        """
        return None

    def get_device_info(self):
        """
        Get device information.

        :rtype: dict
        :return an empty dictionnary
        """
        return {}

    def initialize(self):
        """
        Initialize the environment of the target.
        """
        return

    def cleanup(self, campaign_error):
        """
        Clean up the environment of the target.

        :type campaign_error: boolean
        :param campaign_error: Notify if errors occur:
            # Check if we use an integer and check if not a negative value
            timeout = self._flash_time_out
            self.get_logger().warning(
                "Flash timeout should be an integer > 0, using value from Device_Catalog ({0})".format(timeout))
        else:
            # Value is good: Inform user on the flash timeout value taken
            self.get_logger().info("Flash timeout defined by the user used ({0} seconds)".format(timeout))

        :rtype: tuple of int and str
        :return: verdict and final dut state
        """
        return True, "NO_POWER_STATE"

    def init_device_connection(self, skip_boot_required, first_power_cycle, power_cycle_retry_number):
        """
        Init the device connection.

        Call for first device connection attempt or to restart device before test case execution
        """
        return_code, return_msg = self.switch_on()

        connection_status = (return_code == Global.SUCCESS)
        power_cycle_occurence = 1
        boot_failure_occurence = 0
        connection_failure_occurence = 0
        return (connection_status,
                return_msg,
                power_cycle_occurence,
                boot_failure_occurence,
                connection_failure_occurence)

    def switch_on(self, boot_timeout=None,
                  settledown_duration=None,
                  simple_switch_mode=False):
        """
        Switch ON the board

        :param boot_timeout: Total time to wait for booting
        :param settledown_duration: Time to wait until start to count for timeout,
                                    Period during which the device must have started.
        :rtype: list
        :return: Output status and output log
        """
        self.get_logger().info("Switching on the board...")
        self._is_phone_booted = True
        self.get_logger().info("Phone should be ready!")
        self.connect_board()

        return Global.SUCCESS, "No errors"

    def switch_off(self):
        """
        Switch OFF the board.

        :rtype: list
        :return: Output status and output log
        """
        self.get_logger().info("Switch off the board...")
        self.disconnect_board()

        return Global.SUCCESS, "No errors"

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
        return True

    def connect_board(self):
        """
        Open connection to the board
        """
        # Connect to the board
        self.get_logger().info("Connecting the board...")
        self._is_phone_connected = True
        self.get_logger().info("*** Connected!")

        # Retrieve/update device properties
        DeviceManager().update_device_properties(self.whoami().get('device'))

        return self._is_phone_connected

    def disconnect_board(self):
        """
        Close SSH to the board.
        """
        self.get_logger().info("Disconnecting the board...")
        self._is_phone_connected = False
        self.get_logger().info("*** Disconnected!")

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

        # Run cmd only if phone is available
        if self._is_phone_connected:
            # Run the command
            logging_msg = "*** RUN: %s\r" % str(cmd)
            self.get_logger().info(logging_msg)
            self.get_logger().info("SUCCESS!")
            result = Global.SUCCESS
            output = "No errors"
        else:
            result = Global.FAILURE
            output = "NO PHONE!!"
            self.get_logger().error(output)

        return result, output

    def is_available(self):
        """
        Check if the board can be used.

        :return: availability status
        :rtype: bool
        """
        return self._is_phone_connected

    def is_booted(self):
        """
        Check if the board has booted successfully.

        :return: boot status
        :rtype: bool
        """
        return self._is_phone_booted

    def get_sw_release(self):
        """
        Get the SW release of the device.

        :rtype: str
        :return: SW release
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.sw_release")
        return self.device_properties.sw_release

    def retrieve_serial_number(self):
        """
        Retrieve the serial number of the device.

        :rtype: str
        :return: serial number of the device, or None if unknown
        """
        return self._serial_number

    def get_serial_number(self):
        """
        Get the device's serial number

        :return: device serial number
        :rtype: str
        """
        return self._serial_number

    def get_device_id(self):
        """
        Get the device's unique id

        :return: device unique id
        :rtype: str
        """
        self.get_logger().warning("Deprecated method, you should use device property"
                                  " : device.device_properties.device_id")
        return self.device_properties.device_id

    def retrieve_device_id(self):
        """
        Retrieve the unique id of the device.

        :rtype: str
        :return: unique id of the device, or None if unknown
        """
        return self.device_properties.device_id
