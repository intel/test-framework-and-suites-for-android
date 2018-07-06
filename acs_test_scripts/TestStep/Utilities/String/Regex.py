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
import re
from acs.Core.TestStep.TestStepBase import TestStepBase
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class Regex(TestStepBase):
    """
    Regex command class
    """

    def __init__(self, tc_name, global_config, ts_conf, factory):
        """
        Constructor
        """
        # Call DeviceTestStepBase base Init function
        TestStepBase.__init__(self, tc_name, global_config, ts_conf, factory)

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        if self._pars.action not in ["SEARCH", "MATCH"]:
            self._raise_config_exception("ACTION argument's value (%s) is invalid" %
                                         self._pars.action)

        if self._pars.action == "SEARCH":
            self._logger.info("Regex search (Pattern: %s in string %s" % (self._pars.pattern, self._pars.string))
            re_result = re.search(self._pars.pattern, self._pars.string)
        elif self._pars.action == "MATCH":
            self._logger.info("Regex match (Pattern: %s in string %s" % (self._pars.pattern, self._pars.string))
            re_result = re.match(self._pars.pattern, self._pars.string)
        result = (re_result is not None)

        if self._pars.save_as is not None:
            context.set_info(self._pars.save_as, result)
            return

        # Invert result if needed
        if not self._pars.pass_if:
            result = not result

        if not result:
            self._raise_config_exception(AcsConfigException.OPERATION_FAILED,
                                         "Pattern search/match not satisfied\n"
                                         "Pattern: %s\n"
                                         "String: %s" % (self._pars.pattern, self._pars.string))
