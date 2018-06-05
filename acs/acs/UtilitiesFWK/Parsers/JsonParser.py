__copyright__ = """ (c)Copyright 2013, Intel Corporation All Rights Reserved.
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
"""

__organization__ = "INTEL MCG PSI"
__author__ = "sis-cta-team@intel.com"

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
