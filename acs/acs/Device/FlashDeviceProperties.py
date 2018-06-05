"""
:copyright: (c)Copyright 2014, Intel Corporation All Rights Reserved.
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

:organization: INTEL MCG PSI
:summary: This file implements the FlashDeviceProperties class used by the device
:since: 06/11/2014
:author: cbonnard
"""
from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.Utilities import AcsConstants

# pylint: disable=E1002


class FlashDeviceProperties(AttributeDict):

    """
    Store software properties, eg all software pieces that can vary on a device.

    """

    def __init__(self, *args, **kwargs):
        """
        Constructor
        """
        # For now only sw pieces that are update by flash action are stored
        self["fw_version"] = AcsConstants.NOT_AVAILABLE
        self["sw_release"] = AcsConstants.NOT_AVAILABLE
        self["baseband_version"] = AcsConstants.NOT_AVAILABLE

        super(FlashDeviceProperties, self).__init__(*args, **kwargs)
