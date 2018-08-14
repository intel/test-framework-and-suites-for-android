#!/usr/bin/env python
##
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
##

import types
import sys
from testlib.base.base_step import step as base_step
from testlib.base.abstract.mock_step import mock_step

MODULES = {"wifi_module": {"wifi_ui": "wifi_steps", "mock": "mock", }, }

MODULE_PATHS = {"wifi_steps": "testlib.scripts.wireless.wifi.wifi_steps",
                "local_steps": "testlib.scripts.connections.local.local_steps",
                "bluetooth_steps": "testlib.scripts.wireless.bluetooth.bluetooth_steps",
                "ui_steps": "testlib.scripts.android.ui.ui_steps",
                "adb_steps": "testlib.scripts.android.adb.adb_steps",
                "logcat_steps": "testlib.scripts.android.logcat.logcat_steps",
                }


def get_module(mod_type):
    if mod_type in MODULES.keys():
        mod_param = [s for s in sys.argv if mod_type in s]
        if mod_param:
            return MODULES[mod_type][mod_param[0].split("=")[-1]]
    return None


def import_module(module_name):
    """ Method for geting the desired step class by importing it's
    module and returning the class object from inside it. """

    if module_name == 'mock':
        new_mock_step = mock_step
        return new_mock_step

    module_path_to_import = MODULE_PATHS[module_name]

    return __import__(name=module_path_to_import, globals=globals(), locals=locals(), fromlist=["*"])


def get_obj(module, step_class):
    try:
        obj = getattr(module, step_class)
    except:
        raise Exception("Module {0} does not implement class {1}.".format(module, step_class))

    if obj:
        if (not isinstance(obj, (type, types.ClassType))):
            raise Exception("Target {0} found, but not of type Class".format(step_class))
        if(not issubclass(obj, base_step)):
            raise Exception("Target {0} found, but subclass is not a 'step'".format(step_class))
    return obj
