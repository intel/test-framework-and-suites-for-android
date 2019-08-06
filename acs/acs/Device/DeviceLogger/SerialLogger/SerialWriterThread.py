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

from Queue import Queue
from time import strftime
import threading


class SerialWriterThread():

    """
    Logger based on serial utility
    """

    def __init__(self, logger):
        # Output file
        self._output_file_path = None

        # Reader thread stop condition
        self._stop_event = threading.Event()

        # Internal buffer
        self._queue = Queue()

        self.__writer_thread = None

        # Logger
        self._logger = logger

    def stop(self):
        """
        Stop the writer thread
        """
        self._stop_event.set()

        if self.__writer_thread is not None:
            try:
                self.__writer_thread.join(5)
            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException:
                pass
            finally:
                del self.__writer_thread
                self.__writer_thread = None
        return

    def start(self):
        """
        Start the write thread
        """
        self._stop_event.clear()
        self.__writer_thread = threading.Thread(target=self._run)
        self.__writer_thread.name = "SerialWriterThread"
        self.__writer_thread.daemon = True
        self.__writer_thread.start()

    def push(self, line):
        """
        Push data in the internal queue

        :type  line: string
        :param line: data to be written
        """
        self._queue.put_nowait(line)

    def set_output_path(self, output_path):
        """
        Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self._output_file_path = output_path

    def _run(self):
        """
        Runner thread method
        """
        # Create the output file if output file was specified
        if self._output_file_path is None:
            self._logger.info("No file specified for serial logger output")
            self._output_file_path = strftime("_%Y-%m-%d_%Hh%M.%S") + "_serial.log"
            self._logger.info("%s will be used." % self._output_file_path)

        while not self._stop_event.is_set():
            try:
                with open(self._output_file_path, "ab") as output_stream:
                    while not self._queue.empty():
                        try:
                            line = self._queue.get_nowait()
                            if len(line) > 0:
                                output_stream.write(line)
                                output_stream.flush()
                        except Exception as e:  # pylint: disable=W0703
                            self._logger.error(str(e))
            except (IOError, OSError, TypeError) as e:
                self._logger.error(str(e))
                break
