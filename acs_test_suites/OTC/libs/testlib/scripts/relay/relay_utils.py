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

# imports
import time


def select_menu_item(relay, option):
    """ description:


        tags:
            utils, crashmode, fastboot, power, ros, android, relay, reboot
    """
    count = 0
    while count < int(option):
        relay.press_volume_down()
        time.sleep(0.5)
        count += 1


def select_ros_menu_item(relay, mode="android"):
    """ description:


        tags:
            utils, recovery, android, relay, reboot
    """
    select_menu_item(relay, mode)


def select_fastboot_menu_item(relay, option):
    """ description:


        tags:
            utils, fastboot, android, relay, reboot
    """
    select_menu_item(relay, option)


def select_crashmode_menu_item(relay, option):
    """ description:


        tags:
            utils, crashmode, android, relay, reboot
    """
    select_menu_item(relay, option)
