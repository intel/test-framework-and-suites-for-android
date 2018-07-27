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

from testlib.scripts.connections.local.local_step import step as local_step
from testlib.scripts.connections.local import local_utils
from testlib.base.base_step import step as base_step
# from testlib.base import base_utils

import os
import socket
from subprocess import Popen, PIPE
import time
import traceback
from zipfile import ZipFile


class change_dir(local_step):

    """ description:
            changes the current directory to the given one

        usage:
            change_dir(new_folder = "path/to/the/new/folder)

        tags:
            local, change, folder
    """
    def __init__(self, new_folder, **kwargs):
        self.new_folder = new_folder.rstrip("/")
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not change dir to {0}".format(self.new_folder))
        self.set_passm("Change directory to {0}".format(self.new_folder))

    def do(self):
        self.local_connection.cd(self.new_folder)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("pwd")
        if self.new_folder == "..":
            return True
            # TODO with OLDPWD
        else:
            return self.new_folder == stdout.strip()


class delete_file(local_step):

    """ description:
            deletes the given folder on the host

        usage:
            delete_folder(folder = "path/to/folder")

        tags:
            local, delete, folder
    """
    def __init__(self, file_name, **kwargs):
        self.file_name = file_name
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not delete file {0}".format(self.file_name))
        self.set_passm("Deleting file {0}".format(self.file_name))

    def do(self):
        self.local_connection.delete_file(self.file_name)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.file_name))
        return "No such file or directory" in stderr


class delete_folder(local_step):

    """ description:
            deletes the given folder on the host

        usage:
            delete_folder(folder = "path/to/folder")

        tags:
            local, delete, folder
    """
    def __init__(self, folder, **kwargs):
        self.folder = folder
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not delete folder {0}".format(self.folder))
        self.set_passm("Folder {0} deleted".format(self.folder))

    def do(self):
        self.local_connection.delete_folder(self.folder)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.folder))
        return "No such file or directory" in stderr


class delete_folder_content(local_step):

    """ description:
            deletes the content of the given folder on the host

        usage:
            delete_folder_content(folder = "path/to/folder")

        tags:
            local, delete, folder, content
    """
    def __init__(self, folder, **kwargs):
        self.folder = folder
        local_step.__init__(self, **kwargs)
        self.set_passm("Content of the folder {0} deleted".format(self.folder))
        self.set_errorm("", "Could not delete the content of the folder {0}".format(self.folder))

    def do(self):
        self.local_connection.delete_folder_content(self.folder)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.folder))
        return len(stdout) < 1


class create_folder(local_step):

    """ description:
            creates the given folder on the host at the given path

        usage:
            create_folder(path = "path/to/folder",
                          folder = "folder_name")

        tags:
            local, create, folder
    """
    def __init__(self, path, folder, **kwargs):
        self.folder = folder
        self.path = path
        local_step.__init__(self, **kwargs)
        self.folder_path = os.path.join(self.path, self.folder)
        self.set_passm("Create {0}".format(self.folder_path))
        self.set_errorm("", "Could not create folder {0}".format(self.folder_path))

    def do(self):
        self.local_connection.create_folder(self.folder_path)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.folder_path))
        return "No such file or directory" not in stderr


class copy_folder(local_step):

    """ description:
            copies the given folder to the given destination

        usage:
            copy_folder(path = "path/to/folder",
                        folder = "path/to/destination")

        tags:
            local, copy, folder
    """
    def __init__(self, folder, destination, **kwargs):
        self.folder = folder
        self.destination = destination
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not copy folder {0} to {1}".format(self.folder, self.destination))
        self.set_passm("Folder {0} copied to {1}".format(self.folder, self.destination))

    def do(self):
        command = "cp -r {0} {1}".format(self.folder, self.destination)
        self.local_connection.run_cmd(command)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.destination))
        return "No such file or directory" not in stderr


