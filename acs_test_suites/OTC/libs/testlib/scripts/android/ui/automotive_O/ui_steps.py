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

# standard libraries
import time
import traceback
# from warnings import warn

from testlib.base.base_step import step as base_step
from testlib.scripts.android.android_step import step as android_step
from testlib.scripts.android.ui.ui_step import step as ui_step
from testlib.scripts.android.ui import ui_utils
from testlib.scripts.android.adb.adb_step import step as adb_step
from testlib.scripts.android.adb import adb_utils
from testlib.scripts.android.ui.gms import gms_utils
from testlib.utils.statics.android import statics
from testlib.utils.connections.adb import Adb
from testlib.scripts.android.ui import uiconfig
from testlib.scripts.android.ui import ui_steps


class set_pin_screen_lock(ui_step):

    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """

    def __init__(self, dut_pin="1234",
                 require_pin_to_start_device=False, wait_time=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.require_pin_to_start_device = require_pin_to_start_device
        if dut_pin:
            self.dut_pin = dut_pin
        else:
            self.dut_pin = "1234"
        if wait_time:
            self.wait_time = int(wait_time)
        else:
            self.wait_time = 5000

    def do(self):
        ui_steps.open_security_settings(serial=self.serial)()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"textContains": "Screen lock"})()
        if self.uidevice(text="Confirm your PIN").wait.exists(timeout=self.wait_time):
            if self.device_info.confirm_pin_go_back is not None:
                ui_steps.click_button(
                    serial=self.serial, view_to_find=self.device_info.confirm_pin_go_back)()
            else:
                self.uidevice.press.back()
                if adb_utils.is_virtual_keyboard_on(serial=self.serial):
                    ui_steps.press_back(serial=self.serial)()
                ui_steps.press_back(serial=self.serial)()
        else:
            ui_steps.click_button(
                serial=self.serial, view_to_find={"textContains": "PIN"})()
            if self.uidevice(text="Require PIN to start device").wait.exists(timeout=self.wait_time):
                if self.require_pin_to_start_device:
                    ui_steps.click_button(serial=self.serial, view_to_find={
                        "textContains": "Require PIN to start device"})()
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"text": "OK"}, optional=True)()
                else:
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"textContains": "No thanks"})()
                if self.device_info.dessert == "M":
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"textContains": "Continue"})()
            if self.uidevice(text="Secure start-up").wait.exists(
                    timeout=self.wait_time):
                if self.require_pin_to_start_device:
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"text": "YES"}, optional=True)()
                else:
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"text": "NO"}, optional=True)()

            ui_steps.edit_text(serial=self.serial, view_to_find={"resourceId":
                                                                 "com.android.settings:id/password_entry"},
                               value=self.dut_pin, is_password=True)()
            ui_steps.click_button(serial=self.serial, view_to_find={
                "resourceId": "com.android.settings:id/next_button"})()
            ui_steps.edit_text(serial=self.serial, view_to_find={"resourceId":
                                                                 "com.android.settings:id/password_entry"},
                               value=self.dut_pin, is_password=True)()
            ui_steps.click_button(serial=self.serial, view_to_find={
                "resourceId": "com.android.settings:id/next_button"})()
            ui_steps.click_button(
                serial=self.serial, view_to_find=self.device_info.password_done_btn_id)()

    def check_condition(self):
        if self.uidevice(className="android.widget.ListView", scrollable=True).wait.exists(timeout=self.wait_time):
            self.uidevice(scrollable=True).scroll.to(text="Screen lock")
        return self.uidevice(className="android.widget.TextView", resourceId="android:id/summary",
                             text="PIN").wait.exists(timeout=self.wait_time)


class remove_pin_screen_lock(ui_step):

    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """

    def __init__(
            self, new_mode="Swipe", dut_pin="1234", wait_time=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.new_mode = new_mode
        if dut_pin:
            self.dut_pin = dut_pin
        else:
            self.dut_pin = "1234"
        if wait_time:
            self.wait_time = int(wait_time)
        else:
            self.wait_time = 5000

    def do(self):
        ui_steps.open_security_settings(serial=self.serial)()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"textContains": "Screen lock"})()
        if self.uidevice(text="Confirm your PIN").wait.exists(timeout=self.wait_time):
            ui_steps.edit_text(view_to_find={"resourceId": "com.android.settings:id/password_entry"},
                               value=self.dut_pin, serial=self.serial, is_password=True)()
            self.uidevice.press("enter")

        ui_steps.click_button(
            serial=self.serial, view_to_find={"textContains": self.new_mode})()

        # Remove device PIN protection
        if self.uidevice(textContains=self.device_info.remove_pin_confirm_desc).wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={
                "text": self.device_info.remove_pin_confirm_button})()

    def check_condition(self):
        if self.uidevice(className="android.widget.ListView", scrollable=True).wait.exists(timeout=self.wait_time):
            self.uidevice(scrollable=True).scroll.to(text="Screen lock")
        return self.uidevice(className="android.widget.TextView", resourceId="android:id/summary",
                             text=self.new_mode).wait.exists(timeout=self.wait_time)


class open_security_settings(adb_step):

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """

    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.component = "com.android.settings/.SecuritySettings"

    def do(self):
        ui_steps.am_start_command(
            serial=self.serial,
            component=self.component)()

    def check_condition(self):
        # check performed in the last step from do()
        return True


class open_users_settings(adb_step):

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """

    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)
        self.component = 'com.android.settings/.Settings\$UserSettingsActivity'

    def do(self):
        ui_steps.am_start_command(
            serial=self.serial,
            component=self.component)()

    def check_condition(self):
        # check performed in the last step from do()
        return True


class am_start_command(adb_step):

    """ description:
            Opens the WiFi Settings page using an intent.

        usage:
            wifi_steps.open_wifi_settings()()

        tags:
            ui, android, settings, wifi, intent
    """

    def __init__(self, component=None, timeout=20,
                 view_to_check=None, view_presence=True, **kwargs):
        self.component = component
        self.timeout = timeout
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        if self.component:
            self.package = self.component.split("/")[0]
        adb_step.__init__(self, **kwargs)
        self.step_data = False

    def do(self):
        if self.package:
            clean_command = "pm clear {0}".format(self.package)
            self.process = self.adb_connection.run_cmd(command=clean_command, ignore_error=False,
                                                       timeout=self.timeout, mode="sync")
        if self.component:
            open_command = "am start -n {0}".format(self.component)
            self.step_data = self.adb_connection.run_cmd(command=open_command, ignore_error=False,
                                                         timeout=self.timeout, mode="sync")

    def check_condition(self):
        stdout = self.step_data.stdout.read()
        stderr = self.step_data.stderr.read()
        self.set_passm("am start -n {0}".format(self.component))
        self.set_errorm(
            "", "am start -n {0}: \n\tStdout\n{1}\n\tStderr\n{2}".format(self.component, stdout, stderr))
        if "Error" in stdout or "Exception" in stdout:
            self.step_data = False
            return self.step_data
        if self.view_to_check is None:
            self.step_data = True
            return self.step_data
        if self.view_presence:
            self.step_data = self.uidevice(
                **self.view_to_check).wait.exists(timeout=self.timeout)
        else:
            self.step_data = self.uidevice(
                **self.view_to_check).wait.gone(timeout=self.timeout)
        return self.step_data


class am_stop_package(adb_step, ui_step):

    """ Description:
            Executes command 'adb shell am force-stop [package_name]'. Pass
            package name to package_name parameter.
        Usage:
            ui_steps.am_stop_package(serial=serial,
                                        package_name="com.android.settings")()
        tags:
            ui, android, stop, package
    """

    def __init__(self, package_name, view_to_check=None,
                 view_presence=True, timeout=5000, **kwargs):
        """
        :param package_name: package name of the app to be stopped
        :param view_to_check: view after a package is closed to be checked
        :param view_presence: should be True if appears, False if disappears
        :param kwargs: serial and standard kwargs for base_step
        """
        adb_step.__init__(self, **kwargs)
        ui_step.__init__(self, **kwargs)
        self.package_name = package_name
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.timeout = timeout
        self.step_data = False

    def do(self):
        try:
            self.adb_connection.run_cmd(
                "am force-stop " + str(self.package_name))
            self.step_data = True
        except Exception as e:
            info_message = "Exception encountered when stop " + \
                str(self.package_name) + ": " + e.message
            if self.serial:
                info_message = "[ " + str(self.serial) + " ] " + info_message
            self.logger.info(info_message)

    def check_condition(self):
        if self.step_data is False:
            return False
        if self.view_to_check is None:
            return True
        print self.view_to_check
        if self.view_presence:
            self.step_data = self.uidevice(
                **self.view_to_check).wait.exists(timeout=self.timeout)
        else:
            self.step_data = self.uidevice(
                **self.view_to_check).wait.gone(timeout=self.timeout)
        return self.step_data


# TODO: rename with open_quick_settings_with_swipe
# add desciption
class open_notifications_menu(ui_step):

    def __init__(self, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.set_passm("Open notification menu - swipe")
        self.set_errorm("", "Open notification menu - swipe")
        self.x_center = self.uidevice.info['displayWidth'] / 2
        self.y_center = self.uidevice.info['displayHeight'] / 2

    def do(self):
        ui_steps.swipe(serial=self.serial, sx=self.x_center, sy=1,
                       ex=self.x_center, ey=self.y_center, steps=10)()
        time.sleep(1)
        ui_steps.swipe(serial=self.serial, sx=self.x_center, sy=1,
                       ex=self.x_center, ey=self.y_center, steps=10)()
        time.sleep(1)

    def check_condition(self):
        return ui_steps.wait_for_view(view_to_find={"resourceId": "com.android.systemui:id/quick_settings_container"},
                                      serial=self.serial)()


class press_all_apps(ui_step):

    """ description:
            opens all application activity

        usage:
            ui_steps.press_all_apps()

        tags:
            ui, android, press, click, allapps, applications
    """

    def __init__(self, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.step_data = False

    def do(self):
        if self.device_info.all_apps_icon is not None:
            ui_steps.press_home(serial=self.serial)()
            time.sleep(1)
            self.uidevice(descriptionContains="Apps").click.wait()
            dut_platform = statics.Device(serial=self.serial)
            self.dut_dessert = dut_platform.dessert
            while not self.uidevice(text="Calculator").wait.exists(timeout=1000):
                first_app = self.uidevice(className="android.widget.TextView")
                maxx = self.uidevice.info['displaySizeDpX']
                maxy = self.uidevice.info['displaySizeDpY']
                # swipe horizontally
                self.uidevice.swipe(
                    1, int(maxy / 2), int(maxx) - 1, int(maxy / 2))
                self.uidevice.swipe(
                    int(maxx / 2), int(maxy / 2), int(maxx / 2), int(maxy) - 1)
                if first_app == self.uidevice(className="android.widget.TextView"):
                    break
            self.step_data = True
        else:
            self.logger.error("All apps icon not available for platform: {"
                              "0}".format(self.device_info.platform))

    def check_condition(self):
        if self.step_data is False:
            return self.step_data
        adb_connection = Adb(serial=self.serial)
        product_name = adb_connection.parse_cmd_output(
            cmd="cat /system/build.prop", grep_for="ro.product.name")
        if product_name:
            ro_name = product_name.split("=")[1]
        if self.dut_dessert == "M" and ro_name is not "r0_bxtp_abl":
            return self.uidevice(
                resourceId="com.android.launcher3:id/apps_list_view").wait.exists(timeout=20000)
        elif self.dut_dessert == "L":
            return self.uidevice(
                descriptionContains="Apps page 1 of").wait.exists(timeout=20000)
        elif ro_name == "r0_bxtp_abl":
            pass


class press_home(ui_step):

    """ description:
            opens home page

        usage:
            ui_steps.press_home()

        tags:
            ui, android, press, click, home, homepage
    """

    def __init__(self, wait_time=20000, **kwargs):
        self.wait_time = wait_time
        ui_step.__init__(self, **kwargs)
        # adb_connection = Adb(serial=self.serial)
        # product_name = adb_connection.parse_cmd_output(
        #     cmd="cat /system/build.prop", grep_for="ro.product.name")
        # self.ro_name = None
        # if product_name:
        #     ro_name = product_name.split("=")[1]
        #     self.ro_name = ro_name
        self.step_data = False

    @property
    def home_state(self):
        #
        if self.uidevice(textContains="Google").wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.android.systemui:id/user_name").wait.exists(timeout=100) or \
           self.uidevice(descriptionContains="Home screen", className="android.widget.LinearLayout")\
               .wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.google.android.googlequicksearchbox:id/vertical_search_button")\
               .wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.google.android.googlequicksearchbox:id/search_edit_frame")\
               .wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.android.car.overview:id/gear_button").wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.android.car.overview:id/voice_button").wait.exists(timeout=100) or \
           self.uidevice(resourceId="com.android.launcher3:id/btn_qsb_search").wait.exists(timeout=100):
            return True
        else:
            return False

    def do(self):
        # if self.home_state:
        #    self.logger.info("Home screen already present [ {0} ]".format(
        # self.serial))
        time_elapsed = 0
        while time_elapsed < self.wait_time:
            if self.device_info.device_type == "tab":
                # self.uidevice.press.recent()
                self.uidevice.press.home()
            else:
                self.uidevice.open.quick_settings()
            if self.home_state:
                self.step_data = True
                break
            time_elapsed += 300

    def check_condition(self):
        # time_elapsed = 0
        # while time_elapsed < self.wait_time:
        #    if self.home_state:
        #        return True
        #    else:
        #        self.uidevice.press.home()
        #    time_elapsed += 300
        return self.step_data


