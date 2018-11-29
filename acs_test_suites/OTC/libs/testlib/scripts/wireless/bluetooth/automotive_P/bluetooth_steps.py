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

import time
#  import os.path
import traceback

# from testlib.base.base_step import step as base_step
# from testlib.scripts.wireless.bluetooth.bt_step import Step as BtStep
from testlib.scripts.android.ui import ui_steps
# from testlib.scripts.android.ui import ui_utils
from testlib.scripts.wireless.bluetooth.automotive_O import bluetooth_steps as parent_bluetooth_steps
# from testlib.scripts.wireless.bluetooth import bluetooth_utils


class GetAndroidVersion(parent_bluetooth_steps.GetAndroidVersion):
    """ Description:
            Gets Android version via adb command (float type)
        Usage:
            bluetooth_steps.GetAndroidVersion(serial=serial)()
    """

    pass


class ClickBluetoothSwitch(parent_bluetooth_steps.ClickBluetoothSwitch):
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

        parent_bluetooth_steps.ClickBluetoothSwitch.__init__(self, state="ON", check_if_already=False, **kwargs)
        self.state = state
        # In some platform, state text is 'On' & 'Off', so covert to 'checked'
        self.checked = True if state == "ON" else False
        self.check_if_already = check_if_already
        self.switch = self.uidevice(className="android.widget.Switch", enabled=True)
        self.step_data = True
        self.set_passm("BT set to " + self.state)

    def do(self):
            try:
                # ui_steps.click_button_if_exists(serial=self.serial,wait_time = 5000,
                #                                 view_to_find = {"text": "Connection preferences"})()
                ui_steps.click_button_common(
                    serial=self.serial, view_to_find={"text": "Connection preferences"})()
                ui_steps.click_button_common(
                    serial=self.serial, view_to_find={"text": "Bluetooth"})()
                # ui_steps.click_button_with_scroll(serial=self.serial,view_to_find = {"text": "Bluetooth"})()
                # check if switch is present
                if not self.switch.wait.exists(timeout=self.timeout):
                    raise Exception("No BT switch found")
                if not self.switch.info["checked"] == self.checked:
                    self.switch.click()
                else:
                    # check if already has required state
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
            # wait for switch transition
            if not self.switch.wait.exists(timeout=self.timeout):
                self.set_errorm("Set BT to " + self.state, "BT state not set to " + self.state + " correctly")
                self.step_data = False
            else:
                # check if it has required state
                if not self.uidevice(className="android.widget.Switch",
                                     enabled=True,
                                     checked=self.checked).wait.exists(timeout=self.timeout):
                    self.set_errorm("Set BT to " + self.state, "BT state not set to " + self.state)
                    self.step_data = False
            self.uidevice.press.back()
            self.uidevice.press.back()

        return self.step_data


class OpenBluetoothSettings(parent_bluetooth_steps.OpenBluetoothSettings):
    """ Description:
            Opens the Bluetooth activity from settings, either from all
            apps menu, or by sending an intent. Call this from the Home
            screen if use_intent=False
        Usage:
            bluetooth_steps.OpenBluetoothSettings(serial=serial, use_intent=False, version=version)()
    """

    pass


class CheckBtVisibility(parent_bluetooth_steps.CheckBtVisibility):
    """ Description:
            Checks if the device is visible. Call this from the BT settings list,
            with BT ON
        Usage:
            bluetooth_steps.CheckBtVisibility(serial=serial, version=version)()
    """

    pass


class WaitBtScanning(parent_bluetooth_steps.WaitBtScanning):
    """ Description:
            Makes sure that the BT scanning progress is finished, by waiting
            for progress bar to be gone. Call this from BT settings list,
            with BT on
        Usage:
            bluetooth_steps.WaitBtScanning(serial=serial,
                                timeout_appear=5000, time_to_wait=60000, version=version)()
    """

    pass


class GetBtMac(parent_bluetooth_steps.GetBtMac):
    """ Description:
            Get BT Address Mac via adb command
        Usage:
            bluetooth_steps.GetBtMac(serial=serial)()
    """

    pass


