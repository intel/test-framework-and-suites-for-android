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
:summary: This file implements the reader of PTI logs (opened in MPTA)
:since: 06/05/2011
:author: sfusilie
"""

import array
import select
import socket
import threading
import time

from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.Device.DeviceLogger.MptaLogger.MptaAnalyzerThread import MptaAnalyzerThread
from acs.Device.DeviceLogger.MptaLogger.MptaWriterThread import MptaWriterThread


class MptaReaderThread():

    def __init__(self, probe):
        # Writer
        self.__writer_thread = MptaWriterThread()
        self.__analyser_thread = MptaAnalyzerThread()

        # Var init
        self.__temp_data = []
        self.__probe = probe

        # Status
        self._s = None
        self._is_acq_running = 0

        # Messages to trigger
        self.__messages_to_trigger = {}

        # Message to received
        self.__message_to_receive = None
        self.__message_received = None
        self.__is_message_received = False

        # Lock object
        self.__lock_message_triggered = threading.RLock()
        self.__lock_message_received = threading.RLock()

        self.__log_file_mutex = threading.RLock()

        self.__acq_thread = None

    def _get_log_data(self):

        data = array.array("B", [0] * 1024 * 512)

        # Acquisition loop
        while self._is_acq_running:
            if self._s is not None:
                r, _, _ = select.select([self._s], [], [], 1)
                if r:
                    if self._s is not None:
                        # Get data from the socket
                        nbytes, _ = self._s.recvfrom_into(data)
                        if nbytes > 0:
                            limit = int(nbytes)

                            # Decode incoming messages
                            self.__log_file_mutex.acquire()
                            self._decode_ost(data[0:limit])
                            self.__log_file_mutex.release()

        del data

    def _decode_ost(self, data):
        offset = 0

        if len(self.__temp_data) > 0:
            data = self.__temp_data + data

        length = len(data)

        while length > 15:
            # check it's the beginning of a frame
            if (data[0 + offset] != 0x10) | (data[1 + offset] != 0x00) | (data[2 + offset] != 0x84):
                offset += 1
                length -= 1
                continue

            # Get frame length
            frame_length = data[3 + offset]
            frame_ext_offset = 0

            if frame_length == 0:
                # Use extended length
                # frame_length = data[4+offset] + data[5+offset]*math.pow(2, 8) + data[6+offset]*math.pow(2, 16)
                #                + data[7+offset]*math.pow(2, 24)
                # Hardcode math.pow values
                # We don't want to compute it at each iteration
                frame_length = data[4 + offset] + data[5 + offset] * 256 + data[
                    6 + offset] * 65536 + data[7 + offset] * 16777216
                frame_ext_offset = 4

            if (frame_length + 4 + frame_ext_offset) > length:
                #  incomplete data -> end the loop
                break

            # Get Master
            master = data[5 + offset]

            # no modem message
            if master != 72:
                # check if file exists
                if self._is_acq_running:
                    end = int(offset + 4 + frame_ext_offset + frame_length)
                    self.__writer_thread.push(data[offset:end])

                    buf = data[int(offset + 15 + frame_ext_offset):int(offset + 4 + frame_ext_offset + frame_length)]
                    self.__analyser_thread.push(buf)
                else:
                    pass

            length -= int(4 + frame_ext_offset + frame_length)
            offset += int(4 + frame_ext_offset + frame_length)

        # Store incomplete frame
        if length > 0:
            self.__temp_data = data[offset:(offset + length)]

    def set_output_file(self, filename):
        self.__writer_thread.set_output_file(filename)

    def connect(self):
        """ Connects to logger probe.

            probe: Probe name. Can be 'FIDO' or 'LTB'.
        """

        if self.__probe == "LTB":

            # establish tcp connection with LTB
            host = '127.0.0.1'  # Symbolic name meaning the local host
            port = 6666  # Arbitrary non-privileged port
            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self._s.connect((host, port))

        elif self.__probe == "FIDO":
            # establish tcp connection with FIDO
            host = '127.0.0.1'  # Symbolic name meaning the local host
            port = 7654  # Arbitrary non-privileged port
            self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._s.connect((host, port))

            # Send Reserve Data Channel command to Fido
            data_cmd = "DATA FidoTest TRACEBOX/0.0.0.0\r\n\r\n"
            self._s.send(data_cmd)
        else:
            error_msg = "MptaLoggerThread lib error in 'connect' - Unknown probe name"
            raise AcsConfigException(AcsConfigException.EXTERNAL_LIBRARY_ERROR, error_msg)

    def disconnect(self):
        """ Disconnects from logger probe.
        """
        if self._s is not None:
            self._s.shutdown(socket.SHUT_RDWR)
            self._s.close()
            time.sleep(1)
            self._s = None

    def start_record(self):
        """ Starts log acquisition.

            file_name: Name of the file where software logs will be stored.
        """

        # Init acq flag
        self._is_acq_running = 1

        # Launch log acquisiton thread
        try:
            self.__writer_thread.start()
            self.__analyser_thread.start()

            self.__acq_thread = threading.Thread(target=self._get_log_data)
            self.__acq_thread.name = "MptaReaderThread"
            self.__acq_thread.daemon = True
            self.__acq_thread.start()

        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            pass

    def stop_record(self):
        """ Stops log acquisition.
        """
        # flag to stop thread
        self._is_acq_running = 0
        if self.__acq_thread is not None:
            self.__acq_thread.join(10)
        del self.__temp_data
        self.__temp_data = []

        self.__writer_thread.stop()
        self.__analyser_thread.stop()

    def add_trigger_message(self, message):
        self.__analyser_thread.add_trigger_message(message)
        return

    def remove_trigger_message(self, message):
        self.__analyser_thread.remove_trigger_message(message)
        return

    def is_message_received(self, message, timeout):
        return self.__analyser_thread.is_message_received(message, timeout)

    def get_message_triggered_status(self, message):
        return self.__analyser_thread.get_message_triggered_status(message)
