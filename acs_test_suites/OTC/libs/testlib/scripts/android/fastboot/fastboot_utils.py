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

# import ConfigParser
# import commands
# import os
# import re
# import requests
# import serial
# import subprocess
# import threading
# import time
# import warnings
# import zipfile
# from testlib.scripts.connections.local import local_steps
# from testlib.scripts.connections.local import local_utils
# from testlib.utils.connections.adb import Adb as connection_adb
from testlib.utils.connections.local import Local as connection_local
# from uiautomator import Device


def get_var(var, serial=None):
    if serial:
        fastboot_cmd = "fastboot -s {0} getvar {1} 2>&1".format(serial, var)
    else:
        fastboot_cmd = "fastboot getvar {0} 2>&1".format(var)
    local_connection = connection_local()
    # Get the output of the command
    value = local_connection.run_cmd(command=fastboot_cmd)
    # Get the var value (if the fastboot var exists)
    var_value = [i for i in value if var in i and "UNKNOWN COMMAND" not in i]
    if len(var_value):
        return var_value[0].split('\n')[0].split(':')[-1].strip().lower()
    return None
