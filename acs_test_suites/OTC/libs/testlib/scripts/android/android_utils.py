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


from testlib.utils.connections.local import Local


def get_package_name_from_apk(apk_path):
    local_connection = Local()
    command = "aapt dump badging " + apk_path + " | grep package"
    stdout, stderr = local_connection.run_cmd(command=command)
    return stdout.split("'")[1]


def get_app_label_from_apk(apk_path):
    local_connection = Local()
    command = "aapt dump badging " + apk_path + " | grep application-label:"
    stdout, stderr = local_connection.run_cmd(command=command)
    return stdout.split("'")[1]