class copy_folder_content(local_step):

    """ description:
            copies the given folder content to the given destination

        usage:
            copy_folder(path = "path/to/folder",
                        folder = "path/to/destination")

        tags:
            local, copy, folder
    """
    def __init__(self, folder, destination, **kwargs):
        self.folder = folder
        self.destination = destination
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not copy folder {0}'s content to {1}".format(self.folder, self.destination))
        self.set_passm("Folder {0}'s content copied to {1}".format(self.folder, self.destination))

    def do(self):
        command = "cp {0}/* {1}".format(self.folder, self.destination)
        self.local_connection.run_cmd(command)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.destination))
        return "No such file or directory" not in stderr


class copy_file(local_step):

    """ description:
            copies the given file to the given destination

        usage:
            copy_folder(path = "path/to/file",
                        folder = "path/to/destination")

        tags:
            local, copy, folder
    """
    def __init__(self, file, destination, with_rename=False, **kwargs):
        self.file = file
        self.destination = destination
        self.with_rename = with_rename
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not copy file {0} to {1}".format(self.file, self.destination))
        self.set_passm("File {0} copied to {1}".format(self.file, self.destination))

    def do(self):
        command = "cp {0} {1}".format(self.file, self.destination)
        self.step_data = self.local_connection.run_cmd(command)

    def check_condition(self):
        stdout, stderr = self.local_connection.run_cmd("ls {0}".format(self.destination))
        if self.with_rename:
            file_name = self.destination.split("/")[-1]
        else:
            file_name = self.file.split("/")[-1]
        return file_name in stdout


class unzip_archive(local_step):

    """ description:
            unzips an archive to a given destination

        usage:
            unzip_archive(zip_path = "path/to/the/zip/archive",
                          unzip_destination = "path/to/the/destination")

        tags:
            local, zip, unzip, archive
    """
    def __init__(self, zip_path, unzip_destination, **kwargs):
        self.zip_path = zip_path
        self.unzip_destination = unzip_destination
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not unzip {0} to {1}".format(self.zip_path, self.unzip_destination))
        self.set_passm("{0} archive unzipped to {1}".format(self.zip_path, self.unzip_destination))

    def do(self):
        zip_file = ZipFile(self.zip_path)
        zip_file.extractall(self.unzip_destination)

    def check_condition(self):
        # TODO
        return True


class extract_tar(local_step):

    """ description:
            untars an archive to a given destination

        usage:
            extract_tar(tar_path = "path/to/the/zip/archive",
                        untar_path = "path/to/the/destination")

        tags:
            local, tar, archive
    """

    def __init__(self, tar_path, untar_path, **kwargs):
        self.tar_path = tar_path
        self.untar_path = untar_path
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not extract tar {0} to {1}".format(self.tar_path, self.untar_path))
        self.set_passm("{0} archive extracted to {1}".format(self.tar_path, self.untar_path))

    def do(self):
        change_dir(new_folder=self.untar_path)()
        self.step_data = self.local_connection.run_cmd(command="gzip -d < {0} | tar xvf -".format(self.tar_path))

    def check_condition(self):
        return len(self.step_data[1]) < 1


class wait_for_ping(local_step):

    """ description:
            checks the connection to the given ip for the given timeout
                until ping works

        usage:
            wait_for_ping(timeout = "seconds_while_ping_is_checked",
                          ip = "ip_of_the_host")

        tags:
            local, ping, network, ip, wait
    """
    def __init__(self, ip, timeout=30, **kwargs):
        self.ip = ip
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not ping {0} in {1} seconds".format(self.ip, self.timeout))
        self.set_passm("{0} pinged in {1} seconds".format(self.ip, self.timeout))

    def do(self):
        try:
            self.local_connection.wait_for_ping(self.ip, timeout=self.timeout)
        except Exception:
            print "{0}: Error waiting for ping - {1}".format(self.ip, traceback.format_exc())

    def check_condition(self):
        return self.local_connection.check_ping(self.ip)


class reboot_fastboot_bootloader(local_step):

    """ description:
            reboots the <serial> device into bootloader from fastboot

        usage:
            reboot_fastboot_bootloader(serial = serial)()

        tags:
            local, serial, reboot, android, fastboot
    """

    def __init__(self, serial, **kwargs):
        self.serial = serial
        local_step.__init__(self, **kwargs)

    def do(self):
        self.local_connection.run_cmd(command="fastboot -s {0} reboot bootloader".format(self.serial))

    def check_condition(self):
        return local_utils.has_fastboot_serial(serial=self.serial,
                                               iterations=20)


