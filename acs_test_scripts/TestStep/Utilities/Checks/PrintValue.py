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
from acs.Core.TestStep.TestStepBase import TestStepBase


class PrintValue(TestStepBase):

    def run(self, context):
        value_found = True
        var = self._pars.value_to_print
        try:
            TestStepBase.run(self, context)
        except BaseException:
            value_found = False

        if value_found is True:
            self.ts_verdict_msg = "VERDICT: %s value is {0}.".format(self._pars.value_to_print) % var
        else:
            self.ts_verdict_msg = "VERDICT: %s value wasn't found." % var
        self._logger.debug(self.ts_verdict_msg)
