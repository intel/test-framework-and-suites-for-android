#!/usr/bin/env python#!/usr/bin/env python

#######################################################################
#
# @filename:    ui_steps.py
# @description: UI test steps
# @author:      ion-horia.petrisor@intel.com
#
#######################################################################

# standard libraries
import time

from testlib.scripts.android.ui.ui_step import step as ui_step
from testlib.utils.connections.adb import Adb
from testlib.scripts.android.ui.automotive_O import ui_steps as parent_ui_steps


class set_pin_screen_lock(parent_ui_steps.set_pin_screen_lock):
    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """

    pass


class remove_pin_screen_lock(parent_ui_steps.remove_pin_screen_lock):

    """ description:
            sets screen lock method to PIN <selected PIN>
                if already set to PIN, it will skip

        usage:
            ui_steps.set_pin_screen_lock(pin = "1234")()

        tags:
            ui, android, click, button
    """
    pass


class open_security_settings(parent_ui_steps.open_security_settings):

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """
    pass


class open_users_settings(parent_ui_steps.open_users_settings):

    """ description:
            Opens the Security Settings page using an intent.

        usage:
            ui_steps.open_security_settings()()

        tags:
            ui, android, settings, security, intent
    """
    pass


class am_start_command(parent_ui_steps.am_start_command):

    """ description:
            Opens the WiFi Settings page using an intent.

        usage:
            wifi_steps.open_wifi_settings()()

        tags:
            ui, android, settings, wifi, intent
    """

    pass


class am_stop_package(parent_ui_steps.am_stop_package):
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


# TODO: rename with open_quick_settings_with_swipe
# add desciption
class open_notifications_menu(parent_ui_steps.open_notifications_menu):
    pass


class press_all_apps(parent_ui_steps.press_all_apps):

    """ description:
            opens all application activity

        usage:
            ui_steps.press_all_apps()

        tags:
            ui, android, press, click, allapps, applications
    """
    pass


class press_home(parent_ui_steps.press_home):

    """ description:
            opens home page

        usage:
            ui_steps.press_home()

        tags:
            ui, android, press, click, home, homepage
    """
    pass


class press_recent_apps(parent_ui_steps.press_recent_apps):

    """ description:
            opens recent apps

        usage:
            ui_steps.press_recent_apps()

        tags:
            ui, android, press, click, recent apps, homepage
    """
    pass


class app_in_recent_apps(parent_ui_steps.app_in_recent_apps):

    """ description:
            opens recent apps and checks if <app_name> app is present

        usage:
            ui_steps.app_in_recent_apps(app_name = "Chrome")

        tags:
            ui, android, press, click, recent apps, homepage, app
    """
    pass


class open_app_from_recent_apps(parent_ui_steps.open_app_from_recent_apps):
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


class open_app_from_allapps(parent_ui_steps.open_app_from_allapps):
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


class find_app_from_allapps(parent_ui_steps.find_app_from_allapps):
    """ description:
            finds the application identified by <view_to_find> from
                all application activity

        usage:
            ui.steps.find_app_from_allapps(view_to_find = {"text": "Settings"})()

        tags:
            ui, android, find, app, application, allapps
    """
    pass


