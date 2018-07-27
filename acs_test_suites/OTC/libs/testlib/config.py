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

import os


class GoogleAccount:
    EMAIL_ID = os.getenv("GOOGLE_ACCOUNT_EMAIL_ID")
    PASSWORD = os.getenv("GOOGLE_ACCOUNT_PASSWORD")
    # print "###########", EMAIL_ID, PASSWORD


class WiFiAP:
    SSID = os.getenv("WIFI_CONNECTION_AP_SSID")
    PASSWORD = os.getenv("WIFI_CONNECTION_PASSWORD")
    SECURITY = os.getenv("WIFI_CONNECTION_SECURITY")
    # print "###########", SSID, PASSWORD, SECURITY
