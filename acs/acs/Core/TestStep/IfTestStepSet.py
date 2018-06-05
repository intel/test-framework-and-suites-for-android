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
:summary: This file implements a Test Step Set that if on its steps
:since: 11/24/2015
:author: sdubrayx
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
