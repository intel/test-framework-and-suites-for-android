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
import re


class GetStrAfterKeyword(TestStepBase):
    """
    This command is used to get the string after a string that is found until
    the first whitespace
    """

    def run(self, context):
        TestStepBase.run(self, context)

        keyword_str = self._pars.keyword
        base_str = self._pars.input_string
        regexp = re.search(keyword_str + "(\w+)", base_str)
        if not regexp:
            self._raise_config_exception(AcsConfigException.OPERATION_FAILED,
                                         "Keyword: %s was not found in -\n"
                                         "String: %s" % (keyword_str, base_str))
        result = regexp.group(1)
        self._logger.debug("%s result: %s", self.name, result)
        context.set_info(self._pars.save_as, result)
