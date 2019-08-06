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
import time

from acs.UtilitiesFWK.Utilities import run_local_command
from LogCatAnalyzerThread import LogCatAnalyzerThread
from LogCatWriterThread import LogCatWriterThread


class LogCatReaderThread():

    """ Logger based on logcat utility
    """

    def __init__(self, device_handle, logger, logcat_cmd_line, enable_writer=True, enable_acs_watchdog=True):

        # Log logger
        self._logger = logger

        # Device handle
        self._device = device_handle

        # Store logcat command line
        self._logcat_cmd_line = logcat_cmd_line

        # Reader thread stop condition
        self._stop_event = threading.Event()
        self._stop_event.set()

        # Analyzer
        self.__analyser_thread = LogCatAnalyzerThread(self._logger)

        # Writer
        self.__writer_thread = None
        if enable_writer:
            self.__writer_thread = LogCatWriterThread(self._logger)

        # ADB process
        self._adb_process = None
        self._adb_stdout = None

        self.__reader_thread = None
        self.__incomplete_frame = None
        self.__lock = threading.Lock()
        self.__do_reset = False
        self.__enable_watchdog = enable_acs_watchdog

    def __del__(self):
        # Stop the current adb process if any
        self.__stop_adb_process()

    def __stop_adb_process(self):
        try:
            if self._adb_process and self._adb_process.poll() is None:
                self._adb_process.terminate()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as proc_exception:
            self._logger.debug("Unable to kill adb process (%s)" % (str(proc_exception),))

    def set_output_path(self, output_path):
        """Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        if self.__writer_thread:
            self.__writer_thread.set_output_path(output_path)

    def stop(self):
        """ Stop the logcat threads
        """
        if not self._stop_event.is_set():
            if self.__reader_thread:
                try:
                    self._stop_event.set()
                    # Wait 5 seconds to complete the end of thread
                    self.__reader_thread.join(5)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except BaseException:
                    pass
                finally:
                    del self.__reader_thread
                    self.__reader_thread = None

            if self.__writer_thread:
                self.__writer_thread.stop()

            if self.__analyser_thread:
                self.__analyser_thread.stop()

            # Stop the current adb process if any
            self.__stop_adb_process()

    def start(self, retry=3):
        """ Start the reader thread
        """

        if self._stop_event.is_set():
            # Handle retry
            attempt = 0
            success = False
            while not success and attempt < retry:
                attempt += 1

                if self.__start_logcat_thread():
                    self.__analyser_thread.start()

                    if self.__writer_thread:
                        self.__writer_thread.start()

                    self.__reader_thread = threading.Thread(target=self.__run)
                    self.__reader_thread.name = "LogCatReaderThread: %s" % self._logcat_cmd_line
                    self.__reader_thread.daemon = True
                    self._stop_event.clear()
                    self.__reader_thread.start()
                    success = True
                else:
                    time.sleep(2)

            if not success and self._logger:
                self._logger.error("Cannot start the LogcatReader, connection with ADB server cannot be done")

    def __start_logcat_thread(self):
        cmd = self._device.format_cmd(self._logcat_cmd_line, True)
        self._adb_process, self._adb_stdout = run_local_command(cmd)
        return self._adb_process and self._adb_stdout

    def reset(self):
        self.__do_reset = True

    def __reset(self):
        """ Reset adb connection
        """

        self.__lock.acquire()

        if self._logger:
            self._logger.debug("Reset logcat reader thread")

        # kill previous adb process
        self.__stop_adb_process()

        self.__start_logcat_thread()

        self.__incomplete_frame = None

        self.__lock.release()

    def __run(self):
        """
        Start the Logcat reader thread
        """
        # Init ADB, Service
        self.__incomplete_frame = None
        wd_log_timeout_def = float(self._device.get_watchdog_log_time()) * 2
        t_0 = time.time()

        while not self._stop_event.is_set():

            if not self._stop_event.is_set() and self.__do_reset:
                self.__do_reset = False
                self.__reset()
                # Reinitialize watchdog timeout
                t_0 = time.time()

            if not self._stop_event.is_set() and self._adb_stdout and not self._adb_stdout.empty():
                # Reinitialize watchdog timeout
                t_0 = time.time()

                # read data from logcat
                logcat_data = self._adb_stdout.get_nowait()

                for line in logcat_data.splitlines(True):
                    if line and not self._stop_event.is_set():
                        if self.__incomplete_frame:
                            # We have incomplete frame, we assume that
                            # the end of the frame is the next received one
                            line = self.__incomplete_frame + line
                            self.__incomplete_frame = None

                        if line.endswith("\n"):
                            if line.rstrip("\n"):
                                # Push it for writing
                                if self.__writer_thread:
                                    self.__writer_thread.push(line)

                                # Push it for analyze
                                self.__analyser_thread.push(line)
                        else:
                            # Incomplete frame, keep it for next time
                            self.__incomplete_frame = line

            # Compute watchdog timeout
            wd_log_timeout = time.time() - t_0

            if self.__enable_watchdog and wd_log_timeout >= wd_log_timeout_def:
                if not self._stop_event.is_set():
                    if self._logger:
                        self._logger.error("Logcat reader watchdog timeout !")
                    self.__do_reset = True

    def add_trigger_message(self, message):
        self.__analyser_thread.add_trigger_message(message)

    def remove_trigger_message(self, message):
        self.__analyser_thread.remove_trigger_message(message)

    def get_message_triggered_status(self, message):
        return self.__analyser_thread.get_message_triggered_status(message)

    def reset_trigger_message(self, message):
        self.__analyser_thread.reset_trigger_message(message)

    def is_message_received(self, message, timeout):
        return self.__analyser_thread.is_message_received(message, timeout)

    def is_started(self):
        return not self._stop_event.is_set()
