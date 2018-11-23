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

from testlib.utils.ui.uiandroid import UIDevice as ui_device
# from testlib.base import base_utils
from testlib.utils.connections.adb import Adb as connection_adb
from testlib.scripts.android.adb import adb_utils
from testlib.scripts.android.ui import ui_statics

import time
from time import strftime


def my_handler(**kwargs):
    """ description:
            Create handler class to be registered

        usage:
            ui_utils.my_handler(selector = {'textContains': 'Process system isn't responding.'},
                                action_view = {'text': 'OK'},
                                action = 'click',
                                handler_name = 'process_system',
                                serial = some_serial)

        tags:
            ui, android, handler, function, create
    """

    class My_Handler(object):

        def __init__(self, serial, selector, action, action_view, handler_name):
            self.selector = selector
            self.action = action
            self.action_view = action_view
            self.handler_name = handler_name
            if serial:
                self.uidevice = ui_device(serial=serial)
            else:
                self.uidevice = ui_device()
            self.serial = serial

        def create_handler_function(self):
            obj = self

            def function_template(*args, **kwargs):
                if obj.uidevice(**obj.selector).exists:
                    print "[ {0} ]: Handler {1} has been triggered".format(str(obj.serial), obj.handler_name)
                    if obj.action == "click":
                        obj.uidevice(**obj.action_view).click.wait()
                    elif self.action == "press":
                        obj.uidevice.press(obj.action_view)
                    return True
            return function_template

        def register(self):
            funct = self.create_handler_function()
            funct.__name__ = self.handler_name
            self.uidevice.handlers.on(funct)

    return My_Handler(**kwargs)


def register_handlers(ui_handler_groups, serial=None):
    """ description:
            Register all the hadlers that are part of <ui_handler_group>

        usage:
            ui_utils.register_handlers(ui_handler_group = "cts")

        tags:
            ui, android, handler, register
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    for ui_handler_group in ui_handler_groups.split(" "):
        for handler_name, handler_value in ui_statics.handler_list.iteritems():
            if ui_handler_group in handler_value['groups'] and handler_name not in uidevice.handlers():
                handler_function = my_handler(selector=handler_value['selector'], action_view=handler_value[
                    'action_view'], action=handler_value['action'], handler_name=handler_name, serial=serial)
                handler_function.register()
                print "[ {0} ]: Handler {1} has been registered".format(serial, handler_name)


def get_registered_handlers(serial=None):
    """ description:
            returns all register handlers

        usage:
            ui_utils.get_registered_handlers()

        tags:
            ui, android, handler, get
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    return uidevice.handlers()


def get_triggered_watchers(serial=None):
    """ description:
            returns all register watchers that were triggered

        usage:
            ui_utils.get_triggered_watchers()

        tags:
            ui, android, watcher, get, triggered
    """
    if serial:
        uidevice = ui_device(serial=serial)
        adb_connection = connection_adb(serial=serial)
    else:
        uidevice = ui_device()
        adb_connection = connection_adb()

    triggered_watchers = []
    if adb_connection.check_connected():
        try:
            for watcher in uidevice.watchers:
                if uidevice.watcher(watcher).triggered:
                    triggered_watchers.append(watcher)
        except Exception as e:
            if "RPC" not in str(e.message) and "not connected" not in \
                    str(e.message) and "not attached" not in str(e.message):
                print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                    "Registered watchers query exception due to lack of adb connectivity: {0}".format(
                        e.message)
                raise
            else:
                print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                    "Watchers could not be queried due to exception: {}".format(
                        e.message)

    return triggered_watchers


