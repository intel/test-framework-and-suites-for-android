#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

try:
    # Try to load subprocess32
    import subprocess32 as subproc
except ImportError:
    # Else use std subprocess
    import subprocess as subproc
import time
from logging import ERROR, DEBUG
from Queue import Queue
from ProcessLineReaderWin import ProcessLineReaderWin
from AcsSubprocessBase import AcsSubprocessBase
from acs.ErrorHandling.AcsToolException import AcsToolException


class AcsSubprocessWin(AcsSubprocessBase):

    """
    Windows AcsSubprocess implementation
    """

    def __init__(self, command_line, logger, silent_mode=False,
                 stdout_level=DEBUG, stderr_level=ERROR, max_empty_log_time=60):
        """
        Class that will execute a command regardless the Host OS and return the result message

        :type  command_line: str
        :param command_line: Command to be run

        :type  logger: logger object
        :param logger: logger to be used to log messages

        :type  silent_mode: bool
        :param silent_mode: display logs in the logger

        :type  stdout_level: logger level
        :param stdout_level: logger level used to log stdout message

        :type  stderr_level: logger level
        :param stderr_level: logger level used to log stderr message

        :type  max_empty_log_time: int
        :param max_empty_log_time: max delay w/o log, after this delay a message will be displayed
        """
        super(AcsSubprocessWin, self).__init__(command_line, logger, silent_mode,
                                               stdout_level, stderr_level, max_empty_log_time)

    def _check_io(self, read_to_eof=False):
        """
        Method that will query stdout and stderr streams, log them if needed, and store them in internal queue

        :type  read_to_eof: bool
        :param read_to_eof: read to the end of stdout/stderr stream
        """
        if self._my_process:
            do_read = True
            while do_read:
                for io_name, io_ctx in self._readable.items():
                    io_lines = io_ctx["stream"].read_lines()
                    if io_lines is None:
                        io_ctx["stream"].stop_read()
                        del self._readable[io_name]
                    else:
                        for io_line in io_lines:
                            if not self._silent_mode:
                                self._logger.log(io_ctx["log_level"], io_line.rstrip("\n"))
                            self._last_log_time = time.time()
                            self._stdout_data.put_nowait(io_line.rstrip("\r"))

                if read_to_eof and self._readable:
                    # Still some readable and we request us to read to the eof
                    do_read = True
                else:
                    # Stop reading
                    do_read = False

    def _init_readable(self):
        """
        Method that will init stdout and stderr stream and bind associate log level
        """
        if self._my_process:
            # Create readable collection for select usage
            self._readable = {"stdout": {"stream": ProcessLineReaderWin("stdout",
                                                                        self._my_process,
                                                                        self._my_process.stdout),
                                         "log_level": self._stdout_level},
                              "stderr": {"stream": ProcessLineReaderWin("stderr",
                                                                        self._my_process,
                                                                        self._my_process.stderr),
                                         "log_level": self._stderr_level}}

    def _start_process(self):
        """
        Initialize subprocess execution
        """
        try:
            # Clear the queue (in case of second run)
            self._stdout_data = Queue()

            # Start the process
            self._my_process = subproc.Popen(self._command_line, shell=False,
                                             stdout=subproc.PIPE, stderr=subproc.PIPE,
                                             bufsize=1, universal_newlines=True)
        except OSError as os_error:
            if not self._silent_mode:
                self._logger.error("Cannot execute {0}".format(self._command_line))
            raise AcsToolException(AcsToolException.OPERATION_FAILED, "OSError: {0}".format(os_error))