class press_recent_apps(ui_step):

    """ description:
            opens recent apps

        usage:
            ui_steps.press_recent_apps()

        tags:
            ui, android, press, click, recent apps, homepage
    """

    def do(self):
        if not self.uidevice(resourceId="com.android.systemui:id/recents_view").wait.exists(timeout=1000) and not \
                self.uidevice(textContains="recent screens").wait.exists(timeout=1000):
            self.uidevice.press.recent()

    def check_condition(self):
        return self.uidevice(resourceId="com.android.systemui:id/task_view_content").wait.exists(timeout=1000) or \
            self.uidevice(text="Your recent screens appear here").wait.exists(
                timeout=1000)


class app_in_recent_apps(base_step):

    """ description:
            opens recent apps and checks if <app_name> app is present

        usage:
            ui_steps.app_in_recent_apps(app_name = "Chrome")

        tags:
            ui, android, press, click, recent apps, homepage, app
    """

    def __init__(self, app_name, target="tablet", **kwargs):
        self.app_name = app_name
        self.target = target
        base_step.__init__(self, **kwargs)
        self.set_passm("{0} is present in recent apps".format(self.app_name))
        self.set_errorm(
            "", "Could not find {0} in recent apps".format(self.app_name))

    def do(self):
        ui_steps.press_recent_apps(serial=self.serial)()

    def check_condition(self):
        app_filter = {"descriptionContains": self.app_name}
        if self.target == "tablet":
            return ui_utils.is_view_visible_scroll_left(
                view_to_find=app_filter)
        elif self.target == "phone":
            return ui_utils.is_view_visible(view_to_find=app_filter)


class open_app_from_recent_apps(android_step):

    """ description:
            Opens <app_name> app from recent apps.
            If the DUT is a tablet (default), it will swipe to the
            left for multiple apps in recent apps.
            If the DUT is a phone, it will scroll down for multiple
            apps in recent apps.

        usage:
            ui_steps.open_app_in_recent_apps(app_name = "Chrome")

        tags:
            ui, android, press, click, recent apps, homepage, app
    """

    def __init__(self, app_name, target="tablet", **kwargs):
        android_step.__init__(self, **kwargs)
        self.app_name = app_name
        self.target = target
        self.set_passm("Open {0} from recent apps".format(self.app_name))
        self.set_errorm(
            "", "Could not open {0} from recent apps".format(self.app_name))

    def do(self):
        ui_steps.press_recent_apps(serial=self.serial)()

    def check_condition(self):
        app_filter = {"descriptionContains": self.app_name}
        if self.target == "tablet":
            return ui_utils.is_view_visible_scroll_left(
                view_to_find=app_filter, click=True)
        elif self.target == "phone":
            return ui_utils.is_view_visible(
                view_to_find=app_filter, click=True)