class open_smart_lock_settings(parent_ui_steps.open_smart_lock_settings):
    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """
    pass


class open_settings(parent_ui_steps.open_settings):
    """ description:
            opens settings activity from all application page

        usage:
            ui_steps.open_settings()

        tags:
            ui, android, press, click, settings, allapps
    """
    pass


class open_settings_app(parent_ui_steps.open_settings_app):
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


class open_app_from_settings(parent_ui_steps.open_app_from_settings):
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
class open_quick_settings(parent_ui_steps.open_quick_settings):
    """ description:
            opens quick settings

        usage:
            ui_steps.open_quick_settings()

        tags:
            ui, android, open, press, click, quicksettings
 """
    pass


class open_playstore(parent_ui_steps.open_playstore):
    """ description:
            opens Play store application from all application page

        usage:
            ui_steps.open_play_store()

        tags:
            ui, android, press, click, playstore, allapps, applications
    """
    pass


class open_google_books(parent_ui_steps.open_google_books):
    """ description:
            opens Google Books application from all application page

        usage:
            ui_steps.open_google_books()

        tags:
            ui, android, press, click, books, allapps, applications
    """
    pass


class add_google_account(parent_ui_steps.add_google_account):

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


class add_app_from_all_apps_to_homescreen(parent_ui_steps.add_app_from_all_apps_to_homescreen):
    """ description:
            Click on an App from App view and drag it
            to home screen

        usage:
            test_verification('app_to_drag_from_app_view')()

        tags:
            homescreen, drag app icon
    """
    pass


class uninstall_app_from_apps_settings(parent_ui_steps.uninstall_app_from_apps_settings):
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


class uninstall_app(parent_ui_steps.uninstall_app):
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


class open_display_from_settings(parent_ui_steps.open_display_from_settings):
    """ description:
            open display menu from settings

        usage:
            ui_steps.open_display_from_settings(view_to_check =
                {"text":"Daydream"})()

        tags:
            ui, android, press, click, app, application, settings
    """
    pass


class open_picture_from_gallery(parent_ui_steps.open_picture_from_gallery):

    """ description:
            open picture from gallery

        usage:
            ui_steps.open_picture_from_gallery()()

        tags:
            ui, android, press, click, picture, gallery
    """
    pass


class enable_developer_options(parent_ui_steps.enable_developer_options):

    """ description:
            enables developer options in Settings

        usage:
            ui_steps.enable_developer_options()()

        tags:
            ui, android, developer, options
    """
    pass


class disable_options_from_developer_options(parent_ui_steps.disable_options_from_developer_options):

    """ description:
            disables an option from developer options

        usage:
            ui_steps.disable_options_from_developer_options(developer_options =
                                                         ["Verify apps over USB"])()

        tags:
            ui, android, disable, developer options
    """
    pass


class enable_options_from_developer_options(parent_ui_steps.enable_options_from_developer_options):

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


class enable_oem_unlock(parent_ui_steps.enable_options_from_developer_options):
    """ description:
            enables Oem unlock from "Developer options"

        usage:
            ui_steps.enable_oem_unlock()()

        tags:
            ui, android, enable, developer options
    """
    pass


class allow_unknown_sources(parent_ui_steps.allow_unknown_sources):
    """ description:
            enables/disables Unknwon sources according to <state>

        usage:
            cts_steps.allow_unknown_sources(state = "ON")()

        tags:
            ui, android, cts, allow, unknown_sources
    """
    pass


class put_device_into_sleep_mode(parent_ui_steps.put_device_into_sleep_mode):
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


class wake_up_device(parent_ui_steps.wake_up_device):
    """ description:
            wakes the device from sleep with sleep button
            checks the logcat for wake message

        usage:
            ui_steps.wake_up_device()()

        tags:
            ui, android, wake
    """
    pass


class unlock_device_swipe(parent_ui_steps.unlock_device_swipe):
    """ description:
            unlocks the screen with swipe

        usage:
            ui_steps.unlock_device_swipe()()

        tags:
            ui, android, unlock
    """
    pass


class unlock_device_pin(parent_ui_steps.unlock_device_pin):

    """ description:
            unlocks the screen with PIN

        usage:
            ui_steps.unlock_device_pin(pin = "1234")()

        tags:
            ui, android, unlock, PIN
    """
    pass


class unlock_device(parent_ui_steps.unlock_device):
    """ description:
            unlocks the screen with swipe and/or PIN


        usage:
            ui_steps.unlock_device()()

        tags:
            ui, android, unlock
    """
    pass


class perform_startup_wizard(parent_ui_steps.perform_startup_wizard):

    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """
    pass


class perform_startup_wizard_for_new_user(parent_ui_steps.perform_startup_wizard_for_new_user):
    """ description:
            performs start-up wizard

        usage:
            ui_steps.perform_startup_wizard(serial = "some_serial")()

        tags:
            ui, android, startup, wizard
    """
    pass


class set_orientation(parent_ui_steps.set_orientation):

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


class close_app_from_recent(parent_ui_steps.close_app_from_recent):

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


class open_widget_section(parent_ui_steps.open_widget_section):
    """ description:
            opens the widget section on L dessert

        usage:
            open_widget_section()()

        tags:
            android, L, ui, widget, homescreen
    """
    pass


class add_widget_to_homescreen(parent_ui_steps.add_widget_to_homescreen):
    """ description:
            adds a widget to the homescreen. Homescreen should be empty

        usage:
            add_widget_to_homescreen(widget_name = "Sound search")()

        tags:
            android, ui, widget, homescreen
    """
    pass


