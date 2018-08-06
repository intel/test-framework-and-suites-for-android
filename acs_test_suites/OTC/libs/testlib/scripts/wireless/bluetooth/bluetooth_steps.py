# !/usr/bin/env python
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

#######################################################################
#  @description: Bluetooth test steps
#  @author:      adrian.palko@intel.com
#  @author:      lucia.huru@intel.com
#  @author:      mihaela.maracine@intel.com
#######################################################################

import time
#  import os.path
import traceback

from testlib.base.base_step import step as base_step
from testlib.scripts.wireless.bluetooth.bt_step import Step as BtStep
from testlib.scripts.android.ui import ui_steps
from testlib.scripts.android.ui import ui_utils
# from testlib.scripts.wireless.bluetooth import bluetooth_utils


class GetAndroidVersion(BtStep):

    """ Description:
            Gets Android version via adb command (float type)
        Usage:
            bluetooth_steps.GetAndroidVersion(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = None
        self.set_errorm("Get version", "Could not obtain Android version")

    def do(self):
        try:
            self.step_data = self.adb_connection.cmd('shell getprop ro.build.version.release').communicate()[
                0].decode("utf-8").strip()
        except Exception, e:
            self.set_errorm("Get version", e.message)

    def check_condition(self):
        """
        :return: True if android version is successfully obtained, False if not. Version is saved in step_data as string
        """
        if self.step_data:
            self.set_passm("Android version " + str(self.step_data))
            return True
        else:
            return False


class ClickBluetoothSwitch(BtStep):

    """ Description:
            Only makes sure that the Bluetooth switch has the required state.
            Furthermore, if you call this function with check_if_already=True,
            if BT switch already has the required state, it returns failure.
            Call this from the Bluetooth Settings activity
        Usage:
            bluetooth_steps.ClickBluetoothSwitch(
                        state = "ON", check_if_already=False)()
    """

    def __init__(self, state="ON", check_if_already=False, **kwargs):
        """
        :param state: "ON" for on state required, OFF for off state required
        :param check_if_already: True to fail if already has the required state, False otherwise
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.state = state
        #  In some platform, state text is 'On' & 'Off', so covert to 'checked'
        self.checked = True if state == "ON" else False
        self.check_if_already = check_if_already
        self.switch = self.uidevice(className="android.widget.Switch", enabled=True)
        self.step_data = True
        self.set_passm("BT set to " + self.state)

    def do(self):
        try:
            #  check if switch is present
            if not self.switch.wait.exists(timeout=self.timeout):
                raise Exception("No BT switch found")
            if not self.switch.info["checked"] == self.checked:
                self.switch.click()
            else:
                #  check if already has required state
                if self.check_if_already:
                    raise Exception("BT already has " + self.state + " state")
                self.set_passm("BT already set to " + self.state)
        except Exception, e:
            self.set_errorm("Set BT to " + self.state, e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if required state was set, False if not
        """
        if self.step_data:
            #  wait for switch transition
            if not self.switch.wait.exists(timeout=self.timeout):
                self.set_errorm("Set BT to " + self.state, "BT state not set to " + self.state + " correctly")
                self.step_data = False
            else:
                #  check if it has required state
                if not self.uidevice(className="android.widget.Switch",
                                     enabled=True,
                                     checked=self.checked).wait.exists(
                        timeout=self.timeout):
                    self.set_errorm("Set BT to " + self.state, "BT state not set to " + self.state)
                    self.step_data = False
        return self.step_data


class OpenBluetoothSettings(BtStep):

    """ Description:
            Opens the Bluetooth activity from settings, either from all
            apps menu, or by sending an intent. Call this from the Home
            screen if use_intent=False
        Usage:
            bluetooth_steps.OpenBluetoothSettings(serial=serial, use_intent=False, version=version)()
    """

    def __init__(self, use_intent=False, **kwargs):
        """
        :param use_intent: True to open from the home screen, False to use BT settings launch intent
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.use_intent = use_intent
        self.step_data = True
        #  part of logging message
        if self.use_intent:
            self.message_str = "with intent"
        else:
            self.message_str = "from menu"
        self.set_passm("BT settings opened " + self.message_str)

    def do(self):
        try:
            if self.use_intent:
                #  execute start BT command if use_intent=True
                cmd_launch_bt_settings = "shell am start -a android.settings.BLUETOOTH_SETTINGS -p com.android.settings"
                self.adb_connection.cmd(cmd_launch_bt_settings).wait()
            else:
                ui_steps.open_settings(serial=self.serial)()
                ui_steps.click_button_if_exists(serial=self.serial,
                                                wait_time=5000, view_to_find={"text": "Connected devices"})()
                ui_steps.click_button_with_scroll(serial=self.serial,
                                                  view_to_find={"text": "Bluetooth"})()
        except Exception, e:
            self.set_errorm("Open " + self.message_str, e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if BT settings list was launched, False if not
        """
        if self.step_data:
            self.set_errorm("Open " + self.message_str, "BT settings was not opened")
            #  wait for the BT activity to open
            self.step_data = self.uidevice(text="Bluetooth").wait.exists(timeout=self.timeout)
        return self.step_data


class CheckBtVisibility(BtStep):

    """ Description:
            Checks if the device is visible. Call this from the BT settings list,
            with BT ON
        Usage:
            bluetooth_steps.CheckBtVisibility(serial=serial, version=version)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = True
        self.set_passm("DUT is visible")

    def do(self):
        if not ui_steps.wait_for_view_common(serial=self.serial,
                                             view_to_find={"textContains": "is visible"}, optional=True)():
            self.step_data = ui_steps.wait_for_view_common(serial=self.serial,
                                                           view_to_find={"textMatches": ".*?(v|V)isible.*?"})()

    def check_condition(self):
        """
        :return: True if BT is visible message was found on the screen, False if not
        """
        if not self.step_data:
            self.set_errorm("Check if visible",
                            "Check condition for Visibility has failed, 'visible' text can not" +
                            " be found on the screen")
            # self.step_data = self.uidevice(textContains=" is visible").wait.exists(timeout=self.timeout)
        return self.step_data


class WaitBtScanning(BtStep):

    """ Description:
            Makes sure that the BT scanning progress is finished, by waiting
            for progress bar to be gone. Call this from BT settings list,
            with BT on
        Usage:
            bluetooth_steps.WaitBtScanning(serial=serial,
                                timeout_appear=5000, time_to_wait=60000, version=version)()
    """

    def __init__(self, timeout_appear=5000, time_to_wait=60000, **kwargs):
        """
        :param timeout_appear: time to wait till the scanning progress bar appears
        :param time_to_wait: time to wait till the scanning progress bar is gone
        :param kwargs: serial, version, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.timeout_appear = timeout_appear
        self.time_to_wait = time_to_wait
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.step_data = True

    def do(self):
        if self.device_info.dessert < "O":
            try:
                if not self.bt_list.wait.exists(timeout=self.timeout_appear):
                    raise Exception("BT devices list was not found")
                #  scroll here to reveal scanning progressbar
                if not self.bt_list.scroll.to(text="Available devices"):
                    raise Exception("Available devices title was not found in BT list")
            except Exception, e:
                self.set_errorm("Wait scan finish", e.message)
                self.step_data = False
        else:
            time.sleep(15)

    def check_condition(self):
        """
        :return: True if BT scanning progress was finished after timeout reached, False if not
        """
        if self.device_info.dessert < "O" and self.step_data:
            progress_bar = self.uidevice(resourceId="com.android.settings:id/scanning_progress")
            if progress_bar.wait.exists(timeout=self.timeout_appear):
                self.set_passm("Scanning progress finished")
                self.set_errorm("Wait scan finish", "Timeout reached, still scanning")
                self.step_data = progress_bar.wait.gone(timeout=self.time_to_wait)
            else:
                self.set_passm("Scanning progress already finished")
                self.step_data = True
            return self.step_data


class GetBtMac(BtStep):

    """ Description:
            Get BT Address Mac via adb command
        Usage:
            bluetooth_steps.GetBtMac(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = None
        self.set_errorm("Obtain BT MAC", "Could not obtain BT MAC address")

    def do(self):
        try:
            self.step_data = self.adb_connection.cmd('shell settings get secure bluetooth_address').communicate()[
                0].decode("utf-8").strip()
        except Exception, e:
            self.set_errorm("Obtain BT MAC", e.message)

    def check_condition(self):
        """
        :return: True if bt mac was found, False if not. Note that the mac is saved in step_data
        """
        if self.step_data:
            self.set_passm("BT MAC address " + str(self.step_data))
            return True
        else:
            return False


class BtChangeDeviceName(BtStep):

    """ Description:
            Replaces the name of the devices with the given name, if not
            already named with the given name. If there is not any character
            given in the name, it validates that Rename button from the
            pop-up is disabled. Call this from the BT settings list, with
            BT ON
        Usage:
            bluetooth_steps.BtChangeDeviceName(serial=serial, name = "", version=version)()
    """

    def __init__(self, name="", **kwargs):
        """
        :param name: name to be set; if empty, it checks if the Rename button is disabled
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.name = name
        self.step_data = True
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")

    def do(self):
        try:
            if self.version.startswith("5.") or self.version.startswith("6.0"):
                #  LLP, M versions
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT devices list was not found")
                if not self.name == '':
                    #  check if BT does not already have the given name
                    if not self.bt_list.scroll.to(textContains="is visible to nearby devices"):
                        raise Exception("BT name was not found down of the list")
                    bt_check_object = self.uidevice(textContains="is visible to nearby devices")
                    condition = bt_check_object.info["text"].startswith(self.name + " is visible to nearby devices")
                else:
                    #  if empty name is given, do not need to check if not already
                    condition = False
                #  if BT does not already have given name, rename it
                if not condition:
                    #  open Rename pop-up
                    menu_button = self.uidevice(description="More options")
                    if not menu_button.wait.exists(timeout=self.timeout):
                        raise Exception("More options button in BT settings not found")
                    menu_button.click()
                    rename_button = self.uidevice(textContains="Rename ")
                    if not rename_button.wait.exists(timeout=self.timeout):
                        raise Exception("Rename option from the menu not found")
                    rename_button.click()
                    if not self.uidevice(resourceId="android:id/alertTitle", text="Rename this device").wait.exists(
                            timeout=self.timeout):
                        raise Exception("Rename DUT alert title not opened")
                    #  replace name
                    rename_edit_text = self.uidevice(className="android.widget.EditText")
                    '''if not rename_edit_text.wait.exists(timeout=self.timeout):
                        raise Exception("Rename Edit text not found")
                    rename_edit_text.set_text(self.name)
                    #  force a small delay due to window transition
                    time.sleep(1)
                    rename_button = self.uidevice(text="Rename")
                    if not rename_button.wait.exists(timeout=self.timeout):
                        raise Exception("Rename button from pop-up not found")
                        '''
                    ui_steps.edit_text(view_to_find={"className": "android.widget.EditText"}, value=self.name,
                                       serial=self.serial)()
                    rename_button = self.uidevice(text="Rename")
                    #  if given name is empty, check the status of Rename button and return to the BT list
                    if self.name == '':
                        if rename_edit_text.text:
                            raise Exception("Error when clearing old BT name, not empty")
                        if rename_button.enabled:
                            raise Exception("Rename button in popup not disabled when empty name")
                        cancel_button = self.uidevice(text="Cancel")
                        if not cancel_button.wait.exists(timeout=self.timeout):
                            raise Exception("Cancel button not found in Rename popup when empty name")
                        cancel_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after cancel rename BT with empty name")
                        self.set_passm("Rename button disabled when empty name")
                    #  if given name is not empty, rename it
                    else:
                        rename_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after renaming BT")
                        if not self.bt_list.scroll.to(textContains="is visible to nearby devices"):
                            raise Exception("BT name was not found down of the list after rename")
                        bt_check_object = self.uidevice(textContains="is visible to nearby devices")
                        if not bt_check_object.info["text"].startswith(self.name + " is visible to nearby devices"):
                            raise Exception("Found: " + bt_check_object.info["text"] + " instead of " + self.name)
                        self.set_passm("Device renamed: " + self.name)
                #  else pass, and write in the logs that device is already renamed
                else:
                    self.set_passm("Device already named: " + self.name)

            elif self.version.startswith("7."):
                #  N version
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT devices list was not found")
                if not self.name == '':
                    #  check if BT does not already have the given name
                    if not self.bt_list.scroll.to(textContains="is visible to nearby devices"):
                        raise Exception("BT name was not found down of the list")
                    bt_check_object = self.uidevice(textContains="is visible to nearby devices")
                    condition = bt_check_object.info["text"].startswith(self.name + " is visible to nearby devices")
                else:
                    #  if empty name is given, do not need to check if not already
                    condition = False
                #  if BT does not already have given name, rename it
                if not condition:
                    #  open Rename pop-up
                    menu_button = self.uidevice(description="More options")
                    if not menu_button.wait.exists(timeout=self.timeout):
                        raise Exception("More options button in BT settings not found")
                    menu_button.click()
                    rename_button = self.uidevice(textContains="Rename ")
                    if not rename_button.wait.exists(timeout=self.timeout):
                        raise Exception("Rename option from the menu not found")
                    rename_button.click()
                    if not self.uidevice(resourceId="android:id/alertTitle", text="Rename this device").wait.exists(
                            timeout=self.timeout):
                        raise Exception("Rename DUT alert title not opened")
                    #  force a small delay due to window transition and close keyboard
                    time.sleep(1)
                    if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[
                            0].decode("utf-8"):
                        self.uidevice.press.back()
                        time.sleep(1)
                    #  replace name
                    rename_edit_text = self.uidevice(className="android.widget.EditText")
                    '''if not rename_edit_text.wait.exists(timeout=self.timeout):
                        raise Exception("Rename Edit text not found")
                    rename_edit_text.set_text(self.name)
                    #  force a small delay due to window transition and close keyboard
                    time.sleep(1)
                    if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[
                        0].decode("utf-8"):
                        self.uidevice.press.back()
                        time.sleep(1)
                        '''
                    ui_steps.edit_text(view_to_find={"className": "android.widget.EditText"}, value=self.name,
                                       serial=self.serial)()
                    rename_button = self.uidevice(text="RENAME")
                    if not rename_button.wait.exists(timeout=self.timeout):
                        raise Exception("Rename button from pop-up not found")
                    #  if given name is empty, check the status of Rename button and return to the BT list
                    if self.name == '':
                        if rename_edit_text.text:
                            raise Exception("Error when clearing old BT name, not empty")
                        if rename_button.enabled:
                            raise Exception("Rename button in popup not disabled when empty name")
                        cancel_button = self.uidevice(text="CANCEL")
                        if not cancel_button.wait.exists(timeout=self.timeout):
                            raise Exception("Cancel button not found in Rename popup when empty name")
                        cancel_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after cancel rename BT with empty name")
                        self.set_passm("Rename button disabled when empty name")
                    #  if given name is not empty, rename it
                    else:
                        rename_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after renaming BT")
                        if not self.bt_list.scroll.to(textContains="is visible to nearby devices"):
                            raise Exception("BT name was not found down of the list after rename")
                        bt_check_object = self.uidevice(textContains="is visible to nearby devices")
                        if not bt_check_object.info["text"].startswith(self.name + " is visible to nearby devices"):
                            raise Exception("Found: " + bt_check_object.info["text"] + " instead of " + self.name)
                        self.set_passm("Device renamed: " + self.name)
                #  else pass, and write in the logs that device is already renamed
                else:
                    self.set_passm("Device already named: " + self.name)
            else:
                #  O-dessert version
                if not self.name == '':
                    #  check if BT does not already have the given name
                    if not self.bt_list.scroll.to(textContains="visible"):
                        raise Exception("BT name was not found down of the list")
                    bt_check_object = self.uidevice(textContains="Visible as")
                    condition = self.name in bt_check_object.info["text"]
                else:
                    #  if empty name is given, do not need to check if not already
                    condition = False
                #  if BT does not already have given name, rename it
                if not condition:
                    ui_steps.click_button_common(serial=self.serial,
                                                 view_to_find={"textContains": "Device name"})()
                    if not self.uidevice(resourceId="android:id/alertTitle", text="Rename this device").wait.exists(
                            timeout=self.timeout):
                        raise Exception("Rename DUT alert title not opened")
                    #  force a small delay due to window transition and close keyboard
                    time.sleep(1)
                    if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[
                            0].decode("utf-8"):
                        self.uidevice.press.back()
                        time.sleep(1)
                    #  replace name
                    rename_edit_text = self.uidevice(className="android.widget.EditText")
                    ui_steps.edit_text(view_to_find={"className": "android.widget.EditText"}, value=self.name,
                                       serial=self.serial)()
                    rename_button = self.uidevice(text="RENAME")
                    if not rename_button.wait.exists(timeout=self.timeout):
                        raise Exception("Rename button from pop-up not found")
                    #  if given name is empty, check the status of Rename button and return to the BT list
                    if self.name == '':
                        if rename_edit_text.text:
                            raise Exception("Error when clearing old BT name, not empty")
                        if rename_button.enabled:
                            raise Exception("Rename button in popup not disabled when empty name")
                        cancel_button = self.uidevice(text="CANCEL")
                        if not cancel_button.wait.exists(timeout=self.timeout):
                            raise Exception("Cancel button not found in Rename popup when empty name")
                        cancel_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after cancel rename BT with empty name")
                        self.set_passm("Rename button disabled when empty name")
                    #  if given name is not empty, rename it
                    else:
                        rename_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception("BT devices list not reached after renaming BT")
                        if not self.bt_list.scroll.to(textContains="visible"):
                            raise Exception("BT name was not found down of the list after rename")
                        self.set_passm("Device renamed: " + self.name)
                #  else pass, and write in the logs that device is already renamed
                else:
                    self.set_passm("Device already named: " + self.name)
                # self.set_passm("Device already named: " + self.name)
        except Exception, e:
            message = e.message
            if message is None or message == "":
                message = traceback.print_exc()
            self.set_errorm("Rename BT to " + self.name, message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if device was renamed(or Rename button is grayed out when empty name), False if not.
        """
        return self.step_data


class BtSearchDevices(BtStep):

    """ Description:
            Refreshes the BT available list until a certain device has
            appeared(for a max_attempt tries). Note that this let the BT
            list scrolled to the required device in the list. Call this in
            BT settings list, with BT ON and not any scanning in progress
        Usage:
            bluetooth_steps.BtSearchDevices(serial=serial,
                                dev_to_find="BT_test", scan_timeout=60000,
                                max_attempts=1, version=version)()
    """

    def __init__(self, dev_to_find, scan_timeout=60000, max_attempts=1, **kwargs):
        """
        :param dev_to_find: name of the device to be found
        :param scan_timeout: maximum timeout for scanning progress
        :param max_attempts: maximum no. of tries
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.dev_to_find = dev_to_find
        self.scan_timeout = scan_timeout
        self.max_attempts = max_attempts
        self.step_data = True
        #  if self.version.startswith("5.") or self.version.startswith("6.0"):
        #     self.bt_list = self.uidevice(resourceId="android:id/list")
        #     self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")

    def do(self):
        try:
            #  if not self.uidevice(text="Available devices").wait.exists(timeout=self.timeout):
            #     raise Exception("BT devices list was not found")
            counter = 1
            #  condition = True means that the device was found
            condition = False
            while not condition:
                #  break if max_attempts reached
                if counter > self.max_attempts:
                    break
                if self.device_info.dessert < 'O':
                    #  open More options menu and click Refresh
                    menu_button = self.uidevice(description="More options")
                    if not menu_button.wait.exists(timeout=self.timeout):
                        raise Exception("Try " + str(counter) + ": More options button in BT settings not found")
                    menu_button.click()
                    refresh_button = self.uidevice(text="Refresh")
                    if not refresh_button.wait.exists(timeout=self.scan_timeout):
                        raise Exception("Try " + str(counter) + ": Refresh button was not found")
                    refresh_button.click()
                else:
                    if counter != 1:
                        self.uidevice.press.back()
                    ui_steps.click_button_common(serial=self.serial,
                                                 view_to_find={"text": "Pair new device"}, optional=True)()
                #  if not self.bt_list.wait.exists(timeout=self.timeout):
                #     raise Exception("Try " + str(counter) + ": BT devices list was not found")
                #  wait until scanning process is finished
                if not WaitBtScanning(serial=self.serial,
                                      time_to_wait=self.scan_timeout, critical=False,
                                      version=self.version)():
                    raise Exception("Wait for scanning to finish failed")
                counter += 1
                #  check if device was found, if not, perform again the while loop
                condition = ui_steps.wait_for_view_common(serial=self.serial,
                                                          view_to_find={"text": self.dev_to_find}, optional=True)()
            self.set_passm("Device " + self.dev_to_find + " found after " + str(
                counter - 1) + " attempt(s)")
        except Exception, e:
            self.set_errorm("Scan after " + self.dev_to_find, e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if device was found, False if not.
        """
        if self.step_data:
            #  returns if the device is on the screen, or not
            self.set_errorm("Scan after " + self.dev_to_find,
                            "Search failed, device " + self.dev_to_find + " was not found in Available devices" +
                            " list after " + str(self.max_attempts) + " attempt(s)")
            self.step_data = self.uidevice(text=self.dev_to_find).exists
        return self.step_data


class GetPasskey(BtStep):

    """ Description:
            Get the pairing code from the pair request window. Call this in
            the Pairing request window
        Usage:
            bluetooth_steps.GetPasskey(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = None
        self.set_errorm("Get passkey from Pair request", "Could not obtain passkey")

    def do(self):
        try:
            passkey_object = self.uidevice(resourceId="com.android.settings:id/pairing_subhead")
            if not passkey_object.exists:
                raise Exception("Pairing code not displayed")
            #  save the passkey in step_data
            self.step_data = passkey_object.text
        except Exception, e:
            self.set_errorm("Get passkey from Pair request", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if passkey was found, False if not. Note that the passkey is saved as str in step_data
        """
        if self.step_data:
            self.set_passm("Passkey " + str(self.step_data))
            return True
        else:
            return False


class PasskeyCheck(BtStep):

    """ Description:
            This method checks if the pairing request passkeys are both
            on the initiator and on the receiver
        Usage:
            bluetooth_steps.PasskeyCheck(serial=serial, passkey_initiator=passkey1,
                                            passkey_receiver=passkey2)()
     """

    def __init__(self, passkey_initiator, passkey_receiver, **kwargs):
        """
        :param passkey_initiator: passkey of the initiator device
        :param passkey_receiver: passkey of the receiver device
        :param kwargs: standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.passkey_initiator = passkey_initiator
        self.passkey_receiver = passkey_receiver
        self.set_passm("Pairing code matches; " + str(self.passkey_initiator) + " = " + str(self.passkey_receiver))
        self.set_errorm("Pairing code does not match",
                        "Initiator: " + str(self.passkey_initiator) + " Receiver: " + str(self.passkey_initiator))

    def do(self):
        #  do nothing, only check
        pass

    def check_condition(self):
        """
        :return: True if passkeys match, False if not.
        """
        return self.passkey_initiator == self.passkey_receiver


class CheckIfPaired(BtStep):

    """ Description:
            Checks if the device is paired, or not(depending on the paired parameter)
            with another device. Call this with the BT list opened
        Usage:
            bluetooth_steps.CheckIfPaired(serial=serial,
                            dev_paired_with = DEVNAME, paired=True, version=version)()
    """

    def __init__(self, dev_paired_with, paired=True, **kwargs):
        """
        :param dev_paired_with: name of the device to check if DUT is(not) paired with
        :param paired: True, to check if DUT is paired with, False, to check if DUT is not paired with
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.dev_paired_with = dev_paired_with
        self.paired = paired
        self.step_data = True
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        if self.paired:
            self.message_str = "Check if paired"
            self.set_passm("Paired with " + str(dev_paired_with))
            self.set_errorm(self.message_str, "Not paired with " + str(dev_paired_with))
        else:
            self.message_str = "Check if not paired"
            self.set_passm("Not paired with " + str(dev_paired_with))
            self.set_errorm(self.message_str, "Paired with " + str(dev_paired_with))

    def do(self):
        try:
            if self.device_info.dessert < "O":
                if self.uidevice(text="YES").wait.exists(timeout=1000):
                    self.uidevice(text="YES").click()
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT list not found")
                if self.bt_list.scroll.to(text=self.dev_paired_with):
                    device_layout = self.bt_list.child_by_text(self.dev_paired_with, allow_scroll_search=False,
                                                               className="android.widget.LinearLayout")
                    if self.paired:
                        if not device_layout.child(resourceId="com.android.settings:id/deviceDetails").wait.exists(
                                timeout=self.timeout):
                            self.step_data = False
                    else:
                        if not device_layout.child(resourceId="com.android.settings:id/deviceDetails").wait.gone(
                                timeout=self.timeout):
                            self.step_data = False
                else:
                    if self.paired:
                        self.step_data = False
            else:
                condition = False
                condition = ui_steps.wait_for_view_common(serial=self.serial,
                                                          view_to_find={"textContains": self.dev_paired_with},
                                                          second_view_to_find={
                                                              "resourceId": "com.android.settings:id/settings_button"},
                                                          position='right', optional=True)()
                if self.paired:
                    if condition:
                        self.step_data = True
                    else:
                        self.step_data = False
                else:
                    if condition:
                        self.step_data = False
                    else:
                        self.step_data = True
        except Exception, e:
            self.set_errorm(self.message_str, e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if DUT is paired (or not, depending on Paired=True/False) with required device, False otherwise
        """
        return self.step_data


class WaitPairRequest(BtStep):

    """ Description:
            Waits for the pair request alert to appear or to be gone,
            as defined by parameter appear=True/False.
        Usage:
            bluetooth_steps.WaitPairRequest(serial=serial,
                                    appear=True, time_to_wait=10000, version=version)()
    """

    def __init__(self, appear=True, time_to_wait=10000, **kwargs):
        """
        :param appear: True, to check if appears, False, to check if gone
        :param time_to_wait: maximum time to wait for pairing request window
        :param kwargs: serial, version, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.appear = appear
        self.time_to_wait = time_to_wait
        if self.appear:
            self.set_passm("Pair request appeared")
            self.set_errorm("Wait pair request window",
                            "Pair request not appeared after " + str(self.time_to_wait) + " milliseconds")
        else:
            self.set_passm("Pair request gone")
            self.set_errorm("Wait pair request window gone",
                            "Pair request not gone after " + str(self.time_to_wait) + " milliseconds")

    def do(self):
        #  nothing to do here, only to check
        pass

    def check_condition(self):
        """
        :return: True if pairing request window appears(or is gone), False otherwise
        """
        if self.version.startswith("5."):
            #  LLP version
            if self.appear:
                #  wait for appear of pair request dialog
                self.step_data = self.uidevice(resourceId="android:id/alertTitle",
                                               text="Bluetooth pairing request").wait.exists(timeout=self.time_to_wait)
            else:
                #  wait until pair request dialog disappears
                self.step_data = self.uidevice(resourceId="android:id/alertTitle",
                                               text="Bluetooth pairing request").wait.gone(timeout=self.time_to_wait)
        else:
            #  M version
            if self.appear:
                #  wait for appear of pair request dialog
                self.step_data = self.uidevice(resourceId="android:id/alertTitle",
                                               textContains="Pair with").wait.exists(timeout=self.time_to_wait)
            else:
                #  wait until pair request dialog disappears
                self.step_data = self.uidevice(resourceId="android:id/alertTitle",
                                               textContains="Pair with").wait.gone(timeout=self.time_to_wait)
        return self.step_data


class InitiatePairRequest(BtStep):

    """ Description:
            Initiate a pair request. It searches for the device name, clicks on it and assures
            that the initiator device is in the pairing request window (i.e. if pair request window
            is not displayed on the screen, it checks if the "Cannot communicate" message is displayed,
            and if not, it searches the request in the notifications menu)
        Usage:
            bluetooth_steps.InitiatePairRequest(serial=serial, dev_to_pair_name="Name",
                        scan_timeout=60000, scan_max_attempts=1, version=version)()
    """

    def __init__(self, dev_to_pair_name, scan_timeout=60000, scan_max_attempts=1, **kwargs):
        """
        :param dev_to_pair_name: name of device to pair with
        :param scan_timeout: maximum timeout for scanning progress
        :param scan_max_attempts: maximum no. of scan tries till the device is found
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.dev_to_pair_name = dev_to_pair_name
        self.scan_timeout = scan_timeout
        self.scan_max_attempts = scan_max_attempts
        self.step_data = True
        self.set_passm("Pair request initiated to " + str(dev_to_pair_name))

    def do(self):
        try:
            #  search for required device
            if not BtSearchDevices(serial=self.serial, dev_to_find=self.dev_to_pair_name,
                                   scan_timeout=self.scan_timeout,
                                   timeout=self.timeout, max_attempts=self.scan_max_attempts, version=self.version,
                                   critical=False)():
                raise Exception("Search for device failed")
            #  click on the device name (already scrolled in the view)
            self.uidevice(text=self.dev_to_pair_name).click()

            if self.version.startswith("5."):
                #  LLP version
                #  if pair request window not appear on the device, open notification and check
                #  if there is not even there the pairing request
                if not self.uidevice(resourceId="android:id/alertTitle",
                                     text="Bluetooth pairing request").wait.exists(timeout=5000):
                    if self.uidevice(textContains="Can't communicate with").exists:
                        raise Exception(
                            "Pair request not initiated from DUT because can't communicate with other one device")
                    if not SearchPairRequestNotification(serial=self.serial, timeout=self.timeout, version=self.version,
                                                         critical=False, no_log=True)():
                        raise Exception(
                            "Pair request not appeared on the screen, also failed" +
                            " searching it in notifications menu")
                    if not WaitPairRequest(serial=self.serial, appear=True, time_to_wait=self.timeout,
                                           version=self.version, critical=False, no_log=True)():
                        raise Exception("Pair request not initiated")
                if not self.uidevice(resourceId="com.android.settings:id/message_subhead",
                                     text=self.dev_to_pair_name).wait.exists(timeout=self.timeout):
                    raise Exception("Pair request not initiated to the expected device")
            else:
                #  M, N version
                #  if pair request window not appear on the device, open notification and check
                #  if there is not even there the pairing request
                pair_request_title_obj = self.uidevice(resourceId="android:id/alertTitle", textContains="Pair with")
                if not pair_request_title_obj.wait.exists(timeout=5000):
                    if self.uidevice(textContains="Can't communicate with").exists:
                        raise Exception(
                            "Pair request not initiated from DUT because can't communicate with other one device")
                    if self.device_info.dessert < "O":
                        if not SearchPairRequestNotification(serial=self.serial, timeout=self.timeout,
                                                             version=self.version, critical=False, no_log=True)():
                            raise Exception(
                                "Pair request not appeared on the screen, also failed" +
                                " searching it in notifications menu")
                        if not WaitPairRequest(serial=self.serial, appear=True, time_to_wait=self.timeout,
                                               version=self.version, critical=False, no_log=True)():
                            raise Exception("Pair request not initiated")
                pair_request_title_str = pair_request_title_obj.text
                if not pair_request_title_str == "Pair with " + str(self.dev_to_pair_name) + "?":
                    raise Exception(
                        "Pair request not initiated to the expected device, found " + str(pair_request_title_str))
        except Exception, e:
            self.set_errorm("Pair request to " + str(self.dev_to_pair_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Both devices are in the pair request window, False otherwise
        """
        return self.step_data


class PairDevice(BtStep):

    """ Description:
            Initiate a pair request. It searches for the device name, clicks on it and assures
            that the initiator device is in the pairing request window (i.e. if pair request window
            is not displayed on the screen, it checks if the "Cannot communicate" message is displayed,
            and checks device name paired or not to DUT, If paired returns true)
        Usage:
            bluetooth_steps.PairDevice(serial=serial, dev_to_pair_name="Name",
                        scan_timeout=60000, scan_max_attempts=1, version=version)()
    """

    def __init__(self, dev_to_pair_name, scan_timeout=60000, scan_max_attempts=1, **kwargs):
        """
        :param dev_to_pair_name: name of device to pair with
        :param scan_timeout: maximum timeout for scanning progress
        :param scan_max_attempts: maximum no. of scan tries till the device is found
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.dev_to_pair_name = dev_to_pair_name
        self.scan_timeout = scan_timeout
        self.scan_max_attempts = scan_max_attempts
        self.step_data = True
        self.set_passm("Paired with " + str(dev_to_pair_name))

    def do(self):
        try:
            #  search for required device
            if not BtSearchDevices(serial=self.serial, dev_to_find=self.dev_to_pair_name,
                                   scan_timeout=self.scan_timeout,
                                   timeout=self.timeout, max_attempts=self.scan_max_attempts, version=self.version,
                                   critical=False)():
                raise Exception("Search for device failed")
            #  click on the device name (already scrolled in the view)
            self.uidevice(text=self.dev_to_pair_name).click()
            if self.version.startswith("5."):
                #  LLP version
                #  if pair request window not appear on the device, open notification and check
                #  if there is not even there the pairing request
                if not self.uidevice(resourceId="android:id/alertTitle",
                                     text="Bluetooth pairing request").wait.exists(timeout=5000):
                    if self.uidevice(textContains="Can't communicate with").exists:
                        raise Exception(
                            "Pair request not initiated from DUT because can't communicate with other one device")
            else:
                #  M, N version
                #  if pair request window not appear on the device, open notification and check
                #  if there is not even there the pairing request
                pair_request_title_obj = self.uidevice(resourceId="android:id/alertTitle", textContains="Pair with")
                if not pair_request_title_obj.wait.exists(timeout=5000):
                    if self.uidevice(textContains="Can't communicate with").exists:
                        raise Exception(
                            "Pair request not initiated from DUT because can't communicate with other one device")
        except Exception, e:
            self.set_errorm("Pair request to " + str(self.dev_to_pair_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device was paired, False if not
        """
        if self.step_data:
            #  check if is  paired with required device
            self.step_data = CheckIfPaired(serial=self.serial, dev_paired_with=self.dev_to_pair_name, paired=True,
                                           timeout=self.timeout, version=self.version, critical=False)()
        return self.step_data


class ReceivePairRequest(BtStep):

    """ Description:
            Receives a pair request. It assures that device is
            in the pairing request window (i.e. if pair request window
            is not received on the screen, it searches it in the
            notifications menu)
        Usage:
            bluetooth_steps.ReceivePairRequest(serial=serial,
                        dev_receiving_from_name="Name", version=version)()
    """

    def __init__(self, dev_receiving_from_name, **kwargs):
        """
        :param dev_receiving_from_name: name of the device receiving pair request from
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.dev_receiving_from_name = dev_receiving_from_name
        self.step_data = True
        self.set_passm("Pair request received from " + str(self.dev_receiving_from_name))

    def do(self):
        try:
            if self.version.startswith("5."):
                #  LLP version
                #  if pair request window not appear on the receiver device, open notification and check if
                #  there is not even there the pairing request
                if not self.uidevice(resourceId="android:id/alertTitle", text="Bluetooth pairing request").wait.exists(
                        timeout=5000):
                    if not SearchPairRequestNotification(serial=self.serial, timeout=self.timeout, version=self.version,
                                                         critical=False)():
                        raise Exception(
                            "Pair request not received on the screen, also failed" +
                            " searching it in notifications menu")
                    if not WaitPairRequest(serial=self.serial, appear=True, time_to_wait=self.timeout,
                                           version=self.version, critical=False)():
                        raise Exception("Pair request not received")
                if not self.uidevice(resourceId="com.android.settings:id/message_subhead",
                                     text=self.dev_receiving_from_name).wait.exists(timeout=self.timeout):
                    raise Exception("Pair request not received from the expected device")
            else:
                #  M, N version
                #  if pair request window not appear on the receiver device, open notification and check if
                #  there is not even there the pairing request
                pair_request_title_obj = self.uidevice(resourceId="android:id/alertTitle", textContains="Pair with")
                if not pair_request_title_obj.wait.exists(timeout=5000):
                    if not SearchPairRequestNotification(serial=self.serial, timeout=self.timeout, version=self.version,
                                                         critical=False, no_log=True)():
                        raise Exception(
                            "Pair request not received on the screen, also failed" +
                            " searching it in notifications menu")
                    if not WaitPairRequest(serial=self.serial, appear=True, time_to_wait=self.timeout,
                                           verion=self.version, critical=False, no_log=True)():
                        raise Exception("Pair request not received on device")
                pair_request_title_str = pair_request_title_obj.text
                if not pair_request_title_str == "Pair with " + str(self.dev_receiving_from_name) + "?":
                    raise Exception(
                        "Pair request not received from the expected device, found " + str(pair_request_title_str))
        except Exception, e:
            self.set_errorm("Pair request from " + str(self.dev_receiving_from_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Both devices are in the pair request window, False otherwise
        """
        return self.step_data


class SearchPairRequestNotification(BtStep):

    """ Description:
            Opens a Pairing request from the notification menu. Note that
            this does not check if, indeed the pairing request dialog appears,
            it only clicks the notification. Call this only if the request
            dialog is not displayed and it should be
        Usage:
            bluetooth_steps.SearchPairRequestNotification(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = True
        self.set_passm("Pairing request notification clicked")

    def do(self):
        try:
            #  open notification menu
            if not OpenNotificationsMenu(serial=self.serial, timeout=self.timeout, version=self.version, critical=False,
                                         no_log=True)():
                raise Exception("Notification menu not opened when searching for pairing request")
            #  click on the pairing request notification
            if not BtCheckNotificationAppear(serial=self.serial, text_contains="Pairing request",
                                             click_on_notification=True, time_to_appear=self.timeout,
                                             version=self.version, critical=False, no_log=True)():
                raise Exception("Check Pair request notification not successful")
        except Exception, e:
            self.set_errorm("Search pair request in notifications ", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Pair request notification was found and clicked, False otherwise
        """
        return self.step_data


class OpenNotificationsMenu(BtStep):

    """ Description:
            Opens the notifications menu in order to operate with Bluetooth notifications
        Usage:
            bluetooth_steps.OpenNotificationsMenu(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.set_passm("Notifications menu opened")
        self.set_errorm("Open notifications", "Notifications menu not opened")

    def do(self):
        self.uidevice.open.notification()
        #  sleep here for transition to be finished
        time.sleep(2)

    def check_condition(self):
        """
        :return: True if Notifications menu was opened, False otherwise
        """
        self.step_data = self.uidevice(resourceId="com.android.systemui:id/notification_stack_scroller").wait.exists(
            timeout=self.timeout)
        # self.step_data = True
        return self.step_data


class CloseNotificationsMenu(BtStep):

    """ Description:
            Closes the notifications menu
        Usage:
            bluetooth_steps.CloseNotificationsMenu(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = True
        self.notifications_menu = self.uidevice(resourceId="com.android.systemui:id/notification_stack_scroller")
        self.set_passm("Notifications menu closed")
        self.set_errorm("Close notifications", "Notifications menu not gone")

    def do(self):
        try:
            if not self.notifications_menu.exists:
                raise Exception("Notifications menu is not already opened")
            self.uidevice.press.back()
        except Exception, e:
            self.set_errorm("Close notifications", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Notifications menu was closed, False otherwise
        """
        if self.step_data:
            self.step_data = self.notifications_menu.wait.gone(timeout=self.timeout)
        return self.step_data


class PerformActionPairRequest(BtStep):

    """ Description:
            Performs a click on the button with label exact text as defined by
            action parameter and checks if the pair request window is gone. If
            the action is 'Timeout', it only waits for pair request window to be
            gone, the amount of time as defined by timeout parameter. Call this
            only when Pair request window is already shown
        Usage:
            bluetooth_steps.PerformActionPairRequest(serial=serial,
                                                        action="Pair", version=version)()
    """

    def __init__(self, action="Pair", **kwargs):
        """
        :param action: "Pair"/"Cancel"/"Timeout" action to be performed
        :param kwargs: serial, timeout, version, no_log,  and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        if action not in ["Cancel", "Pair", "Timeout"]:
            raise Exception("Config error: not any expected value for action")

        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.action = action
        else:
            #  N version
            self.action = action.upper()
        self.step_data = True
        self.set_passm("Action " + str(self.action) + " successful")
        self.set_errorm("Action " + str(self.action), "Pair request window not gone after action performed")

    def do(self):
        try:
            #  if action is not Timeout, perform click on the button
            if self.action.upper() != "TIMEOUT":
                action_button = self.uidevice(text=self.action)
                if not action_button.wait.exists(timeout=self.timeout + 30000):
                    raise Exception("Button " + str(self.action) + " not found")
                action_button.click()
            if self.uidevice(text="YES").wait.exists(timeout=1000):
                self.uidevice(text="YES").click()
        except Exception, e:
            self.set_errorm("Action " + str(self.action), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if pair request window is gone, False if not
        """
        if self.step_data:
            #  check if the pair request window is gone
            self.step_data = WaitPairRequest(serial=self.serial, appear=False, time_to_wait=self.timeout,
                                             version=self.version, critical=False)()
        return self.step_data


class CouldNotPairDialogCheck(BtStep):

    """ Description:
            Checks if the "Couldn't pair" dialog is displayed
            (by waiting for it) and clicks on it's OK button.
        Usage:
            bluetooth_steps.CouldNotPairDialogCheck(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = True
        self.set_passm("Dialog appeared, canceled successful")
        self.set_errorm("Could not pair dialog", "Not canceled successfully")
        self.dialog_window = self.uidevice(resourceId="android:id/message", textContains="incorrect PIN or passkey")

    def do(self):
        try:
            if self.device_info.dessert < "O":
                #  wait for dialog to appear
                if not self.dialog_window.wait.exists(timeout=self.timeout + 30000):
                    raise Exception("Dialog not appeared")
                #  click on it's OK button
                ok_button = self.uidevice(text="OK")
                if not ok_button.wait.exists(timeout=self.timeout + 30000):
                    raise Exception("OK not found in the dialog")
                ok_button.click()
            else:
                pass
                #  in O dialog box disappears automatically, we are not checking dialog box for greater than O dessert
        except Exception, e:
            self.set_errorm("Could not pair dialog", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Could not pair dialog is gone after press on OK, False otherwise
        """
        if self.step_data:
            #  check if dialog is gone
            self.step_data = self.dialog_window.wait.gone(timeout=self.timeout)
        return self.step_data


class BtRemoveAllPairedDevices(BtStep):

    """ Description:
            All pair devices will be removed from the list. Call this in BT
            devices list, with no scanning in progress
        Usage:
            bluetooth_steps.BtRemoveAllPairedDevices(serial = serial,
                                            max_attempts=20, version=version)()
    """

    def __init__(self, max_attempts=20, **kwargs):
        """
        :param max_attempts: maximum no. of tries
        :param kwargs: serial, version, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.max_attempts = max_attempts
        self.paired_title = self.uidevice(text="Paired devices")
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.step_data = True
        self.set_passm("Nothing to unpair")
        self.set_errorm(str(max_attempts) + "attempts", "Not removed all paired devices")

    def do(self):
        try:
            if self.version.startswith("5.") or self.version.startswith("6.") or self.version.startswith("7."):
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT devices list was not found")
                #  execute only if Paired devices title is found
                if self.bt_list.scroll.to(text="Paired devices"):
                    counter = 1
                    #  for each existing paired button, click on it and FORGET
                    while self.paired_title.exists:
                        if counter > self.max_attempts:
                            break
                        paired_button = self.uidevice(description="Device settings")
                        paired_button.click.wait()
                        time.sleep(1)
                        if not self.uidevice(resourceId="android:id/alertTitle").wait.exists(timeout=self.timeout):
                            raise Exception(
                                "Alert title not opened when removing " + " (device no. " + str(
                                    counter) + ")")
                        if self.version.startswith("5."):
                            #  LLP version
                            forget_button = self.uidevice(resourceId="android:id/button2", text="FORGET")
                        elif self.version.startswith("6.0"):
                            #  M version
                            forget_button = self.uidevice(resourceId="android:id/button2", text="Forget")
                            #  force a small delay due to window transition
                            time.sleep(1)
                        else:
                            #  N version
                            #  force a small delay due to window transition and close keyboard
                            time.sleep(1)
                            if "mInputShown=true" in self.adb_connection.cmd(
                                    "shell dumpsys input_method").communicate()[0].decode("utf-8"):
                                self.uidevice.press.back()
                                time.sleep(1)
                            forget_button = self.uidevice(text="FORGET")
                        if not forget_button.wait.exists(timeout=self.timeout):
                            raise Exception(
                                "Forget button not found when unpair " + " (device no. " + str(
                                    counter) + ")")
                        forget_button.click()
                        if not self.bt_list.wait.exists(timeout=self.timeout):
                            raise Exception(
                                "Not returned to BT list after unpair " + " (device no. " + str(
                                    counter) + ")")
                        counter += 1
                    self.set_passm(str(counter - 1) + " device(s) unpaired")
            else:
                counter = 1
                #  for each existing paired button, click on it and FORGET
                while self.paired_title.exists and self.uidevice(description="Settings"):
                    if counter > self.max_attempts:
                        break
                    ui_steps.click_button_common(serial=self.serial,
                                                 view_to_find={"description": "Settings"},
                                                 view_to_check={"resourceId": "android:id/alertTitle"})()
                    time.sleep(1)
                    if not ui_steps.click_button_common(serial=self.serial,
                                                        view_to_find={"text": "FORGET"})():
                        raise Exception("Forget button not found when unpair " + " (device no. " + str(counter) + ")")
                    counter += 1
                    self.set_passm(str(counter - 1) + " device(s) unpaired")

        except Exception, e:
            self.set_errorm("Unpair devices", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if all paired devices were unpaired, False otherwise
        """
        if self.step_data and self.device_info.dessert < "O":
            #  check if "Paired devices" title is gone
            self.step_data = self.uidevice(text="Paired devices").wait.gone(timeout=self.timeout)
        else:
            self.step_data = self.uidevice(description="Settings").wait.gone(timeout=self.timeout)
        return self.step_data


class OpenPairedDeviceSettings(BtStep):

    """ Description:
            Open the device settings alert title for a certain paired device.
            Call this in BT settings list for a device a device already
            paired
        Usage:
            bluetooth_steps.OpenPairedDeviceSettings(serial = serial,
                                        device_name="DEV_name", version=version)()
    """

    def __init__(self, device_name, **kwargs):
        """
        :param device_name: name of device in the list for which Settings should be opened
        :param kwargs: serial, version, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.device_name = device_name
        self.step_data = True
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.set_passm("Device settings opened for device " + str(self.device_name))
        self.set_errorm("Paired device settings for " + str(self.device_name), "Device settings not opened")

    def do(self):
        try:
            if self.device_info.dessert < "O":
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT list not found")
                if not self.bt_list.scroll.to(text=self.device_name):
                    raise Exception("Device " + str(self.device_name) + " not found in BT list")
                #  get linear layout corresponding to required device
                device_layout = self.bt_list.child_by_text(self.device_name, allow_scroll_search=False,
                                                           className="android.widget.LinearLayout")
                #  get the device settings button corresponding to required device by searching the child of the linear
                #  layout
                device_settings_button = device_layout.child(resourceId="com.android.settings:id/deviceDetails")
                if not device_settings_button.wait.exists(timeout=self.timeout):
                    raise Exception("Device settings button not found")
                #  click on device settings
                device_settings_button.click()
                if self.version.startswith("5.") or self.version.startswith("6.0"):
                    #  LLP, M versions
                    #  do nothing, no workaround needed
                    pass
                else:
                    #  N version workaround
                    if not self.uidevice(resourceId="android:id/alertTitle", text="Paired devices").wait.exists(
                            timeout=self.timeout + 30000):
                        raise Exception("Device settings not opened")
                    #  force a small delay due to window transition and close keyboard
                    time.sleep(1)
                    if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[
                            0].decode("utf-8"):
                        self.uidevice.press.back()
                        time.sleep(1)
            else:
                paired_button = self.uidevice(description="Settings")
                paired_button.click.wait()
                time.sleep(1)
                if not self.uidevice(resourceId="android:id/alertTitle").wait.exists(timeout=self.timeout):
                    raise Exception("Alert title not opened when removing")
                    #  O version
                    #  force a small delay due to window transition and close keyboard
                time.sleep(1)
                if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[0].decode(
                        "utf-8"):
                    self.uidevice.press.back()
        except Exception, e:
            self.set_errorm("Paired device settings for " + str(self.device_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device settings was opened, False otherwise
        """
        if self.step_data:
            #  check if Device settings window is opened
            self.step_data = self.uidevice(resourceId="android:id/alertTitle", text="Paired devices").wait.exists(
                timeout=self.timeout)
        return self.step_data


class UnpairDevice(BtStep):

    """ Description:
            Unpair a certain device from the list.Call this in BT settings
            list for a device a device already paired
        Usage:
            bluetooth_steps.UnpairDevice(serial = serial,
                                    device_name="DEV_name", version=version)()
    """

    def __init__(self, device_name, **kwargs):
        """
        :param device_name: name of device from the list to be unpaired
        :param kwargs: serial, timeout, version, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.device_name = device_name
        self.step_data = True
        if self.version.startswith("5.") or self.version.startswith("6.0"):
            #  LLP, M versions
            self.bt_list = self.uidevice(resourceId="android:id/list")
        else:
            #  N version
            self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.set_passm("Device " + str(self.device_name) + " unpaired")
        self.set_errorm("Unpair device " + str(self.device_name), "Device is still paired")

    def do(self):
        try:
            if not OpenPairedDeviceSettings(serial=self.serial, device_name=self.device_name, timeout=self.timeout,
                                            version=self.version, critical=False)():
                raise Exception("Open paired device settings failed")
            if not self.uidevice(text=self.device_name):
                raise Exception("Name of the device not found in the unpair alert window")
            #  click on forget
            if self.version.startswith("5."):
                #  LLP version
                forget_button = self.uidevice(resourceId="android:id/button2", text="FORGET")
            elif self.version.startswith("6.0"):
                #  M version
                forget_button = self.uidevice(resourceId="android:id/button2", text="Forget")
                #  force a small delay due to window transition
                time.sleep(1)
            else:
                #  N version
                forget_button = self.uidevice(text="FORGET")
            if not forget_button.wait.exists(timeout=self.timeout):
                raise Exception("Forget button not found when unpairing device")
            forget_button.click()
            if not self.bt_list.wait.exists(timeout=self.timeout):
                raise Exception("Not returned to BT list after unpairing device")
        except Exception, e:
            self.set_errorm("Unpair device " + str(self.device_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device was unpaired, False if not
        """
        if self.step_data:
            #  check if is not paired with required device
            self.step_data = CheckIfPaired(serial=self.serial, dev_paired_with=self.device_name, paired=False,
                                           timeout=self.timeout, version=self.version, critical=False)()
        return self.step_data


class DisconnectDevice(BtStep):

    """ Description:
            disconnect a certain device from the list and still it will be paired
        Usage:
            bluetooth_steps.DisconnectDevice(serial = serial,
                                    device_name="DEV_name", version=version)()
    """

    def __init__(self, device_name, **kwargs):
        """
        :param device_name: name of device from the list to be disconnected
        :param kwargs: serial, timeout, version, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.device_name = device_name
        self.step_data = True
        self.set_passm("Device " + str(self.device_name) + " Disconnected and still will be paired")
        self.set_errorm("DisconnectDevice" + str(self.device_name), "Device is still connected")

    def do(self):
        try:
            if ui_steps.click_button_common(serial=self.serial, view_to_find={"textContains": self.device_name},
                                            view_to_check={"resourceId": "android:id/alertTitle"})():
                if not ui_steps.click_button_common(serial=self.serial, view_to_find={"textContains": "ok"})():
                    self.step_data = False
            else:
                self.step_data = False

        except Exception, e:
            self.set_errorm("Disconnect device " + str(self.device_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device was paired, False if not
        """
        if self.step_data:
            #  check if is not paired with required device
            self.step_data = CheckIfPaired(serial=self.serial, dev_paired_with=self.device_name, paired=True,
                                           timeout=self.timeout, version=self.version, critical=False)()
        return self.step_data


class BtCheckNotificationAppear(BtStep):

    """ Description:
            Checks if a Bluetooth notification appeared (searching for a
            textContains selector). You have two options: click on
            notification (and validates that the notification menu is gone),
            or only check if appeared. Call this with notification menu
            already opened
        Usage:
            bluetooth_steps.BtCheckNotificationAppear(serial=serial,
                        text_contains="text_contained_into_notification_title",
                        click_on_notification=False, time_to_appear=60000)()
    """

    def __init__(self, text_contains, click_on_notification=False, time_to_appear=60000, **kwargs):
        """
        :param text_contains: text contained in the notification to check
        :param click_on_notification: True-click on notification. False-only check
        :param time_to_appear: max time to wait till notification appears
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.text_contains = text_contains
        self.click_on_notification = click_on_notification
        self.time_to_appear = time_to_appear
        self.step_data = True
        self.notification = self.uidevice(resourceId="android:id/notification_main_column").child(
            textContains=self.text_contains)
        if self.click_on_notification:
            self.set_passm("Notification '" + str(
                self.text_contains) + "' found, clicked on it successful")
        else:
            self.set_passm("Notification '" + str(self.text_contains) + "' found")

    def do(self):
        try:
            #  check if notification appeared
            if not self.notification.wait.exists(timeout=self.time_to_appear):
                raise Exception("Notification not appeared")
            #  click on the notification if required and validate that the notifications menu is gone
            if self.click_on_notification:
                self.notification.click()
                if not self.uidevice(resourceId="com.android.systemui:id/notification_stack_scroller").wait.gone(
                        timeout=self.timeout):
                    raise Exception("Notification menu not gone after click")
        except Exception, e:
            self.set_errorm("Notification " + str(self.text_contains), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if notification was found (and was clicked if requested), False if not
        """
        return self.step_data


class BtCheckNotificationGone(BtStep):

    """ Description:
            Waits for a Bluetooth notification to be gone (searching for a
            textContains selector). Call this with notification menu
            already opened, with the required notification already displayed
        Usage:
            bluetooth_steps.BtCheckNotificationGone(serial=serial,
                        text_contains="text_contained_into_notification_title",
                        time_to_wait=60000)()
    """

    def __init__(self, text_contains, time_to_wait=60000, **kwargs):
        """
        :param text_contains: text contained in the desired notification
        :param time_to_wait: max time to wait till notification is gone
        :param kwargs: serial, timeout, no_log and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.text_contains = text_contains
        self.time_to_wait = time_to_wait
        self.step_data = True
        self.notification = self.uidevice(resourceId="android:id/notification_main_column").child(
            textContains=self.text_contains)
        self.set_passm("Notification '" + str(self.text_contains) + "' gone")

    def do(self):
        try:
            #  wait for the notification to be gone
            if not self.notification.wait.gone(timeout=self.time_to_wait):
                raise Exception("Notification not gone after " + str(self.time_to_wait))
        except Exception, e:
            self.set_errorm("Notification " + str(self.text_contains), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if notification was gone, False if not
        """
        return self.step_data


class PressHome(BtStep):

    """ Description:
            Press the home button as a setup for tests.
        Usage:
            bluetooth_steps.PressHome(serial=serial)()
    """

    def __init__(self, **kwargs):
        """
        :param kwargs: serial, timeout and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.step_data = True
        self.set_passm("Home pressed")

    def do(self):
        try:
            self.uidevice.press.home()
            time.sleep(1)
        except Exception, e:
            self.step_data = False
            self.set_errorm("Press home exception", e.message)

    def check_condition(self):
        """
        :return: True if home pressed, False if not.
        """
        return self.step_data


class StopPackage(BtStep):

    """ Description:
            Executes command 'adb shell am force-stop [package_name]'. By default,
            it stops the Settings app, but you can also clear other apps by passing
            their package name to package_name parameter. This does not check
            anything, to be used for setup/teardown of tests
        Usage:
            bluetooth_steps.StopPackage(serial=serial,
                                        package_name="com.android.settings")()
    """

    def __init__(self, package_name="com.android.settings", **kwargs):
        """
        :param package_name: package name of the app to be stopped
        :param kwargs: serial and standard kwargs for base_step
        """
        BtStep.__init__(self, **kwargs)
        self.package_name = package_name

    def do(self):
        try:
            self.adb_connection.cmd("shell am force-stop " + str(self.package_name)).wait()
        except Exception, e:
            info_message = "Exception encountered when stop " + str(self.package_name) + ": " + e.message
            if self.serial:
                info_message = "[ " + str(self.serial) + " ] " + info_message
            self.logger.info(info_message)

    def check(self):
        #  prevent test step to display info, not relevant for BT tests
        pass


class LogInfo(base_step):

    """ Description:
            Logs an info message
        Usage:
            bluetooth_steps.LogInfo(message=<your_message>)()
    """

    def __init__(self, info_message):
        """
        :param info_message: info message to be logged
        """
        base_step.__init__(self)
        self._info_message = info_message

    def do(self):
        self.logger.info(self._info_message)

    def check(self):
        #  prevent test step to display info, not relevant for BT tests
        pass


class ConnectPairedDevices(BtStep):

    """ Description:
            Do not use in BT tests!
            Connects device with the already paired <dev_to_connect_name>
        Usage:
            bluetooth_steps.ConnectPairedDevices(dev_to_connect_name=<device name>)()
        Tags:
            ui, android, bluetooth
    """

    def __init__(self, dev_to_connect_name, **kwargs):
        BtStep.__init__(self, **kwargs)
        self.dev_to_connect_name = dev_to_connect_name
        self.connected = True
        self.set_passm("Connected to device " + str(dev_to_connect_name))

    def do(self):
        try:
            ui_steps.click_button_if_exists(serial=self.serial,
                                            view_to_find={"text":
                                                          self.dev_to_connect_name})()
        except Exception, e:
            self.connected = False
            self.set_errorm("Connect to device " +
                            str(self.dev_to_connect_name), e.message)

    def check_condition(self):
        if ui_utils.is_text_visible(text_to_find=self.dev_to_connect_name,
                                    serial=self.serial):
            self.connected = True
        else:
            self.connected = False
        return self.connected
