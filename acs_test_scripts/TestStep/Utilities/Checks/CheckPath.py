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
from acs.ErrorHandling.AcsConfigException import AcsConfigException
import os.path


class CheckPath(TestStepBase):
    """
    Check some properties of path
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
        path_to_check = self._pars.path_to_check
        operator = self._pars.operator

        self._logger.info("CheckPath: path to check '{0}', operator '{1}'".format(path_to_check, operator))

        # Do required check
        result = False
        if operator == "EXIST":
            result = os.path.exists(path_to_check)
        elif operator == "IS_FILE":
            result = os.path.isfile(path_to_check)
        elif operator == "IS_DIRECTORY":
            result = os.path.isdir(path_to_check)

        # Invert result if needed
        if not self._pars.pass_if:
            result = not result

        if not result:
            self._raise_config_exception(AcsConfigException.OPERATION_FAILED, "Path check not satisfied")
