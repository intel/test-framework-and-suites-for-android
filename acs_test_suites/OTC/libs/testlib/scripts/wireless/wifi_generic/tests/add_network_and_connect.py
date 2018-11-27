#!/usr/bin/env python

'''
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
'''

import time
from testlib.scripts.android.ui import ui_steps
from testlib.scripts.wireless.wifi import wifi_steps
from testlib.utils.defaults import wifi_defaults
from testlib.base.base_utils import parse_args

'''initialization '''
args = parse_args()
script_params = args["script_args"]

''' test start '''

# turn display on, if turned off
ui_steps.wake_up_device(serial=args["serial"])()

# ensure the device is unlocked
ui_steps.unlock_device(serial=args["serial"], pin=wifi_defaults.wifi['pin'])()


# go to home screen
ui_steps.press_home(serial=args["serial"])()

# make sure there are no saved networks
wifi_steps.clear_saved_networks(serial=args["serial"])()

if script_params["execute_add_network_and_test_ping"] == "True":

    # add the Wi-Fi network
    wifi_steps.add_network(ssid=script_params["ap_name"],
                           security=script_params["dut_security"],
                           password=script_params["passphrase"],
                           serial=args["serial"])()

    # wait until the device connects to a wifi network
    wifi_steps.wait_until_connected(serial=args["serial"])()

    # check we are connected to the correct network.
    wifi_steps.check_connection_info(serial=args["serial"],
                                     SSID=script_params["ap_name"],
                                     state='CONNECTED/CONNECTED')()

    # check connection
    wifi_steps.ping_gateway(trycount=5, serial=args["serial"])()

    if script_params["iterate_connect_disconnect"] == "True":
        for x in xrange(int(script_params["iterations"])):
            # Turn ON the wifi and check if it is successfully turned ON
            wifi_steps.set_wifi(serial=args["serial"],
                                state="OFF", use_adb=False)()

            time.sleep(3)

            # Check for the connection status
            wifi_steps.check_connection_info(serial=args["serial"],
                                             state='DISCONNECTED/DISCONNECTED')()

            # Turn OFF the wifi and check if it is successfully turned turned
            # OFF
            wifi_steps.set_wifi(serial=args["serial"],
                                state="ON", use_adb=False)()

            time.sleep(3)

            wifi_steps.wait_until_connected(serial=args["serial"])()

            # Check for the connection status
            wifi_steps.check_connection_info(serial=args["serial"],
                                             SSID=script_params["ap_name"],
                                             state='CONNECTED/CONNECTED')()

            # check connection
            wifi_steps.ping_gateway(trycount=5, serial=args["serial"])()

''' test end '''
