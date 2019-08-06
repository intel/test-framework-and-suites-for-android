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
from acs.Device.DeviceLogger.MptaLogger.MptaReaderThread import MptaReaderThread


class MptaLogger(ILogger):

    """
    classdocs
    """

    def __init__(self, probe):
        """
        Constructor
        """
        self.__reader_thread = MptaReaderThread(probe)
        self.__is_connected = False

    def __del__(self):
        """
        Desctructor
        """
        try:
            self.__reader_thread.disconnect()
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            pass

    def set_output_file(self, path):
        """ Specify the path where log will be saved

        :type  path: string
        :param path: Path to the output log file
        """
        self.__reader_thread.set_output_file(path)

    def start(self):
        """ Start the logging.
        """
        if not self.__is_connected:
            self.__reader_thread.connect()
            self.__is_connected = True

        self.__reader_thread.start_record()

    def stop(self):
        """ Stop the logging.
        """
        self.__reader_thread.stop_record()

        if self.__is_connected:
            self.__reader_thread.disconnect()
            self.__is_connected = False

    def is_message_received(self, message, timeout):
        """ Check if a message is received

        :type  message: string
        :param message: message that we look for
        :type  timeout: int
        :param timeout: time limit where we expect to receive the message

        :return: message content if received, None else
        :rtype: String
        """
        return self.__reader_thread.is_message_received(message, timeout)

    def add_trigger_message(self, message):
        """ Trigger a message

        :type  message: string
        :param message: message to be triggered
        """
        self.__reader_thread.add_trigger_message(message)
        return

    def get_message_triggered_status(self, message):
        """ Get the status of a message triggered

        :type  message: string
        :param message: message triggered
        :return: Message status
        :rtype: string
        """
        return self.__reader_thread.get_message_triggered_status(message)

    def remove_trigger_message(self, message):
        return self.__reader_thread.remove_trigger_message(message)

    def reset(self):
        """ Reset the logger, can be used on log issue
        """
        # pylint: disable=E1101
        self.__reader_thread.disconnect()
        self.__reader_thread.stop()
        self.__reader_thread.start()
        self.__reader_thread.connect()
        # pylint: enable=E1101
