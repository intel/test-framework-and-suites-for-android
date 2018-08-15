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
from testlib.graphics.system_ui import NotificationAndQuickSettingsImpl
from testlib.graphics.common import adb_impl, window_info


class NotificationAndQuickSettings(UIATestBase):

    def setUp(self):
        super(NotificationAndQuickSettings, self).setUp()
        adb_impl.unlock_screen()
        self.notifi_quick_settings = NotificationAndQuickSettingsImpl()

    def tearDown(self):
        super(NotificationAndQuickSettings, self).tearDown()

    def test_HW_Composition_2PlanesPerOutput(self):
        """
        1.Enter into Home screen.
        2. Drag the areas corresponding to the Notification Panel.
        3. Drag the areas corresponding to the  Quick Settings Panel.
        4. Each Panel, Notification and Quick Settings, is properly displayed on top of the Home Screen.
        """
        try:
            self.notifi_quick_settings.drag_notification_panel()
            self.notifi_quick_settings.drag_quick_settings_panel()
        except:
            pass
        layer_num = window_info.get_layer_number()
        assert any(i in layer_num for i in [0, 1]) is False, "Layer number is less than 2"
