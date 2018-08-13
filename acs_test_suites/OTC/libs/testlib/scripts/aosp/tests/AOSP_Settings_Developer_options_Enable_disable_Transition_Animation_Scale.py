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

# Setup
ui_steps.press_home(serial=args["serial"])()

# Run
ui_steps.enable_developer_options(serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Developer options"},
                             view_to_check={"text": "OEM unlocking"},
                             serial=args["serial"])()

# option 1 animation off
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation off"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation off"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation off"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down",
                              retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 2 Animation scale .5x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale .5x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale .5x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale .5x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down", retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 3 Animation scale 1x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale 1x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale 1x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale 1x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down", retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 4 Animation scale 1.5x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale 1.5x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale 1.5x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale 1.5x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down", retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 5 Animation scale 2x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale 1.5x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale 2x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale 2x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down", retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 6 Animation scale 5x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale 1.5x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale 5x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale 5x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down", retrieve_info=True,
                              serial=args["serial"])()["text"]

# option 7 Animation scale 10x
ui_steps.click_button_common(view_to_find={"text": "Transition animation scale"},
                             view_to_check={"text": "Animation scale 1.5x"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Animation scale 10x"},
                             serial=args["serial"])()
ui_steps.wait_for_view_common(view_to_find={"text": "Animation scale 10x"},
                              second_view_to_find={"className": "android.widget.TextView"},
                              position="down",
                              retrieve_info=True,
                              serial=args["serial"])()["text"]
