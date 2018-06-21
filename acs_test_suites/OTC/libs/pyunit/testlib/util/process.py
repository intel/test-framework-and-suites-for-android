'''
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?

SPDX-License-Identifier: Apache-2.0
'''
import os
import time
import platform
import subprocess
import ctypes
import signal
import re
import tempfile


def killall(ppid_str):
    """
    Method description:
         Kill all children process according to parent process ID
    """
    os_version = platform.system()
    try:
        if os_version == "Linux" or os_version == "Darwin":
            ppid_str = str(ppid_str)
            pidgrp_array = []
            if not ppid_str.isdigit():
                return

            def getchildpids(ppid_str):
                """
                   Return a list of children process
                """
                query_command = "ps -ef | awk '{if ($3 == %s) print $2;}'" % str(ppid_str)
                result_pids = os.popen(query_command).read()
                result_pids = result_pids.split()
                return result_pids

            pidgrp_array.extend(getchildpids(ppid_str))
            for pid_id in pidgrp_array:
                pidgrp_array.extend(getchildpids(pid_id))
            # Insert self process ID to PID group list
            pidgrp_array.insert(0, ppid_str)
            while len(pidgrp_array) > 0:
                pid_id = pidgrp_array.pop()
                try:
                    os.kill(int(pid_id), signal.SIGKILL)
                except OSError, error:
                    pattern = re.compile('No such process')
                    match = pattern.search(str(error))
                    if not match:
                        print "[ Error: fail to kill pid_id: %s," \
                            " error: %s ]\n" % (int(pid_id), error)
        # kill for windows platform
        else:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(1, 0, int(ppid_str))
            kernel32.TerminateProcess(handle, 0)
    except OSError, error:
        pattern = re.compile('No such process')
        match = pattern.search(str(error))
        if not match:
            print "[ Error: fail to kill pid: %s, error: %s ]\n" \
                % (int(ppid_str), error)
    return None


def shell_command_nomsg(cmd, timeout=90):
    """Execute shell command without message"""
    cmd_open = subprocess.Popen(cmd, shell=True)
    if not cmd_open:
        return -1
    t_timeout = timeout
    tick = 3
    ret = None
    while True:
        time.sleep(tick)
        ret = cmd_open.poll()
        if ret is not None:
            break

        if t_timeout > 0:
            t_timeout -= tick

        if t_timeout <= 0:
            # timeout, kill command
            try:
                cmd_open.kill()
                cmd_open.wait()
            except OSError:
                pass
            ret = -1
            break
    return ret


def shell_command(cmd_str, timeout_second=90):
    """
    Method description:
        execute shell command, and return result in sync mode
    """
    tmp_process = subprocess.Popen(cmd_str,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    time_cnt_float = 0
    exit_code_int = None
    result_array = []
    while time_cnt_float < timeout_second:
        exit_code_int = tmp_process.poll()
        if exit_code_int is not None:
            break
        time_cnt_float += 0.2
        time.sleep(0.2)

    if exit_code_int is None:
        killall(tmp_process.pid)
        exit_code_int = -1
        result_array = []
    elif not cmd_str.endswith('&'):
        while True:
            tmp_line = tmp_process.stdout.readline()
            if not tmp_line or tmp_line.find('daemon started') >= 0:
                break
            result_array.append(tmp_line)
    return [exit_code_int, result_array]


def shell_command_ext(cmd="",
                      timeout=None,
                      stdout_file=None,
                      stderr_file=None,
                      callbk=None):
    """shell executor, return [exitcode, stdout/stderr]
       timeout: None means unlimited timeout
    """
    if stdout_file is None:
        stdout_file = tempfile.mktemp(prefix="shell_stdout_")

    if stderr_file is None:
        stderr_file = tempfile.mktemp(prefix="shell_stderr_")

    exit_code = None
    wbuffile1 = file(stdout_file, "w")
    wbuffile2 = file(stderr_file, "w")
    rbuffile1 = file(stdout_file, "r")
    rbuffile2 = file(stderr_file, "r")
    cmd_open = subprocess.Popen(args=cmd,
                                shell=True,
                                stdout=wbuffile1,
                                stderr=wbuffile2)
    rbuffile1.seek(0)
    rbuffile2.seek(0)
    while True:
        exit_code = cmd_open.poll()
        if exit_code is not None:
            break
        if callbk and callable(callbk):
            callbk(rbuffile1.read())
        if timeout is not None:
            timeout -= 0.2
            if timeout <= 0:
                exit_code = "timeout"
                killall(cmd_open.pid)
                time.sleep(2)
                break
        time.sleep(0.2)

    rbuffile1.seek(0)
    rbuffile2.seek(0)
    stdout_log = rbuffile1.read()
    stderr_log = rbuffile2.read()
    wbuffile1.close()
    wbuffile2.close()
    rbuffile1.close()
    rbuffile2.close()
    os.remove(stdout_file)
    os.remove(stderr_file)
    return [exit_code, stdout_log, stderr_log]
