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
from testlib.util.uiatestbase import UIATestBase
from testlib.util.common import g_common_obj
from testlib.graphics.common import adb_impl, window_info


class RotateScreen(UIATestBase):

    def setUp(self):
        super(RotateScreen, self).setUp()

    def tearDown(self):
        super(RotateScreen, self).tearDown()

    def test_Rotate_180Degree(self):
        print("[RunTest]: %s" % self.__str__())
        g_common_obj.launch_app_am("com.android.settings", ".Settings")
        adb_impl.change_automatic_rotation(0)  # Turn off auto rotation
        adb_impl.screen_rotation(2)  # Rotate 180
        adb_impl.screen_rotation(0)  # Rotate back to default
        assert window_info.get_current_focus_window()[0] == "com.android.settings", "Settings not present."
