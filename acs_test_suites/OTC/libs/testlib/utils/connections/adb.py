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

import subprocess
import time
import os
import local
import connection
from testlib.base import base_utils
import signal


class AdbError(Exception):
    """Error for adb connection issues"""
    pass


class Adb(connection.Connection):
    """
    Singleton object to facilitate adb connection with the device
    Only one device per object

    serial  -- device serial
    port    -- the port for adb server running on the host

    verbose -- if True print some extra messages to STDOUT
    """

    __metaclass__ = base_utils.SingletonType
    serial = None
    port = None
    adb = "adb"
    cmd_prefix = []
    verbose = False
    local_conn = local.Local()

    def __init__(self, **kwargs):
        super(Adb, self).__init__()
        if "port" in kwargs:
            self.port = kwargs['port']
            if self.port:
                self.adb = "{0} -P {1}".format(self.adb, self.port)
                os.environ['ANDROID_ADB_SERVER_PORT'] = self.port
        if "serial" in kwargs:
            self.serial = kwargs['serial']
        if "verbose" in kwargs:
            self.verbose = kwargs['verbose']
        self.cmd_prefix = self.adb.split()
        self.cmd_prefix.extend(["-s", self.serial])

    def run_cmd(self, command, mode="sync", soutfile=None, dont_split=False, timeout=10, env={}, liveprint=True,
                ignore_error=False, cmd_type=None):
        """run adb shell command"""
        cmd = []
        cmd.extend(self.cmd_prefix)
        if cmd_type != "reboot":
            cmd.append('shell')
        if dont_split:
            cmd.append(command)
        else:
            cmd.extend(command.split())
        return self.run_cmd_linux(cmd, mode=mode, soutfile=soutfile, timeout=timeout, env=env, liveprint=liveprint,
                                  ignore_error=ignore_error)

    def run_cmd_linux(self, command, mode="sync", soutfile=None, timeout=10, env={}, liveprint=True,
                      ignore_error=False):
        """run linux bash command using Popen"""
        if self.verbose:
            print "Executing {0}".format(" ".join(command))
        __env = os.environ
        __env.update(env)
        p = None
        __err = 'Timeout {0} second(s) reached while executing "{1}"'.format(timeout, " ".join(command))
        if soutfile is None:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=__env)
        else:
            p = subprocess.Popen(command, stdout=open(soutfile, "wr"), stderr=subprocess.PIPE, env=__env)
        if mode.lower() == "sync":
            def handler(signum, frame):
                raise base_utils.TimeoutError(__err)

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            while True:
                if self.verbose and soutfile is None and liveprint:
                    print "STDOUT", p.stdout.read()
                    print "STDERR", p.stderr.read()
                if p.poll() is not None:
                    if not ignore_error:
                        __error = p.stderr.read().strip()
                        if __error != '' and "Warning" not in __error:
                            signal.alarm(0)
                            raise AssertionError("Error encountered:\n{0}".format(__error))
                    signal.alarm(0)
                    return p

        elif mode.lower() == "async":
            # Add below lines to fail in case run_cmd returns with failure
            # while starting to execute the command
            time.sleep(0.5)
            if p.poll() not in [None, 0]:
                if not ignore_error:
                    __error = p.stderr.read().strip()
                    # print __error
                    if __error != '' and "Warning" not in __error:
                        raise AssertionError(
                            "Error encountered:\n{0}".format(__error))
            return p
        else:
            raise AdbError("Mode '{0}' not supported. \
                            Use only 'sync' or 'async'.".format(mode))

    def open_connection(self):
        """connect to device if not already connected"""
        if not self.check_connected():
            cmd_string = "{0} connect {1}".format(self.adb, self.serial)
            self.run_cmd_linux(cmd_string.split(), timeout=10)
            time.sleep(1)
        return self.check_connected()

    def adb_root(self):
        """get adb root session"""
        cmd_string = "{0} -s {1} root".format(self.adb, self.serial)
        p = self.run_cmd_linux(cmd_string.split(), timeout=5)
        if "adbd is already running as root" not in p.stdout.read():
            time.sleep(5)
        return self.open_connection()

    def adb_remount(self):
        """remount /system and /vendor"""
        cmd_string = "{0} -s {1} remount".format(self.adb, self.serial)
        return self.run_cmd_linux(cmd_string.split(), timeout=10)

    def adb_disable_verity(self):
        """Disable verity in order to write in /system partition"""
        cmd_string = "{0} -s {1} disable-verity".format(self.adb, self.serial)
        return self.run_cmd_linux(cmd_string.split(), timeout=20)

    def kill_server(self):
        """kill adb server"""
        cmd_string = "{0} kill-server".format(self.adb)
        self.run_cmd_linux(cmd_string.split())
        time.sleep(1)

    def reboot_device(self, reboot_params="", ip_enabled=False, reboot_timeout=60):
        """reboot the device and check it is connected again"""
        if self.verbose:
            print "Rebooting .."
        ip = self.serial.split(":")[0]
        cmd = "reboot {0}".format(reboot_params)
        reboot_proc = self.run_cmd(cmd, mode="sync", cmd_type="reboot")
        if reboot_proc.poll() == 0:
            if ip_enabled:
                try:
                    self.local_conn.wait_for_no_ping(ip, timeout=reboot_timeout / 2)
                except base_utils.TimeoutError:
                    return False
                self.kill_server()
                time.sleep(1)
                try:
                    self.local_conn.wait_for_ping(ip, timeout=reboot_timeout)
                except base_utils.TimeoutError:
                    return False
                if reboot_params == "":
                    self.open_connection()
                return True
            else:
                waiting = 0
                while waiting < reboot_timeout:
                    time.sleep(2)
                    check = self.check_connected(device_state=reboot_params)
                    if check is None:
                        # timeout
                        return False
                    if check:
                        break
                    waiting += 2
                return waiting < reboot_timeout
        else:
            return False

    def check_connected(self, device_state=None):
        """check adb connection with the device"""
        if device_state == "recovery":
            return self.local_conn.check_adb(serial=self.serial,
                                             device_state=device_state)

        if device_state == "fastboot" or device_state == "bootloader":
            return self.local_conn.check_fastboot(serial=self.serial)

        try:
            self.run_cmd("ls sdcard", timeout=20)
        except base_utils.TimeoutError:
            return None
        except Exception:
            return False
        return True

    def close_connection(self):
        """discovnnect from the device"""
        cmd_string = "{0} disconnect {1}".format(self.adb, self.serial)
        self.run_cmd_linux(cmd_string.split(), timeout=1)

    def get_file(self, remote, local, timeout=60):
        """get file from the device"""
        cmd = []
        cmd.extend(self.cmd_prefix)
        cmd_string = "pull {0} {1}".format(remote, local)
        cmd.extend(cmd_string.split())
        p = self.run_cmd_linux(cmd, timeout=timeout, ignore_error=True, liveprint=False)
        err = p.stderr.read()
        out = p.stdout.read()
        assert "KB/s" in err or "100%" in out or (not err and not out), "Could not get file\n{0}".format(err)

    def put_file(self, local, remote, timeout=60):
        """push file to device"""
        cmd = []
        cmd.extend(self.cmd_prefix)
        cmd_string = "push {0} {1}".format(local, remote)
        cmd.extend(cmd_string.split())
        p = self.run_cmd_linux(cmd, timeout=timeout, ignore_error=True, liveprint=False)
        err = p.stderr.read()
        out = p.stdout.read()
        assert "KB/s" in err or "100%" in out or (not err and not out), "Could not push file\n{0}".format(err)

    def install_apk(self, apk, timeout=60):
        """install apk"""
        cmd = ["shell", "settings", "get", "secure", "install_non_market_apps"]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)
        (unknown_apps_state, err) = p.communicate()
        unknown_apps_state = unknown_apps_state.strip()
        cmd = ["shell", "settings", "get", "global", "package_verifier_enable"]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)
        (package_verifier_state, err) = p.communicate()
        package_verifier_state = package_verifier_state.strip()
        cmd = ["shell", "settings", "put", "secure", "install_non_market_apps", "1"]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)

        cmd = ["shell", "settings", "put", "global", "package_verifier_enable", "0"]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)

        cmd = []
        cmd.extend(self.cmd_prefix)
        cmd_string = "install {0}".format(apk)
        cmd.extend(cmd_string.split())
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)

        err = p.stderr.read()
        out = p.stdout.read()

        cmd = ["shell", "settings", "put", "secure", "install_non_market_apps", unknown_apps_state]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)

        cmd = ["shell", "settings", "put", "global", "package_verifier_enable", package_verifier_state]
        cmd = self.cmd_prefix + cmd
        p = self.run_cmd_linux(cmd,
                               timeout=timeout,
                               ignore_error=True,
                               liveprint=False)

        assert "Success" in out or "ALREADY_EXISTS" in out, "Could: not install apk {0}\Stdout: {1}\nStderr:  {" \
                                                            "2}".format(apk, out, err)

    def uninstall_apk(self, package, timeout=60):
        """install apk"""
        cmd = []
        cmd.extend(self.cmd_prefix)
        cmd_string = "uninstall {0}".format(package)
        cmd.extend(cmd_string.split())
        p = self.run_cmd_linux(cmd, timeout=timeout, ignore_error=True, liveprint=False)
        err = p.stderr.read()
        out = p.stdout.read()
        assert "Success" in out, "Could: not uninstall package {0}\nStdout: {1}\nStderr: {2}\n".format(package, out,
                                                                                                       err)

    def kill_command(self, pid):
        self.run_cmd("kill {0}".format(pid))

    def kill_all(self, pids):
        for pid in pids:
            self.kill_command(pid)

    def cd(self, path):
        raise NotImplementedError("Method not overwritten")

    def set_env(self, var_name, var_value):
        raise NotImplementedError("Method not overwritten")

    def unset_env(self, var_name):
        raise NotImplementedError("Method not overwritten")

    def load_CPU(self):
        """
        loads CPU
        returns the subprocess object
        """
        cmd = "cat /dev/urandom > /dev/null & \
cat /dev/urandom > /dev/null & cat /dev/urandom > /dev/null & \
cat /dev/urandom > /dev/null & cat /dev/urandom > /dev/null"
        return self.run_cmd(cmd, mode="async")

    def clear_logcat(self):
        """clears logcat"""
        self.run_cmd("logcat -c")

    def parse_cmd_output(self, cmd, grep_for=None, multiple_grep=None, left_separator=None, right_separator=None,
                         strip=False, dont_split=False, timeout=60, ignore_error=False):
        """
        By default gets the output from adb shell command
        Can grep for strings or cut for delimiters
        """
        # tmp file name should be uniq to allow getting output from
        # multiple devices at the same time

        tmp_file_name = "tmp_{0}_{1}_{2}".format("5037" if self.port is None else str(self.port), self.serial.split(
            ":")[0], str(int(round(time.time() * 1000000))))
        self.run_cmd(cmd, soutfile=tmp_file_name, timeout=timeout, dont_split=dont_split, ignore_error=ignore_error)
        with open(tmp_file_name, 'r') as f:
            string = f.read()
            string = base_utils.parse_string(string, grep_for=grep_for, multiple_grep=multiple_grep,
                                             left_separator=left_separator, right_separator=right_separator,
                                             strip=strip)
        os.remove(tmp_file_name)
        return string

    def parse_logcat(self, grep_for=None, left_separator=None, right_separator=None, strip=False):
        """parses logcat output"""
        cmd = "logcat -d"
        return self.parse_cmd_output(cmd, grep_for=grep_for, left_separator=left_separator,
                                     right_separator0=right_separator, strip=strip)

    def parse_dmesg(self, grep_for=None, left_separator=None, right_separator=None, strip=False):
        """parses dmesg output"""
        cmd = "dmesg"
        return self.parse_cmd_output(cmd, grep_for=grep_for, left_separator=left_separator,
                                     right_separator=right_separator, strip=strip)

    def parse_file(self, file_name, grep_for=None, left_separator=None, right_separator=None, strip=False):
        """parses the file located at file_name"""
        cmd = "cat {0}".format(file_name)
        return self.parse_cmd_output(cmd, grep_for=grep_for, left_separator=left_separator,
                                     right_separator=right_separator, strip=strip)

    def check_ping(self, ip):
        """checks ping to an ip from the device"""
        cmd = "ping -c1 {0}".format(ip)
        return "1 received" in self.parse_cmd_output(cmd)

    def check_interface_up(self, interface):
        """
        checks interface status from netcfg command

        usage:
            adb_conn.check_interface_up(wlan0)
        """
        return "UP" in self.parse_cmd_output("netcfg", grep_for=interface)

    def check_interface_down(self, interface):
        """
        checks interface status from netcfg command

        usage:
            adb_conn.check_interface_up(wlan0)
        """
        return "UP" not in self.parse_cmd_output("netcfg", grep_for=interface)

    def check_interface_has_ip(self, interface):
        """
        checks if interface has an IP address assigned

        usage:
            adb_conn.check_interface_has_ip(wlan0)
        """
        output = self.parse_cmd_output("netcfg", grep_for=interface)
        return output.split()[2].strip() != "0.0.0.0/0"

    def check_interface_has_this_ip(self, interface, ip, mask="24"):
        """
        checks if interface has the given IP address assigned
        and the given mask

        usage:
            adb_conn.check_interface_has_ip(wlan0)
        """
        output = self.parse_cmd_output("netcfg", grep_for=interface)
        return output.split()[2] == "{0}/{1}".format(ip, mask)

    def clear_app_cache(self):
        """clears app cache"""
        # TODO
        pass

    def get_prop(self, prop):
        """get prop from the device"""
        cmd = "getprop {0}".format(prop)
        return self.parse_cmd_output(cmd, strip=True).strip()

    def set_prop(self, prop, value):
        """set prop on the device"""
        self.run_cmd("setprop {0} {1}".format(prop, value))

    def pgrep(self, grep_for=""):
        """returns list of pids that match grep_for"""
        string = self.parse_cmd_output("ps", grep_for=grep_for)
        if self.verbose:
            print "________________________________________________"
            print string
            print "________________________________________________"
        line_separator = "\r\n"
        if line_separator not in string:
            line_separator = "\n"
        pids = []
        for line in string.split(line_separator):
            if grep_for in line:
                try:
                    pid = line.split()[1]
                    if pid.isdigit():
                        pids.append(pid)
                except Exception:
                    pass
        return pids

    def pgrep_common(self, args):
        """returns list of pids for give args.
                Works the same as 'pgrep' in android"""
        string = self.parse_cmd_output("pgrep " + args)
        if self.verbose:
            print "________________________________________________"
            print string
            print "________________________________________________"
        line_separator = "\r\n"
        if line_separator not in string:
            line_separator = "\n"
        output = []
        for line in string.split(line_separator):
            if line != "":
                output.append(line)
        return output

    def get_pid(self, grep_for):
        """return first pid to mach process name"""
        pids = self.pgrep(grep_for=grep_for)
        return None if len(pids) == 0 else pids[0]


if __name__ == "__main__":
    pass
