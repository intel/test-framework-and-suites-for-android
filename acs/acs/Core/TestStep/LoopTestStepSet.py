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
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class LoopTestStepSet(TestStepSet):

    """
    Implements test step set which runs its steps in a loop.

    Differently from a normal test step set, it doesn't need to be defined and then
    invoked. A **<Loop/>** tag is declared directly where actions need to be executed in a loop.
    A loop can call any type of test step, i.e. a simple test step as well as a test step
    set.

    As for a normal test step set, all the attribute declared for the **<Loop/>** tag are passed
    down to the test steps, except Nb (the number of iterations).
    """

    def run(self, context):
        """
        Runs the test step

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: Test Case context
        """
        TestStepBase.run(self, context)

        loop_id = str(self._pars.id)

        try:
            nb_iteration = int(self._pars.nb)
        except ValueError:
            error_msg = ("Loop expects an integer value as "
                         "iteration number (Given value type: {0})").format(type(self._pars.nb))
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        if nb_iteration < 0:
            error_msg = ("Loop expects a positive value as "
                         "iteration number (Given value: {0})").format(self._pars.nb)
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        # Log in acs logs
        self._logger.info("--- Running loop '%s' of %d iterations ---", loop_id, nb_iteration)

        # Loop on Test Steps
        for iteration in xrange(nb_iteration):
            self._logger.info("--- Loop '%s' - Iteration %d ---", loop_id, (iteration + 1))
            TestStepSet.run(self, context)
