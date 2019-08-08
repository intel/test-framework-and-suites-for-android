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
import time
import traceback

from testlib.scripts.android.adb.adb_step import step as adb_step
from testlib.scripts.android.ui.ui_step import step as ui_step
from testlib.scripts.connections.local.local_step import step as local_step
from testlib.scripts.android.adb import adb_utils
from testlib.scripts.android import android_utils
from testlib.scripts.android.ui import ui_steps
from testlib.scripts.android.ui import ui_utils
from testlib.scripts.connections.local import local_steps
from testlib.scripts.connections.local import local_utils
from testlib.base.base_step import step as base_step
from testlib.base import base_utils
from testlib.scripts.android.adb.adb_utils import Sqlite


class connect_device(adb_step):

    """ description:
            connect to device and check connection. you should pass the
                serial (ip:5555) and, optional, the adb port

        usage:
            connect_device(serial = "10.237.112.157:5555",
                port = "17000")

        tags:
            adb, connect
    """
    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        if self.adb_connection.serial:
            self.set_errorm("", "adb connection could not be established for device: {0}".format(
                self.adb_connection.serial))
            self.set_passm("serial = {0}".format(self.adb_connection.serial))
        else:
            self.set_errorm("", "adb connection could not be established")
            self.set_passm("adb connection established")

    def do(self):
        self.adb_connection.open_connection()

    def check_condition(self):
        return self.adb_connection.check_connected()


class disconnect_device(adb_step):

    """ description:
            disconnect from device and check connection.

        usage:
            disconnect_device(serial = "10.237.112.157:5555",
                port = "17000")

        tags:
            adb, connect
    """
    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "adb connection could not be established for device: {0}".format(
            self.adb_connection.serial))
        self.set_passm("serial = {0}".format(self.adb_connection.serial))

    def do(self):
        self.adb_connection.close_connection()

    def check_condition(self):
        return not self.adb_connection.check_connected() or "." not in self.serial


class root_connect_device(adb_step):

    """ description:
            connect to device as root and check connection. you should
                pass the serial (ip:5555) and, optional, the adb port

        usage:
            root_connect_device(serial = "10.237.112.157:5555",
                port = "17000")

        tags:
            adb, root, connect
    """
    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.set_errorm("",
                        "adb root connection could not be established for device: {0}".format(
                            self.adb_connection.serial))

    def do(self):
        self.adb_connection.adb_root()

    def check_condition(self):
        return self.adb_connection.check_connected()


class remount(adb_step):

    """ description:
            Remounts the /system and /vendor (if present) partitions on the device read-write

        usage:
            adb_steps.remount()()

        tags:
            adb, remount, system
    """
    def __init__(self, should_remount=False, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.outcome = "remount "
        if should_remount:
            self.outcome += "succeeded"
        else:
            self.outcome += "failed"
        self.set_errorm("",
                        "adb remount failed for device: {0}".format(self.adb_connection.serial))

    def do(self):
        self.step_data = self.adb_connection.adb_remount().stdout.read()

    def check_condition(self):
        return self.outcome in self.step_data


class kill_server(adb_step, local_step):

    """ description:
            kills the adb server on the host

        usage:
            kill_server()

        tags:
            adb, kill, server
    """
    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "adb server could not be killed")

    def do(self):
        self.adb_connection.kill_server()

    def check_condition(self):
        adb_pids = self.local_connection.get_pids_without_grep("adb")
        return len(adb_pids) == 0


