#!/usr/bin/env python
# coding=utf-8
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

# Used defined libraries
from testlib.base.base_utils import parse_args
from testlib.scripts.android.ui import ui_steps
from testlib.utils import logger
from testlib.utils.statics.android import statics
from testlib.scripts.wireless.bluetooth import bluetooth_steps

#############################################
log = None
if "LOG_PATH" in os.environ:
    testlib_log_path = os.environ["LOG_PATH"]
else:
    import testlib
    testlib_log_path = os.path.dirname(testlib.__file__) + "/logs/"

log = logger.testlib_log(log_path=testlib_log_path, log_name="testlib_default")

serial = None
script_args = None

# ############# Get parameters ############
args = parse_args()

dessert = statics.get_dessert(serial=args["serial"])

if dessert == "P":
    ui_steps.PressNotification(serial=args["serial"])()
    ui_steps.click_button_common(view_to_find={"resourceId": "com.android.systemui:id/settings_button"},
                                 serial=args["serial"])()
    ui_steps.click_button_common(view_to_find={"text": "More"}, serial=args["serial"])()
    Settings_not_found = []
    Settings_to_check = {"Display", "Sound", "Wi‑Fi", "Bluetooth", "App info", "Date & time", "Users", "Accounts",
                         "Security", "Google", "System"}
    for find in Settings_to_check:
        try:
            ui_steps.wait_for_view_common(view_to_find={"text": find}, serial=args["serial"])()
        except:
            Settings_not_found.append(find)
            log.info(find + " option is not available in IVI settings")
    # Tear Down
            bluetooth_steps.ClearRecentApps(serial=args["serial"])()


else:
    ui_steps.press_home(serial=args["serial"])()
    ui_steps.click_button_common(view_to_find={"resourceId": "com.android.systemui:id/settings_button"},
                                 serial=args["serial"])()
    Settings_not_found = []
    Settings_to_check = {"Display", "Sound", "Wi‑Fi", "Bluetooth", "App info", "Date & time", "Users", "System"}
    for find in Settings_to_check:
        try:
            ui_steps.wait_for_view_common(view_to_find={"text": find}, serial=args["serial"])()
        except:
            Settings_not_found.append(find)
            log.info(find + " option is not available in IVI settings")

    # TearDown
    ui_steps.press_home(serial=args["serial"])()
