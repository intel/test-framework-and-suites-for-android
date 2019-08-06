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
import lxml.etree as et

from acs.UtilitiesFWK.Parsers.IParser import IParser

XSI = "http://www.w3.org/2001/XMLSchema-instance"


class XMLParser(IParser):

    """
   This class parse XML files
    """

    def __init__(self, file_path, file_schema=None):
        """
        :type file_path: str
        :param file_path: path to the file to parse
        :type file_schema: str
        :param file_schema: path to schema file to ensure file to parse integrity
        """
        self.__file_path = file_path
        self.__tree = None
        self._local_dict = {}
        parser = et.XMLParser(remove_blank_text=True, remove_comments=True)

        try:
            self.__tree = et.parse(self.__file_path, parser)
            # if no schema provided, try to find schema information from xml content
            if not file_schema:
                # retrieve the schema information from content
                file_schema = self.__retrieve_xml_schema()
            if file_schema:
                file_schema = self.__load_shema(file_schema)
                file_schema.assertValid(self.__tree)
        except et.XMLSyntaxError as ex:
            raise IOError("%s is corrupted: %s" % (self.__file_path, str(ex)))

    def keys(self):
        """
        Get all node name of the content

        :return: list of keys
        :rtype: list.
        """
        return [self.__tree.getroot().tag]

    def get(self, path, default_value=None):
        """
        Get the value content specified from parsed content

        :param path: key value or xpath like path
        :type  key: str

        :param default_value: default value returned if not found
        :type default_value: str

        :return: content found at the key specified
        :rtype: list
        """
        value = default_value
        if self.__tree is not None:
            value = self.__tree.xpath(path)

        return value

    def get_parsed_content(self):
        """
        Get loaded xml content

        :rtype: etree.Elements
        :return: parsed xml content
        """
        return self.__tree

    def __retrieve_xml_schema(self):
        """
        Retrieve xml schema filename from xml data
        """
        xsd_file = ""
        schema_locations = self.__tree.xpath("//*/@xsi:noNamespaceSchemaLocation", namespaces={'xsi': XSI})
        if schema_locations:
            directory_file = os.path.dirname(self.__file_path)
            schema_file = os.path.normpath(schema_locations[0])
            xsd_file = os.path.join(directory_file, schema_file)
        return xsd_file

    def __load_shema(self, file_schema):
        """
        Load xml schema to validate the xml catalog

        :type file_schema: string
        :param file_schema: Xml schema to load

        :rtype: etree.XMLSchema
        :return: XML schema to validate the xml catalog file
        """
        if not os.path.isfile(file_schema):
            raise IOError("'%s' schema not found !" % file_schema)
        try:
            return et.XMLSchema(et.parse(file_schema))
        except et.XMLSchemaParseError as xml_schema_error:
            raise IOError("'%s' schema is invalid ! (%s)" % (file_schema, str(xml_schema_error)))