class open_app_from_allapps(ui_step):

    """ description:
            opens the application identified by <view_to_finWidgetd> from
                all application activity
                if <view_to_check> given it will check that
                the object identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

        usage:
            ui.steps.open_app_from_allapps(view_to_find = {"text": "Settings"})()

        tags:
            ui, android, press, click, app, application, allapps
    """

    def __init__(self, view_to_find, view_to_check=None,
                 view_presence=True, wait_time=20000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.wait_time = wait_time
        if "instance" not in self.view_to_find:
            self.view_to_find["instance"] = 0
        self.set_errorm(
            "", "App {0} could not be opened applications page".format(view_to_find))
        self.set_passm(
            "App {0} opened for applications page".format(view_to_find))

    def do(self):

        ui_steps.press_all_apps(serial=self.serial)()
        ui_utils.click_apps_entry(
            serial=self.serial, view_to_find=self.view_to_find)

    def check_condition(self):
        if self.view_to_check is None:
            return True
        self.uidevice(**self.view_to_check).wait.exists(timeout=self.wait_time)
        exists = self.uidevice(**self.view_to_check).wait.exists(timeout=1000)
        return exists if self.view_presence else not exists


class find_app_from_allapps(ui_step):

    """ description:
            finds the application identified by <view_to_find> from
                all application activity

        usage:
            ui.steps.find_app_from_allapps(view_to_find = {"text": "Settings"})()

        tags:
            ui, android, find, app, application, allapps
    """

    def __init__(self, view_to_find, presence=True, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.presence = presence
        self.set_errorm(
            "", "App {0} was not found in applications page".format(view_to_find))
        self.set_passm(
            "App {0} found in applications page".format(view_to_find))

    def do(self):
        ui_steps.press_all_apps(serial=self.serial)()

    def check_condition(self):
        return ui_steps.wait_for_view(
            serial=self.serial, view_to_find=self.view_to_find, presence=self.presence)()


class open_smart_lock_settings(ui_step):

    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """

    def __init__(self, pin, **kwargs):
        self.pin = pin
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_security_settings(serial=self.serial)()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Smart Lock"},
                              view_to_check={"resourceId": "com.android.settings:id/password_entry"})()
        ui_steps.edit_text(serial=self.serial, view_to_find={"resourceId": "com.android.settings:id/password_entry"},
                           value=self.pin, is_password=True)()
        self.uidevice.press("enter")

    def check_condition(self):
        return ui_steps.wait_for_view(
            serial=self.serial, timeout=5000, view_to_find={"text": "Trusted devices"})()


class open_settings(ui_step):

    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """

    def __init__(
            self, intent=False, settings_check_point=".*?(S|s)ettings", timeout=5000, **kwargs):
        self.intent = intent
        self.settings_check_point = settings_check_point
        self.timeout = timeout
        ui_step.__init__(self, **kwargs)

    def do(self):
        if self.intent:
            ui_steps.am_start_command(
                serial=self.serial, component="com.android.settings/.Settings")()
        else:
            all_apps_icon = self.device_info.all_apps_icon
            if all_apps_icon is not None:
                # for property in all_apps_icon:
                #    if self.uidevice(**property).wait.exists(
                # timeout=self.timeout)
                #        self.uidevice(**property).click.wait()
                #        break
                ui_steps.open_app_from_allapps(
                    serial=self.serial, view_to_find={"text": "Settings"})()
            else:
                ui_steps.press_car(serial=self.serial)()
                # click_button_with_scroll(serial=self.serial, view_to_find={
                #    "text": "Settings"})()
                # Todo need to replace the below lines with above commented
                # line when two settings in car replaced with actual one.
                # self.uidevice(scrollable=True).scroll.toEnd()
                # self.uidevice(index="6",
                #              className="android.widget.FrameLayout").child(
                #              text="Settings").click()
                for i in range(0, 5):
                    if self.uidevice(text="Settings").count == 2:
                        self.uidevice(text="Settings")[1].click()
                        break
                    else:
                        self.uidevice(scrollable=True).scroll()
                else:
                    self.uidevice(text="Settings").click()

    def check_condition(self):
        return ui_steps.wait_for_view(serial=self.serial, timeout=5000,
                                      view_to_find={"textMatches": self.settings_check_point}, iterations=1)()


class open_settings_app(ui_step):

    """ description:
            opens an app/activity ideintified by <view_to_find> from
                settings page starting from homepahe
                if <view_to_check> given it will check that
                the object identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

        usage:
            ui_steps.open_settings_app(
                view_to_find = {"text": "Apps"},
                view_to_check = {"text": "Donwloaded"})()

        tags:
            ui, android, press, click, app, application, settings, homepage
    """

    def __init__(self, view_to_find, view_to_check=None,
                 view_presence=True, wait_time=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.wait_time = wait_time
        self.set_errorm("", "Could not open app {0} from settings checking {1}".format(
            view_to_find, view_to_check))
        self.set_passm(
            "Open app {0} from settings checking {1}".format(view_to_find, view_to_check))

    def do(self):
        ui_steps.open_settings(serial=self.serial)()
        ui_steps.open_app_from_settings(
            serial=self.serial, view_to_find=self.view_to_find)()

    def check_condition(self):
        if self.view_to_check is None:
            return True
        if self.wait_time:
            self.uidevice(
                **self.view_to_check).wait.exists(timeout=self.wait_time)
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


class open_app_from_settings(ui_step):

    """ description:
            opens an app/activity ideintified by <view_to_find> from
                settings page
                if <view_to_check> given it will check that
                the object identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

        usage:
            ui_steps.open_app_from_settings(view_to_find =
                    {"text": "Apps"}, view_to_check = {"text": "Donwloaded"})()

        tags:
            ui, android, press, click, app, application, settings
    """

    def __init__(self, view_to_find, view_to_check=None,
                 view_presence=True, wait_time=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.wait_time = wait_time
        # self.scroll = scroll
        self.set_errorm("", "Could not open app {0} from settings checking {1}".format(
            view_to_find, view_to_check))
        self.set_passm(
            "Open app {0} from settings checking {1}".format(view_to_find, view_to_check))

    def do(self):
        if self.uidevice(scrollable=False).exists:
            self.uidevice(scrollable=False).scroll.vert.toBeginning(
                steps=100, max_swipes=1000)
            self.uidevice(scrollable=False).scroll.to(**self.view_to_find)
        else:
            self.uidevice(scrollable=True).scroll.vert.toBeginning(
                steps=100, max_swipes=1000)
            self.uidevice(scrollable=True).scroll.to(**self.view_to_find)
        self.uidevice(**self.view_to_find).click.wait()

    def check_condition(self):
        if self.view_to_check is None:
            return True
        if self.wait_time:
            self.uidevice(
                **self.view_to_check).wait.exists(timeout=self.wait_time)
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


# TODO: remake
class open_quick_settings(ui_step):

    """ description:
            opens quick settings

        usage:
            ui_steps.open_quick_settings()

        tags:
            ui, android, open, press, click, quicksettings
 """

    def __init__(self, version="L", **kwargs):
        ui_step.__init__(self, **kwargs)
        self.version = version
        self.set_errorm("", "Could not open quick setings")
        self.set_passm("Open quick settings")

    def do(self):
        if self.device_info.dessert == "L" or self.device_info.dessert == "M":
            time.sleep(1)
            self.uidevice.open.quick_settings()
            time.sleep(1)
            self.uidevice.open.quick_settings()
            time.sleep(1)
        else:
            self.uidevice.open.quick_settings()

    def check_condition(self):
        return self.uidevice(
            descriptionContains="Battery").wait.exists(timeout=1000)


class open_playstore(ui_step):

    """ description:
            opens Play store application from all application page

        usage:
            ui_steps.open_play_store()

        tags:
            ui, android, press, click, playstore, allapps, applications
    """

    def do(self):
        ui_steps.open_app_from_allapps(
            serial=self.serial, view_to_find={"text": "Play Store"})()

    def check_condition(self):
        self.uidevice.wait.idle()
        return self.uidevice(text="Add a Google Account").wait.exists(timeout=5000) or \
            self.uidevice(
                text="HOME", resourceId="com.android.vending:id/title").wait.exists(timeout=20000)


class open_google_books(ui_step):

    """ description:
            opens Google Books application from all application page

        usage:
            ui_steps.open_google_books()

        tags:
            ui, android, press, click, books, allapps, applications
    """

    def do(self):
        ui_steps.open_app_from_allapps(
            serial=self.serial, view_to_find={"text": "Play Books"})()

    def check_condition(self):
        self.uidevice.wait.idle()
        return self.uidevice(text="Add a Google Account").wait.exists(timeout=100) or \
            self.uidevice(text="Read Now").wait.exists(timeout=100) or \
            self.uidevice(text="My Library").wait.exists(timeout=100) or \
            self.uidevice(text="Settings").wait.exists(timeout=100) or\
            self.uidevice(text="Help").wait.exists(timeout=100)


class add_google_account(ui_step):

    """ description:
            adds google account <account> from settings page

        usage:
            ui_steps.add_google_accout(version = "L",
                                      account = "account_email",
                                      paswword = "account_password")

        tags:
            ui, android, google, account, playstore, apps
    """

    def __init__(self, account=uiconfig.GoogleAccount.EMAIL_ID,
                 password=uiconfig.GoogleAccount.PASSWORD, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.account = account
        self.password = password
        self.version = self.debug_info.dessert

    def do(self):
        ui_steps.open_settings(serial=self.serial)()

        if self.version == "L":
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"text": "Accounts"}, view_to_check={"text": "Add account"})()
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"text": "Add account"}, view_to_check={"text": "Google"})()

        elif self.version == "K":
            ui_steps.open_app_from_settings(serial=self.serial, view_to_find={"text": "Add account"},
                                            view_to_check={"text": "Add an account"})()

        elif self.version == "O":
            ui_steps.open_app_from_settings(serial=self.serial, view_to_find={"text": "Users & accounts"},
                                            view_to_check={"text": "Users & accounts"})()
            ui_steps.click_button(
                serial=self.serial, view_to_find={"text": "Add account"})()

            ui_steps.click_button(
                serial=self.serial, view_to_find={"text": "Google"})()

            ui_steps.edit_text(serial=self.serial, view_to_find={
                "text": "Email or phone"}, value=self.account)()

            ui_steps.click_button_common(
                serial=self.serial, view_to_find={"text": "NEXT"})()

            ui_steps.edit_text(serial=self.serial, view_to_find={"text": "Enter your password"},
                               value=self.password, is_password=True)()

            ui_steps.click_button_common(
                serial=self.serial, view_to_find={"text": "NEXT"})()

            ui_steps.click_button_common(
                serial=self.serial, view_to_find={"text": "I AGREE"})()
            # todo: check what else can be checked

            ui_steps.click_button_common(serial=self.serial,
                                         view_to_find={
                                             "resourceId": "com.google.android.gms:id/next_button"},
                                         view_to_check={"text": self.account})()  # todo: check what else can be checked

        if self.version != "O":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Google"},
                                  view_to_check={"textContains": "Do you want to add an existing"})()

            ui_steps.click_button(serial=self.serial, view_to_find={
                "text": "Existing"}, view_to_chec={"text": "Sign in"})()

            ui_steps.edit_text(serial=self.serial,
                               view_to_find={
                                   "resourceId": "com.google.android.gsf.login:id/username_edit"},
                               value=self.account)()
            ui_steps.edit_text(serial=self.serial,
                               view_to_find={
                                   "resourceId": "com.google.android.gsf.login:id/password_edit"},
                               value=self.password, is_password=True)()

            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "resourceId": "com.google.android.gsf.login:id/next_button"},
                                  view_to_check={"text": "OK"})()

            ui_steps.click_button(serial=self.serial, view_to_find={"text": "OK"}, wait_time=99999,
                                  view_to_check={"text": "Google services"})()

            ui_steps.click_button(serial=self.serial, view_to_find={
                "descriptionContains": self.device_info.next_btn_id})()

        if self.version == "L":
            self.uidevice(textContains="Set up payment").wait.exists(
                timeout=3000)
            ui_steps.click_button(serial=self.serial, view_to_find={"textContains": "Skip"}, wait_time=3000,
                                  view_to_check={"text": "Google"})()
        elif self.version == "K":
            self.uidevice(serial=self.serial, text="Not now").wait.exists(
                timeout=3000)
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Not now"}, wait_time=5000,
                                  view_to_check={"textContains": "Account sign"})()

            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "resourceId": "com.google.android.gsf.login:id/next_button"},
                                  view_to_check={"text": "Settings"})()

    def check_condition(self):
        if self.version == "L":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Google"}, wait_time=3000,
                                  view_to_check={"text": self.account})()

        elif self.version == "K":
            ui_steps.open_app_from_settings(serial=self.serial, view_to_find={"text": "Google"},
                                            view_to_check={"text": self.account})()

        elif self.version == "O":
            ui_steps.click_button_common(serial=self.serial, view_to_find={"text": self.account},
                                         view_to_check={"text": self.account})()


class add_app_from_all_apps_to_homescreen(ui_step):

    """ description:
            Click on an App from App view and drag it
            to home screen

        usage:
            test_verification('app_to_drag_from_app_view')()

        tags:
            homescreen, drag app icon
    """

    def __init__(self, view_text, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_text = view_text
        self.set_passm(str(self.view_text))

    def do(self):
        ui_steps.press_all_apps(serial=self.serial)()
        app = self.uidevice(text=self.view_text)
        self.x_coord = (
            app.info['bounds']['left'] + app.info['bounds']['right']) / 2
        self.y_coord = (
            app.info['bounds']['bottom'] + app.info['bounds']['top']) / 2
        ui_steps.swipe(serial=self.serial, sx=self.x_coord,
                       sy=self.y_coord, ex=self.x_coord, ey=self.y_coord)()

    def check_condition(self):
        self.uidevice.wait.update()
        return self.uidevice(text=self.view_text).wait.exists(timeout=1000)


class uninstall_app_from_apps_settings(ui_step, base_step):

    """ description:
            unistalls <app_name> application from Apps page in settings
                it check that <package_name> package is not present
                anymore in pm list packages

        usage:
            ui_steps.uninstall_app_from_apps_settings(
                app_name = "Angry Birds",
                package_name = "com.rovio.angrybirdsstarwars.ads.iap")()

        tags:
            ui, android, uninstall, app, apps, application
    """

    def __init__(self, app_name, package_name, **kwargs):
        self.app_name = app_name
        self.package_name = package_name
        ui_step.__init__(self, **kwargs)
        adb_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.click_button(serial=self.serial, view_to_find={"text": self.app_name},
                              view_to_check={"textContains": "Uninstall"})()
        ui_steps.click_button(serial=self.serial, view_to_find={
            "textContains": "Uninstall"}, view_to_check={"text": "OK"})()
        ui_steps.click_button(
            serial=self.serial,
            view_to_find={
                "text": "OK"})()
        if self.uidevice(text="Google Play Store").wait.exists(timeout=1000):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "OK"}, view_to_check={"text": "OK"},
                                  view_presence=False)()

    def check_condition(self):
        if self.package_name:
            command = "pm list packages"
            grep_stdout = self.adb_connection.parse_cmd_output(
                cmd=command,
                grep_for=self.package_name
            )
            return self.package_name not in grep_stdout
        else:
            return True


class uninstall_app(ui_step):

    """ description:
            unistalls <app_name> application from Apps starting from
                homepage
                it check that <package_name> package is not present
                anymore in pm list packages

        usage:
            ui_steps.uninstall_app(
                app_name = "Angry Birds",
                package_name = "com.rovio.angrybirdsstarwars.ads.iap")()

        tags:
            ui, android, uninstall, app, apps, application, homepage
    """

    def __init__(self, app_name, package_name, **kwargs):
        self.app_name = app_name
        self.package_name = package_name
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_settings(serial=self.serial)()
        ui_steps.open_app_from_settings(
            serial=self.serial, view_to_find={"text": "Apps"}, view_to_check="Donwloaded")()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": self.app_name},
                              view_to_check={"textContains": "Uninstall"})()
        ui_steps.click_button(serial=self.serial, view_to_find={
            "textContains": "Uninstall"}, view_to_check={"text": "OK"})()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "OK"}, view_to_check={"text": "OK"},
                              view_presence=False)()

    def check_condition(self):
        if self.package_name:
            command = "pm list packages"
            grep_stdout = self.adb_connection.parse_cmd_output(
                cmd=command,
                grep_for=self.package_name
            )
            return self.package_name not in grep_stdout
        else:
            return True


