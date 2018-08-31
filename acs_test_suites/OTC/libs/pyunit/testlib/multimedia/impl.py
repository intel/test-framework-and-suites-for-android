# coding: UTF-8
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


class ImplCommon(object):
    def __init__(self, device=None):
        self.d = device
        self.commonObj = g_common_obj
        if self.d is None:
            self.d = self.commonObj.get_device()

    def setChecked(self, uiautomatorObj, checked=True):
        checked = bool(checked)
        if uiautomatorObj.checked != checked:
            uiautomatorObj.click()

    def __getattr__(self, name):
        if hasattr(self, name + "Kwargs"):
            return self.d(**getattr(self, name + "Kwargs"))
        raise AttributeError("%s has no such attr: %s" % (self.__class__.__name__, name))