def get_registered_watchers(serial=None):
    """ description:
            returns all register watchers

        usage:
            ui_utils.get_registered_watchers()

        tags:
            ui, android, watcher, get
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    return uidevice.watchers


def register_watchers(ui_watcher_groups, serial=None):
    """ description:
            register all the watchers that are part of <ui_watcher_group>

        usage:
            ui_utils.register_watchers(ui_watcher_goup = "cts")

        tags:
            ui, android, watcher, register
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    remove_non_group_watchers(
        ui_watcher_groups=ui_watcher_groups.split(" "), serial=serial)
    for ui_watcher_group in ui_watcher_groups.split(" "):
        for watcher_name, watcher_value in ui_statics.watcher_list.iteritems():
            if ui_watcher_group in watcher_value['groups']:
                if watcher_name not in uidevice.watchers:
                    try:
                        if watcher_value['action'] == "click":
                            uidevice.watcher(watcher_name).when(**watcher_value['selector']).click(**watcher_value[
                                'action_view'])
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher {0} has been  registered for {1}.".format(
                                    watcher_name, serial)
                        elif watcher_value['action'] == "press":
                            uidevice.watcher(watcher_name).when(**watcher_value['selector'])\
                                .press(watcher_value['action_view'])
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher {0} has been registered for {1}."\
                                .format(watcher_name, serial)
                        else:
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + "Invalid watcher action: {" \
                                                                                "0}".format(
                                                                                    watcher_value['action'])
                    except Exception as e:
                        if "RPC" not in str(e.message) and "not connected" not in str(e.message) and "not attached" \
                                not in str(e.message):
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher registration exception due to lack of adb connectivity: {0}"\
                                .format(e.message)
                            raise
                        else:
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher {} could not be registered due to exception: {}"\
                                .format(watcher_name, e.message)


def remove_non_group_watchers(ui_watcher_groups, serial=None):
    """ description:
            removes all the watchers that are not part of <ui_watcher_group>

        usage:
            ui_utils.remove_non_group_watchers(ui_watcher_goup = "cts")

        tags:
            ui, android, watcher, remove
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    try:
        for watcher in uidevice.watchers:
            found = True
            for ui_watcher_group in ui_watcher_groups:
                if ui_statics.watcher_list in (watcher) and ui_watcher_group in ui_statics.watcher_list[watcher][
                        'groups']:
                    break
                else:
                    found = False
            if not found:
                uidevice.watchers.remove(watcher)
    except Exception as e:
        if "RPC" not in str(e.message) and "not connected" not in str(e.message) and "not attached" not in str(
                e.message):
            print "[ {0} ]: Remove non-group watchers due to lost adb connection exception: {1}".format(serial,
                                                                                                        e.message)
            raise
        else:
            print "[ {0} ]: Non group watchers could not be unregistered due to exception: {1}".format(serial,
                                                                                                       e.message)


def remove_watchers(ui_watcher_group=None, serial=None):
    """ description:
            removes all the watchers that are part of <ui_watcher_group>
            if <ui_watcher_group> is None it will remove all watchers

        usage:
            ui_utils.remove_watchers(ui_watcher_goup = "cts")

        tags:
            ui, android, watcher, remove
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    try:
        for watcher in ui_statics.watcher_list:
            if ui_watcher_group:
                if ui_watcher_group in ui_statics.watcher_list[watcher]['groups']:
                    uidevice.watchers.remove(watcher)
            else:
                uidevice.watchers.remove()
    except Exception as e:
        if "RPC" not in str(e.message) and "not connected" not in str(e.message) and "not attached" not in str(
                e.message):
            print "[ {0} ]: Watchers unregister due to lost adb connection exception: {1}".format(serial, e.message)
            raise
        else:
            print "[ {0} ]: Watchers could not be unregistered due to exception: {1}".format(serial, e.message)


