#!/usr/bin/env python
"""
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
"""

import os
import re
import shutil
from subprocess import Popen, PIPE
import sys
import time

from testlib.utils.connections.connection import Connection
from testlib.base import base_utils


class Local(Connection):
    pids = []
    env_vars = {}

    def __init__(self, **kwargs):
        super(Local, self).__init__()
        self.env_vars["DISPLAY"] = "\":0.0\""

        # get local OS
        self.OS = None
        cmd = "uname -a"
        proc = self.__execute_command(cmd)
        (stdout, stderror) = proc.communicate(input=None)
        if stdout.lower().find("cygwin") != -1:
            self.OS = "windows"
        elif stdout.lower().find("linux") != -1:
            self.OS = "linux"
        else:
            raise Exception("OS '{0}' not supported. Use only \
                            'CYGWIN' or 'Linux'.".format(stdout))

    def open_connection(self):
        pass

    def close_connection(self):
        pass

    def get_file(self, remote, local):
        shutil.copy2(remote, local)

    def put_file(self, local, remote):
        shutil.copy2(local, remote)

    def __execute_command(self, cmd):
        command = cmd
        my_proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        """
        command = cmd.split()
        print command
        import os
        my_proc = Popen(command, stdout = PIPE, stderr = PIPE, env = os.environ)
        #p = Popen(command, stdout = PIPE, subprocess.PIPE, env = __env)
        """
        return my_proc

    def __get_pids(self):
        my_pids = []
        cmd = None
        if self.OS == "windows":
            cmd = "ps -Wa|grep -v /usr/bin/ps"
        elif self.OS == "linux":
            cmd = "ps ax|grep -v 'ps ax'"
        proc = self.__execute_command(cmd)
        (stdout, stderror) = proc.communicate(input=None)
        ps_out = stdout.splitlines()

        for line in ps_out:
            pid = (line.split())[0]
            if pid != "PID":
                my_pids += [pid]
        return my_pids

    def __get_command_pids(self, before, after):
        pids = []
        for pid in after:
            if pid not in before:
                pids += [pid]
        return pids

    def __get_list(self, dict_var):
        vars_list = []
        for (key, value) in dict_var.items():
            vars_list.append("export {0}={1}".format(key, value))
        return vars_list

    def wait_for_ping(self, ip, num_packets=1, timeout=5):
        with base_utils.timeout(seconds=timeout, error_message="Ping timedout"):
            while not self.check_ping(ip=ip, num_packets=num_packets):
                time.sleep(1)
                pass

    def wait_for_no_ping(self, ip, num_packets=1, timeout=5):
        with base_utils.timeout(seconds=timeout, error_message="Ping timedout"):
            while self.check_ping(ip=ip, num_packets=num_packets):
                time.sleep(1)
                pass

    def check_ping(self, ip, num_packets=1):
        cmd = "ping -c{0} {1}".format(num_packets, ip)
        out, err = self.run_cmd(cmd)
        return "{0} received".format(num_packets) in out

    def wait_for_fastboot(self, serial, timeout=5):
        with base_utils.timeout(seconds=timeout, error_message="Wait for fastboot timedout"):
            (out, err) = self.run_cmd(command="fastboot devices")
            while serial not in out:
                time.sleep(1)
                (out, err) = self.run_cmd(command="fastboot devices")

    def wait_for_crashmode(self, serial, timeout=5):
        device_state = "bootloader"
        with base_utils.timeout(seconds=timeout, error_message="Wait for crashmode timedout"):
            (out, err) = self.run_cmd(command="adb devices")
            while device_state not in out:
                time.sleep(1)
                (out, err) = self.run_cmd(command="adb devices")

    def get_fastboot_devices(self):
        cmd = "fastboot devices"
        out, err = self.run_cmd(command=cmd)
        devices = []
        for line in out.split('\n'):
            if len(line) > 0:
                devices.append(line.split()[0])
        return devices

    def get_crashmode_devices(self):
        cmd = "adb devices"
        out, err = self.run_cmd(command=cmd)
        devices = []
        for line in out.split('\n'):
            if len(line) > 0 and line.split()[-1] == "bootloader":
                devices.append(line.split()[0])
        return devices

    def check_fastboot(self, serial):
        cmd = "fastboot devices"
        out, err = self.run_cmd(command=cmd)
        return serial in out

    def wait_for_adb(self, serial, timeout=5, device_state="device"):
        with base_utils.timeout(seconds=timeout, error_message="adb device not found"):
            out = self.parse_cmd_output(cmd="adb devices", grep_for=serial)
            # (out,err) = self.run_cmd(command = "adb devices")
            while device_state not in out:
                time.sleep(1)
                # (out,err) = self.run_cmd(command = "adb devices")
                out = self.parse_cmd_output(cmd="adb devices", grep_for=serial)

    def get_adb_devices(self, device_state="device", charging=False, ptest=False):
        cmd = "adb devices"
        out = self.parse_cmd_output(cmd="adb devices", grep_for=device_state)
        devices = []
        for line in out.split('\n'):
            if "List" not in line and len(line) > 0:
                serial = line.split()[0]
                cmd = "adb -s {0} shell getprop ro.bootmode".format(serial)
                out, err = self.run_cmd(command=cmd)
                if "charger" in out:
                    if not charging:
                        continue
                else:
                    if charging:
                        continue
                if "ptest" in out:
                    if not ptest:
                        continue
                else:
                    if ptest:
                        continue
                devices.append(serial)
        return devices

    def check_adb(self, serial, device_state="device"):
        # cmd = "adb devices"
        out = self.parse_cmd_output(cmd="adb devices", grep_for=serial)
        return device_state in out

    def run_cmd(self,
                command,
                mode="sync",
                live_print=False,
                with_flush=False,
                stderr_ok="",
                ignore_error=False):
        (out, err) = (None, None)
        if self.OS == "windows":
            # windows
            out, err = self.run_cmd_win(command, mode="sync")
            return (out, err)
        elif self.OS == "linux":
            # linux
            if live_print:
                self.run_cmd_linux(command,
                                   mode=mode,
                                   live_print=live_print,
                                   with_flush=with_flush,
                                   stderr_ok=stderr_ok,
                                   ignore_error=ignore_error)
            else:
                out, err = self.run_cmd_linux(command,
                                              mode=mode)
                return (out, err)
        else:
            raise Exception("OS '{0}' not supported. \
                            Use only 'CYGWIN' or 'Linux'.".format(out))

    def run_cmd_win(self, command, mode="sync"):
        cmd = command

        if mode.lower() == "sync":
            # close and open connection as workaround
            # as it is not working properly on windows
            (stdin, stdout, stderr) = self.__execute_command(cmd)
            return (stdout.read(), stderr.read())
        else:
            # todo: add async on win using schtasks
            raise Exception("Mode '{0}' not supported for windows. \
                            Use 'sync' mode.".format(mode))

    def run_cmd_linux(self,
                      command,
                      mode="sync",
                      live_print=False,
                      with_flush=False,
                      stderr_ok="",
                      ignore_error=False):
        # change to the current path and set the env vars
        cmd_list = self.__get_list(self.env_vars)
        cmd_list += [command]
        cmd = ";".join(cmd_list)
        if mode.lower() == "sync":
            proc = self.__execute_command(cmd)
            if live_print:
                while True:
                    out = proc.stdout.readline()
                    if proc.poll() is not None:
                        __error = proc.stderr.read().strip()
                        if not ignore_error:
                            for line in __error.split("\n"):
                                assert line.strip() in stderr_ok, "Error encountered:\n{0}".format(__error)
                        return proc
                    print re.sub(r'[^\x00-\x7F] + ', ' ', out),
                    if with_flush:
                        sys.stdout.flush()
            else:
                (stdout, stderror) = proc.communicate(input=None)
                return (stdout, stderror)
        elif mode.lower() == "async":
            # get ps
            pids_before = self.__get_pids()
            # start command
            proc = self.__execute_command(cmd)
            time.sleep(2)
            # get ps and extract the PID of the command executed
            pids_after = self.__get_pids()
            # get the pid from the diff between before and after
            pids = self.__get_command_pids(pids_before, pids_after)
            self.pids += pids
            return (proc, None)
        else:
            raise Exception("Mode '{0}' not supported. \
                            Use only 'sync' or 'async'.".format(mode))

    def get_pids(self, pname):
        cmd = "ps -ef | grep {0}".format(pname)
        proc = self.__execute_command(cmd)
        pids = []
        for line in proc.stdout.readlines():
            pid = line.split()[1]
            pids.append(pid)
        return pids

    def get_pids_without_grep(self, pname):
        cmd = "ps -ef | grep -v grep | grep {0} -i --color=auto".format(pname)
        proc = self.__execute_command(cmd)
        pids = []
        for line in proc.stdout.readlines():
            pid = line.split()[1]
            pids.append(pid)
        return pids

    def kill_command(self, pid, self_pids=True):
        # proc = self.__execute_command("kill -9 {0}".format(pid))
        if self_pids:
            self.pids.remove(pid)

    def kill_all(self, pids, self_pids=True):
        for pid in pids:
            self.kill_command(pid, self_pids)

    def cd(self, path):
        os.chdir(path)

    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)

    def delete_folder(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)

    def delete_folder_content(self, path):
        if os.path.exists(path):
            self.run_cmd(command="rm -rf {0}/*".format(path))

    def create_folder(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def set_env(self, var_name, var_value):
        self.env_vars[var_name] = "\"{0}\"".format(var_value)

    def unset_env(self, var_name):
        if var_name in self.env_vars.keys():
            del self.env_vars[var_name]

    def parse_cmd_output(self,
                         cmd,
                         grep_for=None,
                         multiple_grep=None,
                         left_separator=None,
                         right_separator=None,
                         strip=False,
                         to_stderr=False):
        """
        By default gets the output from adb shell command
        Can grep for strings or cut for delimiters
        """
        stdout, stderr = self.run_cmd(cmd)
        if to_stderr:
            stdout = stderr
        string = base_utils.parse_string(stdout, grep_for=grep_for, multiple_grep=multiple_grep,
                                         left_separator=left_separator, right_separator=right_separator, strip=strip)
        return string
