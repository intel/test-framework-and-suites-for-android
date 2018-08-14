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

from testlib.base.abstract.abstract_step import abstract_step
from testlib.base.abstract import abstract_utils


USE_MODULE = abstract_utils.get_module("wifi_module")
if USE_MODULE is None:
    # default 'wifi_steps'
    USE_MODULE = "wifi_steps"


@abstract_step(use_module=USE_MODULE)
class clear_saved_networks():
    """ description:
            Clear all saved networks. Can remove a maximum of <max_entries> networks.


        optional parameters:
            max_entries - maximum entries to remove (default is 20)
    """
    pass


@abstract_step(use_module=USE_MODULE)
class add_network():
    """ description:
            Add a Wi-Fi network.

        required parameters:
            ssid
            security

        optional parameters:
            password
            EAP_method
            phase_2_auth
            CA_certificate
            identity
            anonymous_identity
            proxy
            proxy_pac_url
            proxy_hostname
            proxy_port
            proxy_bypass
            ip_settings
            ip_address
            gateway
            network_prefix_length
            dns1
            dns2
            valid_config
    """
    pass


@abstract_step(use_module=USE_MODULE)
class check_connection_info():
    """ description:
            Check connection information

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

    """
    pass


@abstract_step(use_module=USE_MODULE)
class wait_until_connected():
    """ description: Waits untill the device is connected to a wifi network.

        optional parameters:
        timeout (default is 30)
    """
    pass


@abstract_step(use_module=USE_MODULE)
class scan_and_check_ap():
    """ description:
            Check weather an AP SSID can be found by a Wi-Fi scan.

            NOTE: Carefull when looking for an AP SSID that is saved as it will
            show up even when the AP SSID is not visible or in range!

        required parameters:
            ap

        optional parameters:
            trycount (default is 10)
            should_exist (default is True)
    """
    pass


@abstract_step(use_module=USE_MODULE)
class set_wifi():
    """ description:
            Turns Wifi on or off.

        optional parameters:
            state (ON/OFF) (default is ON)
    """
    pass


@abstract_step(use_module=USE_MODULE)
class wait_for_state():
    """ description: Waits untill the device has the wifi state given as parameter.

        optional parameters:
        state (default is 'CONNECTED/CONNECTED')
        timeout (default is 30)
    """
    pass


@abstract_step(use_module=USE_MODULE)
class modify_network():
    """ description: Modify an existing network.
    """
    pass


@abstract_step(use_module=USE_MODULE)
class ping_gateway():
    """ Pings the DUT gateway <trycount> times.
        Will fail if all pings fail.
    """


@abstract_step(use_module=USE_MODULE)
class ping_ip():
    """ Pings the IP for <trycount> times.
        It will fail if the packet loss is less then or equal to <target_percent>
    """


@abstract_step(use_module=USE_MODULE)
class find_available_ip():
    """
        returns the first IP that is available from a range of IPs
    """


@abstract_step(use_module=USE_MODULE)
class open_wifi_settings():
    """ description:
            open wifi settings page.
    """
    pass
