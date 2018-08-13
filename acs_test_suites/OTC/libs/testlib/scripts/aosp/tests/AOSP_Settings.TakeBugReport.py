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
import time

# ############# Get parameters ############
args = parse_args()

# Setup
ui_steps.press_home(serial=args["serial"])()

# Run
ui_steps.enable_developer_options(serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Developer options"},
                             view_to_check={"text": "OEM unlocking"},
                             serial=args["serial"])()

# for full report
ui_steps.click_button_common(view_to_find={"text": "Take bug report"},
                             view_to_check={"text": "Interactive report"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Full report"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "REPORT"},
                             serial=args["serial"])()


# for interactive report
ui_steps.click_button_common(view_to_find={"text": "Take bug report"},
                             view_to_check={"text": "Interactive report"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "Interactive report"},
                             serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "REPORT"},
                             serial=args["serial"])()

# teardown
# moving  to home to verify if the report has been submitted
ui_steps.press_home(serial=args["serial"])()
time.sleep(60)  # Sleep is mentioned because captured BugReport might take few seconds to reflect on notifaction bar
ui_steps.wait_for_view_common(view_to_find={"text": "Tap to share your bug report"},
                              serial=args["serial"])()
