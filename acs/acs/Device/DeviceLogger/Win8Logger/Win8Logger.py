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

from acs.Device.DeviceLogger.ILogger import ILogger
from acs.Device.DeviceLogger.Win8Logger.Win8ReaderThread import Win8ReaderThread
from acs.Core.Report.ACSLogging import LOGGER_FWK


class Win8Logger(ILogger):

    """
    Logger based on Windows8 log system.
    """

    def __init__(self, ip_address, port_number):
        """Constructor of the Win8Logger class.

        :type ip_address: string
        :param serial_number: device's serial number.
        :type port_number: int
        :param port_number: which port to listen, to read logs of the device.
        """
        self._logger = LOGGER_FWK
        self.__reader_thread = Win8ReaderThread(ip_address, port_number)

    def set_output_file(self, path):
        """ Specify the path where log will be saved.

        :type  path: string
        :param path: Path to the output log file
        """
        self.__reader_thread.set_output_path(path)
        return

    def start(self):
        """ Start the logging.
        """
        self.__reader_thread.start()
        return

    def stop(self):
        """ Stop the logging.
        """
        self.__reader_thread.stop()
        return

    def reset(self):
        self.__reader_thread.reset()  # pylint: disable=E1101
        return

    def is_message_received(self, message, timeout):
        """ Check if a message is received

        :type  message: string
        :param path: message that we look for
        :type  timeout: int
        :param timeout: time limit where we expect to receive the message

        :return: message content if received, None else
        :rtype: String
        """
        return self.__reader_thread.is_message_received(message, timeout)  # pylint: disable=E1101

    def add_trigger_message(self, message):
        """ Trigger a message

        :type  message: string
        :param path: message to be triggered
        """
        self.__reader_thread.add_trigger_message(message)  # pylint: disable=E1101
        return

    def get_message_triggered_status(self, message):
        """ Get the status of a message triggered

        :type  message: string
        :param path: message triggered
        :return: Message status
        :rtype: string
        """
        return self.__reader_thread.get_message_triggered_status(message)  # pylint: disable=E1101

    def remove_trigger_message(self, message):
        return self.__reader_thread.remove_trigger_message(message)  # pylint: disable=E1101

    def reset_trigger_message(self, message):
        return self.__reader_thread.reset_trigger_message(message)  # pylint: disable=E1101


if __name__ == "__main__":
    log_reader = Win8Logger("127.0.0.1", 8003)
    log_reader.set_output_file("log22022012.txt")
    log_reader.start()
