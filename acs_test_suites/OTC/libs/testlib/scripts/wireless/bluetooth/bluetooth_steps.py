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

# import time
#  import os.path
# import traceback

from testlib.base.base_step import step as base_step
# from testlib.scripts.wireless.bluetooth.bt_step import Step as BtStep
# from testlib.scripts.android.ui import ui_steps
# from testlib.scripts.android.ui import ui_utils
from testlib.base.abstract.abstract_step import devicedecorator
# from testlib.scripts.wireless.bluetooth import bluetooth_utils


@devicedecorator
class GetAndroidVersion():

    """ Description:
            Gets Android version via adb command (float type)
        Usage:
            bluetooth_steps.GetAndroidVersion(serial=serial)()
    """

    pass


@devicedecorator
class ClickBluetoothSwitch():

    """ Description:
            Only makes sure that the Bluetooth switch has the required state.
            Furthermore, if you call this function with check_if_already=True,
            if BT switch already has the required state, it returns failure.
            Call this from the Bluetooth Settings activity
        Usage:
            bluetooth_steps.ClickBluetoothSwitch(
                        state = "ON", check_if_already=False)()
    """
    pass


@devicedecorator
class OpenBluetoothSettings():

    """ Description:
            Opens the Bluetooth activity from settings, either from all
            apps menu, or by sending an intent. Call this from the Home
            screen if use_intent=False
        Usage:
            bluetooth_steps.OpenBluetoothSettings(serial=serial, use_intent=False, version=version)()
    """

    pass


@devicedecorator
class CheckBtVisibility():

    """ Description:
            Checks if the device is visible. Call this from the BT settings list,
            with BT ON
        Usage:
            bluetooth_steps.CheckBtVisibility(serial=serial, version=version)()
    """
    pass


@devicedecorator
class WaitBtScanning():

    """ Description:
            Makes sure that the BT scanning progress is finished, by waiting
            for progress bar to be gone. Call this from BT settings list,
            with BT on
        Usage:
            bluetooth_steps.WaitBtScanning(serial=serial,
                                timeout_appear=5000, time_to_wait=60000, version=version)()
    """
    pass


@devicedecorator
class GetBtMac():

    """ Description:
            Get BT Address Mac via adb command
        Usage:
            bluetooth_steps.GetBtMac(serial=serial)()
    """

    pass


@devicedecorator
class BtChangeDeviceName():

    """ Description:
            Replaces the name of the devices with the given name, if not
            already named with the given name. If there is not any character
            given in the name, it validates that Rename button from the
            pop-up is disabled. Call this from the BT settings list, with
            BT ON
        Usage:
            bluetooth_steps.BtChangeDeviceName(serial=serial, name = "", version=version)()
    """
    pass


@devicedecorator
class BtSearchDevices():

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


@devicedecorator
class GetPasskey():

    """ Description:
            Get the pairing code from the pair request window. Call this in
            the Pairing request window
        Usage:
            bluetooth_steps.GetPasskey(serial=serial)()
    """
    pass


@devicedecorator
class PasskeyCheck():

    """ Description:
            This method checks if the pairing request passkeys are both
            on the initiator and on the receiver
        Usage:
            bluetooth_steps.PasskeyCheck(serial=serial, passkey_initiator=passkey1,
                                            passkey_receiver=passkey2)()
     """
    pass


@devicedecorator
class CheckIfPaired():

    """ Description:
            Checks if the device is paired, or not(depending on the paired parameter)
            with another device. Call this with the BT list opened
        Usage:
            bluetooth_steps.CheckIfPaired(serial=serial,
                            dev_paired_with = DEVNAME, paired=True, version=version)()
    """
    pass


@devicedecorator
class WaitPairRequest():

    """ Description:
            Waits for the pair request alert to appear or to be gone,
            as defined by parameter appear=True/False.
        Usage:
            bluetooth_steps.WaitPairRequest(serial=serial,
                                    appear=True, time_to_wait=10000, version=version)()
    """
    pass


@devicedecorator
class InitiatePairRequest():

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


@devicedecorator
class PairDevice():

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


@devicedecorator
class ReceivePairRequest():

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


@devicedecorator
class SearchPairRequestNotification():

    """ Description:
            Opens a Pairing request from the notification menu. Note that
            this does not check if, indeed the pairing request dialog appears,
            it only clicks the notification. Call this only if the request
            dialog is not displayed and it should be
        Usage:
            bluetooth_steps.SearchPairRequestNotification(serial=serial)()
    """
    pass


@devicedecorator
class OpenNotificationsMenu():

    """ Description:
            Opens the notifications menu in order to operate with Bluetooth notifications
        Usage:
            bluetooth_steps.OpenNotificationsMenu(serial=serial)()
    """
    pass


@devicedecorator
class CloseNotificationsMenu():

    """ Description:
            Closes the notifications menu
        Usage:
            bluetooth_steps.CloseNotificationsMenu(serial=serial)()
    """

    pass


@devicedecorator
class PerformActionPairRequest():

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


@devicedecorator
class CouldNotPairDialogCheck():

    """ Description:
            Checks if the "Couldn't pair" dialog is displayed
            (by waiting for it) and clicks on it's OK button.
        Usage:
            bluetooth_steps.CouldNotPairDialogCheck(serial=serial)()
    """

    pass


@devicedecorator
class BtRemoveAllPairedDevices():

    """ Description:
            All pair devices will be removed from the list. Call this in BT
            devices list, with no scanning in progress
        Usage:
            bluetooth_steps.BtRemoveAllPairedDevices(serial = serial,
                                            max_attempts=20, version=version)()
    """

    pass


@devicedecorator
class OpenPairedDeviceSettings():

    """ Description:
            Open the device settings alert title for a certain paired device.
            Call this in BT settings list for a device a device already
            paired
        Usage:
            bluetooth_steps.OpenPairedDeviceSettings(serial = serial,
                                        device_name="DEV_name", version=version)()
    """

    pass


@devicedecorator
class UnpairDevice():

    """ Description:
            Unpair a certain device from the list.Call this in BT settings
            list for a device a device already paired
        Usage:
            bluetooth_steps.UnpairDevice(serial = serial,
                                    device_name="DEV_name", version=version)()
    """

    pass


@devicedecorator
class DisconnectDevice():

    """ Description:
            disconnect a certain device from the list and still it will be paired
        Usage:
            bluetooth_steps.DisconnectDevice(serial = serial,
                                    device_name="DEV_name", version=version)()
    """

    pass


@devicedecorator
class BtCheckNotificationAppear():

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


@devicedecorator
class BtCheckNotificationGone():

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


@devicedecorator
class PressHome():

    """ Description:
            Press the home button as a setup for tests.
        Usage:
            bluetooth_steps.PressHome(serial=serial)()
    """

    pass


@devicedecorator
class StopPackage():

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
        # prevent test step to display info, not relevant for BT tests
        pass


@devicedecorator
class ConnectPairedDevices():

    """ Description:
            Do not use in BT tests!
            Connects device with the already paired <dev_to_connect_name>
        Usage:
            bluetooth_steps.ConnectPairedDevices(dev_to_connect_name=<device name>)()
        Tags:
            ui, android, bluetooth
    """
    pass
