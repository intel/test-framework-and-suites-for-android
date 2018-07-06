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


class MathOperation (TestStepBase):
    """
    Mathematical operation
    """
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """
        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)
        self._result = None

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """

        TestStepBase.run(self, context)

        assert self._pars.operator in [self.ADD, self.SUBTRACT, self.MULTIPLY, self.DIVIDE], \
            "Operator value is invalid (it should have been checked by the framework)"

        first_value = float(self._pars.first)
        second_value = float(self._pars.second)

        if self._pars.operator == self.ADD:
            self._result = first_value + second_value
        elif self._pars.operator == self.SUBTRACT:
            self._result = first_value - second_value
        elif self._pars.operator == self.MULTIPLY:
            self._result = first_value * second_value
        elif self._pars.operator == self.DIVIDE:
            if second_value == 0:
                msg = "Second value = 0 ! Division by 0 is not possible"
                self._logger.error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, msg)
            else:
                self._result = first_value / second_value

        context.set_info(self._pars.save_result_as, str(self._result))

        self.ts_verdict_msg = "VERDICT: %s stored as {0}".format(self._result) % self._pars.save_result_as
        self._logger.debug(self.ts_verdict_msg)