class kill_process(adb_step):

    """ description:
            kills the adb server on the host

        usage:
            kill_process(process_name = "mediaserver")

        tags:
            adb, kill, server
    """

    def __init__(self, process_name, timeout=10, with_reboot=False, reboot_timeout=20, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.process_name = process_name
        self.set_errorm("", "Cannot kill process {0}".format(process_name))
        self.set_passm("{0} killed".format(process_name))
        self.timeout = timeout
        self.with_reboot = with_reboot
        self.reboot_timeout = reboot_timeout

    def do(self):
        self.process_pid = self.adb_connection.get_pid(self.process_name)

        if self.process_pid:
            command(serial=self.serial,
                    command="kill {0}".format(self.process_pid))()
            time.sleep(self.timeout)

    def check_condition(self):
        if self.with_reboot:
            time_passed = 0
            while local_utils.has_adb_serial(serial=self.serial) and self.reboot_timeout > time_passed:
                time.sleep(1)
                time_passed += 1
            self.set_passm("Process {0} killed and the device rebooted!".format(self.process_name))
            self.set_errorm("", "Process {0} killed, but the device was not rebooted in {1}!".format(
                self.process_name, self.reboot_timeout))
            return self.reboot_timeout > time_passed
        process_info = self.adb_connection.parse_cmd_output(cmd="ps", grep_for=self.process_name)
        if self.process_pid:
            self.step_data = self.process_pid not in process_info
            return self.step_data
        return None


class reboot(adb_step, local_step):

    """ description:
            restarts the device via adb. you can pass paramters to the
                reboot operation (recovery, flash, ...). after
                reboot_timeout is exceeded, if ping is not established,
                the step reports FAIL

        usage:
            reboot(command = "recovery", reboot_timeout = 200)

        tags:
            adb, reboot, fastboot, repair
    """
    def __init__(self,
                 command="",
                 reboot_timeout=120,
                 ip_enabled=False,
                 no_ui=False,
                 disable_uiautomator=False,
                 boot_to_Android=True,
                 pin=None,
                 safe_mode=False,
                 **kwargs):
        adb_step.__init__(self, **kwargs)
        local_step.__init__(self, **kwargs)
        self.reboot_timeout = reboot_timeout
        self.command = command
        self.pin = pin
        self.ip_enabled = ip_enabled
        self.boot_to_Android = boot_to_Android
        self.no_ui = no_ui
        self.disable_uiautomator = disable_uiautomator
        self.safe_mode = safe_mode
        if self.ip_enabled:
            self.ip = self.serial.split(":")[0]
        self.set_errorm("", "adb reboot did not succeed for {0}".format(self.serial))
        self.set_passm("adb reboot performed {0}".format(self.serial))

    def do(self):
        if self.safe_mode:
            root_connect_device(serial=self.serial)()
            self.adb_connection.set_prop("persist.sys.safemode", 1)
        self.step_data = self.adb_connection.reboot_device(reboot_params=self.command,
                                                           reboot_timeout=self.reboot_timeout,
                                                           ip_enabled=self.ip_enabled)

    def check_condition(self):
        if self.step_data is False:
            return False
        if not self.ip_enabled and len(self.command) == 0:
            local_steps.wait_for_adb(serial=self.serial)()
            if self.no_ui is True:
                return True
            if self.pin:
                ui_ok = True
                wait_for_ui(serial=self.serial, disable_uiautomator=self.disable_uiautomator,
                            boot_to_Android=self.boot_to_Android, pin=self.pin)()
            else:
                ui_ok = wait_for_ui(serial=self.serial, disable_uiautomator=self.disable_uiautomator)()
            print "[ {0} ]: UI is loaded: {1}".format(self.serial, ui_ok)
            return ui_ok
        elif self.command == "fastboot" or self.command == "bootloader":
            time.sleep(30)
            self.set_passm("Device {0} is now in fastboot.".format(self.serial))
            self.set_errorm("", "Device {0} did not boot in fastboot.".format(self.serial))
            return local_utils.has_fastboot_serial(serial=self.serial)
        elif self.command == "crashmode":
            self.set_passm("Device {0} is now in crashmode.".format(self.serial))
            self.set_errorm("", "Device {0} did not boot in crashmode.".format(self.serial))
            return local_steps.wait_for_crashmode(serial=self.serial, timeout=60)()
        try:
            self.local_connection.wait_for_ping(self.ip, timeout=self.reboot_timeout)
        except base_utils.TimeoutError:
            return False
        return True


class reboot_recovery(adb_step):

    """ description:
            restarts the device into recovery mode via adb

        usage:
            adb_steps.reboot_recovery(serial = serial)

        tags:
            adb, recovery, reboot
    """

    def __init__(self, timeout=60, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "adb reboot recovery did not succeed")
        self.set_passm("rebooted to recovery")
        self.timeout = timeout

    def do(self):
        self.step_data = self.adb_connection.reboot_device(reboot_params="recovery", reboot_timeout=self.timeout,
                                                           ip_enabled=False)

    def check_condition(self):
        return local_steps.wait_for_adb(serial=self.serial, timeout=self.timeout, device_state="recovery")()


class reboot_ptest(adb_step):

    """ description:
            restarts the device into ptest mode via adb

        usage:
            adb_steps.reboot_ptest(serial = serial)()

        tags:
            adb, recovery, reboot, ptest
    """

    def __init__(self, timeout=30, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "adb reboot ptest did not succeed")
        self.set_passm("rebooted to ptest")
        self.timeout = timeout

    def do(self):
        self.step_data = self.adb_connection.reboot_device(reboot_params="ptest",
                                                           reboot_timeout=self.timeout,
                                                           ip_enabled=False)
        local_steps.wait_for_adb(serial=self.serial,
                                 timeout=self.timeout,
                                 device_state="device")()

    def check_condition(self):
        return "ptest" in local_utils.get_device_boot_state(serial=self.serial)


class reboot_ptest_clear(adb_step):

    """ description:
            when in ptest, restarts the device into normal mode via adb

        usage:
            adb_steps.reboot_ptest_clear(serial = serial)()

        tags:
            adb, recovery, reboot, ptest
    """

    def __init__(self, timeout=600, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "adb reboot ptest_clear did not succeed")
        self.set_passm("rebooted out of ptest")
        self.timeout = timeout

    def do(self):
        self.step_data = self.adb_connection.reboot_device(reboot_params="ptest_clear",
                                                           reboot_timeout=self.timeout,
                                                           ip_enabled=False)
        local_steps.wait_for_adb(serial=self.serial,
                                 timeout=self.timeout,
                                 device_state="device")()
        wait_for_ui_processes(serial=self.serial)()

    def check_condition(self):
        return "ptest" not in local_utils.get_device_boot_state(serial=self.serial)


class wait_for_ui_processes(adb_step):

    """ description:
            waits for the homepage to appear on the DUT
            it performs startup wizard, accepts telemetry and welcome

        usage:
            wait_for_ui(timeout = 120)

        tags:
            adb, reboot, ui
    """
    def __init__(self, timeout=1800, **kwargs):
        self.timeout = timeout
        self.wait_step = 5
        adb_step.__init__(self, **kwargs)
        self.set_passm("UI processes on the device {0} are alive in less than {1} seconds".format(self.serial,
                                                                                                  self.timeout))
        self.set_errorm("", "UI processes on the device {0} ware not alive in less than {1} seconds".format(
            self.serial, self.timeout))

    def do(self):
        waiting = 0
        while waiting < self.timeout:
            try:
                if local_utils.has_adb_serial(serial=self.serial) and\
                        self.adb_connection.get_pid("com.android.systemui") and \
                        adb_utils.is_prop_set(serial=self.serial, prop="dev.bootcomplete", value="1") and \
                        adb_utils.is_prop_set(serial=self.serial, prop="sys.boot_completed", value="1") and \
                        adb_utils.is_prop_set(serial=self.serial, prop="init.svc.bootanim", value="stopped"):
                    break
            except Exception:
                print "[ {0} ]: Error waiting for ui - {1}".format(self.serial, traceback.format_exc())
            time.sleep(self.wait_step)
            waiting += self.wait_step
        self.step_data = True
        if waiting >= self.timeout:
            print "[ {0} ]: Timeout waiting for UI processes".format(self.serial)
            self.step_data = False

    def check_condition(self):
        return self.step_data


class wait_for_ui(adb_step):

    """ description:
            waits for the homepage to appear on the DUT
            it performs startup wizard, accepts telemetry and welcome

        usage:
            wait_for_ui(timeout = 120)

        tags:
            adb, reboot, ui
    """
    def __init__(self, timeout=1800, disable_uiautomator=False, pin=None, boot_to_Android=True,
                 sim_pin_enabled=False, **kwargs):
        self.timeout = timeout
        self.wait_step = 5
        self.disable_uiautomator = disable_uiautomator
        self.boot_to_Android = boot_to_Android
        self.pin = pin
        self.sim_pin_enabled = sim_pin_enabled
        adb_step.__init__(self, **kwargs)
        self.set_passm("UI on the device {0} is up in less than {1} seconds".format(self.serial, self.timeout))
        self.set_errorm("", "UI on the device {0} was not up in less than {1} seconds".format(self.serial,
                                                                                              self.timeout))

    def do(self):
        root_connect_device(serial=self.serial)()
        wait_for_ui_processes(serial=self.serial, timeout=self.timeout)()
        print "[ {0} ]: ui process started and boot props set".format(self.serial)
        time.sleep(2)
        print "[ {0} ]: Pass the 'To start Android' screen if necessary".format(self.serial)

        if self.pin and self.boot_to_Android:
            enter_pin_to_start_android_if_necesary(serial=self.serial, pin=self.pin, timeout=self.timeout,
                                                   wait_step=self.wait_step)()
            wait_for_ui_processes(serial=self.serial, timeout=self.timeout)()
        print "[ {0} ]: wake and unlock device if necessary".format(self.serial)
        wake_up_device(serial=self.serial)()
        time.sleep(1)
        if self.pin and self.boot_to_Android:
            ui_steps.unlock_device(serial=self.serial, pin=self.pin)()
        else:
            menu_to_unlock(serial=self.serial)()
        command(serial=self.serial, command="svc power stayon true")()
        if self.device_info.platform is not "cel_apl":
            print "[ {0} ]: perform startup wizard if necessary".format(self.serial)
            if ui_utils.is_view_displayed(serial=self.serial,
                                          view_to_find={"resourceId": "com.google.android.setupwizard:id/start"}):
                ui_steps.perform_startup_wizard(serial=self.serial)()
            # accept telemetry if necessary
            print "[ {0} ]: wake device if necessary".format(self.serial)
            wake_up_device(serial=self.serial)()
            time.sleep(1)
            print "[ {0} ]: unlock device if necessary".format(self.serial)
            menu_to_unlock(serial=self.serial)()
            print "[ {0} ]: accept telemetry if necessary".format(self.serial)
            ui_steps.click_button_if_exists(serial=self.serial, view_to_find={"text": "Allow"},
                                            view_to_check={"text": "GOT IT"}, wait_time=5000)()

            # accept welcome if necessary
            print "[ {0} ]: wake device if necessary".format(self.serial)
            wake_up_device(serial=self.serial)()
            time.sleep(1)
            print "[ {0} ]: unlock device if necessary".format(self.serial)
            menu_to_unlock(serial=self.serial)()
            print "[ {0} ]: accept welcome if necessary".format(self.serial)
            ui_steps.click_button_if_exists(serial=self.serial, view_to_find={"text": "GOT IT"}, wait_time=5000)()
            # press OK if necessary
            print "[ {0} ]: wake device if necessary".format(self.serial)
            wake_up_device(serial=self.serial)()
            time.sleep(1)
            print "[ {0} ]: unlock device if necessary".format(self.serial)
            menu_to_unlock(serial=self.serial)()
            print "[ {0} ]: press OK if necessary".format(self.serial)
            ui_steps.click_button_if_exists(serial=self.serial, view_to_find={"text": "OK"}, wait_time=5000)()
        if self.boot_to_Android:
            ui_steps.unlock_device(serial=self.serial)()
            ui_steps.press_home(serial=self.serial)()
        command(serial=self.serial, command="svc power stayon false")()

    def check_condition(self):
        try:
            ui_loaded = ui_utils.is_homescreen(serial=self.serial, sim_pin_enabled=self.sim_pin_enabled)
            if self.disable_uiautomator:
                module_dir = os.path.dirname(os.path.realpath(__file__))
                module_dir = "/".join(module_dir.split("/")[0:-3])
                if "RESOURCES_FOLDER" in os.environ:
                    resource_path = os.environ["RESOURCES_FOLDER"]
                elif "uiautomator_jars_path" in os.environ:
                    resource_path = os.environ["uiautomator_jars_path"]
                else:
                    resource_path = os.path.join(module_dir, "external")
                __jar_files = ["bundle.jar", "uiautomator-stub.jar"]
                __apk_files = ["app-uiautomator-test.apk", "app-uiautomator.apk"]
                jar_not_found = False
                for jar in __jar_files:
                    if not adb_utils.file_exists(serial=self.serial, file_path=os.path.join(resource_path, jar)):
                        jar_not_found = True
                if jar_not_found is False:
                    kill_process(serial=self.serial, process_name="uiautomator")()
                for apk in __apk_files:
                    if adb_utils.is_apk_installed(serial=self.serial, apk_path=os.path.join(resource_path, apk)):
                        uninstall_apk(serial=self.serial, apk_path=os.path.join(resource_path, apk),
                                      uninstall_time=10)()
            if ui_loaded is True:
                self.step_data = True
                return True
            elif ui_loaded is None:
                self.step_data = False
                return True
            elif ui_loaded is False:
                return False
        except Exception:
            print "[ {0} ]: exception in wait for ui - {1}".format(self.serial, traceback.format_exc())
            return False


class enter_pin_to_start_android_if_necesary(adb_step):

    """ description:

        usage:
                enter_pin_to_start_android_if_necesary(serial = serial,pin = "1234")()

        tags:
            adb, pin, start android
    """
    def __init__(self, pin, wait_step, timeout=1800, **kwargs):
        self.pin = pin
        self.timeout = timeout
        self.wait_step = wait_step
        adb_step.__init__(self, **kwargs)

    def do(self):
        if self.pin and adb_utils.is_text_displayed(text_to_find="To start "
                                                    "Android, enter your PIN",
                                                    serial=self.serial,
                                                    wait_time=5):
            command(serial=self.serial,
                    command="input text {0}".format(self.pin))()
            command(serial=self.serial,
                    command="input keyevent KEYCODE_ENTER")()
            self.step_data = "Booting to Android"

    def check_condition(self):
        if self.step_data == "Booting to Android":
            waiting = 0
            while waiting < self.timeout:
                if adb_utils.is_prop_set(serial=self.serial, prop="init.svc.bootanim", value="running"):
                    return True
                waiting += self.wait_step
            return False
        return True


class enable_developer_options(adb_step):

    """ description:
            enables developer options in Settings calling intent

        usage:
            ui_steps.enable_developer_options()()

        tags:
            ui, android, developer, options
    """

    def do(self):
        am_start_command(serial=self.serial, component="com.android.settings/.DevelopmentSettings")()

    def check_condition(self):
        # check performed in the last step from do()
        return True


class open_users_settings(adb_step):

    """ description:
            enables developer options in Settings calling intent

        usage:
            ui_steps.enable_developer_options()()

        tags:
            ui, android, developer, options
    """

    def do(self):
        am_start_command(serial=self.serial, component="com.android.settings/.UsersSettings")()

    def check_condition(self):
        # check performed in the last step from do()
        return True


class push_file(adb_step):

    """ description:
            pushes the file frm <local> path to <remote> destination

                on the DUT. <timeout> can be used for big files. the
                step passes if ls command on the <remote> location
                contains the filename

        usage:
            push_file(local = "/home/tester/file_to.push", remote =
                "/tmp/")

        tags:
            adb, push, file
    """
    def __init__(self, local, remote, timeout=30, **kwargs):
        self.local = local
        self.remote = remote
        self.timeout = timeout
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "{0} could not be pushed on the DUT to {1} over adb".format(self.local, self.remote))
        self.set_passm("{0} was pushed on the DUT to {1} over adb".format(self.local, self.remote))

    def do(self):
        self.adb_connection.put_file(self.local, self.remote, self.timeout)

    def check_condition(self):
        file_name = self.local.split("/")[-1]
        self.step_data =\
            self.adb_connection.parse_cmd_output(cmd="ls {0}".format(self.remote), grep_for=file_name)
        return file_name in self.step_data