def click_apps_entry(view_to_find, serial=None, app=True):
    """ description:
            performs click on an application from Apps page with
            auto scroll support
            if <app> = False it will search through widget pages

        usage:
            ui_utils.click_apps_entry(app = True, **self.view_to_find)

        tags:
            ui, android, click, app, scroll
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    first_app_in_each_page = []

    while True:
        if uidevice(**view_to_find).exists:
            uidevice(**view_to_find).click.wait()
            return True

        first_app = uidevice(className="android.widget.TextView", instance=3)
        first_app_in_each_page.append(first_app.info)
        # apps_view = uidevice(className="android.view.View")

        maxx = uidevice.info['displaySizeDpX']
        maxy = uidevice.info['displaySizeDpY']
        # swipe horizontally
        uidevice.swipe(int(maxx) - 1, int(maxy / 2), 1, int(maxy / 2))
        # swipe vertically
        uidevice.swipe(int(maxx / 2), int(maxy / 2), int(maxx / 2), 1)

        first_app = uidevice(className="android.widget.TextView", instance=3)

        if dict_element_of_list(first_app_in_each_page, first_app.info):
            return False


def dict_element_of_list(my_dict_list, dict):
    """ description:
            Check if <dict> is part of dict list <my_dict_list>

        usage:
            ui_utils.dict_element_of_list(my_dict_list, dict)

        tags:
            ui, android, helper, dict, list
    """
    for el in my_dict_list:
        eq = True
        for key, val in el.iteritems():
            if val != dict[key] and type(val) != dict:
                eq = False
                break
        if eq:
            return True
    return False


def count_apps_pages(serial=None):
    """ description:
            return the number of Apps pages (not Widgets)
            you must be in first page of All Apps (this is true after
            ui_steps.press_all_apps)

        usage:
            ui_utils.count_apps_pages()

        tags:
            ui, android, swipe, apps
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    uidevice().swipe.left()
    widget_page = is_text_visible("Analog clock")

    result = 1
    while not widget_page:
        result += 1

        uidevice().swipe.left()
        widget_page = is_text_visible("Analog clock")

    return result


def is_switch_on(view_to_find, right_of=False, serial=None):
    """ description:
            return true if the switch in "ON"

        usage:
            ui_utils.is_switch_on(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/text", "instance":"1"})

        tags:
            ui, android, switch, enabled, disabled
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    if right_of:
        switch = uidevice(
            **view_to_find).right(className="android.widget.Switch")
    else:
        switch = uidevice(**view_to_find)
    if switch.info['text'] == "ON":
        return True
    else:
        return False


def is_text_visible(text_to_find, serial=None):
    """ description:
            return true if text is visible on screen
            If it's a list on screen, it also scrolls through it.

        usage:
            ui_utils.is_text_visible("text_to_find")

        tags:
            ui, android, text, visible
    """
    return is_view_visible(serial=serial, view_to_find={"text": text_to_find})


def is_view_visible(view_to_find, serial=None, click=False):
    """ description:
            return true if <view_to_find> is visible on screen.
            if <click> is True, it will click on the view before
            return.
            If it's a list on screen, it also scrolls through it.

        usage:
            ui_utils.is_text_visible("text_to_find")

        tags:
            ui, android, view, visible
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    if uidevice(resourceId="android:id/list").info['scrollable']:
        uidevice(scrollable=True).scroll.to(**view_to_find)

    if uidevice(**view_to_find).exists:
        if click:
            uidevice(**view_to_find).click.wait()
        return True
    else:
        return False


def is_view_visible_scroll_left(view_to_find, serial=None, click=False):
    """ description:
            return true if view is visible on screen.
            If <click> is True, it will click on the view before
            return.
            If there are multiple pages, it will scroll to them
            to the left.

        usage:
            ui_utils.is_text_visible_scroll_left("text_to_find")

        tags:
            ui, android , view, visible, swipe, scroll
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    while True:
        if uidevice(**view_to_find).exists:
            if click:
                uidevice(**view_to_find).click.wait()
            return True

        scr_dump_before = uidevice.dump()
        uidevice().swipe.left()
        time.sleep(1)
        scr_dump_after = uidevice.dump()

        if scr_dump_before == scr_dump_after:
            return False


def is_text_visible_scroll_left(text_to_find, serial=None):
    """ description:
            return true if the view with given text is visible on
            screen.
            If there are multiple pages, it will scroll to them to
            the left.

        usage:
            ui_utils.is_text_visible_scroll_left("App")

        tags:
            ui, android , text, visible, swipe, scroll
    """
    return is_view_visible_scroll_left(serial=serial, view_to_find={"text": text_to_find})


def is_enabled(view_to_find, serial=None, **kwargs):
    """ description:
            return true if element is enabled, false if disabled (grayed
            out in UI). Ignore 'enabled' parameter if you only want to
            check status. Use 'enabled' (True, False) to state the
            expected status

        usage:
            ui_utils.is_enabled(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/text"},
                    enabled = True)

        tags:
            ui, android, view, enabled, disabled
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    state = uidevice(**view_to_find).info['enabled']

    if 'enabled' in kwargs:
        enabled = kwargs['enabled']
        if enabled and state:
            return True
        elif enabled and not state:
            return False
        elif not enabled and state:
            return False
    return state


