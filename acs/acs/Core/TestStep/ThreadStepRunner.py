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
:summary: This file implements a Thread which runs a test step
:since: 15/03/2013
:author: fbongiax
"""

import threading


class ThreadStepRunner(threading.Thread):

    """
    Implements thread which runs a test step
    """

    def __init__(self, queue, execution_queue, context):
        """
        Constructor
        """

        threading.Thread.__init__(self)

        self._queue = queue
        self._execution_queue = execution_queue
        self._context = context

    def run(self):
        """
        Runs the test step into a thread.
        """

        threading.Thread.run(self)

        # Grab test step from the queue
        test_step = self._queue.get()

        try:
            test_step.run(self._context)
            self._execution_queue.put((test_step.name, test_step.ts_verdict_msg))
        except Exception as ex:
            self._execution_queue.put(ex)
        finally:
            # signals to queue job is done
            self._queue.task_done()