class pull_file(adb_step, local_step):

    """ description:
            pulls the file from <remote> path to <local> destination
                from the DUT. <timeout> can be used for big files. the
                step passes if ls command on the <local> location
                contains the filename

        usage:
            pull_file(local = "/home/tester/file_to.push", remote =
                "/tmp/")

        tags:
            adb, pull, file
    """
    def __init__(self, local, remote, timeout=30, **kwargs):
        self.local = local
        self.remote = remote
        self.timeout = timeout
        adb_step.__init__(self, **kwargs)
        local_step.__init__(self, **kwargs)
        self.set_errorm("", "{0} could not be pulled from the DUT to {1} over adb".format(self.remote, self.local))
        self.set_passm("{0} was pulled from the DUT to {1} over adb".format(self.remote, self.local))

    def do(self):
        self.adb_connection.get_file(local=self.local, remote=self.remote, timeout=self.timeout)

    def check_condition(self):
        file_name = self.remote.split("/")[-1]
        self.step_data, stde =\
            self.local_connection.run_cmd(command="ls {0}".format(self.local))
        return file_name in self.step_data and len(stde) == 0


class wake_up_device(adb_step):

    """ description:
            wakes the device from sleep with sleep button
            checks the logcat for wake message
            fails if the DUT is not in sleep mode

        usage:
            adb_steps.wake_up_device()()

        tags:
            adb, android, wake
    """

    def __init__(self, tries=5, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.tries = tries

    def do(self):
        while not adb_utils.is_power_state(serial=self.serial, state="ON") and self.tries > 0:
            command(serial=self.serial, command="input keyevent 26")()
            time.sleep(3)
            self.tries -= 1

    def check_condition(self):
        return adb_utils.is_power_state(serial=self.serial, state="ON")


class put_device_into_sleep_mode(adb_step):

    """ description:
            puts device into sleep mode

        usage:
            adb_steps.put_device_into_sleep_mode()()

        tags:
            adb, android, sleep
    """

    def __init__(self, tries=5, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.tries = tries

    def do(self):
        while adb_utils.is_power_state(serial=self.serial, state="ON") and self.tries > 0:
            command(serial=self.serial, command="input keyevent 26")()
            time.sleep(3)
            self.tries -= 1

    def check_condition(self):
        return adb_utils.is_power_state(serial=self.serial, state="OFF")


class menu_to_unlock(adb_step):

    """ description:
            send menu keyevent to unlock the device

        usage:
            adb_steps.menu_to_unlock()()

        tags:
            adb, android, unlock
    """

    def __init__(self, tries=5, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.tries = tries

    def do(self):
        while ui_utils.is_device_locked(serial=self.serial) and self.tries > 0:
            command(serial=self.serial, command="input keyevent 82")()
            time.sleep(3)
            self.tries -= 1

    def check_condition(self):
        return not ui_utils.is_device_locked(serial=self.serial)


class delete_folder_content(adb_step):

    """ description:
            deletes the content of the remote <folder>

        usage:
            delete_folder_content(folder = "/tmp")

        tags:
            adb, folder, delete, content
    """
    def __init__(self, folder, **kwargs):
        self.folder = folder
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not delete the content of {0} on the device over adb".format(self.folder))
        self.set_passm("Deleted the content of {0} on the device over adb".format(self.folder))

    def do(self):
        command(serial=self.serial, command="rm -rf {0}/*".format(self.folder))()

    def check_condition(self):
        ls_process = self.adb_connection.run_cmd("ls {0}".format(self.folder))
        return len(ls_process.stdout.read()) < 1


class delete_folder(adb_step):

    """ description:
            deletes the content of the remote <folder>

        usage:
            delete_folder(folder = "/tmp")

        tags:
            adb, folder, delete, content
    """
    def __init__(self, folder, **kwargs):
        self.folder = folder
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not delete {0} on the device over adb".format(self.folder))
        self.set_passm("Deleted {0} on the device over adb".format(self.folder))

    def do(self):
        command(serial=self.serial, command="rm -rf {0}".format(self.folder))()

    def check_condition(self):
        ls_process = self.adb_connection.run_cmd("ls {0}".format(self.folder))
        return "No such file or directory" in ls_process.stdout.read()


class create_folder(adb_step):

    """ description:
            creates <folder> at the given <path>

        usage:
            create_folder(path = "/sdcard/", folder = "test")

        tags:
            adb, folder, create
    """
    def __init__(self, path, folder, **kwargs):
        self.folder = folder
        self.path = path
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "Could not create folder {0} in {1}".format(self.folder, self.path))
        self.set_passm("Created folder {0} in {1}".format(self.folder, self.path))

    def do(self):
        command(serial=self.serial, command="mkdir {0}/{1}".format(self.path, self.folder))()

    def check_condition(self):
        ls_process = self.adb_connection.run_cmd("ls {0}".format(self.path))
        return self.folder in ls_process.stdout.read()


class check_folders_exist(adb_step):

    """ description:
            checks if the folder from <folder_list> are all present on
            the device

        usage:
            adb_steps.check_folders_exist(serial = self.serial,
                          folder_list = ["/mnt/sdcard/test",
                                         "/mnt/sdcard/test/bbb_short"
                                         "/mnt/sdcard/test/bbb_full",])()

        tags:
            adb, folder, exist
    """

    def __init__(self, folder_list, presence=True, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.folder_list = folder_list
        self.presence = presence

    def do(self):
        self.step_data = True
        for folder in self.folder_list:
            self.step_data = self.step_data and adb_utils.folder_exists(serial=self.serial, folder=folder)
            print "{0} - {1}".format(folder, self.step_data)

    def check_condition(self):
        if not self.presence:
            self.step_data = not self.step_data
        return self.step_data


class check_package_installed(adb_step):

    """ description:
            checks if the folder from <folder_list> are all present on
            the device

        usage:
            adb_steps.check_folders_exist(serial = self.serial,
                          folder_list = ["/mnt/sdcard/test",
                                         "/mnt/sdcard/test/bbb_short"
                                         "/mnt/sdcard/test/bbb_full",])()

        tags:
            adb, folder, exist
    """

    def __init__(self, package, presence=True, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.package = package
        self.presence = presence

    def do(self):
        self.step_data = adb_utils.is_package_installed(package_name=self.package, serial=self.serial)

    def check_condition(self):
        if not self.presence:
            self.step_data = not self.step_data
        return self.step_data


class command(adb_step):

    """ description:
            runs the given command on the host. to check the correct
                execution of the command, the stdout or stderr can be
                grepped for given string (if it is present or not)

        usage:
            command(command = "command_to_be_executed",
                    <stdout_grep = "text_to_exist_in_stdout>,
                    <stdout_not_grep = "text_not_to_exist_in_stdout>,
                    <stderr_grep = "text_to_exist_in_stderr>,
                    <stderr_not_grep = "text_not_to_exist_in_stderr>,)

        tags:
            adb, command, grep, stdout, stderr
    """
    command = None

    def __init__(self, command, stdout_grep=None, stdout_not_grep=None, stderr_grep=None, stderr_not_grep=None,
                 timeout=20, mode="sync", ignore_error=False, **kwargs):
        self.command = command
        self.stdout_grep = stdout_grep
        self.stderr_grep = stderr_grep
        self.stdout_not_grep = stdout_not_grep
        self.stderr_not_grep = stderr_not_grep
        self.timeout = timeout
        self.mode = mode
        self.ignore_error = ignore_error
        adb_step.__init__(self, **kwargs)
        self.set_errorm("", "Executing adb command {0}".format(self.command))
        self.set_passm("Executing adb command {0}".format(self.command))

    def do(self):
        self.step_data = self.adb_connection.run_cmd(command=self.command, timeout=self.timeout, mode=self.mode,
                                                     ignore_error=self.ignore_error)

    def check_condition(self):
        if self.mode == "async":
            if self.stdout_grep:
                if self.stdout_grep in self.step_data.stdout.read():
                    return True
                else:
                    return False
            return True
        if self.stdout_grep or self.stdout_not_grep or self.stderr_grep or self.stderr_not_grep:
            stdout = self.step_data.stdout.read()
            stderr = self.step_data.stderr.read()
        else:
            stdout = ""
            stderr = ""
        if self.verbose:
            stds = "\n\tSTDOUT = \n\t{0}\tSTDERR = \n\t{1}\n".format(stdout, stderr)
        return_value = True
        if self.stdout_grep:
            if self.verbose:
                error_mess = "\'{0}\' not in stdout - {1}".format(self.stdout_grep, stds)
                self.set_errorm("", "Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return_value = return_value and self.stdout_grep in stdout
        if self.stdout_not_grep:
            if self.verbose:
                error_mess = "\'{0}\' in stdout - {1}".format(self.stdout_not_grep, stds)
                self.set_errorm("Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return_value = return_value and self.stdout_not_grep not in stdout
        if self.stderr_grep:
            if self.verbose:
                error_mess = "\'{0}' not in stderr - {1}".format(self.stderr_grep, stds)
                self.set_errorm("Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return_value = return_value and self.stderr_grep in stderr
        if self.stderr_not_grep:
            if self.verbose:
                error_mess = "\'{0}\' in stderr - {1}".format(self.stderr_not_grep, stds)
                self.set_errorm("Executing {0}: {1}".format(self.command, error_mess))
                self.set_passm("Executing {0}: {1}".format(self.command, stds))
            return_value = return_value and self.stderr_not_grep not in stderr
        return return_value


class am_start_command(adb_step):

    """ description:
            runs the given am command on the device

        usage:


        tags:
            adb, am, command
    """

    def __init__(self, component=None, timeout=20, **kwargs):
        self.component = component
        self.timeout = timeout
        if self.component:
            self.package = self.component.split("/")[0]
        adb_step.__init__(self, **kwargs)

    def do(self):
        if self.package:
            command(command="pm clear {0}".format(self.package), serial=self.serial, timeout=self.timeout)()
        if self.component:
            self.step_data = command(command="am start -n {0}".format(self.component), serial=self.serial,
                                     timeout=self.timeout)()

    def check_condition(self):
        stdout = self.step_data.stdout.read()
        stderr = self.step_data.stderr.read()
        self.set_passm("am start -n {0}".format(self.component))
        self.set_errorm("", "am start -n {0}: \n\tStdout\n{1}\n\tStderr\n{2}".format(self.component, stdout, stderr))
        if "Error" not in stdout and "Exception" not in stdout:
            return True
        return False


class check_device_reboots(base_step):

    def __init__(self, serial, reboot_timeout=20, **kwargs):
        self.serial = serial
        self.reboot_timeout = reboot_timeout
        base_step.__init__(self, **kwargs)
        self.set_passm("Device {0} rebooted!".format(self.serial))
        self.set_errorm("", "Device {0} was not rebooted in {1}!".format(self.serial, self.reboot_timeout))

    def do(self):
        self.step_data = 0
        while local_utils.has_adb_serial(serial=self.serial) and self.reboot_timeout > self.step_data:
            time.sleep(1)
            self.step_data += 1

    def check_condition(self):
        return self.reboot_timeout > self.step_data


class check_buildstamp(adb_step):

    """ description:
            checks the given build number is the the same as the one
                in /etc/buildstamp on the DUT

        usage:
            check_buildstamp(build_number = 940)

        tags:
            adb, command, build_stamp, build_number
    """
    def __init__(self, build_number, **kwargs):
        self.build_number = build_number
        adb_step.__init__(self, **kwargs)

    def do(self):
        self.result = self.build_number in \
            self.adb_connection.parse_file("/etc/buildstamp", grep_for=self.build_number)

    def check_condition(self):
        return self.result


class sqlite_replace_query(adb_step):

    """ description:
            replaces <values> of the <columns> in sqlite db <db> and
                <table> with the where clause given by the
                <where_columns> and <where_values>
            it checks the correct query execution with select query

        usage:
            sqlite_replace_query(db = "/data/system/locksettings.db",
                table = "locksettings", columns = ["user", "value"],
                values = ["0", "1"], where_columns = ["name"], values =
                ["lockscreen.disabled"]

        tags:
            adb, command, sqlite, query, update
    """
    def __init__(self, db, table, columns, values, where_columns, where_values, **kwargs):
        self.db = db
        self.table = table
        self.columns = columns
        self.values = values
        self.where_columns = where_columns
        self.where_values = where_values
        adb_step.__init__(self, **kwargs)

    def do(self):
        query = Sqlite.generate_update_query(db=self.db, table=self.table, columns=self.columns, values=self.values,
                                             where_columns=self.where_columns, where_values=self.where_values)
        self.set_passm(query)
        self.set_errorm("", query)
        command(serial=self.serial,
                command=query)()

    def check_condition(self):
        sqlite_select_query(serial=self.serial, db=self.db, table=self.table, columns=self.columns,
                            where_columns=self.columns, where_values=self.values, values=self.values)()


class sqlite_select_query(adb_step):

    """ description:
            check <values> of the <columns> in sqlite db <db> and
                <table> with the where clause given by the
                <where_columns> and <where_values>
            it checks the correct query execution with select query

        usage:
            sqlite_replace_query(db = "/data/system/locksettings.db",
                table = "locksettings", columns = ["user", "value"],
                values = ["0", "1"], where_columns = ["name"], values =
                ["lockscreen.disabled"]

        tags:
            adb, command, sqlite, query, update
    """

    def __init__(self, db, table, columns, values, where_columns, where_values, **kwargs):
        self.db = db
        self.table = table
        self.columns = columns
        self.values = values
        self.where_columns = where_columns
        self.where_values = where_values
        adb_step.__init__(self, **kwargs)

    def do(self):
        query = Sqlite.generate_select_query(db=self.db,
                                             table=self.table,
                                             columns=self.columns,
                                             where_columns=self.where_columns,
                                             where_values=self.where_values)
        self.set_passm(query)
        self.set_errorm("", query)
        process = self.adb_connection.run_cmd(serial=self.serial, command=query)
        self.step_result = process.stdout.read().strip().split("|")

    def check_condition(self):
        i = 0
        for value in self.values:
            if str(value) != self.step_result[i]:
                return False
            i += 1
        return True


class input_back(adb_step):
    """ description:
            sends back keycode to the device

        usage:
            input_back()()

        tags:
            adb, command, input, back
    """
    def do(self, **kwargs):
        command(serial=self.serial, command="input keyevent 4", mode="async")()

    def check_condition(self):
        return True


class set_prop(adb_step):

    """ description:
            sets the prop <key> with the value <value> using setprop
            it checks the value using getprop

        usage:
            set_prop(key = "persist.sys.utility_iface",
                     value =" eth0")

        tags:
            adb, command, prop, setprop
    """
    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        adb_step.__init__(self, **kwargs)

    def do(self):
        cmd = "setprop {0} {1}".format(self.key, self.value)
        command(serial=self.serial,
                command=cmd)()

    def check_condition(self):
        command = "getprop {0}".format(self.key)
        return self.value == self.adb_connection.parse_cmd_output(cmd=command, grep_for=self.value)


class install_apk(adb_step):

    """ description:
            installs apk from <apk_path> on the DUT
            it checks if the package is present in pm list packages

        usage:
            install_apk(apk_path = "/path/to/app.apk")

        tags:
            adb, command, install, application
    """
    def __init__(self, apk_path, install_time=None, **kwargs):
        self.apk_path = apk_path
        self.package_name = android_utils.get_package_name_from_apk(apk_path)
        adb_step.__init__(self, **kwargs)
        self.set_passm("Installing {0}".format(self.apk_path))
        self.set_errorm("", "Installing {0}".format(self.apk_path))
        if install_time:
            self.install_time = install_time
        else:
            self.install_time = None

    def do(self):
        if self.install_time:
            self.adb_connection.install_apk(apk=self.apk_path, timeout=self.install_time)
        else:
            self.adb_connection.install_apk(apk=self.apk_path)

    def check_condition(self):
        return adb_utils.is_apk_installed(serial=self.serial, apk_path=self.apk_path)


class uninstall_apk(adb_step):

    """ description:
            uninstalls apk (<package_name> is taken from the apk with aapt)
            it checks if the package is no longer present in pm list
            packages

        usage:
            uninstall_apk(apk_path = "/path/to/app.apk")

        tags:
            adb, command, uninstall, application
    """
    def __init__(self, apk_path, uninstall_time=5, **kwargs):
        self.apk_path = apk_path
        self.package_name = android_utils.get_package_name_from_apk(apk_path)
        adb_step.__init__(self, **kwargs)
        self.set_passm("Uninstalling {0}".format(self.apk_path))
        self.set_errorm("", "Uninstalling {0}".format(self.apk_path))
        if uninstall_time:
            self.uninstall_time = uninstall_time

    def do(self):
        if self.uninstall_time:
            self.adb_connection.uninstall_apk(package=self.package_name, timeout=self.uninstall_time)
        else:
            self.adb_connection.uninstall_apk(package=self.package_name)

    def check_condition(self):
        return not adb_utils.is_apk_installed(serial=self.serial, apk_path=self.apk_path)


class check_serial(adb_step):
    """
        description:
            checks if the DUT has the given <serial_to_check> serial.

        usage:
            check_serial(serial_to_check = "10.237.100.212:5555")()

        tags:
            android, adb, serial
    """
    def __init__(self, serial_to_check, **kwargs):
        self.serial_to_check = serial_to_check
        adb_step.__init__(self, **kwargs)
        self.set_passm("Device has serial: {0}".format(self.serial_to_check))
        self.set_errorm("", "Device does not have serial: ".format(self.serial_to_check))

    def do(self):
        self.step_data = adb_utils.get_serial(serial=self.serial)

    def check_condition(self):
        return self.serial_to_check == self.step_data


class load_CPU(adb_step):

    """ description:
            loads CPU on the device

        usage:
            adb_steps.load_CPU()()

        tags:
            android, adb, CPU, load
    """
    def do(self):
        self.step_data = self.adb_connection.load_CPU()

    def check_condition(self):
        self.step_data is not None


class take_screenshot_given_path(adb_step):

    """ description:
            takes screenshot from the device, saves it to
            /data/local/tmp with <screenshot_file> name and copies
            it to the <host_path> path on the host

        usage:
           take_screenshot_given_path(screenshot_file = "file.png",
                                      host_path = "/tmp/"

        tags:
            adb, android, screenshot, host, pull
    """
    def __init__(self, screenshot_file, host_path, **kwargs):
        self.file_name = screenshot_file
        self.host_path = host_path
        adb_step.__init__(self, **kwargs)
        self.set_passm("Taking {0} screenshot to {1}".format(self.file_name, self.host_path))
        self.set_errorm("", "Taking {0} screenshot to {1}".format(self.file_name, self.host_path))

    def do(self):
        remote_path = "/data/local/tmp/{0}".format(self.file_name)
        command(serial=self.serial, command="screencap -p {0}".format(remote_path), timeout=60)()
        self.step_data = pull_file(serial=self.serial, local=self.host_path, remote=remote_path)()

    def check_condition(self):
        return self.file_name in self.step_data


class take_screenrecord_given_path(adb_step):

    """ description:
            takes screenrecord from the device, saves it to
            /data/local/tmp with <screenshot_file> name and copies
            it to the <host_path> path on the host

        usage:
           take_screenrecord_given_path(screenrecord_file = "file.png",
                                        host_path = "/tmp/"

        tags:
            adb, android, screenrecord, host, pull
    """
    def __init__(self, screenrecord_file, host_path, record_time=10, **kwargs):
        self.file_name = screenrecord_file
        self.host_path = host_path
        self.record_time = record_time
        adb_step.__init__(self, **kwargs)
        self.set_passm("Taking {0} screenshot to {1}".format(self.file_name, self.host_path))
        self.set_errorm("", "Taking {0} screenshot to {1}".format(self.file_name, self.host_path))

    def do(self):
        remote_path = "/data/local/tmp/{0}".format(self.file_name)
        cmd = "screenrecord --time-limit {0} {1}".format(self.record_time, remote_path)
        command(serial=self.serial, command=cmd, timeout=self.record_time + 10)()
        self.step_data = pull_file(serial=self.serial, local=self.host_path, remote=remote_path)()

    def check_condition(self):
        return self.file_name in self.step_data


class perform_startup_wizard_with_tap(adb_step):

    """ description:
            performs the startup wizard using tap

        usage:
           adb_steps.perform_startup_wizard_with_tap()()

        tags:
            adb, android, startup wizard, tap
    """
    def do(self):

        lcd_density = self.adb_connection.get_prop("ro.sf.lcd_density_info")
        lcd_density = lcd_density.strip("[").strip("]").split(" ")
        width = int(lcd_density[0])
        height = int(lcd_density[2].strip("px"))
        command(serial=self.serial, command="input tap 50 50")()
        time.sleep(1)
        command(serial=self.serial, command="input tap {0} 50".format(width - 50))()
        time.sleep(1)
        command(serial=self.serial, command="input tap {0} {1}".format(width - 50, height - 50))()
        time.sleep(1)
        command(serial=self.serial, command="input tap 50 {0}".format(height - 50))()

    def check_condition(self):
        return True


class enable_uiautomator_service(adb_step, ui_step):

    """ description:
            enables uiautomator rpc server

        usage:
           adb_steps.enable_uiautomator_service()()

        tags:
            adb, android, uiautomator, start
    """
    def __init__(self, apks=True, timeout=60, **kwargs):
        ui_step.__init__(self, **kwargs)
        adb_step.__init__(self, **kwargs)
        self.timeout = timeout
        self.apks = apks

    def do(self):
        module_dir = os.path.dirname(os.path.realpath(__file__))
        module_dir = "/".join(module_dir.split("/")[0:-3])
        if "RESOURCES_FOLDER" in os.environ:
            res_path = os.environ["RESOURCES_FOLDER"]
        elif "uiautomator_jars_path" in os.environ:
            res_path = os.environ["uiautomator_jars_path"]
        else:
            res_path = os.path.join(module_dir, "external")

        if self.apks:
            ui_apks = ["app-uiautomator.apk", "app-uiautomator-test.apk"]
            for ui_apk in ui_apks:
                install_apk(serial=self.serial, apk_path=os.path.join(res_path, ui_apk), install_time=300)()
        else:
            bundle_jar_path = os.path.join(res_path, "bundle.jar")
            push_file(serial=self.serial,
                      local=bundle_jar_path,
                      remote="/data/local/tmp")()
            uiautomator_stub_jar_path = os.path.join(res_path, "uiautomator-stub.jar")
            push_file(serial=self.serial,
                      local=uiautomator_stub_jar_path,
                      remote="/data/local/tmp")()

    def check_condition(self):
        if self.apks:
            return True

        waiting = 0
        while self.timeout > waiting:
            try:
                print "[ {0} ]: Device UI info - {1}".format(self.serial, self.uidevice.info)
                return True
            except Exception:
                print "[ {0} ]: Error enabling uiautomator - {1}".format(self.serial, traceback.format_exc())
                time.sleep(5)
                waiting += 5
        return False


class change_bios(adb_step):

    """ description:
            executes curl command on the local host

        usage:
            change_bios(url = "url_to_be_opened",
                        args = "arguments_to_be_passed_to_curl,
                        grep_for = "text_to_be_search_in_the_output,)

        tags:
            local, command, curl, grep, stdout
    """

    def __init__(self, bios_file, bios_version, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.bios_file = bios_file
        self.bios_version = bios_version
        self.bios_destination = "/dev/efi/"
        self.mount_cmd = "mount \-t vfat /dev/block/by-name/android_bootloader /dev/efi"
        self.umount_cmd = "umount"
        self.get_bios_vers_cmd = "cat /sys/devices/virtual/dmi/id/bios_version"
        self.set_passm("Bios changed!")

    def do(self):
        local_steps.wait_for_adb(serial=self.serial)()
        root_connect_device(serial=self.serial)()
        create_folder(serial=self.serial, path="dev", folder="efi")()
        command(serial=self.serial, command=self.mount_cmd)()
        push_file(serial=self.serial, local=self.bios_file, remote=self.bios_destination)()
        command(serial=self.serial, command=self.umount_cmd)()
        reboot(serial=self.serial)()

    def check_condition(self):
        time.sleep(5)
        local_steps.wait_for_adb(serial=self.serial, timeout=200)()
        crt_bios_vers = self.adb_connection.parse_cmd_output(cmd=self.get_bios_vers_cmd)
        return self.bios_version in crt_bios_vers


class do_provision(adb_step):

    """ description:
            executes curl command on the local host

        usage:
            do_provision(url = "url_to_be_opened",
                         args = "arguments_to_be_passed_to_curl,
                         grep_for = "text_to_be_search_in_the_output,)

        tags:
            local, command, curl, grep, stdout
    """

    def __init__(self, exoPlayerDemo_path, widevineSamplePlayer_path, txei_sec_tools_path, keybox_path, **kwargs):
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        adb_step.__init__(self, **kwargs)
        self.exoPlayerDemo_path = exoPlayerDemo_path
        self.widevineSamplePlayer_path = widevineSamplePlayer_path
        self.keybox_path = keybox_path
        self.remote_keybox_path = "/data"
        self.txei_sec_tools_path = txei_sec_tools_path
        self.remote_txei_sec_tools_path = "/system/bin"
        self.set_txei_sec_tools_exec_cmd = "chmod 777 {0} TXEI_SEC_TOOLS".format(self.remote_txei_sec_tools_path)
        self.input_cmd = "TXEI_SEC_TOOLS -acd-write 1 /data/keybox.bin 128 128"

    def do(self):
        local_steps.wait_for_adb(serial=self.serial)()
        root_connect_device(serial=self.serial)()
        local_steps.command(serial=self.serial, command="adb -s {0} remount".format(self.serial))()
        install_apk(serial=self.serial, apk_path=self.exoPlayerDemo_path)
        install_apk(serial=self.serial, apk_path=self.widevineSamplePlayer_path)
        push_file(serial=self.serial, local=self.keybox_path, remote=self.remote_keybox_path)()
        push_file(serial=self.serial, local=self.txei_sec_tools_path, remote=self.remote_txei_sec_tools_path)()
        command(serial=self.serial, command=self.set_txei_sec_tools_exec_cmd)()
        command(serial=self.serial, command=self.input_cmd)()
        kill_process(serial=self.serial, process_name="drm")()
        kill_process(serial=self.serial, process_name="mediaserver")()
        reboot(serial=self.serial)()

    def check_condition(self):
        time.sleep(5)
        local_steps.wait_for_adb(serial=self.serial, timeout=200)()
        return True


class enable_package_from_pm(adb_step, ui_step):

    """ description:
            enables package <package_name> from pm
            adb root is needed

        usage:
            adb_steps.enable_packege_from_pm(package_name = " com.google.android.ears")()

        tags:
            android, adb, pm, package, enable
    """

    def __init__(self, package_name, app_name, is_widget=False, **kwargs):
        self.package_name = package_name
        self.app_name = app_name
        self.is_widget = is_widget
        adb_step.__init__(self, **kwargs)
        ui_step.__init__(self, **kwargs)

    def do(self):
        root_connect_device(serial=self.serial)()
        command(serial=self.serial, command="pm enable {0}".format(self.package_name))()

    def check_condition(self):
        if self.is_widget:
            ui_steps.open_widget_section(serial=self.serial)()
        else:
            ui_steps.home_page(serial=self.serial)()
            ui_steps.press_all_apps(serial=self.serial)()
        return ui_utils.is_text_visible_scroll_left(serial=self.serial, text_to_find=self.app_name)


class check_wifi_driver(adb_step):

    """ description:
            checks the presence of the wifi driver.

        usage:
            adb_steps.check_wifi_driver(driver = "")()

        tags:
            android, adb, wifi, drivers
    """

    def __init__(self, driver, **kwargs):
        self.driver = driver
        adb_step.__init__(self, **kwargs)

    def do(self):
        self.driver = self.device_info.wifi_driver
        self.my_driver = self.adb_connection.parse_cmd_output(cmd='lsmod', grep_for=self.driver).strip()

    def check_condition(self):
        if self.my_driver != "":
            return True
        else:
            self.set_errorm("", "Driver {} not present.".format(self.driver))
            return False


class check_gvb_state(adb_step):

    """ description:
            Checks if the color variable is correctly set

        usage:
            adb_steps.check_gvb_state(color = "green")()

        tags:
            fastboot, vars
    """

    def __init__(self, color, **kwargs):
        self.color = color
        adb_step.__init__(self, **kwargs)

    def do(self):
        local_steps.wait_for_adb(serial=self.serial)()

    def check_condition(self):
        return adb_utils.is_prop_set(serial=self.serial, prop="ro.boot.verifiedbootstate", value=self.color)


class change_permissions(adb_step):

    """ description:
            Changes the permissions of a file from Android DUT

        usage:
            adb_steps.change_permissions(file_name = test, perm = 777)()

        tags:
            adb, permissions, file
    """

    def __init__(self, file_name, perm, **kwargs):
        self.file_name = file_name
        self.perm = perm
        adb_step.__init__(self, **kwargs)

    def do(self):
        command(serial=self.serial, command="chmod " + str(self.perm) + " " + self.file_name)()

    def check_condition(self):
        command(serial=self.serial,
                command="stat " + self.file_name,
                stdout_grep=str(self.perm))()


class disable_verity(adb_step):

    """ description:
            Disables verity in order to make /system partition RW

        usage:
            adb_steps.disable_verity()()

        tags:
            adb, verity, system
    """

    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)

    def do(self):
        self.step_data = self.adb_connection.adb_disable_verity()

    def check_condition(self):
        return "disabled" in self.step_data.stdout.read()


class provision_sofia(adb_step):

    """ description:
            Provision for SoFIA platform.

        usage:
            adb_steps.check_gvb_state(wvkeyboxtool = file1, keybox = kb34.bin)()

        tags:
            adb, provision, widevine, sofia
    """

    def __init__(self, wvkeyboxtool, keybox, **kwargs):
        self.wvkeyboxtool = wvkeyboxtool
        self.keybox = keybox
        self.system_path = "/system/bin/"
        self.remote_wvkeyboxtool = self.system_path + os.path.basename(self.wvkeyboxtool)
        self.remote_keybox = self.system_path + os.path.basename(self.keybox)
        adb_step.__init__(self, **kwargs)

    def do(self):
        root_connect_device(serial=self.serial)()
        if "kb_provisioning" in self.device_info.provisioning_type:
            root_connect_device(serial=self.serial)()
            disable_verity(serial=self.serial)()
            reboot(serial=self.serial)()
            root_connect_device(serial=self.serial)()
            local_steps.wait_for_adb(serial=self.serial)()
            remount(serial=self.serial,
                    should_remount=True)()
            push_file(serial=self.serial, local=self.wvkeyboxtool, remote=self.remote_wvkeyboxtool)()
            push_file(serial=self.serial, local=self.keybox, remote=self.remote_keybox)()
            change_permissions(serial=self.serial, file_name=self.remote_wvkeyboxtool, perm=777)()
            command(serial=self.serial,
                    command=self.remote_wvkeyboxtool +
                    " -w " + self.remote_keybox)()
            command(serial=self.serial,
                    command="rm " + self.remote_wvkeyboxtool)()
            command(serial=self.serial,
                    command="rm " + self.remote_keybox)()

    def check_condition(self):
        # No check
        return True


class wait_for_text(adb_step):
    """ description:
        wait for a text to appear on screen by looking into
        ui dump xml

        usage:
            wait_for_text(text_to_find=<text>)

        tags:
            adb, adb_utils
    """
    def __init__(self, text_to_find, timeout=100, **kwargs):
        self.text_to_find = text_to_find
        self.timeout = timeout
        adb_step.__init__(self, **kwargs)

    def do(self):
        self.step_data = adb_utils.is_text_displayed(text_to_find=self.text_to_find,
                                                     serial=self.serial,
                                                     wait_time=self.timeout)

    def check_condition(self):
        return self.step_data


class wait_for_view(adb_step):
    """ description:
        wait for a view to appear on screen by looking into
        ui dump xml

        usage:
            wait_for_view(view_to_find={"text": "Text"})

        tags:
            adb, adb_utils
    """
    def __init__(self, view_to_find, timeout=1000, **kwargs):
        self.view_to_find = view_to_find
        self.timeout = timeout
        adb_step.__init__(self, **kwargs)

    def do(self):
        self.step_data = adb_utils.is_view_displayed(view_to_find=self.view_to_find,
                                                     serial=self.serial,
                                                     wait_time=self.timeout)

    def check_condition(self):
        return self.step_data


class swipe(adb_step):
    """ description:
            swipes from (<sx>, <sy>) to (<ex>, <ey>)
                in <steps> steps
                if <view_to_check> given it will check that
                the object identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False after swipe
            Uses only adb commands
        usage:
            adb_steps.swipe(sx = 10, sy = 10, ex = 100, ey = 100)

        tags:
            ui, android, swipe
    """

    def __init__(self, sx, sy, ex, ey, steps=100, view_presence=True,
                 exists=True, view_to_check=None, wait_time=None,
                 iterations=1, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.view_presence = view_presence
        self.wait_time = wait_time
        self.start_x = sx
        self.start_y = sy
        self.end_x = ex
        self.end_y = ey
        self.steps = steps
        self.exists = exists
        self.view_to_check = view_to_check
        self.iterations = iterations

    def do(self):
        iterations = 0
        if self.view_to_check:
            while iterations < self.iterations:
                if not adb_utils.is_view_displayed(view_to_find=self.view_to_check,
                                                   serial=self.serial,
                                                   wait_time=1000):
                    command(serial=self.serial, command="input swipe {0} {1} {2} {3} {4}"
                            .format(self.start_x, self.start_y,
                                    self.end_x, self.end_y, self.steps))()
                iterations += 1
        else:
            command(serial=self.serial, command="input swipe {0} {1} {2} {3} {4}"
                    .format(self.start_x, self.start_y,
                            self.end_x, self.end_y, self.steps))()

    def check_condition(self):
        if self.view_to_check is None:
            return True

        exists = adb_utils.is_view_displayed(view_to_find=self.view_to_check, serial=self.serial,
                                             wait_time=self.wait_time, exists=self.exists)
        return exists if self.view_presence else not exists


class unlock_device_swipe(adb_step):

    """ description:
            unlocks the screen with swipe using only adb

        usage:
            ui_steps.unlock_device_swipe()()

        tags:
            ui, android, unlock
    """

    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.set_passm("Unlock device - swipe")
        self.set_errorm("", "Unlock device - swipe")

    def do(self):
        swipe(serial=self.serial, sx=200, sy=500, ex=200, ey=0,
              exists=False,
              view_to_check={"resource-id": "com.android.systemui:id/lock_icon"},
              iterations=3)()
        time.sleep(2)

    def check_condition(self):
        return adb_utils.is_view_displayed(serial=self.serial,
                                           view_to_find={"resource-id":
                                                         "com.android.systemui:id/lock_icon"},
                                           wait_time=1,
                                           exists=False)


class unlock_device_pin(adb_step):

    """ description:
            unlocks the screen with PIN

        usage:
            ui_steps.unlock_device_pin(pin = "1234")()

        tags:
            ui, android, unlock, PIN
    """

    def __init__(self, pin="1234", wrong_pin=False, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.pin = pin
        self.wrong_pin = wrong_pin
        self.set_passm("Unlock device - PIN")
        self.set_errorm("", "Unlock device - PIN")

    def do(self):
        command(serial=self.serial,
                command="input text {0}".format(self.pin))()
        command(serial=self.serial,
                command="input keyevent KEYCODE_ENTER")()

    def check_condition(self):
        if self.wrong_pin:
            return adb_utils.is_view_displayed(serial=self.serial,
                                               view_to_find={"resource-id":
                                                             "com.android.systemui:id/lock_icon"})

        else:
            return adb_utils.is_view_displayed(serial=self.serial,
                                               view_to_find={"resource-id":
                                                             "com.android.systemui:id/lock_icon"},
                                               wait_time=1,
                                               exists=False)


class unlock_device(ui_step):
    """ description:
            unlocks the screen with swipe and/or PIN

        usage:
            ui_steps.unlock_device()()

        tags:
            ui, android, unlock
    """

    def __init__(self, pin=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.set_passm("Unlock device with swipe and/or PIN")
        self.set_errorm("", "Unlock device with swipe and/or PIN")
        self.pin = pin

    def do(self):
        if ui_utils.is_device_locked(serial=self.serial):
            unlock_device_swipe(serial=self.serial)()
        if self.pin and ui_utils.is_device_pin_locked(serial=self.serial):
            unlock_device_pin(serial=self.serial, pin=self.pin)()

    def check_condition(self):
        return adb_utils.is_view_displayed(serial=self.serial,
                                           view_to_find={"resource-id":
                                                         "com.android.systemui:id/lock_icon"},
                                           wait_time=1,
                                           exists=False)


class block_device(adb_step):
    """ description:
        unlocks DUT with wrong PIN 5 times in a row

    usage:
        adb_steps.block_device(pin = "2222")()

    tags:
        adb, android, PIN
    """

    def __init__(self, pin="2222", **kwargs):
        self.pin = pin
        adb_step.__init__(self, **kwargs)

    def do(self):
        # enter wrong pin 5 times
        root_connect_device(serial=self.serial)()
        kill_process(serial=self.serial, process_name="uiautomator")()
        put_device_into_sleep_mode(serial=self.serial)()
        time.sleep(2)
        wake_up_device(serial=self.serial)()
        swipe(serial=self.serial, sx=200, sy=500, ex=200, ey=0)()

        for i in range(0, 5):
            command(serial=self.serial,
                    command="input text {0}".format(self.pin))()
            command(serial=self.serial,
                    command="input keyevent KEYCODE_ENTER")()
            if i is not 4:
                wait_for_view(serial=self.serial,
                              view_to_find={"text": "Wrong PIN"})()

    def check_condition(self):
        if not adb_utils.is_view_displayed(serial=self.serial,
                                           view_to_find={"resource-id":
                                                         "android:id/message"}):
            return False

        return adb_utils.is_text_displayed(serial=self.serial,
                                           text_to_find="You have incorrectly "
                                           "typed your PIN 5 times.")


class block_device_at_boot_time(adb_step):
    """ description:
            enters wrong PIN 10 times in a row at boot time using adb_steps

        usage:
            adb_steps.block_device_at_boot_time()()

        tags:
            ui, android, PIN
    """
    def __init__(self, pin="2222", **kwargs):
        self.pin = pin
        adb_step.__init__(self, **kwargs)

    def do(self):
        for i in range(0, 10):
            command(serial=self.serial,
                    command="input text {0}".format(self.pin))()
            command(serial=self.serial,
                    command="input keyevent KEYCODE_ENTER")()
            if i is not 9:
                wait_for_view(serial=self.serial,
                              view_to_find={"text": "Wrong PIN"})()

        wait_for_text(serial=self.serial,
                      text_to_find="To unlock")()

    def check_condition(self):
        return adb_utils.is_text_displayed(text_to_find="To unlock",
                                           serial=self.serial)