def is_radio_button_enabled(instance, serial=None):
    """ description:
            Check the actual state of a radio button.
            Return True if radio button checked or false if unchecked

        usage:
            ui_utils.is_radio_button_enabled(instance = 0)

        tags:
            ui, android, radio, enabled, disabled
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    radio_btn = uidevice(
        className="android.widget.RadioButton", instance=instance)
    return radio_btn.info['checked']


def is_checkbox_checked(view_to_find, serial=None, is_switch=False, relationship="sibling"):
    """ description:
            check the actual state of a checkbox

        usage:
            ui_utils.is_checkbox_checked(view_to_find = {"text":"view_text"})

        tags:
            ui, android, check, enabled, disabled
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    if is_switch:
        if relationship == "sibling":
            btn = uidevice(
                **view_to_find).sibling(className="android.widget.Switch")
        elif relationship == "right":
            btn = uidevice(
                **view_to_find).right(className="android.widget.Switch")
        elif relationship == "left":
            btn = uidevice(
                **view_to_find).left(className="android.widget.Switch")
    else:
        if relationship == "sibling":
            btn = uidevice(
                **view_to_find).sibling(className="android.widget.CheckBox")
        elif relationship == "right":
            btn = uidevice(
                **view_to_find).right(className="android.widget.CheckBox")
        elif relationship == "left":
            btn = uidevice(
                **view_to_find).left(className="android.widget.CheckBox")
    return btn.info['checked']


def move_slider(view_to_find, position=50, x_min_delta=16, x_max_delta=5, serial=None):
    """ description:
            move the slider to position which is a percentage
            the percentage is not very precise due to slider borders
            position = 100 means move slider to 100%
            x_min_delta, x_max_delta are offset for finding actual slider
                position

        usage:
            ui_utils.move_slider(view_to_find = {
                                        "className":'android.widget.SeekBar',
                                        "instance":0}, position = 30)

        tags:
            ui, android, slider, move
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    coords = uidevice(**view_to_find).info['visibleBounds']
    y_slider = (coords['top'] + coords['bottom']) / 2
    x_min = coords['left'] + x_min_delta
    x_max = coords['right'] - x_max_delta
    x_length = x_max - x_min

    target_pos = x_min + position / 100.0 * x_length
    uidevice(**view_to_find).drag.to(target_pos, y_slider, steps=100)


def get_resolution(serial=None):
    """ description:
            Gets the resolution of the screen

        usage:
            ui_utils.get_resolution()

        tags:
            ui, android, resolution
    """
    if serial:
        adb_connection = connection_adb(serial)
    else:
        adb_connection = connection_adb()
    prop_screen_dimension = adb_connection.get_prop('ro.sf.lcd_density_info')
    return prop_screen_dimension.split('px')[0].split(' x ')


def is_developer_options_enabled(serial=None):
    """ description:
            Check if developer options is enabled

        usage:
            ui_utils.is_developer_options_enabled()

        tags:
            ui, android, settings, developer
    """
    if serial:
        uidevice = ui_device(serial=serial)
        adb_connection = connection_adb(serial=serial)
    else:
        uidevice = ui_device()
        adb_connection = connection_adb()
    # uidevice.press.home()
    # uidevice(description = "Apps").click.wait()
    # uidevice(text = "Settings").wait.exists(timeout = 5000)
    # click_apps_entry(serial = serial,
    #                 view_to_find = {"text": "Settings"})
    # if uidevice(scrollable = True).exists:
    #    return uidevice(scrollable = True).scroll.to(text = "Developer
    # options")
    # else:
    #    return uidevice(text = "Developer options").exists

    # settings is launched through activity managert to avoid conflict in
    # launching setting for differ Andoroid OS(IVI and Non-IVI)
    adb_connection.run_cmd("am start -n com.android.settings/.Settings")
    if uidevice(text="System").exists:
        uidevice(text="System").click.wait()
    elif uidevice(scrollable=True).exists:
        uidevice(scrollable=True).scroll.to(text="System")
        if uidevice(text="System").exists:
            uidevice(text="System").click.wait()
        else:
            return False
    if uidevice(scrollable=True).exists:
        uidevice(scrollable=True).scroll.to(text="Developer options")
    return uidevice(text="Developer options").exists


def get_view_middle_coords(view_to_find, serial=None):
    """ description:
            Return the coordinates for the middle of the view

        usage:
            ui_utils.get_view_middle_coords()

        tags:
            ui, android, view, center
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    app = uidevice(**view_to_find)
    x_coord_r = app.info['bounds']['right']
    y_coord_b = app.info['bounds']['bottom']
    x_coord_l = app.info['bounds']['left']
    y_coord_t = app.info['bounds']['top']
    return (x_coord_r + x_coord_l) / 2, (y_coord_b + y_coord_t) / 2