class wait_for_crashmode(local_step):

    """ description:

        usage:
            wait_for_crashmode(timeout = 5,
                          serial = serial)

        tags:
            local, serial, wait, android, fastboot
    """
    def __init__(self, serial, timeout=120, **kwargs):
        self.serial = serial
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Serial {0} not in crashmode".format(self.serial))
        self.set_passm("Serial {0} in crashmode".format(self.serial))

    def do(self):
        try:
            self.local_connection.wait_for_crashmode(self.serial, timeout=self.timeout)
        except Exception:
            print "{0}: Error waiting for crashmode - {1}".format(self.serial, traceback.format_exc())

    def check_condition(self):
        self.step_data = local_utils.has_adb_serial(serial=self.serial, device_state="bootloader")
        return self.step_data


class wait_for_fastboot(local_step):

    """ description:

        usage:
            wait_for_fastboot(timeout = "seconds_while_ping_is_checked",
                          serial = serial)

        tags:
            local, serial, wait, android, fastboot
    """
    def __init__(self, serial, timeout=120, **kwargs):
        self.serial = serial
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Serial {0} not in fastboot".format(self.serial))
        self.set_passm("Serial {0} in fastboot".format(self.serial))

    def do(self):
        try:
            self.local_connection.wait_for_fastboot(self.serial, timeout=self.timeout)
        except Exception:
            print "{0}: Error waiting for fastboot - {1}".format(self.serial, traceback.format_exc())

    def check_condition(self):
        self.step_data = local_utils.has_fastboot_serial(serial=self.serial, iterations=self.timeout)
        return self.step_data


class wait_for_cos(local_step):

    """ description:

        usage:
            wait_for_cos(timeout = 30,
                          serial = serial)

        tags:
            local, serial, wait, android, cos
    """
    def __init__(self, serial, timeout=120, **kwargs):
        self.serial = serial
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Serial {0} not in cos".format(self.serial))
        self.set_passm("Serial {0} in cos".format(self.serial))

    def do(self):
        self.result = False
        time_passed = 0
        while local_utils.get_device_boot_state(serial=self.serial) != "charge_os" and time_passed < self.timeout:
            time.sleep(2)
            time_passed += 2
        if time_passed < self.timeout:
            self.result = True

    def check_condition(self):
        return self.result


class wait_for_adb(local_step):

    """ description:

        usage:
            wait_for_adb(timeout = "seconds_while_ping_is_checked",
                          serial = serial)

        tags:
            local, serial, wait
    """
    def __init__(self, serial, timeout=120, device_state="device", **kwargs):
        self.serial = serial
        self.device_state = device_state
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Serial {0} not in adb".format(self.serial))
        self.set_passm("Serial {0} in adb".format(self.serial))

    def do(self):
        try:
            self.local_connection.wait_for_adb(self.serial, timeout=self.timeout, device_state=self.device_state)
        except Exception:
            print "{0}: Error waiting for adb - {1}".format(self.serial,
                                                            traceback.format_exc())

    def check_condition(self):
        self.step_data = local_utils.has_adb_serial(serial=self.serial, device_state=self.device_state)
        return self.step_data


