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

from testlib.scripts.android.android_step import step as android_step
from testlib.utils.ui.uiandroid import UIDevice as ui_device
from testlib.scripts.android.ui import ui_utils
import os


class step(android_step):
    """
        helper class for all gui test steps
    """
    uidevice = None

    def __init__(self, **kwargs):
        android_step.__init__(self, **kwargs)
        self.uidevice = ui_device(**kwargs)

        if "TESTLIB_UI_WATCHERS_GROUP" in os.environ:
            ui_utils.register_watchers(serial=self.serial, ui_watcher_groups=os.environ["TESTLIB_UI_WATCHERS_GROUP"])
        elif "ui_watcher_group" in kwargs:
            ui_utils.register_watchers(serial=self.serial, ui_watcher_groups=kwargs["ui_watcher_group"])
        else:
            pass
            # ui_utils.remove_watchers(serial = self.serial)
        if "TESTLIB_UI_HANDLERS_GROUP" in os.environ:
            ui_utils.register_handlers(serial=self.serial, ui_handler_groups=os.environ["TESTLIB_UI_HANDLERS_GROUP"])
        elif "ui_handler_group" in kwargs:
            ui_utils.register_handlers(serial=self.serial, ui_handler_groups=kwargs["ui_handler_group"])

    def take_picture(self, file_name):
        try:
            self.uidevice.screenshot(file_name)
        except Exception:
            pass

    def get_ui_dump(self, file_name):
        # save UI dump
        try:
            uidevice = ui_device(serial=self.serial)
            uidevice.dump(out_file=file_name, compressed=False, serial=self.serial)
        except Exception:
            pass
