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
from testlib.util.common import g_common_obj


def create_file(size=5):
    count = 1024 * size
    command = "dd if=/dev/zero of=/mnt/sdcard/" + \
        str(size) + "Mbigfile bs=1024 count=" + str(count)
    result = g_common_obj.adb_cmd_capture_msg(command, 1200)
    print "The result of create big file :" + result
    if result.find(str(count)) != -1:
        return True, "/mnt/sdcard/" + str(size) + "Mbigfile"
    return False, "Not fill the file into device"


def create_file_no_space():
    command = "dd if=/dev/zero of=/mnt/sdcard/bigfile"
    result = g_common_obj.adb_cmd_capture_msg(command, 1200)
    print "The result of create big file till momery full :" + result
    if result.find("No space left on device") != -1:
        return True, "/mnt/sdcard/bigfile"
    return False, "Not fill the file into device"


def fill_no_space_except(size=5):
    result, msg = create_file(size)
    if result:
        result1, msg1 = create_file_no_space()
        if result1:
            g_common_obj.adb_cmd_capture_msg("rm -rf " + msg)
            return True, "/mnt/sdcard/bigfile"
        else:
            return result1, msg1
    else:
        return result, msg
