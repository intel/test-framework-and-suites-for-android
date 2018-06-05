"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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

:organization: INTEL MCG PSI
:summary: This module implements TestStep Catalog parser
:since: 03/12/13
:author: ssavrim
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
