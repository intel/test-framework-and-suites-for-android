#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
