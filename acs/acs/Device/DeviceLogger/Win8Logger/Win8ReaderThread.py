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

import threading
import socket
from Win8WriterThread import Win8WriterThread


class Win8ReaderThread(object):

    """
    Class describing the thread used to read logs send by the Win8 DUT.
    """

    __SOCKET_TIMEOUT = 5.0
    """
    Socket timeout used when reading data from the socket.
    """

    def __init__(self, device_ip, port_number):
        """
        Constructor of Win8ReaderThread

        :type device_ip: string
        :param device_ip: Ip address of the targeted device

        :type port_number: int
        :param port_number: Port where the logger (running on the device) is
        listening for connection
        """

        # initialization of the variables.
        self.__ip_address = device_ip
        self.__port = port_number

        self.__reader_thread = None
        self.__socket = None
        self.__thread_alive = threading.Event()
        self.__thread_alive.set()

        # Creating a Win8WriterThread.
        self.__writer_thread = Win8WriterThread()

    def start(self):
        """
        Starts the Reader and Writer threads.
        Connects to the logger.
        And then starts listening to the logger.
        """
        self.__writer_thread.start()

        self.__reader_thread = threading.Thread(target=self.__run)
        self.__reader_thread.name = "Win8ReaderThread"

        self._connect()

        self.__reader_thread.start()

    def set_output_path(self, output_path):
        """
        Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self.__writer_thread.set_output_path(output_path)
        return

    def stop(self):
        """
        Disconnect the thread from the socket of the DUT logger.
        """
        try:
            self._disconnect()
        except Exception as ex:  # pylint: disable=W0703
            print "Error: %s" % str(ex)

    def _connect(self):
        """
        Opens the connection with the logger.
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.settimeout(self.__SOCKET_TIMEOUT)
        print "Trying to Connect..."
        self.__socket.connect((self.__ip_address, self.__port))
        print "Connected"

    def _disconnect(self):
        """
        Closes the connection with the logger.
        """
        # close gently the reader thread
        if self.__reader_thread.is_alive():
            self.__thread_alive.clear()
            self.__reader_thread.join(5)
        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()
        self.__socket = None
        # close gently the writer thread
        self.__writer_thread.stop()

    def __run(self):
        while self.__thread_alive.isSet():
            # Read the socket
            try:
                data = self.__socket.recv(8192)
                if data is not None:
                    self.__writer_thread.push(data)
            except socket.timeout:
                # no data has been received from the socket
                pass


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    log_reader = Win8ReaderThread("127.0.0.1", 8003)
    log_reader.start()
