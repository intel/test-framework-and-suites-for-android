'''
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
'''

from testlib.scripts.storage_usb.storage_usb_step import StorageUsbStep
from testlib.scripts.storage_usb import storage_usb_utils
from testlib.utils.connections.adb import Adb


class CheckSDCardMount(StorageUsbStep):
    def __init__(self, **kwargs):
        StorageUsbStep.__init__(self, **kwargs)
        self.sdcard = False
        self.adb = Adb(serial=self.serial)
        self.uuid = ""

    def do(self):
        self.adb.adb_root()
        blkid_out = self.adb.run_cmd('blkid')
        for line in blkid_out.stdout.read().split('\n'):
            if 'mmcblk0p1' in line:
                self.sdcard = True
                self.uuid = line.split(' ')[1].split('=')[1].strip('"')
                break

    def check_condition(self):
        if self.sdcard:
            vol = self.adb.run_cmd("sm list-volumes")
            for line in vol.stdout.read().strip().split('\n'):
                if self.uuid in line:
                    if 'mounted' in line.split()[-2]:
                        self.set_passm(
                            "SD Card Mounted with UUID: " + self.uuid)
                        return True
        self.set_errorm("", "SD Card Not Mounted")
        return False


class CheckMountstats(StorageUsbStep):
    def __init__(self, fstype, blk_name, **kwargs):
        StorageUsbStep.__init__(self, **kwargs)
        self.fstype = fstype
        self.blk_name = blk_name

    def do(self):
        self.res = False
        uuid = storage_usb_utils.get_UUID(self.blk_name, serial=self.serial)
        stats = self.adb_connection.parse_cmd_output(
            'cat /proc/self/mountstats').split('\n')
        for line in reversed(stats):
            if uuid in line:
                if self.fstype in line:
                    self.res = True
                break
            else:
                self.set_errorm("", "Mount Point Not Found")

    def check_condition(self):
        if self.res:
            return True
        return False
