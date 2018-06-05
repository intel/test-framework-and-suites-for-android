"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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
:summary: This file implements the Reference device
:since: 05/08/2013
:author: cbonnard
"""
from acs.Device.Model.AndroidDevice.AndroidDeviceBase import AndroidDeviceBase


class ReferenceDeviceBase(AndroidDeviceBase):

    """
        Android Phone Base implementation
    """

    def __init__(self, config, logger):
        """
        Constructor

        :type  phone_name: string
        :param phone_name: Name of the current phone(e.g. PHONE1)
        """

        AndroidDeviceBase.__init__(self, config, logger)
        self._logger.info("Reference device initialized")
        if self._enableIntelImage:
            self._logger.info("Intel image forced")
        if self._enableAdbRoot:
            self._logger.info("Adb root enabled")
