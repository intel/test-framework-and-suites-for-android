#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

__copyright__ = """
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
:summary: This module ensure that each Device Model defined
          in the Catalog (Test Scripts) respect the XSD contract.

.. note:: For now (non-exhaustive list), 4 Device Models exists :

    * Android
    * Windows
    * Linux
    * Misc

Parameters :

    * OS_FAMILY => The Device Model OS family (Android, Windows, Linux, ...)

    .. note:: This parameter is optional. If you don't provide it all Device Model(s) are to be checked!

        You can also pass more than one OS family, separated with semicolon (Android;Linux).

EXEC_SCRIPT Globals Reminder ::

DEVICE   => ACS phone instance,  check IPhone interface
DEVICE.run_cmd => if you do adb shell cmd, please do not add the \"
                 e.g: "adb shell echo hello" instead of
                      "adb shell \"echo hello\""

IO_CARD => IOCard instance (usb relay or ariane board), check IIOCard interface

PRINT_INFO  => log std message in ACS log
PRINT_DEBUG => log debug message in ACS log
PRINT_ERROR => log error message in ACS log
LOCAL_EXEC => run local cmd on the bench
TC_PARAMETERS => get a parameter value from xml test case file. Name of this parameter is defined by the user.

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
import os
import fnmatch
import os.path as path

from lxml import etree
from acs.Core.PathManager import Paths


def check():
    """
    Performs All checks.

    :return: The list of invalid file(s) found, if any
    :rtype: tuple

    .. note:: Returns a tuple of 2 lists :

        * Invalid Device model(s) file(s) with error(s) details as a tuple of 2 elements.
        * Valid Device model(s) file(s) as a string.


    """
    global OS_FAMILY, OUTPUT, DEVICE_MODELS_CATALOG, FWK_DEVICE_MODELS_CATALOG

    invalid, valid = [], []
    device_models_families = os.listdir(DEVICE_MODELS_CATALOG)

    if not OS_FAMILY:
        OS_FAMILY = device_models_families

    for family in OS_FAMILY:

        family_path = path.abspath(path.join(DEVICE_MODELS_CATALOG, family))
        if not path.isdir(family_path):
            OUTPUT += 'This Device Model OS family : {0} was not found at : {1}'.format(family, family_path)
            OUTPUT += '\n\nAvailable Families are : {0}'.format(tuple(device_models_families))
            continue

        previous_schema_abspath, current_schema_abspath = "", ""
        for root, dirnames, filenames in os.walk(family_path):
            for filename in fnmatch.filter(filenames, '*.xml'):
                full_name = path.join(root, filename)
                try:
                    # Parse the xml file
                    catalog_tree = etree.parse(full_name)
                    if catalog_tree:
                        # Apply xml schema on the xml file
                        catalog_tree_root = catalog_tree.getroot()
                        schema_relpath = catalog_tree_root.attrib.get(SCHEMA_LOCATION_KEY)
                        if not schema_relpath:
                            invalid.append((full_name[len(DEVICE_MODELS_CATALOG) + 1:],
                                            "Does not define an 'xsi:noNamespaceSchemaLocation' in root element!"))
                            continue

                        schema_basename = path.basename(schema_relpath)
                        current_schema_abspath = path.abspath(path.join(FWK_DEVICE_MODELS_CATALOG, schema_basename))
                        if current_schema_abspath != previous_schema_abspath:
                            if not path.isfile(current_schema_abspath):
                                OUTPUT += SCHEMA_ERROR_MSG.format(current_schema_abspath, full_name)
                                continue

                            xml_schema = etree.XMLSchema(etree.parse(current_schema_abspath))
                            previous_schema_abspath = current_schema_abspath

                            if not xml_schema.validate(catalog_tree):
                                invalid.append((full_name[len(DEVICE_MODELS_CATALOG) + 1:], xml_schema.error_log))
                            else:
                                valid.append(full_name[len(DEVICE_MODELS_CATALOG) + 1:])

                except etree.XMLSchemaParseError as etree_error:
                    OUTPUT += SCHEMA_ERROR_MSG.format(current_schema_abspath, full_name)
                    OUTPUT += '\n\n{0}'.format(etree_error)

                except etree.Error as e:
                    OUTPUT += "'{0}' catalog seems to be corrupted ! ({1})".format(full_name, e)

    return invalid, valid


def report_valid_models():
    """
    Reports the Valid Device Model(s) file(s)

    """
    global VALID_DEVICE_MODELS, OUTPUT

    if VALID_DEVICE_MODELS:
        OUTPUT += "\n\n{0} VALID DEVICE MODEL CATALOG(S) FOUND IN : {1} folder !\n".format(len(VALID_DEVICE_MODELS),
                                                                                           DEVICE_MODELS_CATALOG)
        for idx, valid in enumerate(VALID_DEVICE_MODELS):
            OUTPUT += '\n\t{0}. "{1}"'.format(idx + 1, valid)


def report_invalid_models():
    """
    Reports the Invalid Device Model(s) file(s)

    """
    global INVALID_DEVICE_MODELS, OUTPUT

    OUTPUT += ("\n\n{0} INVALID DEVICE MODEL CATALOG(S) FOUND IN :"
               " {1} folder !\n").format(len(INVALID_DEVICE_MODELS), DEVICE_MODELS_CATALOG)
    for idx, invalids in enumerate(INVALID_DEVICE_MODELS):
        OUTPUT += '\n\n{idx}. "{0}" (Errors Details) :\n\n{1}'.format(*invalids, idx=idx + 1)


# Checking The Selected OS Device Catalog (Android, Linux, Windows, Mac, ...)
OUTPUT = ""
SCHEMA_LOCATION_KEY = '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'
SCHEMA_ERROR_MSG = '\nThe XML Schema ({0}) for file "{1}" seems not valid!'

FWK_DEVICE_MODELS_CATALOG = Paths.FWK_DEVICE_MODELS_CATALOG
DEVICE_MODELS_CATALOG = Paths.DEVICE_MODELS_CATALOG

OS_FAMILY = TC_PARAMETERS('OS_FAMILY', "")

if OS_FAMILY:
    OS_FAMILY = str(OS_FAMILY).split(';')

INVALID_DEVICE_MODELS, VALID_DEVICE_MODELS = check()

# Invalid Device Model(s) found !
if INVALID_DEVICE_MODELS:
    VERDICT = FAILURE
    report_invalid_models()
else:
    VERDICT = SUCCESS
    report_valid_models()
