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
from acs.ErrorHandling.TestEquipmentException import TestEquipmentException
from acs.UtilitiesFWK.Utilities import Global, internal_shell_exec


class RunLocalCommand(TestStepBase):
    """
    Run local command
    """

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context

        Context parameters list:
        - cmd: command to be run
        - timeout: script execution timeout in sec
        - silent_mode: Display logs in ACS logger
        - save_as: context variable name where stdout of the command is put
        """
        TestStepBase.run(self, context)

        # Fetch params values
        command = self._pars.command
        timeout = self._pars.timeout
        silent_mode = self._pars.silent_mode
        command_result = self._pars.save_as

        exit_status, output = internal_shell_exec(cmd=command, timeout=timeout, silent_mode=silent_mode)
        if not silent_mode:
            self._logger.info("RunLocalCommand: output for {0} command: '{1}'".format(command, output))

        if exit_status == Global.FAILURE:
            raise TestEquipmentException(TestEquipmentException.COMMAND_LINE_ERROR,
                                         "RunCommand: Error at execution of '{0}' command: {1}".format(command, output))

        context.set_info(command_result, output)