class open_display_from_settings(ui_step):

    """ description:
            open display menu from settings

        usage:
            ui_steps.open_display_from_settings(view_to_check =
                {"text":"Daydream"})()

        tags:
            ui, android, press, click, app, application, settings
    """

    def __init__(self, view_to_check=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_check = view_to_check

    def do(self):
        ui_steps.open_settings(serial=self.serial)()
        ui_steps.open_app_from_settings(serial=self.serial, print_error="Failed to open Display",
                                        view_to_find={"text": "Display"}, view_to_check={"text": "Daydream"})()

    def check_condition(self):
        if self.view_to_check is None:
            return True
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


class open_picture_from_gallery(ui_step, adb_step):

    """ description:
            open picture from gallery

        usage:
            ui_steps.open_picture_from_gallery()()

        tags:
            ui, android, press, click, picture, gallery
    """

    def __init__(self, view_to_check=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        adb_step.__init__(self, **kwargs)
        self.view_to_check = view_to_check

    def do(self):
        ui_steps.open_app_from_allapps(
            serial=self.serial, view_to_find={'text': 'Gallery'})()
        resolution = ui_utils.get_resolution(serial=self.serial)
        self.uidevice.click(int(resolution[0]) / 2, int(resolution[1]) / 3)

    def check_condition(self):
        if self.view_to_check is None:
            return True
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


class enable_developer_options(ui_step):

    """ description:
            enables developer options in Settings

        usage:
            ui_steps.enable_developer_options()()

        tags:
            ui, android, developer, options
    """

    def __init__(self, intent=False, **kwargs):
        self.intent = intent
        ui_step.__init__(self, **kwargs)

    def do(self):
        if self.intent:
            ui_steps.am_start_command(
                serial=self.serial, component="com.android.settings/.DevelopmentSettings")()
        else:
            ui_steps.open_settings(serial=self.serial)()
            ui_steps.click_button_common(
                serial=self.serial, view_to_find={"text": "System"}, optional=True)()
            ui_steps.click_button_common(serial=self.serial, view_to_find={"textContains": "About "},
                                         view_to_check={"text": "Build number"})()
            for i in range(7):
                ui_steps.click_button_common(
                    serial=self.serial, view_to_find={"text": "Build number"})()
            ui_steps.press_back(serial=self.serial)()

    def check_condition(self):
        if self.intent:
            return True
        return self.uidevice(
            text="Developer options").wait.exists(timeout=1000)


class disable_options_from_developer_options(ui_step):

    """ description:
            disables an option from developer options

        usage:
            ui_steps.disable_options_from_developer_options(developer_options =
                                                         ["Verify apps over USB"])()

        tags:
            ui, android, disable, developer options
    """

    def __init__(self, developer_options, enabled=False, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.enabled = enabled
        self.dev_opts = developer_options
        self.set_passm("{0} is(are) disabled".format(developer_options))
        self.set_errorm(
            "", "One or more options from {0} could not be disabled".format(developer_options))

    def do(self):
        if not self.enabled:
            if not ui_utils.is_developer_options_enabled(serial=self.serial):
                ui_steps.press_home(serial=self.serial)()
                ui_steps.enable_developer_options(serial=self.serial)()
            ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "Developer options"},
                                         view_to_check={"text": "Take bug report"})()
        version = adb_utils.get_android_version(
            serial=self.serial, full_version_name=True)
        is_switch = True
        if version == "5.0":
            is_switch = False
        for opt in self.dev_opts:
            ui_steps.click_checkbox_button(serial=self.serial, view_to_find={"text": opt}, state="OFF", scrollable=True,
                                           is_switch=is_switch, relationship="right")()

    def check_condition(self):
        return True


class enable_options_from_developer_options(ui_step):

    """ description:
            enables an option from developer options
            if <enabled> parameter is True, <Developer options> is enabled

        usage:
            ui_steps.enable_options_from_developer_options(developer_options =
                                                         ["Verify apps over USB"])()

        tags:
            ui, android, enable, developer options
    """

    def __init__(
            self, developer_options, enabled=False, confirm_view="Enable", **kwargs):
        self.enabled = enabled
        self.confirm_view = confirm_view
        ui_step.__init__(self, **kwargs)
        self.dev_opts = developer_options
        self.set_passm("{0} is(are) enabled".format(developer_options))
        self.set_errorm(
            "", "One or more options from {0} could not be enabled".format(developer_options))

    def do(self):
        if not self.enabled:
            if not ui_utils.is_developer_options_enabled(serial=self.serial):
                ui_steps.press_home(serial=self.serial)()
                ui_steps.enable_developer_options(serial=self.serial)()
            ui_steps.click_button_common(serial=self.serial, view_to_find={"text": "Developer options"},
                                         view_to_check={"text": "Take bug report"})()
        version = adb_utils.get_android_version(
            serial=self.serial, full_version_name=True)

        is_switch = True
        if version == "5.0":
            is_switch = False
        for opt in self.dev_opts:
            ui_steps.click_checkbox_button(serial=self.serial, view_to_find={"text": opt}, is_switch=is_switch,
                                           scrollable=True, confirm_view={
                                               "text": self.confirm_view},
                                           relationship="right")()

    def check_condition(self):
        return True


class enable_oem_unlock(ui_step):

    """ description:
            enables Oem unlock from "Developer options"

        usage:
            ui_steps.enable_oem_unlock()()

        tags:
            ui, android, enable, developer options
    """

    def __init__(self, enabled=False, **kwargs):
        self.enabled = enabled
        ui_step.__init__(self, **kwargs)

    def do(self):
        if not self.enabled:
            ui_steps.press_home(serial=self.serial)()
            ui_steps.enable_developer_options(
                serial=self.serial,
                intent=True)()
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Developer options"},
                                  view_to_check={"text": "Take bug report"})()
        version = adb_utils.get_android_version(
            serial=self.serial, full_version_name=True)
        is_switch = True
        oem_switch_text = "OEM unlocking"
        if version == "5.0":
            is_switch = False
            oem_switch_text = "Enable OEM unlock"

        ui_steps.click_checkbox_button(serial=self.serial, view_to_find={"text": oem_switch_text}, is_switch=is_switch,
                                       scrollable=True, confirm_view=self.device_info.oem_unlock_btn_id,
                                       relationship="right")()

    def check_condition(self):
        # Check performed in the last step from do()
        return True


class allow_unknown_sources(ui_step):

    """ description:
            enables/disables Unknwon sources according to <state>

        usage:
            cts_steps.allow_unknown_sources(state = "ON")()

        tags:
            ui, android, cts, allow, unknown_sources
    """

    def __init__(self, state="ON", **kwargs):
        self.state = state
        ui_step.__init__(self, **kwargs)
        self.set_passm("Allow unknown sources is {0}".format(self.state))
        self.set_errorm(
            "", "Allow unknown sources could not be set {0}".format(self.state))

    def do(self):
        ui_steps.open_security_settings(serial=self.serial)()
        self.uidevice(scrollable=True).scroll.to(text="Unknown sources")

        if self.state == "ON":
            ui_steps.click_checkbox_button(serial=self.serial, view_to_find={"text": "Unknown sources"},
                                           confirm_view={"text": "OK"}, state=self.state, is_switch=True,
                                           relationship="right")()
        else:
            ui_steps.click_checkbox_button(serial=self.serial, view_to_find={"text": "Unknown sources"},
                                           state=self.state, is_switch=True, relationship="right")()

    def check_condition(self):
        return ui_utils.is_checkbox_checked(serial=self.serial, view_to_find={"text": "Unknown sources"},
                                            is_switch=True, relationship="right")


