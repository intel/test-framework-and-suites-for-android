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

from uiautomator import Device
from testlib.scripts.wireless.bluetooth import bluetooth_steps


def bt_pair_devices(serial, dev, dut_name, dev_name, action_dut="Pair", action_dev="Pair",
                    perform_action_first_on_initiator=True,
                    pair_request_initiator="dut", scan_timeout=60000, timeout=10000, scan_max_attempts=1,
                    time_to_wait_timeout_action=60000, version_dut="", version_dev="", **kwargs):
    """Description:
            Given two devices by the serial and the name, they will pair,
            cancel or timeout depending on the action requested. The pair
            request can be initiated by default by DUT either by the other
            device if pair_request_initiator is different by DUT. Make sure
            that you call this with BT settings opened on both devices(with
            BT opened and not any process in progress). Note that, if the
            first action performed is Timeout(either on initiator, or receiver),
            the other one action does not matter, because we must only validate
            that the pair request window is gone also on the another one device
            after timeout has expired
        Usage:
            bt_utils.bt_pair_devices(serial=dut_serial, dev=dev_serial,
                        dut_name="DUT_Name", dev_name="DEV_Name", action_dut="Pair",
                        action_dev="Pair", perform_action_first_on_initiator=True,
                        pair_request_initiator="DUT", scan_timeout=60000,
                        timeout=10000, scan_max_attempts=1, time_to_wait_timeout_action=60000,
                        version_dut="", version_dev="",critical=True, no_log=False)()
    :param serial: serial of DUT
    :param dev: serial of the DEV
    :param dut_name: name of DUT
    :param dev_name: name of DEV
    :param action_dut: "Pair"/"Cancel"/"Timeout" action to be performed on DUT
    :param action_dev: "Pair"/"Cancel"/"Timeout" action to be performed on DEV
    :param perform_action_first_on_initiator: True, to perform first on initiator the action, False otherwise
    :param pair_request_initiator: "dut"/"dev" - what device should initiate the pairing request
    :param scan_timeout: maximum timeout for scanning progress
    :param timeout: default timeout for each wait for exists
    :param scan_max_attempts: maximum no. of scan tries till the device is found
    :param time_to_wait_timeout_action: maximum time to wait for "Timeout" action
    :param version_dut: os version of the DUT
    :param version_dev: os version of the DEV
    :param kwargs: no_log and standard kwargs for base_step
    """

    #  ### initiate all required vars, according to params ###

    #  expected time for the pair request window to disappear on a device after disappears on other one device
    #  theoretically, when pair request is gone on a device, it is expected to be gone also on other one device; we will
    #  consider 1s timeout for slow ui platforms
    __request_disappear_timeout = 1000

    pair_request_initiator = pair_request_initiator.lower()
    if pair_request_initiator == "dut":
        receiver_name = dev_name
        initiator_name = dut_name
        initiator_serial = serial
        receiver_serial = dev
        action_initiator = action_dut
        action_receiver = action_dev
        version_initiator = version_dut
        version_receiver = version_dev
    elif pair_request_initiator == "dev":
        receiver_name = dut_name
        initiator_name = dev_name
        initiator_serial = dev
        receiver_serial = serial
        action_initiator = action_dev
        action_receiver = action_dut
        version_initiator = version_dev
        version_receiver = version_dut
    else:
        raise Exception("Config error: not any expected value for pair_request_initiator")
    if action_dut not in ["Cancel", "Pair", "Timeout"]:
        raise Exception("Config error: not any expected value for action_dut")
    if action_dev not in ["Cancel", "Pair", "Timeout"]:
        raise Exception("Config error: not any expected value for action_dev")

    #  ### call here all the required steps ###

    bluetooth_steps.BtSearchDevices(serial=receiver_serial, dev_to_find=initiator_name, scan_timeout=scan_timeout,
                                    timeout=timeout, max_attempts=scan_max_attempts, version=version_receiver,
                                    **kwargs)()

    bluetooth_steps.InitiatePairRequest(serial=initiator_serial, dev_to_pair_name=receiver_name,
                                        scan_timeout=scan_timeout, timeout=timeout,
                                        scan_max_attempts=scan_max_attempts, version=version_initiator, **kwargs)()
    bluetooth_steps.ReceivePairRequest(serial=receiver_serial, dev_receiving_from_name=initiator_name,
                                       version=version_receiver, timeout=timeout, **kwargs)()

    #  now we have both devices into pair request window, so we can check the passkey
    passkey_string_initiator = bluetooth_steps.GetPasskey(serial=initiator_serial, version=version_initiator,
                                                          **kwargs)()
    passkey_string_receiver = bluetooth_steps.GetPasskey(serial=receiver_serial, version=version_receiver, **kwargs)()
    bluetooth_steps.PasskeyCheck(serial=serial, passkey_initiator=passkey_string_initiator,
                                 passkey_receiver=passkey_string_receiver, **kwargs)()

    #  if actions are performed first on pair request initiator, we have the following scenarios that must
    #  be treated
    if perform_action_first_on_initiator:
        if action_initiator == "Pair":
            bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                     version=version_initiator, **kwargs)()
            if action_receiver == "Pair":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
            elif action_receiver == "Cancel":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
            elif action_receiver == "Timeout":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
        elif action_initiator == "Cancel":
            bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                     version=version_initiator, **kwargs)()
            bluetooth_steps.WaitPairRequest(serial=receiver_serial, appear=False,
                                            time_to_wait=__request_disappear_timeout, **kwargs)()
            if version_initiator.startswith("5.") or version_initiator.startswith("7"):
                #  LLP,N version
                #  no window to treat
                pass
            else:
                #  M versions
                bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
        elif action_initiator == "Timeout":
            #  does not matter what action is on receiver, only check if after timeout on initiator, pair
            #  request is gone on receiver
            bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                     timeout=time_to_wait_timeout_action, version=version_initiator,
                                                     **kwargs)()
            bluetooth_steps.WaitPairRequest(serial=receiver_serial, appear=False,
                                            time_to_wait=__request_disappear_timeout, version=version_receiver,
                                            **kwargs)()
    #  if actions are performed first on pair request receiver, we have the following scenarios that must
    #  be treated
    else:
        if action_initiator == "Pair":
            if action_receiver == "Pair":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         version=version_initiator, **kwargs)()
            elif action_receiver == "Cancel":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         version=version_initiator, **kwargs)()
                bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
            elif action_receiver == "Timeout":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.WaitPairRequest(serial=initiator_serial, appear=False,
                                                time_to_wait=__request_disappear_timeout, version=version_initiator,
                                                **kwargs)()
        elif action_initiator == "Cancel":
            if action_receiver == "Pair":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         version=version_initiator, **kwargs)()
                bluetooth_steps.CouldNotPairDialogCheck(serial=receiver_serial, **kwargs)()
                if version_initiator.startswith("5.") or version_initiator.startswith("7"):
                    #  LLP,N version
                    #  no window to treat
                    pass
                else:
                    #  M versions
                    bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
            elif action_receiver == "Cancel":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         version=version_initiator, **kwargs)()
                if version_initiator.startswith("5.") or version_initiator.startswith("7"):
                    #  LLP,N version
                    #  no window to treat
                    pass
                else:
                    #  M versions
                    bluetooth_steps.CouldNotPairDialogCheck(serial=initiator_serial, **kwargs)()
            elif action_receiver == "Timeout":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.WaitPairRequest(serial=initiator_serial, appear=False,
                                                time_to_wait=__request_disappear_timeout, version=version_initiator,
                                                **kwargs)()
        elif action_initiator == "Timeout":
            if action_receiver == "Pair":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_initiator, **kwargs)()
                bluetooth_steps.CouldNotPairDialogCheck(serial=receiver_serial, **kwargs)()
            elif action_receiver == "Cancel":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.PerformActionPairRequest(serial=initiator_serial, action=action_initiator,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_initiator, **kwargs)()
            elif action_receiver == "Timeout":
                bluetooth_steps.PerformActionPairRequest(serial=receiver_serial, action=action_receiver,
                                                         timeout=time_to_wait_timeout_action,
                                                         version=version_receiver, **kwargs)()
                bluetooth_steps.WaitPairRequest(serial=initiator_serial, appear=False,
                                                time_to_wait=__request_disappear_timeout, version=version_initiator,
                                                **kwargs)()

    #  now we must check if devices are paired, or not, according to parameters
    if action_dut == "Pair" and action_dev == "Pair":
        bluetooth_steps.CheckIfPaired(serial=serial, dev_paired_with=dev_name, paired=True, timeout=timeout,
                                      version=version_dut, **kwargs)()
        bluetooth_steps.CheckIfPaired(serial=dev, dev_paired_with=dut_name, paired=True, timeout=timeout,
                                      version=version_dev, **kwargs)()
    else:
        bluetooth_steps.CheckIfPaired(serial=serial, dev_paired_with=dev_name, paired=False, timeout=timeout,
                                      version=version_dut, **kwargs)()
        bluetooth_steps.CheckIfPaired(serial=dev, dev_paired_with=dut_name, paired=False, timeout=timeout,
                                      version=version_dev, **kwargs)()