class BtChangeDeviceName(parent_bluetooth_steps.BtChangeDeviceName):
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
        parent_bluetooth_steps.BtChangeDeviceName.__init__(self, name="", **kwargs)
        self.name = name
        self.step_data = True
        self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")

    def do(self):
        try:
            ui_steps.click_button_common(serial=self.serial, wait_time=5000,
                                         view_to_find={"text": "Connection preferences"})()
            ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "Bluetooth"})()
            ui_steps.click_button_common(serial=self.serial,
                                         view_to_find={"textContains": "Device name"})()
            if not self.uidevice(resourceId="android:id/alertTitle", text="Rename this device").wait.exists(
                    timeout=self.timeout):
                raise Exception("Rename DUT alert title not opened")
            # force a small delay due to window transition and close keyboard
            time.sleep(1)
            if "mInputShown=true" in self.adb_connection.cmd("shell dumpsys input_method").communicate()[
                0].decode("utf-8"):
                self.uidevice.press.back()
                time.sleep(1)
            # replace name
            rename_edit_text = self.uidevice(className="android.widget.EditText")
            ui_steps.edit_text(view_to_find={"className": "android.widget.EditText"}, value=self.name,
                               serial=self.serial)()
            rename_button = self.uidevice(text="RENAME")
            if not rename_button.wait.exists(timeout=self.timeout):
                raise Exception("Rename button from pop-up not found")
            # if given name is empty, check the status of Rename button and return to the BT list
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
            # if given name is not empty, rename it
            else:
                rename_button.click()
                if not self.bt_list.wait.exists(timeout=self.timeout):
                    raise Exception("BT devices list not reached after renaming BT")
                self.uidevice.press.back()
                self.uidevice.press.back()
                if not self.bt_list.scroll.to(textContains="visible"):
                    raise Exception("BT name was not found down of the list after rename")
                self.set_passm("Device renamed: " + self.name)
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


class BtSearchDevices(parent_bluetooth_steps.BtSearchDevices):
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

    pass


class GetPasskey(parent_bluetooth_steps.GetPasskey):
    """ Description:
            Get the pairing code from the pair request window. Call this in
            the Pairing request window
        Usage:
            bluetooth_steps.GetPasskey(serial=serial)()
    """

    pass


class PasskeyCheck(parent_bluetooth_steps.PasskeyCheck):
    """ Description:
            This method checks if the pairing request passkeys are both
            on the initiator and on the receiver
        Usage:
            bluetooth_steps.PasskeyCheck(serial=serial, passkey_initiator=passkey1,
                                            passkey_receiver=passkey2)()
     """

    pass


class CheckIfPaired(parent_bluetooth_steps.CheckIfPaired):
    """ Description:
            Checks if the device is paired, or not(depending on the paired parameter)
            with another device. Call this with the BT list opened
        Usage:
            bluetooth_steps.CheckIfPaired(serial=serial,
                            dev_paired_with = DEVNAME, paired=True, version=version)()
    """

    pass


class WaitPairRequest(parent_bluetooth_steps.WaitPairRequest):
    """ Description:
            Waits for the pair request alert to appear or to be gone,
            as defined by parameter appear=True/False.
        Usage:
            bluetooth_steps.WaitPairRequest(serial=serial,
                                    appear=True, time_to_wait=10000, version=version)()
    """

    pass


class InitiatePairRequest(parent_bluetooth_steps.InitiatePairRequest):
    """ Description:
            Initiate a pair request. It searches for the device name, clicks on it and assures
            that the initiator device is in the pairing request window (i.e. if pair request window
            is not displayed on the screen, it checks if the "Cannot communicate" message is displayed,
            and if not, it searches the request in the notifications menu)
        Usage:
            bluetooth_steps.InitiatePairRequest(serial=serial, dev_to_pair_name="Name",
                        scan_timeout=60000, scan_max_attempts=1, version=version)()
    """

    pass


