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

import os
import sys

from acs.Core.Report.SecondaryTestReport import SecondaryTestReport
from acs.UseCase.UseCaseBase import UseCaseBase
from acs.UtilitiesFWK.ExecScriptCtx import init_ctx
from acs.UtilitiesFWK.Utilities import Global


class ExecScript(UseCaseBase):

    """
    Generic use case that run shell commands and extract the verdict
    from the exec return code or by parsing the stdout
    """

    def __init__(self, tc_name, global_config):
        """
        Constructor
        """
        UseCaseBase.__init__(self, tc_name, global_config)

        self.__setup_script = self._tc_parameters.get_param_value("SETUP_SCRIPT_PATH")
        self.__run_script = self._tc_parameters.get_param_value("SCRIPT_PATH")
        self.__teardown_script = self._tc_parameters.get_param_value("TEAR_DOWN_SCRIPT_PATH")
        self.__finalize_script = self._tc_parameters.get_param_value("FINALIZE_SCRIPT_PATH")

        self.__verdict = None
        self.__message = None

        self.__tc_report = SecondaryTestReport(self._device.get_report_tree().get_report_path())

    def __add_result(self, tc_name, tc_result, tc_comment):
        self.__tc_report.add_result(tc_name, tc_result, tc_comment,
                                    self.get_name(), self.tc_order)

    def __get_script_path(self, script_path):
        new_path = script_path
        if not os.path.exists(script_path):
            new_path = os.path.join(self._execution_config_path, script_path)

        if not os.path.exists(new_path):
            new_path = os.path.join(self._execution_config_path,
                                    os.path.dirname(self._name),
                                    script_path)

        if not os.path.exists(new_path):
            return Global.FAILURE, new_path
        else:
            return Global.SUCCESS, new_path

    def __exec_script(self, script):
        # Initialize execution context
        global_values = globals()
        init_ctx(global_values, self._logger, self._global_conf)

        # Tune the execution context for the EXEC_SCRIPT
        my_path = os.path.dirname(os.path.abspath(script))
        global_values["MY_PATH"] = my_path
        global_values["EXEC_UC"] = self
        global_values["TC_PARAMETERS"] = self._tc_parameters.get_param_value
        global_values["ADD_RESULT"] = self.__add_result
        global_values["PASS"] = self.__tc_report.verdict.PASS
        global_values["BLOCKED"] = self.__tc_report.verdict.BLOCKED
        global_values["FAIL"] = self.__tc_report.verdict.FAIL

        sys.path.append(my_path)
        current_dir = os.getcwd()
        try:
            execfile(script, global_values)
        finally:
            os.chdir(current_dir)

        return global_values["VERDICT"], global_values["OUTPUT"]

    # TODO
    # Support any script execution thru a std popen call
    # Serialize in pickle json all additionnal parameters defined by the test
    # in the environment variable "TC_PARAMETERS", "MY NAME", "ORDER" (to allow populate secondary report)

    def set_up(self):
        UseCaseBase.set_up(self)

        if self.__setup_script is not None:
            result, full_path = self.__get_script_path(self.__setup_script)
            if result == Global.FAILURE:
                return Global.FAILURE, "Cannot find %s" % self.__setup_script
            self.__setup_script = full_path

        result, full_path = self.__get_script_path(self.__run_script)
        if result == Global.FAILURE:
            return Global.FAILURE, "Cannot find %s" % self.__run_script
        self.__run_script = full_path

        if self.__teardown_script is not None:
            result, full_path = self.__get_script_path(self.__teardown_script)
            if result == Global.FAILURE:
                return Global.FAILURE, "Cannot find %s" % self.__teardown_script
            self.__teardown_script = full_path

        if self.__finalize_script is not None:
            result, full_path = self.__get_script_path(self.__finalize_script)
            if result == Global.FAILURE:
                return Global.FAILURE, "Cannot find %s" % self.__finalize_script
            self.__finalize_script = full_path

        verdict = Global.SUCCESS
        message = "Success"
        if self.__setup_script is not None:
            verdict, message = self.__exec_script(self.__setup_script)

        return verdict, message

    def run_test(self):
        UseCaseBase.run_test(self)

        if self.__run_script is not None:
            verdict, message = self.__exec_script(self.__run_script)
        else:
            verdict = Global.FAILURE
            message = "No script to run !"

        return verdict, message

    def tear_down(self):
        UseCaseBase.tear_down(self)

        verdict = Global.SUCCESS
        message = "Success"
        if self.__teardown_script is not None:
            verdict, message = self.__exec_script(self.__teardown_script)

        return verdict, message

    def finalize(self):
        UseCaseBase.finalize(self)

        verdict = Global.SUCCESS
        message = "Success"
        if self.__finalize_script is not None:
            verdict, message = self.__exec_script(self.__finalize_script)

        return verdict, message
