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
import subprocess
import time
from testlib.utils.connections.local import Local as connection_local


def has_adb_serial(serial, device_state="device"):
    local_connection = connection_local()
    return local_connection.check_adb(serial=serial, device_state=device_state)


def get_adb_devices(device_state="device"):
    local_connection = connection_local()
    return local_connection.get_adb_devices(device_state=device_state)


def get_fastboot_devices():
    local_connection = connection_local()
    return local_connection.get_fastboot_devices()


def get_connected_android_devices():
    local_connection = connection_local()
    connected_devices = {}
    connected_devices['android'] = local_connection.get_adb_devices(device_state="device", charging=False)
    connected_devices['charge_os'] = local_connection.get_adb_devices(device_state="device", charging=True)
    connected_devices['ptest'] = local_connection.get_adb_devices(device_state="device", ptest=True)
    connected_devices['recovery'] = local_connection.get_adb_devices(device_state="recovery")
    connected_devices['fastboot'] = local_connection.get_fastboot_devices()
    connected_devices['crashmode'] = local_connection.get_crashmode_devices()
    return connected_devices


def get_device_boot_state(serial):
    connected_devices = get_connected_android_devices()
    for key in connected_devices:
        if serial in connected_devices[key]:
            return key
    return None


def is_device_connected(serial, except_charging=False):
    serials_list = []
    connected_android_devices = get_connected_android_devices()
    for key in connected_android_devices:
        if not except_charging or key != 'charge_os':
            serials_list.extend(connected_android_devices[key])
    return serial in serials_list


def has_fastboot_serial(serial, iterations=10):
    local_connection = connection_local()

    for i in range(iterations):
        (out, err) = local_connection.run_cmd(command="fastboot devices")
        if serial in out:
            return True
        time.sleep(1)
    return False


