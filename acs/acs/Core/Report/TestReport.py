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
:summary: This file implements the test report of ACS
:since: 12/05/2010
:author: sfusilie
"""

from datetime import datetime
import getpass
from lxml import etree
import os
import os.path
import platform
import shutil
import socket
import tempfile

from acs.Core.CampaignMetrics import CampaignMetrics
from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.ErrorHandling.AcsToolException import AcsToolException
import acs.UtilitiesFWK.Utilities as Util
from XMLUtilities import clean_xml_text
from acs.Core.Hack import open_inheritance_hack
from acs.Core.PathManager import Files

open_inheritance_hack()


class Report:

    def __init__(self,
                 campaign_report_path,
                 device_name,
                 campaign_name,
                 campaign_relative_path,
                 campaign_type,
                 user_email,
                 metacampaign_uuid):

        self.statistics = None
        self.bench_info = None
        self.campaign_info = None
        self.device_info = None
        self.flash_info = None
        self._blocked_rate = None
        self._fail_rate = None
        self._pass_rate = None
        self._execution_rate = None
        self._critical_failure_cnt = None
        self._execution_time = None
        self._mtbf = None
        self._ttcf = None
        self._metacampaign_uuid = metacampaign_uuid

        self.document = etree.Element("TestReport")
        self.path = os.path.normpath(campaign_report_path)
        long_file = "{0}.xml".format(Files.acs_output_name)
        self.filename = os.path.join(self.path, long_file)

        # Create the XSL file path and generate it in the same folder as the XML file
        self._base = os.path.dirname(self.filename)
        self._xsl_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "html/report.xsl")

        # Create and Initialize <CampaignInfo> sub-node
        self._init_campaign_info_node(os.path.splitext(os.path.basename(campaign_name))[0],
                                      campaign_relative_path,
                                      campaign_type,
                                      user_email)

        # Create and Initialize <BenchInfo> sub-node
        self._init_bench_info_node()

        # Create and Initialize <DeviceInfo> sub-node
        self._init_device_info_node(device_name)

        # Create and Initialize <FlashInfo> sub-node
        self._init_flash_info_node(device_name)

        # Create and Initialize <Statistics> sub-node
        self._init_statistics_node()

        # Create the test report file
        self.update_report_file()

    @property
    def metacampaign_uuid(self):
        """
        Get the metacampaign uuid

        :rtype uuid: str
        :return: Uuid of the relevant campaign
        """
        return self._metacampaign_uuid

    @property
    def report_file_path(self):
        """
        Return the path to the xml report file
        """
        return self.filename

    def update_report_file(self):
        """
        Update the xml report file
        """
        try:

            temp_test_report_file = os.path.join(tempfile.gettempdir(), "Temporary_TestReport.xml")
            processing_instruction = etree.ProcessingInstruction(
                "xml-stylesheet", "type=\"text/xsl\" href=\"report.xsl\"")
            with open(temp_test_report_file, 'w') as f_test_report:
                f_test_report.write(etree.tostring(processing_instruction, pretty_print=True, xml_declaration=True))
                f_test_report.write(etree.tostring(self.document, pretty_print=True))

            # Copy the temporary file into the test report
            shutil.move(temp_test_report_file, self.filename)
            # copy the XSL file in the same folder ad the XML file
            shutil.copy(self._xsl_path, self._base)

        except Exception as report_exception:
            LOGGER_FWK.warning("Fail to update test report '%s' ! (%s)" % (str(self.filename), str(report_exception)))

    def build_deviceinfo_file(self, input_list):
        """
        Creates a file containing all devices info with format
        <property name= "<name>" value="<value>"/>

        :type input_list: dict
        :param input_list:List containing all getprop keys/values
        """
        # Check if input list is empty, if yes, write nothing.
        if not input_list or not isinstance(input_list, dict):
            return

        # Prepare XML file
        xml_doc = etree.Element("DeviceProperties")
        file_path = os.path.join(self.path, "device_info.xml")

        # Assign style sheet to test report
        processing_instruction = etree.ProcessingInstruction(
            "xml-stylesheet", "type=\"text/xsl\" href=\"../../Core/Report/html/deviceinfo.xsl\"")

        # Create the <DeviceProperties> base element
        for key, value in input_list.items():
            # Build <property name= "<name>" value="<value>"/>
            element = etree.SubElement(xml_doc, "property")
            element.set("name", clean_xml_text(key))
            element.set("value", clean_xml_text(value))

        # Write and close XML File (getprop.txt)
        with open(file_path, 'w') as f_test_report:
            f_test_report.write(etree.tostring(processing_instruction, pretty_print=True, xml_declaration=True))
            f_test_report.write(etree.tostring(xml_doc, pretty_print=True))

    def _init_campaign_info_node(self, campaign_name,
                                 campaign_relative_path, campaign_type,
                                 user_email):
        """
        Initialize the CampaignInfo Node with theses values:

        DeviceInfo:
            - Campaign Name
            - Campaign Relative path
            - Campaign Type (MTBF, SANITY .....)
            - User email
            - MetaCampaign UUID
            - MetaCampaign result UUID

        Optional:
            - Development Campaign

        :param campaign_name: Name of the campaign
        :param campaign_name: Relative path of the campaign
        :param campaign_type: Type of the campaign
        :param user_email: Email address of the user who launch the campaign
        """
        # Create the <BenchInfo> element
        self.campaign_info = etree.SubElement(self.document, "CampaignInfo")

        # Create the <CampaignName> element
        campaign_name_el = etree.SubElement(self.campaign_info, "CampaignName")
        campaign_name_el.set("relative_path", campaign_relative_path)
        # Set CampaignName
        campaign_name_el.text = clean_xml_text(campaign_name)

        # Create the <CampaignType> element
        campaign_type_el = etree.SubElement(self.campaign_info, "CampaignType")

        # Set CampaignType value
        if campaign_type in (None, ""):
            campaign_type = "Default"
        campaign_type_el.text = clean_xml_text(campaign_type)

        # Create the <UserEmail> element
        user_email_el = etree.SubElement(self.campaign_info, "UserEmail")

        # Set UserEmail
        if user_email in (None, ""):
            user_email = Util.AcsConstants.NOT_AVAILABLE
        user_email_el.text = clean_xml_text(user_email)

        # Create the <MetaCampaignUUID> element
        metacampaign_uuid_el = etree.SubElement(self.campaign_info, "MetaCampaignUUID")
        # Set MetaCampaignUUID value
        metacampaign_uuid_el.text = self._metacampaign_uuid

        # Create the <MetaCampaignResultID> element
        metacampaign_result_id_el = etree.SubElement(self.campaign_info, "MetaCampaignResultId")
        # Set MetaCampaignResultId value
        metacampaign_result_id_el.text = Util.AcsConstants.NOT_AVAILABLE

    def _init_bench_info_node(self):
        """
        Initialize the DeviceInfo Node with theses values:

        DeviceInfo:
            - Bench Name (hostname)
            - Bench user
            - Bench IP
            - Bench OS
            - ACS Version (host)

        :rtype: None
        """

        # Create the <BenchInfo> element
        self.bench_info = etree.SubElement(self.document, "BenchInfo")

        # Create the <BenchName> node for hostInfo
        bench_name = etree.SubElement(self.bench_info, "BenchName")
        # Set BenchName value
        bench_name.text = clean_xml_text(self.__get_bench_name())

        # Create the <BenchUser> node for hostInfo
        bench_user = etree.SubElement(self.bench_info, "BenchUser")
        # Set BenchUser value
        bench_user.text = clean_xml_text(self.__get_bench_user())

        # Create the <BenchIp> node for hostInfo
        bench_ip = etree.SubElement(self.bench_info, "BenchIp")
        # Set BenchIp value
        bench_ip.text = self.__get_bench_ip()

        # Create the <BenchOs> node for hostInfo
        bench_os = etree.SubElement(self.bench_info, "BenchOs")
        # Set BenchName value
        bench_os.text = self.__get_bench_os()

        # Create the <AcsVersion> node for hostInfo
        acs_version = etree.SubElement(self.bench_info, "AcsVersion")
        # Set AcsVersion value
        acs_version.text = Util.get_acs_release_version()

    def _init_device_info_node(self, device_name):
        """
        Initialize the DeviceInfo Node with theses values:

        DeviceInfo:
            - Device Model
            - Build Number (SwRelease)
            - DeviceId
            - IMEI
            - Model Number
            - FwVersion (Firmware Version)
            - Baseband version
            - Kernel Version
            - ACS Agent Version
            - Board type

        :type device_name: str
        :param device_name: Name of the device

        :rtype: None
        """
        # Create the <DeviceInfo> element
        self.device_info = etree.SubElement(self.document, "DeviceInfo")

        # Create the <DeviceModel> node for DeviceInfo
        device_model = etree.SubElement(self.device_info, "DeviceModel")
        # Set DeviceModel value
        device_model.text = device_name

        # Create the <SwRelease> node for DeviceInfo
        sw_release = etree.SubElement(self.device_info, "SwRelease")
        # Set default SwRelease value
        sw_release.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <DeviceId> node for DeviceInfo
        device_id = etree.SubElement(self.device_info, "DeviceId")
        # Set DeviceId value
        device_id.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <Imei> node for DeviceInfo
        imei = etree.SubElement(self.device_info, "Imei")
        # Set Imei default value
        imei.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <ModelNumber> node for DeviceInfo
        model_number = etree.SubElement(self.device_info, "ModelNumber")
        # Set ModelNumber default value
        model_number.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <FwVersion> node for DeviceInfo
        firmware_version = etree.SubElement(self.device_info, "FwVersion")
        # Set FwVersion default value
        firmware_version.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <BasebandVersion> node for DeviceInfo
        baseband_version = etree.SubElement(self.device_info, "BasebandVersion")
        # Set BasebandVersion default value
        baseband_version.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <KernelVersion> node for DeviceInfo
        kernel_version = etree.SubElement(self.device_info, "KernelVersion")
        # Set KernelVersion default value
        kernel_version.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <AcsAgentVersion> node for DeviceInfo
        acs_agent_version = etree.SubElement(self.device_info, "AcsAgentVersion")
        # Set KernelVersion default value
        acs_agent_version.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <BoardType> node for DeviceInfo
        board_type = etree.SubElement(self.device_info, "BoardType")
        # Set device type default value
        board_type.text = Util.AcsConstants.NOT_AVAILABLE

    def _init_flash_info_node(self, device_name):
        """
        Initialize the FlashInfo Node with theses values:
        Set of values to be updated
        FlashInfo:
            - Build Number/ SwRelease
            - Model Number
            - FwVersion (Firmware Version)
            - Baseband version


        :type device_name: str
        :param device_name: Name of the device

        :rtype: None
        """
        # Create the <FlashInfo> element
        self.flash_info = etree.SubElement(self.document, "FlashInfo")

        # Create the <SwRelease> node for FlashInfo
        sw_release = etree.SubElement(self.flash_info, "SwRelease")
        # Set default SwRelease value
        sw_release.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <BranchBuildTypeNumber> node for FlashInfo
        branch_buildtype_number = etree.SubElement(self.flash_info, "BranchBuildTypeNumber")
        # Set BranchBuildTypeNumber default value
        branch_buildtype_number.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <FwVersion> node for FlashInfo
        firmware_version = etree.SubElement(self.flash_info, "FwVersion")
        # Set FwVersion default value
        firmware_version.text = Util.AcsConstants.NOT_AVAILABLE

        # Create the <BasebandVersion> node for FlashInfo
        baseband_version = etree.SubElement(self.flash_info, "BasebandVersion")
        # Set BasebandVersion default value
        baseband_version.text = Util.AcsConstants.NOT_AVAILABLE

    def _init_statistics_node(self):
        """
        Initialize the Statistics Node:
        :rtype: None
        """
        # Create the main <Statistics> element
        self.statistics = CampaignMetrics.instance().get_metrics("xml", log_metrics=True)
        self.document.append(self.statistics)

    def _create_verdict_nodes(self, tcase_node, verdict):
        """
        Create nodes related to the test case verdict

        :type tcase_node: xml node object
        :param tcase_node: instance corresponding to the node TestCase in the xml report

        :type verdict: tuple
        :param verdict: Test case verdict containing (expected verdict, obtained verdict, reported verdict)
        """
        if isinstance(verdict, tuple):
            (expected_verdict, obtained_verdict, reported_verdict) = verdict
        else:
            # By default the test case is not executed ("NOT EXECUTED", "NOT EXECUTED", "NOT EXECUTED")
            (expected_verdict, obtained_verdict, reported_verdict) = ("NOT EXECUTED", "NOT EXECUTED", "NOT EXECUTED")

        # Create a <ExpectedVerdict> element
        expected_verdict_el = etree.SubElement(tcase_node, "ExpectedVerdict")
        # Add the value of ExpectedVerdict
        expected_verdict_el.text = expected_verdict

        # Create a <ObtainedVerdict> element
        obtained_verdict_el = etree.SubElement(tcase_node, "ObtainedVerdict")
        # Add the value of ObtainedVerdict
        obtained_verdict_el.text = obtained_verdict

        # Create a <Verdict> element
        test_verdict_el = etree.SubElement(tcase_node, "Verdict")
        # Add the value of reported Verdict
        test_verdict_el.text = reported_verdict

    def _create_testcase_node(self,
                              test_case_name,
                              test_case_relative_path="",
                              test_case_order=-1,
                              test_case_description="unknown",
                              use_case_name='unknown',
                              parameters="unknown",
                              verdict=None,
                              comment="not executed",
                              start_time=None,
                              end_time=None,
                              exec_nb=1,
                              retry_nb=1,
                              acceptance_nb=1,
                              exec_results=[]):
        """
        Create a node containing test results.

        :type test_case_name: str
        :param test_case_name: Name of the executed test case

        :type test_case_relative_path: str
        :param test_case_relative_path: Relative path of the executed test case

        :type test_case_order: int
        :param test_case_order: Test case order

        :type test_case_description: str
        :param test_case_description: Description of the usecase's purpose

        :type use_case_name: str
        :param use_case_name: Name of the use case which the test case refers to

        :type parameters: str
        :param parameters: String describing a set of usecase's parameters

        :type verdict: tuple
        :param verdict: Test case verdict containing (expected verdict, obtained verdict, reported verdict)

        :type comment: str
        :param comment: Verdict's comment

        :type start_time: datetime
        :param start_time: Time of testcase begin

        :type end_time: datetime
        :param end_time: Time of testcase ends

        :type exec_nb: int
        :param exec_nb: Execution time/occurence

        :type retry_nb: int
        :param retry_nb: Max retry nb

        :type acceptance_nb: int
        :param acceptance_nb: Acceptance number

        :type exec_results: list
        :param exec_results: Results for each execution, as strings

        :rtype: Element
        :return: Node containing all test result's values
        """
        # Set default value for start_time and end_time
        # if necessary
        if start_time is None or end_time is None:
            start_time = datetime.now()
            end_time = start_time

        # compute execution time
        delta_time = end_time - start_time
        # Round seconds to upper integer to avoid 0s execution time when
        # execution is 0s < t < 1s
        if delta_time.microseconds > 0:
            round_up = 1
        else:
            round_up = 0
        delta_time_seconds = (delta_time.days * 3600 * 24) + delta_time.seconds + round_up
        days, remainder = divmod(delta_time_seconds, 3600 * 24)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        delta_time_str = '%0.2d:%0.2d:%0.2d' \
            % (hours + days * 24, minutes, seconds)

        # Create the main <TestCase> element
        test_case = etree.Element("TestCase")
        test_case.set("id", test_case_name)
        test_case.set("order", str(test_case_order))
        test_case.set("relative_path", test_case_relative_path)

        # Create a <UseCase> element
        use_case = etree.SubElement(test_case, "UseCase")
        # Set UseCase value
        use_case.text = use_case_name

        # create a <ExecutionTime> element
        test_execution_time = etree.SubElement(test_case, "ExecutionTime")
        test_execution_time.text = delta_time_str

        # create a <StartExecutionDate> element
        test_execution_date = etree.SubElement(test_case, "StartExecutionDate")
        test_execution_date.text = datetime.strftime(start_time, "%d/%m/%Y")

        # create a <StartExecutionTime> element
        test_start_exec_time = etree.SubElement(test_case, "StartExecutionTime")
        test_start_exec_time.text = datetime.strftime(start_time, "%H:%M:%S")

        # Create a <Description> element
        test_description = etree.SubElement(test_case, "Description")
        # Set Test Description
        test_description.text = test_case_description

        # Create a <Parameters> element
        test_parameters = etree.SubElement(test_case, "Parameters")
        # Set Test parameters
        test_parameters.text = parameters

        # Create verdict nodes
        self._create_verdict_nodes(test_case, verdict)

        # Create a Exec element
        exec_nb_node_deprecated = etree.SubElement(test_case, "Exec")
        exec_nb_node_deprecated.text = str(exec_nb)
        exec_nb_node = etree.SubElement(test_case, "Tries")
        exec_nb_node.attrib['nb'] = str(len(exec_results))
        for i, res in enumerate(exec_results):
            try_node = etree.SubElement(exec_nb_node, "Try")
            try_node.attrib['id'] = str(i + 1)
            try_node.attrib['result'] = str(res)

        # Create a Max Attempt element
        max_attempt_node = etree.SubElement(test_case, "MaxAttempt")
        max_attempt_node.text = str(retry_nb)

        # Create a acceptance element
        acceptance_node = etree.SubElement(test_case, "Acceptance")
        acceptance_node.text = str(acceptance_nb)

        # Create a <Comment> element
        test_comment = etree.SubElement(test_case, "Comment")

        # Set test comment
        if isinstance(comment, basestring):
            test_comment.text = clean_xml_text(comment)
        elif isinstance(comment, list) and len(comment) == 1:
            test_comment.text = clean_xml_text(comment[0])
        else:
            for element in comment:
                if element is not None:
                    sub_test_comment = etree.SubElement(test_comment, "SubComment")
                    sub_test_comment.text = clean_xml_text(element)
        return test_case

    def initialize_results(self, testcases_list):
        """
        Initialize the test report file, instantiating test results
        with default values

        :type testcases_list: list
        :param testcases_list: Initial list of testcases to run (include duplicate)
        """

        tc_order = 1
        for tc in testcases_list:
            tc_name = os.path.basename(tc.get_name())
            tc_rel_path = os.path.dirname(tc.get_name())
            tc_node = self._create_testcase_node(tc_name, tc_rel_path, tc_order, tc.get_params().get_description())
            self.document.append(tc_node)
            tc_order += 1

        # Update test report file
        self.update_report_file()

    def add_comment(self, tc_order, comment):
        """
        Add a comment to a testcase into test report file.
        If no testcase exists for given order, nothing will be done.

        :type tc_order: int
        :param tc_order: order of the testcase in which comment will be added

        :type comment: str
        :param comment: the comment to add to given testcase
        """

        tc_order = str(tc_order)
        # get all TestCase nodes and loop on them
        node_list = self.document.xpath("//TestCase[@order='%s']" % tc_order)
        if node_list:
            node = node_list[0]
            # wanted node is found
            # get node comment, or create one if no comment node exists
            node_comment = node.find("Comment")
            if node_comment is None:
                # Comment node doesnt exist, so we only update the text of this node
                node_comment = etree.SubElement(node, "Comment")
            elif node_comment.find("SubComment") is None:
                # previous text exist but there is not subcomment node
                old_text_content = node_comment.text
                # add 2 sub comment
                # one dedicated to new comment
                etree.SubElement(node_comment, "SubComment").text = comment
                # one dedicated to previous comment
                etree.SubElement(node_comment, "SubComment").text = old_text_content
                node_comment.text = ""
            else:
                # previous subcomments exist, add a new one with new comment
                etree.SubElement(node_comment, "SubComment").text = clean_xml_text(comment)

        # Update test report file
        self.update_report_file()

    def add_result(self, tc_conf, tc_order, start_time, end_time, verdict, execution_nb, execution_results):
        """
        Add testcase results into test report file.

        :type tc_conf: TestCaseConf
        :param tc_conf: test case configuration

        :type tc_order: int
        :param tc_order: test case order

        :type start_time: datetime
        :param start_time: Time of testcase begin

        :type end_time: datetime
        :param end_time: Time of testcase ends

        :type verdict: tuple
        :param verdict: tuple containing expected verdict, obtained verdict, and computed verdict

        :type execution_nb: int
        :param execution_nb: number of execution of test_case

        :type execution_results: list
        :param execution_results: Results for each execution, as strings
        """

        tc_name = os.path.basename(tc_conf.get_name())
        tc_rel_path = os.path.dirname(tc_conf.get_name())
        tc_order = str(tc_order)
        tc_params = tc_conf.get_params()
        (max_attemt, acceptance_criteria) = tc_params.get_acceptance_criteria()

        old_node = None

        node_list = self.document.xpath("//TestCase[@id='%s' and @order='%s']" % (tc_name, tc_order))
        if node_list:
            old_node = node_list[0]

        # Create the main <TestCase> element
        node = self._create_testcase_node(
            tc_name,
            tc_rel_path,
            tc_order,
            tc_params.get_description(),
            tc_params.get_ucase_name(),
            tc_params.get_tc_params_string(),
            verdict,
            tc_conf.get_messages(),
            start_time, end_time,
            execution_nb,
            max_attemt,
            acceptance_criteria,
            execution_results)

        if old_node is not None:
            self.document.replace(old_node, node)
        else:
            self.document.append(node)

        # Update test report file
        self.update_report_file()

    def update_flash_info_node(self, flash_properties):
        """
        Update the FlashInfo node in the campaign result file.

        :param properties: set of properties and their associated values
        :type properties: dict

        This dictionary contains following information :
            - SwRelease
            - FwVersion
            - BasebandVersion


        :rtype: None
        :return: None
        """

        if isinstance(flash_properties, dict):
            for property_name, property_value in flash_properties.items():
                if property_value in [None, ""]:
                    property_value = Util.AcsConstants.NOT_AVAILABLE
                property_node = self.flash_info.find(property_name)
                if property_node is not None:
                    property_node.text = clean_xml_text(str(property_value))
            # Update test report file
            self.update_report_file()

    def update_device_info_node(self, device_properties):
        """
        Update the DeviceInfo node in the campaign result file.

        :param device_properties: set of properties and their associated values
        :type device_properties: dict

        This dictionary contains following information :
            - SwRelease
            - DeviceId
            - Imei
            - ModelNumber
            - FwVersion
            - BasebandVersion
            - KernelVersion
            - AcsAgentVersion

        """

        if isinstance(device_properties, dict):
            for property_name, property_value in device_properties.items():
                if property_value in [None, ""]:
                    property_value = Util.AcsConstants.NOT_AVAILABLE
                property_node = self.device_info.find(property_name)
                if property_node is not None:
                    property_node.text = clean_xml_text(str(property_value))
            # Update test report file
            self.update_report_file()

    def update_statistics_node(self):
        # replace statistic node with new one
        new_statistics = CampaignMetrics.instance().get_metrics("xml", log_metrics=True)

        if self.statistics is not None:
            self.document.replace(self.statistics, new_statistics)
        else:
            self.document.append(new_statistics)

        self.statistics = new_statistics

        # Update test report file
        self.update_report_file()

    def write_metacampaign_result_id(self, metacampaign_result_id):
        """
        Write the Meta Campaign UUID of the current campaign execution to the report file.

        :type metacampaign_result_id: string
        :param metacampaign_result_id: Meta Campaign UUID previously retrieved on the server.

        .. attention:: if device is None or empty string, "Not available"
        will be written instead.

        :rtype: None
        :return: None
        """
        metacampaign_result_id_to_write = Util.AcsConstants.NOT_AVAILABLE
        if metacampaign_result_id not in [None, "", "None"] and isinstance(metacampaign_result_id, str):
            metacampaign_result_id_to_write = metacampaign_result_id
        metacampaign_result_id_node = self.campaign_info.find('MetaCampaignResultId')
        if metacampaign_result_id_node is not None:
            metacampaign_result_id_node.text = str(metacampaign_result_id_to_write)
        else:
            raise AcsToolException(AcsToolException.XML_PARSING_ERROR, "Node MetaCampaignResultId does not exist!")
        # Update the report file
        self.update_report_file()

    def __get_bench_name(self):
        """
        Retrieve the Bench Name of which execute the current Campaign

        :rtype: str
        :return: The Bench Name (hostname)
        """
        try:
            hostname = socket.gethostname()
            if hostname not in (None, ""):
                return hostname
            else:
                return Util.AcsConstants.NOT_AVAILABLE
        except:  # pylint: disable=W0702
            return Util.AcsConstants.NOT_AVAILABLE

    def __get_bench_ip(self):
        """
        Retrieve the Bench Ip of which execute the current Campaign

        :rtype: str
        :return: The Bench Ip
        """
        try:
            host_ip = socket.gethostbyname(socket.gethostname())
            if host_ip not in (None, ""):
                return host_ip
            else:
                return Util.AcsConstants.NOT_AVAILABLE
        except:  # pylint: disable=W0702
            return Util.AcsConstants.NOT_AVAILABLE

    def __get_bench_user(self):
        """
        Retrieve the current user of which execute the current Campaign

        :rtype: str
        :return: The Bench User (hostname)
        """
        try:
            user = getpass.getuser()
            if user not in (None, ""):
                return user
            else:
                return Util.AcsConstants.NOT_AVAILABLE
        except:  # pylint: disable=W0702
            return Util.AcsConstants.NOT_AVAILABLE

    def __get_bench_os(self):
        """
        Retrieve the current OS of which execute the current Campaign

        :rtype: str
        :return: The Bench OS (hostname)
        """
        try:
            bits = platform.architecture()[0]
            os_sys = platform.system()

            # Check release
            if os.name == "nt":
                release = platform.release()
                # Windows Seven Limitation
                if release == "post2008Server":
                    release = "Seven"
            else:
                (distname, version) = platform.dist()[:2]
                release = distname + " " + version

            full_os_name = os_sys + " " + release + " (" + bits + ")"

            if full_os_name not in (None, ""):
                return full_os_name
            else:
                return Util.AcsConstants.NOT_AVAILABLE
        except:  # pylint: disable=W0702
            return Util.AcsConstants.NOT_AVAILABLE