def get_sent_received_count(serial=None, share_type="Sent", count_successful=True, count_unsuccessful=False,
                            notif_menu_already_opened=False, **kwargs):
    """ Description:
            Swipes down to open the notification bar and gets the current number of successful or
            unsuccessful OPP file transfers. If no Sent/Received notification is found, it
            returns 0 as files count, otherwise it returns the found number.
            If count_successful=True, then it returns the value of the successful transfers
            If count_unsuccessful=True, then it returns the value of the successful transfers
            If the notification menu is already opened, set notif_menu_already_opened to True
        Usage:
            count_value = bt_utils.get_sent_received_count(serial=device_serial,
                                    share_type=Received/Sent, count_successful=bool,
                                    count_unsuccessful=bool, notif_menu_already_opened=False)()
    :param serial: serial of the device
    :param share_type: "Sent"/"Received" share type to count in notification menu
    :param count_successful: True to count successful transfers
    :param count_unsuccessful: True to count unsuccessful transfers
    :param notif_menu_already_opened: True, it assumes that the notification menu is already opened
    :param kwargs: timeout, version, no_log and standard kwargs for base_step
    """

    #  ### initiate all required vars, according to params ###

    uidevice = Device(serial=serial)

    if share_type is "Sent":
        notification_title = "Bluetooth share: Sent files"
    elif share_type is "Received":
        notification_title = "Bluetooth share: Received files"
    else:
        raise Exception("Config error, not any of expected value for share_type")

    #  ### call here all the required steps ###

    if not notif_menu_already_opened:
        bluetooth_steps.OpenNotificationsMenu(serial=serial, **kwargs)()

    notification = uidevice(resourceId="android:id/notification_main_column").child(textContains=notification_title)
    if notification.wait.exists(timeout=1000):
        file_count = bluetooth_steps.BtOppGetNotificationNumberUpdate(serial=serial,
                                                                      share_type=share_type,
                                                                      count_successful=count_successful,
                                                                      count_unsuccessful=count_unsuccessful,
                                                                      notif_menu_already_opened=True, **kwargs)()
    else:
        file_count = 0

    if not notif_menu_already_opened:
        time.sleep(1)
        bluetooth_steps.CloseNotificationsMenu(serial=serial, **kwargs)()

    #  ### return computed value ###
    return file_count
