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

import os

# Used defined libraries
from testlib.base.base_utils import parse_args
from testlib.scripts.android.ui import ui_steps
from testlib.utils import logger

log = None
if "LOG_PATH" in os.environ:
    testlib_log_path = os.environ["LOG_PATH"]
else:
    import testlib
    testlib_log_path = os.path.dirname(testlib.__file__) + "/logs/"

log = logger.testlib_log(log_path=testlib_log_path, log_name="testlib_default")

# ############# Get parameters ############

args = parse_args()

ui_steps.press_home(serial=args["serial"])()
ui_steps.open_settings(serial=args["serial"])()
ui_steps.click_button_common(view_to_find={"text": "System"},
                             serial=args["serial"])()
if ui_steps.wait_for_view_common(view_to_find={"text": "Developer options"},
                                 optional=True,
                                 serial=args["serial"])():
    log.info("Developer option is already enabled")
else:
    ui_steps.enable_developer_options(serial=args["serial"])()
    log.info("Developer option is enabled")

ui_steps.enable_options_from_developer_options(serial=args["serial"],
                                               developer_options=["Force 4x MSAA"])()

# TearDown
ui_steps.disable_options_from_developer_options(serial=args["serial"],
                                                developer_options=["Force 4x MSAA"])()
