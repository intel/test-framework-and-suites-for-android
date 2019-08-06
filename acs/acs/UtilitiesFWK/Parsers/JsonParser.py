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

import json

from acs.UtilitiesFWK.Parsers.IParser import IParser
from acs.UtilitiesFWK.Parsers.ParserUtil import get_dict_value_from_path
from acs.UtilitiesFWK.Parsers.ParserUtil import convert_as_list_of_elements


class JsonParser(dict, IParser):

    """
    This class parse JSON files
    """

    def __init__(self, file_path, file_schema=None):
        """
        :type file_path: str
        :param file_path: path to the file to parse
        :type file_schema: str
        :param file_schema: path to schema file to ensure file to parse integrity
        """
        self._file_path = file_path
        with open(file_path) as f:
            json_data = json.loads(f.read())
        if not isinstance(json_data, dict):
            raise TypeError("Cannot convert JSON data to a dictionary")
        # if no schema provided, try to find schema information from xml content
        if not file_schema:
            # retrieve the schema information from content
            file_schema = self.__retrieve_json_schema()
        if file_schema:
            file_schema = JsonSchema(file_schema)
            file_schema.assertValid(json_data)
        super(JsonParser, self).__init__(json_data)

    def keys(self):
        """
        Get all keys of the yaml parsed content

        :return: list of keys
        :rtype: list.
        """
        return super(JsonParser, self).keys()

    def get(self, path, default_value=None):
        """
        Get the value content specfied from parsed content

        :param path: key value or xpath like path
        :type  path: str.

        :return: content found at the key specified
        :rtype: Depends on key content
        """

        raw_value = get_dict_value_from_path(super(JsonParser, self), path, default_value)
        # xml xpath request return a list of nodes
        # emulate the same behavior on json
        value = convert_as_list_of_elements(raw_value)
        return value

    def get_parsed_content(self):
        """
        Get loaded json content

        :rtype: dict()
        :return: the content of file
        """
        return super(JsonParser, self)

    def __retrieve_json_schema(self):
        """
        Retrieve json schema filename from json data
        """
        # Not implemented
        return ""


class JsonSchema(object):

    """
    This class implements the json schema check.
    Not implemented yet.
    """

    def __init__(self, schema_file):
        self.__schema = schema_file

    def assertValid(self, tree):
        return True