class put_device_into_sleep_mode(ui_step):

    """ description:
            sets the device into sleep mode with sleep button
            checks the logcat for sleep message
            fails if the DUT is already in sleep mode

        usage:
            ui_steps.put_device_into_sleep_mode()()

        tags:
            ui, android, sleep
    """

    def __init__(self, tries=5, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.tries = tries

    def do(self):
        while adb_utils.is_power_state(serial=self.serial, state="ON") and self.tries > 0:
            self.uidevice.sleep()
            time.sleep(3)
            self.tries -= 1

    def check_condition(self):
        return adb_utils.is_power_state(serial=self.serial, state="OFF")


class wake_up_device(ui_step):

    """ description:
            wakes the device from sleep with sleep button
            checks the logcat for wake message

        usage:
            ui_steps.wake_up_device()()

        tags:
            ui, android, wake
    """

    def __init__(self, tries=5, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.tries = tries

    def do(self):
        adb_utils.stay_on(serial=self.serial)
        while adb_utils.is_power_state(serial=self.serial, state="OFF") and self.tries > 0:
            self.uidevice.wakeup()
            time.sleep(3)
            self.tries -= 1

    def check_condition(self):
        return adb_utils.is_power_state(serial=self.serial, state="ON")


class unlock_device_swipe(ui_step):

    """ description:
            unlocks the screen with swipe

        usage:
            ui_steps.unlock_device_swipe()()

        tags:
            ui, android, unlock
    """

    def __init__(self, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.set_passm("Unlock device - swipe")
        self.set_errorm("", "Unlock device - swipe")

    def do(self):
        # Sometimes the screen may be off on some low performance devices
        self.uidevice.wakeup()
        ui_steps.swipe(
            serial=self.serial,
            sx=200,
            sy=600,
            ex=200,
            ey=0,
            steps=15)()
        time.sleep(2)

    def check_condition(self):
        return not ui_utils.is_device_locked(serial=self.serial)


class unlock_device_pin(ui_step):

    """ description:
            unlocks the screen with PIN

        usage:
            ui_steps.unlock_device_pin(pin = "1234")()

        tags:
            ui, android, unlock, PIN
    """

    def __init__(self, pin="1234", wrong_pin=False, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.pin = pin
        self.wrong_pin = wrong_pin
        self.set_passm("Unlock device - PIN")
        self.set_errorm("", "Unlock device - PIN")

    def do(self):
        # Sometimes the screen may be off on some low performance devices
        self.uidevice.wakeup()
        self.uidevice(descriptionContains="PIN area").wait.exists(timeout=1000)
        ui_steps.edit_text(serial=self.serial, view_to_find={"descriptionContains": "PIN area"},
                           is_password=True, value=self.pin)()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"descriptionContains": "Enter"})()
        self.uidevice(descriptionContains="Enter").wait.gone()

    def check_condition(self):
        if self.wrong_pin:
            return ui_utils.is_device_pin_locked(serial=self.serial)
        else:
            return not ui_utils.is_device_pin_locked(serial=self.serial)


class unlock_device(ui_step):

    """ description:
            unlocks the screen with swipe and/or PIN


        usage:
            ui_steps.unlock_device()()

        tags:
            ui, android, unlock
    """

    def __init__(self, pin=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.set_passm("Unlock device with swipe and/or PIN")
        self.set_errorm("", "Unlock device with swipe and/or PIN")
        self.pin = pin

    def do(self):
        # Sometimes the screen may be off on some low performance devices
        self.uidevice.wakeup()
        if ui_utils.is_device_locked(serial=self.serial):
            ui_steps.unlock_device_swipe(serial=self.serial)()
        if ui_utils.bxtp_car_locked(serial=self.serial):
            ui_steps.click_button(serial=self.serial, view_to_find={
                "resourceId": "com.android.systemui:id/user_name"})()
        if self.pin and ui_utils.is_device_pin_locked(serial=self.serial):
            ui_steps.unlock_device_pin(serial=self.serial, pin=self.pin)()

    def check_condition(self):
        return not ui_utils.is_device_locked(serial=self.serial)


class perform_startup_wizard(ui_step):

    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """

    def __init__(self, wait_time=2000, **kwargs):
        self.wait_time = wait_time
        ui_step.__init__(self, **kwargs)

    def do(self):
        print "[ {0} ]: Set startup wizard language to United States if necessary".format(self.serial)
        if not self.uidevice(textContains=self.device_info.predefined_language_text_id)\
                .wait.exists(timeout=self.wait_time):
            if self.uidevice(resourceId="android:id/numberpicker_input").wait.exists(timeout=self.wait_time):
                view_to_scroll = {
                    "resourceId": "android:id/numberpicker_input"}
            else:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"resourceId":
                                                    "com.google.android.setupwizard:id/language_picker"})()
                view_to_scroll = {
                    "resourceId": "android:id/select_dialog_listview"}
            if not self.uidevice(textContains=self.device_info.predefined_language_text_id)\
                    .wait.exists(timeout=self.wait_time):
                ui_steps.scroll_to_text_from_scrollable(text_to_find=self.device_info.predefined_language_text_id,
                                                        serial=self.serial, view_to_scroll=view_to_scroll,
                                                        iterations=200,
                                                        direction="down", critical=False, blocking=False)()
                ui_steps.scroll_to_text_from_scrollable(text_to_find=self.device_info.predefined_language_text_id,
                                                        serial=self.serial, view_to_scroll=view_to_scroll,
                                                        iterations=200, direction="up")()
            else:
                ui_steps.click_button(
                    serial=self.serial, view_to_find={"textContains": "United State"})()
        if self.device_info.dessert == "M":
            ui_steps.click_button(
                serial=self.serial, view_to_find={"textContains": "United State"})()

        print "[ {0} ]: Start performing startup wizard".format(self.serial)
        ui_steps.click_button(serial=self.serial, view_to_find={"resourceId":
                                                                "com.google.android.setupwizard:id/start"},
                              view_to_check={"descriptionContains": "Back"})()
        print "[ {0} ]: Set up as new".format(self.serial)
        if self.uidevice(text="Set up as new").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Set up as new"}, wait_time=self.wait_time,
                                  view_to_check={"text": "Get connected"})()
        print "[ {0} ]: Skip or configure SIM settings if necessary".format(self.serial)
        if self.uidevice(textContains="SIM").wait.exists(timeout=self.wait_time):
            if self.uidevice(textContains="Skip").wait.exists(timeout=self.wait_time):
                ui_steps.click_button(serial=self.serial, view_to_find={"text": "Skip"}, wait_time=self.wait_time,
                                      view_to_check={"textContains": "network"})()
            elif self.uidevice(textContains=self.device_info.next_btn_id).wait.exists(timeout=self.wait_time):
                print "[ {0} ]: Selecting a SIM for cellular data".format(self.serial)
                ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                      wait_time=self.wait_time, view_to_check={"textContains": "a SIM for calls"})()
                print "[ {0} ]: Selecting a SIM for calls".format(self.serial)
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "className": "android.widget.RadioButton", "instance": 1},
                                      wait_time=self.wait_time, view_to_check={"textContains": "a SIM for calls"})()
                ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                      wait_time=self.wait_time, view_to_check={"textContains": "a SIM for text "
                                                                                               "messages"})()
                print "[ {0} ]: Selecting a SIM for text messages".format(self.serial)
                ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                      wait_time=self.wait_time, view_to_check={"textContains": "network"})()

        print "[ {0} ]: Skip network settings".format(self.serial)
        ui_steps.click_button(serial=self.serial, view_to_find=self.device_info.skip_wifi_btn_id,
                              view_to_check=self.device_info.wifi_skip_anyway_btn_id)()
        ui_steps.click_button(
            serial=self.serial, view_to_find=self.device_info.wifi_skip_anyway_btn_id)()
        print "[ {0} ]: Wait for connection and update checking if necessary".format(self.serial)
        if self.uidevice(textContains="Checking connection").wait.exists(timeout=self.wait_time):
            timeout = 2 * self.wait_time * 60
            wait_time = 0
            while not self.uidevice(descriptionContains="Add your account")\
                    .wait.exists(timeout=1000) and wait_time < timeout:
                wait_time += self.wait_time
                time.sleep(self.wait_time / 1000)
                ui_steps.wake_up_device(serial=self.serial)()
                if self.uidevice(textContains="Got another device").wait.exists(timeout=self.wait_time):
                    print "[ {0} ]: Skip copying stuff from another device".format(self.serial)
                    ui_steps.click_button(serial=self.serial, view_to_find={"text": "No thanks"},
                                          view_to_check={"text": self.device_info.next_btn_id})()
                    ui_steps.click_button(
                        serial=self.serial, view_to_find={"text": self.device_info.next_btn_id})()
            print "[ {0} ]: Checking connection page disappeared in {1} seconds"\
                .format(self.serial, int(wait_time / 1000))
            if self.uidevice(descriptionContains="Add your account").wait.exists(timeout=1000):
                print "[ {0} ]: Add your account page appeared".format(self.serial)
                wait_time = 0
                while not self.uidevice(descriptionContains="Or create a new account")\
                        .wait.exists(timeout=1000) and wait_time < timeout:
                    wait_time += self.wait_time
                    time.sleep(self.wait_time / 1000)
                    ui_steps.wake_up_device(serial=self.serial)()
                if wait_time < timeout:
                    print "[ {0} ]: 'Or create a new account' option appeared in {1} seconds"\
                        .format(self.serial, int(wait_time / 1000))
                    wait_time = 0
                    while not self.uidevice(resourceId="skip").wait.exists(timeout=1000) and wait_time < timeout:
                        wait_time += self.wait_time
                        time.sleep(self.wait_time / 1000)
                        ui_steps.wake_up_device(serial=self.serial)()
                    if wait_time < timeout:
                        print "[ {0} ]: Skip option appeared in {1} seconds".format(self.serial, int(wait_time / 1000))
                        ui_steps.click_button(serial=self.serial, view_to_find={"resourceId": "skip"},
                                              view_to_check={"descriptionContains": "Skip account setup"})()

                        self.uidevice.press(61)
                        self.uidevice.press("enter")
                        self.uidevice(descriptionContains="Skip account setup").wait.gone(
                            timeout=self.wait_time)
                    else:
                        print "[ {0} ]: Skip option did not appear before the timeout of {1} seconds"\
                            .format(self.serial, int(timeout))
                else:
                    print "[ {0} ]: 'Or create a new account' option did not appear before the timeout of {1} " \
                          "seconds".format(self.serial, int(timeout))
        print "[ {0} ]: Skip Google Services".format(self.serial)
        if self.uidevice(textContains="Google services").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"resourceId":
                                                                    "com.google.android.gms:id/suw_navbar_more"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
            ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                  view_to_check={"textContains": "Date"})()

        print "[ {0} ]: Accept Date page if necessary".format(self.serial)
        if self.uidevice(textContains="Date").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                  view_to_check={"text": "Name"})()
        print "[ {0} ]: Accept Name page".format(self.serial)
        ui_steps.click_button(
            serial=self.serial, view_to_find={"text": self.device_info.next_btn_id})()
        print "[ {0} ]: Skip email setup".format(self.serial)
        if self.uidevice(textContains="Set up email").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Not now"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
            ui_steps.click_button(
                serial=self.serial, view_to_find={"text": self.device_info.next_btn_id})()
        print "[ {0} ]: Skip PIN settings if necessary".format(self.serial)
        if self.uidevice(resourceId="com.google.android.setupwizard:id/lock_screen_intro_check_box")\
                .wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "resourceId": "com.google.android.setupwizard:id/lock_screen_intro_check_box"},
                                  view_to_check=self.device_info.skip_pin_btn_id)()
        ui_steps.click_button(serial=self.serial, view_to_find=self.device_info.skip_pin_btn_id,
                              view_to_check=self.device_info.skip_anyway_btn_id)()
        ui_steps.click_button(
            serial=self.serial, view_to_find=self.device_info.skip_anyway_btn_id)()
        print "[ {0} ]: Collapse Google services page if necessary".format(self.serial)
        if self.uidevice(text="More").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "More"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
        if self.uidevice(description="More").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"description": "More"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
        print "[ {0} ]: Finish setup wizard".format(self.serial)
        ui_steps.click_button(
            serial=self.serial, view_to_find=self.device_info.finish_startup_btn_id)()
        print "[ {0} ]: Setup wizard performed".format(self.serial)

    def check_condition(self):
        return ui_utils.is_homescreen(serial=self.serial)


class perform_startup_wizard_for_new_user(ui_step):

    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """

    def __init__(self, user_name, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.user_name = user_name

    def do(self):
        if self.device_info.dessert == "M":
            if ui_utils.is_view_displayed(serial=self.serial, view_to_find={"description": "More"}):
                ui_steps.click_button(serial=self.serial, view_to_find={"description": "More"},
                                      view_to_check={"text": self.device_info.next_btn_id})()
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Continue"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
            ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                  view_to_check={"textContains": "network"})()

        elif self.device_info.dessert == "L":
            ui_steps.click_button(serial=self.serial, view_to_find={"resourceId":
                                                                    "com.google.android.setupwizard:id/start"},
                                  view_to_check={"text": "Skip"})()
        if self.uidevice(textContains="SIM").wait.exists(timeout=1000):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Skip"}, wait_time=10000,
                                  view_to_check={"textContains": "network"})()
        ui_steps.click_button(serial=self.serial, view_to_find={
            "text": "Skip"}, view_to_check={"text": "Skip anyway"})()

        ui_steps.click_button(serial=self.serial, view_to_find={
            "text": "Skip anyway"}, view_to_check={"text": "Name"})()

        ui_steps.edit_text(serial=self.serial, view_to_find={
            "className": "android.widget.EditText"}, value=self.user_name)()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"text": self.device_info.next_btn_id})()
        if ui_utils.is_view_displayed(serial=self.serial, view_to_find={"text": "More"}):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "More"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
        if ui_utils.is_view_displayed(serial=self.serial, view_to_find={"description": "More"}):
            ui_steps.click_button(serial=self.serial, view_to_find={"description": "More"},
                                  view_to_check={"text": self.device_info.next_btn_id})()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"text": self.device_info.next_btn_id})()
        time.sleep(2)
        if ui_utils.is_view_displayed(serial=self.serial, view_to_find={"text": "GOT IT"}):
            ui_steps.click_button(
                serial=self.serial,
                view_to_find={
                    "text": "GOT IT"})()

    def check_condition(self):
        return True


class set_orientation(ui_step):

    """ description:
            sets the orientation of the device
            available options:
                - phones: portrait, reverse-portrait and landscape
                - tablets: portrait, reverse-landscape and landscape
        usage:
            ui_steps.set_orientation(orientation = "landscape",
                                     target = "phone")()

        tags:
            ui, android, orientation, display
    """

    __orientation = {}
    __orientation["tablet"] = {}
    __orientation["phone"] = {}
    __orientation["tablet"]["landscape"] = "right"
    __orientation["tablet"]["portrait"] = "natural"
    __orientation["tablet"]["reverse-portrait"] = "left"
    # upsidedown cannot be set
    # _orientation["tablet"]["reverse-landscape"] = "upsidedown"
    __orientation["phone"]["landscape"] = "left"
    __orientation["phone"]["portrait"] = "natural"
    __orientation["phone"]["reverse-landscape"] = "right"
    # upsidedown cannot be set
    # _orientation["phone"]["reverse-landscape"] = "upsidedown"

    def __init__(self, orientation="landscape", target="tablet", **kwargs):
        ui_step.__init__(self, **kwargs)
        self.orientation = orientation
        self.target = target
        self.set_passm("Setting orientation to {0}".format(self.orientation))
        self.set_errorm("", "Setting orientation to ".format(self.orientation))

    def do(self):
        self.uidevice.orientation = self.__orientation[
            self.target][self.orientation]
        time.sleep(1)

    def check_condition(self):
        return self.uidevice.orientation == self.__orientation[
            self.target][self.orientation]


