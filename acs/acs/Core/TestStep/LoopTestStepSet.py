"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

:organization: INTEL MCG PSI
:summary: This file implements a Test Step Set that loops on its steps
:since: 05/04/2015
:author: gcharlex
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