def get_center_coords(bounds):
    """ description:
            Return if center coords from bounds dict

        usage:
            ui_utils.get_center_coords(obj.info['bounds'])

        tags: ui, android, center, coords
    """

    x = bounds['left'] + (bounds['right'] - bounds['left']) / 2
    y = bounds['top'] + (bounds['bottom'] - bounds['top']) / 2
    return (x, y)


def is_device_locked(serial=None):
    """ description:
            Check if the device is locked

        usage:
            ui_utils.is_device_locked()

        tags:
            ui, android, lock
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    return uidevice(resourceId="com.android.systemui:id/lock_icon").exists


def bxtp_car_locked(serial=None):
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    return uidevice(resourceId="com.android.systemui:id/user_name").exists


def is_device_pin_locked(serial=None):
    """ description:
            Check if the device is locked with pin

        usage:
            ui_utils.is_device_pin_locked()

        tags:
            ui, android, lock, pin
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    if uidevice(resourceId="android:id/message"):
        is_blocked = "You have incorrectly typed your PIN 5 times." in uidevice(
            resourceId="android:id/message").info["text"]
        return is_blocked

    return uidevice(resourceId="com.android.systemui:id/pinEntry").exists


def is_view_displayed(view_to_find, serial=None, wait_time=5000):
    """ description:
            Return True if <view_to_find> is visible on screen.

        usage:
            ui_utils.is_view_displayed(view_to_find = {"Text": "text"})

        tags:
            ui, android, view, displayed
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    return uidevice(**view_to_find).wait.exists(timeout=wait_time)


def check_google_account(serial=None):
    """ description:
            Check if a Google account is configured on the device

        usage:
            ui_utils.check_google_account()

        tags:
            ui, android, account, google
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    uidevice.press.home()
    uidevice(description="Apps").click.wait()
    uidevice(text="Settings").click.wait()
    uidevice(text="Accounts").click.wait()

    return_value = is_text_visible("Google")
    uidevice.press.recent()
    uidevice(text="Settings").swipe.right()
    uidevice.press.home()
    return return_value


def google_account_exists(serial=None, db="/data/system/users/0/accounts.db", table="accounts", where="1"):
    """ description:
            Check if a Google account is configured on the device from
            DB

        usage:
            ui_utils.google_account_exists()

        tags:
            ui, android, account, google, sqlite, db
    """
    return int(adb_utils.sqlite_count_query(serial=serial, db=db, table=table, where=where)) == 1


def get_view_text(view_to_find, serial=None):
    """ description:
            Get text information from a view. If view cannot be found,
            return False

        usage:
            ui_utils.get_view_text(view_to_find = {"resourceId":
                                                   "android:id/hours"})

        tags:
            ui, android, view, text
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    if uidevice(**view_to_find).exists:
        return uidevice(**view_to_find).info['text']
    else:
        return False


def view_exists(view_to_find, serial=None):
    """ description:
            Check if view exists

        usage:
            ui_utils.view_exists(view_to_find = {"resourceId":
                                                 "android:id/hours"})

        tags:
            ui, android, view
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    if not uidevice(scrollable=True).exists:
        return uidevice(**view_to_find).exists
    else:
        sx = uidevice.info['displayWidth'] / 2
        sy = uidevice.info['displayHeight'] / 2
        ex = sx
        ey = ex
        exists = False
        delta = 50
        one_direction = 0
        while one_direction < 2:
            ey = sy + delta
            a = uidevice.dump(compressed=False)
            uidevice.swipe(sx, sy, ex, ey, steps=10)
            uidevice.wait.idle()
            b = uidevice.dump(compressed=False)
            if uidevice(**view_to_find).exists:
                exists = True
                break
            if a == b:
                delta = -50
                one_direction += 1
        return exists


