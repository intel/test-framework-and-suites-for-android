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

from Queue import Queue, Empty
import threading
import time


class Win8WriterThread():

    """
    Class describing the thread used to write logs read by the
    Win8ReaderThread.
    """

    def __init__(self):
        """
        Constructor of Win8WriterThread
        """
        self.__output_file_path = None
        self.__output_stream = None

        self.__start_writing = False

        # creating the internal queue.
        self.__queue = Queue()

        self.__writer_thread = None

    def start(self):
        """
        Start the writer thread
        """
        self.__writer_thread = threading.Thread(target=self.__run)
        self.__writer_thread.name = "Win8WriterThread"
        self.__writer_thread.start()

    def stop(self):
        """
        Stop gently the writer thread
        """
        self.__start_writing = False
        self.__writer_thread.join(5)

    def set_output_path(self, output_path):
        """Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self.__output_file_path = output_path
        return

    def push(self, line):
        """
        Push data in the internal queue of the writer

        :type line: string
        :param line: data to be pushed in the internal queue
        """
        self.__queue.put_nowait(line)

    def __run(self):
        first_write = False
        # Create the output file if output file was specified
        if self.__output_file_path is not None:
            # Close it if needed
            if self.__output_stream is not None and not self.__output_stream.closed:
                self.__output_stream.close()
            first_write = True

        self.__start_writing = True
        while self.__start_writing:
            while not self.__queue.empty():
                try:
                    line = self.__queue.get_nowait()
                    if len(line) > 0:
                        if first_write:
                            # create the file if it is the first time that there are logs
                            self.__output_stream = open(self.__output_file_path, "wb")
                            first_write = False
                        if self.__output_stream is not None:
                            self.__output_stream.write(line)
                            self.__output_stream.flush()
                except Empty:
                    pass
            time.sleep(1)

        # Close the output file
        if self.__output_stream is not None and not self.__output_stream.closed:
            self.__output_stream.flush()
            self.__output_stream.close()

        return
