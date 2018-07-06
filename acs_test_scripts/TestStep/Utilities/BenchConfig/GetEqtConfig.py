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


class GetEqtConfig(TestStepBase):
    """
    Get equipment config class
    """

    def __init__(self, tc_name, global_config, ts_conf, factory):
        """
        Constructor
        """
        # Call TestStepBase base Init function
        TestStepBase.__init__(self, tc_name, global_config, ts_conf, factory)

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        if self._pars.eqt in self._global_conf.benchConfig.get_dict():
            eqt_config = {}
            for key, parameters in self._global_conf.benchConfig.get_dict()[self._pars.eqt].iteritems():
                if isinstance(parameters, dict):
                    eqt_config[key] = parameters["value"]
            context.set_info(self._pars.save_as, eqt_config)
        else:
            self._raise_config_exception("Equipment : %s not found in Bench Config." % self._pars.eqt)
