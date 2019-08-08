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
import platform

import lxml.etree as et

import acs.UtilitiesFWK.Utilities as Utils
from acs.Core.CampaignConf import CampaignConf
from acs.Core.CatalogParser.CatalogParser import CatalogParser
from acs.Core.PathManager import Paths
from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.Core.TestCaseConf import TestCaseConf
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class DefaultCampaignGenerator(object):

    """
    This generator is responsible of parsing ACS campaign file. It's the legacy implementation that will load
    the campaign as it is described in the file itself.
    """

    def __init__(self, global_config):
        self._global_config = global_config
        self._logger = LOGGER_FWK
        self._file_extension = ".xml"

        self._ucase_catalogs = self._global_config.usecaseCatalog
        self._files_in_test_suites = None

    @property
    def files_in_test_suites(self):
        if self._files_in_test_suites is None:
            self._files_in_test_suites = self._parse_test_suites()
        return self._files_in_test_suites

    def _parse_test_suites(self):
        """
        This method will populate execution folder with test suites content to allow TC to be parsed by the generator.
        If qcl_test_suites is acs_test_suites, all the content will be copied
        If not, only "some" parts of acs_test_suites will be copied.

        :param qcl_test_suites: path of the test suites to handle
        :type qcl_test_suites: str

        :return: test suites path once copy is done
        :rtype: str
        """
        test_suites = os.path.abspath(os.path.expanduser(Paths.TEST_SUITES))
        existing_files = {}
        for root, dirs, files in os.walk(test_suites):
            for f in files:
                fname, ext = os.path.splitext(f)
                if ext != self._file_extension:
                    continue
                existing_files.setdefault(fname, []).append(os.path.join(root, fname))
        return existing_files

    def _find_obj_in_test_suites(self, name, errors):
        found_obj = self.files_in_test_suites.get(name)
        if found_obj is None:
            errors.append('{} does not exist'.format(name))
        elif len(found_obj) != 1:
            self._logger.warning("Got multiple occurences of {}. Taking the first one".format(name))
            return found_obj[0]
        else:
            # len cannot be == 0 as we have setdefault(name, []).append above
            return found_obj[0]

    def _find_campaign_path(self, campaign_name):
        campaign_file_path = (os.path.normpath(campaign_name)
                              if os.path.isfile(os.path.normpath(campaign_name))
                              else os.path.normpath(
                                  os.path.join(Paths.EXECUTION_CONFIG,
                                               campaign_name + self._file_extension)))

        if not os.path.isfile(campaign_file_path):
            error_msg = "Campaign file not found : %s !" % (campaign_file_path,)
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)
        return campaign_file_path

    def load(self, **kwargs):
        """
        This function parses the campaign config XML file into two lists:
            full test case list to execute + subcampaign file list.
        It also read TestCases XML files and store them.

        :return name of a list containing all TestCaseConf +
            a list containing all CampaignConf ordered as in the campaign XML
        :rtype Tuple of TestCaseConf list, CampaignConf list
        """
        campaign_name = os.path.normpath(kwargs["campaign_name"])

        campaign_file_path = self._find_campaign_path(campaign_name)

        sub_campaign_list, tc_list = self._load_campaign(campaign_file_path)

        return campaign_file_path, tc_list, sub_campaign_list

    def _parse_campaign_file_path(self, campaign_file_path):
        # XML parser parses the campaign config file
        try:
            return et.parse(campaign_file_path)
        except et.XMLSyntaxError:
            _, error_msg, _ = Utils.get_exception_info()
            self._logger.error("Campaign file is corrupted : parsing-reading issue in {0}".format(campaign_file_path))
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

    def _load_campaign(self, campaign_file_path):
        group_id = 0
        parent_campaign_list = []
        campaign_config_doc = self._parse_campaign_file_path(campaign_file_path)
        # Add this parameter for backward compatibility
        # On old version of the campaign file, this parameter
        # does not exists, so add it quietly with None as value.
        self._global_config.campaignConfig["testEnv"] = "None"
        # Extract parameters node from campaign config file
        self._extract_parameters(campaign_config_doc)
        # Extract targets node from campaign config file
        self._extract_targets(campaign_config_doc)
        # We shall update the parent campaign list to parse the TestCases node
        parent_campaign_list.append(campaign_file_path)
        # First time we parse the main campaign set the parent name to empty
        # string, and parent campaign list to empty list
        tc_list, sub_campaign_list = self._extract_test_cases(campaign_config_doc, parent_campaign_list, group_id)
        return sub_campaign_list, tc_list

    def _extract_parameters(self, campaign_config_doc):
        """
        This function completes the _global_config dictionary with parameters
        :param campaign_config_doc a DOM tree
        :type Document
        """

        # Get Test Campaign Configuration
        parameters = campaign_config_doc.xpath('//Parameters/*')
        for parameter in parameters:
            self._global_config.campaignConfig.update(parameter.attrib)

    def _extract_targets(self, campaign_config_doc):
        """
        This function completes the _global_config dictionary with targets
        :param campaign_config_doc a Etree tree
        :type Document
        """

        # Get Test Campaign Target Values (Throughput, B2B)
        targets = campaign_config_doc.xpath('//Targets/*')
        for target in targets:
            self._global_config.campaignConfig.update(target.attrib)

    def _extract_test_cases(self, campaign_config_doc, parent_campaign_list, group_id):
        """
        This function creates a set of test cases objects from parsing and returns
        the test cases list + the subcampaign list
        :type Document
        :param campaign_config_doc a Etree
        :param group_id a reference number for test group list inside test case list
        :type list
        :return test_cases a TestCaseConf list + subcampaigns a CampaignConf list
        """

        def create_test_case_element(node, last_parent, random=False, group_id=None):
            parse_status = True
            tcelement = TestCaseConf(node, random, group_id)
            error_msg = None
            try:
                tcelement = self._unify_path(tcelement, last_parent)
            except AcsConfigException as ex_msg:
                error_msg = "Error while reading-parsing TC item in " + \
                            str(last_parent) + " file => ignore TestCase item (exception = " + \
                            str(ex_msg) + ")"
                self._logger.warning(error_msg)
                self._logger.error("Test case not found, it will not be executed")
                parse_status = False

            try:
                tcelement = self._load_usecase_of_testcase(tcelement)
            except AcsConfigException as ex_msg:
                error_msg = "Error while reading-parsing TC item in " + \
                            str(last_parent) + " file => ignore TestCase item (exception = " + \
                            str(ex_msg) + ")"
                self._logger.warning(error_msg)
                self._logger.error("Test case based on unknown usecase (%s)," % (tcelement.get_name(),) +
                                   " it will not be executed")
                parse_status = False

            tcelement.add_message(error_msg)
            tcelement.set_valid(parse_status)
            return tcelement

        # Get the list of Test cases to execute
        test_case_list = []
        sub_campaign_list = []
        tcs_node = campaign_config_doc.xpath('//TestCases')
        if not tcs_node:
            # Inform the user that the campaign config template is bad
            error_msg = "Error while reading-parsing campaign item " + \
                        str(parent_campaign_list[-1]) + " file => no <TestCases> ...  </TestCases> node found "
            self._logger.warning(error_msg)

        tc_nodes = campaign_config_doc.xpath('//TestCases/*')
        if tc_nodes:
            for node in tc_nodes:
                last_parent = parent_campaign_list[-1] if parent_campaign_list else ""
                if node.tag == "TestCase":
                    tcelement = create_test_case_element(node, last_parent)
                    if tcelement is not None:
                        test_case_list.append(tcelement)
                elif node.tag == "RANDOM":
                    for subnode in node:
                        if True:  # subnode.nodeType == subnode.ELEMENT_NODE:
                            if subnode.tag == "TestCase":
                                tcelement = create_test_case_element(subnode, last_parent,
                                                                     random=True)
                                if tcelement is not None:
                                    test_case_list.append(tcelement)
                            elif subnode.tag == "GROUP":
                                group_id += 1
                                for group_node in subnode:
                                    if group_node.tag == "TestCase":
                                        tcelement = create_test_case_element(group_node, last_parent,
                                                                             random=True, group_id=group_id)
                                        if tcelement is not None:
                                            test_case_list.append(tcelement)
                elif node.tag == "SubCampaign":
                    # Parse sub campaign config and check arguments
                    # Check also that we do not fall into infinite loop by calling again a parent campaign name
                    try:
                        sub_campaign_config = CampaignConf(node, parent_campaign_list)
                        # unify path according to the closest parent campaign
                        sub_campaign_config = self._unify_path(sub_campaign_config, last_parent)
                        sub_campaign_config.check_campaign_sanity()
                    except AcsConfigException as ex_msg:
                        error_msg = "Error while reading-parsing campaign item in " + \
                                    str(last_parent) + " file => ignore SubCampaign item (exception = " + \
                                    str(ex_msg) + ")"
                        self._logger.warning(error_msg)
                        continue
                    # Compose relative file path for sub campaign config file
                    sub_campaign_file_path = sub_campaign_config.get_name()
                    campaign_path = os.path.join(Paths.EXECUTION_CONFIG,
                                                 sub_campaign_file_path + self._file_extension)

                    if not os.path.isfile(campaign_path):
                        error_msg = "Campaign file not found %s !" % (campaign_path,)
                        raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)
                    try:
                        sub_campaign_config_doc = et.parse(os.path.abspath(campaign_path))
                    except et.XMLSyntaxError:
                        _, error_msg, _ = Utils.get_exception_info()
                        raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)
                    # Parse of the Sub Campaign node is OK
                    # in parent campaign file + Parse of the file sub Campaign is OK
                    # add sub campaign item to sub campaign list
                    # (for debug purpose - configuration file copy in AWR)
                    sub_campaign_list.append(sub_campaign_config)

                    # After parsing sub Campaign node, we shall update the sub campaign parent campaign list
                    parent_sub_campaign_list = sub_campaign_config.get_parent_campaign_list()[:]
                    parent_sub_campaign_list.append(sub_campaign_file_path)

                    # we call a sub campaign, parse it by a recursive call to _extract_test_cases() method
                    try:
                        test_case_subset_list, sub_campaign_subset_list = self._extract_test_cases(
                            sub_campaign_config_doc, parent_sub_campaign_list, group_id)
                    except Exception:  # pylint: disable=W0703
                        _, error_msg, _ = Utils.get_exception_info()
                        self._logger.warning(error_msg)
                        continue

                    # Repeat test case subset list runNumber of time in the current test case list
                    if test_case_subset_list:
                        exec_number = int(sub_campaign_config.get_run_number())
                        test_case_list.extend(test_case_subset_list * exec_number)
                    # add sub campaign subset list to sub campaign list (for debug purpose -
                    # configuration file copy in AWR)
                    if sub_campaign_subset_list:
                        sub_campaign_list.extend(sub_campaign_subset_list)
                else:
                    # other case of parsing error continue the campaign execution
                    error_msg = "Error while reading-parsing campaign item in " + \
                                str(last_parent) + " file => node <" + node.tag + \
                                "> is not parsed according to campaign config template "
                    self._logger.warning(error_msg)
        else:
            # Inform the user that the campaign config template is bad
            error_msg = "Campaign item " + str(parent_campaign_list[-1]) + " is empty"
            self._logger.warning(error_msg)

        return test_case_list, sub_campaign_list

    def _unify_path(self, element, campaign_name):
        """
        This function unifies path according to a campaign path
        """

        # TC path could be relative to _ExecutionConfig or to the path of the campaign
        path_base_possibility = [""]
        if campaign_name:
            path_base_possibility.append(os.path.dirname(campaign_name))
        abs_exec_config = os.path.abspath(Paths.EXECUTION_CONFIG)

        found = False
        tested = []
        for base in path_base_possibility:
            base_abs_path = os.path.join(abs_exec_config, base)

            # Fix windows & linux path merging
            el_abs_path = os.path.normpath(os.path.join(base_abs_path, element.get_raw_name()))

            tested.append(el_abs_path + self._file_extension)
            if os.path.exists(el_abs_path + self._file_extension):
                found = True
                # Add relpath to _ExecutionConfig in order to reduce Uniquified TCs list
                el_name = self.__clean_tc_path(os.path.relpath(el_abs_path, abs_exec_config))
                element.set_name(el_name)

        if not found:
            # pylint: disable=W0141
            # Delete duplicated paths and join them in a message
            error_msg = ' or '.join(map(str, list(set(tested))))
            error_msg += " does not exist"
            element.set_name(element.get_raw_name())
            element.add_message(error_msg + "\n")
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)
        return element

    def __clean_tc_path(self, path):
        """
        As in campaign, TC relative path is written either for
        linux or windows system. The method will insure a proper path and
        avoid a mix of "\" and "/" in the same path.


        :param path: TC path to be cleaned
        :type path: str

        :return: cleaned TC path
        """

        if platform.system() != "Windows":
            tc_path = path.replace("\\", "/")
        else:
            tc_path = path.replace("/", "\\")
        return tc_path

    def _load_usecase_of_testcase(self, tcase_conf):
        """
        Get test case class name, based on test case configuration
        :rtype: string
        :return: the class name of the test case, or None
        """
        try:
            ucase_name = tcase_conf.get_ucase_name()
            ucase_class = tcase_conf.get_ucase_class()
            # if no use case class has been specified
            if ucase_class is None:
                # Extract usecase class name from the usecase catalog
                ucase_class = self._get_ucase_class_from_ucase(ucase_name)
                tcase_conf.set_ucase_class(ucase_class)
        except AcsConfigException:
            raise
        return tcase_conf

    def _get_ucase_class_from_ucase(self, ucase):
        """
        This function gets the use case class from the use case name.

        :type   ucase: string
        :param  ucase: use case name

        :rtype:     object
        :return:    use case class
        """

        if not self._ucase_catalogs:
            error_msg = "No use case catalog has been found!"
            raise AcsConfigException(AcsConfigException.FILE_NOT_FOUND, error_msg)

        ucase_dic = self._ucase_catalogs.get(ucase)

        if not ucase_dic:
            error_msg = "Use case {0} not found in UC catalog!".format(ucase)
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

        # Presence of ClassName element
        # is already checked by CatalogParser using xsd
        ucase_class_name = ucase_dic.get(CatalogParser.CLASSNAME_ELEM)
        ucase_class = Utils.get_class(ucase_class_name)
        return ucase_class
