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

import time
from acs.Core.TestStep.TestStepBase import TestStepBase


class SuspendToTime(TestStepBase):
    """
    Suspend the execution until specified time
    """

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        wait_time = self._pars.to_time - time.time()
        if wait_time < 0:
            self._logger.info("Reach timestamp since {0} seconds".format(abs(wait_time)))
            return
        else:
            self._logger.info("Suspend execution for {0} seconds".format(wait_time))
            time.sleep(wait_time)
