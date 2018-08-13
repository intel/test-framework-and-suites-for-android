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
# import serial.tools.list_ports


# ############# Get parameters ############
args = parse_args()

ui_steps.press_home(serial=args["serial"])()
ui_steps.press_car(serial=args["serial"])()
ui_steps.open_settings(serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "System"},
                             view_to_check={"textContains": "Languages"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "About phone"},
                             view_to_check={"text": "Status"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Status"},
                             view_to_check={"text": "Serial number"},
                             serial=args["serial"])()

# print the seria; number of the dveice
print ui_steps.wait_for_view_common(view_to_find={"text": "Serial number"},
                                    second_view_to_find={"className": "android.widget.TextView"},
                                    position="down", retrieve_info=True,
                                    serial=args["serial"])()["text"]