class PairDevice(parent_bluetooth_steps.PairDevice):
    """ Description:
            Initiate a pair request. It searches for the device name, clicks on it and assures
            that the initiator device is in the pairing request window (i.e. if pair request window
            is not displayed on the screen, it checks if the "Cannot communicate" message is displayed,
            and checks device name paired or not to DUT, If paired returns true)
        Usage:
            bluetooth_steps.PairDevice(serial=serial, dev_to_pair_name="Name",
                        scan_timeout=60000, scan_max_attempts=1, version=version)()
    """

    pass


class ReceivePairRequest(parent_bluetooth_steps.ReceivePairRequest):
    """ Description:
            Receives a pair request. It assures that device is
            in the pairing request window (i.e. if pair request window
            is not received on the screen, it searches it in the
            notifications menu)
        Usage:
            bluetooth_steps.ReceivePairRequest(serial=serial,
                        dev_receiving_from_name="Name", version=version)()
    """

    pass


class SearchPairRequestNotification(parent_bluetooth_steps.SearchPairRequestNotification):
    """ Description:
            Opens a Pairing request from the notification menu. Note that
            this does not check if, indeed the pairing request dialog appears,
            it only clicks the notification. Call this only if the request
            dialog is not displayed and it should be
        Usage:
            bluetooth_steps.SearchPairRequestNotification(serial=serial)()
    """

    pass


class OpenNotificationsMenu(parent_bluetooth_steps.OpenNotificationsMenu):
    """ Description:
            Opens the notifications menu in order to operate with Bluetooth notifications
        Usage:
            bluetooth_steps.OpenNotificationsMenu(serial=serial)()
    """

    pass


class CloseNotificationsMenu(parent_bluetooth_steps.CloseNotificationsMenu):
    """ Description:
            Closes the notifications menu
        Usage:
            bluetooth_steps.CloseNotificationsMenu(serial=serial)()
    """

    pass


class PerformActionPairRequest(parent_bluetooth_steps.PerformActionPairRequest):
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

    pass


class CouldNotPairDialogCheck(parent_bluetooth_steps.CouldNotPairDialogCheck):
    """ Description:
            Checks if the "Couldn't pair" dialog is displayed
            (by waiting for it) and clicks on it's OK button.
        Usage:
            bluetooth_steps.CouldNotPairDialogCheck(serial=serial)()
    """

    pass