class open_add_google_account_wizard(parent_ui_steps.open_add_google_account_wizard):
    """ description:
            opens add google account wizard from Settings

        usage:
            ui_steps.open_add_google_account_wizard()()

        tags:
            ui, android, google, account
    """
    pass


class open_google_account_for_edit(parent_ui_steps.open_google_account_for_edit):

    """ description:
            opens google accounts for editing

        usage:
            ui_steps.open_google_account_for_edit(serial = serial)()

        tags:
            ui, android, google, account
    """
    pass


class remove_google_account(parent_ui_steps.remove_google_account):
    """ description:
            removes gmail account given its name

        usage:
            ui_steps.remove_google_account(account = "intelchat002@gmail.com")()

        tags:
            ui, android, google, account
    """
    pass


class remove_all_google_accounts(parent_ui_steps.remove_all_google_accounts):
    """ description:
            removes all gmail accounts

        usage:
            ui_steps.remove_google_account()()

        tags:
            ui, android, google, account
    """
    pass


class show_as_list(parent_ui_steps.show_as_list):
    """ description:
            Show as list when grid or list is available in More options

        usage:
            ui_steps.show_as_list(serial = serial)()

        tags:
            ui, android, list, grid, open
    """
    pass


class close_all_app_from_recent(parent_ui_steps.close_all_app_from_recent):
    """ description:
            close all application from recent apps

        usage:
            ui_steps.close_all_app_from_recent()()

        tags:
            ui, android, recent, close app,
    """
    pass


class set_timezone_from_settings(parent_ui_steps.set_timezone_from_settings):
    """ description:
            Configures system timezone to a specified value.

        usage:
            ui_steps.set_timezone_from_settings(serial = serial,
                                                timezone = "London")()

        tags:
            ui, android, timezone
    """
    pass


class sync_google_account(parent_ui_steps.sync_google_account):
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


class handle_google_action_required(parent_ui_steps.handle_google_action_required):
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


class set_orientation_vertical(parent_ui_steps.set_orientation_vertical):

    """ description:
        Sets the device orientation to the 'portrait' or 'landscape' as defined
        for devices of type phone.

    usage:
        ui_steps.set_orientation_vertical(serial = serial, orientation='portrait')()

    tags:
        ui, android, click, button
    """
    pass


class block_device(parent_ui_steps.block_device):

    """ description:
            unlocks DUT with wrong PIN 5 times in a row

        usage:
            ui_steps.block_device(pin = "2222")()

        tags:
            ui, android, PIN
    """
    pass


class block_device_at_boot_time(parent_ui_steps.block_device_at_boot_time):

    """ description:
            enters wrong PIN 10 times in a row at boot time

        usage:
            ui_steps.block_device_at_boot_time()()

        tags:
            ui, android, PIN
    """
    pass


class create_new_user(parent_ui_steps.create_new_user):

    """ description:
            Creates new user

        usage:
            ui_steps.create(user_name = "USER"()()

        tags:
            ui, android, create, user
    """
    pass


class remove_user(parent_ui_steps.remove_user):
    """ description:
            Deletes new user

        usage:
            ui_steps.remove_user(user_name = "USER"()()

        tags:
            ui, android, delete, user
    """
    pass


class set_up_user(parent_ui_steps.set_up_user):

    """ description:
            Deletes new user

        usage:
            ui_steps.set_up_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """
    pass


class switch_user(parent_ui_steps.switch_user):
    """ description:
            Deletes new user

        usage:
            ui_steps.switch_user(user_name = "USER"()()

        tags:
            ui, android, switch, user
    """
    pass


