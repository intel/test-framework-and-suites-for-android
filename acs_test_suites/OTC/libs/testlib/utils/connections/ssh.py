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

import time
import os
from testlib.base import base_utils

from testlib.utils.connections.connection import Connection


class SSH(Connection):
    __metaclass__ = base_utils.SingletonType
    pids = []
    host = ""
    prev_path = curr_path = ""
    env_vars = {}

    def __init__(self, **kwargs):
        raise "SSH wrapper not implemented"
        super(SSH, self).__init__()
        self.host = kwargs["host"]
        self.user = kwargs["user"]
        if "password" in kwargs:
            self.password = kwargs["password"]
        else:
            self.password = None
        self.prev_path = self.curr_path = "/home/{0}".format(self.user)
        self.env_vars["DISPLAY"] = "\":0.0\""
        self.ssh_open = False
        self.sftp_open = False
        if "sftp_enabled" in kwargs:
            self.sftp_enabled = kwargs["sftp_enabled"]
        else:
            self.sftp_enabled = True

        # get remote OS
        self.remote_OS = None
        cmd = "uname -a"
        self.open_connection()
        (stdin, stdout, stderr) = self.exec_command(cmd)
        stdout_str = stdout.read()
        if stdout_str.lower().find("cygwin") != -1:
            self.remote_OS = "windows"
        elif stdout_str.lower().find("linux") != -1:
            self.remote_OS = "linux"
        else:
            raise Exception("OS '{0}' not supported. \
                            Use only 'CYGWIN' or 'Linux'.".format(stdout_str))

    def open_connection(self):
        if not self.ssh_open:
            self.connect(self.host, username=self.user, password=self.password)
            self.ssh_open = True
        if self.sftp_enabled:
            if not self.sftp_open:
                self.sftp = self.open_sftp()
                self.sftp_open = True

    def close_connection(self, clean=False):
        if clean:
            my_pids = list(self.pids)
            for pid in my_pids:
                self.kill_command(pid)
        super(SSH, self).close()
        self.ssh_open = False
        if self.sftp_enabled:
            self.sftp.close()
            self.sftp_open = False

    def get_file(self, remote, local):
        # TODO: if one of the paths starts with ~ -> do not concatenate
        # get dir list
        if self.sftp_enabled is False:
            raise Exception("The ssh connection is not sftp enabled")
        node_type = str(self.sftp.lstat(remote))[0]
        if node_type == '-':
            print "****copying file>", remote, "->", local
            self._get_file(remote, local)
        elif node_type == 'l':
            # ignore links
            print "****ignoring link>", remote
        elif node_type == 'd':
            print "****entering DIR>", remote
            nodes = self.sftp.listdir(path=remote)
            if not os.path.exists(local):
                print "****creating DIR> " + local
                os.mkdir(local)
            else:
                print "****path already exists> " + local

            for node in nodes:
                remote_path = remote + "/" + node
                local_path = local + "/" + node
                print remote + "/" + node + " <> " + local + "/" + node
                self.get_file(remote_path, local_path)

    def put_file(self, local, remote):
        # get dir list
        if self.sftp_enabled is False:
            raise Exception("The ssh connection is not sftp enabled")
        nodes = None
        if os.path.isdir(local):
            # todo: test if remote is file; if yes -> error
            nodes = os.listdir(local)
            try:
                print "****creating DIR> " + remote
                self.sftp.mkdir(remote)
            except IOError:
                print "****path already exists> " + remote
            for node in nodes:
                remote_path = remote + "/" + node
                local_path = local + "/" + node
                print "****entering DIR>", local_path
                self.put_file(local_path, remote_path)
        else:
            # the parameter is a file or a link
            # TODO: test if remote is dir, if yes then add the file name to the remote value
            # TODO: test if file does not exist at all
            if os.path.islink(local):
                print "****ignoring link>", local
            elif os.path.isfile(local):
                print "****copying file>", local, "->", remote
                self._put_file(local, remote)

    def _get_file(self, remote, local):
        if self.remote_OS == "windows":
            # workaround for windows
            self.close_connection()
            self.open_connection()
            self.sftp = self.open_sftp()
        self.sftp.get(remote, local)
        if self.remote_OS == "windows":
            self.close_connection()
            self.open_connection()

    def _put_file(self, remote, local):
        if self.remote_OS == "windows":
            # workaround for windows
            self.close_connection()
            self.open_connection()
            self.sftp = self.open_sftp()
        self.sftp.put(remote, local)
        if self.remote_OS == "windows":
            self.close_connection()
            self.open_connection()

    def __get_pids(self):
        my_pids = []
        cmd = None
        if self.remote_OS == "windows":
            cmd = "ps -Wa|grep -v /usr/bin/ps"
        elif self.remote_OS == "linux":
            cmd = "ps ax|grep -v 'ps ax'"
        (stdin, stdout, stderr) = self.exec_command(cmd)
        ps_out = stdout.readlines()
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

    def exec_command(self, command, bufsize=-1, timeout=None):
        """
        Execute a command on the SSH server.  A new L{Channel} is opened and
        the requested command is executed.  The command's input and output
        streams are returned as python C{file}-like objects representing
        stdin, stdout, and stderr.

        @param command: the command to execute
        @type command: str
        @param bufsize: interpreted the same way as by the built-in C{file()}
                        function in python
        @type bufsize: int
        @return: the stdin, stdout, and stderr of the executing command
        @rtype: tuple(L{ChannelFile}, L{ChannelFile}, L{ChannelFile})

        @raise SSHException: if the server fails to execute the command
        """
        chan = None
        tries = 0
        while tries < 5:
            # sometimes on Windows EOFError exception is issued
            try:
                chan = self._transport.open_session()
                tries += 1
                break
            except EOFError:
                time.sleep(5)

        chan.settimeout(timeout)
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        return stdin, stdout, stderr

    def run_cmd(self, command, mode="sync", timeout=None):
        (out, err) = (None, None)
        if self.remote_OS == "windows":
            # windows
            out, err = self.run_cmd_win(command, mode=mode, timeout=timeout)
        elif self.remote_OS == "linux":
            # linux
            out, err = self.run_cmd_linux(command, mode=mode, timeout=timeout)
        else:
            raise Exception("OS '{0}' not supported. \
                            Use only 'CYGWIN' or 'Linux'.".format(out))
        return (out, err)

    def run_cmd_win(self, command, mode="sync", timeout=None):
        cmd = command
        if mode.lower() == "sync":
            # close and open connection as workaround
            # as it is not working properly on windows
            self.close_connection()
            self.open_connection()
            (stdin, stdout, stderr) = self.exec_command(cmd, timeout=timeout)
            return (stdout.read(), stderr.read())
        else:
            self.close_connection()
            self.open_connection()
            pids_before = self.__get_pids()
            (stdin, stdout, stderr) = self.exec_command(cmd, timeout=timeout)
            time.sleep(2)
            pids_after = self.__get_pids()
            pids = self.__get_command_pids(pids_before, pids_after)
            self.pids += pids
            return (pids, None)

    def run_cmd_linux(self, command, mode="sync", timeout=None):
        # change to the current path and set the env vars
        cmd_list = self.__get_list(self.env_vars)
        cmd_list += ["cd {0}".format(self.curr_path), command]

        cmd = ";".join(cmd_list)
        if cmd.find("sudo") != -1:
            cmd = "xhost + local:;" + cmd

        if mode.lower() == "sync":
            # add the eport display statement
            (stdin, stdout, stderr) = self.exec_command(cmd, timeout=timeout)
            return (stdout.read(), stderr.read())
        elif mode.lower() == "async":
            # get ps
            pids_before = self.__get_pids()

            # start command
            (stdin, stdout, stderr) = self.exec_command(cmd, timeout=timeout)
            time.sleep(2)
            # get ps and extract the PID of the command executed
            pids_after = self.__get_pids()

            # get the pid from the diff between before and after
            pids = self.__get_command_pids(pids_before, pids_after)
            self.pids += pids
            return (pids, None)
        else:
            raise Exception("Mode '{0}' not supported. \
                            Use only 'sync' or 'async'.".format(mode))

    def kill_command(self, pid):
        # try to kill command by PID
        if self.remote_OS == "linux":
            (stdin, stdout, stderr) = self.exec_command("kill -9 {0}".format(pid))
            self.pids.remove(pid)
        else:
            (stdin, stdout, stderr) = self.exec_command("kill.exe -f -9 {0}".format(pid))
            self.pids.remove(pid)

    def kill_all(self, pids):
        # try to kill command by PID
        for pid in pids:
            self.kill_command(pid)

    def cd(self, path):
        if path == "-":
            # swap the values in self.prev_path with self.curr_path
            self.prev_path, self.curr_path = self.curr_path, self.prev_path
        elif os.path.isabs(path):
            self.prev_path = self.curr_path
            self.curr_path = os.path.normpath(path)
        else:
            self.prev_path = self.curr_path
            self.curr_path = os.path.normpath(self.curr_path + "/" + path)

    def set_env(self, var_name, var_value):
        self.env_vars[var_name] = "\"{0}\"".format(var_value)

    def unset_env(self, var_name):
        if var_name in self.env_vars.keys():
            del self.env_vars[var_name]
