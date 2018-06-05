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
