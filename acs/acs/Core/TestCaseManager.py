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
:summary: This file implements the test case manager
:author: cbresoli
"""

from datetime import datetime
import fnmatch
import os
import inspect

from acs.Core.CampaignMetrics import CampaignMetrics
from acs.Core.PathManager import Folders
from acs.Core.Report.ACSLogging import ACSLogging, LOGGER_FWK, LOGGER_FWK_STATS
from acs.Device.DeviceManager import DeviceManager
from acs.Core.Equipment.EquipmentManager import EquipmentManager
from acs.ErrorHandling.AcsBaseException import AcsBaseException
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.AcsToolException import AcsToolException
from acs.ErrorHandling.DeviceException import DeviceException
from acs.UtilitiesFWK.Utilities import Global, AcsConstants, DeviceState, format_exception_info, Verdict
import acs.UtilitiesFWK.Utilities as Util


INIT_STEP = "initialize"
SETUP_STEP = "set_up"
RUN_STEP = "run_test"
TEARDOWN_STEP = "tear_down"
FINALIZE_STEP = "finalize"


class TestCaseManager(object):

    """
    Class implementing the TC manager
    """

    def __init__(self, test_report, live_reporting_interface=None):
        self._dut_model_name = "Empty"
        self._tc_verdict = "Empty"
        self._dut_instance = None
        self._verdict = Util.Verdict()
        self._error = Util.Error()
        self._exception = AcsBaseException(AcsBaseException.DEFAULT_ERROR_CODE)
        self._logger = LOGGER_FWK
        self._target_b2b_rate = 0
        self._global_config = None
        self._is_setup_requested = "Empty"
        self._skip_boot_on_power_cycle = "Empty"
        self._boot_retry_number = 1
        self._power_cycle_between_tc = "Empty"
        self._power_cycle_on_failure = "Empty"
        self._final_dut_state = None
        self._has_critical_failure_occurred = False
        # Flag set to True when a CTRL+C (Keyboard Interruption is detected)
        self._user_interruption_request = False
        self.__debug_report = None
        self.max_attempt = 1
        self.acceptance_nb = 0
        self.execution_nb = 0
        self._execution_results = []
        self.tc_iteration_count = 1
        self.tc_device_crash_count = 0
        self.__test_report = test_report
        self._live_reporting_interface = live_reporting_interface
        self.__campaign_metrics = CampaignMetrics.instance()
        self._test_case = None
        self._tc_debug_directory = None
        self._device_info_to_report = {}
        self._device_info_status = Verdict.FAIL

    @property
    def test_failed_on_critical(self):
        """
        :return: True if test case failed on a critical failure, False otherwise
        """
        return self._has_critical_failure_occurred

    def power_cycle_device(self):
        """
        This function perform power cycle of the device if required
        This function is called after execution of test and after test report is updated

        :rtype: boolean, string
        :return: status, error message
        """
        status = False
        status_msg = ""

        # By default no power cycle will be done
        is_power_cycle_required = False

        # If critical failure occurs we force the power cycle in all cases !
        if self._has_critical_failure_occurred:
            is_power_cycle_required = True
            self._logger.info("Critical failure occurred => Power cycle the device !")
        # If 'powerCycleBetweenTC' parameter is set to True => power cycle the device !
        elif self._power_cycle_between_tc:
            is_power_cycle_required = True
            self._logger.info(
                "'powerCycleBetweenTC' is set to True => Power cycle the device between each test case !")
        # If 'powerCycleOnFailure' parameter is set to True => power cycle the
        # device only when the verdict is FAIL or BLOCKED!
        elif self._power_cycle_on_failure and self._tc_verdict in [self._verdict.FAIL, self._verdict.BLOCKED]:
            is_power_cycle_required = True
            self._logger.info(
                "'powerCycleOnFailure' is set to True and test case failure occurred => Power cycle the device !")

        if is_power_cycle_required:
            if not Util.get_config_value(self._global_config.campaignConfig,
                                         "Campaign Config", "isIoCardUsed", False,
                                         default_cast_type="str_to_bool"):
                status = self._dut_instance.reboot()
            else:
                # DO connection with the device / board
                # It is not the first boot!
                (status, status_msg) = self.connect_device(False)
            if self._has_critical_failure_occurred:
                # Start chrono here for MTBF calculation
                # This is done here to exclude time to boot from calculation
                # Only do it a new critical failure occurred
                self.__campaign_metrics.set_mtbf_ref_time()
                # The board has been reboot, clear the flag
                self._has_critical_failure_occurred = False
        else:
            status = True

        return status, status_msg

    def handle_critical_failure(self):
        """
        Handle critical failure to power cycle the device
        and retrieve device logs
        """
        # This option will force to retrieve all embedded logs, to be sure to have crash logs, ap logs ...
        # on critical failures
        if self._dut_instance.get_config("retrieveDeviceLogOnCriticalFailure", "False", "str_to_bool"):
            # Power cycle the device
            (status_power_cycle, status_power_cycle_msg) = self.power_cycle_device()
            if status_power_cycle:
                # We did a reboot on critical failure
                # Try to retrieve all debug logs
                self._dut_instance.retrieve_debug_data(tc_debug_data_dir=self._tc_debug_directory)
            else:
                self._logger.debug(status_power_cycle_msg)

    def _get_b2b_verdict(self, b2b_iteration, b2b_verdict_count):
        """
        This function computes the verdict of a B2B TC comparing the
        current PASS rate & the targeted PASS rate

        :param b2b_iteration: Number of iteration attempted
        :param b2b_verdict_count: number of iteration having a for each verdict
        """
        msg = []
        pass_rate = 0.0

        for verdict, verdict_count in b2b_verdict_count.iteritems():
            rate = (float(verdict_count) / float(b2b_iteration)) * 100
            if verdict == Verdict.PASS:
                pass_rate = rate
                msg.append("PASS Rate %.0f%% (%d out of %d) - Target PASS Rate %d%%" % (
                    pass_rate, verdict_count, b2b_iteration, self._target_b2b_rate))
            else:
                # Add messages only if the rate is greater than 0
                # This to avoid having a long message in the test case comment
                if rate > 0.0:
                    msg_verdict = "%s Rate %.0f%% (%d out of %d)" % (verdict, rate, verdict_count, b2b_iteration)
                    msg.append(msg_verdict)

        msg = " - ".join(msg)

        if isinstance(self._error.Msg, list):
            self._error.Msg.append(msg)
        else:
            self._error.Msg += " " + msg

        return self._verdict.PASS if pass_rate >= self._target_b2b_rate else self._verdict.FAIL

    def _is_critical_failure(self, error_msg):
        """
        This function checks if a critical failure occurred during execution

        :param error_msg: error message returned by the test
        """
        if (not self._dut_instance.is_available() and not self._skip_boot_on_power_cycle and
                self._test_case.conf.do_device_connection):
            # Unavailable device is a critical failure
            is_critical_failure = True
            error_msg = "Device not available !"

        # Check if there is a critical failure in the error message
        elif self._exception.is_critical_exception(error_msg):
            is_critical_failure = True
            error_msg = "Found critical failure in following message: %s" % (error_msg,)

        else:
            # Reset last critical failure message
            is_critical_failure = False

        # In case of critical failure, update date of critical failure and messages
        if is_critical_failure:
            self.__campaign_metrics.add_critical_failure()
            # Update final message and datetime
            critical_failure_message = AcsBaseException.CRITICAL_FAILURE + " (%s)" % (error_msg,)
            self._logger.critical("%s: %s" % (self._test_case.get_name(), critical_failure_message))

        return is_critical_failure

    def _execute_b2b(self, running_tc, b2b_iteration):
        """ execute_b2b

        This function executes UC in a B2B mode (non continuous mode)

        :param running_tc: Object implementing the TC
        :param b2b_iteration: Number of iterations to be executed in case of B2B TC
        """
        # TC Execution Counter
        self.tc_iteration_count = 1
        tc_iteration_count = 0
        b2b_verdict_count = {x: 0 for x in Util.Verdict2Global.map}

        # Run TC Init
        (self._error.Code, self._error.Msg), self._user_interruption_request = \
            self.__tc_catch_exceptions(running_tc, INIT_STEP)
        if self._error.Code != Global.SUCCESS:
            verdict = self._verdict.BLOCKED
        else:
            while tc_iteration_count < b2b_iteration:
                # Initialize verdicts
                tc_setup_failure = False
                tc_run_test_failure = False
                verdict = "NONE"
                running_tc.test_ok = False

                # Initialize user interruption flags
                run_user_interruption_request = False

                # Run TC Setup
                # Update in all the case the error message
                (self._error.Code, self._error.Msg), setup_user_interruption_request = \
                    self.__tc_catch_exceptions(running_tc, SETUP_STEP)

                if self._error.Code != Global.SUCCESS:
                    verdict = self._verdict.BLOCKED
                    b2b_verdict_count[verdict] += 1
                    tc_setup_failure = True

                if not tc_setup_failure:
                    # Run TC RunTest
                    # Update in all the case the error message
                    (self._error.Code, self._error.Msg), run_user_interruption_request = \
                        self.__tc_catch_exceptions(running_tc, RUN_STEP)

                    if self._error.Code not in (Global.SUCCESS, Global.VALID, Global.INCONCLUSIVE):
                        tc_run_test_failure = True
                    else:
                        running_tc.test_ok = True

                    verdict = Util.error_to_verdict(self._error.Code)
                    b2b_verdict_count[verdict] += 1

                # Run TC TearDown
                (self._error.Code, clean_up_output_msg), teardown_user_interruption_request = \
                    self.__tc_catch_exceptions(running_tc, TEARDOWN_STEP)

                if self._error.Code != Global.SUCCESS:
                    # inform the user if error in TEARDOWN and SETUP + RUNTEST OK)
                    # inform ACS test case manager when an interruption is detected
                    if teardown_user_interruption_request or (not tc_run_test_failure and not tc_setup_failure):
                        # error msg could be a list. Display it as a list, not as a tab
                        if isinstance(clean_up_output_msg, list):
                            self._error.Msg.insert(0, clean_up_output_msg)
                            self._error.Msg.insert(0, "WARNING: TEARDOWN -")
                        else:
                            self._error.Msg = "WARNING: TEARDOWN - %s" % clean_up_output_msg

                if b2b_iteration > 1:
                    msg = "%s Iteration #%d VERDICT: %s - " % (
                        running_tc.get_name(),
                        tc_iteration_count + 1,
                        verdict)

                    if isinstance(self._error.Msg, list):
                        msg = msg.join(str(x) for x in self._error.Msg)
                    else:
                        msg = msg + self._error.Msg

                    self._logger.info(msg)

                    # update b2b verdict in aplogs
                    self._dut_instance.inject_device_log("i", "ACS_TESTCASE", msg)

                tc_iteration_count += 1
                self.tc_iteration_count += 1

                # Manage all reports for this test case iteration execution
                # Manage all reports for this test case execution
                self._handle_test_case_debug_report(tc_iteration_count, verdict)

                # Update self._user_interruption flag to follow Keyboard interruption event
                self._user_interruption_request = (self._user_interruption_request or setup_user_interruption_request or
                                                   run_user_interruption_request or teardown_user_interruption_request)

                # Check device is still alive or user has interrupted the execution
                self._has_critical_failure_occurred = self._is_critical_failure(self._error.Msg)

                if self._has_critical_failure_occurred or self._user_interruption_request:
                    break

        # Run TC Finalize
        (finalize_error_code, finalize_output_msg), finalize_user_interruption_request = \
            self.__tc_catch_exceptions(running_tc, FINALIZE_STEP)
        if finalize_error_code != Global.SUCCESS:
            # inform ACS test case manager when an interruption is detected
            if finalize_user_interruption_request:
                if isinstance(finalize_output_msg, list):
                    self._error.Msg.insert(0, finalize_output_msg)
                    self._error.Msg.insert(0, "WARNING: FINALIZE -")
                else:
                    self._error.Msg = "WARNING: FINALIZE - %s" % finalize_output_msg

        # Update self._user_interruption flag to follow Keyboard interruption event
        self._user_interruption_request = self._user_interruption_request or finalize_user_interruption_request

        # Compute verdict for Back-to-Back test cases
        if b2b_iteration > 1:
            verdict = self._get_b2b_verdict(b2b_iteration, b2b_verdict_count)

        # Reset variable for next TCs
        self.tc_iteration_count = 1

        return verdict, self._error.Msg

    def __get_log_files(self, pattern='*.log'):
        """

        :return:
        :rtype:
        """
        fileslist = []
        for root, dirnames, filenames in os.walk(self._dut_instance.get_report_tree().get_report_path()):
            for filename in fnmatch.filter(filenames, pattern):
                fileslist.append(os.path.join(root, filename))
        return fileslist

    def __parse_log_file(self, filename):
        """

        :param filename:
        :type filename:
        :return:
        :rtype:
        """

        metrics_logs = []
        with open(filename, 'r') as logs:
            for line in logs.readlines():
                if "***** UNEXPECTED DEVICE REBOOT! *****" in line:
                    metrics_logs.append(line)
        return metrics_logs

    def __get_metrics_logs(self):
        """

        :return:
        :rtype:
        """
        metrics_logs = []
        filenames = self.__get_log_files()
        if len(filenames) == 1:
            metrics_logs = self.__parse_log_file(filenames[0])
        else:
            # fallback => degraded mode
            # We got the info from Metrics
            for error in xrange(CampaignMetrics.instance().unexpected_reboot_count):
                metrics_logs.append("ACS ERROR ***** UNEXPECTED DEVICE REBOOT! *****")
        return metrics_logs

    def _handle_test_case_debug_report(self, iteration, verdict):
        """ Manage all test case reporting actions at test case execution
        Retrieve crash events if any and fill debug report file if needed
        Send live reporting test case report information
        :param iteration: Current test case iteration number
        :param verdict: Current test case iteration-instance verdict
        """

        # Get the crash events
        device_crash_events = self._dut_instance.get_crash_events_data(self._test_case)

        # Collect crash information and/or debug data
        if (device_crash_events or "DebugModule" in self._dut_instance.device_modules and
                self._dut_instance.device_modules['DebugModule']):
            self._dut_instance.retrieve_debug_data(verdict=verdict,
                                                   tc_debug_data_dir=self._tc_debug_directory)
        # Fill debug report file
        if (verdict != self._verdict.PASS) or device_crash_events:
            try:
                self.__debug_report.add_debug_log(self._test_case.get_name(),
                                                  self._test_case.tc_order,
                                                  self.execution_nb,
                                                  iteration,
                                                  verdict,
                                                  device_crash_events,
                                                  metrics_logs=self.__get_metrics_logs())
            except (KeyboardInterrupt, SystemExit):
                raise

            except Exception as ex:
                self._logger.error("Cannot fill debug report: %s" % ex)
        # ACS Live Reporting: send TestCase Update info at each iteration to remote server
        if self._live_reporting_interface:
            self._live_reporting_interface.update_running_tc_info(crash_list=device_crash_events,
                                                                  test_info={},
                                                                  device_info=self._device_info_to_report)

    def _execute_b2b_continuous_mode(self, running_tc, b2b_iteration):
        """ execute_b2b_continuous_mode

        This function executes UC in a B2B mode in continuous mode.
        Only Runtest will be looped upon.

        :param running_tc: Object implementing the TC
        :param b2b_iteration: Number of iterations to be executed in case of B2B TC

        """

        # TC Execution Counter
        self.tc_iteration_count = 1
        tc_iteration_count = 0
        b2b_verdict_count = {x: 0 for x in Util.Verdict2Global.map}

        # Initialize verdicts
        tc_init_failure = False
        tc_setup_failure = False
        tc_run_test_failure = False
        running_tc.test_ok = False
        verdict = "NONE"

        # Initialize user interruption flags
        setup_user_interruption_request = False
        teardown_user_interruption_request = False

        # Run TC Init
        # Update in all the case the error message
        (self._error.Code, self._error.Msg), self._user_interruption_request = \
            self.__tc_catch_exceptions(running_tc, INIT_STEP)
        if self._error.Code != Global.SUCCESS:
            verdict = self._verdict.BLOCKED
            tc_setup_failure = True
            tc_init_failure = True
        else:
            # Run TC Setup
            # Update in all the case the error message
            (self._error.Code, self._error.Msg), setup_user_interruption_request = \
                self.__tc_catch_exceptions(running_tc, SETUP_STEP)
            if self._error.Code not in (Global.SUCCESS, Global.VALID, Global.INCONCLUSIVE):
                verdict = self._verdict.BLOCKED
                tc_setup_failure = True

        if not tc_setup_failure:
            # Run TC RunTest
            while tc_iteration_count < b2b_iteration:
                (self._error.Code, run_test_output_msg), run_user_interruption_request = \
                    self.__tc_catch_exceptions(running_tc, RUN_STEP)

                verdict = Util.error_to_verdict(self._error.Code)
                b2b_verdict_count[verdict] += 1

                msg = "%s Iteration #%d VERDICT: %s (%s)" % (running_tc.get_name(),
                                                             tc_iteration_count + 1,
                                                             verdict,
                                                             run_test_output_msg)
                self._error.Msg = run_test_output_msg
                self._logger.info(msg)
                # update each iteration verdict in aplogs
                self._dut_instance.inject_device_log("i", "ACS_TESTCASE", msg)

                tc_iteration_count += 1
                self.tc_iteration_count += 1

                # Manage all reports for this test case execution
                self._handle_test_case_debug_report(tc_iteration_count, verdict)

                # Update self._user_interruption flag to follow Keyboard interruption event
                self._user_interruption_request = (self._user_interruption_request or setup_user_interruption_request or
                                                   run_user_interruption_request)

                # Check device is still alive or user has interrupted the execution
                self._has_critical_failure_occurred = self._is_critical_failure(self._error.Msg)

                # Check device is still alive or user has interrupted the execution
                if self._has_critical_failure_occurred or self._user_interruption_request:
                    break

            # Compute verdict for Back-to-Back test cases
            verdict = self._get_b2b_verdict(b2b_iteration, b2b_verdict_count)

            # If Verdict is fail, remember it for global verdict
            if verdict == self._verdict.FAIL:
                tc_run_test_failure = True

        if not tc_setup_failure and not tc_run_test_failure:
            running_tc.test_ok = True

        # Run TC TearDown
        if not tc_init_failure:
            (self._error.Code, clean_up_output_msg), teardown_user_interruption_request = \
                self.__tc_catch_exceptions(running_tc, TEARDOWN_STEP)

            if self._error.Code != Global.SUCCESS:
                # inform the user if error in TEARDOWN and SETUP + RUNTEST OK)
                # inform ACS test case manager when an interruption is detected
                if teardown_user_interruption_request or (tc_run_test_failure is False and tc_setup_failure is False):
                    clean_up_output_msg = "WARNING: TEARDOWN - %s" % clean_up_output_msg
                    self._error.Msg += " (%s)" % clean_up_output_msg

        # Run TC Finalize
        (finalize_error_code, finalize_output_msg), finalize_user_interruption_request = \
            self.__tc_catch_exceptions(running_tc, FINALIZE_STEP)
        if finalize_error_code != Global.SUCCESS:
            # inform ACS test case manager when an interruption is detected
            if finalize_user_interruption_request:
                finalize_output_msg = "WARNING: FINALIZE -  %s" % finalize_output_msg
                self._error.Msg += " (%s)" % finalize_output_msg

        # Update self._user_interruption flag to follow Keyboard interruption event
        self._user_interruption_request = (self._user_interruption_request or
                                           teardown_user_interruption_request or
                                           finalize_user_interruption_request)

        # Check device is still alive for setup and teardown cases
        # In case of teardown, do not erase critical failures occurred in runtest
        if not self._has_critical_failure_occurred:
            self._has_critical_failure_occurred = self._is_critical_failure(self._error.Msg)

        # Reset variable for next TCs
        self.tc_iteration_count = 1

        return verdict, self._error.Msg

    def setup(self, global_config, debug_report, do_first_power_cycle):
        """ setup

        :param flash_file: Name of the SW image to be flashed
        :param global_config: Dictionary containing all XML file information
        """

        status = None

        self.__debug_report = debug_report
        self._global_config = global_config

        # Get Campaign Parameters
        self._skip_boot_on_power_cycle = Util.get_config_value(self._global_config.campaignConfig,
                                                               "Campaign Config", "skipBootOnPowerCycle", False,
                                                               default_cast_type="str_to_bool")

        self._boot_retry_number = Util.get_config_value(self._global_config.campaignConfig,
                                                        "Campaign Config", "bootRetryNumber", "0",
                                                        default_cast_type=int)

        if self._boot_retry_number < 0:
            error_msg = "Wrong value used for Campaign Config file in [bootRetryNumber] " \
                        "option entry: Use an int value >=0 !"
            self._logger.error(error_msg)
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)
        else:
            self._boot_retry_number += 1

        self._power_cycle_between_tc = Util.get_config_value(self._global_config.campaignConfig,
                                                             "Campaign Config", "powerCycleBetweenTC", False,
                                                             default_cast_type="str_to_bool")

        self._power_cycle_on_failure = Util.get_config_value(self._global_config.campaignConfig,
                                                             "Campaign Config", "powerCycleOnFailure", False,
                                                             default_cast_type="str_to_bool")

        # For retro-compatibility we keep management of finalPowerOff parameter
        final_power_off = Util.get_config_value(self._global_config.campaignConfig,
                                                "Campaign Config", "finalPowerOff")

        final_dut_state = Util.get_config_value(self._global_config.campaignConfig,
                                                "Campaign Config", "finalDutState")

        # In case both parameters are used,
        # raise an exception to force user to use 'finalDutState' parameter
        if final_power_off is not None and final_dut_state is not None:
            warning_msg = "Both 'finalPowerOff' and 'finalDutState' campaign parameters are used ! " \
                          "Using value of 'finalDutState' parameter, value of 'finalPowerOff' will be ignored !"
            self._logger.warning(warning_msg)
            # Force value of finalPowerOff to None
            final_power_off = None

        # Store value of finalDutState if exists
        if final_dut_state is not None:
            final_dut_state = str(final_dut_state).upper()
            if DeviceState.isDeviceState(final_dut_state):
                self._final_dut_state = final_dut_state
            else:
                error_msg = "'finalDutState' campaign parameter is not set correctly (%s) !" % final_dut_state
                self._logger.error(error_msg)
                self._logger.error("Use following possible values: %s" % str(DeviceState.availableState()))
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        # Set finalDutState value using value of finalPowerOff if exists
        elif final_power_off is not None:
            self._logger.warning("'finalPowerOff' campaign parameter will soon no longer be supported ! "
                                 "Use 'finalDutState' campaign parameter instead.")

            if Util.str_to_bool(str(final_power_off)):
                self._final_dut_state = DeviceState.OFF
            else:
                self._final_dut_state = DeviceState.ON

        # By default finalDutState is no-change
        else:
            self._logger.info("'finalDutState' campaign parameter is not set ! Use its default value 'NOCHANGE'.")
            self._final_dut_state = DeviceState.NC

        # Override the value of finalDutState into globalconfig dictionary
        self._global_config.campaignConfig["finalDutState"] = self._final_dut_state

        # Get b2b target rate
        self._target_b2b_rate = Util.get_config_value(self._global_config.campaignConfig,
                                                      "Campaign Config", "targetB2bPassRate", 80, default_cast_type=int)

        # The PHONE1 is always the DUT
        self._dut_instance = DeviceManager().get_device(AcsConstants.DEFAULT_DEVICE_NAME)

        # DO first connection with the device / board
        # => if failure exception raised catched in CampagneEngine instance and verdict set to BLOCKED
        if do_first_power_cycle:
            # FIXME: this code should be handle by power_cycle_device function
            # to have one entry point
            (connection_status, status_msg) = self.connect_device(do_first_power_cycle)
            if connection_status:
                # check that ACS agent is installed
                agent_version = self._dut_instance.device_properties.acs_agent_version
                if agent_version == AcsConstants.NOT_INSTALLED:
                    # agent is not installed
                    self._logger.warning(
                        "ACS Agent is not installed on the device. UECommands that need it won't be able to run.")
                elif agent_version in [None, AcsConstants.NOT_AVAILABLE]:
                    # acs agent installation status is unknown
                    self._logger.warning("Unable to determine if ACS agent is installed or not")
                else:
                    # agent is installed, start it if it is not already running
                    self._dut_instance.init_acs_agent()
            else:
                # Unable to boot&connect the device after test
                self._logger.debug(status_msg)
                status = DeviceException.DUT_BOOT_ERROR

        # Instantiate all device modules
        # Can be done without device connected as module are only loaded on the ACS test bench
        # But device has to be connected at least one time before and serial number retrieved
        # else crashmodule will not be initialized
        self._dut_instance.setup()

        return status

    def connect_device(self, is_first_power_cycle):
        """
        This function boot the device and establish connection. It also update metrics
        :type tcase_order: boolean
        :param is_first_power_cycle: do not switch off on the first time

        :rtype: boolean, string
        :return: status, error message
        """
        connection_status, status_msg, power_cycle_total_count, boot_failure_count, connection_failure_count = \
            self._dut_instance.init_device_connection(self._skip_boot_on_power_cycle,
                                                      is_first_power_cycle,
                                                      self._boot_retry_number)

        # Update campaign metrics
        self.__campaign_metrics.total_boot_count += power_cycle_total_count
        self.__campaign_metrics.boot_failure_count += boot_failure_count
        self.__campaign_metrics.connect_failure_count += connection_failure_count

        # Power cycle on all other devices if parameter powerCycleOnFailure is set to True
        # @TODO: We could do it in parallel, but for the moment this implementation covers the needs
        for device_instance in DeviceManager().get_all_devices():
            if device_instance.config.device_name != AcsConstants.DEFAULT_DEVICE_NAME:
                # User shall set "powerCycleOnFailure" to true in his bench config for the device which to be
                # rebooted on failure, as follow :
                # <Phone name="PHONE1" device_model="my_device_model" description="my_description" >
                # <Parameter powerCycleOnFailure="true" />
                # </Phone>
                is_power_cycle_required = device_instance.get_config("powerCycleOnFailure", "False", "str_to_bool")
                if is_power_cycle_required:
                    device_instance.init_device_connection(False, is_first_power_cycle, self._boot_retry_number)

        return connection_status, status_msg

    def __get_acceptance_criteria(self, tcase_conf):
        """ Retrieve acceptance criteria from:
            First the test case itself
            Then the dut if not specified for the test case
        """
        (tc_max_attempt, tc_acceptance) = tcase_conf.get_params().get_acceptance_criteria()
        (dut_max_attempt, dut_acceptance) = self._dut_instance.get_tc_acceptance_criteria()

        if tc_max_attempt > 0 and tc_acceptance > 0:
            return tc_max_attempt, tc_acceptance
        elif dut_max_attempt > 0 and dut_acceptance > 0:
            return dut_max_attempt, dut_acceptance
        else:
            return 1, 1

    def __block_execution(self, tcase_conf, tcase_order, tc_start_time, error_msg):
        self._tc_verdict = self._verdict.BLOCKED

        # Compute the verdict regarding the expected result
        expected_verdict = tcase_conf.get_params().get_tc_expected_result()
        obtained_verdict = self._tc_verdict
        # Update the test case verdict after computation
        self._tc_verdict = Verdict.compute_verdict(expected_verdict, obtained_verdict)

        # Log the test case verdict
        verdict_code = "%s: VERDICT: %s (EXPECTED: %s - OBTAINED: %s)" \
                       % (tcase_conf.get_name(), self._tc_verdict, expected_verdict, obtained_verdict)
        verdict_msg = "%s: MESSAGE: %s" % (tcase_conf.get_name(), error_msg)

        self._logger.info(verdict_code)
        self._logger.info(verdict_msg)

        if expected_verdict != self._verdict.PASS:
            # Only display expected, obtained verdicts if different from PASS
            tcase_conf.add_message([verdict_code, str(error_msg)])

        # update TC verdict in report
        all_verdicts = (expected_verdict, obtained_verdict, self._tc_verdict)
        self.__test_report.add_result(tcase_conf, tcase_order, tc_start_time, datetime.now(),
                                      all_verdicts, self.execution_nb, self._execution_results)

        return self._tc_verdict, error_msg

    def __tc_catch_exceptions(self, target_object, method_name, *args, **kwargs):
        """
        Wrapped call to target_object.method_name(*args, **kwargs)
        """
        # Boolean used to inform user request end of the campaign
        abort_campaign_request = False

        try:
            exec_method = getattr(target_object, method_name)
            result = exec_method(*args, **kwargs)

        except (KeyboardInterrupt, SystemExit):
            return_code = Global.BLOCKED
            return_msg = AcsBaseException.USER_INTERRUPTION
            abort_campaign_request = True
            self._logger.error(return_msg)
            result = (return_code, return_msg)

        except AcsBaseException as ex:
            return_code = ex.get_error_code()
            return_msg = ex.get_error_message()
            self._logger.error(return_msg)
            result = (return_code, return_msg)

        except Exception:
            return_code = Global.BLOCKED
            return_msg = str(format_exception_info())
            self._logger.error(return_msg)
            result = (return_code, return_msg)

        return result, abort_campaign_request

    @staticmethod
    def _create_tc(tcase_class, tcase_conf, global_config):
        """
        Instantiate TC using its class name
        :param tcase_class: Class of the test case
        :param tcase_conf: TestCase configuration
        :param global_config: Campaign global configuration

        :return: test case instance
        """
        test_case = tcase_class(tcase_conf, global_config)
        return Global.SUCCESS, test_case

    def execute_test_case(self, error_msg, execution_status, tcase_conf, tcase_order, tc_start_time):
        b2b_iteration = self._test_case.get_b2b_iteration()
        b2b_continuous_mode = self._test_case.get_b2b_continuous_mode()
        self.execution_nb = 0
        self._execution_results = []
        success_counter = 0
        verdicts = []
        tc_stopping_time = None

        if self.max_attempt >= self.acceptance_nb:
            self._dut_instance.inject_device_log("i", "ACS_TESTCASE", "NAME: {0}: ORDER {1}".format(
                self._test_case.get_name(),
                tcase_order))
            while (self.execution_nb < self.max_attempt) and (success_counter < self.acceptance_nb):

                # Reset execution_status, to prevent wrong status on retry
                execution_status = None

                if self.execution_nb >= 1:
                    msg = "%s: RETRY %d" % (self._test_case.get_name(), self.execution_nb)
                    self._logger.info(msg)
                else:
                    tcase_conf.clear_messages()
                self.execution_nb += 1

                if not b2b_continuous_mode or b2b_iteration <= 1:
                    (self._tc_verdict, self._error.Msg) = \
                        self._execute_b2b(self._test_case, b2b_iteration)
                else:
                    (self._tc_verdict, self._error.Msg) = \
                        self._execute_b2b_continuous_mode(self._test_case, b2b_iteration)

                tc_stopping_time = datetime.now()
                # Compute the verdict regarding the expected result
                expected_verdict = self._test_case.get_tc_expected_result()
                obtained_verdict = self._tc_verdict
                # Update the test case verdict after computation
                self._tc_verdict = Verdict.compute_verdict(expected_verdict, obtained_verdict)

                # Log the test case verdict
                verdict_code = "VERDICT: %s (EXPECTED: %s - OBTAINED: %s)" \
                               % (self._tc_verdict,
                                  expected_verdict,
                                  obtained_verdict)
                verdict_msg = "MESSAGE: %s " % self._error.Msg

                self._logger.log(ACSLogging.MINIMAL_LEVEL, "%s: %s" % (self._test_case.get_name(), verdict_code))
                self._logger.log(ACSLogging.MINIMAL_LEVEL, "%s: %s" % (self._test_case.get_name(), verdict_msg))

                # update b2b verdict in aplogs
                self._dut_instance.inject_device_log("i", "ACS_TESTCASE", "VERDICT: {0}: {1}".format(
                    self._test_case.get_name(),
                    self._tc_verdict))

                self._execution_results.append(self._tc_verdict)

                if self.max_attempt > 1:
                    tmp_msg = "TRY %d: %s " % (self.execution_nb, verdict_code)

                    # error msg could be a list. Display it as a list, not as a tab
                    if isinstance(self._error.Msg, list):
                        msg = self._error.Msg
                        msg.insert(0, tmp_msg)
                    else:
                        msg = tmp_msg + "=> %s" % self._error.Msg

                else:
                    if expected_verdict == self._verdict.PASS:
                        msg = self._error.Msg
                    else:
                        # Only display expected, obtained verdicts if different from PASS
                        if isinstance(self._error.Msg, list):
                            msg = [verdict_code] + self._error.Msg
                        else:
                            msg = [verdict_code, str(self._error.Msg)]

                tcase_conf.add_message(msg)

                if self._tc_verdict == self._verdict.PASS:
                    success_counter += 1

                verdicts.append(self._tc_verdict)

                # Check if user has interrupted the test
                if self._user_interruption_request:
                    execution_status = AcsBaseException.USER_INTERRUPTION
                    break

                if self.execution_nb < self.max_attempt and success_counter < self.acceptance_nb:
                    if self._test_case.handle_power_cycle:
                        status_power_cycle, status_power_cycle_msg = self.power_cycle_device()
                        if not status_power_cycle:
                            # Unable to boot&connect the device after test
                            execution_status = DeviceException.DUT_BOOT_ERROR
                            self._logger.debug(status_power_cycle_msg)

            # Create final verdict after doing tc execution tries
            self._tc_verdict = self._verdict.FAIL
            for v in Util.Verdict2Global.map:
                if all(verdict == v for verdict in verdicts):
                    self._tc_verdict = v
                    break

            # Check the acceptance criteria
            if success_counter >= self.acceptance_nb:
                # Reset critical failure count if tc verdict is success
                self._has_critical_failure_occurred = False
                # Enough PASS => final verdict = PASS
                self._tc_verdict = self._verdict.PASS

            if len(verdicts) > 1:
                msg = "ACCEPTANCE CRITERIA VERDICT: %s" % self._tc_verdict
                msg += " (acceptance=%d, try=%d, success=%d)" % (self.acceptance_nb,
                                                                 self.execution_nb,
                                                                 success_counter)
                self._logger.info("%s: %s" % (self._test_case.get_name(), msg))
                tcase_conf.add_message(msg)

            # If the user sets his test case as critical (refer to option 'IsCritical' in the test case file),
            # a critical failure will be raised if the verdict is not PASS
            if self._test_case.get_is_critical() and not Util.Verdict.is_pass(self._tc_verdict):
                self._has_critical_failure_occurred = True
                self.__campaign_metrics.add_critical_failure()
                critic_msg = "Test case parameter 'IsCritical' is set to True and unexpected verdict occurred !"
                # Update final message and datetime
                critical_failure_message = AcsBaseException.CRITICAL_FAILURE + " (%s)" % (critic_msg,)
                self._logger.critical("%s: %s" % (self._test_case.get_name(), critical_failure_message))

            # Check if final verdict (after retries) is critical
            # Record last verdict to determine if power cycle on failure is required
            elif not self._has_critical_failure_occurred:
                self._has_critical_failure_occurred = self._is_critical_failure(self._error.Msg)

            # update TC verdict in report
            all_verdicts = expected_verdict, obtained_verdict, self._tc_verdict
            self.__test_report.add_result(tcase_conf, tcase_order, tc_start_time, datetime.now(),
                                          all_verdicts, self.execution_nb, self._execution_results)
        else:
            error_msg = ("Prohibitive behavior: "
                         "TcMaxAttempt value (%s) is lower than "
                         "TcAcceptanceCriteria value (%s)" % (str(self.max_attempt), str(self.acceptance_nb)))
        return error_msg, execution_status, tc_stopping_time, success_counter

    def check_board_availability(self, conf, verdict=None):
        """
        Checks board availability based on test case configuration.
        If test case is tagged as "IsProvisioning" check is done
        at the end, else before starting test case.

        Instance's attributes update:

            * self._device_info_status: bears whether info retrieval from DUT is PASS or not
            * self._device_info_to_report: bears Device info retrieved from DUT

        .. note:: DUT.get_reporting_device_info() method uses `crashToolUploader` tool.
            This may change in future...

        :param TestCaseConf conf: Test case configuration
        :param Verdict verdict: (optional) Test case verdict (when called after its execution)
        """
        is_provisioning = conf.is_provisioning

        if ('TCR' in self._device_info_to_report and
                'build' in self._device_info_to_report['TCR'] and
                'buildId' in self._device_info_to_report['TCR']['build']):
            # Reset build ID if already present,
            # in order not to get previously cached (and maybe corrupted) build ID.
            self._device_info_to_report['TCR']['build']['buildId'] = ""

        # First condition applies on all test cases except for "IsProvisioning" tagged one(s)
        if ((verdict is None and not is_provisioning) or
                # Second condition applies only on test cases tagged "IsProvisioning" which get PASS verdict
                (is_provisioning and verdict == self._verdict.PASS)):
            self._device_info_status, self._device_info_to_report = self._dut_instance.get_reporting_device_info()

    def execute(self, tcase_class, tcase_conf, tcase_order):
        """ execute

        This function manages the execution of the TC itself (setup,
        runtest & cleanup) for each TC. It also manages the B2B mechanisms

        :type tcase_class: string
        :param tcase_class: TC class
        :type tcase_conf: TestCaseConf
        :param tcase_conf: the TC configuration
        :type tcase_order: int
        :param tcase_order: TC order in campaign execution

        :rtype: tuple
        :return: tuple containing: - reported verdict
                                   - output messages
        """

        execution_status = None
        error_msg = None
        tc_start_time = datetime.now()
        tc_stopping_time = None
        success_counter = 0
        (self.max_attempt, self.acceptance_nb) = self.__get_acceptance_criteria(tcase_conf)

        # Create test case debug dir
        if "DebugModule" in self._dut_instance.device_modules and self._dut_instance.device_modules['DebugModule']:
            self._tc_debug_directory = os.path.join(self._dut_instance.get_report_tree().get_report_path(),
                                                    self._dut_instance.get_name(), Folders.DEBUG_LOGS,
                                                    tcase_conf.get_name().replace("\\", "/").split("/")[-1] +
                                                    "_" + str(tcase_order))
            if not os.path.exists(self._tc_debug_directory):
                os.makedirs(self._tc_debug_directory)

        # Start logging for test
        if self._tc_debug_directory and self._dut_instance.retrieve_tc_debug_log:
            self._dut_instance.start_device_log(os.path.join(self._tc_debug_directory,
                                                             self._dut_instance.retrieve_tc_debug_log))

        # Collect additional device and build information before test case execution
        # This applies on all test cases except for "IsProvisioning" tagged one(s)
        if not(tcase_conf.is_provisioning and tcase_conf.do_device_connection):
            self.check_board_availability(tcase_conf)

        # Sending TestCase Starting info to remote server for Live Reporting control
        if self._live_reporting_interface:
            self._live_reporting_interface.send_start_tc_info(tc_name=tcase_conf.get_name(),
                                                              tc_order=tcase_order,
                                                              device_info=self._device_info_to_report)
        try:
            # Initialize test case runner
            (tc_init_code, tc_object), tc_user_abort_request = (
                self.__tc_catch_exceptions(self, "_create_tc", tcase_class, tcase_conf, self._global_config)
            )

            if tc_init_code == Global.SUCCESS:
                # Get the test case class instance
                self._test_case = tc_object
                self._test_case.tc_order = tcase_order

                if self._test_case:
                    error_msg, execution_status, tc_stopping_time, success_counter = (
                        self.execute_test_case(error_msg, execution_status, tcase_conf, tcase_order, tc_start_time)
                    )
                else:
                    error_msg = "Unable to instantiate test case"
            else:
                error_msg = tc_object
                # Add the error to the tc log to have it in the reporting (ease the failure analysis)
                tcase_conf.add_message(error_msg)
                if tc_user_abort_request:
                    execution_status = AcsBaseException.USER_INTERRUPTION

            if error_msg is not None:
                (self._tc_verdict,
                 output_messages) = self.__block_execution(tcase_conf, tcase_order, tc_start_time, error_msg)
            # update final verdict in aplogs
            self._dut_instance.inject_device_log(
                "i", "ACS_TESTCASE", "FINAL_VERDICT: {0}: {1}".format(tcase_conf.get_name(), self._tc_verdict))

            # Stop logging for test
            if self._tc_debug_directory and self._dut_instance.retrieve_tc_debug_log:
                self._dut_instance.stop_device_log()
            self._dut_instance.clean_debug_data()

        finally:
            verdict = self._tc_verdict if not self._user_interruption_request else self._verdict.INTERRUPTED
            # This applies only on test cases tagged "IsProvisioning"
            if tcase_conf.is_provisioning:
                self.check_board_availability(self._test_case.conf, verdict=verdict)
            # Sending TestCase Stopped info to remote server for Live Reporting control
            if self._live_reporting_interface is not None:
                params = dict(
                    verdict=verdict,
                    execution_nb=self.execution_nb,
                    success_counter=success_counter,
                    max_attempt=self.max_attempt,
                    acceptance_nb=self.acceptance_nb,
                    tc_parameters=tcase_conf.get_params().get_params_as_dict(),
                    tc_comments=tcase_conf.get_messages(),
                    tc_description=tcase_conf.get_params().get_description(),
                    tc_b2b_iteration=tcase_conf.get_params().get_b2b_iteration(),
                    tc_b2b_continuous=tcase_conf.get_params().get_b2b_continuous_mode(),
                    tc_expected_results=tcase_conf.get_params().get_tc_expected_result(),

                )
                if tcase_conf.is_provisioning:
                    params['device_info'] = self._device_info_to_report
                self._live_reporting_interface.send_stop_tc_info(**params)

            # Stats the result
            LOGGER_FWK_STATS.info(("Executed test_case={0}; from use_case={1}; verdict={2}; tries={3}; "
                                   "max_attempt={4}; acceptance={5}").format(
                tcase_conf.get_name().replace("/", "\\"),
                inspect.getmodule(tcase_class).__name__.split(".")[-1],
                self._tc_verdict,
                self.execution_nb,
                self.max_attempt,
                self.acceptance_nb))

        if self._test_case and self._test_case.get_is_warning():
            warning_verdict = self._verdict.PASS
        else:
            warning_verdict = self._tc_verdict

        return self._tc_verdict, execution_status, warning_verdict

    def cleanup(self, campaign_error):
        """
        This method cleans up the execution phase by disconnecting devices
        & power it off when possible.
        Add a flag campaign_error to do some specific operations on the device

        :type campaign_error: boolean
        :param campaign_error: Notify if errors occurred

        :rtype: tuple of int and str
        :return: verdict and dut state
        """

        # Clean up the DUT
        status = False
        dut_state = DeviceState.NC
        try:
            if self._dut_instance is not None:
                status, dut_state = self._dut_instance.cleanup(campaign_error)
        finally:
            # Release all devices
            DeviceManager().release_all_devices()
            # Release all equipments
            EquipmentManager().delete_all_equipments()

        return status, dut_state

    def get_device_instance(self):
        """
        Get the device instance or None if not already instantiated

        :rtype: object
        :return: device instance
        """
        return self._dut_instance

    def set_live_reporting_interface(self, live_interface=None):
        """
        Set the live reporting interface

        :rtype: None or Exception
        :return: Exception if an existing interface already exists
        """
        if self._live_reporting_interface is None:
            self._live_reporting_interface = live_interface
        else:
            raise AcsToolException(AcsToolException.INSTANTIATION_ERROR, "A live reporting interface already exist!")
