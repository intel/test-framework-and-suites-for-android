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

from testlib.scripts.android.ui import ui_steps
from testlib.scripts.android.ui import ui_utils
from testlib.scripts.android.adb import adb_utils
from testlib.scripts.wireless.wifi.automotive_O import wifi_steps as parent_wifi_steps
from testlib.scripts.wireless.wifi import wifi_steps

import time


class install_WIFI_certificate(parent_wifi_steps.install_WIFI_certificate):
    """ description:
            installs certificate from /sdcard/ with the password = <cert_pass>
            setting its name to <cert_name>

        usage:
            ui_steps.install_certificate(password = "1234")()

        tags:
            ui, android, click, button
    """
    pass


class open_wifi_settings(parent_wifi_steps.open_wifi_settings):

    """ description:
            Opens the WiFi Settings page using an intent or UI.

        usage:
            wifi_steps.open_wifi_settings(serial=self.serial)()

        tags:
            ui, android, settings, wifi, intent
    """

    def __init__(self, use_adb=False, **kwargs):
        parent_wifi_steps.open_wifi_settings.__init__(
            self, use_adb=False, **kwargs)
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
                    "text": "Network & internet"}, optional=True)()
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


class forget_wifi_network(parent_wifi_steps.forget_wifi_network):
    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """
    pass


class forget_wifi(parent_wifi_steps.forget_wifi):
    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """
    pass


class check_connection_info(parent_wifi_steps.check_connection_info):
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
    pass


class set_wifi_state(parent_wifi_steps.set_wifi_state):
    """
    Description: Turns Wifi on or off from command lineDefault value for the
            state is ON.
        usage:
            wifi_steps.set_wifi_state(state = "OFF")()

        tags:
            adb, android, wifi
    """
    pass


set_wifi = set_wifi_state


class wait_until_connected(parent_wifi_steps.wait_until_connected):
    """ description: Waits until the device is connected to a wifi network.
    """
    pass


class wait_for_state(parent_wifi_steps.wait_for_state):
    """ description: Waits until the wifi is in the desired state.
    """
    pass


class scan_and_check_ap(parent_wifi_steps.scan_and_check_ap):
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
    pass


class clear_saved_networks(parent_wifi_steps.clear_saved_networks):

    def do(self):
        if self.open_wifi_settings:
            # Turn on Wi-Fi and go to Settings - Wi-Fi menu and Turn
            wifi_steps.set_wifi(
                serial=self.serial,
                state="ON",
                use_adb=self.use_adb)()
            wifi_steps.open_wifi_settings(serial=self.serial, use_adb=False)()

        # Click the More button
        # if not ui_steps.click_button_if_exists(serial=self.serial,
        #            view_to_find = self.device_info.wifi_more_options_id)():
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
            i = self.uidevice(resourceId="android:id/title").count
            number_of_saved_networks = i - 1
            for x in xrange(number_of_saved_networks):
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "resourceId": "android:id/title"},
                                      view_to_check={"textContains": "CANCEL"})()
                ui_steps.click_button(serial=self.serial,
                                      view_to_find={
                                          "textContains": "FORGET"},
                                      view_to_check={"textContains": "Add network"})()

            # If we still have an entry in the list, the step is failed.
            if self.max_entries == 0:
                self.step_data = False
                self.set_errorm("", "Network still in 'Saved Networks' list.")
            else:
                self.step_data = True
        else:
            self.step_data = True


class set_wifi_security(parent_wifi_steps.set_wifi_security):

    def __init__(self, security, password=None, EAP_method=None, phase_2_auth=None, user_certificate=None,
                 identity=None, anonymous_identity=None, ca_certificate=None, clear_text_boxes=True, **kwargs):
        parent_wifi_steps.set_wifi_security.__init__(
            self,
            security,
            password,
            EAP_method,
            phase_2_auth,
            user_certificate,
            identity,
            anonymous_identity,
            ca_certificate,
            clear_text_boxes,
            **kwargs)
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


class set_wifi_advanced_options(parent_wifi_steps.set_wifi_advanced_options):

    pass


