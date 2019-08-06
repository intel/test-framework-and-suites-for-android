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
