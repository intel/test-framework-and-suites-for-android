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

import re

# Legacy versions are Android versions which support old Acs agent compiled in Eclipse
# Starting to KitKat Acs agent used will be based on 2 agents (user & system) compiled in Android Studio
ANDROID_LEGACY_VERSIONS = ["unknown", "icecreamsandwich", "jellybean.*", "kitkat"]


def get_acs_agent_instance(device, device_version):
    """
    Return the Acs agent instance depending on the Android version

    :param device: device instance
    :return: IAgent instance
    """
    device_version_str = str(device_version).lower()
    is_legacy_version = any([re.compile(x).match(device_version_str) for x in ANDROID_LEGACY_VERSIONS])
    if is_legacy_version:
        from acs.Device.Model.AndroidDevice.Agent.AcsAgentLegacy import AcsAgentLegacy
        agent_instance = AcsAgentLegacy(device)
    else:
        from acs.Device.Model.AndroidDevice.Agent.AcsAgent import AcsAgent
        agent_instance = AcsAgent(device)

    return agent_instance