class add_network(parent_wifi_steps.add_network):

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
                 ca_certificate=None, hidden_ssid=None, identity=None, anonymous_identity=None,
                 proxy=None, proxy_pac_url=None, proxy_hostname=None, proxy_port=None, proxy_bypass=None,
                 ip_settings=None, ip_address=None, gateway=None, network_prefix_length=None, dns1=None, dns2=None,
                 valid_config=True, apply_config=True, **kwargs):
        parent_wifi_steps.add_network.__init__(self, ssid, security, password, EAP_method, phase_2_auth,
                                               user_certificate, ca_certificate,
                                               identity, anonymous_identity, proxy, proxy_pac_url, proxy_hostname,
                                               proxy_port, proxy_bypass, ip_settings,
                                               ip_address, gateway, network_prefix_length, dns1, dns2, valid_config,
                                               apply_config, **kwargs)
        self.ssid = ssid
        self.security = security
        self.password = password
        self.EAP_method = EAP_method
        self.phase_2_auth = phase_2_auth
        self.user_certificate = user_certificate
        self.ca_certificate = ca_certificate
        self.hidden_ssid = hidden_ssid
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
        # if self.device_info.dessert in ["L", "M"]:
        #     ui_steps.click_button(serial=self.serial,
        #                           view_to_find={"descriptionContains": "More"},
        #                           view_to_check={"textContains": "Add network"})()
        # if self.device_info.dessert in ["N"]:
        #     ui_steps.wait_for_view_with_scroll(serial=self.serial, timeout=10000,
        #                                        view_to_find={"resourceId": "android:id/icon_frame"},
        #                                        iterations=5)()

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

        set_wifi_advanced_options(serial=self.serial, proxy=self.proxy, proxy_pac_url=self.proxy_pac_url,
                                  proxy_hostname=self.proxy_hostname, proxy_port=self.proxy_port,
                                  proxy_bypass=self.proxy_bypass, ip_settings=self.ip_settings,
                                  ip_address=self.ip_address, gateway=self.gateway,
                                  network_prefix_length=self.network_prefix_length,
                                  dns1=self.dns1, dns2=self.dns2, clear_text_boxes=False)()

        # Implementation of adding Hidden network capability that is changed in
        # UI, P dessert onwards
        if self.hidden_ssid == '1':
            if adb_utils.is_virtual_keyboard_on(serial=self.serial):
                ui_steps.press_back(serial=self.serial)()
            # The attributes of the below View To Find has to be taken properly
            # to work. This is temporary and fails some times. Add scroll =
            # False
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "resourceId": "com.android.settings:id/wifi_advanced_toggle"},
                                  view_to_check={"textContains": "Hidden network"}, scroll=False)()

            ui_steps.click_button(serial=self.serial,
                                  view_to_find={
                                      "resourceId": "com.android.settings:id/hidden_settings"},
                                  view_to_check={"textContains": "Yes"}, scroll=False)()

            ui_steps.click_button(serial=self.serial,
                                  view_to_find={"textContains": "Yes"},
                                  view_to_check={"textContains": "SAVE"}, scroll=False)()

        # Click Save
        apply_config_btn = {
            "className": "android.widget.Button",
            "enabled": True}
        apply_config_btn.update(self.device_info.wifi_add_network_save_btn_id)
        print apply_config_btn
        if self.apply_config:
            # if self.valid_config:
            #     ui_steps.click_button(serial=self.serial,
            #                           view_to_find = {"textContains" : "SAVE"})()
            #                           # view_to_check = {"descriptionContains" : "Add network"})()
            #     ui_steps.click_button(serial=self.serial,
            #                           view_to_find={'className': 'android.widget.Button', 'enabled': True,
            # 'textContains': 'SAVE'},
            #                           view_to_check=None)()
            # else:
            apply_config_btn.update({"enabled": False})
            ui_steps.click_button(serial=self.serial,
                                  view_to_find={'className': 'android.widget.Button', 'enabled': True,
                                                'textContains': 'SAVE'})()
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


class modify_network(parent_wifi_steps.modify_network):
    """ description:
            Modify an existing Wi-Fi network.

        usage:
            wifi_steps.modify_network(ssid='MyAP', password='1234')()

        valid_config - it will check weather the Save button is available to click

        tags:
            ui, android, ssid, wifi
    """
    pass


class ping_gateway(parent_wifi_steps.ping_gateway):
    """
    Description:
                Pings the DUT gateway <trycount> times.
                Will fail if the packet loss is less then or equal to <target_percent>
    """
    pass


class ping_ip(parent_wifi_steps.ping_ip):
    """
    Description:
                Pings the IP for <trycount> times.
                It will fail if the packet loss is less then or equal to <target_percent>
    """
    pass


class find_available_ip(parent_wifi_steps.find_available_ip):
    """
        returns the first IP that is available from a range of IPs

    """
    pass


class check_network_information(parent_wifi_steps.check_network_information):
    """
    Description: Check the network information on device.
    """
    pass
