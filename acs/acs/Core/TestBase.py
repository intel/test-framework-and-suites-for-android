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
:summary: This file implements the test base class
:author: vdechefd
"""

import os

from acs.Core.Report.ACSLogging import LOGGER_TEST_SCRIPT
from acs.Device.DeviceManager import DeviceManager
from acs.UtilitiesFWK.Utilities import Global, Error, AcsConstants
from acs.Core.PathManager import Paths


class TestBase(object):

    """
    This class is the common class for all use cases
    """

    def __init__(self, tcase_conf, global_config):
        # Initialize main attributes of the test case (name, parameters ...)
        self._name = tcase_conf.get_name()
        self._global_conf = global_config
        self._conf = tcase_conf
        self._tc_parameters = tcase_conf.get_params()
        self._logger = LOGGER_TEST_SCRIPT

        self._logger.info("")
        self._logger.info("%s: TestCase creation" % self._name)
        self._logger.info("")

        # Used for test case verdict purpose
        self._error = Error()

        # Get the path of execution config folder
        self._execution_config_path = os.path.abspath(Paths.EXECUTION_CONFIG)

        # Used by the test case manager to update the current status of the test case execution
        self.test_ok = False

        # This attribute is used to power cycle the device when error is detected after test case execution
        self._handle_power_cycle = True

    @property
    def tc_order(self):
        return self._conf.tc_order

    @tc_order.setter
    def tc_order(self, tc_order):
        self._conf.tc_order = tc_order

    @property
    def conf(self):
        """
        Public property
        """
        return self._conf

    @property
    def params(self):
        """
        Public property
        """
        return self._tc_parameters

    @property
    def usecase_name(self):
        """
        Aliasing java-style property
        """
        return self.params.get_ucase_name()

    @property
    def reporting_folder_path(self):
        """
        Return the folder path where the campaign report is generated
        """
        report_path = ""
        if self._global_conf:
            report_path = self._global_conf.campaignConfig.get("campaignReportTree").get_report_path()
        return report_path

    @property
    def is_provisioning(self):
        """
        This property tells whether a TC is of `provisioning` kind or not

        :return: Whether True or False
        """
        return self._tc_parameters.is_provisioning

    def initialize(self):
        self._logger.info("")
        self._logger.info("%s: Initialize" % self._name)
        self._logger.info("")
        return Global.SUCCESS, "No actions"

    def set_up(self):
        """
        Initialize the test
        """
        self._logger.info("")
        self._logger.info("%s: Setup" % self._name)
        self._logger.info("")
        return Global.SUCCESS, "No actions"

    def run_test(self):
        """
        Execute the test
        """
        self._logger.info("")
        self._logger.info("%s: RunTest" % self._name)
        self._logger.info("")
        return Global.SUCCESS, "No actions"

    def tear_down(self):
        """
        End and dispose the test
        """
        self._logger.info("")
        self._logger.info("%s: TearDown" % self._name)
        self._logger.info("")
        return Global.SUCCESS, "No actions"

    def finalize(self):
        """
        Clear all remaining objects created by the test
        """
        self._logger.debug("")
        self._logger.debug("%s: Finalize" % self._name)
        self._logger.debug("")

        # Finalize all instantiated UECommands for all instantiated devices
        for device in DeviceManager().get_all_devices():
            if device.uecommands:
                device.inject_device_log("i", "ACS_TESTCASE", "FINALIZE: %s" % self._name)
                for _, uecmd_object in device.uecommands.iteritems():
                    if uecmd_object:
                        uecmd_object.finalize()
                device.uecommands = {}
        return Global.SUCCESS, AcsConstants.NO_ERRORS

    def _get_file_path(self, file_path):
        """
        Returns a file path built from the provided path fragment C{file_path}.
        If the provide path fragment is an absolute path and the file exists
        on the filesystem, this path is returned.
        Otherwise, we try to find a corresponding file in I{ACS}
        I{execution directory} or in this use case's directory.

        :param file_path: the path fragment
        :type file_path: str

        :rtype: str
        :return: a new file path.
        """
        # Initialize the return value
        new_path = file_path
        # Save the path suffix for later use
        path_suffix = file_path
        # Remove leading "/" if any
        # (otherwise os.path.join does not act as expected)
        if path_suffix.startswith("/"):
            path_suffix = path_suffix[1:]
            # Check whether file path exists or not
        if not os.path.exists(new_path):
            # If that path does not exist we look
            # for a file in the execution directory
            new_path = os.path.join(
                self._execution_config_path,
                path_suffix)

        # If no such file exists in the execution directory
        # we look for a file in this use case directory
        if not os.path.exists(new_path):
            new_path = os.path.join(
                self._execution_config_path,
                os.path.dirname(self._name),
                path_suffix)

        # Return the operation status and the last
        # attempted file path.
        if not os.path.exists(new_path):
            return Global.FAILURE, new_path
        else:
            return Global.SUCCESS, new_path

    def get_logger(self):
        """
        Returns this objects logger instance.

        :rtype: Logging.Logging().logger
        :return: the logger
        """
        return self._logger

    def get_name(self):
        """
        Return the name of the test

        :rtype:     string
        :return:    Return the test name
        """
        return self._name

    def get_description(self):
        """
        Return the name of the test

        :rtype:     string
        :return:    Return test description
        """
        return self._tc_parameters.get_description()

    def get_b2b_iteration(self):
        """
        Return B2B iteration number

        :rtype:     integer
        :return:    Return B2B iteration number
        """
        return self._tc_parameters.get_b2b_iteration()

    def get_b2b_continuous_mode(self):
        """
        Return B2B continuous mode

        :rtype:     boolean
        :return:    Return B2B continuous mode (True/False)
        """
        return self._tc_parameters.get_b2b_continuous_mode()

    def get_parameters(self):
        """
        Return the name of the test

        :rtype:     string
        :return:    Return test description
        """
        return self._tc_parameters.get_tc_params_string()

    def get_tc_parameters(self):
        """
        Return the tc parameters

        :rtype:     dict
        :return:    Return a dictionary containing the TC parameters
        """
        return self._tc_parameters

    def get_usecase_name(self):
        """
        Return the name of the use case

        :rtype:     string
        :return:    Return use case name
        """
        return self._tc_parameters.get_ucase_name()

    def get_is_critical(self):
        """
        This function returns if the UC was tagged as critical.
        :rtype:     bool
        :return:    Return True on critical test
        """
        return self._tc_parameters.get_is_critical()

    def get_acceptance_criteria(self):
        """
        Get the acceptance criteria for this test case.

        :rtype: tuple (int, int)
        :return: tuple (max retry, acceptance)
        """
        return self._tc_parameters.get_acceptance_criteria()

    def get_tc_expected_result(self):
        """
        Get the expected verdict for this test case.

        :rtype: string
        :return: PASS, FAIL or BLOCKED
        """
        return self._tc_parameters.get_tc_expected_result()

    @property
    def handle_power_cycle(self):
        """
        This function returns if the power cycle need to be handle for this UC.
        :rtype:     bool
        :return:    Return True on critical test
        """
        return self._handle_power_cycle

    def get_is_warning(self):
        """
        This function returns if the TC was tagged as warning
        :rtype:     bool
        :return:    Return True on warning test
        """
        return self._tc_parameters.get_is_warning()
