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

from testlib.scripts.android.android_step import step as android_step
from testlib.utils.connections.adb import Adb as connection_adb
from testlib.base import base_utils


class step(android_step):
    '''helper class for all adb test steps'''
    adb_connection = None

    def __init__(self, **kwargs):
        android_step.__init__(self, **kwargs)
        self.adb_connection = connection_adb(**kwargs)

    def take_picture(self, file_name):
        # catch all exceptions and ignore them
        try:
            self.adb_connection.run_cmd("screencap -p /sdcard/screen.png")
            self.adb_connection.get_file("/sdcard/screen.png", file_name)
            self.adb_connection.run_cmd("rm /sdcard/screen.png")
        except Exception, e:
            if "device not found" in e.message:
                raise base_utils.DeviceNotFoundError("Serial {0} not found".format(self.serial))