class command(local_step):

    """ description:
            runs the given command on the host. to check the correct
                execution of the command, the stdout or stderr can be
                grepped for given string.
            environment variables cand be set via env_var dictionary

        usage:
            command(command = "command_to_be_executed",
                    <stdout_grep = "text_to_exist_in_stdout>,
                    <stderr_grep = "text_to_exist_in_stderr>)

        tags:
            local, command, grep, stdout, stderr
    """

    command = None
    check_command = None
    output_check_command = None

    def __init__(self, command, stdout_grep=None, stderr_grep=None, stdout_not_grep=None, stderr_not_grep=None,
                 env_vars=None, live_print=False, check_step=True, mode="sync", stderr_ok="", ignore_error=False,
                 **kwargs):
        self.command = command
        self.stdout_grep = stdout_grep
        self.stderr_grep = stderr_grep
        self.stdout_not_grep = stdout_not_grep
        self.stderr_not_grep = stderr_not_grep
        self.live_print = live_print
        self.check_step = check_step
        self.mode = mode
        self.stderr_ok = stderr_ok
        self.ignore_error = ignore_error
        local_step.__init__(self, **kwargs)
        if env_vars:
            for name, value in env_vars:
                self.local_connection.set_env(name, value)
        self.set_passm("Running {0}".format(self.command))
        self.set_errorm("", "Running {0}".format(self.command))

    def do(self):
        self.step_data = self.local_connection.run_cmd(command=self.command, live_print=self.live_print,
                                                       with_flush=self.with_flush, stderr_ok=self.stderr_ok,
                                                       ignore_error=self.ignore_error, mode=self.mode)

    def check_condition(self):
        if self.verbose:
            stds = "\n\tSTDOUT = \n\t {0} \tSTDERR =\n\t{1}\n".format(self.step_data[0], self.step_data[1])
        if self.stdout_grep:
            if self.verbose:
                error_mess = "\'{0}\' not in stdout - {1}".format(self.stdout_grep, stds)
                self.set_errorm(" ", "Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return self.stdout_grep in self.step_data[0]
        elif self.stdout_not_grep:
            if self.verbose:
                error_mess = "\'{0}\' not in stdout - {1}".format(self.stdout_grep, stds)
                self.set_errorm(" ", "Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return self.stdout_not_grep not in self.step_data[0]
        elif self.stderr_grep:
            if self.verbose:
                error_mess = "\'{0}\' not in stderr - {1}".format(self.stderr_grep, stds)
                self.set_errorm(" ", "Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return self.stderr_grep in self.step_data[1]
        elif self.stderr_not_grep:
            if self.verbose:
                error_mess = "\'{0}\' not in stderr - {1}".format(self.stderr_grep, stds)
                self.set_errorm(" ", "Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return self.stderr_not_grep not in self.step_data[1]
        elif self.check_step is False:
            return None
        return True


class ssh_command(local_step):

    """ description:
            executes command via ssh from the host
                ssh@ssh_user:ssh_pass@ssh_host some_command

        usage:
            command_via_ssh(command = "chmod +x " + some_sh_file,
                            ssh_host = "10.237.100.219",
                            ssh_user = "root")()

        tags:
            ssh, local, host, ddwrt, command

    """

    def __init__(self, command, ssh_host, ssh_user, ssh_pass=None, check_command=None, check_command_output=None,
                 live_print=False, stderr_ok="", ignore_error=False, with_flush=False, with_sudo=False, mode="sync",
                 **kwargs):
        local_step.__init__(self, **kwargs)
        self.command = command
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_host = ssh_host
        self.check_command = check_command
        self.check_command_output = check_command_output
        self.live_print = live_print
        self.stderr_ok = stderr_ok
        self.with_sudo = with_sudo
        self.with_flush = with_flush
        self.ignore_error = ignore_error
        self.mode = mode
        self.set_errorm("", "Command {0} was not executed succesfully".format(self.command))
        self.set_passm("Execute {}".format(self.command))

    def do(self):
        if self.ssh_pass:
            if self.with_sudo:
                command = "sshpass -p {0} ssh -t {1}@{2} 'echo {0} | sudo -S {3}'".format(self.ssh_pass,
                                                                                          self.ssh_user,
                                                                                          self.ssh_host, self.command)
            else:
                command = "sshpass -p {0} ssh {1}@{2} '{3}'".format(self.ssh_pass, self.ssh_user, self.ssh_host,
                                                                    self.command)
        else:
            command = "ssh {0}@{1} '{2}'".format(self.ssh_user, self.ssh_host, self.command)
        self.step_data = self.local_connection.run_cmd(command=command, live_print=self.live_print,
                                                       with_flush=self.with_flush, stderr_ok=self.stderr_ok,
                                                       ignore_error=self.ignore_error, mode=self.mode)

    def check_condition(self):
        if self.check_command is None:
            return True
        if self.ssh_pass:
            command = "sshpass -p {0} ssh {1}@{2} {3}".format(self.ssh_pass, self.ssh_user, self.ssh_host,
                                                              self.check_command)
        else:
            command = "ssh {0}@{1} {2}".format(self.ssh_user, self.ssh_host, self.check_command)
        sout, serr = self.local_connection.run_cmd(command=command)
        return self.check_command_output in sout


class scp_command(local_step):

    """ description:
            copies files from <local> to <remote> using scp
                scp /local/file ssh_user:ssh_pass@ssh_host:/remote/path

        usage:
            copy_file_via_ssh(local = some.file,
                              remote = ".",
                              ssh_host = "10.237.100.219",
                              ssh_user = "root")()

        tags:
            ssh, local, host, ddwrt, copy, scp

    """

    def __init__(self, local, remote, ssh_host, ssh_user, ssh_pass=None, live_print=False, stderr_ok="",
                 with_rename=False, **kwargs):
        local_step.__init__(self, **kwargs)
        self.local = local
        self.remote = remote
        self.ssh_user = ssh_user
        self.ssh_pass = ssh_pass
        self.ssh_host = ssh_host
        self.live_print = live_print
        self.stderr_ok = stderr_ok
        self.with_rename = with_rename
        self.set_errorm("", "{0} could not be copied to {1} on {1}".format(self.local, self.remote, self.ssh_host))
        self.set_passm("{0} copied to {1} on {2}".format(self.local, self.remote, self.ssh_host))

    def do(self):
        self.step_data = True
        if self.ssh_pass:
            command = "sshpass -p {0} scp {1} {2}@{3}:{4}".format(self.ssh_pass, self.local, self.ssh_user,
                                                                  self.ssh_host, self.remote)
        else:
            command = "scp {0} {1}@{2}:{3}".format(self.local, self.ssh_user, self.ssh_host, self.remote)
        self.local_connection.run_cmd(command=command, with_flush=self.with_flush, live_print=self.live_print,
                                      stderr_ok=self.stderr_ok)

    def check_condition(self):
        if not self.step_data:
            self.set_errorm("", "{0} is an invalid local path".format(self.local))
            return False
        if self.ssh_pass:
            command = "sshpass -p {0} ssh {1}@{2} ls {3}".format(self.ssh_pass, self.ssh_user, self.ssh_host,
                                                                 self.remote)
        else:
            command = "ssh {0}@{1} ls {2}".format(self.ssh_user, self.ssh_host, self.remote)
        sout, serr = self.local_connection.run_cmd(command=command)
        self.set_errorm("", serr)
        if self.with_rename:
            file_name = self.remote.split("/")[-1]
        else:
            file_name = self.local.split("/")[-1]
        return file_name in sout


class curl(base_step):

    """ description:
            executes curl command on the local host

        usage:
            curl(url = "url_to_be_opened",
                 args = "arguments_to_be_passed_to_curl,
                 grep_for = "text_to_be_search_in_the_output,)

        tags:
            local, command, curl, grep, stdout
    """

    def __init__(self, url, args="", grep_for=None, **kwargs):
        self.command = "curl {0} {1}".format(args, url)
        self.grep_for = grep_for
        base_step.__init__(self, **kwargs)
        if self.grep_for:
            self.set_passm("Curl for {0} checking \'{1}\'".format(url, self.grep_for))
            self.set_errorm("", "Failed curl for {0} checking \'{1}\'".format(url, self.grep_for))
        else:
            self.set_passm("Curl for {0}".format(url))
            self.set_errorm("", "Failed curl for {0}".format(url))

    def do(self):
        self.stdout, self.stderr = command(command=self.command, stdout_grep=self.grep_for)()

    def check_condition(self):
        self.step_data = self.stdout.strip()
        if self.grep_for:
            return self.grep_for in self.stdout and "error" not in self.stderr
        return "error" not in self.stderr


class wget(local_step):

    """ description:
            executes wget command on the local host

        usage:
            curl(url = "url_to_be_opened",
                 user = "user_needed_to_access_url",
                 passwd = "password_needed_to_access_url"
                 path_to_download = "path_to_download",)()

        tags:
            local, command, wget
    """

    def __init__(self, url, user=None, passwd=None, path_to_download=None, aditional_params=None, live_print=False,
                 mode="sync", **kwargs):
        local_step.__init__(self, **kwargs)
        self.url = url
        self.user = user
        self.passwd = passwd
        self.set_passm("{0} download done".format(url))
        self.set_errorm("", "Error! Cannot download {0}!".format(url))
        self.path_to_download = path_to_download
        self.aditional_params = aditional_params
        self.live_print = live_print
        self.mode = mode

    def do(self):
        self.step_data = local_utils.wget(url=self.url, user=self.user, passwd=self.passwd,
                                          path_to_download=self.path_to_download,
                                          aditional_params=self.aditional_params, live_print=self.live_print,
                                          mode=self.mode)

    def check_condition(self):
        if self.mode == "sync":
            stdout, stderr = self.local_connection.run_cmd("ls")
            return self.url.split('/')[-1] in stdout
        elif self.mode == "async":
            return True
        else:
            self.set_errorm("", "Invalid mode")
            return False


class kill_socket(local_step):

    """ description:
            kills the PID of a running program associated to a socket, identified by port number

        usage:
            kill_socket(port_number, process_name)

        tags:
            local, socket, pid
    """

    def __init__(self, port_number, process_name, **kwargs):
        self.port_number = port_number
        self.process_name = process_name
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not kill PID of " + self.process_name + " using port number " + self.port_number)
        self.set_passm("Killed PID of " + self.process_name + " using port number " + self.port_number)

    def do(self):

        p1 = Popen(['lsof', '-i', ":" + self.port_number], stdout=PIPE)
        p2 = Popen(["grep", self.process_name], stdin=p1.stdout, stdout=PIPE)

        output = p2.communicate()[0]
        output_list = output.split('\n')
        if len(output_list) > 0:
            pid_list = []
            for process_string in output_list[:-1]:
                process_line = process_string.split()
                pid_list.append(process_line[1])
            unique_pids = list(set(pid_list))
            for pid in unique_pids:
                pass
                # p3 = Popen(['kill', '-9', pid], stdout=PIPE)

    def check_condition(self):
        p1 = Popen(['lsof', '-i', ":" + self.port_number], stdout=PIPE)
        p2 = Popen(["grep", self.process_name], stdin=p1.stdout, stdout=PIPE)
        output = p2.communicate()[0]
        output_list = output.split('\n')
        if len(output_list[:-1]) == 0:
            return True
        else:
            return False


class check_socket_available(local_step):

    """ description:
            checks the availability of a socket
            fails if the verified socket is already used

        usage:
            local_steps.check_socket_availability(ip_address, port_number)()

        tags:
            local, socket, pid
    """

    def __init__(self, ip_address, port_number, **kwargs):
        self.port_number = port_number
        self.ip_address = ip_address
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Socket busy: " + self.ip_address + " : " + self.port_number)
        self.set_passm("Socket available: " + self.ip_address + " : " + self.port_number)

    def do(self):
        pass

    def check_condition(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(1)
            s.connect((self.ip_address, int(self.port_number)))
            s.close()
            return False
        except Exception:
            return True


class wait_until_disconnected(local_step):

    """ description:
            Waits until the device is no longer present in the
            devices list (the output of adb devices)
            Used when waiting for a shutdown or reboot

        usage:
            local_steps.wait_until_disconnected(timeout = "seconds_while_ping_is_checked",
                                                serial = serial)()

        tags:
            local, adb, wait, reboot
    """

    def __init__(self, serial, timeout=20, device_state="device", **kwargs):
        self.serial = serial
        self.device_state = device_state
        self.timeout = timeout
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "Serial {0} is still in adb".format(self.serial))
        self.set_passm("Serial {0} not adb - rebooting".format(self.serial))

    def do(self):
        count = 0
        while count < self.timeout:
            self.step_data = not local_utils.has_adb_serial(serial=self.serial, device_state=self.device_state)
            if self.step_data:
                break
            time.sleep(1)
            count += 1
        else:
            print "{0}: Error waiting for device to disconnect - {1}".format(self.serial, traceback.format_exc())

    def check_condition(self):
        return self.step_data