class add_trusted_location(parent_ui_steps.add_trusted_location):
    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """
    pass


class remove_trusted_location(parent_ui_steps.remove_trusted_location):
    """ description:
            Adds a trusted location (Smart lock)

        usage:
            ui_steps.add_trusted_location(location_name = "Test location"()()

        tags:
            ui, android, switch, user
    """
    pass


class add_trusted_device(parent_ui_steps.add_trusted_location):
    """ description:
            Adds a trusted device (Smart lock)

        usage:
            ui_steps.add_trusted_device(device_name = <device_name>)()

        tags:
            ui, android, switch, user
    """
    pass


class set_date_and_time(parent_ui_steps.set_date_and_time):
    pass


class enable_disable_auto_time_date(parent_ui_steps.enable_disable_auto_time_date):
    """ description:
            Enables or disables the auto time and date option in settings

        usage:
            ui_steps.enable_disable_auto_time_date(serial=serial,
                                                   enable=True/False)()

        tags:
            ui, android, enable, disable, time, date
    """
    pass


class enable_disable_auto_timezone(parent_ui_steps.enable_disable_auto_timezone):
    """ description:
            Enables or disables the timezone switch button from Date & time settings

        usage:
            ui_steps.set_automatic_timezone(serial=serial,
                                            time_zone_switch_value=True for "ON"/ False for "OFF")()

        tags:
            ui, android, enable, disable, timezone
    """
    pass


class press_map(parent_ui_steps.press_map):
    """ description:
                Open car map application

            usage:
                ui_steps.press_map(serial=serial)()

            tags:
                ui, android, map, ivi
        """

    def __init__(self, view_to_check={"packageName": "com.android.car.mapsplaceholder"}, timeout=5000, **kwargs):
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
            # Todo x has to be dynamic based on the screen size
            x = 410
            activity_bar_single_element_width = x / 6
            # In P dessert Maps resides at 2 position and click has to be done at the center
            map_x_coordinate = activity_bar_single_element_width * 3 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            y = info['displaySizeDpY']
            map_y_coordinate = y - 30

            for i in range(0, 5):
                # cmd = "input tap 405 1050"
                cmd = "input tap {0} {1}".format(map_x_coordinate, map_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(2)
                if self.check_view():
                    self.step_data = True
                    break


class press_dialer(parent_ui_steps.press_dialer):
    """ description:
                Open car dialer application

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
    """

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
            # Todo x has to be dynamic based on the screen size
            x = 410
            activity_bar_single_element_width = x / 6
            # In P dessert Dialer resides at 4 position and click has to be done at the center
            dialer_x_coordinate = activity_bar_single_element_width * 5 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            y = info['displaySizeDpY']
            dialer_y_coordinate = y - 30

            cmd = "input tap {0} {1}".format(dialer_x_coordinate, dialer_y_coordinate)
            adb_connection = Adb(serial=self.serial)
            adb_subprocess_object = adb_connection.run_cmd(cmd)
            if adb_subprocess_object.poll() == 0:
                self.step_data = True


class press_media(parent_ui_steps.press_media):
    """ description:
                Open car media application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """

    def __init__(self, view_to_check={"packageName": "com.android.car.media"}, timeout=5000,
                 **kwargs):
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
            # Todo x has to be dynamic based on the screen size
            x = 410
            activity_bar_single_element_width = x / 6
            # In P dessert Media resides at 3 position and click has to be done at the center
            media_x_coordinate = activity_bar_single_element_width * 4 - activity_bar_single_element_width / 2

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            y = info['displaySizeDpY']
            media_y_coordinate = y - 30

            for i in range(0, 5):
                cmd = "input tap {0} {1}".format(media_x_coordinate, media_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(1)
                if self.check_view():
                    self.step_data = True
                    break


class press_car(parent_ui_steps.press_car):
    """ description:
                Open car application and shows app picker

            usage:
                ui_steps.press_dialer(serial=serial)()

            tags:
                ui, android, dialer, ivi
        """

    def __init__(self, view_to_check={"text": "All apps"}, timeout=5000, **kwargs):
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
            # Todo x has to be dynamic based on the screen size
            x = 410
            activity_bar_single_element_width = x / 6
            # In P dessert Car(All apps icon) resides at 5 position and click has to be done at the center
            car_x_coordinate = activity_bar_single_element_width * 6 - activity_bar_single_element_width / 2
            self.view_to_check = {"text": "All apps"}

            # Default acitivity bar resides at the bottom, so y coordinate
            # can be used and to click at the center reducing the value by 30
            y = info['displaySizeDpY']
            car_y_coordinate = y - 30

            for i in range(0, 5):
                cmd = "input tap {0} {1}".format(car_x_coordinate, car_y_coordinate)
                adb_connection = Adb(serial=self.serial)
                adb_connection.run_cmd(cmd)
                time.sleep(1)
                if self.check_view():
                    self.step_data = True
                    break


class press_bell(ui_step):
    """ description:
                Open bell icon (Notification in android P)
            usage:
                ui_steps.press_bell(serial=serial)()
            tags:
                ui, android, press, click, quick setting, bell

    """

    def __init__(self, **kwargs):
        ui_step.__init__(self, **kwargs)
        self.step_data = False

    def do(self):
        self.uidevice.open.quick_settings()
        self.step_data = True

    def check_condition(self):
        return self.step_data
