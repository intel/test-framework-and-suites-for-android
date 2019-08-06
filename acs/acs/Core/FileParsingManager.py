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


from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.Core.PathManager import Paths
import acs.UtilitiesFWK.Utilities as Utils


class FileParsingManager:

    """ FileParsingManager

        This class implements the File Parsing Manager.
        This manager takes XML files as inputs and parses them into dictionaries.
        It will parse:
        - use case catalog
        - bench config
        - equipment catalog
        - campaign
    """

    def __init__(self, bench_config_name, equipment_catalog, global_config):

        self._file_extention = ".xml"

        self._execution_config_path = Paths.EXECUTION_CONFIG
        self._equipment_catalog_path = Paths.EQUIPMENT_CATALOG

        self._bench_config_name = (bench_config_name if os.path.isfile(bench_config_name) else
                                   os.path.join(self._execution_config_path, bench_config_name + self._file_extention))

        self._equipment_catalog_name = equipment_catalog + self._file_extention
        self._global_config = global_config

        self._ucase_catalogs = None
        self._logger = LOGGER_FWK

    def parse_bench_config(self):
        """
        This function parses the bench config XML file into a dictionary.
        """

        def __parse_node(node):
            """
            This private function parse a node from bench_config parsing.

            :rtype: dict
            :return: Data stocked into a dictionnary.
            """
            dico = {}
            name = node.get('name', "")
            if name:
                # store all keys (except 'name')/value in a dict
                for key in [x for x in node.attrib if x != "name"]:
                    dico[key] = node.attrib[key]

            node_list = node.xpath('./*')
            if node_list:
                for node_item in node_list:
                    name = node_item.get('name', "")
                    if name:
                        dico[name] = __parse_node(node_item)
            return dico

        def __parse_bench_config(document):
            """
            Last version of function parsing bench_config adapted for Multiphone.

            :type document: object
            :param document: xml document parsed by etree

            :rtype: dict
            :return: Data stocked into a dictionary.
            """

            # parse bench_config (dom method)
            bench_config = {}
            node_list = document.xpath('/BenchConfig/*/*')

            for node in node_list:
                name = node.get('name', "")
                if name:
                    bench_config[name] = __parse_node(node)
            return bench_config

        # body of the parse_bench_config() function.
        if not os.path.isfile(self._bench_config_name):
            error_msg = "Bench config file : %s does not exist" % self._bench_config_name
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)

        try:
            document = et.parse(self._bench_config_name)
        except et.XMLSyntaxError:
            _, error_msg, _ = Utils.get_exception_info()
            error_msg = "{}; {}".format(self._bench_config_name, error_msg)
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

        result = __parse_bench_config(document)

        bench_config_parameters = Utils.BenchConfigParameters(dictionnary=result,
                                                              bench_config_file=self._bench_config_name)

        return bench_config_parameters

    def parse_equipment_catalog(self):
        """
        This function parses the equipment catalog XML file into a dictionary.
        """
        # Instantiate empty dictionaries
        eqt_type_dic = {}

        # Get the xml doc
        equipment_catalog_path = os.path.join(self._equipment_catalog_path, self._equipment_catalog_name)

        if not os.path.isfile(equipment_catalog_path):
            error_msg = "Equipment catalog file : %s does not exist" % equipment_catalog_path
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)

        try:
            equipment_catalog_doc = et.parse(equipment_catalog_path)
        except et.XMLSyntaxError:
            _, error_msg, _ = Utils.get_exception_info()
            error_msg = "{}; {}".format(equipment_catalog_path, error_msg)
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

        root_node = equipment_catalog_doc.xpath('/Equipment_Catalog')
        if not root_node:
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND,
                                     "Wrong XML: could not find expected document root node: "
                                     "'Equipment_Catalog'")
        # Parse EquipmentTypes
        list_eq_types = root_node[0].xpath('./EquipmentType')
        for eq_type in list_eq_types:
            eqt_type_dic.update(self._load_equipment_type(eq_type))

        self._global_config.equipmentCatalog = eqt_type_dic.copy()

    def _load_equipment_type(self, node):
        """
        This function parses an "EquipmentType" XML Tag into a dictionary
        :type node: Etree node
        :param node: the "EquipmentType" node
        :rtype dic: dict
        :return: a dictionary of equipment
        """
        dic = {}
        eqt_type_name = node.get("name", "")
        if eqt_type_name:
            dic[eqt_type_name] = self._load_equipments(node)
        return dic

    def _load_equipments(self, node):
        """
        This function parses "Equipment" XML Tags into a dictionary
        :type node: Etree node
        :param node: the node containing "Equipment" nodes
        """
        # Get common equipment type parameters
        dic = {}
        dic.update(self._get_parameters(node))
        eqt_nodes = node.xpath('./Equipment')
        for sub_node in eqt_nodes:
            eqt_model = sub_node.get("name", "")
            if eqt_model:
                dic[eqt_model] = self._get_parameters(sub_node)
                dic[eqt_model].update(self._load_transport(sub_node))
                dic[eqt_model].update(self._load_features(sub_node))
                dic[eqt_model].update(self._load_controllers(sub_node))
        return dic

    def _load_transport(self, node):
        """
        This function parses a "Transport" XML Tags from a node into a dictionary
        :type node: DOM node
        :param node: the node from which to get all parameters value
        :rtype dic: dict
        :return: a dictionary of transports
        """
        dic = {}
        transport_node = node.xpath('./Transports')
        if transport_node:
            dic["Transports"] = self._get_parameters(transport_node[0])
        return dic

    def _load_controllers(self, node):
        """
        This function parses a "Controllers" XML Tags from a node into a dictionary
        :type node: DOM node
        :param node: the node from which to get all parameters value
        :rtype dic: dict
        :return: the dictionary of controllers
        """
        dic = {}
        transport_node = node.xpath('./Controllers')
        if transport_node:
            dic["Controllers"] = self._get_parameters(transport_node[0])
        return dic

    def _load_features(self, node):
        """
        This function parses a "Features" XML Tags from a node into a dictionary
        :type node: Element node
        :param node: the node from which to get all parameters value

        :rtype dic: dict
        :return: a dictionary of features
        """
        dic = {}
        transport_node = node.xpath('./Features')
        if transport_node:
            dic["Features"] = self._get_parameters(transport_node[0])
        return dic

    def _get_parameters(self, node):
        """
        This function parses all "Parameter" XML Tags from a node into a dictionary
        :type node: Element node
        :param node: the node from which to get all parameters value

        :rtype dic: dict
        :return: a dictionary of parameters
        """
        dic = {}
        parameters = node.xpath('./Parameter')
        for parameter in parameters:
            name = parameter.get("name", "")
            value = parameter.get("value", "")
            if name:
                dic[name] = value
        return dic
