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
:since: 05/08/2011
:author: sfusilie
"""
import os
from XMLUtilities import clean_xml_text
from acs.Core.Hack import open_inheritance_hack
from acs.Core.PathManager import Files
open_inheritance_hack()


class DebugReport(object):

    TAB = ' ' * 4
    LINESEP = '\n'

    def __init__(self, path):
        self.path = path
        long_file = "{0}_debug.xml".format(Files.acs_output_name)
        self._filename = os.path.join(self.path, long_file)

    def __create_file(self):
        # The with statement is exception-safe: the file is closed even if write fails.
        with open(self._filename, 'w+') as outfile:
            outfile.write("<?xml version=\"1.0\" ?>" + DebugReport.LINESEP)
            outfile.write("<DebugReport>" + DebugReport.LINESEP)
            outfile.write("</DebugReport>")

    def add_debug_log(self, tc_name, tc_order, retry, iteration, verdict, device_crash_events, **options):
        """
        Add debug logs in the DebugTestReport file

        :type tc_name : string
        :param tc_name : Name of the test case

        :type tc_order : int
        :param tc_order : Test case order

        :type retry : int
        :param retry: Number of retry

        :type iteration : int
        :param iteration: Iteration number

        :type verdict : string
        :param iteration: Verdict of the test case

        :type device_crash_events : string
        :param iteration: Extract of Device logs of the current test case
        """
        if not os.path.isfile(self._filename):
            # Report does not exist, create it.
            self.__create_file()

        device_error_open_tag = "{0}<DeviceErrorLog>{1}".format(DebugReport.TAB * 2, DebugReport.LINESEP)
        device_error_close_tag = "{0}</DeviceErrorLog>{1}".format(DebugReport.TAB * 2, DebugReport.LINESEP)
        # The with statement is exception-safe: the file is closed even if write fails.
        with open(self._filename, 'r+') as outfile:
            outfile.seek(-15, os.SEEK_END)  # Just before "</DebugReport>"

            tc_rel_path = os.path.dirname(tc_name)
            tc_name = os.path.basename(tc_name)

            # START DEBUG ID
            debug_tag = '{3}{4}<Debug id="{0}" order="{1}" relative_path="{2}">{3}'.format(tc_name,
                                                                                           tc_order,
                                                                                           tc_rel_path,
                                                                                           DebugReport.LINESEP,
                                                                                           DebugReport.TAB)
            outfile.write(debug_tag)

            # RETRY
            outfile.write("{0}<Try>".format(DebugReport.TAB * 2))
            outfile.write("{0}".format(retry))
            outfile.write("</Try>{0}".format(DebugReport.LINESEP))

            # ITERATION
            outfile.write("{0}<Iteration>".format(DebugReport.TAB * 2))
            outfile.write("{0}".format(iteration))
            outfile.write("</Iteration>{0}".format(DebugReport.LINESEP))

            # VERDICT
            outfile.write("{0}<Verdict>".format(DebugReport.TAB * 2))
            outfile.write("{0}".format(verdict))
            outfile.write("</Verdict>{0}".format(DebugReport.LINESEP))

            # DEVICE LOG
            outfile.write(device_error_open_tag)
            outfile.write(self.format_device_crashlog(device_crash_events))
            outfile.write(device_error_close_tag)

            if options and options.get('metrics_logs'):
                # DEVICE LOG (UNEXPECTED REBOOT)
                outfile.write(device_error_open_tag)
                [outfile.write("{0}{1}".format(DebugReport.TAB * 3, line))
                 for line in options.get('metrics_logs') if line]
                outfile.write(device_error_close_tag)

            # END DEBUG ID
            outfile.write("{0}</Debug>{1}".format(DebugReport.TAB, DebugReport.LINESEP))
            # END DOC
            outfile.write("</DebugReport>")

    def format_device_crashlog(self, device_crash_events):
        """
        Filter all device crash logs from ACS logs

        :type device_crash_events : list
        :param device_crash_events: List of device crash logs

        :rtype: string
        :return: formatted logs
        """
        output_log = ""
        for error in device_crash_events:
            output_log += "{0}{1}{2}".format(DebugReport.TAB * 3, error, DebugReport.LINESEP)
        output_log = self.__replace_special_characters(output_log)
        return output_log

    def __replace_special_characters(self, logs):
        """
        Replace all special characters to be readable in xml format
        In xml text content we have to perform following replacement:
            & by &amp;
            ' by &apos;
            " by &quot;
            < by &lt;
            > by &gt;

        :type logs : string
        :param iteration: Logs to parse

        :rtype: string
        :return: logs reworked to be readable in xml format
        """
        reworked_logs = str(logs)
        reworked_logs = reworked_logs.replace("&", "&amp;").replace("\"", "&quot;").replace("'", "&apos;")
        reworked_logs = reworked_logs.replace("<", "&lt;").replace(">", "&gt;")
        return clean_xml_text(reworked_logs)