class close_app_from_recent(ui_step):

    """ description:
        Close application from recent apps.
        If you have multiple applications opened this step will scroll
        through recent apps until it find the view or the list is over.

        usage:
            ui_steps.close_app_from_recent(view_to_find=
            {"text": "YouTube"})()

        tags:
            ui, android, scroll,recent apps,close app, close
    """

    def __init__(self, view_to_find, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find

    def do(self):
        ui_steps.press_home(serial=self.serial)()
        ui_steps.press_recent_apps(serial=self.serial)()
        if ui_utils.swipe_to_app_from_recent(serial=self.serial, view_to_find=self.view_to_find):
            self.uidevice(**self.view_to_find).swipe.right()

    def check_condition(self):
        return not ui_utils.swipe_to_app_from_recent(
            serial=self.serial, view_to_find=self.view_to_find)


class open_widget_section(ui_step):

    """ description:
            opens the widget section on L dessert

        usage:
            open_widget_section()()

        tags:
            android, L, ui, widget, homescreen
    """

    def do(self):
        ui_steps.press_home(serial=self.serial)()
        page_indicator = self.uidevice(
            resourceId="com.google.android.googlequicksearchbox:id/page_indicator")
        x = (page_indicator.info["bounds"]["left"] +
             page_indicator.info["bounds"]["right"]) / 2
        y = (page_indicator.info["bounds"]["top"] +
             page_indicator.info["bounds"]["bottom"]) / 2
        ui_steps.swipe(serial=self.serial, sx=x, sy=y, ex=x, ey=y, steps=100)()
        ui_steps.click_button(view_to_find={"text": "Widgets"})()

    def check_condition(self):
        return self.uidevice(text="Analog clock").wait.exists(timeout=1000)


class add_widget_to_homescreen(ui_step):

    """ description:
            adds a widget to the homescreen. Homescreen should be empty

        usage:
            add_widget_to_homescreen(widget_name = "Sound search")()

        tags:
            android, ui, widget, homescreen
    """

    def __init__(self, widget_name, displayed_name, **kwargs):
        self.widget_name = widget_name
        self.displayed_name = displayed_name
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_widget_section(serial=self.serial)()
        if ui_utils.is_text_visible_scroll_left(serial=self.serial, text_to_find=self.widget_name):
            widget = self.uidevice(text=self.widget_name)
            x = (widget.info["bounds"]["left"] +
                 widget.info["bounds"]["right"]) / 2
            y = (widget.info["bounds"]["top"] +
                 widget.info["bounds"]["bottom"]) / 2
            ui_steps.swipe(
                serial=self.serial,
                sx=x,
                sy=y,
                ex=x,
                ey=y,
                steps=100)()
            self.step_data = True
        else:
            self.step_data = False

    def check_condition(self):
        self.uidevice.wait.update()
        return self.step_data and self.uidevice(
            textContains=self.displayed_name).wait.exists(timeout=1000)


class open_add_google_account_wizard(ui_step):

    """ description:
            opens add google account wizard from Settings

        usage:
            ui_steps.open_add_google_account_wizard()()

        tags:
            ui, android, google, account
    """

    def do(self):
        ui_steps.open_settings(serial=self.serial)()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Accounts"},
                              view_to_check={"text": "Add account"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Add account"},
                              view_to_check={"text": "Google"})()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Google"},
                              view_to_check={"descriptionContains": "Enter your email"})()


class open_google_account_for_edit(ui_step):

    """ description:
            opens google accounts for editing

        usage:
            ui_steps.open_google_account_for_edit(serial = serial)()

        tags:
            ui, android, google, account
    """

    def do(self):
        ui_steps.open_settings(serial=self.serial)()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Accounts"},
                              view_to_check={"text": "Google"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Google"},
                              view_to_check={"resourceId": "android:id/title", "text": "Accounts"})()


class remove_google_account(ui_step):

    """ description:
            removes gmail account given its name

        usage:
            ui_steps.remove_google_account(account = "intelchat002@gmail.com")()

        tags:
            ui, android, google, account
    """

    def __init__(self, account="intelchat002@gmail.com", **kwargs):
        self.account = account
        ui_step.__init__(self, **kwargs)

    def do(self):
        self.acc_no = gms_utils.get_google_account_number(serial=self.serial)
        ui_steps.open_settings(serial=self.serial)()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Accounts"},
                              view_to_check={"text": "Add account"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Google"},
                              view_to_check={"text": "Google"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"textContains": self.account},
                              view_to_check={"text": "Sync"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"description": "More options"},
                              view_to_check={"text": "Remove account"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Remove account"},
                              view_to_check={"textContains": "Removing this account"})()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Remove account"},
                              view_to_check={"text": "Accounts"})()

    def check_condition(self):
        acc_no = gms_utils.get_google_account_number(serial=self.serial)
        ui_steps.close_app_from_recent(
            serial=self.serial, view_to_find={"text": "Settings"})()
        return acc_no == (self.acc_no - 1)


class remove_all_google_accounts(ui_step):

    """ description:
            removes all gmail accounts

        usage:
            ui_steps.remove_google_account()()

        tags:
            ui, android, google, account
    """

    def do(self):
        while gms_utils.get_google_account_number(serial=self.serial) > 0:
            ui_steps.remove_google_account(
                serial=self.serial,
                account="gmail.com")()


class show_as_list(ui_step):

    """ description:
            Show as list when grid or list is available in More options

        usage:
            ui_steps.show_as_list(serial = serial)()

        tags:
            ui, android, list, grid, open
    """

    def do(self):
        ui_steps.click_button(serial=self.serial, view_to_find={"description": "More options"},
                              view_to_check={"textContains": "view"})()
        self.uidevice.wait.idle()
        if not ui_steps.click_button(serial=self.serial, view_to_find={"text": "List view"}, optional=True)():
            self.uidevice.press.back()


class close_all_app_from_recent(ui_step):

    """ description:
            close all application from recent apps

        usage:
            ui_steps.close_all_app_from_recent()()

        tags:
            ui, android, recent, close app,
    """

    def __init__(self, **kwargs):
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.press_home(serial=self.serial)()
        ui_steps.press_recent_apps(serial=self.serial)()

        self.uidevice(
            resourceId="com.android.systemui:id/task_view_content").wait.exists(timeout=20000)
        while(self.uidevice(resourceId="com.android.systemui:id/task_view_content").count > 0):
            self.uidevice(
                resourceId="com.android.systemui:id/task_view_content").swipe.right()

    def check_condition(self):
        ui_steps.press_home(serial=self.serial)()
        ui_steps.press_recent_apps(serial=self.serial)()
        exist_stat = self.uidevice(
            text="Your recent screens appear here").wait.exists(timeout=1000)
        ui_steps.press_home(serial=self.serial)()
        return exist_stat


class set_timezone_from_settings(ui_step):

    """ description:
            Configures system timezone to a specified value.

        usage:
            ui_steps.set_timezone_from_settings(serial = serial,
                                                timezone = "London")()

        tags:
            ui, android, timezone
    """

    def __init__(self, timezone="London", **kwargs):
        self.timezone = timezone
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_settings(serial=self.serial)()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Date & time"},
                              view_to_check={"text": "Select time zone"})()

        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Select time zone"},
                              view_to_check={"description": "Navigate up"})()
        if not self.uidevice(text=self.timezone).wait.exists(timeout=1000):
            ui_steps.scroll_up_to_view(serial=self.serial, view_to_check={
                "text": self.timezone}, ey=100, critical=False)()
        if not self.uidevice(text=self.timezone).wait.exists(timeout=1000):
            ui_steps.scroll_up_to_view(serial=self.serial, view_to_check={
                "text": self.timezone}, ey=500, iterations=20)()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": self.timezone},
                              view_to_check={"text": "Select time zone"})()

    def check_condition(self):
        return self.uidevice(text="Select time zone").wait.exists(timeout=1000)


class sync_google_account(ui_step):

    """ description:
            Attempts to sync an existing google account.
            Returns True on success, False on failure.
            Sync is attempted <max_attempts> times

        usage:
            ui_steps.sync_google_account(serial = serial,
                                        account = "account@gmail.com",
                                        password = "password",
                                        max_attempts = 42)()

        tags:
            ui, android, timezone
    """

    def __init__(self,
                 account="intelchat002@gmail.com",
                 password="intel002",
                 max_attempts=2,
                 **kwargs):
        self.account = account
        self.password = password
        self.max_attempts = max_attempts
        ui_step.__init__(self, **kwargs)

    def do(self):
        try:
            while self.step_data is not True and self.max_attempts > 0:
                ui_steps.open_google_account_for_edit(serial=self.serial)()
                ui_steps.click_button(serial=self.serial, view_to_find={"text": self.account},
                                      view_to_check={"resourceId": "com.android.settings:id/user_id",
                                                     "text": self.account})()
                ui_steps.click_button(serial=self.serial, view_to_find={"description": "More options"},
                                      view_to_check={"text": "Sync now"})()
                ui_steps.click_button(serial=self.serial, view_to_find={"text": "Sync now"},
                                      view_to_check={"description": "More options"})()
                ui_steps.click_button(serial=self.serial, view_to_find={"description": "More options"},
                                      view_to_check={"text": "Remove account"})()
                if self.uidevice(text="Sync now").wait.exists(timeout=60000):
                    self.uidevice.press.back()
                    if self.uidevice(textContains="experiencing problems").wait.exists(timeout=1000):
                        self.step_data = False
                        ui_steps.handle_google_action_required(serial=self.serial, account=self.account,
                                                               password=self.password)()
                    else:
                        self.step_data = True
                else:
                    self.step_data = False
                self.max_attempts = self.max_attempts - 1
        except Exception:
            self.logger.error(traceback.format_exc())
            self.step_data = False
            pass

    def check_condition(self):
        # TODO: proper check_condition after implementing non-inheritable
        # failures
        return True


class handle_google_action_required(ui_step):

    """ description:
            If "Action required" message is displayed, reenter password.

        usage:
            ui_steps.handle_google_action_required(serial = serial,
                                        account = "account@gmail.com",
                                        password = "password")()

        tags:
            ui, android, google account
    """

    def __init__(self,
                 account="intelchat002@gmail.com",
                 password="intel002",
                 **kwargs):
        self.account = account
        self.password = password
        ui_step.__init__(self, **kwargs)

    def do(self):
        try:
            ui_steps.open_quick_settings(serial=self.serial)()
            if self.uidevice(text="Account Action Required").wait.exists(timeout=20000):
                ui_steps.click_button(serial=self.serial, view_to_find={"text": "Account Action Required"},
                                      view_to_check={"text": "Try again"})()
                ui_steps.click_button(serial=self.serial, view_to_find={"text": "Try again"},
                                      view_to_check={"text": "Re-type password"})()
                ui_steps.edit_text(serial=self.serial, view_to_find={"className": "android.widget.EditText"},
                                   value=self.password, is_password=True)()
                ui_steps.click_button(serial=self.serial, view_to_find={"text": self.device_info.next_btn_id},
                                      view_to_check={"textContains": "Checking info"})()
                self.uidevice(textContains="Checking info").wait.gone(
                    timeout=60000)
                ui_steps.open_quick_settings(serial=self.serial)()
                if self.uidevice(text="Account Action Required").wait.exists(timeout=20000):
                    self.step_data = False
                else:
                    self.step_data = True
                self.uidevice.press.back()
            else:
                self.step_data = True
        except Exception:
            self.logger.error(traceback.format_exc())
            self.step_data = False
            pass

    def check_condition(self):
        # TODO: proper check_condition after implementing non-inheritable
        # failures
        return True


