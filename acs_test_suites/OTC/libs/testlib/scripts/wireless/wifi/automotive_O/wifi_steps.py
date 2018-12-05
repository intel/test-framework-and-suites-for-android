#!/usr/bin/env python
##
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
##

from testlib.base.base_step import BlockingError
from testlib.scripts.wireless.wifi.wifi_step import step as wifi_step
from testlib.scripts.android.ui import ui_steps
from testlib.scripts.android.ui import ui_utils
from testlib.scripts.wireless.wifi import wifi_utils
from testlib.scripts.android.adb import adb_utils
from testlib.scripts.wireless.wifi import wifi_steps

import time
import re


class install_WIFI_certificate(wifi_step):

    """ description:
            installs certificate from /sdcard/ with the password = <cert_pass>
            setting its name to <cert_name>

        usage:
            ui_steps.install_certificate(password = "1234")()

        tags:
            ui, android, click, button
    """

    def __init__(self, cert_pass="whatever", cert_name=None,
                 dut_pin=None, wait_time=5, **kwargs):
        wifi_step.__init__(self, **kwargs)
        if cert_pass:
            self.cert_pass = cert_pass
        else:
            self.cert_pass = "whatever"
        if cert_name:
            self.cert_name = cert_name
        else:
            self.cert_name = "TLS_certificate"
        if dut_pin:
            self.dut_pin = dut_pin
        else:
            self.dut_pin = "1234"
        if wait_time:
            self.wait_time = int(wait_time) * 1000
        else:
            self.wait_time = 5000

    def do(self):
        ui_steps.open_security_settings(serial=self.serial)()
        # In Android O, "Clear credentials" is available under "Encryption &
        # credentials"

        # if self.device_info.dessert == "O":
        #    ui_steps.click_button(serial=self.serial, view_to_find={
        #        "textContains": "Encryption"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "Encryption"})()

        if self.uidevice(className="android.widget.ListView",
                         scrollable=True).wait.exists(timeout=self.wait_time):
            self.uidevice(
                scrollable=True).scroll.to(
                textContains="Install certificate")
        if self.uidevice(className="android.support.v7.widget.RecyclerView",
                         scrollable=True).wait.exists(timeout=self.wait_time):
            self.uidevice(
                scrollable=True).scroll.to(
                textContains="Install certificate")
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "Install certificate"})()

        ui_steps.click_button(serial=self.serial,
                              view_to_find={"descriptionContains": "Show roots"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "B free"})()
        if self.uidevice(className="android.widget.ListView",
                         scrollable=True).wait.exists(timeout=self.wait_time):
            self.uidevice(scrollable=True).scroll.to(text="client.p12")
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": "client.p12"},
                              view_to_check={"textContains": "OK"})()

        if adb_utils.is_virtual_keyboard_on(serial=self.serial):
            ui_steps.press_back(serial=self.serial)()
        ui_steps.edit_text(serial=self.serial,
                           view_to_find={"resourceId":
                                         "com.android.certinstaller:id/credential_password"},
                           value=self.cert_pass,
                           is_password=True)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "OK"})()
        ui_steps.edit_text(serial=self.serial,
                           view_to_find={"resourceId":
                                         "com.android.certinstaller:id/credential_name"},
                           value=self.cert_name)()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "VPN and apps"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "Wi-Fi"},
                              view_to_check={"textContains": "Wi-Fi"})()
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"textContains": "OK"})()
        if self.uidevice(
                resourceId="com.android.settings:id/password_entry").wait.exists(timeout=self.wait_time):
            ui_steps.edit_text(serial=self.serial,
                               view_to_find={"resourceId":
                                             "com.android.settings:id/password_entry"},
                               value=self.dut_pin,
                               is_password=True)()
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"textContains": "Continue"})()

    def check_condition(self):
        return ui_steps.wait_for_view_with_scroll(serial=self.serial,
                                                  view_to_find={"text": "Clear credentials",
                                                                "enabled": "true"})()


