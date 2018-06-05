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
:summary: this file implements the win8 logger
:since: 22/02/2012
:author: rbertolini
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
