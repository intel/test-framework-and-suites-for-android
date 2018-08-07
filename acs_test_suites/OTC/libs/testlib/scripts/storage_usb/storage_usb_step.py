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

# Standard library
from uiautomator import Device

# Userdefined library
from testlib.scripts.android.adb.adb_step import step as adb_step


class StorageUsbStep(adb_step):
    '''helper class for all storage and usb test steps
       Refere wifi step and wifi_steps for more details
    '''

    def __init__(self, **kwargs):
        adb_step.__init__(self, **kwargs)

        # replacing old uidevice available in testlib/external with standard
        #  uiautomator device class
        self.uidevice = Device(serial=self.serial)

    def get_driver_logs(self, file_name):
        try:
            self.adb_connection.run_cmd(
                "echo 'see dmesg' > /sdcard/locallogfile")
            self.adb_connection.get_file("/sdcard/locallogfile", file_name)
        except:
            pass

    def get_failed_dmsg(self, file_name):
        try:
            self.adb_connection.run_cmd("dmesg > /sdcard/localdmsgfile")
            self.adb_connection.get_file("/sdcard/localdmsgfile", file_name)
        except:
            pass

    def get_ui_dump(self, file_name):
        # save UI dump
        try:
            self.uidevice.dump(out_file=file_name,
                               compressed=False,
                               serial=self.serial)
        except:
            pass
