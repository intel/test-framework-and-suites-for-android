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
# This particular import has been done to do a workaround for a python bug
# See the bottom of: http://code.google.com/p/modwsgi/wiki/ApplicationIssues
from time import strptime

from datetime import datetime


class LogCatWriterThread():

    def __init__(self, logger):
        # Output file
        self.__output_file_path = None
        self.__output_stream = None
        self.__start_writting = False

        # Writer thread stop condition
        self._stop_event = threading.Event()
        self._stop_event.set()

        # Internal buffer
        self.__queue = Queue()

        self.__writer_thread = None

        self._logger = logger

        # Delay to wait before processing new item in the queue
        self.writer_loop_delay = 0.1

    def set_output_path(self, output_path):
        """Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self.__output_file_path = output_path
        return

    def stop(self):
        """ Stop the writer thread
        """
        if not self._stop_event.is_set():
            if self.__writer_thread is not None:
                try:
                    self._stop_event.set()
                    self.__writer_thread.join(5)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except BaseException:
                    pass
                finally:
                    del self.__writer_thread
                    self.__writer_thread = None

    def start(self):
        """ Start the write thread
        """
        if self._stop_event.is_set():
            self._stop_event.clear()
            self.__writer_thread = threading.Thread(target=self.__run)
            self.__writer_thread.name = "LogCatWriterThread: %s" % self.__output_file_path
            self.__writer_thread.daemon = True
            self.__writer_thread.start()

    def push(self, line):
        """Push data in the internal queue

        :type  line: string
        :param line: data to be written
        """
        self.__queue.put_nowait(line)

    def is_time_format(self, test_str):
        """ Test if test_str contains a date formated like in logcat file
        """
        try:
            strptime(test_str, '%d-%m %H:%M:%S.%f')
            return True
        except (ValueError, AttributeError):
            return False

        except Exception as exc:
            if self._logger:
                self._logger.error("Unexpected exception in Logcat writer thread : %s" % (str(exc),))
            return False

    def write_line_in_logcat_file(self, line_logcat):
        self.__output_stream.write("%s - %s\n" % (time.strftime("host: %d/%m %H:%M:%S", time.localtime(time.time())),
                                                  line_logcat.rstrip("\r\n"),))
        self.__output_stream.flush()

    def __run(self):
        """ Runner thread method
        """
        last_log_date = datetime.min
        first_write = False
        skipping_log = False

        # Create the output file if output file was specified
        if self.__output_file_path:
            # Close it if needed
            if self.__output_stream and not self.__output_stream.closed:
                self.__output_stream.close()
            first_write = True

        self.__start_writting = True
        while not self._stop_event.is_set():
            while not self.__queue.empty():
                try:
                    line = self.__queue.get_nowait()
                    if len(line) > 0:
                        if first_write:
                            # create the file if it is the first
                            # time that there are logs
                            self.__output_stream = open(self.__output_file_path, "wb")
                            first_write = False
                        if self.__output_stream:
                            # extract the begining of the line
                            str_date = line[0:18]
                            # if the line begin by a date
                            if self.is_time_format(str_date):
                                # change string to date
                                log_date = datetime.strptime(str_date, '%d-%m %H:%M:%S.%f')

                                # compare the date of the line with these of
                                # last logcat recorded
                                if log_date > last_log_date:
                                    # log doesn t need to be skipped
                                    skipping_log = False

                                if (log_date >= last_log_date) and not skipping_log:
                                    # then line is logged in file
                                    self.write_line_in_logcat_file(line)
                                    last_log_date = log_date
                                else:
                                    # log_cat must be skipped
                                    skipping_log = True
                            else:
                                if not skipping_log:
                                    # lines without date are logged in file
                                    # if log are not skipped
                                    self.write_line_in_logcat_file(line)

                except Empty:
                    pass
            self._stop_event.wait(self.writer_loop_delay)

        # Close the output file
        if self.__output_stream and not self.__output_stream.closed:
            self.__output_stream.flush()
            self.__output_stream.close()

        return
