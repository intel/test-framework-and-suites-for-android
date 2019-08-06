#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.Utilities import AcsConstants

# pylint: disable=E1002


class DeviceCapability(AttributeDict):

    """
    Store a device capability
    """

    def __str__(self):
        return self["name"]

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        self["name"] = AcsConstants.NOT_AVAILABLE
        super(DeviceCapability, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    test = DeviceCapability({'name': "wifi", 'group': 'cws'})
    print test.name
    print test.group
    print test
    print str(test) == "wifi"
