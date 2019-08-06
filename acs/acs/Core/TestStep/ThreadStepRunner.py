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
