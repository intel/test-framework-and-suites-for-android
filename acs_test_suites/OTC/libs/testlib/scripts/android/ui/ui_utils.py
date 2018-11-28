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


import time
from time import strftime

from testlib.utils.ui.uiandroid import UIDevice as ui_device
from testlib.utils.connections.adb import Adb as connection_adb
from testlib.scripts.android.ui import ui_statics
from testlib.base.abstract.abstract_step import devicedecorator


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
            if ui_handler_group in handler_value['groups'] and\
               handler_name not in uidevice.handlers():
                handler_function = my_handler(selector=handler_value['selector'],
                                              action_view=handler_value['action_view'],
                                              action=handler_value['action'],
                                              handler_name=handler_name,
                                              serial=serial)
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
    """description:
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
            if "RPC" not in str(e.message) and "not connected" \
                    not in str(e.message) and "not attached" not in str(e.message):
                print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                    "Registered watchers query exception due to lack of adb connectivity: {0}".format(e.message)
                raise
            else:
                print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                    "Watchers could not be queried due to exception: {}".format(e.message)

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
    remove_non_group_watchers(ui_watcher_groups=ui_watcher_groups.split(" "), serial=serial)
    for ui_watcher_group in ui_watcher_groups.split(" "):
        for watcher_name, watcher_value in ui_statics.watcher_list.iteritems():
            if ui_watcher_group in watcher_value['groups']:
                if watcher_name not in uidevice.watchers:
                    try:
                        if watcher_value['action'] == "click":
                            uidevice.watcher(watcher_name).\
                                when(**watcher_value['selector']).click(**watcher_value['action_view'])
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher {0} has been  registered for {1}.".format(watcher_name, serial)
                        elif watcher_value['action'] == "press":
                            uidevice.watcher(watcher_name).\
                                when(**watcher_value['selector']).press(watcher_value['action_view'])
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher {0} has been  registered for {1}.".format(watcher_name, serial)
                        else:
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Invalid watcher action: {0}".format(watcher_value['action'])
                    except Exception as e:
                        if "RPC" not in str(e.message) and "not connected" not in str(e.message) and "not attached" \
                                not in str(e.message):
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + \
                                "Watcher registration exception due to lack of adb connectivity: {0}".\
                                format(e.message)
                            raise
                        else:
                            print strftime("%d/%m %X.%S0 ", time.localtime()) + "Watcher {} could not be registered " \
                                "due to exception: {}".format(watcher_name, e.message)


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
                if watcher in ui_statics.watcher_list.keys() and \
                        ui_watcher_group in ui_statics.watcher_list[watcher]['groups']:
                    break
                else:
                    found = False
            if not found:
                uidevice.watchers.remove(watcher)
    except Exception as e:
        if "RPC" not in str(e.message) and "not connected" \
                not in str(e.message) and "not attached" not in str(e.message):
            print "[ {0} ]: Remove non-group watchers due to lost adb connection exception: {1}".\
                format(serial, e.message)
            raise
        else:
            print "[ {0} ]: Non group watchers could not be unregistered due to exception: {1}".\
                format(serial, e.message)


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
        if ui_watcher_group:
            for watcher in ui_statics.watcher_list:
                if ui_watcher_group in ui_statics.watcher_list[watcher]['groups']:
                    uidevice.watchers.remove(watcher)
        else:
            uidevice.watchers.remove()
    except Exception as e:
        if "RPC" not in str(e.message) and "not connected" not in str(e.message) and "not attached" \
                not in str(e.message):
            print "[ {0} ]: Watchers unregister due to lost adb connection exception: {1}".\
                format(serial, e.message)
            raise
        else:
            print "[ {0} ]: Watchers could not be unregistered due to exception: {1}".format(serial, e.message)


@devicedecorator
def click_apps_entry():

    """ description:
            performs click on an application from Apps page with
            auto scroll support
            if <app> = False it will search through widget pages

        usage:
            ui_utils.click_apps_entry(app = True, **self.view_to_find)

        tags:
            ui, android, click, app, scroll
    """
    pass


@devicedecorator
def dict_element_of_list():

    """ description:
            Check if <dict> is part of dict list <my_dict_list>

        usage:
            ui_utils.dict_element_of_list(my_dict_list, dict)

        tags:
            ui, android, helper, dict, list
    """
    pass


@devicedecorator
def count_apps_pages():

    """ description:
            return the number of Apps pages (not Widgets)
            you must be in first page of All Apps (this is true after
            ui_steps.press_all_apps)

        usage:
            ui_utils.count_apps_pages()

        tags:
            ui, android, swipe, apps
    """
    pass


@devicedecorator
def is_switch_on():

    """ description:
            return true if the switch in "ON"

        usage:
            ui_utils.is_switch_on(view_to_find = {"resourceId":
                    "com.intel.TelemetrySetup:id/text", "instance":"1"})

        tags:
            ui, android, switch, enabled, disabled
    """
    pass


@devicedecorator
def is_text_visible():

    """ description:
            return true if text is visible on screen
            If it's a list on screen, it also scrolls through it.

        usage:
            ui_utils.is_text_visible("text_to_find")

        tags:
            ui, android, text, visible
    """
    pass


@devicedecorator
def is_view_visible():

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
    pass


@devicedecorator
def is_view_visible_scroll_left():

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
    pass


@devicedecorator
def is_text_visible_scroll_left():

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
    pass


@devicedecorator
def is_enabled():

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
    pass


@devicedecorator
def is_radio_button_enabled():

    """ description:
            Check the actual state of a radio button.
            Return True if radio button checked or false if unchecked

        usage:
            ui_utils.is_radio_button_enabled(instance = 0)

        tags:
            ui, android, radio, enabled, disabled
    """
    pass


@devicedecorator
def is_checkbox_checked():

    """ description:
            check the actual state of a checkbox

        usage:
            ui_utils.is_checkbox_checked(view_to_find = {"text":"view_text"})

        tags:
            ui, android, check, enabled, disabled
    """


@devicedecorator
def move_slider():

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
    pass


@devicedecorator
def get_resolution():

    """ description:
            Gets the resolution of the screen

        usage:
            ui_utils.get_resolution()

        tags:
            ui, android, resolution
    """
    pass


@devicedecorator
def is_developer_options_enabled():

    """ description:
            Check if developer options is enabled

        usage:
            ui_utils.is_developer_options_enabled()

        tags:
            ui, android, settings, developer
    """
    pass


@devicedecorator
def get_view_middle_coords():

    """ description:
            Return the coordinates for the middle of the view

        usage:
            ui_utils.get_view_middle_coords()

        tags:
            ui, android, view, center
    """
    pass


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


@devicedecorator
def is_device_locked():
    """ description:
            Check if the device is locked

        usage:
            ui_utils.is_device_locked()

        tags:
            ui, android, lock
    """
    pass


@devicedecorator
def bxtp_car_locked():
    pass


@devicedecorator
def is_device_pin_locked():
    """ description:
            Check if the device is locked with pin

        usage:
            ui_utils.is_device_pin_locked()

        tags:
            ui, android, lock, pin
    """
    pass


@devicedecorator
def is_view_displayed():

    """ description:
            Return True if <view_to_find> is visible on screen.

        usage:
            ui_utils.is_view_displayed(view_to_find = {"Text": "text"})

        tags:
            ui, android, view, displayed
    """
    pass


@devicedecorator
def check_google_account():

    """ description:
            Check if a Google account is configured on the device

        usage:
            ui_utils.check_google_account()

        tags:
            ui, android, account, google
    """
    pass


@devicedecorator
def google_account_exists():

    """ description:
            Check if a Google account is configured on the device from
            DB

        usage:
            ui_utils.google_account_exists()

        tags:
            ui, android, account, google, sqlite, db
    """
    pass


@devicedecorator
def get_view_text():

    """ description:
            Get text information from a view. If view cannot be found,
            return False

        usage:
            ui_utils.get_view_text(view_to_find = {"resourceId":
                                                   "android:id/hours"})

        tags:
            ui, android, view, text
    """
    pass


@devicedecorator
def view_exists():

    """ description:
            Check if view exists

        usage:
            ui_utils.view_exists(view_to_find = {"resourceId":
                                                 "android:id/hours"})

        tags:
            ui, android, view
    """
    pass


@devicedecorator
def wait_for_view():

    """ description:
            Wait for specified view, <wait_time> miliseconds.
            Return False if view does not exist after <wait_time> ms.

        usage:
            ui_utils.wait_for_view(view_to_find = {"resourceId":
                                                   "android:id/hours"})

        tags:
            ui, android, view, wait, exists
    """
    pass


@devicedecorator
def is_homescreen():

    """ description:
            Check homescreen is displayed

        usage:
            ui_utils.is_homescreen()

        tags:
            ui, android, homescreen
    """
    pass


@devicedecorator
def is_display_direction_landscape():
    pass


@devicedecorator
def swipe_to_app_from_recent():

    """ description:
            Swipe to the desired app from recent apps menu.

        usage:
            ui_utils.swipte_to_app_from_recent(view_to_find=
            {"text": "YouTube"})

        tags:
            ui, android, scroll,recent apps, swipe
    """
    pass


@devicedecorator
def search_object_in_direction():
    """ description:
            Searches a text in a direction (up, down, left or right)

        usage:
            ui_utils.search_object_in_direction()

        tags:
            ui, android
    """
    pass
