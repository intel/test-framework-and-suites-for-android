"""
@copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

@organization: INTEL MCG PSI
@summary: This module implements Factory to instantiate Acs agent object depending on Android OS version
@since: 27/01/2015
@author: ssavrim
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
