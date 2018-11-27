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

from testlib.base.abstract.abstract_step import devicedecorator


@devicedecorator
class install_WIFI_certificate():

    """ description:
            installs certificate from /sdcard/ with the password = <cert_pass>
            setting its name to <cert_name>

        usage:
            ui_steps.install_certificate(password = "1234")()

        tags:
            ui, android, click, button
    """

    pass


@devicedecorator
class open_wifi_settings():
    """ description:
            Opens the WiFi Settings page using an intent or UI.

        usage:
            wifi_steps.open_wifi_settings(serial=self.serial)()

        tags:
            ui, android, settings, wifi, intent
    """
    pass


@devicedecorator
class forget_wifi_network():

    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """

    pass


@devicedecorator
class forget_wifi():

    """ description:
            Removes the provided WiFi SSID from known networks.

        usage:
            wifi_steps.forget_wifi_network(ap_name = "my_wifi_ssid")()

        tags:
            ui, android, settings, wifi
    """

    pass


@devicedecorator
class check_connection_info():
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


@devicedecorator
class set_wifi_state():
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


@devicedecorator
class wait_for_state():
    """ description: Waits until the device is connected to a wifi network.
    """
    pass


@devicedecorator
class wait_until_connected():
    """ description: Waits until the device is connected to a wifi network.
    """
    pass


@devicedecorator
class scan_and_check_ap():
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


@devicedecorator
class clear_saved_networks():

    """ description:
            clear saved network

   """
    pass


@devicedecorator
class set_wifi_security():

    pass


@devicedecorator
class set_wifi_advanced_options():

    pass


@devicedecorator
class add_network():

    """ description:
            add network

   """
    pass


@devicedecorator
class modify_network():
    """ description:
            Modify an existing Wi-Fi network.

        usage:
            wifi_steps.modify_network(ssid='MyAP', password='1234')()

        valid_config - it will check weather the Save button is available to click

        tags:
            ui, android, ssid, wifi
    """
    pass


@devicedecorator
class ping_gateway():
    """
    Description:
                Pings the DUT gateway <trycount> times.
                Will fail if the packet loss is less then or equal to <target_percent>
    """
    pass


@devicedecorator
class ping_ip():
    """
    Description:
                Pings the IP for <trycount> times.
                It will fail if the packet loss is less then or equal to <target_percent>
    """
    pass


@devicedecorator
class find_available_ip():
    """
        returns the first IP that is available from a range of IPs

    """
    pass


@devicedecorator
class check_network_information():
    """
    Description: Check the network information on device.
    """
    pass
