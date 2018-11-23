#!/usr/bin/env python

########################################################################
#
# @filename:    ui_utils.py
# @description: GUI tests helper functions
# @author:      ion-horia.petrisor@intel.com, silviux.l.andrei@intel.com
#
#######################################################################

from testlib.scripts.android.ui.automotive_O import ui_utils as parent_ui_utils
from testlib.base.abstract.abstract_step import inherite


@inherite(parent_ui_utils.click_apps_entry)
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


@inherite(parent_ui_utils.dict_element_of_list)
def dict_element_of_list():

    """ description:
            Check if <dict> is part of dict list <my_dict_list>

        usage:
            ui_utils.dict_element_of_list(my_dict_list, dict)

        tags:
            ui, android, helper, dict, list
    """
    pass


@inherite(parent_ui_utils.count_apps_pages)
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


@inherite(parent_ui_utils.is_switch_on)
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


@inherite(parent_ui_utils.is_text_visible)
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


@inherite(parent_ui_utils.is_view_visible)
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


@inherite(parent_ui_utils.is_view_visible_scroll_left)
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


@inherite(parent_ui_utils.is_text_visible_scroll_left)
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


@inherite(parent_ui_utils.is_enabled)
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


@inherite(parent_ui_utils.is_radio_button_enabled)
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


@inherite(parent_ui_utils.is_checkbox_checked)
def is_checkbox_checked():

    """ description:
            check the actual state of a checkbox

        usage:
            ui_utils.is_checkbox_checked(view_to_find = {"text":"view_text"})

        tags:
            ui, android, check, enabled, disabled
    """
    pass


@inherite(parent_ui_utils.move_slider)
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


@inherite(parent_ui_utils.get_resolution)
def get_resolution():

    """ description:
            Gets the resolution of the screen

        usage:
            ui_utils.get_resolution()

        tags:
            ui, android, resolution
    """
    pass


@inherite(parent_ui_utils.is_developer_options_enabled)
def is_developer_options_enabled():

    """ description:
            Check if developer options is enabled

        usage:
            ui_utils.is_developer_options_enabled()

        tags:
            ui, android, settings, developer
    """
    pass


@inherite(parent_ui_utils.get_view_middle_coords)
def get_view_middle_coords():

    """ description:
            Return the coordinates for the middle of the view

        usage:
            ui_utils.get_view_middle_coords()

        tags:
            ui, android, view, center
    """
    pass


@inherite(parent_ui_utils.is_device_locked)
def is_device_locked():

    """ description:
            Check if the device is locked

        usage:
            ui_utils.is_device_locked()

        tags:
            ui, android, lock
    """
    pass


@inherite(parent_ui_utils.bxtp_car_locked)
def bxtp_car_locked():
    pass


@inherite(parent_ui_utils.is_device_pin_locked)
def is_device_pin_locked():

    """ description:
            Check if the device is locked with pin

        usage:
            ui_utils.is_device_pin_locked()

        tags:
            ui, android, lock, pin
    """
    pass


@inherite(parent_ui_utils.is_view_displayed)
def is_view_displayed():
    """ description:
            Return True if <view_to_find> is visible on screen.

        usage:
            ui_utils.is_view_displayed(view_to_find = {"Text": "text"})

        tags:
            ui, android, view, displayed
    """
    pass


@inherite(parent_ui_utils.check_google_account)
def check_google_account():

    """ description:
            Check if a Google account is configured on the device

        usage:
            ui_utils.check_google_account()

        tags:
            ui, android, account, google
    """
    pass


@inherite(parent_ui_utils.google_account_exists)
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


@inherite(parent_ui_utils.get_view_text)
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


@inherite(parent_ui_utils.view_exists)
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


@inherite(parent_ui_utils.wait_for_view)
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


@inherite(parent_ui_utils.is_homescreen)
def is_homescreen():

    """ description:
            Check homescreen is displayed

        usage:
            ui_utils.is_homescreen()

        tags:
            ui, android, homescreen
    """
    pass


@inherite(parent_ui_utils.is_display_direction_landscape)
def is_display_direction_landscape():
    pass


@inherite(parent_ui_utils.swipe_to_app_from_recent)
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


@inherite(parent_ui_utils.search_object_in_direction)
def search_object_in_direction():
    """ description:
            Searches a text in a direction (up, down, left or right)

        usage:
            ui_utils.search_object_in_direction()

        tags:
            ui, android
    """
    pass
