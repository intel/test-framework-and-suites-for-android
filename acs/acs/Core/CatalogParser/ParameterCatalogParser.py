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
import time
from CatalogParser import CatalogParser
from acs.Core.PathManager import Paths
from acs.UtilitiesFWK.Utilities import str_to_bool

PARAMETER_NAME_TAG = "name"
OVERRIDE_ATTRIB = "override"


class ParameterCatalogParser(CatalogParser):

    """
    This class implements the Catalog Parser for Parameter
    """
    XML_SCHEMA_FILE = os.path.join(Paths.FWK_PARAMETER_CATALOG, "parameter.xsd")

    def __init__(self):
        catalog_paths = [Paths.PARAMETER_CATALOG]
        CatalogParser.__init__(self, catalog_paths)

    def parse_catalog_file(self, catalog_file):
        """
        Parse catalog and validate regarding loaded xml schema (if any)
        Return it as a dictionary

        :type catalog_file: string
        :param catalog_file: Catalog file to parse

        :rtype: dict
        :return: Dictionary containing catalog elements
        """
        parameter_dictionary = {}
        # Validate and parse the xml file
        parameter_catalog_etree = self.validate_catalog_file(catalog_file)

        if parameter_catalog_etree:
            for parameter_node in parameter_catalog_etree.getroot():
                # Get the parameter name
                if PARAMETER_NAME_TAG in parameter_node.attrib:
                    parameter_name = parameter_node.attrib[PARAMETER_NAME_TAG]
                    parameter_dictionary[parameter_name] = {}

                    for parameter_children in parameter_node:
                        # Get all element of the parameter node
                        if OVERRIDE_ATTRIB not in parameter_children.attrib:
                            parameter_dictionary[parameter_name][parameter_children.tag] = parameter_children.text
                        else:
                            parameter_dictionary[parameter_name][parameter_children.tag] = \
                                (str_to_bool(parameter_children.attrib[OVERRIDE_ATTRIB]), parameter_children.text)
        return parameter_dictionary


if __name__ == "__main__":
    t_0 = time.time()

    cwd = os.getcwd()
    ts_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(ts_path)

    parameter_catalog_parser = ParameterCatalogParser()
    ts_catalog_dict = parameter_catalog_parser.parse_catalog_folder()
    print ts_catalog_dict
    for param in ts_catalog_dict.iterkeys():
        print (param + ": " + str(ts_catalog_dict[param]))
    print time.time() - t_0
