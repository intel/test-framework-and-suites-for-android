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
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class CheckContextInfoExists(TestStepBase):
    """
    Check that a key is present in the context
    """

    STR_KEY = "KEY"

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """
        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)
        self._key = self._pars.key

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        # Looks for the key in the context, raise an error if it doesn't exist
        info = context.get_info(self._key)
        if info is None:
            return_message = "%s is not found in the context" % self._key
            self._logger.error(return_message)
            raise AcsConfigException(AcsConfigException.OPERATION_FAILED, return_message)
