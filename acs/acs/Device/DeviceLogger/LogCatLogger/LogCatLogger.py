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
:since: 06/05/2011
:author: sfusilie
"""
from acs.Device.DeviceLogger.ILogger import ILogger
from LogCatReaderThread import LogCatReaderThread
from acs.Core.Report.ACSLogging import LOGGER_FWK


class LogCatLogger(ILogger):

    """
    Logger based on Android log cat system
    """
    ACS_FILTER_KEY = ["ACS", "opcode::"]

    def __init__(self, device_handle, write_logcat_file):
        """Constructor

        :type device_handle: IDevice
        :param device_handle: device handle
        :type write_logcat_file: bool
        :param write_logcat_file: specify if we have to write logcat file or not
        """
        self._logger = LOGGER_FWK

        logcat_cmd_line = device_handle.get_config("logcatCmdLine", "adb shell logcat -v threadtime")
        if "-v threadtime" not in logcat_cmd_line:
            logcat_cmd_line += " -v threadtime"

        acs_logcat_cmd_line = device_handle.get_config(
            "acsLogcatCmdLine", "adb shell logcat *:S ACS ACS_RSP ACS_WD -v threadtime")
        if "-v threadtime" not in acs_logcat_cmd_line:
            acs_logcat_cmd_line += " -v threadtime"

        enable_watchdog = device_handle.get_config("enableWatchdog", True, "str_to_bool")

        self.__acs_log_reader_thread = LogCatReaderThread(device_handle=device_handle,
                                                          logger=self._logger,
                                                          enable_writer=device_handle.get_config(
                                                              "writeAcsLogcat", "False", "str_to_bool"),
                                                          logcat_cmd_line=acs_logcat_cmd_line,
                                                          enable_acs_watchdog=enable_watchdog)

        self.__std_log_reader_thread = LogCatReaderThread(device_handle=device_handle,
                                                          logger=None,
                                                          enable_writer=write_logcat_file,
                                                          logcat_cmd_line=logcat_cmd_line,
                                                          enable_acs_watchdog=enable_watchdog)

        self.__device_handle = device_handle

    def set_output_file(self, path):
        """ Specify the path where log will be saved

        :type  path: string
        :param path: Path to the output log file
        """
        self.__acs_log_reader_thread.set_output_path(path.replace(".log", "_acs.log"))
        self.__std_log_reader_thread.set_output_path(path)

    def start(self):
        """ Start the logging.
        """
        if self.__device_handle.get_config("cleanLogcat", "True", "str_to_bool"):
            self.__device_handle.run_cmd("adb logcat -c", 5)

        if not self.__acs_log_reader_thread.is_started():
            self._logger.debug("Starting ACS logcat processing...")
            self.__acs_log_reader_thread.start()
            self._logger.debug("ACS logcat processing started")

        if not self.__std_log_reader_thread.is_started():
            self._logger.debug("Starting standard logcat processing...")
            self.__std_log_reader_thread.start()
            self._logger.debug("Standard log processing started")

    def stop(self):
        """ Stop the logging.
        """
        if self.__acs_log_reader_thread.is_started():
            self._logger.debug("Stopping ACS logcat processing...")
            self.__acs_log_reader_thread.stop()
            self._logger.debug("ACS logcat processing stopped")

        if self.__std_log_reader_thread.is_started():
            self._logger.debug("Stopping standard logcat processing...")
            self.__std_log_reader_thread.stop()
            self._logger.debug("Standard logcat processing stopped")

    def reset(self):
        self.__acs_log_reader_thread.reset()
        self.__std_log_reader_thread.reset()

    def __get_logger(self, message):
        for key in LogCatLogger.ACS_FILTER_KEY:
            if key in message:
                return self.__acs_log_reader_thread
        return self.__std_log_reader_thread

    def is_message_received(self, message, timeout):
        """ Check if a message is received

        :type  message: string
        :param message: message that we look for
        :type  timeout: int
        :param timeout: time limit where we expect to receive the message

        :return: message content if received, None else
        :rtype: String
        """
        return self.__get_logger(message).is_message_received(message, timeout)

    def add_trigger_message(self, message):
        """ Trigger a message

        :type  message: string
        :param message: message to be triggered
        """
        self.__get_logger(message).add_trigger_message(message)

    def get_message_triggered_status(self, message):
        """ Get the status of a message triggered

        :type  message: string
        :param message: message triggered
        :return: Message status
        :rtype: string
        """
        return self.__get_logger(message).get_message_triggered_status(message)

    def remove_trigger_message(self, message):
        self.__get_logger(message).remove_trigger_message(message)

    def reset_trigger_message(self, message):
        self.__get_logger(message).reset_trigger_message(message)
