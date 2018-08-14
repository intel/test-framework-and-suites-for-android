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
import os
from testlib.config import WiFiAP

# All domain should use configuration from {domain}config.py only. Priority
# should be given {domain}config.py compare to testlib.config.py
# Usecase configurations


class WiFiConfigurableAP(object):
    TYPE = os.getenv("ACCESS_POINT_TYPE")
    SSID = os.getenv("WIFI_CONFIGURABLE_AP_SSID")
    MODE = {"b": "b",
            "bg": "bg",
            "g": "g",
            "mixed": "mixed",
            "n": "n",
            "ng": "ng"}
    SECURITY = {"unsecured": "none",
                "wpa_psk_mixed": "wpa_psk_mixed",
                "wpa_psk": "wpa_psk",
                "wpa2": "wpa2",
                "wpa_enterprise": "wpa_enterprise",
                "wpa2_enterprise": "wpa2_enterprise",
                "wep64": "wep64",
                "wep128": "wep128"}
    DUT_SECURITY = {"unsecured": "None",
                    "WEP": "WEP",
                    "WPA": "WPA",
                    "WPA2 PSK": "WPA2 PSK",
                    "WPA/WPA2 PSK": "WPA/WPA2 PSK",
                    "802.1xEAP": "802.1xEAP"}
    ENCRYPTION = {"tkip": "tkip",
                  }  # Todo need to add other encryption
    PASSWORD = "test1234"
    SSH_HOST = os.getenv("ACCESS_POINT_IP")
    SSH_USER = os.getenv("ACCESS_POINT_USER_NAME")
    SSH_PASSWORD = None  # Currently not configured to have password
    CHANNEL_BW = "20"
    CHANNEL_NO = None
    ENABLE_FIVE_GHZ_INTERFACE = "0"
    ENABLE_IPV6 = 0
    ENABLE_RADVD = 0
    DHCP_LEASE = None
    TX_POWER = None
    IPV4_CLASS = SSH_HOST  # Currently it is as SSH HOST IP


# Testcase Parameter set
class ConnectWiFiWithPassword(WiFiAP):
    pass


class ConnectConfigurableOpenWiFiAP(WiFiConfigurableAP):
    MODE = WiFiConfigurableAP.MODE["mixed"]
    SECURITY = WiFiConfigurableAP.SECURITY["unsecured"]
    DUT_SECURITY = WiFiConfigurableAP.DUT_SECURITY["unsecured"]
    ENCRYPTION = None
    PASSWORD = None
