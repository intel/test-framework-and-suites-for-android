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
:summary: This file implements MPTA logging
:since: 17/03/2011
:author: vtinelli
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
        except:
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
