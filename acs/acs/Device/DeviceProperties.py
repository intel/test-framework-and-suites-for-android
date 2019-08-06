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


class DeviceProperties(AttributeDict):

    """
    Store device properties
    For now only one class for all devices.
    However, specific device properties class must be created according to specific hardware needs.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        self["fw_version"] = AcsConstants.NOT_AVAILABLE
        self["sw_release_flashed"] = AcsConstants.NOT_AVAILABLE
        self["sw_release"] = AcsConstants.NOT_AVAILABLE
        self["model_number"] = AcsConstants.NOT_AVAILABLE
        self["baseband_version"] = AcsConstants.NOT_AVAILABLE
        self["device_id"] = AcsConstants.NOT_AVAILABLE
        self["kernel_version"] = AcsConstants.NOT_AVAILABLE
        self["imei"] = AcsConstants.NOT_AVAILABLE
        self["acs_agent_version"] = AcsConstants.NOT_AVAILABLE
        self["board_type"] = AcsConstants.NOT_AVAILABLE
        super(DeviceProperties, self).__init__(*args, **kwargs)
