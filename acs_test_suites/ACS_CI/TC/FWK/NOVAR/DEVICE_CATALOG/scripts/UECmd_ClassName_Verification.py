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
DEVICE   => ACS phone instance,  check IPhone interface
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
MY_PATH => folder path of the python script

CREATE SECOND REPORT:
ADD_RESULT("TEST_1", PASS, "test 1 comment")
ADD_RESULT("TEST_2", FAIL, ["test 2 sub_comment", "test 2 sub_comment"])
ADD_RESULT("TEST_3", BLOCKED, "test 3 comment")

VERDICT => verdict of the test, SUCCESS or FAILURE
OUTPUT  => message that will be displayed in ACS report
           (mostly used in case of error)
"""
import acs.UtilitiesFWK.Utilities as Utils
from acs.Core.PathManager import Paths
from lxml import etree
import os
import fnmatch

VERDICT = FAILURE
OUTPUT = "Test fail class or uecmd can not be instantiate"
bool_instantiate_all_class_name = True
bool_instantiate_all_ue_cmd = True

# Parse Device catalog
list_ClassName = []
list_UECmd = []
for root, dirnames, filenames in os.walk(Paths.DEVICE_MODELS_CATALOG):
    for filename in fnmatch.filter(filenames, '*.xml'):
        device_cfg_path = os.path.join(root, filename)
        device_cfg = etree.parse(device_cfg_path)

        list_ClassName.extend(device_cfg.xpath("//Parameter[@ClassName]"))
        list_UECmd.extend(device_cfg.xpath("//Parameter[@UECmd]"))

# Check if all class name can be instantiate
for dict_class_name in list_ClassName:
    class_name = dict_class_name.attrib['ClassName']
    if Utils.get_class(class_name):
        OUTPUT = "%s is instantiate" % class_name
    else:
        bool_instantiate_all_class_name = False
        OUTPUT = "Test fail %s can not be instantiate" % class_name

# Check if all UECmd can be instantiate
for dict_ue_cmd in list_UECmd:
    ue_cmd = dict_ue_cmd.attrib['UECmd']
    ue_cmd_factory = "%s%s" % (ue_cmd, ".Factory.Factory")
    if Utils.get_class(ue_cmd_factory):
        OUTPUT = "%s is instantiate" % ue_cmd_factory
    else:
        bool_instantiate_all_ue_cmd = False
        OUTPUT = "Test fail %s can not be instantiate" % ue_cmd_factory

if bool_instantiate_all_class_name and bool_instantiate_all_ue_cmd:
    VERDICT = SUCCESS
    OUTPUT = "All class name and all UECmd are instantiate"
else:
    VERDICT = FAILURE
