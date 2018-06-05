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
:summary: This file implements a Test Step Set class
:since: 15/03/2013
:author: fbongiax
"""
from acs.Core.TestStep.TestStepBase import TestStepBase


class TestStepSet(TestStepBase):

    """
    Implements test step set.

    .. uml::

        class TestStepBase

        class TestStepSet {
            run(context)
            add_step(test_step)
            add_steps(test_steps)
        }

        TestStepBase <|- TestStepSet

    A test step set is declared as follow:

    .. code-block:: xml
        :linenos:

        <TestStepSet Id="InitDevice">
            <!-- These operations are needed for both DUT and second device -->
            <TestStep Id="CONNECT_DEVICE" />
            <TestStep Id="ENABLE_FLIGHT_MODE" />
        </TestStepSet>

    To execute a test step set, use a test step with **SetId** attribute:

    .. code-block:: xml
        :linenos:

        <TestStep SetId="InitDevice" DEVICE="PHONE1" />

    All the attribute of test step **InitDevice** are passed to the test steps inside the set.
    A test step inside the set can however override the attribute passed in if it wants.
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """

        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)

        self._test_steps = []

    def run(self, context):
        """
        Runs the test step
        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: test case context
        """

        for test_step in self._test_steps:
            test_step.run(context)
            if isinstance(self.ts_verdict_msg, list):  # pylint: disable=E0203
                self.ts_verdict_msg.append((test_step.name, test_step.ts_verdict_msg))  # pylint: disable=E0203
            else:
                self.ts_verdict_msg = [(test_step.name, test_step.ts_verdict_msg)]  # pylint: disable=W0201

    def add_step(self, test_step):
        """
        Add a test step to the collection

        :type test_step: :py:class:`~acs.Core.TestStep.TestStepBase`
        :param test_step: the test step to add
        """

        self._test_steps.append(test_step)

    def add_steps(self, test_steps):
        """
        Add a list of test steps to the collection

        :type test_steps: list
        :param test_steps: the array of test_step to add
        """

        self._test_steps.extend(test_steps)
