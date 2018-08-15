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
from testlib.util.common import g_common_obj


class systemUI(object):
    pass


class NotificationAndQuickSettingsImpl(object):

    """ NotificationAndQuickSettingsImpl """

    def __init__(self):
        super(NotificationAndQuickSettingsImpl, self).__init__()
        self.device = g_common_obj.get_device()
        self.device.screen.on()

    def drag_notification_panel(self):
        for _ in range(0, 3):
            self.device.press.home()
            self.device.open.notification()
            time.sleep(3)
            if self.device(resourceId="android:id/notification_main_column").exists:
                break
        assert self.device(resourceId="android:id/notification_main_column").exists,\
            "[FAILURE] Notification panel is failed to display on top of the Home Screen."
        for _ in range(0, 2):
            self.device.press.back()

    def drag_quick_settings_panel(self):
        for _ in range(0, 3):
            self.device.press.home()
            self.device.open.quick_settings()
            time.sleep(3)
            if self.device(resourceId="com.android.systemui:id/quick_settings_panel").exists:
                break
        assert self.device(resourceId="com.android.systemui:id/quick_settings_panel").exists,\
            "[FAILURE] Quick Settings panel is failed to display on top of the Home Screen."
        self.device.press.back()