def wget(url,
         user=None, passwd=None,
         path_to_download=None, aditional_params=None,
         live_print=False,
         mode="sync"):

    local_connection = connection_local()

    wget_cmd = "wget "
    if user is not None:
        wget_cmd += " --user={0}".format(user)
    if passwd is not None:
        wget_cmd += " --password={0}".format(passwd)
    wget_cmd += " --no-check-certificate "
    if aditional_params is not None:
        wget_cmd += "{0} ".format(aditional_params)
    wget_cmd += url
    if path_to_download is not None:
        local_connection.cd(path=path_to_download)

    proc = subprocess.Popen(wget_cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    if mode == "async":
        return proc
    if live_print:
        while True:
            out = proc.stderr.readline()
            if "Not Found" in out:
                print out,
                return False
            if proc.poll() is not None:
                return proc
            print out,
    else:
        (stdout, stderror) = proc.communicate(input=None)
        return (stdout, stderror)


def folder_exists(path):
    return os.path.isdir(path)


def get_command_output(command, to_stderr=False):
    local_connection = connection_local()
    return local_connection.parse_cmd_output(cmd=command,
                                             to_stderr=to_stderr)


def can_ping_ip(ip):
    command = "ping -c 1 -q {0}".format(ip)
    out = get_command_output(command=command)
    return "1 packets transmitted, 1 received, 0% packet loss" in out


def get_ssh_command_output(command,
                           ssh_host,
                           ssh_user,
                           ssh_pass,
                           to_stderr=False):
    print "Running {0} on {1}@{2}".format(command, ssh_user, ssh_host)
    ssh_command = "sshpass -p {0} ssh {1}@{2} '{3}'".format(ssh_pass, ssh_user, ssh_host, command)
    return get_command_output(command=ssh_command,
                              to_stderr=to_stderr)


def get_ssh_fastboot_devices(ssh_host,
                             ssh_user,
                             ssh_pass,
                             with_platform=False):
    command = "fastboot devices"
    out = get_ssh_command_output(ssh_pass=ssh_pass,
                                 ssh_user=ssh_user,
                                 ssh_host=ssh_host,
                                 command=command)

    devices = []
    for line in out.split('\n'):
        if len(line) > 0:
            if with_platform:
                device = {}
                device['serial'] = line.split()[0]
                command = "fastboot -s {0} getvar product-string".format(device['serial'])
                out = get_ssh_command_output(ssh_pass=ssh_pass,
                                             ssh_user=ssh_user,
                                             ssh_host=ssh_host,
                                             command=command,
                                             to_stderr=True)
                device['platform'] = out.split('\n')[0].split('/')[-1]
            else:
                device = line.split()[0]
            devices.append(device)
    return devices


def get_ssh_adb_devices(ssh_host,
                        ssh_user,
                        ssh_pass,
                        device_state="device",
                        charging=False,
                        with_platform=False):
    command = "adb devices"
    out = get_ssh_command_output(ssh_pass=ssh_pass,
                                 ssh_user=ssh_user,
                                 ssh_host=ssh_host,
                                 command=command)
    devices = []
    for line in out.split('\n'):
        if "List" not in line and len(line) > 0 and device_state in line:
            serial = line.split()[0]
            command = "adb -s {0} shell getprop ro.bootmode".format(serial)
            out = get_ssh_command_output(ssh_pass=ssh_pass,
                                         ssh_user=ssh_user,
                                         ssh_host=ssh_host,
                                         command=command)
            if "charger" in out:
                if not charging:
                    continue
            else:
                if charging:
                    continue
            if with_platform:
                device = {}
                device["serial"] = serial
                command = "adb -s {0} shell getprop ro.product.device".format(serial)
                out = get_ssh_command_output(ssh_pass=ssh_pass,
                                             ssh_user=ssh_user,
                                             ssh_host=ssh_host,
                                             command=command)
                device["platform"] = out.strip()
            else:
                device = serial
            devices.append(device)
    return devices


def get_ssh_connected_android_devices(ssh_host,
                                      ssh_user,
                                      ssh_pass,
                                      with_platform=False):
    connected_devices = {}
    connected_devices['android'] = get_ssh_adb_devices(ssh_pass=ssh_pass,
                                                       ssh_user=ssh_user,
                                                       ssh_host=ssh_host,
                                                       device_state="device",
                                                       charging=False,
                                                       with_platform=with_platform)
    connected_devices['charge_os'] = get_ssh_adb_devices(ssh_pass=ssh_pass,
                                                         ssh_user=ssh_user,
                                                         ssh_host=ssh_host,
                                                         device_state="device",
                                                         charging=True,
                                                         with_platform=with_platform)
    connected_devices['recovery'] = get_ssh_adb_devices(ssh_pass=ssh_pass,
                                                        ssh_user=ssh_user,
                                                        ssh_host=ssh_host,
                                                        device_state="recovery",
                                                        with_platform=with_platform)
    connected_devices['fastboot'] = get_ssh_fastboot_devices(ssh_pass=ssh_pass,
                                                             ssh_user=ssh_user,
                                                             ssh_host=ssh_host,
                                                             with_platform=with_platform)
    return connected_devices


def get_ssh_hostname(ssh_host,
                     ssh_user,
                     ssh_pass):
    command = "hostname"
    out = get_ssh_command_output(ssh_pass=ssh_pass,
                                 ssh_user=ssh_user,
                                 ssh_host=ssh_host,
                                 command=command)
    return out.strip()


def delete_file_over_ssh(ssh_host,
                         ssh_user,
                         ssh_pass,
                         file_path):
    command = "rm {0}".format(file_path)
    get_ssh_command_output(ssh_pass=ssh_pass,
                           ssh_user=ssh_user,
                           ssh_host=ssh_host,
                           command=command)


def create_file_over_ssh(ssh_host,
                         ssh_user,
                         ssh_pass,
                         file_path):
    command = "touch {0}".format(file_path)
    get_ssh_command_output(ssh_pass=ssh_pass,
                           ssh_user=ssh_user,
                           ssh_host=ssh_host,
                           command=command)


def create_folder_structure_over_ssh(ssh_host,
                                     ssh_user,
                                     ssh_pass,
                                     folder_path):
    command = "mkdir -p {0}".format(folder_path)
    get_ssh_command_output(ssh_pass=ssh_pass,
                           ssh_user=ssh_user,
                           ssh_host=ssh_host,
                           command=command)
