#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
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

@organization: INTEL MCG PSI
@summary: This module implements a generic Parser class
@since: 07/08/14
@author: kturban
"""

__organization__ = "INTEL MCG PSI"
__author__ = "sis-cta-team@intel.com"

import os
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.UtilitiesFWK.Parsers.JsonParser import JsonParser
from acs.UtilitiesFWK.Parsers.XMLParser import XMLParser
from acs.UtilitiesFWK.Parsers.YamlParser import YamlParser


class Parser(object):

    """
    Generic wrapper for parser
    """
    # could be more dynamic using "Utilities.Parsers.XMLParser"
    # but it requires to make more generic some piece of code from DeviceModuleFactory
    available_parsers = {".json": JsonParser,
                         ".yaml": YamlParser,
                         ".xml": XMLParser
                         }

    @staticmethod
    def get_parser(file_path, schema_file=None):
        """
        Get the right parser according to file path extension

        Schema file is not mandatory
        Moreover, if no schema file provided here, parser can try to find this information in parsed content

        :type file_path: str
        :param file_path: path to the file to parse
        :type schema_file: str
        :param schema_file: path to schema file to ensure file to parse integrity

        :rtype: a parser class
        :return: the parser class which handle the file format
        """
        if not os.path.isfile(file_path):
            error_msg = "Cannot parse {0}, the file was not found".format(file_path)
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)

        _, extension = os.path.splitext(file_path)
        if extension not in Parser.available_parsers:
            error_msg = "The {0} extension is not supported by the parser".format(extension)
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        try:
            parser = Parser.available_parsers[extension](file_path, schema_file)
        except Exception as e:
            error_msg = "Cannot instantiate parser : {0}".format(e)
            raise AcsConfigException(error_msg)
        return parser
