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
:since: 21 nov 2012test_comment
:author: sfusilie
"""
from lxml import etree
import os

import acs.UtilitiesFWK.Utilities as Util
from XMLUtilities import clean_xml_text
from acs.Core.Hack import open_inheritance_hack

open_inheritance_hack()


class SecondaryTestReport(object):
    __metaclass__ = Util.Singleton

    TEST_REPORT_FILENAME = "extTestResult.xml"
    verdict = Util.Verdict

    def __init__(self, campaign_report_path):
        """
        :param campaign_report_path: Path of the campaign report
        :type campaign_report_path: str
        """
        self.__report_path = os.path.normpath(campaign_report_path)
        self.__filename = os.path.join(self.__report_path, self.TEST_REPORT_FILENAME)

        if os.path.isfile(self.__filename):
            self.__document = etree.parse(self.__filename).getroot()
        else:
            self.__document = etree.Element("Test_Report")

    def __clean_node(self, currentNode, indent="\t", newl="\n"):
        """
        Clean xml node
        """
        flt = indent + newl
        if len(currentNode):
            for node in currentNode:
                if node.text:
                    node.text = node.text.lstrip(flt).strip(flt)
                self.__clean_node(node, indent, newl)

    def __write_report(self):
        """
        Write report ti xml file
        """
        self.__clean_node(self.__document)
        content = etree.tostring(self.__document, pretty_print=True, xml_declaration=True)
        with open(self.__filename, 'w') as report_file:
            report_file.write(content)

    def __create_node_value(self, key, value):
        """
        Create xml node and value
        """
        key_node = etree.Element(str(key))
        key_node.text = value
        return key_node

    def __get_test_node(self, acs_tc_id, acs_tc_order):
        """
        Retrieve or create test node
        """
        test_result_node = None

        if acs_tc_id and acs_tc_order:
            xpath_query = "//Test_Result[@acs_tc_id=\"%s\" and @acs_tc_order=\"%s\"]" % (acs_tc_id, acs_tc_order)
            nodes = self.__document.xpath(xpath_query)
            if nodes:
                test_result_node = nodes[0]

        if test_result_node is None:
            test_result_node = etree.SubElement(self.__document, "Test_Result")

            if acs_tc_id:
                test_result_node.set("acs_tc_id", str(acs_tc_id))

            if acs_tc_order:
                test_result_node.set("acs_tc_order", str(acs_tc_order))

        test_node = etree.SubElement(test_result_node, "Test")
        return test_node

    def add_result(self, test_id, test_result, test_comment,
                   acs_tc_id=None, acs_tc_order=None):
        """
        Add result to the report
        """
        test_node = self.__get_test_node(acs_tc_id, acs_tc_order)
        test_node.append(self.__create_node_value("Test_Id", test_id))
        test_node.append(self.__create_node_value("Test_Result", test_result))

        node_test_comment = etree.SubElement(test_node, "Test_Comment")

        # Set test comment
        if isinstance(test_comment, basestring):
            node_test_comment.text = clean_xml_text(test_comment)
        elif isinstance(test_comment, list) and len(test_comment) == 1:
            node_test_comment.text = clean_xml_text(test_comment[0])
        else:
            for element in test_comment:
                sub_test_comment = etree.SubElement(node_test_comment, "SubComment")
                sub_test_comment.text = clean_xml_text(element)
        self.__write_report()

    def add_result_from_dict(self, dico, acs_tc_id=None, acs_tc_order=None):
        """
        Add a dictionary of result to the report
        dictionary should as follow:
            result = {key_tag: {
                                'status': Verdict.FAIL,
                                'comment': "your text"
                                }
        """
        for tcd_name, tcd_status in dico.items():
            # skip if vital key is not here
            if not set(["status", "comment"]).issubset(tcd_status):
                continue
            self.add_result(tcd_name, tcd_status.get("status", "N\A"),
                            tcd_status.get("comment", "N\A"), acs_tc_id, acs_tc_order)
