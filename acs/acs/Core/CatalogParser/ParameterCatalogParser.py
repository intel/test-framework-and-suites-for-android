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
:summary: This module implements Parameter Catalog parser
:since: 05/12/13
:author: ssavrim
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
