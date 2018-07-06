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
from acs.ErrorHandling.AcsToolException import AcsToolException
from acs.ErrorHandling.DeviceException import DeviceException


class Dummy(TestStepBase):

    """
        Validate Test Step mechanism
    """

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """

        TestStepBase.run(self, context)

        self._logger.info("Saves input value (%s) into context using variable name (%s)...",
                          self._pars.input_1, self._pars.ctx_data_1)
        context.set_info(self._pars.ctx_data_1, self._pars.input_1)

        self._logger.info("Saves input values (%s and %s) into context bundle using variable name (%s)...",
                          self._pars.input_1, self._pars.input_2, self._pars.ctx_data_2)
        context.set_nested_info([self._pars.ctx_data_2, "INPUT_1"], self._pars.input_1)
        context.set_nested_info([self._pars.ctx_data_2, "INPUT_2"], self._pars.input_2)

        self._logger.info("Generates return code (%s), with comment (%s)...", self._pars.return_code,
                          self._pars.comment)
        self.ts_verdict_msg = self._pars.comment

        if self._pars.return_code == "SUCCESS":
            pass
        elif self._pars.return_code == "FAILURE":
            raise DeviceException(DeviceException.OPERATION_FAILED, self._pars.comment)
        elif self._pars.return_code == "BLOCKED":
            raise AcsToolException(AcsToolException.OPERATION_FAILED, self._pars.comment)
        elif self._pars.return_code == "ACS_EXCEPTION":
            raise AcsToolException(AcsToolException.OPERATION_FAILED, self._pars.comment)
        elif self._pars.return_code == "DEVICE_EXCEPTION":
            raise DeviceException(DeviceException.OPERATION_FAILED, self._pars.comment)
        elif self._pars.return_code == "UNKNOWN_EXCEPTION":
            raise ValueError(self._pars.comment)
        else:
            raise AcsToolException(AcsToolException.OPERATION_FAILED, self._pars.comment)