class open_wifi_settings(wifi_step):

    """ description:
            Opens the WiFi Settings page using an intent or UI.

        usage:
            wifi_steps.open_wifi_settings(serial=self.serial)()

        tags:
            ui, android, settings, wifi, intent
    """

    def __init__(self, use_adb=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.use_adb = use_adb

    def do(self):
        clean_command = "pm clear com.android.settings"
        self.process = self.adb_connection.run_cmd(command=clean_command,
                                                   ignore_error=False,
                                                   timeout=10,
                                                   mode="sync")

        if self.use_adb is True:
            open_command = "am start -a android.intent.action.MAIN -n com.android.settings/.wifi.WifiSettings"
            self.process = self.adb_connection.run_cmd(command=open_command,
                                                       ignore_error=False,
                                                       timeout=10,
                                                       mode="sync")
        else:
            ui_steps.open_settings(serial=self.serial)()
            time.sleep(3)
            ui_steps.click_button(
                serial=self.serial, view_to_find={
                    "text": "Network & Internet"}, optional=True)()
            time.sleep(5)
            ui_steps.click_button(
                serial=self.serial, view_to_find={
                    "textMatches": "Wi.Fi"}, view_to_check={
                    "textMatches": "Wi.Fi"})()

    def check_condition(self):
        error_strings = [": not found", "Error"]
        output = self.process.stdout.read()
        for error in error_strings:
            if error in output:
                print "Error:"
                print output
                return False
        return True


class forget_wifi_network(wifi_step):

    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """

    ap_name = None

    def __init__(self, ap_name, security=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ap_name = ap_name
        self.set_passm(self.ap_name)
        self.set_errorm("", self.ap_name)
        self.security = security

    def do(self):
        if wifi_utils.is_known_AP(ap_name=self.ap_name,
                                  serial=self.serial,
                                  device=self.device_info):
            ui_steps.click_button(
                serial=self.serial,
                view_to_find={"textContains": self.ap_name},
                view_to_check=self.device_info.wifi_saved_network_forget_btn_id)()
            ui_steps.click_button(
                serial=self.serial,
                view_to_find=self.device_info.wifi_saved_network_forget_btn_id,
            )()

        else:
            self.set_passm(self.ap_name + " is already unknown.")

    def check_condition(self):
        return not wifi_utils.is_known_AP(ap_name=self.ap_name,
                                          serial=self.serial,
                                          device=self.device_info, security=self.security)


class forget_wifi(wifi_step):

    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """

    ap_name = None

    def __init__(self, ap_name, security=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ap_name = ap_name
        self.set_passm(self.ap_name)
        self.set_errorm("", self.ap_name)
        self.security = security

    def do(self):
        if wifi_utils.is_known_AP(ap_name=self.ap_name,
                                  serial=self.serial,
                                  device=self.device_info):
            ui_steps.click_button(
                serial=self.serial,
                view_to_find={"textContains": self.ap_name},
                view_to_check=self.device_info.wifi_saved_network_forget_btn_id)()
            ui_steps.click_button(
                serial=self.serial,
                view_to_find=self.device_info.wifi_saved_network_forget_btn_id,
            )()

        else:
            self.set_passm(self.ap_name + " is already unknown.")

    def check_condition(self):
        return True


class check_connection_info(wifi_step):
    """ description:
            Check the WiFi connection information.

        usage:
            wifi_steps.check_connection_info(SSID = "ddwrt", Security='WPA-PSK')()

            Use <parama_name>="None" to expect the setting not to be present on DUT.

            Example of possible values for all supported parameters:
            {'DHCP_server': '192.168.1.1',
             'DNS_addresses': '8.8.8.8,8.8.4.4',
             'Frequency': '2437MHz',
             'Gateway': '192.168.1.1',
             'Link_speed': '65Mbps',
             'MAC': 'dc:85:de:b9:5c:db',
             'SSID': 'Android Core QA',
             'Security': 'WPA2-PSK',
             'group_cipher': 'TKIP',
             'ip_address': '192.168.1.122',
             'p2p_device_address': 'de:85:de:b9:5c:db',
             'pairwise_cipher': 'CCMP',
             'state': 'CONNECTED/CONNECTED'}

        tags:
            android, settings, wifi
    """

    def __init__(self, state=None, SSID=None, Link_speed=None, Frequency=None,
                 Security=None, group_cipher=None, pairwise_cipher=None,
                 ip_address=None, Gateway=None, MAC=None, p2p_device_address=None,
                 DHCP_server=None, DNS_addresses=None, timeout=0, regex=False, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.params = {'DHCP_server': DHCP_server,
                       'DNS_addresses': DNS_addresses,
                       'Frequency': Frequency,
                       'Gateway': Gateway,
                       'Link_speed': Link_speed,
                       'MAC': MAC,
                       'SSID': SSID,
                       'Security': Security,
                       'ip_address': ip_address,
                       'p2p_device_address': p2p_device_address,
                       'state': state,
                       'pairwise_cipher': pairwise_cipher,
                       'group_cipher': group_cipher}
        self.timeout = timeout
        self.regex = regex

    def do(self):
        # get the wifi dumpsys: adb shell "dumpsys wifi"
        wifi_conf = self.adb_connection.parse_cmd_output("dumpsys wifi")
        self.wifi_info = wifi_utils.get_connection_info(wifi_conf)

    def check_condition(self):
        while self.timeout > -1:
            outcome = True
            error_msg = ""
            for param_name in self.params.keys():
                if self.params[param_name] is not None:
                    if self.wifi_info[param_name] == "UNKNOWN/IDLE":
                        if self.params[param_name] == "CONNECTED/CONNECTED":
                            outcome = False
                    elif self.params[param_name] == "None":
                        if self.wifi_info[param_name] is not None:
                            outcome = False
                            error_msg = error_msg + "wrong '{0}' parameter. Expected '{1}',"\
                                .format(param_name, self.params[param_name]) +\
                                " but actual value is '{0}'\n".format(
                                    self.wifi_info[param_name])

                    elif not self.regex:
                        if self.params[param_name] != self.wifi_info[param_name]:
                            outcome = False
                            error_msg = error_msg + "wrong '{0}' parameter. Expected '{1}',"\
                                .format(param_name, self.params[param_name]) +\
                                " but actual value is '{0}'\n".format(
                                    self.wifi_info[param_name])
                    else:
                        m = re.search(
                            self.params[param_name],
                            self.wifi_info[param_name])

                        if m is None:
                            outcome = False
                            error_msg = error_msg + "wrong '{0}' parameter. Expected '{1}',"\
                                .format(param_name, self.params[param_name]) +\
                                " but actual value is '{0}'\n".format(
                                    self.wifi_info[param_name])

            if outcome:
                break
            # print connection info in case check fails
            print "wifi connection info : \n", self.wifi_info
            self.timeout -= 2
            time.sleep(2)
            if self.timeout > -1:
                wifi_conf = self.adb_connection.parse_cmd_output(
                    "dumpsys wifi")
                self.wifi_info = wifi_utils.get_connection_info(wifi_conf)
        self.set_errorm("", error_msg)
        return outcome


class set_wifi_state(wifi_step):
    """
    Description: Turns Wifi on or off from command lineDefault value for the
            state is ON.
        usage:
            wifi_steps.set_wifi_state(state = "OFF")()

        tags:
            adb, android, wifi
    """

    def __init__(self, state="ON", use_adb=False,
                 open_wifi_settings=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.state = state
        self.use_adb = use_adb
        self.open_wifi_settings = open_wifi_settings
        self.set_passm("Setting WiFi state to " + self.state)

    def do(self):
        if self.state == "ON":
            wifi_state = "enable"
        else:
            wifi_state = "disable"
        if self.open_wifi_settings:
            wifi_steps.open_wifi_settings(serial=self.serial, use_adb=False)()
        current_wifi_state = wifi_utils.check_wifi_state_on(serial=self.serial)
        if self.state == "ON":
            if current_wifi_state:
                message = "wifi state is already ON ,hence no action is performed"
                self.set_passm(message)
        else:
            if not current_wifi_state:
                message = "wifi state is already OFF ,hence no action is performed"
                self.set_passm(message)

        if self.use_adb:
            clean_command = "pm clear com.android.settings"
            self.process = self.adb_connection.run_cmd(command=clean_command,
                                                       ignore_error=False,
                                                       timeout=10,
                                                       mode="sync")
            if self.state == "ON":
                if not current_wifi_state:
                    message = "wifi is turned ON"
                    self.set_passm(message)
                    self.adb_connection.parse_cmd_output("svc wifi {}".format(wifi_state),
                                                         dont_split=True)
            else:
                if current_wifi_state:
                    message = "wifi is turned OFF"
                    self.set_passm(message)
                    self.adb_connection.parse_cmd_output("svc wifi {}".format(wifi_state),
                                                         dont_split=True)

            # self.adb_connection.parse_cmd_output("am start -n"
            #                " com.android.settings/.wifi.WifiStatusTest",
            #                dont_split=True)
        else:

            if self.state == "ON":
                if not current_wifi_state:
                    message = "wifi is turned ON"
                    self.set_passm(message)
                    ui_steps.click_button(serial=self.serial,
                                          view_to_find={
                                              "resourceId": "com.android.settings:id/switch_text"},
                                          view_to_check={"textContains": self.state})()
            else:
                if current_wifi_state:
                    message = "wifi is turned OFF"
                    self.set_passm(message)
                    ui_steps.click_button(serial=self.serial,
                                          view_to_find={
                                              "resourceId": "com.android.settings:id/switch_text"},
                                          view_to_check={"textContains": self.state})()

            # self.adb_connection.parse_cmd_output("am start -n"
            #                " com.android.settings/.wifi.WifiStatusTest",
            #                dont_split=True)

    def check_condition(self):
        # if self.state == "ON":
        #     text_to_find = "Enabled"
        #     self.adb_connection.parse_cmd_output("echo 10 > /proc/net/rtl8723bs/log_level",
        #                 dont_split=True, ignore_error=True)
        # else:
        #     text_to_find = "Disabled"
        # ## TODO: investiagate alternate verification possibility: without UI
        # ret_value = False
        # for counter in range(5):
        #     ui_steps.wait_for_view(view_to_find = {"textContains":"Wi-Fi state:"},
        #                    timeout = 5000,
        #                    serial = self.serial)()
        #     if self.uidevice(text="Wi-Fi state:").right(text=text_to_find):
        #         ret_value = True
        #         break
        #     time.sleep(1)
        # if ret_value == False:
        #     print "'{}' not found in com.android.settings/.wifi.WifiStatusTest.".format(text_to_find)
        # return ret_value

        # below wifi utility returns True when wifi in "ON" else False
        for counter in range(5):
            time.sleep(1)
            status = wifi_utils.check_wifi_state_on(self.serial)
            if self.state == "ON":
                self.step_data = True if status else False
            else:
                if status:
                    self.step_data = False
                else:
                    self.step_data = True
            return self.step_data


# Create an alias for set_from_wifi_settings to set_wifi
# set_wifi = set_from_wifi_settings
set_wifi = set_wifi_state


class wait_until_connected(wifi_step):
    """ description: Waits until the device is connected to a wifi network.
    """

    def __init__(self, timeout=120, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.timeout = timeout
        self.connected = 'CONNECTED/CONNECTED'
        self.wifi_info = None

    def do(self):
        self.resolution = wait_for_state(
            serial=self.serial,
            state=self.connected,
            timeout=self.timeout)()

    def check_condition(self):
        return self.resolution


class wait_for_state(wifi_step):
    """ description: Waits until the wifi is in the desired state.
    """

    def __init__(self, state='CONNECTED/CONNECTED', timeout=150, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.timeout = timeout
        self.state = state
        self.wifi_info = None

    def do(self):
        while self.timeout > 0:
            wifi_conf = self.adb_connection.parse_cmd_output("dumpsys wifi")
            self.wifi_info = wifi_utils.get_connection_info(wifi_conf)
            # check the state when both parts are provided
            if "/" in self.state:
                if self.wifi_info['state'] == self.state:
                    break
            # check only the first part of the state (CONNECTED/DISCONNECTED)
            else:
                if self.wifi_info['state'].split("/")[0] == self.state:
                    break

            time.sleep(2)
            self.timeout -= 1

    def check_condition(self):
        if self.timeout > 0:
            self.step_data = True
            return True
        else:
            self.step_data = False
            return False


class scan_and_check_ap(wifi_step):

    """ description:
            Check weather an AP SSID can be found by a Wi-Fi scan.

            NOTE: Carefull when looking for an AP SSID that is saved as it will
            show up even when the AP SSID is not visible or in range!

            <option> parameter selects the type of scann:
                - "ser_off" - by setting wifi off and then on
                - "refresh" - by

        usage:
            wifi_steps.scan_and_check_ap("MyAP", should_exist=True)()

        tags:
            ui, android, ssid, scan
    """

    def __init__(self, ap, option="set_off", trycount=10,
                 open_wifi=None, should_exist=True, **kwargs):
        self.ap = ap
        self.option = option
        self.trycount = trycount
        self.should_exist = should_exist
        self.open_wifi = open_wifi

        wifi_step.__init__(self, **kwargs)
        self.set_passm(str(ap) + " scanned")
        if self.should_exist:
            self.set_errorm(
                "", "Could not find AP SSID after scan: " + self.ap)
        else:
            self.set_errorm(
                "",
                "AP SSID was found by scan when it should not: " +
                self.ap)

        self.exclude_ap_names = ["Wi?Fi", "On"]
        if self.ap in self.exclude_ap_names:
            print "WARNING: You are using bad AP names for testing: " + \
                ",".join(self.exclude_ap_names)
        self.found_ap = None

    def do(self):
        # Making sure we are in Settings - Wi-Fi menu and turning on/off-on
        # Wi-Fi (in order to force a scan)
        if self.option == "set_off":
            wifi_steps.set_wifi(serial=self.serial, state="OFF")()
            time.sleep(1)
            wifi_steps.set_wifi(serial=self.serial, state="ON")()
        elif self.option == "refresh":
            if not self.open_wifi:
                wifi_steps.open_wifi_settings(serial=self.serial)()
            # Click "More"
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"descriptionContains": "More"},
                                  view_to_check={"textContains": "Refresh"})()

            # Click "Refresh"
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"textContains": "Refresh"},
                                  view_to_check={"textContains": "Refresh"},
                                  view_presence=False)()
        else:
            raise BlockingError("Invalid scanning option: {}\n".format(self.option) +
                                "Should be on of: ['set_off', 'refresh']")
        if not self.open_wifi:
            wifi_steps.open_wifi_settings(serial=self.serial)()
        time.sleep(1)
        # Checking if the AP SSID is in the current view. We do this every
        # second for self.trycount seconds.
        self.found_ap = self.uidevice(text=self.ap).wait.exists(timeout=1000)
        iteration = 0
        while not self.found_ap and iteration < self.trycount:
            if self.uidevice(scrollable=True).exists:
                self.found_ap = self.uidevice(
                    scrollable=True).scroll.to(
                    text=self.ap)

            iteration += 1
            time.sleep(1)

    def check_condition(self):
        return (self.found_ap == self.should_exist)


class clear_saved_networks(wifi_step):

    """ description:
            Clear all saved networks. Can remove a maximum of <max_entries> networks.

        usage:
            wifi_steps.clear_saved_networks(serial=self.serial)()
            OR
            wifi_steps.clear_saved_networks(max_entries=10)()

        tags:
            ui, android, ssid, clear, wifi
    """

    def __init__(self, max_entries=20, use_adb=False,
                 open_wifi_setting=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.max_entries = max_entries
        self.steppassed = False
        self.open_wifi_settings = open_wifi_settings
        self.use_adb = use_adb

    def do(self):
        if self.open_wifi_settings:
            # Turn on Wi-Fi and go to Settings - Wi-Fi menu and Turn
            wifi_steps.set_wifi(
                serial=self.serial,
                state="ON",
                use_adb=self.use_adb)()
            wifi_steps.open_wifi_settings(
                serial=self.serial, use_adb=self.use_adb)()

        # Click the More button
        if not ui_steps.click_button(serial=self.serial,
                                     view_to_find=self.device_info.wifi_more_options_id)():
            if self.uidevice(scrollable=True):
                self.uidevice(scrollable=True).scroll.toEnd()

        # Look for the 'Saved Networks' button.
        # If it exists, click it. If not, it means there are no saved Wi-Fi
        # networks.
        if self.uidevice(text="Saved networks").wait.exists(timeout=1000):
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"text": "Saved networks"},
                                  view_to_check={"text": "Saved networks"})()

            # Get the top saved network from the ListView
            while self.max_entries > 0:
                if not self.uidevice(**self.device_info.wifi_saved_networks_list_id)\
                    .child(**self.device_info.wifi_saved_networks_list_element_id)\
                        .wait.exists(timeout=1000):
                    break
                self.uidevice(**self.device_info.wifi_saved_networks_list_id)\
                    .child(**self.device_info.wifi_saved_networks_list_element_id)\
                    .click.wait()
                self.uidevice(
                    **self.device_info.wifi_saved_network_forget_btn_id).wait.exists(timeout=1000)
                if not ui_steps.click_button(serial=self.serial,
                                             view_to_find=self.device_info.wifi_saved_network_forget_btn_id,
                                             optional=True,
                                             scroll=False, view_to_check={"text": "Saved networks"})():
                    break

                '''ui_steps.click_button(serial=self.serial,
                                      view_to_find = self.device_info.wifi_saved_network_forget_btn_id,
                                      view_to_check = {"text":"Saved networks"})()

                self.max_entries -= 1
                '''
                if not ui_steps.click_button(serial=self.serial,
                                             view_to_find=self.device_info.wifi_saved_network_forget_btn_id,
                                             optional=True,
                                             scroll=False, view_to_check={"text": "Saved networks"})():
                    break
            # If we still have an entry in the list, the step is failed.
            if self.max_entries == 0:
                self.step_data = False
                self.set_errorm("", "Network still in 'Saved Networks' list.")
            else:
                self.step_data = True
        else:
            self.step_data = True

    def check_condition(self):
        return self.step_data


class set_wifi_security(wifi_step):

    def __init__(self, security, password=None, EAP_method=None, phase_2_auth=None, user_certificate=None,
                 identity=None, anonymous_identity=None, ca_certificate=None, clear_text_boxes=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.security = security
        self.password = password
        self.EAP_method = EAP_method
        self.phase_2_auth = phase_2_auth
        self.user_certificate = user_certificate
        self.identity = identity
        self.anonymous_identity = anonymous_identity
        self.ca_certificate = ca_certificate
        self.clear_text = clear_text_boxes
        self.step_data = False

    def do(self):
        # Complete security fields
        if self.security:
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "className": "android.widget.Spinner",
                                      "resourceId": "com.android.settings:id/security"},
                                  view_to_check={"textContains": self.security})()
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "textContains": self.security},
                                  view_to_check={"className": "android.widget.Spinner",
                                                 "resourceId": "com.android.settings:id/security"})()

            if self.password:
                ui_steps.edit_text(serial=self.serial, clear_text=self.clear_text,
                                   view_to_find={
                                       "resourceId": "com.android.settings:id/password"},
                                   value=self.password,
                                   scroll=True,
                                   is_password=True)()

            if self.EAP_method:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/method"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.EAP_method},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/method"})()

            if self.phase_2_auth:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/phase2"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.phase_2_auth},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/phase2"})()

            if self.EAP_method and not self.user_certificate and \
               ui_utils.is_view_displayed(serial=self.serial,
                                          view_to_find={"resourceId": "com.android.settings:id/ca_cert"}):
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/ca_cert"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.device_info.wifi_ca_certificate_none_id},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/ca_cert"})()

            if self.user_certificate:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/user_cert"})()

                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.user_certificate},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/user_cert"})()

            if self.ca_certificate:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/ca_cert"})()

                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.ca_certificate},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/ca_cert"})()

            if self.identity:
                ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                   view_to_find={
                                       "resourceId": "com.android.settings:id/identity"},
                                   value=self.identity,
                                   is_password=False)()

            if self.anonymous_identity:
                ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                   view_to_find={
                                       "resourceId": "com.android.settings:id/anonymous"},
                                   value=self.anonymous_identity,
                                   is_password=False)()

            if self.device_info.dessert in ['N'] and self.EAP_method == "TLS" and \
                    ui_utils.is_view_displayed(serial=self.serial,
                                               view_to_find={"resourceId": "com.android.settings:id/ca_cert"}):
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/ca_cert"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": self.device_info.wifi_ca_certificate_none_id},
                                      view_to_check={"className": "android.widget.Spinner",
                                                     "resourceId": "com.android.settings:id/ca_cert"})()

        self.step_data = True

    def check_condition(self):
        return self.step_data


