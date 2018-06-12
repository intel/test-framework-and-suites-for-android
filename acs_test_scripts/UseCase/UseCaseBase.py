"""
Copyright (C) 2013 Intel Corporation
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
import acs_test_scripts.Device.UECmd.UECmdTypes as UECmdTypes

from acs.UseCase.UseCaseBase import UseCaseBase as UCBase


class UseCaseBase(UCBase):
    """
    Base class for all use case implementation
    """

    def __init__(self, tc_conf, global_config):
        """
        Constructor
        """
        UCBase.__init__(self, tc_conf, global_config)

        # UECmd type
        self._uecmd_types = UECmdTypes
