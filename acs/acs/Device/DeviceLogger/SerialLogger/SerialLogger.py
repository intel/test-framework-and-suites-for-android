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
:summary: This file expose the device interface IPhone
:since: 30/11/2011
:author: sfusilie, vgombertx, apairex
"""
import serial

from acs.Device.DeviceLogger.ILogger import ILogger
from acs.Core.Report.ACSLogging import LOGGER_FWK
from SerialReaderThread import SerialReaderThread
from acs.UtilitiesFWK.Utilities import Global


class SerialLogger(ILogger):

    """
    Logger based on serial port
    """

    def __init__(self, phone_handle):
        """Constructor

        :type phone_handle: IDevice
        :param phone_handle: device instance
        """
        self._logger = LOGGER_FWK
        self.__reader_thread = SerialReaderThread(phone_handle, self._logger)

    def configure(self, com_port="none", baudrate=115200,
                  bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                  stopbits=serial.STOPBITS_ONE, timeout=1,
                  hdw_flow_control=True):
        """ Com port configuration

        :type com_port: string
        :param com_port: Path to the com port (COM1 or /deb/ttyUSB0)
        :type baudrate: int
        :param baudrate: com port baud rate
        :type bytesize: int
        :param bytesize: com port byte size
        :type parity: string
        :param parity: com port parity
        :type stopbits: float
        :param stopbits: com port stop bits
        :type timeout: float
        :param timeout: com port timeout
        :type hdw_flow_control: boot
        :param hdw_flow_control: com port hdw control
        """
        self.__reader_thread.configure(com_port, baudrate, bytesize,
                                       parity, stopbits, timeout, hdw_flow_control)

        return Global.SUCCESS

    def set_output_file(self, path):
        """ Specify the path where log will be saved

        :type  path: string
        :param path: Path to the output log file
        """
        self.__reader_thread.set_output_path(path)
        return

    def start(self):
        """ Start the logging.
        """
        return self.__reader_thread.start()

    def stop(self):
        """ Stop the logging.
        """
        self.__reader_thread.stop()
        return

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

        :rtype: list of string
        :return: list of Message status
        """
        return self.__reader_thread.get_message_triggered_status(message)

    def remove_trigger_message(self, message):
        """ Remove Trigger

        :type  message: string
        :param message: Trigger to remove
        """
        return self.__reader_thread.remove_trigger_message(message)

    def reset_trigger_message(self, message):
        """ Reset the messages triggered based on message pattern

        :type  message: string
        :param message: pattern to reset messages
        """
        return self.__reader_thread.reset_trigger_message(message)


# Unit tests
if __name__ == "__main__":
    serialLogger = SerialLogger(None)
    serialLogger.set_output_file("c:\\temp\\serial.txt")
    serialLogger.configure("COM1", 115200)
    serialLogger.start()

    while True:
        pass