class set_wifi_advanced_options(wifi_step):

    def __init__(self, proxy=None, proxy_pac_url=None, proxy_hostname=None, proxy_port=None, proxy_bypass=None,
                 ip_settings=None, ip_address=None, gateway=None,
                 network_prefix_length=None, dns1=None, dns2=None, clear_text_boxes=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.proxy = proxy
        self.proxy_pac_url = proxy_pac_url
        self.proxy_hostname = proxy_hostname
        self.proxy_port = proxy_port
        self.proxy_bypass = proxy_bypass
        self.ip_settings = ip_settings
        self.ip_address = ip_address
        self.gateway = gateway
        self.network_prefix_length = network_prefix_length
        self.dns1 = dns1
        self.dns2 = dns2
        self.clear_text = clear_text_boxes
        self.step_data = False

        self.advanced = (self.proxy or self.ip_settings) is not None

    def do(self):
        # If we want to set 'proxy' or 'ip settings', we need to check the
        # 'Advanced" checkbox.
        if self.advanced:
            ui_steps.click_checkbox_button(serial=self.serial,
                                           view_to_find={
                                               "resourceId": "com.android.settings:id/wifi_advanced_togglebox"},
                                           state="ON",
                                           relationship="sibling")()

            # Complete the proxy settings
            if self.proxy:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId":
                                                    "com.android.settings:id/proxy_settings"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"textContains": self.proxy})()

                if self.proxy_hostname:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/proxy_hostname"},
                                       value=self.proxy_hostname,
                                       is_password=False)()

                if self.proxy_port:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/proxy_port"},
                                       value=self.proxy_port,
                                       is_password=False)()

                if self.proxy_bypass:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/proxy_exclusionlist"},
                                       value=self.proxy_bypass,
                                       is_password=False)()

                if self.proxy_pac_url:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/proxy_pac"},
                                       value=self.proxy_pac_url,
                                       is_password=False)()

            # Complete the IP Settings
            if self.ip_settings:
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"className": "android.widget.Spinner",
                                                    "resourceId": "com.android.settings:id/ip_settings"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={"textContains": self.ip_settings})()

                if self.gateway:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/gateway"},
                                       value=self.gateway,
                                       is_password=False)()

                if self.network_prefix_length:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/network_prefix_length"},
                                       value=self.network_prefix_length,
                                       is_password=False)()

                if self.dns1:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/dns1"},
                                       value=self.dns1,
                                       is_password=False)()

                if self.dns2:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/dns2"},
                                       value=self.dns2,
                                       is_password=False)()

                if self.ip_address:
                    ui_steps.edit_text(scroll=True, clear_text=self.clear_text, serial=self.serial,
                                       view_to_find={
                                           "resourceId": "com.android.settings:id/ipaddress"},
                                       value=self.ip_address,
                                       is_password=False)()
        self.step_data = True

    def check_condition(self):
        return self.step_data


