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

# this is a dictionary with all the channels (2.4 & 5 GHz) with their corresponding frequencies
channel_no_to_freq = {'153': '5765', '157': '5785', '60': '5300', '132': '5660', '116': '5580', '64': '5320',
                      '136': '5680', '112': '5560', '48': '5240', '44': '5220', '40': '5200', '1': '2412',
                      '3': '2422', '2': '2417', '5': '2432', '4': '2427', '7': '2442', '6': '2437', '9': '2452',
                      '8': '2447', '144': '5720', '140': '5700', '149': '5745', '120': '5600', '108': '5540',
                      '124': '5620', '128': '5640', '165': '5825', '100': '5500', '161': '5805', '104': '5520',
                      '11': '2462', '10': '2457', '13': '2472', '12': '2467', '14': '2484', '56': '5280',
                      '36': '5180', '52': '5260'}


wifi = {"dut_security": "WPA",
        "ap_name": "ddwrt",
        "ap2_name": "ddwrt_2",
        "ap3_name": "ddwrt_3",
        "passphrase": "test1234",
        "encryption": "aes",
        "radius_identity": None,
        "EAP_method": None,
        "phase_2_auth": None,
        "user_certificate": None,
        "new_ssid": "ap2",
        "ap2_ip": "192.168.2.1",
        "ap2_passphrase": "secondap1234",
        "ap2_encryption": "aes",
        "compare_method": "cmp",
        "wifi_file_name": "generated_wifi",
        "device_path": "/storage/sdcard0/Download/",
        "port_number_wifi": "20211",
        "file_size": 1024,
        "local_path": ".",
        "protocol": "ftp",
        "post_action_transition_wait_time": 10,
        "pre_action_transition_wait_time": 5,
        "trycount": 60,
        "pin": '1234',
        "sta_channel": "11",
        "sta_channel_5ghz": "48",
        "test_page_ip": "172.16.1.1",
        "hotSpot_ip": "192.168.43.1"
        }

p2p = {"p2p_port_number": "20212",
       "root_dir": "/data/ftpdfiles/",
       "copy_from": str(os.environ['PYTHONPATH'].rstrip(':') + '/testlib/external/busybox'),
       "p2p_file_name": "generated_p2p",
       "p2p_device_path": "/storage/sdcard0/Download/",
       "cli_group_state": "UserAuthorizingNegotiationRequestState",
       "go_group_state": "GroupNegotiationState",
       "p2p_freq": channel_no_to_freq[wifi["sta_channel"]]
       }

# Values for IPV6 and radvd setup
RADVD_CONF_FILE = "radvd.conf"
AP_IPV6_PREFIX = "2001:1234:5678:9abc"
