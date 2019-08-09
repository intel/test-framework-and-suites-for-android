#!/usr/bin/python
"""
Copyright (C) 2018 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.


SPDX-License-Identifier: Apache-2.0
"""

import uiautomator

from testlib.base import base_utils
from testlib.utils.connections.adb import Adb as connection_adb


class UIDevice(uiautomator.AutomatorDevice):
    __metaclass__ = base_utils.SingletonType

    def __init__(self, **kwargs):
        serial = None
        local_port = None
        self.verbose = False
        if "serial" in kwargs:
            serial = kwargs['serial']
        if "local_port" in kwargs:
            local_port = kwargs['local_port']
        if "verbose" in kwargs:
            self.verbose = kwargs['verbose']
        super(UIDevice, self).__init__(serial=serial, local_port=local_port)

    def dump(self, out_file=None, serial=None, compressed=False):
        if out_file:
            return_value = super(UIDevice, self).dump(filename=out_file, compressed=compressed)
        else:
            return_value = super(UIDevice, self).dump(compressed=compressed)
        if serial:
            adb_connection = connection_adb(serial=serial)
        else:
            adb_connection = connection_adb()
        adb_connection.run_cmd("rm /data/local/tmp/dump.xml", timeout=10)
        adb_connection.run_cmd("rm /data/local/tmp/local/tmp/dump.xml", timeout=10)
        return return_value
