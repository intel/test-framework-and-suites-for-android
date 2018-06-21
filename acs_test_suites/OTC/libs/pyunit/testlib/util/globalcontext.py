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
import os


class GlobalContext:
    """
    GlobalContext class is used to hold global settings & configurations
    for test cases in single place.

    The purposes of this class:
    Decouple with nose context object;
    Provide global contexts even not run in nose runner.

    """

    def __init__(self):
        self.device_serial = None
        self.devicetype = "default"
        self.language = "en.US"
        oat_logdir_root = os.path.expanduser('~/.oat')
        if not os.path.exists(oat_logdir_root):
            os.makedirs(oat_logdir_root)
        self.user_log_dir = os.path.normpath(oat_logdir_root + '/logs/')
        if not os.path.exists(self.user_log_dir):
            os.makedirs(self.user_log_dir)
        self.sc_tmp_dir = os.path.normpath(oat_logdir_root + '/sc/')
        if not os.path.exists(self.sc_tmp_dir):
            os.makedirs(self.sc_tmp_dir)
        self.anr_captured = False
        self.crash_captured = False