class BtRemoveAllPairedDevices(parent_bluetooth_steps.BtRemoveAllPairedDevices):
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
        parent_bluetooth_steps.BtRemoveAllPairedDevices.__init__(self, max_attempts=20, **kwargs)
        self.max_attempts = max_attempts
        self.paired_title = self.uidevice(text="Available media devices")
        self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.step_data = True
        self.set_passm("Nothing to unpair")
        self.set_errorm(str(max_attempts) + "attempts", "Not removed all paired devices")

    def do(self):
        try:
            counter = 1
            # for each existing paired button, click on it and FORGET
            while self.paired_title.exists and self.uidevice(description="Settings"):
                if counter > self.max_attempts:
                    break
                ui_steps.click_button_common(serial=self.serial,
                                             view_to_find={"description": "Settings"})()
                time.sleep(1)
                if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET"})():
                    raise Exception("Forget button not found when unpair " + " (device no. " + str(counter) + ")")
                if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET DEVICE"})():
                    raise Exception(
                        "Forget device button not found when unpair " + " (device no. " + str(counter) + ")")

                counter += 1
                self.set_passm(str(counter - 1) + " device(s) unpaired")
            if ui_steps.click_button_common(serial=self.serial,
                                            view_to_find={"text": "Previously connected devices"})():
                counter = 1
                while self.uidevice(description="Settings"):
                    if counter > self.max_attempts:
                        break
                    ui_steps.click_button_common(serial=self.serial,
                                                 view_to_find={"description": "Settings"})()
                    time.sleep(1)
                    if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET"})():
                        raise Exception("Forget button not found when unpair " + " (device no. " + str(counter) + ")")
                    if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET DEVICE"})():
                        raise Exception(
                            "Forget device button not found when unpair " + " (device no. " + str(counter) + ")")

                    counter += 1
                    self.set_passm(str(counter - 1) + " device(s) unpaired")
                    self.uidevice.press.back()

        except Exception, e:
            self.set_errorm("Unpair devices", e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if all paired devices were unpaired, False otherwise
        """
        self.step_data = self.uidevice(description="Settings").wait.gone(timeout=self.timeout)
        return self.step_data


class OpenPairedDeviceSettings(parent_bluetooth_steps.OpenPairedDeviceSettings):
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
        parent_bluetooth_steps.OpenPairedDeviceSettings.__init__(self, device_name, **kwargs)
        self.device_name = device_name
        self.step_data = True
        self.bt_list = self.uidevice(resourceId="com.android.settings:id/list")
        self.set_passm("Device settings opened for device " + str(self.device_name))
        self.set_errorm("Paired device settings for " + str(self.device_name), "Device settings not opened")

    def do(self):
        try:
            paired_button = self.uidevice(description="Settings")
            paired_button.click.wait()
            time.sleep(1)
            if not ui_steps.wait_for_view_common(serial=self.serial, view_to_find={"text": "FORGET"})():
                raise Exception("text button not found")
        except Exception, e:
            self.set_errorm("Paired device settings for " + str(self.device_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device settings was opened, False otherwise
        """
        if self.step_data:
            return self.step_data


class UnpairDevice(parent_bluetooth_steps.UnpairDevice):
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
        parent_bluetooth_steps.UnpairDevice.__init__(self, device_name, **kwargs)
        self.device_name = device_name
        self.step_data = True
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
            # click on forget
            if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET"})():
                    raise Exception("Forget button not found when unpair ")
            if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "FORGET DEVICE"})():
                    raise Exception("Forget device button not found when unpair ")
        except Exception, e:
            self.set_errorm("Unpair device " + str(self.device_name), e.message)
            self.step_data = False

    def check_condition(self):
        """
        :return: True if Device was unpaired, False if not
        """
        if self.step_data:
            # check if is not paired with required device
            self.step_data = CheckIfPaired(serial=self.serial, dev_paired_with=self.device_name, paired=False,
                                           timeout=self.timeout, version=self.version, critical=False)()
        return self.step_data


class DisconnectDevice(parent_bluetooth_steps.DisconnectDevice):
    """ Description:
            disconnect a certain device from the list and still it will be paired
        Usage:
            bluetooth_steps.DisconnectDevice(serial = serial,
                                    device_name="DEV_name", version=version)()
    """
    pass


class BtCheckNotificationAppear(parent_bluetooth_steps.BtCheckNotificationAppear):
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
    pass


class BtCheckNotificationGone(parent_bluetooth_steps.BtCheckNotificationGone):
    """ Description:
            Waits for a Bluetooth notification to be gone (searching for a
            textContains selector). Call this with notification menu
            already opened, with the required notification already displayed
        Usage:
            bluetooth_steps.BtCheckNotificationGone(serial=serial,
                        text_contains="text_contained_into_notification_title",
                        time_to_wait=60000)()
    """
    pass


class PressHome(parent_bluetooth_steps.PressHome):
    """ Description:
            Press the home button as a setup for tests.
        Usage:
            bluetooth_steps.PressHome(serial=serial)()
    """
    pass


class StopPackage(parent_bluetooth_steps.StopPackage):
    """ Description:
            Executes command 'adb shell am force-stop [package_name]'. By default,
            it stops the Settings app, but you can also clear other apps by passing
            their package name to package_name parameter. This does not check
            anything, to be used for setup/teardown of tests
        Usage:
            bluetooth_steps.StopPackage(serial=serial,
                                        package_name="com.android.settings")()
    """

    pass


class LogInfo(parent_bluetooth_steps.LogInfo):
    """ Description:
            Logs an info message
        Usage:
            bluetooth_steps.LogInfo(message=<your_message>)()
    """
    pass


class ConnectPairedDevices(parent_bluetooth_steps.ConnectPairedDevices):
    """ Description:
            Do not use in BT tests!
            Connects device with the already paired <dev_to_connect_name>
        Usage:
            bluetooth_steps.ConnectPairedDevices(dev_to_connect_name=<device name>)()
        Tags:
            ui, android, bluetooth
    """
    pass