def wait_for_view(view_to_find, serial=None, wait_time=20000):
    """ description:
            Wait for specified view, <wait_time> miliseconds.
            Return False if view does not exist after <wait_time> ms.

        usage:
            ui_utils.wait_for_view(view_to_find = {"resourceId":
                                                   "android:id/hours"})

        tags:
            ui, android, view, wait, exists
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()
    if uidevice(**view_to_find).wait.exists(timeout=wait_time):
        return True
    else:
        return False


def is_homescreen(serial=None, sim_pin_enabled=False):
    """ description:
            Check homescreen is displayed

        usage:
            ui_utils.is_homescreen()

        tags:
            ui, android, homescreen
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    if sim_pin_enabled:
        return is_view_displayed(serial=serial, view_to_find={"resourceId": "com.android.systemui:id/simPinEntry"})

    views = [
        {"resourceId": "com.google.android.googlequicksearchbox:id/workspace"},
        {"resourceId":
            "com.google.android.googlequicksearchbox:id/search_edit_frame"},
        {"text": "Welcome"},
        {"text": "Encrypting"},
        {"resourceId": "com.android.launcher:id/search_button_container"},
        {"textContains": "has stopped."},
        {"resourceId": "com.android.systemui:id/user_name"},
        {"resourceId": "com.android.car.overview:id/gear_button"},
        {"resourceId": "com.android.car.overview:id/voice_button"},
        {"resourceId": "com.android.launcher3:id/btn_qsb_search"}
    ]
    for view in views:
        if adb_utils.is_power_state(serial=serial, state="OFF"):
            uidevice.wakeup()
        if uidevice(resourceId="com.android.systemui:id/lock_icon"):
            uidevice.swipe(200, 500, 200, 0, 10)
        if is_view_displayed(serial=serial, view_to_find=view):
            return True
    if is_view_displayed(serial=serial, view_to_find={"textContains": "To start Android, enter your"}):
        return None
    return False


def is_display_direction_landscape(serial=None):

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    if uidevice.info["displayWidth"] > uidevice.info["displayHeight"]:
        return True
    else:
        return False


def swipe_to_app_from_recent(view_to_find, serial=None):
    """ description:
            Swipe to the desired app from recent apps menu.

        usage:
            ui_utils.swipte_to_app_from_recent(view_to_find=
            {"text": "YouTube"})

        tags:
            ui, android, scroll,recent apps, swipe
    """

    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    x_center = uidevice.info['displayWidth'] / 2
    y_center = uidevice.info['displayHeight'] / 2

    while not uidevice(**view_to_find).wait.exists(timeout=1000):
        if (uidevice(resourceId="com.android.systemui:id/task_view_bar").count < 4):
            return False

        uidevice.swipe(
            sx=x_center, sy=y_center, ex=x_center, ey=y_center * 150 / 100, steps=10)
    return True


def search_object_in_direction(searched_object, direction_to_search, object_type, serial=None):
    """ description:
            Searches a text in a direction (up, down, left or right)

        usage:
            ui_utils.search_object_in_direction()

        tags:
            ui, android
    """
    if serial:
        uidevice = ui_device(serial=serial)
    else:
        uidevice = ui_device()

    if direction_to_search == "up":
        return uidevice(**searched_object).up(**object_type)

    elif direction_to_search == "down":
        return uidevice(**searched_object).down(**object_type)

    elif direction_to_search == "left":
        return uidevice(**searched_object).left(**object_type)

    elif direction_to_search == "right":
        return uidevice(**searched_object).right(**object_type)
