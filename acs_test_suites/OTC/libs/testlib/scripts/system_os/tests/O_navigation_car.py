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
# Used defined libraries
from testlib.base.base_utils import parse_args
from testlib.scripts.android.ui import ui_steps

# ############# Get parameters ############
args = parse_args()
script_args = args["script_args"]
###############################

option = script_args["option"]

if option == "home":
    ui_steps.press_home(serial=args["serial"])()
if option == "car":
    ui_steps.press_home(serial=args["serial"])()
    ui_steps.press_car(serial=args["serial"])()
if option == "settings":
    ui_steps.open_settings(serial=args["serial"])()
if option == "map":
    ui_steps.press_map(serial=args["serial"])()
if option == "SystemUpdater":
    ui_steps.press_home(serial=args["serial"])()
    ui_steps.press_car(serial=args["serial"])()
    ui_steps.click_button_common(view_to_find={"text": "SystemUpdater"},
                                 view_to_check={"text": "SystemUpdater"},
                                 serial=args["serial"])()
if option == "Contacts":
    ui_steps.press_home(serial=args["serial"])()
    ui_steps.press_car(serial=args["serial"])()
    ui_steps.click_button_common(view_to_find={"text": "Contacts"},
                                 view_to_check={"text": "Contacts"},
                                 serial=args["serial"])()
