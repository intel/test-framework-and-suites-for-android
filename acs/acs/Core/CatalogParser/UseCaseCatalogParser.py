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
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from lxml import etree


class UseCaseCatalogParser(CatalogParser):

    """
    This class implements the Catalog Parser for acs.UseCase.

    .. uml::

        class UseCaseCatalogParser {
            parse_catalog_file(catalog_file)
        }

        CatalogParser <|- UseCaseCatalogParser
    """
    XML_SCHEMA_FILE = os.path.join(Paths.FWK_USECASE_CATALOG, "usecase.xsd")
    YAML_CONFIG_FILE = os.path.join(Paths.TEST_SCRIPTS_USECASE_CATALOG, "usecase.yaml")

    def __init__(self):
        catalog_paths = [Paths.FWK_USECASE_CATALOG, Paths.TEST_SCRIPTS_USECASE_CATALOG]
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
        usecase_dictionary = {}
        # Validate and parse the xml file
        usecase_catalog_etree = self.validate_catalog_file(catalog_file)

        if usecase_catalog_etree:
            for usecase_node in usecase_catalog_etree.getroot():
                # Get the usecase Id
                if CatalogParser.ID_ATTRIB in usecase_node.attrib:
                    usecase_name = usecase_node.attrib[CatalogParser.ID_ATTRIB]
                    usecase_dictionary[usecase_name] = {}

                    for usecase_children in usecase_node:
                        # Get ClassName, Description of the usecase
                        if usecase_children.tag in [CatalogParser.CLASSNAME_ELEM, CatalogParser.DESCRIPTION_ELEM]:
                            usecase_dictionary[usecase_name][usecase_children.tag] = usecase_children.text

        # TODO: UC parameters are not yet parsed due to the fact that AWI Release 1.0 does not yet imports them.
        # TODO: This will need to be changed for future AWI releases.

        return usecase_dictionary

    def _check_subdomain(self,
                         catalog_file,
                         item_id,
                         item_domain,
                         item_subdomain,
                         possible_domains,
                         possible_subdomains):
        """
        Validate SubDomain attributes using YAML config

        :type catalog_file: string
        :param catalog_file: Catalog file

        :type item_id: string
        :param item_id: Id of the item (UseCase or Test Step)

        :type item_domain: string
        :param item_domain: Domain to be checked

        :type item_subdomain: string
        :param item_subdomain: SubDomain to be checked

        :type possible_domains: list
        :param possible_domains: List of possible domains

        :type possible_subdomains: list
        :param possible_subdomains: List of possible subdomains

        """

        if possible_subdomains is None:
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR,
                                     "'%s' is invalid ! (Domain %s is not valid for item %s; Expected values are %s)"
                                     % (catalog_file, str(item_domain), str(item_id), str(possible_domains)))
        elif len(possible_subdomains) == 0:
            raise AcsConfigException(AcsConfigException.YAML_PARSING_ERROR,
                                     "'%s' file is invalid ! (no SubDomains exist for Domain %s)"
                                     % (self._yaml_config_file, str(item_domain)))
        elif item_subdomain not in possible_subdomains:
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR,
                                     "'%s' catalog is invalid ! (SubDomain %s is not valid for item %s; Expected values are %s)"  # NOQA
                                     % (catalog_file, str(item_subdomain), str(item_id), str(possible_subdomains)))

    def _check_xml_logic(self, catalog_file):
        """
        Validate catalog file regarding loaded YAML logic
        regarding to Domains &SubDomains
        Return a boolean setting if xml file logic is valid

        :type catalog_file: string
        :param catalog_file: Catalog file to parse

        :rtype: none
        :return: none
        """

        # Parse the xml file
        catalog_etree = etree.parse(catalog_file)

        if catalog_etree and self._yaml_config:

            domains = self._yaml_config.get("DOMAINS")
            if not domains:
                raise AcsConfigException(AcsConfigException.YAML_PARSING_ERROR,
                                         "'%s' file is invalid ! (DOMAINS section does not exists!)"
                                         % self._yaml_config_file)

            for node in catalog_etree.getroot():
                item_id = node.attrib[CatalogParser.ID_ATTRIB]
                item_domain = node.attrib[CatalogParser.DOMAIN_ATTRIB]
                item_subdomain = node.attrib[CatalogParser.SUBDOMAIN_ATTRIB]

                # Check that logic between Domain, SubDomain is respected
                self._check_subdomain(catalog_file,
                                      item_id,
                                      item_domain,
                                      item_subdomain,
                                      domains.keys(),
                                      domains.get(item_domain))
