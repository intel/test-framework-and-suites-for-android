"""

:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described herein and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

:organization: INTEL MCG PSI

:since: 2012-06-08
:author: sfusilie
"""
from acs.Core.Report.SecondaryTestReport import SecondaryTestReport
from acs.UseCase.UseCaseBase import UseCaseBase
from acs.UtilitiesFWK.ExecScriptCtx import init_ctx
from acs.UtilitiesFWK.Utilities import Global

import os
import sys


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
