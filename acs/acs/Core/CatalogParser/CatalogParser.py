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
import yaml

from lxml import etree
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class CatalogParser(object):

    """
    This class implements the Catalog Parser interface
    It is an entry point to parse xml files and return it as a dictionary

    It is a folder (i.e.: _Catalogs/UseCase) composed of
    a list of .xml files validated by a .xsd schema
    i.e.: _Catalogs/UseCase/usecase.xsd (MANDATORY to check the xml file)
                    /telephony.xml (MUST respect defined rules in usecase.xsd)
                    /cws/cws.xml (MUST respect defined rules in usecase.xsd)
    """

    ID_ATTRIB = "Id"
    DOMAIN_ATTRIB = "Domain"
    SUBDOMAIN_ATTRIB = "SubDomain"
    FEATURE_ATTRIB = "Feature"

    CLASSNAME_ELEM = "ClassName"
    DESCRIPTION_ELEM = "Description"
    PARAMETERS_ELEM = "Parameters"
    PARAMETER_ELEM = "Parameter"

    XML_SCHEMA_FILE = ""
    YAML_CONFIG_FILE = ""

    CATALOG_EXTENTION = ".xml"

    def __init__(self, catalog_paths):
        """
        Validate optional XML schema (xsd) & YAML logic files
        & load their contents

        :type catalog_paths: list
        :param catalog_paths: catalog paths list.
            Catalogs can come from different locations (acs, acs_test_scripts)
        """

        self._xml_schema = None
        self._yaml_config = None
        self._catalog_paths = catalog_paths

        if self.XML_SCHEMA_FILE and os.path.isfile(self.XML_SCHEMA_FILE):
            self._xml_schema = self.__load_xml_schema(self.XML_SCHEMA_FILE)

        if self.YAML_CONFIG_FILE and os.path.isfile(self.YAML_CONFIG_FILE):
            self._yaml_config = self.__load_yaml_config(self.YAML_CONFIG_FILE)

    def __load_xml_schema(self, xml_schema):
        """
        Load xml schema to validate the xml catalog

        :type xml_schema: string
        :param xml_schema: Xml schema to load

        :rtype: etree.XMLSchema
        :return: XML schema to validate the xml catalog file
        """

        try:
            return etree.XMLSchema(etree.parse(xml_schema))
        except etree.XMLSchemaParseError as xml_schema_error:
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR,
                                     "'%s' schema is invalid ! (%s)"
                                     % (xml_schema, str(xml_schema_error)))

    def __load_yaml_config(self, yaml_config):
        """
        Load YAML configuration to validate
        the xml catalog domain, subdomain & feature

        :type yaml_config: string
        :param yaml_config: YAML config to load

        :rtype: dict
        :return: dict of complete YAML file
        """

        try:
            with open(yaml_config) as f:
                return yaml.load(f)
        except yaml.scanner.ScannerError as yaml_config_error:
            raise AcsConfigException(AcsConfigException.YAML_PARSING_ERROR,
                                     "'%s' is invalid ! (%s)"
                                     % (yaml_config, str(yaml_config_error)))

    def __check_xml_schema(self, catalog_file):
        """
        Validate catalog file regarding loaded xml schema (if any)
        Return it as a dictionary

        :type catalog_file: string
        :param catalog_file: Catalog file to parse

        :rtype: etree.XML
        :return: X to validate the xml catalog file
        """

        try:
            # Parse the xml file
            catalog_etree = etree.parse(catalog_file)

            if catalog_etree and self._xml_schema:
                # Apply xml schema on the xml file
                self._xml_schema.assertValid(catalog_etree)

        except etree.Error as xml_parsing_error:
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR,
                                     "'%s' catalog is invalid ! (%s)"
                                     % (catalog_file, str(xml_parsing_error)))

        return catalog_etree

    def _check_xml_logic(self, catalog_file):
        """
        Validate catalog file regarding loaded YAML logic
        regarding to Domains, SubDomains & Features
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
                raise AcsConfigException(
                    AcsConfigException.YAML_PARSING_ERROR,
                    "'%s' file is invalid ! (DOMAINS section does not exists!)"
                    % self._yaml_config_file)

            for node in catalog_etree.getroot():
                item_id = node.attrib[CatalogParser.ID_ATTRIB]
                item_domain = node.attrib[CatalogParser.DOMAIN_ATTRIB]
                item_subdomain = node.attrib[CatalogParser.SUBDOMAIN_ATTRIB]
                item_feature = node.attrib[CatalogParser.FEATURE_ATTRIB]

                # Check that logic between Domain, SubDomain & Feature is respected
                item_features = self._check_subdomain(catalog_file,
                                                      item_id,
                                                      item_domain,
                                                      item_subdomain,
                                                      domains.keys(),
                                                      domains.get(item_domain))

                self._check_feature(catalog_file,
                                    item_id,
                                    item_subdomain,
                                    item_feature,
                                    item_features)

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

        :rtype: list
        :return: List of associated features when item_subdomain is validated
        """

        subdomains = self._yaml_config.get("SUB_DOMAINS")

        if not subdomains:
            raise AcsConfigException(
                AcsConfigException.YAML_PARSING_ERROR,
                "'%s' file is invalid ! (SUB_DOMAINS section does not exists!)"
                % self._yaml_config_file)
        elif possible_subdomains is None:
            raise AcsConfigException(
                AcsConfigException.XML_PARSING_ERROR,
                "'%s' is invalid ! (Domain %s is not valid for item %s; Expected values are %s)"
                % (catalog_file, str(item_domain),
                   str(item_id), str(possible_domains)))
        elif len(possible_subdomains) == 0:
            raise AcsConfigException(
                AcsConfigException.YAML_PARSING_ERROR,
                "'%s' file is invalid ! (no SubDomains exist for Domain %s)"
                % (self._yaml_config_file, str(item_domain)))
        elif item_subdomain not in possible_subdomains:
            raise AcsConfigException(
                AcsConfigException.XML_PARSING_ERROR,
                "'%s' catalog is invalid ! (SubDomain %s is not valid for item %s; Expected values are %s)"
                % (catalog_file, str(item_subdomain),
                   str(item_id), str(possible_subdomains)))
        else:
            return subdomains.get(item_subdomain)

    def _check_feature(self, catalog_file, item_id, item_subdomain,
                       item_feature, possible_features):
        """
        Validate Feature attributes using YAML config

        :type catalog_file: string
        :param catalog_file: Catalog file

        :type item_id: string
        :param item_id: Id of the item (UseCase or Test Step)

        :type item_subdomain: string
        :param item_subdomain: SubDomain to be checked

        :type item_feature: string
        :param item_feature: Feature to be checked

        :type possible_features: list
        :param possible_features: List of possible features

        :rtype: none
        :return: none
        """

        if possible_features is None:
            raise AcsConfigException(
                AcsConfigException.YAML_PARSING_ERROR,
                "'%s' is invalid ! (SubDomain %s does not exist)"
                % (self._yaml_config_file, str(item_subdomain)))
        elif len(possible_features) > 0 and item_feature not in possible_features:
            raise AcsConfigException(
                AcsConfigException.XML_PARSING_ERROR,
                "'%s' catalog is invalid ! (Feature %s is not valid for item %s; Expected values are %s)"
                % (catalog_file, str(item_feature),
                   str(item_id), str(possible_features)))
        elif len(possible_features) == 0 and len(item_feature) > 0:
            raise AcsConfigException(
                AcsConfigException.XML_PARSING_ERROR,
                "'%s' catalog is invalid ! (Feature %s is not valid for item %s; No features expected)"
                % (catalog_file, str(item_feature), str(item_id)))

    def validate_catalog_file(self, catalog_file):
        """
        Validate catalog file regarding xml schema & logic (if any)
        Return it as a dictionary

        :type catalog_file: string
        :param catalog_file: Catalog file to parse

        :rtype: etree.XML
        :return: X to validate the xml catalog file
        """

        catalog_etree = self.__check_xml_schema(catalog_file)

        if catalog_etree:
            self._check_xml_logic(catalog_file)

        return catalog_etree

    def parse_catalog_file(self, catalog_file):
        """
        Parse catalog and validate regarding loaded xml schema (if any)
        Return it as a dictionary

        :type catalog_file: string
        :param catalog_file: Catalog file to parse

        :rtype: dict
        :return: Dictionary containing catalog elements
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED,
                                 "'parse_catalog_file' is not implemented !")

    def parse_catalog_folder(self):
        """
        Parse folder(s) which are known to contain catalogs (usecases, test steps, parameters)
        If multiple catalogs are in the folder, it will return a concatenated dictionary.
        If a key is already defined in the dictionary, raise an AcsConfigException

        :type catalog_paths: list
        :param catalog_paths: catalog paths list. Catalogs can come from different locations (acs, acs_test_scripts)

        :type: dict
        :return: Dictionary containing catalog elements
        """
        concatenated_dictionary = {}

        for catalog_path in self._catalog_paths:
            for root, _, catalog_list in os.walk(catalog_path):
                for catalog_file in catalog_list:
                    if catalog_file.lower().endswith(self.CATALOG_EXTENTION):
                        temp_dictionary = self.parse_catalog_file(os.path.join(root, catalog_file))
                        for item_name in temp_dictionary.iterkeys():
                            if item_name in concatenated_dictionary:
                                raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR,
                                                         "item '%s' is defined more than one time !" % item_name)
                        concatenated_dictionary.update(temp_dictionary)

        return concatenated_dictionary
