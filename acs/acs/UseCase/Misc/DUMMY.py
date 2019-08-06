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

import Queue
import random
import time

from acs.UseCase.UseCaseBase import UseCaseBase
from acs.UtilitiesFWK.Utilities import Verdict
from acs.UtilitiesFWK.Utilities import Verdict2Global
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class Dummy(UseCaseBase):
    returns_code = Queue.Queue()
    steps = Queue.Queue()

    def __init__(self, tc_conf, global_config):
        """
        Constructor
        """
        UseCaseBase.__init__(self, tc_conf, global_config)

        # Get TC Parameters
        self._step = self._tc_parameters.get_param_value("STEP", "RUNTEST")
        self._return_code = self._tc_parameters.get_param_value("RETURN_CODE", Verdict.PASS)
        # Update return code for retro-compatibility
        self._return_code = self._return_code.replace("SUCCESS", Verdict.PASS)
        self._return_code = self._return_code.replace("FAILURE", Verdict.FAIL)

        self._comment = self._tc_parameters.get_param_value("COMMENT", "No Comment")
        self._duration = int(self._tc_parameters.get_param_value("DURATION", 0))
        self._init_exception = self._tc_parameters.get_param_value("INIT_EXCEPTION", False, "str_to_bool")

        if self._init_exception is True:
            raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR,
                                     "Exception raised according to TC param 'INIT_EXCEPTION'")

        # Clear existing queue to avoid unexpected behavior
        if not Dummy.returns_code.empty():
            with Dummy.returns_code.mutex:
                Dummy.returns_code.queue.clear()

        if not Dummy.steps.empty():
            with Dummy.steps.mutex:
                Dummy.steps.queue.clear()

        # Fill the FIFO queue taking into account the b2b iteration number
        for _i in range(self.get_b2b_iteration()):
            for code in self._return_code.split(";"):
                if code.strip() == "RANDOM":
                    code = random.choice(Verdict2Global.map.keys())
                Dummy.returns_code.put(code.strip())

            for step in self._step.split(";"):
                if step.strip() == "RANDOM":
                    step = random.choice(["SETUP", "RUNTEST", "TEARDOWN"])
                Dummy.steps.put(step.strip())

        # Get return code and step only if queue is not empty.
        # By default verdict = PASS, step = RUNTEST
        self._current_verdict = Verdict.PASS
        self._current_step = "RUNTEST"

        if not Dummy.returns_code.empty():
            self._current_verdict = Dummy.returns_code.get()

        if not Dummy.steps.empty():
            self._current_step = Dummy.steps.get()

    def __get_step_verdict(self, step):
        return_code = Verdict.PASS

        if step == self._current_step:
            return_code = self._current_verdict

            if not Dummy.returns_code.empty():
                self._current_verdict = Dummy.returns_code.get()

            if not Dummy.steps.empty():
                self._current_step = Dummy.steps.get()

        return return_code

    def set_up(self):
        """
        Execute the test
        """

        UseCaseBase.set_up(self)
        time.sleep(self._duration)

        verdict = self.__get_step_verdict("SETUP")
        return_code = Verdict2Global.map[verdict]

        comment = "(SETUP) " + self._comment
        return return_code, comment

    def run_test(self):
        """
        Execute the test
        """

        UseCaseBase.run_test(self)
        time.sleep(self._duration)

        verdict = self.__get_step_verdict("RUNTEST")
        return_code = Verdict2Global.map[verdict]

        comment = "(RUNTEST) " + self._comment
        return return_code, comment

    def tear_down(self):
        """
        Execute the test
        """

        UseCaseBase.tear_down(self)
        time.sleep(self._duration)

        verdict = self.__get_step_verdict("TEARDOWN")
        return_code = Verdict2Global.map[verdict]

        comment = "(TEARDOWN) " + self._comment
        return return_code, comment
