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

import datetime

import time
from Queue import Queue, Empty
from threading import Thread

from acs.UtilitiesFWK.Patterns import Cancel


def enqueue_output(out, queue):
    """
    Local function that will consume stdout stream and put the content in a queue

    :type   out: pipe
    :param  out: stdout stream

    :type   queue: Queue
    :param  queue: queue where each stdout line will be inserted
    """
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()


class AcsSubprocessBase(object):

    def __init__(self, command_line, logger, silent_mode, stdout_level, stderr_level, max_empty_log_time):
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
        self._command_line = command_line
        self._logger = logger
        self._silent_mode = silent_mode

        self._my_process = None
        self._log_level = None
        self._last_log_time = None
        self._stdout_level = stdout_level
        self._stderr_level = stderr_level
        self._stdout_data = Queue()
        self._max_empty_log_time = max_empty_log_time
        self._readable = []

        self._format_cmd()

    @property
    def _stdout_iter(self):
        """
        Create iterator based on the stdout queue content
        """
        while True:
            try:
                yield self._stdout_data.get_nowait()
            except Empty:
                break

    @property
    def command(self):
        """
        :return:    Properly formatted command to execute
        :rtype:     str
        """
        return self._command_line

    def _format_cmd(self):
        """
        Format command to be executed
        """
        # For retrocompatibilty we do not do anything if it is a list
        if not isinstance(self._command_line, list):
            self._command_line = str(self._command_line).encode('ascii', 'ignore')

    def _safe_kill(self):
        """
        Kill process and subprocess if psutil is available, else do a simple process kill
        """
        if self._my_process:
            try:
                import psutil

                main_proc = psutil.Process(self._my_process.pid)
                try:
                    # psutil version > v0.4.1
                    procs_to_rip = main_proc.get_children(recursive=True)
                except TypeError:
                    # psutil version <= v0.4.1
                    procs_to_rip = main_proc.get_children()

                procs_to_rip.append(main_proc)

                for proc_to_kill in procs_to_rip:
                    if psutil.pid_exists(proc_to_kill.pid) and proc_to_kill.is_running():
                        try:
                            proc_to_kill.terminate()
                        except psutil.NoSuchProcess:
                            continue

                _, proc_still_alive = psutil.wait_procs(procs_to_rip, timeout=1)
                for proc_to_atom in proc_still_alive:
                    if psutil.pid_exists(proc_to_atom.pid) and proc_to_atom.is_running():
                        try:
                            proc_to_atom.kill()
                        except psutil.NoSuchProcess:
                            continue
            except Exception:
                # Something wrong occurs with psutil
                # Stop the process as usual
                self._my_process.kill()

    def _finalize(self, execution_time, timeout, cancel=None):
        """
        Finalize process operation

        :type  execution_time: float
        :param execution_time: execution time of the command

        :type  timeout: float
        :param timeout: timeout of the command

        :type  cancel: Cancel
        :param cancel: the Cancel object of the command

        :return: return True if the process was properly ended
        :rtype: bool
        """
        result = False
        if self._my_process:
            poll_value = self._my_process.poll()
            if poll_value is not None:
                # Read latest data
                self._check_io(True)
                # Process created by Popen is terminated by system
                if poll_value == 0:
                    if not self._silent_mode:
                        self._logger.debug(
                            "Command normally terminated in {0}".format(datetime.timedelta(seconds=execution_time)))
                    result = True
                elif not self._silent_mode:
                    # Note: A negative value -N indicates that the child
                    # was terminated by signal N (Unix only).
                    err_msg = "Command {0} failed".format(self._command_line)
                    self._logger.debug("Command killed by system ({0})".format(poll_value))
                    self._logger.debug("*** COMMAND FAILED!\r")
                    self._logger.error(err_msg)
            else:
                # Process was not terminated until timeout or cancel
                try:
                    self._safe_kill()
                    # Read latest data
                    self._check_io(True)
                except OSError:
                    pass

                if cancel is not None and cancel.is_canceled:
                    if not self._silent_mode:
                        err_msg = "Command {0} was canceled after {1})!".format(self._command_line,
                                                                                datetime.timedelta(
                                                                                    seconds=execution_time))
                        self._logger.debug("*** CANCELED!\r")
                        self._logger.error(err_msg)
                    # execute callback if execution was canceled
                    if cancel.callback is not None:
                        cancel.callback()
                elif not self._silent_mode:
                    err_msg = "Command {0} has timeout after {1})!".format(self._command_line,
                                                                           datetime.timedelta(seconds=timeout))
                    self._logger.debug("*** TIMEOUT!\r")
                    self._logger.error(err_msg)
        return result

    def execute_async(self, get_stdout=True):
        """
        Launch asynchronized execution

        :type get_stdout: bool
        :param get_stdout: specify is stdout queue need to be created

        :rtype: tuple(process, Queue)
        """
        self._start_process()

        stdout_queue = None
        if get_stdout:
            stdout_queue = Queue()
            t = Thread(target=enqueue_output, args=(self._my_process.stdout, stdout_queue))
            t.name = "Thread exec: {0}".format(self._command_line)
            t.daemon = True  # thread dies with the program
            t.start()

        return self._my_process, stdout_queue

    def execute_sync(self, timeout, cancel=None):
        """
        Launch synchronized execution

        :type  timeout: int
        :param timeout: command execution timeout in sec

        :type  cancel: Cancel
        :param cancel: a Cancel object that can be used to stop execution, before completion or timeout(default None)

        :return: Execution status & output str (and optionally C{dict})
        :rtype: tuple(bool & str)
        """
        if not self._silent_mode:
            self._logger.debug("*** RUN: {0}, timeout={1}".format(self._command_line,
                                                                  datetime.timedelta(seconds=timeout)))
        if not cancel:
            cancel = Cancel()

        try:
            # set the begin time for information about duration (printed on stdout)
            begin_time = time.time()
            end_time = begin_time + float(timeout)
            self._start_process()
            self._init_readable()

            # retain the previous time for empty output duration
            self._last_log_time = begin_time

            exec_time = time.time()
            while not cancel.is_canceled and exec_time < end_time and self._my_process.poll() is None:
                # if no output for x seconds, print an info
                if int(time.time() - self._last_log_time) >= self._max_empty_log_time:
                    self._logger.info(
                        "Command execution on going for {0}".format(
                            datetime.timedelta(seconds=int(time.time() - begin_time))))
                    self._last_log_time = time.time()

                self._check_io()
                exec_time = time.time()

            # cleanup operations
            process_result = self._finalize(exec_time - begin_time, timeout, cancel)

        except KeyboardInterrupt:
            self._logger.warning("Command interruption!")
            raise KeyboardInterrupt("Command interruption!")

        finally:
            self._my_process = None

        return process_result, "\n".join(self._stdout_iter)
