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


class GlueCommand(TestStepBase):
    """
    This command is used to create a new string out of minimum 2 and max 3 pieces
    """

    def run(self, context):
        TestStepBase.run(self, context)
        piece1_str = self._pars.piece1
        piece2_str = self._pars.piece2
        output = "{0} {1}".format(piece1_str, piece2_str)
        if self._pars.piece3:
            output = "{0} {1}".format(output, self._pars.piece3)
        self._logger.info("Glued Output: %s", output)
        context.set_info(self._pars.save_as, output)
