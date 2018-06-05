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
:summary: This file implements a Test Step Set that runs its steps in parallel
:since: 15/03/2013
:author: fbongiax
"""

import time
from Queue import Queue

from acs.Core.TestStep.ThreadStepRunner import ThreadStepRunner
from acs.Core.TestStep.TestStepSet import TestStepSet


class ParallelTestStepSet(TestStepSet):

    """
    Implements test step set which runs its steps in parallel.

        .. uml::

            class TestStepSet

            class ParallelTestStepSet {
                run(context)
            }

            class ThreadStepRunner {
                run()
            }

            TestStepSet <|-- ParallelTestStepSet
            ParallelTestStepSet *- ThreadStepRunner : instantiate

    A parallel test step set is declared as follow:

    .. code-block: xml
        :linenos:
        <Fork Id="InitDevices" Serialize="False">
            <!-- Execute the test step set for the DUT -->
            <TestStep SetId="InitDevice" DEVICE="PHONE1" />
            <!-- Execute the test step set for the second device -->
            <TestStep SetId="InitDevice" DEVICE="PHONE2" />
        </Fork>

    Differently from a normal test step set, it doesn't need to be defined and then
    invoked. A **<Fork/>** tag is declared directly where parallel actions need to be executed.
    A fork can call any type of test step, i.e. a simple test step as well as a test step
    set.

    The attribute Serialize is optional and by default is False. In fact the aim of a
    Fork is to execute multiple tasks in parallel. However (mainly for debug purpose) it
    is possible to set Serialize="True". If done, TestStepEngine executes the tasks inside
    **<Fork/>** in the main thread, hence serializing them. In fact, what TestStepEngine does
    under the hood is to create a TestStepSet instead of a ParallelTestStepSet.

    As for a normal test step set, all the attribute declared for the **<Fork/>** tag are passed
    down to the test steps.

    .. warning::
        ParallelTestStepSet uses a thread per each inner test step so potentially threading problems might be introduced
        For this reason use it carefully.
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """

        TestStepSet.__init__(self, tc_conf, global_conf, ts_conf, factory)

        self._queue = Queue()
        self._execution_queue = Queue()

    def run(self, context):
        """
        Runs the test step

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: Test Case context
        """

        # log in acs logs
        self._logger.info("Running %d steps in parallel ...", len(self._test_steps))

        self._create_test_steps_threads(context)

        self._pump_test_steps_into_queue()

        # Waiting until all threads have finished processing their step
        self._queue.join()

        # Get content of the execution queue (exception, test step verdicts)
        while not self._execution_queue.empty():
            # There is at least one exception in the queue
            # Get the first and raise it
            queue_content = self._execution_queue.get()
            if isinstance(queue_content, tuple):
                # In this case the queue will contain a tuple (test_step_name, test_step_verdict)
                if isinstance(self.ts_verdict_msg, list):  # pylint: disable=E0203
                    self.ts_verdict_msg.append(queue_content)  # pylint: disable=E0203
                else:
                    self.ts_verdict_msg = [queue_content]  # pylint: disable=W0201

            else:
                raise queue_content

    def _create_test_steps_threads(self, context):
        """
        Create one thread per test step in the steps collection
        Each thread will process one item from the queue
        """
        for _ in self._test_steps:
            thread = ThreadStepRunner(self._queue, self._execution_queue, context)
            thread.setDaemon(True)
            thread.start()

    def _pump_test_steps_into_queue(self):
        """
        Pumps the test steps into the queue; An equal number of threads are waiting to get a test step from the queue.
        As soon as an item gets pumped into the queue, a waiting thread will get it and run it.
        If a delay was specified, the method waits for that delay before pumping the next test step into the queue
        """
        count = 0
        for step in self._test_steps:
            self._queue.put(step)
            self._delay_if_needed(count)
            count += 1

    def _delay_if_needed(self, count):
        """
        If parameter DELAY is passed and is numeric, then sleep
        """
        if self._pars.delay and float(self._pars.delay) > 0.0 and count < len(self._test_steps) - 1:
            self._logger.info("Waiting for %s before starting the next step" % self._pars.delay)
            self._wait_for_secs(self._pars.delay)

    def _wait_for_secs(self, delay):
        """
        Stops execution for delay secs
        """
        time.sleep(float(delay))