class set_orientation_vertical(ui_step):

    """ description:
        Sets the device orientation to the 'portrait' or 'landscape' as defined
        for devices of type phone.

    usage:
        ui_steps.set_orientation_vertical(serial = serial, orientation='portrait')()

    tags:
        ui, android, click, button
    """
    __orientation = {}
    __orientation["tablet"] = {}
    __orientation["phone"] = {}
    __orientation["tablet"]["landscape"] = "right"
    __orientation["tablet"]["portrait"] = "natural"
    __orientation["tablet"]["reverse-portrait"] = "left"
    __orientation["phone"]["landscape"] = "left"
    __orientation["phone"]["portrait"] = "natural"
    __orientation["phone"]["reverse-landscape"] = "right"

    def __init__(self, orientation="portrait", **kwargs):
        ui_step.__init__(self, **kwargs)
        self.orientation = orientation

    def do(self):
        # set the orientation to 'natural'
        ui_steps.set_orientation(
            serial=self.serial, orientation="portrait", target="phone")()
        # set the orientation to 'portrait'
        self.device_type = adb_utils.get_device_orientation_type(
            serial=self.serial)
        ui_steps.set_orientation(
            serial=self.serial, orientation=self.orientation, target=self.device_type)()

    def check_condition(self):
        return self.uidevice.orientation == self.__orientation[
            self.device_type][self.orientation]


class block_device(ui_step):

    """ description:
            unlocks DUT with wrong PIN 5 times in a row

        usage:
            ui_steps.block_device(pin = "2222")()

        tags:
            ui, android, PIN
    """

    def __init__(self, pin="2222", **kwargs):
        self.pin = pin
        ui_step.__init__(self, **kwargs)

    def do(self):
        # enter wrong pin 5 times
        ui_steps.put_device_into_sleep_mode(serial=self.serial)()
        time.sleep(2)
        ui_steps.wake_up_device(serial=self.serial)()
        ui_steps.unlock_device_swipe(serial=self.serial)()
        for i in range(0, 5):
            ui_steps.unlock_device_pin(
                serial=self.serial, pin=self.pin, wrong_pin=True)()

    def check_condition(self):
        return "You have incorrectly typed your PIN 5 times." in \
               self.uidevice(resourceId="android:id/message").info["text"]


class block_device_at_boot_time(ui_step):

    """ description:
            enters wrong PIN 10 times in a row at boot time

        usage:
            ui_steps.block_device_at_boot_time()()

        tags:
            ui, android, PIN
    """

    def __init__(self, pin="2222", **kwargs):
        self.pin = pin
        ui_step.__init__(self, **kwargs)

    def do(self):
        for i in range(0, 10):
            ui_steps.wait_for_view(serial=self.serial,
                                   view_to_find={"resourceId": "com.android.settings:id/passwordEntry", "enabled":
                                                 "true"})()
            ui_steps.edit_text(serial=self.serial, view_to_find={"resourceId":
                                                                 "com.android.settings:id/passwordEntry"},
                               is_password=True, value=self.pin)()
            # press enter keycode
            self.uidevice.press("enter")

    def check_condition(self):
        return self.uidevice(
            textContains="To unlock your tablet").wait.exists(timeout=5000)


class create_new_user(ui_step):

    """ description:
            Creates new user

        usage:
            ui_steps.create(user_name = "USER"()()

        tags:
            ui, android, create, user
    """

    def __init__(self, user_name=None, set_up_user=False, **kwargs):
        self.user_name = user_name
        self.set_up_user = set_up_user
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_users_settings(serial=self.serial)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Add user or profile"},
                              view_to_check={"textContains": "Users have their own"})()
        ui_steps.click_button(serial=self.serial, view_to_find={"textContains": "Users have their own"},
                              view_to_check={"textContains": "Add new user?"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "OK"},
                              view_to_check={"textContains": "Set up user now?"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Not now"},
                              view_to_check={"textContains": "Not set up"})()
        if self.set_up_user:
            ui_steps.set_up_user(serial=self.serial,
                                 user_name=self.user_name)()

    def check_condition(self):
        if not self.set_up_user:
            ui_steps.wait_for_view(serial=self.serial,
                                   view_to_find={"text": "New user"})()
        return True


class remove_user(ui_step):

    """ description:
            Deletes new user

        usage:
            ui_steps.remove_user(user_name = "USER"()()

        tags:
            ui, android, delete, user
    """

    def __init__(self, user_name, check_condition=True, **kwargs):
        self.user_name = user_name
        ui_step.__init__(self, **kwargs)
        self.perform_check_condition = check_condition
        self.optional = False
        self.step_data = False

    def do(self):
        ui_steps.open_users_settings(serial=self.serial)()
        if not ui_steps.wait_for_view_common(serial=self.serial,
                                             view_to_find={"text": self.user_name}, optional=True)():
            return
        if not ui_steps.click_button_common(serial=self.serial, view_to_find={"text": self.user_name},
                                            second_view_to_find={
                                                "descriptionContains": "Delete user"},
                                            view_to_check={"textContains": "Remove this user?"}, optional=True)():
            ui_steps.click_button_common(serial=self.serial,
                                         view_to_find={"descriptionContains": "more"})()
            ui_steps.click_button_common(serial=self.serial,
                                         view_to_find={"textContains": "Delete"})()

        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "DELETE"})()
        self.step_data = True

    def check_condition(self):
        if self.optional and not self.step_data:
            return self.step_data

        if self.step_data and self.perform_check_condition:
            return not ui_steps.wait_for_view_common(serial=self.serial,
                                                     view_to_find={"text": self.user_name}, optional=True)()
        else:
            return


class set_up_user(ui_step):

    """ description:
            Deletes new user

        usage:
            ui_steps.set_up_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """

    def __init__(self, user_name, **kwargs):
        self.user_name = user_name
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_users_settings(serial=self.serial)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Not set up"},
                              view_to_check={"textContains": "Set up user now?"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Set up now"})()
        time.sleep(10)
        ui_steps.wake_up_device(serial=self.serial)()
        ui_steps.unlock_device(serial=self.serial)()
        ui_steps.perform_startup_wizard_for_new_user(
            serial=self.serial, user_name="New user")()

    def check_condition(self):
        return True


class switch_user(ui_step):

    """ description:
            Deletes new user

        usage:
            ui_steps.switch_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """

    def __init__(self, user_name, **kwargs):
        self.user_name = user_name
        ui_step.__init__(self, **kwargs)

    def do(self):
        ui_steps.open_users_settings(serial=self.serial)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": self.user_name})()
        time.sleep(10)
        ui_steps.put_device_into_sleep_mode(serial=self.serial)()
        ui_steps.wake_up_device(serial=self.serial)()
        ui_steps.unlock_device(serial=self.serial)()

    def check_condition(self):
        # Check if user switched
        ui_steps.open_users_settings(serial=self.serial)()
        ui_steps.wait_for_view(serial=self.serial,
                               view_to_find={"text": "You (" + self.user_name + ")"})()
        return True


class add_trusted_location(ui_step):

    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """

    def __init__(self, location_name, pin, wait_time=30000, **kwargs):
        self.location_name = location_name
        self.pin = pin
        ui_step.__init__(self, **kwargs)
        self.wait_time = wait_time

    def do(self):
        ui_steps.open_smart_lock_settings(serial=self.serial, pin=self.pin)()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Trusted places"},
                              view_to_check={"text": "Add trusted place"})()
        ui_steps.click_button(
            serial=self.serial, view_to_find={"text": "Add trusted place"})()
        if self.uidevice(text="Use location?").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(
                serial=self.serial,
                view_to_find={
                    "text": "Yes"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"resourceId":
                                            "com.google.android.gms:id/marker_map_my_location_button"})()
        if self.uidevice(text="Select this location").wait.exists(timeout=self.wait_time):
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Select this location"},
                                  view_to_check={"resourceId": "com.google.android.gms:id/trusted_place_name"})()
        ui_steps.edit_text(serial=self.serial, view_to_find={"resourceId":
                                                             "com.google.android.gms:id/trusted_place_name"},
                           value=self.location_name)()
        ui_steps.click_button(
            serial=self.serial,
            view_to_find={
                "text": "OK"})()

    def check_condition(self):
        # Check if user switched
        ui_steps.open_smart_lock_settings(serial=self.serial, pin=self.pin)()
        return self.uidevice(text=self.location_name).wait.exists(
            timeout=self.wait_time)


class remove_trusted_location(ui_step):

    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """

    def __init__(self, location_name, pin, wait_time=5000, **kwargs):
        self.location_name = location_name
        self.pin = pin
        ui_step.__init__(self, **kwargs)
        if wait_time:
            self.wait_time = int(wait_time)
        else:
            self.wait_time = 5000

    def do(self):
        ui_steps.open_smart_lock_settings(serial=self.serial, pin=self.pin)()
        ui_steps.click_button(serial=self.serial, view_to_find={"text": "Trusted places"},
                              view_to_check={"text": "Add trusted place"})()
        if self.device_info.dessert == "M":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": self.location_name},
                                  view_to_check={"resourceId": "com.google.android.gms:id/trusted_places_"
                                                 "custom_places_menu_delete_this_location"})()
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"resourceId": "com.google.android.gms:id/trusted_places_custom"
                                                "_places_menu_delete_this_location"},
                                  view_to_check={"text": "Add trusted place"})()
        elif self.device_info.dessert == "L":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": self.location_name},
                                  view_to_check={"text": self.location_name})()
            if ui_utils.is_display_direction_landscape(serial=self.serial):
                ui_steps.click_xy(serial=self.serial, x=self.uidevice.info["displayWidth"] / 2,
                                  y=self.uidevice.info[
                                      "displayHeight"] * self.device_info
                                  .remove_trusted_location_horizontal_percentage)()
            else:
                ui_steps.click_xy(serial=self.serial, x=self.uidevice.info["displayWidth"] / 2,
                                  y=self.uidevice.info[
                                      "displayHeight"] * self.device_info
                                  .remove_trusted_location_vertical_percentage)()

    def check_condition(self):
        # Check if user switched
        ui_steps.open_smart_lock_settings(serial=self.serial, pin=self.pin)()
        return not self.uidevice(text=self.location_name).wait.exists(
            timeout=self.wait_time)


class add_trusted_device(ui_step):

    """ description:
            Adds a trusted device (Smart lock)

        usage:
            ui_steps.add_trusted_device(device_name = <device_name>)()

        tags:
            ui, android, switch, user
    """

    def __init__(self, device_name, pin, wait_time=30000, **kwargs):
        self.device_name = device_name
        self.pin = pin
        ui_step.__init__(self, **kwargs)
        self.wait_time = wait_time

    def do(self):
        ui_steps.open_smart_lock_settings(serial=self.serial,
                                          pin=self.pin)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Trusted devices"},
                              view_to_check={"text": "Add trusted device"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "Add trusted device"},
                              view_to_check={"text": "Choose device"})()
        ui_steps.click_button(serial=self.serial, view_to_find={
            "text": self.device_name}, view_to_check={"text": "YES, ADD"})()
        ui_steps.click_button(serial=self.serial, view_to_find={
            "text": "YES, ADD"}, view_to_check={"text": "Connected"})()

    def check_condition(self):
        # Check if user switched
        ui_steps.open_smart_lock_settings(serial=self.serial, pin=self.pin)()
        return self.uidevice(text=self.device_name).wait.exists(
            timeout=self.wait_time)


