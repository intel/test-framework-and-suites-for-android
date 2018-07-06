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


class Suspend(TestStepBase):

    """
    Suspend the execution for N seconds
    """

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)
        self._logger.info("Suspend execution for {0} seconds".format(self._pars.duration_in_sec))
        if self._pars.refresh_stdout_in_sec and self._pars.refresh_stdout_in_sec > self._pars.duration_in_sec:
            msg = "REFRESH_STDOUT_IN_SEC value is superior to DURATION_IN_SEC value"
            self._logger.info(msg)
            time.sleep(self._pars.duration_in_sec)
            return
        if not self._pars.refresh_stdout_in_sec:
            time.sleep(self._pars.duration_in_sec)
        else:
            div_duration_by_refresh, remainder = divmod(self._pars.duration_in_sec,
                                                        self._pars.refresh_stdout_in_sec)
            # duration_in_sec = refresh_stdout_in_sec * div_duration_by_refresh + remainder
            for i in range(1, int(div_duration_by_refresh) + 1):
                elapsed_time = i * self._pars.refresh_stdout_in_sec
                time.sleep(self._pars.refresh_stdout_in_sec)
                self._logger.info("Suspend execution since {0} seconds".format(elapsed_time))
            time.sleep(remainder)
