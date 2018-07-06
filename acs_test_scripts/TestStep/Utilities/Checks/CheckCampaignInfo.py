"""
Copyright (C) 2017 Intel Corporation

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
from acs.Core.TestStep.TestStepBase import TestStepBase
import acs.UtilitiesFWK.Utilities as Utils
from acs.Device.DeviceManager import DeviceManager


class CheckCampaignInfo(TestStepBase):
    """
    Check that a key is present in the configuration file
    and store found value as a context parameter.
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """
        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        # Looks for the key in the campaign configuration file.
        value = Utils.get_config_value(
            DeviceManager().get_global_config().campaignConfig,
            "Campaign Config", self._pars.key)
        if value is None:
            msg = ("{0}:  Value found for {1} in campaign config was None, " +
                   "storing the default value of {2} instead")
            self._logger.info(msg.format(self._pars.id,
                                         self._pars.key,
                                         self._pars.default_value))
            value = self._pars.default_value
        # Write value to the context so that it can be used by other TestSteps.
        context.set_info(self._pars.param_value, value)
