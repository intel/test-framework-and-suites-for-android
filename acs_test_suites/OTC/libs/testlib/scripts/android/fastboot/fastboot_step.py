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
from testlib.scripts.android.fastboot import fastboot_utils


class step(android_step):

    def __init__(self, **kwargs):
        android_step.__init__(self, **kwargs)
        self.platform_name = fastboot_utils.get_platform_name(
            serial=self.serial)
        self.o_platform_list = ["o_celadon", "o_cel_apl"]
        self.p_platform_list = ["p_cel_apl"]
        self.o_partition_list = ["boot", "bootloader",
                                 "multiboot", "system", "tos", "vbmeta", "vendor"]
