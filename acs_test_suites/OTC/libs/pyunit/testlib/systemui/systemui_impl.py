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
import random
from testlib.util.common import g_common_obj


class SystemUI(object):
    def __init__(self):
        self.d = g_common_obj.get_device()

    def unlock_screen(self):
        """ Unlock screen by via input keyevent 82
        """
        print "Unlock screen via input keyevent 82"

    # wakeup screen if the the screen is in sleep
    def wakeup_screen(self):
        self.d.wakeup()

    # suspend the screen
    def suspend_screen(self, suspend_time):
        self.d.sleep()
        print "[INFO]: wait %s second to enter suspend status......" % suspend_time
        time.sleep(suspend_time)
        cmd = "cat /sys/kernel/debug/pmc_atom/sleep_state"
        result_list = g_common_obj.adb_cmd_capture_msg(cmd).split('\r\n')
        # show s3 status
        print "[INFO]: the S0I3 status: is %s" % result_list[-2].rstrip()
        # check if the device enter into S3 status
        S3_status = result_list[-2].rstrip().find("S0I3 Residency:\t0us")
        assert S3_status == -1, "[INFO]: The device enter into S3 status failed"
        print "[INFO]: The device enter into S3 status successfully"

    def lock_screen(self):
        self.d.sleep()

    def suspend_wakeup(self):
        self.d.sleep()
        time.sleep(60)
        self.d.wakeup()

    def add_clock_to_widget(self):
        self.d.press.home()
        while self.d(className="android.appwidget.AppWidgetHostView").exists:
            self.d(className="android.appwidget.AppWidgetHostView").drag.to(400, 100)
        while self.d(resourceId="com.android.deskclock:id/analog_appwidget").exists:
            self.d(resourceId="com.android.deskclock:id/analog_appwidget").drag.to(400, 100)
        self.d(resourceId="com.google.android.googlequicksearchbox:id/active").long_click()
        self.d(text="Widgets").click.wait()
        self.d(text="Analog clock").long_click()
        assert self.d(resourceId="com.android.deskclock:id/analog_appwidget").exists

    def rm_clock_widget(self):
        self.d.press.home()
        while self.d(resourceId="com.android.deskclock:id/analog_appwidget").exists:
            self.d(resourceId="com.android.deskclock:id/analog_appwidget").drag.to(400, 100)
        assert not self.d(resourceId="com.android.deskclock:id/analog_appwidget").exists, "rm clock widget"

    def launch_clock_from_widget(self):
        self.d.press.home()
        self.d(resourceId="com.android.deskclock:id/analog_appwidget").click.wait()
        assert self.d(description="Alarm").exists

    def add_lock_screen(self):
        setting_pkg_name = "com.android.settings"
        setting_activity_name = ".Settings"
        g_common_obj.launch_app_am(setting_pkg_name, setting_activity_name)
        self.d(text="Security").click()
        self.d(text="Screen lock").click()
        self.d(text="Swipe").click()
        self.d.press.back()
        self.d.press.back()

    def remove_lock_screen(self):
        setting_pkg_name = "com.android.settings"
        setting_activity_name = ".Settings"
        g_common_obj.launch_app_am(setting_pkg_name, setting_activity_name)
        self.d(text="Security").click()
        self.d(text="Screen lock").click()
        self.d(text="None").click()
        self.d.press.back()
        self.d.press.back()

    def lock_screen_take_pic(self):
        self.d.sleep()
        self.d.wakeup()
        self.d(resourceId="com.android.systemui:id/camera_button").swipe.left()
        self.d(resourceId="com.android.camera2:id/shutter_button").click()
        time.sleep(3)
        self.d.press.back()

    def change_wallpaper(self):
        self.d.press.home()
        self.d(resourceId="com.android.launcher:id/cell2").long_click()
        self.d(text="Wallpapers").click()
        self.d(resourceId="com.android.launcher:id/wallpaper_image", index=random.randint(0, 1)).click()
        self.d(text="Set wallpaper").click()
        self.d(resourceId="com.android.launcher:id/cell2").long_click()
        self.d(text="Live Wallpapers").click()
        self.d(className="android.widget.RelativeLayout", index=random.randint(0, 6)).click()
        self.d(text="Set wallpaper").click()
        self.d(resourceId="com.android.launcher:id/cell2").long_click()
        self.d(text="Gallery").click()

    def change_volume_silent_settings(self):
        start_num = (85, 198)
        end_num = (776, 198)
        setting_pkg_name = "com.android.settings"
        setting_activity_name = ".Settings"
        g_common_obj.launch_app_am(setting_pkg_name, setting_activity_name)
        self.d(text="Sound & notification").click()
        space = (end_num[0] - start_num[0]) / 10
        for i in range(10):
            self.d.click(start_num[0] + space * i, start_num[1])
            time.sleep(2)
        self.d.click(end_num[0], end_num[1])

    def quick_settings(self):
        self.d.press.home()
        self.d.open.quick_settings()
        time.sleep(2)
        self.d.open.quick_settings()
        if not self.d(resourceId="com.android.systemui:id/settings_button").exists:
            assert False, "launch setting failed!"

    def cancel_lock_screen(self):
        setting_pkg_name = "com.android.settings"
        setting_activity_name = ".Settings"
        g_common_obj.launch_app_am(setting_pkg_name, setting_activity_name)
        self.d(text="Security").click()
        self.d(text="Screen lock").click()
        self.d(text="None").click()

    def enable_lock_screen(self):
        setting_pkg_name = "com.android.settings"
        setting_activity_name = ".Settings"
        g_common_obj.launch_app_am(setting_pkg_name, setting_activity_name)
        # Be compatible with Sofia
        self.d(resourceId="com.android.settings:id/dashboard").scroll.vert.to(text="Security")
        self.d(text="Security").click()
        self.d(text="Screen lock").click()
        self.d(text="Swipe").click()

    def take_pic_from_lock_screen(self):
        self.d.sleep()
        self.d(resourceId="com.android.systemui:id/camera_button").swipe.left()
        time.sleep(2)
        if self.d(text="NEXT").exists:
            self.d(text="NEXT").click()
        self.d(resourceId="com.android.camera2:id/shutter_button").click()
        self.d(resourceId="com.android.camera2:id/mode_options_overlay").swipe.left()
        time.sleep(2)
        if not self.d(className="android.widget.ImageView").exists:
            assert False, "can't take picture!"

    def power_on_device(self, sleepTime=1):
        self.d.sleep()
        g_common_obj.adb_cmd_capture_msg("input keyevent 26")
        time.sleep(sleepTime)
        output = g_common_obj.adb_cmd_capture_msg("dumpsys window | grep mScreenOnFully")
        screenOn = output.find("mScreenOnFully=true")
        assert screenOn != -1, "backlight turned on failed."

    def power_off_device(self, sleepTime=1):
        self.d.wakeup()
        g_common_obj.adb_cmd_capture_msg("input keyevent 26")
        time.sleep(sleepTime)
        output = g_common_obj.adb_cmd_capture_msg("dumpsys window | grep mScreenOnFully")
        screenOff = output.find("mScreenOnFully=false")
        assert screenOff != -1, "backlight turned off failed."
