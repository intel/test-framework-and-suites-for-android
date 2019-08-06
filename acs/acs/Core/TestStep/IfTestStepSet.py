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

from acs.Core.TestStep.TestStepBase import TestStepBase

from acs.Core.TestStep.TestStepSet import TestStepSet


class IfTestStepSet(TestStepSet):

    """
    Implements test step set which runs its steps in a if.

    Differently from a normal test step set, it doesn't need to be defined and then
    invoked. A **<If/>** tag is declared directly where actions need to be executed in a if.
    A if can call any type of test step, i.e. a simple test step as well as a test step
    set.

    As for a normal test step set, all the attribute declared for the **<If/>** tag are passed
    down to the test steps, except Nb (the number of iterations).
    """

    def run(self, context):
        """
        Runs the test step

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: Test Case context
        """
        TestStepBase.run(self, context)

        if_id = str(self._pars.id)
        cond = str(self._pars.condition)

        if not cond or not cond.strip("0") or cond.strip("0") == "." or cond.lower() == "false":
            # "", 0, 0.0, "[fF]alse" are all False
            self._logger.info("--- Condition '%s' is '%s' => False, skip ---" % (if_id, cond))
        else:
            self._logger.info("--- Condition '%s' is '%s' => True, executing ---" % (if_id, cond))
            TestStepSet.run(self, context)