class add_network(wifi_step):

    """ description:
            Add a Wi-Fi network.

        usage:
            wifi_steps.add_network(ssid='MyAP', security='None')()
            wifi_steps.add_network(ssid='MyAP', security='WEP', password='awsomepassword123')()

        valid_config - it will check weather the Save button is available to click

        tags:
            ui, android, ssid, wifi
    """

    def __init__(self, ssid, security, password=None, EAP_method=None, phase_2_auth=None, user_certificate=None,
                 ca_certificate=None, identity=None, anonymous_identity=None,
                 proxy=None, proxy_pac_url=None, proxy_hostname=None, proxy_port=None, proxy_bypass=None,
                 ip_settings=None, ip_address=None, gateway=None, network_prefix_length=None, dns1=None, dns2=None,
                 valid_config=True, apply_config=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ssid = ssid
        self.security = security
        self.password = password
        self.EAP_method = EAP_method
        self.phase_2_auth = phase_2_auth
        self.user_certificate = user_certificate
        self.ca_certificate = ca_certificate
        self.identity = identity
        self.anonymous_identity = anonymous_identity
        self.proxy = proxy
        self.proxy_pac_url = proxy_pac_url
        self.proxy_hostname = proxy_hostname
        self.proxy_port = proxy_port
        self.proxy_bypass = proxy_bypass
        self.ip_settings = ip_settings
        self.ip_address = ip_address
        self.gateway = gateway
        self.network_prefix_length = network_prefix_length
        self.dns1 = dns1
        self.dns2 = dns2
        self.valid_config = valid_config
        self.apply_config = apply_config

    def wrap_do(self):
        # Go to Settings - Wi-Fi menu and turn on Wi-Fi
        wifi_steps.set_wifi(serial=self.serial, state="ON")()
        wifi_steps.open_wifi_settings(serial=self.serial)()

        # TODO: Implement steps in ui_steps for using spinners and check boxes?

        # Click "More"
        if self.device_info.dessert in ["L", "M"]:
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"descriptionContains": "More"},
                                  view_to_check={"textContains": "Add network"})()
        if self.device_info.dessert in ["N"]:
            ui_steps.wait_for_view_with_scroll(serial=self.serial, timeout=10000,
                                               view_to_find={
                                                   "resourceId": "android:id/icon_frame"},
                                               iterations=5)()

        # Click "Add network"
        ui_steps.click_button(serial=self.serial,
                              view_to_find={
                                  "textContains": "Add network"},
                              view_to_check={"textContains": "Network name"})()

        # Complete the SSID text field
        ui_steps.edit_text(serial=self.serial,
                           view_to_find={
                               "resourceId": "com.android.settings:id/ssid"},
                           value=self.ssid,
                           is_password=False)()

    def do(self):
        self.wrap_do()
        try:
            wifi_steps.set_wifi_security(serial=self.serial, security=self.security, password=self.password,
                                         EAP_method=self.EAP_method, phase_2_auth=self.phase_2_auth,
                                         user_certificate=self.user_certificate, identity=self.identity,
                                         anonymous_identity=self.anonymous_identity,
                                         ca_certificate=self.ca_certificate, clear_text_boxes=False)()
        except Exception:
            self.logger.debug("Install certificate again for TLS test retry")
            ui_steps.press_home(serial=self.serial)()
            wifi_steps.install_WIFI_certificate(
                serial=self.serial,
                cert_pass="whatever",
                cert_name="TLS_certificate",
                dut_pin=1234)()
            self.wrap_do()

            wifi_steps.set_wifi_advanced_options(serial=self.serial, proxy=self.proxy,
                                                 proxy_pac_url=self.proxy_pac_url, proxy_hostname=self.proxy_hostname,
                                                 proxy_port=self.proxy_port,
                                                 proxy_bypass=self.proxy_bypass, ip_settings=self.ip_settings,
                                                 ip_address=self.ip_address, gateway=self.gateway,
                                                 network_prefix_length=self.network_prefix_length,
                                                 dns1=self.dns1, dns2=self.dns2, clear_text_boxes=False)()

        # Click Save
        apply_config_btn = {
            "className": "android.widget.Button",
            "enabled": True}
        apply_config_btn.update(self.device_info.wifi_add_network_save_btn_id)
        if self.apply_config:
            if self.valid_config:
                if self.device_info.dessert != "O":
                    ui_steps.click_button(serial=self.serial,
                                          view_to_find=apply_config_btn,
                                          view_to_check={"descriptionContains": "More"})()
                else:
                    ui_steps.click_button(serial=self.serial,
                                          view_to_find=apply_config_btn,
                                          view_to_check=None)()
            else:
                apply_config_btn.update({"enabled": False})
                ui_steps.click_button(serial=self.serial,
                                      view_to_find=apply_config_btn)()
        else:
            ui_steps.click_button(serial=self.serial,
                                  view_to_find=apply_config_btn)()

        # Sometimes, the AP will not connected at once after the account has
        # been saved, so force to connect to the AP
        if self.apply_config:
            if self.uidevice(resourceId="android:id/title",
                             text=self.ssid).wait.exists(timeout=1000):
                self.uidevice(
                    resourceId="android:id/title",
                    text=self.ssid).click.wait()
                if self.uidevice(textMatches="^(?i)connect$").exists:
                    self.uidevice(textMatches="^(?i)connect$").click.wait()

    def check_condition(self):
        # If we made it here without errors, it means the step is passed.
        return True


