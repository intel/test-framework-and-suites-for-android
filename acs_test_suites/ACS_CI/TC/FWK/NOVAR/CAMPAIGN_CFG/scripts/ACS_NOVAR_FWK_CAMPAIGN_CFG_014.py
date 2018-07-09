# @PydevCodeAnalysisIgnore
# pylint: disable=E0602,W0212
# flake8: noqa
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
"""
DEVICE   => ACS phone instance, check IPhone interface
DEVICE.run_cmd => if you do adb shell cmd, please do not add the \"
                 e.g: "adb shell echo hello" instead of
                      "adb shell \"echo hello\""

IO_CARD => IOCard instance (usb relay or ariane board), check IIOCard interface

PRINT_INFO  => log std message in ACS log
PRINT_DEBUG => log debug message in ACS log
PRINT_ERROR => log error message in ACS log
LOCAL_EXEC => run local cmd on the bench
TC_PARAMETERS => get a paramater value from xml test case file. Name of this parameter is defined by the user.

REPORT_PATH => path of the ACS report folder
MY_PATH => folder path of the python scritp

CREATE SECOND REPORT:
ADD_RESULT("TEST_1", PASS, "test 1 comment")
ADD_RESULT("TEST_2", FAIL, ["test 2 sub_comment", "test 2 sub_comment"])
ADD_RESULT("TEST_3", BLOCKED, "test 3 comment")

VERDICT => verdict of the test, SUCCESS or FAILURE
OUTPUT  => message that will be displayed in ACS report
           (mostly used in case of error)
"""

(max_attempts, acceptance) = EXEC_UC.get_acceptance_criteria()

if acceptance == 1:
    VERDICT = SUCCESS
else:
    VERDICT = FAILURE