class set_date_and_time(ui_step):

    def __init__(
            self, year, day, ntp_switch_state_value, wait_time=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.year = year
        self.day = day
        self.ntp_switch_state_value = ntp_switch_state_value
        self.wait_time = wait_time
        self.step_data = None

    def do(self):
        ui_steps.open_settings_app(serial=self.serial, view_to_find={"text": "Date & time"},
                                   view_to_check={"text": "Automatic date & time"})()

        if self.uidevice(resourceId="android:id/switchWidget", instance=0).info["text"] == "ON":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Automatic date & time"},
                                  view_to_check={"text": "Automatic time zone"})()
        if self.uidevice(resourceId="android:id/switchWidget", instance=1).info["text"] == "ON":
            ui_steps.click_button(serial=self.serial, view_to_find={"text": "Automatic time zone"},
                                  view_to_check={"text": "Set date"})()
        views_to_click = [{"text": "Set date"},
                          {"resourceId": "android:id/date_picker_header_year"},
                          {"text": self.year},
                          {"resourceId": "android:id/prev"},
                          {"text": self.day},
                          {"text": "OK"},
                          {"text": "Set time"},
                          {"index": "11"},
                          {"index": "11"},
                          {"text": "OK"}]
        views_to_check = [{"text": "OK"},
                          {"text": "OK"},
                          {"text": "OK"},
                          {"text": "OK"},
                          {"text": "OK"},
                          {"text": "Set date"},
                          {"text": "OK"},
                          {"text": "OK"},
                          {"text": "OK"},
                          {"text": "Set time"}]
        for i in range(len(views_to_click)):
            ui_steps.click_button(serial=self.serial, view_to_find=views_to_click[
                i], view_to_check=views_to_check[i])()

    def check_condition(self):
        # Check performed in do()
        return True


class enable_disable_auto_time_date(ui_step):

    """ description:
            Enables or disables the auto time and date option in settings

        usage:
            ui_steps.enable_disable_auto_time_date(serial=serial,
                                                   enable=True/False)()

        tags:
            ui, android, enable, disable, time, date
    """

    def __init__(self, serial, enable=True, **kwargs):
        self.serial = serial
        self.enable = enable
        ui_step.__init__(self, serial=self.serial, **kwargs)
        self.set_errorm("", "Could not {0} auto time and date".format(
            "enable" if self.enable else "disable"))
        self.set_passm("Successfully {0} auto time and date".format(
            "enabled" if self.enable else "disabled"))

    def do(self):
        # Open the app and go to date and time
        ui_steps.open_settings_app(serial=self.serial,
                                   view_to_find={"text": "Date & time"},
                                   view_to_check={
                                       "text": "Automatic date & time"},
                                   wait_time=3000)()
        # Define the checkbox used for the step
        self.auto_time_checkbox = self.uidevice(className="android.widget.ListView", resourceId="android:id/list").\
            child_by_text("Automatic date & time", className="android.widget.LinearLayout").\
            child(className="android.widget.Switch")

        # If the option should be enabled and it isn't, click to enable
        # If the option is enabled and the parameter is set to false, click to
        # disable
        if self.enable and not self.auto_time_checkbox.info["checked"]:
            self.auto_time_checkbox.click()
        elif not self.enable and self.auto_time_checkbox.info["checked"]:
            self.auto_time_checkbox.click()

    def check_condition(self):
        # If the option should be enabled and it isn't, return false (step
        # fails)
        if self.enable and not self.auto_time_checkbox.info["checked"]:
            return False
        # If the option should not be enabled and it is, fail the step
        if not self.enable and self.auto_time_checkbox.info["checked"]:
            return False
        return True


class enable_disable_auto_timezone(ui_step):

    """ description:
            Enables or disables the timezone switch button from Date & time settings

        usage:
            ui_steps.set_automatic_timezone(serial=serial,
                                            time_zone_switch_value=True for "ON"/ False for "OFF")()

        tags:
            ui, android, enable, disable, timezone
    """

    def __init__(self, time_zone_switch_value, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.time_zone_switch_value = time_zone_switch_value
        self.set_errorm("", "Could not {0} auto timezone".
                        format("enable" if self.time_zone_switch_value else "disable"))
        self.set_passm("Successfully {0} auto timezone"
                       .format("enabled" if self.time_zone_switch_value else "disabled"))

    def do(self):

        # Define the checkbox used for the step
        self.auto_timezone_checkbox = self.uidevice(className="android.widget.ListView", resourceId="android:id/list")\
            .child_by_text("Automatic time zone", className="android.widget.LinearLayout")\
            .child(className="android.widget.Switch")

        # If the option should be enabled and it isn't, click to enable
        # If the option is enabled and the parameter is set to false, click to
        # disable
        if self.time_zone_switch_value and not self.auto_timezone_checkbox.info["checked"]:
            self.auto_timezone_checkbox.click()
        elif not self.time_zone_switch_value and self.auto_timezone_checkbox.info["checked"]:
            self.auto_timezone_checkbox.click()

    def check_condition(self):
        # If the option should be enabled and it isn't, return false (step
        # fails)
        if self.time_zone_switch_value and not self.auto_timezone_checkbox.info["checked"]:
            return False
        # If the option should not be enabled and it is, fail the step
        if not self.time_zone_switch_value and self.auto_timezone_checkbox.info["checked"]:
            return False
        return True


class press_map(ui_step):

    """ description:
                Open car map application

            usage:
                ui_steps.press_map(serial=serial)()

            tags:
                ui, android, map, ivi
        """

    def check_view(self):
        if self.uidevice(**self.view_to_check).wait.exists(timeout=self.timeout):
            return True
        if self.uidevice(**{"text": "Google Maps", "packageName": "com.google.android.projection.gearhead"})\
                .wait.exists(timeout=self.timeout):
            return True
        return False

    def __init__(self, view_to_check={"resourceId": "com.android.support.car.lenspicker: id/stream_card",
                                      "packageName": "com.android.support.car.lenspicker"}, timeout=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_check = view_to_check
        self.timeout = timeout
        self.set_errorm("", "Could not press car map")
        self.set_passm("Successfully opened car map")
        self.step_data = False

    def do(self):
        if self.device_info.device_type == "tab":
            self.logger.error("Unsupported API, as it only support in "
                              "greater than or equal to Android O IVI "
                              "platform")
        else:
            # Todo need to replace pixel with uiobject
            # currently pixel is used because activity is not dumped through
            # uiautomator
            info = self.uidevice.info
            x = info['displaySizeDpX']
            y = info['displaySizeDpY']

            # In activity bar, 7 options are there.
            activity_bar_single_element_width = x / 7

            # map resides at 2 position and click has to be done at the center
            map_x_coordinate = activity_bar_single_element_width * \
                2 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            map_y_coordinate = y - 30

            for i in range(0, 5):
                # cmd = "input tap 405 1050"
                cmd = "input tap {0} {1}".format(
                    map_x_coordinate, map_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(2)
                if self.check_view():
                    self.step_data = True
                    break

    def check_condition(self):
        return self.step_data


class press_dialer(ui_step):

    """ description:
                Open car dialer application

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
    """

    def __init__(self, timeout=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.timeout = timeout
        self.set_errorm("", "Could not open car dialer")
        self.set_passm("Successfully opened car dialer")
        self.step_data = False

    def do(self):
        if self.device_info.device_type == "tab":
            self.logger.error("Unsupported API, as it only support in greater than or equal to Android O IVI "
                              "platform")
        else:
            # Todo need to replace pixel with uiobject
            # currently pixel is used because activity is not dumped through
            # uiautomator
            info = self.uidevice.info
            x = info['displaySizeDpX']
            y = info['displaySizeDpY']

            # In activity bar, 7 options are there.
            activity_bar_single_element_width = x / 7

            # dialer resides at 3 position and click has to be done at the
            # center
            dialer_x_coordinate = activity_bar_single_element_width * \
                3 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            dialer_y_coordinate = y - 30

            cmd = "input tap {0} {1}".format(
                dialer_x_coordinate, dialer_y_coordinate)
            adb_connection = Adb(serial=self.serial)
            adb_subprocess_object = adb_connection.run_cmd(cmd)
            if adb_subprocess_object.poll() == 0:
                self.step_data = True

    def check_condition(self):
        if self.step_data is True:
            self.step_data = ui_steps.wait_for_view(serial=self.serial,
                                                    view_to_find={
                                                        "text": "Phone", "packageName": "com.android.car.dialer"},
                                                    timeout=self.timeout)()
        return self.step_data


class press_media(ui_step):

    """ description:
                Open car media application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """

    def check_view(self):
        return self.uidevice(**self.view_to_check).wait.exists(
            timeout=self.timeout)

    def __init__(self, view_to_check={"resourceId": "com.android.support.car.lenspicker: id/stream_card",
                                      "packageName": "com.android.support.car.lenspicker"}, timeout=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_check = view_to_check
        self.timeout = timeout
        self.set_errorm("", "Could not open car media")
        self.set_passm("Successfully opened car media")
        self.step_data = False

    def do(self):
        if self.device_info.device_type == "tab":
            self.logger.error("Unsupported API, as it only support in "
                              "greater than or equal to Android O IVI "
                              "platform")
        else:
            # Todo need to replace pixel with uiobject
            # currently pixel is used because activity is not dumped through
            # uiautomator
            info = self.uidevice.info
            x = info['displaySizeDpX']
            y = info['displaySizeDpY']

            # In activity bar, 7 options are there.
            activity_bar_single_element_width = x / 7

            # media resides at 5 position and click has to be done at the
            # center
            media_x_coordinate = activity_bar_single_element_width * \
                5 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            media_y_coordinate = y - 30

            for i in range(0, 5):
                cmd = "input tap {0} {1}".format(
                    media_x_coordinate, media_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(1)
                if self.check_view():
                    self.step_data = True
                    break

    def check_condition(self):
        return self.step_data


class press_car(ui_step):

    """ description:
                Open car application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """

    def check_view(self):
        return self.uidevice(**self.view_to_check).wait.exists(
            timeout=self.timeout)

    def __init__(self, view_to_check={"resourceId": "com.android.support.car.lenspicker:id/stream_card",
                                      "packageName": "com.android.support.car.lenspicker"}, timeout=5000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_check = view_to_check
        self.timeout = timeout
        self.set_errorm("", "Could not open car ")
        self.set_passm("Successfully opened car")
        self.step_data = False

    def do(self):
        if self.device_info.device_type == "tab":
            self.logger.error("Unsupported API, as it only support in "
                              "greater than or equal to Android O IVI "
                              "platform")
        else:
            # Todo need to replace pixel with uiobject
            # currently pixel is used because activity is not dumped through
            # uiautomator
            info = self.uidevice.info
            x = info['displaySizeDpX']
            y = info['displaySizeDpY']

            # In activity bar, 7 options are there.
            activity_bar_single_element_width = x / 7

            # car resides at 7 position and click has to be done at the center
            car_x_coordinate = activity_bar_single_element_width * \
                6 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            car_y_coordinate = y - 30

            for i in range(0, 5):
                cmd = "input tap {0} {1}".format(
                    car_x_coordinate, car_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(1)
                if self.check_view():
                    self.step_data = True
                    break

    def check_condition(self):
        return self.step_data
