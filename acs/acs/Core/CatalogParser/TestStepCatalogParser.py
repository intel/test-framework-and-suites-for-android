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
from acs.Core.CatalogParser.CatalogParser import CatalogParser
from acs.Core.PathManager import Paths


class TestStepCatalogParser(CatalogParser):

    """
    This class implements the Catalog Parser for TestStep.

    .. uml::

        class TestStepCatalogParser {
            parse_catalog_file(catalog_file)
        }

        CatalogParser <|- TestStepCatalogParser
    """
    XML_SCHEMA_FILE = os.path.join(Paths.FWK_TESTSTEP_CATALOG, "teststep.xsd")
    YAML_CONFIG_FILE = os.path.join(Paths.TEST_SCRIPTS_TESTSTEP_CATALOG, "teststep.yaml")

    def __init__(self):
        catalog_paths = [Paths.FWK_TESTSTEP_CATALOG, Paths.TEST_SCRIPTS_TESTSTEP_CATALOG]
        CatalogParser.__init__(self, catalog_paths)

    def parse_catalog_file(self, catalog_file):
        """
        Parse catalog and validate regarding loaded xml schema and/or YAML logic
        Return it as a dictionary

        :type catalog_file: str
        :param catalog_file: Catalog file to parse

        :rtype: dict
        :return: Dictionary containing catalog elements
        """
        teststep_dictionary = {}
        # Validate and parse the xml file
        teststep_catalog_etree = self.validate_catalog_file(catalog_file)

        if teststep_catalog_etree:
            for teststep_node in teststep_catalog_etree.getroot():
                # Get the teststep Id
                if CatalogParser.ID_ATTRIB in teststep_node.attrib:
                    teststep_name = teststep_node.attrib[CatalogParser.ID_ATTRIB]
                    teststep_dictionary[teststep_name] = {}

                    for teststep_children in teststep_node:
                        # Get ClassName, Description of the teststep
                        if teststep_children.tag in [CatalogParser.CLASSNAME_ELEM, CatalogParser.DESCRIPTION_ELEM]:
                            teststep_dictionary[teststep_name][teststep_children.tag] = teststep_children.text
                        # Get Parameters of the teststep
                        elif teststep_children.tag == CatalogParser.PARAMETERS_ELEM:
                            teststep_dictionary[teststep_name][teststep_children.tag] = {}
                            for teststep_parameter_node in teststep_children:
                                if teststep_parameter_node.tag in CatalogParser.PARAMETER_ELEM:
                                    # Retrieve type, isOptional attributes
                                    parameter_dict = {"Type": teststep_parameter_node.attrib["type"],
                                                      "isOptional": teststep_parameter_node.attrib["isOptional"]}

                                    # Retrieve PossibleValues, DefaultValue, Blank if any
                                    for teststep_parameter_children in teststep_parameter_node:
                                        parameter_dict.update(
                                            {teststep_parameter_children.tag: teststep_parameter_children.text})
                                    # Add parameters elements in the dictionary
                                    teststep_dictionary[teststep_name][teststep_children.tag].update(
                                        {teststep_parameter_node.attrib["name"]: parameter_dict})
        return teststep_dictionary


if __name__ == "__main__":
    import time
    import os

    cwd = os.getcwd()
    ts_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(ts_path)

    t_0 = time.time()
    teststep_catalog_parser = TestStepCatalogParser()
    ts_catalog_dict = teststep_catalog_parser.parse_catalog_folder()
    for test_step in ts_catalog_dict.iterkeys():
        print (test_step + ": " + str(ts_catalog_dict[test_step]["Parameters"]))
    print time.time() - t_0

    os.chdir(cwd)
