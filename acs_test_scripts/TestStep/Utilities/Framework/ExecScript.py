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
import os
import sys

from acs.Core.TestStep.TestStepBase import TestStepBase
from acs.Core.PathManager import Paths
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.AcsToolException import AcsToolException
from acs.ErrorHandling.DeviceException import DeviceException
from acs.ErrorHandling.TestEquipmentException import TestEquipmentException
from acs.UtilitiesFWK.ExecScriptCtx import init_ctx


class ExecScript(TestStepBase):
    """
    Execute an external python script
    """

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """
        TestStepBase.run(self, context)

        script = self.__get_script_path(self._pars.script_path)
        self.__exec_script(script, context)

    def __exec_script(self, script, context):
        # Initialize execution context
        global_values = globals()
        init_ctx(global_values, self._logger, self._global_conf)

        # Tune the execution context for exec script test step
        my_path = os.path.dirname(os.path.abspath(script))
        global_values["MY_PATH"] = my_path
        global_values["EXEC_TS"] = self
        global_values["CTX"] = context
        global_values["ERROR_DEVICE"] = ExecScript.__error_device
        global_values["ERROR_ACSTOOL"] = ExecScript.__error_acstool
        global_values["ERROR_ACSCONFIG"] = ExecScript.__error_acsconfig
        global_values["ERROR_EQUIPMENT"] = ExecScript.__error_equipment

        sys.path.append(my_path)
        current_dir = os.getcwd()
        try:
            execfile(script, global_values)
        finally:
            os.chdir(current_dir)

    def __get_script_path(self, script_path):
        execution_config_path = os.path.abspath(Paths.EXECUTION_CONFIG)

        new_path = script_path
        if not os.path.exists(script_path):
            new_path = os.path.join(execution_config_path, script_path)

        if not os.path.exists(new_path):
            new_path = os.path.join(execution_config_path, os.path.dirname(self._testcase_name), script_path)

        if not os.path.exists(new_path):
            raise AcsConfigException("Unable to find exec script with path {0}".format(new_path))
        else:
            return new_path

    @staticmethod
    def __error_device(message):
        raise DeviceException(message)

    @staticmethod
    def __error_acstool(message):
        raise AcsToolException(message)

    @staticmethod
    def __error_acsconfig(message):
        raise AcsConfigException(message)

    @staticmethod
    def __error_equipment(message):
        raise TestEquipmentException(message)