class modify_network(wifi_step):

    """ description:
            Modify an existing Wi-Fi network.

        usage:
            wifi_steps.modify_network(ssid='MyAP', password='1234')()

        valid_config - it will check weather the Save button is available to click

        tags:
            ui, android, ssid, wifi
    """

    def __init__(self, ssid, password=None, proxy=None, proxy_pac_url=None, proxy_hostname=None, proxy_port=None,
                 proxy_bypass=None, ip_settings=None, ip_address=None, gateway=None, network_prefix_length=None,
                 dns1=None, dns2=None, valid_config=True, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ssid = ssid
        self.password = None
        self.proxy = proxy
        self.proxy_pac_url = proxy_pac_url
        self.proxy_hostname = proxy_hostname
        self.proxy_port = proxy_port
        self.proxy_bypass = proxy_bypass
        self.ip_settings = ip_settings
        self.ip_address = ip_address
        self.gateway = gateway
        self.network_prefix_length = network_prefix_length
        self.dns1 = dns1
        self.dns2 = dns2
        self.valid_config = valid_config

        self.clear_text = True
        self.advanced = (self.proxy or self.ip_settings) is not None
        self.ssid_view = {
            "textContains": self.ssid,
            "resourceId": "android:id/title"}
        self.modify_network_view = {
            "textContains": "Modify network",
            "resourceId": "android:id/title"}

    def do(self):
        # Go to Settings - Wi-Fi menu and turn on Wi-Fi
        wifi_steps.set_wifi(serial=self.serial, state="ON")()
        wifi_steps.open_wifi_settings(serial=self.serial)()

        # Scroll to find the SSID
        if self.uidevice(className="android.widget.ScrollView",
                         scrollable=True).wait.exists(timeout=1000):
            self.uidevice(scrollable=True).scroll.to(**self.ssid_view)

        # Long click the wifi SSID
        ui_steps.long_click(serial=self.serial,
                            view_to_find=self.ssid_view,
                            view_to_check=self.modify_network_view)()

        # Click Modify Network
        ui_steps.click_button(serial=self.serial,
                              view_to_find=self.modify_network_view,
                              view_to_check={"textContains": self.ssid})()

        if adb_utils.is_virtual_keyboard_on(serial=self.serial):
            ui_steps.press_back(serial=self.serial)()

        # Modify the password, if applicable
        if self.password:
            ui_steps.edit_text(serial=self.serial, clear_text=True,
                               view_to_find={
                                   "resourceId": "com.android.settings:id/password"},
                               value=self.password,
                               scroll=False,
                               is_password=True)()

        # Set the advanced options
        wifi_steps.set_wifi_advanced_options(serial=self.serial, proxy=self.proxy, proxy_pac_url=self.proxy_pac_url,
                                             proxy_hostname=self.proxy_hostname, proxy_port=self.proxy_port,
                                             proxy_bypass=self.proxy_bypass, ip_settings=self.ip_settings,
                                             ip_address=self.ip_address, gateway=self.gateway,
                                             network_prefix_length=self.network_prefix_length,
                                             dns1=self.dns1, dns2=self.dns2, clear_text_boxes=self.clear_text)()

        # Click Save
        if self.valid_config:
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"className": "android.widget.Button",
                                                "textMatches": "(?i)save", "enabled": True})()
        else:
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"className": "android.widget.Button",
                                                "textMatches": "(?i)save", "enabled": False})()

    def check_condition(self):
        # If we made it here without errors, it means the step is passed.
        return True


