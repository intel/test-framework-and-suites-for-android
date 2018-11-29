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
# from testlib.external.uiautomator import Device
# from testlib.scripts.wireless.bluetooth import bluetooth_steps
# from testlib.scripts.android.ui import ui_steps
from testlib.base.abstract.abstract_step import devicedecorator


@devicedecorator
def bt_pair_devices():
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

    # ### initiate all required vars, according to params ###

    # expected time for the pair request window to disappear on a device after disappears on other one device
    # theoretically, when pair request is gone on a device, it is expected to be gone also on other one device; we will
    # consider 1s timeout for slow ui platforms
    pass


@devicedecorator
def get_sent_received_count():
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

    # ### initiate all required vars, according to params ###
    pass
