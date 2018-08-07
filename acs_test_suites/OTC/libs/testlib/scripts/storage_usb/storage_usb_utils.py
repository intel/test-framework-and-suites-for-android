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


from testlib.utils.connections.adb import Adb as connection_adb


def get_UUID(block_id, serial=None):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    for line in adb_connection.parse_cmd_output('blkid').split('\n'):
        if block_id in line:
            uuid = line.split(' ')[1].split('=')[1].strip('"')
            return uuid
    return "UUID Not Found"
