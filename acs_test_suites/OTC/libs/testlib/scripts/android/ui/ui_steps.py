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

from testlib.scripts.android.ui.ui_step import step as ui_step
from testlib.scripts.android.ui import ui_utils
from testlib.utils.connections.adb import Adb
from testlib.base.base_step import BlockingError
from testlib.base.abstract.abstract_step import devicedecorator, applicable


class dump(ui_step):

    """ description:
            dumps the ui objects to stdout or a file

        usage:
            ui_steps.dump() - dumps to stdout
            ui.steps.dump("/path/to/out_file.xml") - dumps to fil

        tags:
            ui, android, dump, xml, file
    """

    out_file = None

    def __init__(self, out_file=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.out_file = out_file

    def do(self):
        if self.out_file:
            self.uidevice.dump(out_file=self.out_file,
                               compressed=False, serial=self.serial)
        else:
            print self.uidevice.dump(compressed=False, serial=self.serial)

    def check_condition(self):
        return True


@devicedecorator
class set_pin_screen_lock():

    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """
    pass


@devicedecorator
class remove_pin_screen_lock():

    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """
    pass


@devicedecorator
class open_security_settings():

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """
    pass


@devicedecorator
class open_users_settings():

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """
    pass


@devicedecorator
class am_start_command():

    """ description:
            Opens the WiFi Settings page using an intent.

        usage:
            wifi_steps.open_wifi_settings()()

        tags:
            ui, android, settings, wifi, intent
    """
    pass


@devicedecorator
class am_stop_package():

    """ Description:
            Executes command 'adb shell am force-stop [package_name]'. Pass
            package name to package_name parameter.
        Usage:
            ui_steps.am_stop_package(serial=serial,
                                        package_name="com.android.settings")()
        tags:
            ui, android, stop, package
    """
    pass


class click_view(ui_step):

    """ description:
            clicks a view <view>
                if <view_to_check> given it will check that the object
                identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

        usage:
            ui_steps.click_button(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/button_allow"},
                    view_to_check = {"text": "OK"})()

        tags:
            ui, android, click, button
    """

    def __init__(self, view, view_to_check=None,
                 view_presence=True, wait_time=10000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view = view
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.wait_time = wait_time
        self.set_errorm(
            "", "Could not click view {0} checking {1}".format(view, view_to_check))
        self.set_passm(
            "View {0} clicked checking {1}".format(view, view_to_check))

    def do(self):
        self.view.click.wait()

    def check_condition(self):
        if self.view_to_check is None:
            return True
        if self.view_presence:
            check_state = self.uidevice(
                **self.view_to_check).wait.exists(timeout=self.wait_time)
        else:
            check_state = self.uidevice(
                **self.view_to_check).wait.gone(timeout=self.wait_time)
        return check_state


# TODO: rename with open_quick_settings_with_swipe
# add desciption
@devicedecorator
class open_notifications_menu():
    pass


class click_xy(ui_step):

    """ description:
            clicks on the devices on x, y

        usage:
            ui_steps.click_xy(x = 100, y = 100)()

        tags:
            ui, android, click, coords
    """

    def __init__(self, x, y, view_to_check=None, use_adb=True, **kwargs):
        self.x = x
        self.y = y
        self.view_to_check = view_to_check
        self.use_adb = use_adb
        ui_step.__init__(self, **kwargs)
        self.step_data = False
        self.set_passm("Coordinates ({0} x {1}) clicked".format(x, y))
        self.set_errorm(
            "", "Could not click coordinates ({0} x {1})".format(x, y))

    def do(self):
        if self.use_adb:
            cmd = "input tap {0} {1}".format(self.x, self.y)
            adb_connection = Adb(serial=self.serial)
            output = adb_connection.run_cmd(cmd)
            if output:
                self.step_data = True
        else:
            self.step_data = self.uidevice.click(self.x, self.y)

    def check_condition(self):
        if not self.step_data:
            return self.step_data
        if self.view_to_check is None:
            return True
        self.uidevice.wait.update()
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


class long_click(ui_step):

    """ description:
        long clicks a button identified by <view_to_check>
            if <view_to_check> given it will check that the object
            identified by <view_to_check>:
            - appeared if <view_presence> is True
            - disappeared if <view_presence> is False

        usage:
            ui_steps.long_click(view_to_find = {"resourceId":
                "com.intel.TelemetrySetup:id/button_allow"},
                    view_to_check = {"text": "OK"})()

        tags:
            ui, android, long_click, button
    """
    view_to_find = None
    view_to_check = None
    view_presence = None

    def __init__(self, view_to_find, view_to_check=None,
                 view_presence=True, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.view_presence = view_presence

    def do(self):
        self.uidevice(**self.view_to_find).long_click()

    def check_condition(self):
        if self.view_to_check is None:
            return True
        exists = self.uidevice(**self.view_to_check).wait.exists(timeout=1000)
        return exists if self.view_presence else not exists


class edit_text(ui_step):

    """ description:
            puts value in text view identified by view_to_check

        usage:
            ui_steps.edit_text(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/text"},
                    value = "text to input")()

            scroll - scroll for the desired view and then edit the text.
            clear_text - clear the text before writing 'value'(default is True)

        tags:
            ui, android, edit, text
    """

    view_to_find = None
    value = None
    is_password = None

    def __init__(self, view_to_find, value, is_password=False, scroll=False, clear_text=True, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.value = value
        self.is_password = is_password
        self.scroll = scroll
        self.clear_text = clear_text
        self.set_passm("Edit {0} with {1}".format(view_to_find, value))
        self.set_errorm(
            "", "Could not edit {0} with {1}".format(view_to_find, value))

    def do(self):
        self.uidevice.wait.idle()
        if self.scroll and self.uidevice(className="android.widget.ScrollView",
                                         scrollable=True).wait.exists(timeout=1000):
            self.uidevice(scrollable=True).scroll.to(**self.view_to_find)
        text_field = self.uidevice(**self.view_to_find)
        while self.clear_text and text_field.info['text']:
            before = text_field.info['text']
            text_field.clear_text()
            after = text_field.info['text']
            if before == after:
                break
        # if adb_utils.is_virtual_keyboard_on(serial = self.serial):
        #    press_back(serial = self.serial)()
        if text_field.info["className"] != "com.android.keyguard.PasswordTextView":
            text_field.set_text(self.value)
        else:
            for character in self.value:
                click_button(serial=self.serial,
                             view_to_find={"text": character,
                                           "resourceId": "com.android.systemui:id/digit_text"})()

    def check_condition(self):
        # if adb_utils.is_virtual_keyboard_on(serial = self.serial):
        #    press_back(serial = self.serial)()
        if self.is_password:
            return True
        return (self.uidevice(textContains=self.value).wait.exists(timeout=1000))


class scroll_up_to_view(ui_step):

    """ description:
            scrolls up on until <view_to_check> is shown using swipe
            You can scroll "down" if you overwrite ey to <300.

        usage:
            ui_steps.scroll_up_to_view(view_to_check = "Bluetooth")()

        tags:
            ui, android, swipe, scroll
    """

    def __init__(self, view_to_check, sx=300, sy=300, ex=300, ey=400, iterations=10, **kwargs):
        self.start_x = sx
        self.start_y = sy
        self.end_x = ex
        self.end_y = ey
        self.view_to_check = view_to_check
        self.iterations = iterations
        ui_step.__init__(self, **kwargs)

    def do(self):
        iterations = 0
        while (not self.uidevice(**self.view_to_check).wait.exists(timeout=1000) and
               iterations < self.iterations):
            swipe(serial=self.serial,
                  sx=self.start_x, sy=self.start_y,
                  ex=self.end_x, ey=self.end_y,
                  steps=10)()
            iterations += 1

    def check_condition(self):
        return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)


class swipe(ui_step):

    """ description:
            swipes from (<sx>, <sy>) to (<ex>, <ey>)
                in <steps> steps
                if <view_to_check> given it will check that
                the object identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False after swipe

        usage:
            ui_steps.swipe(sx = 10, sy = 10, ex = 100, ey = 100)

        tags:
            ui, android, swipe
    """

    def __init__(self, sx, sy, ex, ey, steps=100, view_presence=True,
                 exists=True, view_to_check=None, wait_time=None, iterations=1, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_presence = view_presence
        self.wait_time = wait_time
        self.start_x = sx
        self.start_y = sy
        self.end_x = ex
        self.end_y = ey
        self.steps = steps
        self.exists = exists
        self.view_to_check = view_to_check
        self.iterations = iterations

    def do(self):
        iterations = 0
        if self.view_to_check:
            while iterations < self.iterations:
                if not self.uidevice(**self.view_to_check).wait.exists(timeout=1000):
                    self.uidevice.swipe(self.start_x, self.start_y,
                                        self.end_x, self.end_y, self.steps)
                iterations += 1
        else:
            self.uidevice.swipe(self.start_x, self.start_y,
                                self.end_x, self.end_y, self.steps)

    def check_condition(self):
        if self.view_to_check is None:
            return True
        if self.wait_time:
            if self.exists:
                self.uidevice(
                    **self.view_to_check).wait.exists(timeout=self.wait_time)
            else:
                self.uidevice(
                    **self.view_to_check).wait.gone(timeout=self.wait_time)
        exists = self.uidevice(**self.view_to_check).wait.exists(timeout=1000)
        return exists if self.view_presence else not exists


class click_switch(ui_step):

    """ description:
            changes switch state to argument state value
                if already in the desired state do nothing
                else clicks the switch and change switched member to
                True

        usage:
            ui_steps.click_switch(
                view_to_find = {"className": "android.widget.Switch",
                                "instance": "1"},
                state = "ON",
                click_to_close_popup = {"text": "Agree"})()

        tags:
            ui, android, click, switch, enable, disable
    """

    view_to_find = None
    state = None
    switch = None

    def __init__(self, view_to_find, state="ON", click_to_close_popup=None,
                 right_of=False, wait_time=3000, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.state = state
        self.switch = None
        self.step_data = False
        self.click_to_close_popup = click_to_close_popup
        self.right_of = right_of
        self.wait_time = wait_time
        self.set_passm(
            "Set switch {0} to {1}".format(view_to_find, self.state))
        self.set_errorm(
            "", "Could not set switch {0} to {1}".format(view_to_find, self.state))

    def do(self):
        wait_for_view(view_to_find=self.view_to_find,
                      serial=self.serial)()
        if self.right_of:
            self.switch = self.uidevice(**self.view_to_find).right(
                className="android.widget.Switch")
        else:
            self.switch = self.uidevice(**self.view_to_find)
        if self.switch.info['text'] == self.state:
            self.step_data = False
        else:
            self.switch.click.wait()
            self.step_data = True

            if self.click_to_close_popup:
                click_button(serial=self.serial,
                             print_error="Failed to close popup",
                             blocking=True,
                             view_to_find=self.click_to_close_popup)()

    def check_condition(self):
        if self.right_of:
            self.switch = self.uidevice(**self.view_to_find).right(
                className="android.widget.Switch", text=self.state).\
                wait.exists(timeout=self.wait_time)
        else:
            self.view_to_find.update({"text": self.state})
            self.switch = self.uidevice(
                **self.view_to_find).wait.exists(timeout=self.wait_time)
        return self.switch


@devicedecorator
class press_all_apps():

    """ description:
            opens all application activity

        usage:
            ui_steps.press_all_apps()

        tags:
            ui, android, press, click, allapps, applications
    """
    pass


@devicedecorator
class press_home():

    """ description:
            opens home page

        usage:
            ui_steps.press_home()

        tags:
            ui, android, press, click, home, homepage
    """

    pass


@devicedecorator
class press_bell(ui_step):

    """ description:
                Open bell icon (Notification in android P)
            usage:
                ui_steps.press_bell(serial=serial)()
            tags:
                ui, android, press, click, quick setting, bell

    """
    pass


class press_back(ui_step):

    """ description:
            presses the back button. If <view_to_check> is passed it will check
            if that view exists

        usage:
            ui_steps.press_back(view_to_check = {"text": "Bluetooth"})

        tags:
            ui, android, press, back
    """
    view_to_check = None

    def __init__(self, view_to_check=None, times=1, **kwargs):
        ui_step.__init__(self, **kwargs)
        if view_to_check:
            self.view_to_check = view_to_check
        self.times = times
        self.set_passm("Press back {0} time(s)".format(times))
        self.set_errorm("", "Could not press back {0} time(s)".format(times))

    def do(self):
        for i in range(self.times):
            self.uidevice.press.back()
            self.uidevice.wait.idle()

    def check_condition(self):
        if self.view_to_check:
            return self.uidevice(**self.view_to_check).wait.exists(timeout=1000)
        return True


@devicedecorator
class press_recent_apps():

    """ description:
            opens recent apps

        usage:
            ui_steps.press_recent_apps()

        tags:
            ui, android, press, click, recent apps, homepage
    """
    pass


@devicedecorator
class app_in_recent_apps():

    """ description:
            opens recent apps and checks if <app_name> app is present

        usage:
            ui_steps.app_in_recent_apps(app_name = "Chrome")

        tags:
            ui, android, press, click, recent apps, homepage, app
    """
    pass


@devicedecorator
class open_app_from_recent_apps():

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
    pass


@devicedecorator
class open_app_from_allapps():

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
    pass


@devicedecorator
class find_app_from_allapps():

    """ description:
            finds the application identified by <view_to_find> from
                all application activity

        usage:
            ui.steps.find_app_from_allapps(view_to_find = {"text": "Settings"})()

        tags:
            ui, android, find, app, application, allapps
    """
    pass


@devicedecorator
class open_smart_lock_settings():

    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """
    pass


@devicedecorator
class open_settings():

    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """
    pass


@devicedecorator
class open_settings_app():

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
    pass


@devicedecorator
class open_app_from_settings():

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
    pass


# TODO: remake
@devicedecorator
class open_quick_settings():

    """ description:
            opens quick settings

        usage:
            ui_steps.open_quick_settings()

        tags:
            ui, android, open, press, click, quicksettings
 """
    pass


@devicedecorator
class open_playstore():

    """ description:
            opens Play store application from all application page

        usage:
            ui_steps.open_play_store()

        tags:
            ui, android, press, click, playstore, allapps, applications
    """
    pass


@devicedecorator
class open_google_books():

    """ description:
            opens Google Books application from all application page

        usage:
            ui_steps.open_google_books()

        tags:
            ui, android, press, click, books, allapps, applications
    """
    pass


@devicedecorator
class add_google_account():

    """ description:
            adds google account <account> from settings page

        usage:
            ui_steps.add_google_accout(version = "L",
                                      account = "account_email",
                                      paswword = "account_password")

        tags:
            ui, android, google, account, playstore, apps
    """
    pass


@devicedecorator
class add_app_from_all_apps_to_homescreen():

    """ description:
            Click on an App from App view and drag it
            to home screen

        usage:
            test_verification('app_to_drag_from_app_view')()

        tags:
            homescreen, drag app icon
    """

    pass


@devicedecorator
class uninstall_app_from_apps_settings():

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
    pass


@devicedecorator
class uninstall_app():

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
    pass


@devicedecorator
class open_display_from_settings():

    """ description:
            open display menu from settings

        usage:
            ui_steps.open_display_from_settings(view_to_check =
                {"text":"Daydream"})()

        tags:
            ui, android, press, click, app, application, settings
    """
    pass


class click_checkbox_button(ui_step):

    """ description:
            click a checkbox button to change it to desired state
            use state = "ON" / "OFF" to choose to check or un-check it
        usage:
            ui_steps.click_checkbox_button(
                view_to_find = {"text":"Automatic restore"},
                state = "ON")()
        tags:
            ui, android, click, settings, checkbox
    """

    def __init__(self, view_to_find, state="ON", confirm_view=None,
                 view_to_check_after_confirm=None, scrollable=False,
                 is_switch=False, relationship="sibling", wait_time=5000,
                 **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.state = state
        self.confirm_view = confirm_view
        self.view_to_check = view_to_check_after_confirm
        self.scrollable = scrollable
        self.is_switch = is_switch
        self.relationship = relationship
        self.wait_time = wait_time
        self.set_passm(
            "Set the {0} checkbox to {1}".format(self.view_to_find, self.state))
        self.set_errorm("", "Could not set the {0} checkbox to {1}".format(
            self.view_to_find, self.state))

    def do(self):
        if self.scrollable:
            self.uidevice(scrollable=True).scroll.to(**self.view_to_find)
        is_checked = ui_utils.is_checkbox_checked(serial=self.serial,
                                                  view_to_find=self.view_to_find,
                                                  is_switch=self.is_switch,
                                                  relationship=self.relationship)
        if (is_checked and self.state == "OFF") or (not is_checked and
                                                    self.state == "ON"):
            click_button(serial=self.serial,
                         view_to_find=self.view_to_find)()

            if self.confirm_view and self.uidevice(**self.confirm_view).wait.exists(timeout=self.wait_time):
                click_button(serial=self.serial,
                             view_to_find=self.confirm_view,
                             view_to_check=self.view_to_check)()
                self.uidevice(
                    **self.confirm_view).wait.gone(timeout=self.wait_time)

    def check_condition(self):
        checkbox_checked = (self.state != "ON")
        timeout = 0
        while not (checkbox_checked is (self.state == "ON")) and timeout < self.wait_time:
            checkbox_checked = ui_utils.is_checkbox_checked(serial=self.serial,
                                                            view_to_find=self.view_to_find,
                                                            is_switch=self.is_switch,
                                                            relationship=self.relationship)
            time.sleep(1)
            timeout += 1000
        return checkbox_checked is (self.state == "ON")


@devicedecorator
class open_picture_from_gallery():

    """ description:
            open picture from gallery

        usage:
            ui_steps.open_picture_from_gallery()()

        tags:
            ui, android, press, click, picture, gallery
    """
    pass


@devicedecorator
class enable_developer_options():

    """ description:
            enables developer options in Settings

        usage:
            ui_steps.enable_developer_options()()

        tags:
            ui, android, developer, options
    """
    pass


@devicedecorator
class disable_options_from_developer_options():

    """ description:
            disables an option from developer options

        usage:
            ui_steps.disable_options_from_developer_options(developer_options =
                                                         ["Verify apps over USB"])()

        tags:
            ui, android, disable, developer options
    """
    pass


@devicedecorator
class enable_options_from_developer_options():

    """ description:
            enables an option from developer options
            if <enabled> parameter is True, <Developer options> is enabled

        usage:
            ui_steps.enable_options_from_developer_options(developer_options =
                                                         ["Verify apps over USB"])()

        tags:
            ui, android, enable, developer options
    """
    pass


@devicedecorator
class enable_oem_unlock():

    """ description:
            enables Oem unlock from "Developer options"

        usage:
            ui_steps.enable_oem_unlock()()

        tags:
            ui, android, enable, developer options
    """
    pass


@devicedecorator
class allow_unknown_sources():

    """ description:
            enables/disables Unknwon sources according to <state>

        usage:
            cts_steps.allow_unknown_sources(state = "ON")()

        tags:
            ui, android, cts, allow, unknown_sources
    """
    pass


@devicedecorator
class put_device_into_sleep_mode():

    """ description:
            sets the device into sleep mode with sleep button
            checks the logcat for sleep message
            fails if the DUT is already in sleep mode

        usage:
            ui_steps.put_device_into_sleep_mode()()

        tags:
            ui, android, sleep
    """
    pass


@devicedecorator
class wake_up_device():

    """ description:
            wakes the device from sleep with sleep button
            checks the logcat for wake message

        usage:
            ui_steps.wake_up_device()()

        tags:
            ui, android, wake
    """
    pass


@devicedecorator
class unlock_device_swipe():

    """ description:
            unlocks the screen with swipe

        usage:
            ui_steps.unlock_device_swipe()()

        tags:
            ui, android, unlock
    """
    pass


@devicedecorator
class unlock_device_pin():

    """ description:
            unlocks the screen with PIN

        usage:
            ui_steps.unlock_device_pin(pin = "1234")()

        tags:
            ui, android, unlock, PIN
    """
    pass


@devicedecorator
class unlock_device():

    """ description:
            unlocks the screen with swipe and/or PIN


        usage:
            ui_steps.unlock_device()()

        tags:
            ui, android, unlock
    """
    pass


class scroll_to_text_from_scrollable(ui_step):

    """ description:
            scrolls up on until <text_to_find> is shown in the <view_to_scroll>
            scrollable view using swipe

        usage:
            ui_steps.scroll_to_text_from_scrollable(text_to_find = "United States",
                                                    view_to_scroll = {"resourceId": "android:id/numberpicker_input"},
                                                    iterations = 200,
                                                    direction = "down")()

        tags:
            ui, android, swipe, scroll, text, scrollable
    """

    def __init__(self, text_to_find="United States",
                 view_to_scroll={
                     "resourceId": "android:id/numberpicker_input"},
                 iterations=200,
                 direction="down",
                 **kwargs):
        self.text_to_find = text_to_find
        self.iterations = iterations
        ui_step.__init__(self, **kwargs)
        self.scrollable_view = self.uidevice(**view_to_scroll)
        if direction == "down":
            self.start_x = int((self.scrollable_view.info['bounds'][
                               'left'] + self.scrollable_view.info['bounds']['right']) / 2)
            self.start_y = self.scrollable_view.info['bounds']['bottom']
            self.end_x = self.start_x
            self.end_y = self.scrollable_view.info['bounds']['top']
        elif direction == "up":
            self.start_x = int((self.scrollable_view.info['bounds'][
                               'left'] + self.scrollable_view.info['bounds']['right']) / 2)
            self.start_y = self.scrollable_view.info['bounds']['top']
            self.end_x = self.start_x
            self.end_y = self.scrollable_view.info['bounds']['bottom']
        elif direction == "left":
            self.start_y = int((self.scrollable_view.info['bounds'][
                               'top'] + self.scrollable_view.info['bounds']['bottom']) / 2)
            self.start_x = self.scrollable_view.info['bounds']['right']
            self.end_y = self.start_y
            self.end_x = self.scrollable_view.info['bounds']['left']
        elif direction == "right":
            self.start_y = int((self.scrollable_view.info['bounds'][
                               'top'] + self.scrollable_view.info['bounds']['bottom']) / 2)
            self.start_x = self.scrollable_view.info['bounds']['left']
            self.end_y = self.start_y
            self.end_x = self.scrollable_view.info['bounds']['right']

    def do(self):
        iterations = 0
        while (self.text_to_find not in self.scrollable_view.info['text'] and iterations < self.iterations):
            swipe(serial=self.serial,
                  sx=self.start_x, sy=self.start_y,
                  ex=self.end_x, ey=self.end_y,
                  steps=10)()
            iterations += 1

    def check_condition(self):
        return self.uidevice(textContains=self.text_to_find).wait.exists(timeout=1000)


@devicedecorator
class perform_startup_wizard():

    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """
    pass


@devicedecorator
class perform_startup_wizard_for_new_user():

    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """
    pass


@devicedecorator
class set_orientation():

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
    pass


class check_object_count(ui_step):

    """ description:

        usage:
            check_object_count(view_to_find = {"text":"Songs"}, count = 2)

        tags:
            ui, android, count
    """

    def __init__(self, view_to_find, count=1, comparator="=", **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.count = count
        self.comparator = comparator

    def do(self):
        pass

    def check_condition(self):
        if self.comparator is "<":
            return self.uidevice(**self.view_to_find).count < self.count
        if self.comparator is ">":
            return self.uidevice(**self.view_to_find).count > self.count
        return self.uidevice(**self.view_to_find).count == self.count


class scroll_to(ui_step):

    """ description:
            scrolls on scrollable ui object
            to object identified by view_to_find

        usage:
            ui_steps.scroll_to(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/button_allow"})()

        tags:
            ui, android, scroll
    """

    view_to_find = None

    def __init__(self, view_to_find, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.set_errorm("", "Could not scrolled to {0}".format(view_to_find))
        self.set_passm("Scrolled to {0}".format(view_to_find))

    def do(self):
        self.success = self.uidevice(scrollable=True).\
            scroll.to(**self.view_to_find)

    def check_condition(self):
        return self.success


@devicedecorator
class close_app_from_recent():

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
    pass


@devicedecorator
class open_widget_section():

    """ description:
            opens the widget section on L dessert

        usage:
            open_widget_section()()

        tags:
            android, L, ui, widget, homescreen
    """
    pass


@devicedecorator
class add_widget_to_homescreen():

    """ description:
            adds a widget to the homescreen. Homescreen should be empty

        usage:
            add_widget_to_homescreen(widget_name = "Sound search")()

        tags:
            android, ui, widget, homescreen
    """
    pass


@devicedecorator
class open_add_google_account_wizard():

    """ description:
            opens add google account wizard from Settings

        usage:
            ui_steps.open_add_google_account_wizard()()

        tags:
            ui, android, google, account
    """
    pass


@devicedecorator
class open_google_account_for_edit():

    """ description:
            opens google accounts for editing

        usage:
            ui_steps.open_google_account_for_edit(serial = serial)()

        tags:
            ui, android, google, account
    """
    pass


@devicedecorator
class remove_google_account():

    """ description:
            removes gmail account given its name

        usage:
            ui_steps.remove_google_account(account = "intelchat002@gmail.com")()

        tags:
            ui, android, google, account
    """
    pass


@devicedecorator
class remove_all_google_accounts():

    """ description:
            removes all gmail accounts

        usage:
            ui_steps.remove_google_account()()

        tags:
            ui, android, google, account
    """
    pass


@devicedecorator
class show_as_list():

    """ description:
            Show as list when grid or list is available in More options

        usage:
            ui_steps.show_as_list(serial = serial)()

        tags:
            ui, android, list, grid, open
    """
    pass


@devicedecorator
class close_all_app_from_recent():

    """ description:
            close all application from recent apps

        usage:
            ui_steps.close_all_app_from_recent()()

        tags:
            ui, android, recent, close app,
    """
    pass


@devicedecorator
class set_timezone_from_settings():

    """ description:
            Configures system timezone to a specified value.

        usage:
            ui_steps.set_timezone_from_settings(serial = serial,
                                                timezone = "London")()

        tags:
            ui, android, timezone
    """
    pass


@devicedecorator
class sync_google_account():

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
    pass


@devicedecorator
class handle_google_action_required():

    """ description:
            If "Action required" message is displayed, reenter password.

        usage:
            ui_steps.handle_google_action_required(serial = serial,
                                        account = "account@gmail.com",
                                        password = "password")()

        tags:
            ui, android, google account
    """
    pass


@devicedecorator
class set_orientation_vertical():

    """ description:
        Sets the device orientation to the 'portrait' or 'landscape' as defined
        for devices of type phone.

    usage:
        ui_steps.set_orientation_vertical(serial = serial, orientation='portrait')()

    tags:
        ui, android, click, button
    """
    pass


@devicedecorator
class block_device():

    """ description:
            unlocks DUT with wrong PIN 5 times in a row

        usage:
            ui_steps.block_device(pin = "2222")()

        tags:
            ui, android, PIN
    """
    pass


@devicedecorator
class block_device_at_boot_time():

    """ description:
            enters wrong PIN 10 times in a row at boot time

        usage:
            ui_steps.block_device_at_boot_time()()

        tags:
            ui, android, PIN
    """
    pass


@devicedecorator
class create_new_user():

    """ description:
            Creates new user

        usage:
            ui_steps.create(user_name = "USER"()()

        tags:
            ui, android, create, user
    """
    pass


@devicedecorator
class remove_user():

    """ description:
            Deletes new user

        usage:
            ui_steps.remove_user(user_name = "USER"()()

        tags:
            ui, android, delete, user
    """
    pass


@devicedecorator
class set_up_user():

    """ description:
            Deletes new user

        usage:
            ui_steps.set_up_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """
    pass


@devicedecorator
class switch_user():

    """ description:
            Deletes new user

        usage:
            ui_steps.switch_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """
    pass


@devicedecorator
class add_trusted_location():

    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """
    pass


@devicedecorator
class remove_trusted_location():

    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """
    pass


@devicedecorator
class add_trusted_device():

    """ description:
            Adds a trusted device (Smart lock)

        usage:
            ui_steps.add_trusted_device(device_name = <device_name>)()

        tags:
            ui, android, switch, user
    """
    pass


@devicedecorator
class set_date_and_time():
    pass

    def check_condition(self):
        # Check performed in do()
        return True


@devicedecorator
class enable_disable_auto_time_date():

    """ description:
            Enables or disables the auto time and date option in settings

        usage:
            ui_steps.enable_disable_auto_time_date(serial=serial,
                                                   enable=True/False)()

        tags:
            ui, android, enable, disable, time, date
    """
    pass


@devicedecorator
class enable_disable_auto_timezone():

    """ description:
            Enables or disables the timezone switch button from Date & time settings

        usage:
            ui_steps.set_automatic_timezone(serial=serial,
                                            time_zone_switch_value=True for "ON"/ False for "OFF")()

        tags:
            ui, android, enable, disable, timezone
    """
    pass


@applicable("automotive")
@devicedecorator
class press_map(ui_step):

    """ description:
                Open car map application

            usage:
                ui_steps.press_map(serial=serial)()

            tags:
                ui, android, map, ivi
        """

    pass


@applicable("automotive")
@devicedecorator
class press_dialer(ui_step):

    """ description:
                Open car dialer application

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
    """
    pass


@applicable("automotive")
@devicedecorator
class press_media():

    """ description:
                Open car media application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """
    pass


@applicable("automotive")
@devicedecorator
class press_car():

    """ description:
                Open car application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """
    pass


class click_button_common(ui_step):

    """ description:
            clicks a button identified by <view_to_find>
                if <view_to_check> given it will check that the object
                identified by <view_to_check>:
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

            clicks a button at the <position> of the <view_to_find>,
            if <second_view_to_find> and <position> are given.

            clicks a button which is (child|sibling|left|right|up|down) of
            the <view_to_find>, if <second_view_to_find> is given.

            By default, screen will be scrolled and checked for
            <view_to_check/second_view_to_find> if screen can be scrollable.
                To avoid scrolling screen, scroll=False should be given

            By default, <view_to_find/second_view_to_find> is not optional. It
            will fail incase <view_to_find/second_view_to_find> is not found
                To avoid failure when view_to_find is not available,
                optional=True should be given

            By default, long_click is false. long_click=True to long_click
            on <view_to_find/second_view_to_find>

        usage:
            ui_steps.click_button_common(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/button_allow"},
                    view_to_check = {"text": "OK"})()

        tags:
            ui, android, click, button
    """

    def __init__(self, view_to_find, view_to_check=None, view_presence=True,
                 timeout=5000, second_view_to_find=None, optional=False,
                 scroll=True, view_to_scroll={"scrollable": "true"},
                 long_click=False, position=None, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.view_presence = view_presence
        self.timeout = timeout
        self.second_view_to_find = second_view_to_find
        self.optional = optional
        self.scroll = scroll
        self.view_to_scroll = view_to_scroll
        self.long_click = long_click
        self.position = position
        self.step_data = False
        self.error_trace_msg = ""

    def do(self):
        time.sleep(0.5)
        if not self.uidevice(**self.view_to_find).exists and self.scroll is True and self.uidevice(
                **self.view_to_scroll).exists:
            self.uidevice(**self.view_to_scroll).scroll.to(**self.view_to_find)
        if self.optional and not self.uidevice(**self.view_to_find).exists:
            return

        if self.second_view_to_find is not None:
            if self.second_view_to_find is not None and self.position is not None:
                uobj = getattr(self.uidevice(**self.view_to_find),
                               self.position)
                try:
                    if uobj(**self.second_view_to_find).exists:
                        if not self.long_click:
                            uobj(**self.second_view_to_find).click.wait()
                        else:
                            uobj(**self.second_view_to_find).long_click()
                        self.step_data = True
                except:
                    self.error_trace_msg = traceback.format_exc()
            elif self.second_view_to_find is not None:
                for pos in ["child", "sibling", "left", "right", "up", "down"]:
                    uobj = getattr(self.uidevice(**self.view_to_find), pos)
                    try:
                        uobj(**self.second_view_to_find).exists
                    except:
                        self.error_trace_msg = traceback.format_exc()
                        continue
                    if uobj(**self.second_view_to_find).exists:
                        if not self.long_click:
                            uobj(**self.second_view_to_find).click.wait()
                        else:
                            uobj(**self.second_view_to_find).long_click()
                        self.step_data = True
                        break
        else:
            try:
                if not self.long_click:
                    self.uidevice(**self.view_to_find).click.wait()
                else:
                    self.uidevice(**self.view_to_find).long_click()
                self.step_data = True
            except:
                self.error_trace_msg = traceback.format_exc()

    def check_condition(self):
        self.set_errorm(self.error_trace_msg, "Could not click {0} checking "
                        "{1}".format(self.view_to_find, self.view_to_check))
        self.set_passm("{0} clicked checking {1}".format(self.view_to_find,
                                                         self.view_to_check))
        if self.step_data is False and self.optional:
            self.set_passm("Could not click {0} and skipped as "

                           "optional step".format(self.view_to_find))
            return True
        if self.step_data is True and self.view_to_check is not None:
            if self.view_presence:
                self.step_data = self.uidevice(
                    **self.view_to_check).wait.exists(timeout=self.timeout)
            else:
                self.step_data = self.uidevice(
                    **self.view_to_check).wait.gone(timeout=self.timeout)
            if self.step_data is False:
                self.set_errorm(self.error_trace_msg, "{0} clicked "
                                "but could not check {1}".format(self.view_to_find,
                                                                 self.view_to_check))
        return self.step_data


class wait_for_view_common(ui_step):

    """ description:
            wait for view identified by <view_to_find>
                - appeared if <view_presence> is True
                - disappeared if <view_presence> is False

            wait for view <view_to_find> (child|sibling|left|right|up|down) <second_view_to_find>
            if <second_view_to_find> is given.

            wait for view <view_to_find> <position> <second_view_to_find>
            if <second_view_to_find> and <position> is given.

            By default, screen will be scrolled and checked for
            <view_to_check/second_view_to_find> if screen can be scrollable.
                To avoid scrolling screen, scroll=False should be given

            By default, <view_to_check/second_view_to_find> is not optional.
            It will fail incase <view_to_check/second_view_to_find> is not found
                To avoid failure, optional=True should be given

            By default, <retrieve_info> is False. retrieve_info=False to
            retrieve info about <view_to_find/second_view_to_find>

        usage:
            ui_steps.wait_for_view_common(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/button_allow"})()

        tags:
            ui, android, find, search, button
    """

    def __init__(self, view_to_find, second_view_to_find=None,
                 view_presence=True, timeout=5000, position=None,
                 optional=False, scroll=True, view_to_scroll={
                     "scrollable": "true"}, return_value=False, retrieve_info=False, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.second_view_to_find = second_view_to_find
        self.view_presence = view_presence
        self.timeout = timeout
        self.position = position
        self.optional = optional
        self.scroll = scroll
        self.view_to_scroll = view_to_scroll
        self.retrieve_info = retrieve_info
        self.step_data = False
        self.return_value = return_value
        self.error_trace_msg = ""

    def do(self):
        time.sleep(0.5)
        if not self.uidevice(**self.view_to_find).exists and self.scroll is True and self.uidevice(
                **self.view_to_scroll).exists:
            self.uidevice(**self.view_to_scroll).scroll.to(**self.view_to_find)
        if self.return_value:
            value = self.uidevice(**self.view_to_find).exists
            return value
        if not self.uidevice(**self.view_to_find).exists:
            return
        if self.second_view_to_find is not None:
            if self.position is not None:
                uobj = getattr(self.uidevice(**self.view_to_find),
                               self.position)
                try:
                    if uobj(**self.second_view_to_find).exists:
                        self.step_data = True if not self.retrieve_info else \
                            uobj(**self.second_view_to_find).info
                except:
                    # print traceback.format_exc()
                    self.error_trace_msg = traceback.format_exc()
            else:
                for pos in ["child", "sibling", "left", "right", "up", "down"]:
                    uobj = getattr(self.uidevice(**self.view_to_find), pos)
                    try:
                        if uobj(**self.second_view_to_find).exists:
                            self.step_data = True if not self.retrieve_info \
                                else uobj(**self.second_view_to_find).info
                            break
                    except:
                        self.error_trace_msg = traceback.format_exc()
                        continue
        else:
            self.step_data = True if not self.retrieve_info else \
                self.uidevice(**self.view_to_find).info

    def check_condition(self):
        if self.second_view_to_find is None:
            if self.view_presence:
                self.set_errorm(self.error_trace_msg, "Could not find {"
                                "0}".format(self.view_to_find))
                self.set_passm("Found view {0}".format(self.view_to_find))
            else:
                self.set_errorm(self.error_trace_msg, "View {0} still "
                                "exists".format(self.view_to_find))
                self.set_passm("View {0} is gone".format(self.view_to_find))
        else:
            if self.view_presence:
                self.set_errorm(self.error_trace_msg, "Could not find {"
                                "0}''\,,{1}".format(self.view_to_find,
                                                    self.second_view_to_find))
                self.set_passm("Found view {0}''\,,{1}".format(
                    self.view_to_find, self.second_view_to_find))
            else:
                self.set_errorm(self.error_trace_msg, "View {0}''\,,{1} still "
                                "exists".format(self.view_to_find, self.second_view_to_find))
                self.set_passm("View {0}''\,,{1} is gone".format(
                    self.view_to_find, self.second_view_to_find))

        if self.step_data is False and self.optional:
            self.set_passm("Could not find {0} and skipped as "
                           "optional step".format(self.view_to_find))
            return True
        if self.step_data is not False:
            if not self.view_presence:
                self.step_data = False
        else:
            if not self.view_presence:
                self.step_data = True
        return self.step_data


class search_image_object(ui_step):

    """ description:
         search for give image object in the <view_to_find> in the current screen
           <view_to_find> is path to the image object to be searched in the
           dut screen.

          search_image_object <view_to_find> <bounds>
            if <bounds> is given, search will fail when not found a match
            inside the bounding box

          search_image_object <view_to_find> <threshold>
            by default <threshold> is 0.8 which actually denotes the
            intensity of object match in the screen.

          usage:
            ui_steps.search_image_object(view_to_find =
            "/path/to/image/object/to/find/in/dut/screen")()

          tags:
            ui, android, find, search, image
    """

    def __init__(self, view_to_find, bounds=None, threshold=0.8,
                 optional=False, scroll=False, view_to_scroll={
                     "scrollable": "true"}, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.view_to_find = view_to_find
        self.bounds = bounds
        self.threshold = threshold
        self.optional = optional
        self.scroll = scroll
        self.view_to_scroll = view_to_scroll
        self.step_data = False

    def do(self):
        import cv2
        '''
        import numpy as np
        from matplotlib import pyplot as plt
        '''
        temp_file_name = time.strftime('%c')
        temp_file_name = "/tmp/screenshot_" + temp_file_name.replace(' ', '-')
        try:
            if not self.take_picture(temp_file_name):
                raise Exception
        except:
            raise BlockingError("Failed to take device screenshot while "
                                "searching for image object")
        screenshot = cv2.imread(temp_file_name, 0)
        try:
            import os
            os.remove(temp_file_name)
        except:
            self.logger.info(
                "Unable to remove temp file: {}".format(temp_file_name))

        img = screenshot.copy()

        try:
            if not os.path.exists(self.view_to_find):
                raise Exception
        except:
            raise BlockingError(
                "Given template file: {} doesn't exist".format(temp_file_name))

        template = cv2.imread(self.view_to_find, 0)
        w, h = template.shape[::-1]

        # All the 6 methods for comparison in a list
        # methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
        #            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF',
        #           'cv2.TM_SQDIFF_NORMED']

        meth = 'cv2.TM_CCOEFF_NORMED'
        method = eval(meth)

        # Apply template Matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # print min_val, max_val, min_loc, max_loc
        if max_val >= self.threshold:
            # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            # print "top left and bottom right is ", top_left, bottom_right
            if self.bounds:
                try:
                    xmin = self.bounds[0][0]
                    ymin = self.bounds[0][1]
                    xmax = self.bounds[1][0]
                    ymax = self.bounds[1][1]
                except:
                    raise BlockingError("Bound value is not correct, should be "
                                        "given as [[xmin, ymin], [xmax, ymax]]")

                if top_left > (xmin, ymin) and bottom_right > (xmax, ymax):
                    self.step_data = True
            else:
                self.step_data = True
        if self.step_data:
            self.set_passm("Image object is found and bounds at {}{}".format(
                list(top_left), list(bottom_right)))
            self.step_data = [list(top_left), list(bottom_right)]
        else:
            self.set_errorm("", "Image object is not found")

        '''cv2.rectangle(img, top_left, bottom_right, 255, 2)
        plt.subplot(121), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(img, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)
        plt.show()
        '''

    def check_condition(self):
        if self.step_data:
            return True
        else:
            return False


class click_image_button(ui_step):

    """ description:
             search and click give image object in the <view_to_find> in the current screen
               <view_to_find> is path to the image object to be searched and clicked in the
               dut screen.

              click_image_button <view_to_find> <bounds>
                if <bounds> is given, search will fail when not found a match
                inside the bounding box

              search_image_object <view_to_find> <threshold>
                by default <threshold> is 0.8 which actually denotes the
                intensity of object match in the screen.

              usage:
                ui_steps.search_image_object(view_to_find =
                "/path/to/image/object/to/find/in/dut/screen")()

              tags:
                ui, android, find, click, image
        """

    def __init__(self, view_to_find, view_to_check=None, **kwargs):
        super(click_image_button, self).__init__(**kwargs)
        self.view_to_find = view_to_find
        self.view_to_check = view_to_check
        self.step_data = False
        self.kwargs = kwargs

    def do(self):
        bounds = search_image_object(
            view_to_find=self.view_to_find, **self.kwargs)()
        if bounds:
            x_center = (bounds[0][0] + bounds[1][0]) / 2
            y_center = (bounds[0][1] + bounds[1][1]) / 2
            self.step_data = click_xy(serial=self.serial, x=x_center,
                                      y=y_center, view_to_check=self.view_to_check)()

    def check_condition(self):
        return self.step_data


class device_info(ui_step):

    def __init__(self, key=None, **kwargs):
        super(device_info, self).__init__(**kwargs)
        self.key = key
        self.step_data = False

    def do(self):
        try:
            self.step_data = self.uidevice.info
        except:
            pass

    def check_condition(self):
        if self.step_data:
            if self.key is not None:
                self.step_data = self.step_data[self.key]
            return True
        else:
            return False


@devicedecorator
class PressNotification(ui_step):
    """
        description:
            Open Notification
        usage:
            ui_steps.PressNotification()
        tags:
            ui, android, press, click, quick setting
      """
    pass


click_button = click_button_common
wait_for_view = wait_for_view_common