class ping_gateway(wifi_step):
    """
    Description:
                Pings the DUT gateway <trycount> times.
                Will fail if the packet loss is less then or equal to <target_percent>
    """

    def __init__(self, trycount=2, timeout=15, target_percent=50, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.trycount = trycount
        self.timeout = timeout
        self.target_percent = target_percent

    def do(self):
        wifi_conf = self.adb_connection.parse_cmd_output("dumpsys wifi")
        self.wifi_info = wifi_utils.get_connection_info(wifi_conf)
        (self.status, loss, ping_output) = wifi_utils.ping(ip=self.wifi_info['Gateway'], trycount=self.trycount,
                                                           target_percent=self.target_percent, timeout=self.timeout,
                                                           serial=self.serial)

        ip = self.wifi_info['Gateway']

        if loss:
            step_message = "=== pinging address " + \
                str(ip) + " lost " + str(loss) + "% out of " + \
                str(self.trycount) + " packets ==="
        else:
            step_message = "Could not determine loss percent. Ping output was: \" {} \"".\
                format(ping_output)

        self.set_passm(step_message)
        self.set_errorm("", step_message)

    def check_condition(self):
        return self.status


class ping_ip(wifi_step):
    """
    Description:
                Pings the IP for <trycount> times.
                It will fail if the packet loss is less then or equal to <target_percent>
    """

    def __init__(self, ip=None, trycount=2, timeout=15,
                 target_percent=50, negative=False, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ip = ip
        self.trycount = trycount
        self.timeout = timeout
        self.target_percent = target_percent
        self.negative = negative

    def do(self):
        if self.ip is not None:
            # run ping only if the destination ip address is valid
            (self.status, loss, ping_output) = wifi_utils.ping(ip=self.ip, trycount=self.trycount,
                                                               target_percent=self.target_percent,
                                                               timeout=self.timeout, serial=self.serial)
            if loss:
                step_message = "=== pinging address " + \
                    str(self.ip) + " lost " + str(loss) + "% out of " + \
                    str(self.trycount) + " packets ==="
            else:
                step_message = "Could not determine loss percent. Ping output was: \" {} \"".\
                    format(ping_output)
            self.set_passm(step_message)
            self.set_errorm("", step_message)
        else:
            step_message = 'Ping failure due to invalid destination IP address!!! ' \
                           'Check device connectivity!!! IP is: ' + \
                str(self.ip)
            self.set_errorm("", step_message)
            self.status = False
            self.negative = False  # in case of invalid destination IP,
            # ping_ip step should fail also for "negative" cases

    def check_condition(self):
        if self.negative:
            return not self.status
        return self.status


class find_available_ip(wifi_step):
    """
        returns the first IP that is available from a range of IPs

    """

    def __init__(self, ip_range=None, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.step_data = None
        self.ip_range = ip_range

    def do(self):
        if self.ip_range is None:
            self.ip_range = wifi_utils.get_ip_range(self.serial)
        if self.ip_range:
            start_ip = self.ip_range.split("_")[0]
            end_ip = self.ip_range.split("_")[1]
            current_ip = start_ip

            found = False

            while not found and current_ip != end_ip:
                if current_ip.split('.')[-1] != '255' and current_ip.split(
                        '.')[-1] != '0' and current_ip.split('.')[-1] != '1':
                    found = not wifi_utils.ping(
                        current_ip, trycount=1, serial=self.serial)[0]
                if not found:
                    current_ip = wifi_utils.int_to_ip(
                        wifi_utils.ip_to_int(current_ip) + 1)
            if found:
                self.step_data = current_ip
            return self.step_data
        else:
            step_message = 'Could not determine available IP addresses range! Check device connectivity!!!'
            self.set_errorm("", step_message)

    def check_condition(self):
        if self.step_data:
            return self.step_data
        else:
            return False


class check_network_information(wifi_step):
    """
    Description: Check the network information on device.
    """

    def __init__(self, ap_name, status=None, link_speed=None,
                 frequency=None, security=None, **kwargs):
        wifi_step.__init__(self, **kwargs)
        self.ap_name = ap_name

        self.params_to_check = {}
        if status is not None:
            self.params_to_check["Status"] = status
        if link_speed is not None:
            self.params_to_check["Link speed"] = link_speed
        if frequency is not None:
            self.params_to_check["Frequency"] = frequency
        if security is not None:
            self.params_to_check["Security"] = security

    def do(self):
        error_msg = ""
        self.decision = True
        wifi_steps.set_wifi(serial=self.serial, state="ON")()
        wifi_steps.open_wifi_settings(serial=self.serial)()

        # Click "More"
        ui_steps.click_button(serial=self.serial,
                              view_to_find={"text": self.ap_name},
                              view_to_check={"textContains": "Signal strength"})()

        for param in self.params_to_check.keys():
            if not self.uidevice(text=param).down(
                    textContains=self.params_to_check[param]):
                error_msg += "Parameter '{0}' has different value than expected '{1}'.\n".\
                             format(param, self.params_to_check[param])
                self.decision = False
        self.set_errorm("", error_msg)

    def check_condition(self):
        return self.decision
