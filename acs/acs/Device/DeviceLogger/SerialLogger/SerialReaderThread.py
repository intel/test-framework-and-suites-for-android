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
:summary: This file is reading data from logcat process
:since: 06/05/2011
:author: sfusilie
"""
import threading
import time
from time import strftime

import serial

from acs.UtilitiesFWK.Utilities import Global
from SerialAnalyzerThread import SerialAnalyzerThread
from SerialWriterThread import SerialWriterThread


class SerialReaderThread():

    """
    Logger based on logcat utility
    """

    def __init__(self, phone_handle, logger):

        # Phone handle
        self._phone = phone_handle

        # Logger
        self._logger = logger

        # Analyzer
        self.__analyser_thread = SerialAnalyzerThread(self._logger)

        # Writer
        self.__writer_thread = SerialWriterThread(self._logger)

        self.__reader_thread = None

        # Reader thread stop condition
        self._stop_event = threading.Event()

        self._recursive_limit = 5

        self.__incomplete_frame = None
        # port configuration
        self.port = 0
        self.baudrate = 115200
        self.bytesize = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_TWO
        self.timeout = None
        self.__serial = None
        self.hardware_flow_control = None

    def configure(self, port, baudrate, bytesize,
                  parity, stopbits, timeout, hardware_flow_control):
        """ Com port configuration

        :type port: string
        :param port: Path to the com port (COM1 or /deb/ttyUSB0)
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
        :type hardware_flow_control: boot
        :param hardware_flow_control: com port hdw control
        """
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.hardware_flow_control = hardware_flow_control

    def __del__(self):
        if self.__serial is not None:
            try:
                self.__serial.close()
            except Exception as e:  # pylint: disable=W0703
                print e

    def stop(self):
        """ Stop the reader thread
        """
        self._stop_event.set()

        if self.__reader_thread is not None:
            try:
                self.__reader_thread.join(5)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception:  # pylint: disable=W0703
                pass
            finally:
                del self.__reader_thread
                self.__reader_thread = None

        self.__writer_thread.stop()
        self.__analyser_thread.stop()

    def start(self):
        """
        Start the reader thread
        """
        if self.__serial is None:
            try:
                self.__serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=self.bytesize,
                    parity=self.parity,
                    stopbits=self.stopbits,
                    timeout=self.timeout,
                    rtscts=self.hardware_flow_control,
                    dsrdtr=self.hardware_flow_control)
            except Exception as e:  # pylint: disable=W0703
                self._logger.error(str(e))
                return Global.FAILURE

            if self.__serial is not None and self.__serial.isOpen():
                self.__analyser_thread.start()
                self.__writer_thread.start()

                self.__reader_thread = threading.Thread(target=self.__run)
                self.__reader_thread.name = "SerialtReaderThread"
                self.__reader_thread.daemon = True
                self._stop_event.clear()
                self.__reader_thread.start()
                return Global.SUCCESS
            else:
                self._logger.error("serial port can't be opened")
                return Global.FAILURE
        else:
            self._logger.info("Logger already logging")
            return Global.SUCCESS

    def set_output_path(self, output_path):
        """Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self.__writer_thread.set_output_path(output_path)

    def __reset(self):
        """
        Reset serial connection
        """
        # Sleep to avoid flooding
        time.sleep(2)

        try:
            self.__serial.close()
            self.__serial.open()
        except Exception as ex:  # pylint: disable=W0703
            self._logger.error("Critical exception in serial thread on reset: %s",
                               str(ex))

    def __run(self):
        """
        Reader thread
        """
        # Init ADB, Service
        self.__incomplete_frame = ""
        while not self._stop_event.is_set():
            try:
                # Read start of the line
                data = self.__serial.read(1)
                # Get timestamp for the start of the line ...
                data_timestamp = strftime("[%Y-%m-%d_%Hh%M.%S]")
                # and read the rest of the line
                data += self.__serial.readline()
                data = data.strip()

                if data:
                    # Format line to push into serial log file
                    self.__incomplete_frame = "{0}{1}\n".format(data_timestamp, data)
            except Exception:  # pylint: disable=W0703
                self.__reset()

            if self.__incomplete_frame:
                # Push it for writing
                self.__writer_thread.push(self.__incomplete_frame)
                # Push it for analyze
                self.__analyser_thread.push(self.__incomplete_frame)
                # Reset received data
                self.__incomplete_frame = ""

        try:
            self.__serial.close()
        except Exception as ex:  # pylint: disable=W0703
            self._logger.error(str(ex))
        finally:
            self.__serial = None

    def add_trigger_message(self, message):
        """ Trigger a message

        :type  message: string
        :param message: message to be triggered
        """
        self.__analyser_thread.add_trigger_message(message)

    def remove_trigger_message(self, message):
        """ Remove Trigger

        :type  message: string
        :param message: Trigger to remove
        """
        self.__analyser_thread.remove_trigger_message(message)

    def get_message_triggered_status(self, message):
        """ Get the status of a message triggered

        :type  message: string
        :param message: message triggered

        :rtype: list of string
        :return: list of Message status
        """
        return self.__analyser_thread.get_message_triggered_status(message)

    def reset_trigger_message(self, message):
        """ Reset the messages triggered based on message pattern

        :type  message: string
        :param message: pattern to reset messages
        """
        self.__analyser_thread.reset_trigger_message(message)
