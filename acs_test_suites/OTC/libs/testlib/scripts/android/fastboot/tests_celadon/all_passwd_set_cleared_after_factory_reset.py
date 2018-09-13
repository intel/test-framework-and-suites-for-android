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
import sys
from testlib.base.base_utils import get_args
from testlib.scripts.android.fastboot import fastboot_steps
from testlib.scripts.android.fastboot import fastboot_utils
from testlib.scripts.relay import relay_steps

# initialization
globals().update(vars(get_args(sys.argv)))
args = {}
for entry in script_args:  # noqa
    key, val = entry.split("=")
    args[key] = val
relay_type = args["relay_type"]
relay_port = args["relay_port"]
power_port = args["power_port"]
ssid = args["ssid"]
password = args["password"]

# test start
try:
    fastboot_utils.push_uiautomator_jar(serial=serial)  # noqa
    fastboot_steps.config_first_boot_wizard(serial=serial)()  # noqa
    fastboot_steps.connect_to_internet(serial=serial, ssid=ssid, password=password)()  # noqa
    fastboot_steps.login_google_account(serial=serial)()  # noqa
    fastboot_steps.factory_data_reset(serial=serial)()  # noqa

    fastboot_utils.push_uiautomator_jar(serial=serial)  # noqa
    fastboot_steps.config_first_boot_wizard(serial=serial)()  # noqa
    fastboot_steps.google_account_is_empty(serial=serial)()  # noqa
    fastboot_steps.factory_data_reset(serial=serial)()  # noqa

except:
    relay_steps.reboot_main_os(serial=serial, relay_type=relay_type, relay_port=relay_port,  # noqa
                               power_port=power_port, wait_ui=False, timeout=300, delay_power_on=30,
                               device_info="broxtonp", force_reboot=True)()
    fastboot_steps.factory_data_reset(serial=serial)()  # noqa
    raise
# test end
