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

# pylama:ignore=E501,E211
import os
import platform
from datetime import datetime
import sys
import socket
import uuid
from acs.UtilitiesFWK.Utilities import Obfuscated

# Add acs_test_scripts repo path into system path to access it
# This is done here because TR instanciates CampaignEngine instead of
# invoking ACS.py
ts_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "acs_test_scripts"))
if os.path.exists(ts_path) and ts_path not in sys.path:
    sys.path.append(ts_path)

ts_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
if os.path.exists(ts_path) and ts_path not in sys.path:
    sys.path.append(ts_path)

from acs.Core.CampaignMetrics import CampaignMetrics  # noqa
from acs.Core.FileParsingManager import FileParsingManager  # noqa
# TestCaseManager requires Equipments, it shall be after adding acs_test_scripts to the system path
from acs.Core.TestCaseManager import TestCaseManager  # noqa
from acs.Core.CampaignGenerator.CampaignGeneratorFactory import CampaignGeneratorFactory  # noqa
from acs.Core.CatalogParser.ParameterCatalogParser import ParameterCatalogParser  # noqa
from acs.Core.CatalogParser.UseCaseCatalogParser import UseCaseCatalogParser  # noqa
from acs.Core.CatalogParser. TestStepCatalogParser import TestStepCatalogParser  # noqa
from acs.Device.DeviceManager import DeviceManager  # noqa
from acs.ErrorHandling.AcsBaseException import AcsBaseException  # noqa
from acs.ErrorHandling.DeviceException import DeviceException  # noqa
from acs.Core.Report.ACSLogging import ACSLogging, LOGGER_FWK, LOGGER_FWK_STATS  # noqa
from acs.Core.Report.CampaignReportTree import CampaignReportTree  # noqa
from acs.Core.Report.DebugTestReport import DebugReport  # noqa
from acs.Core.Report.Live.LiveReporting import LiveReporting  # noqa
from acs.Core.Report.TestReport import Report  # noqa
from acs.UtilitiesFWK.ZipUtilities import zip_folder  # noqa
from acs.Core.PathManager import Paths  # noqa
from acs.Core.PathManager import Files  # noqa
from acs.UtilitiesFWK.UuidUtilities import is_uuid4  # noqa
from acs.Core.Equipment.EquipmentManager import EquipmentManager  # noqa
import acs.UtilitiesFWK.Utilities as Util  # noqa
from acs.Core.ArgChecker import ArgChecker  # noqa

MAX_TC_NB_AUTHORIZED = 5000


# pylint: disable=W0621
class CampaignEngine:
    VERDICT_SEPARATOR = ":"

    def __init__(self, report_folder=None):

        ACSLogging.initialize()

        self.__test_case_manager = None
        self.__file_parsing_manager = None
        self.__test_case_conf_list = []
        self.__logger = LOGGER_FWK
        self.__global_config = None
        self.__test_report = None
        self.__debug_report = None
        self.__sub_campaigns_list = []

        # Local Files
        self.__equipment_catalog = "Equipment_Catalog"

        # Local paths
        self.__campaign_report_tree = None
        self._campaign_report_path = report_folder

        self._campaign_elements = {}
        self._live_reporting_interface = LiveReporting.instance()
        self.__campaign_metrics = CampaignMetrics.instance()
        self.__stop_on_critical_failure = False
        self.__stop_on_first_failure = False
        self._credentials = ""

    @property
    def campaign_report_path(self):
        """
        Getter for the Campaign Report Path to be used for upload script
        :rtype: str
        :return: Campaign Report Path
        """
        if self.__campaign_report_tree:
            # If a campaign report tree is instantiate, ask it
            return_path = self.__campaign_report_tree.get_report_path()
        else:
            # If no, return cmd line option
            return_path = self._campaign_report_path
        return return_path

    def _get_campaign_report_filename_path(self):
        """
        Getter for the Campaign Report File Name Path
        :rtype: str
        :return: Campaign Report Path File Name
        """
        if self.__test_report:
            return self.__test_report.report_file_path
        else:
            return ""

    def __init_logger(self, hw_variant_name, serial_number, campaign_report_path, session_id):
        # Initialize the logger
        log_file_name = '{0}_{1}{2}.log'.format(Util.get_timestamp(), hw_variant_name, str(serial_number))
        logfile = os.path.join(campaign_report_path, log_file_name)
        Files.acs_output_name = logfile[:-4]
        ACSLogging.set_session_id(session_id)
        ACSLogging.set_output_path(logfile)

    def __init_configs(self, bench_config, flash_file_path):
        # Creates Global Parameters dictionary including
        # DUT config, Bench config, Campaign Config, Catalogs Config

        self.__global_config = Util.Dictionary(attribute1='benchConfig',
                                               attribute2='deviceConfig',
                                               attribute3='campaignConfig',
                                               attribute4='equipmentCatalog',
                                               attribute5='usecaseCatalog',
                                               attribute6='campaignReportTree')

        self.__global_config.benchConfig = {}
        self.__global_config.deviceConfig = {}
        self.__global_config.campaignConfig = {}
        self.__global_config.equipmentCatalog = {}
        self.__global_config.usecaseCatalog = {}
        self.__global_config.campaignReportTree = None

        # Creates File Parsing Manager object
        self.__file_parsing_manager = FileParsingManager(bench_config,
                                                         self.__equipment_catalog,
                                                         self.__global_config)

    def __init_report_path(self, campaign_name):
        # Initialize Campaign report path
        # Added microsecond precision to ensure multi campaigns launching
        if self._campaign_report_path is None:
            # No report path specified, provide the campaign name to generate a path
            self.__campaign_report_tree = CampaignReportTree(campaign_name=campaign_name)
        else:
            # Campaign report path was defined at the command line, use it
            self.__campaign_report_tree = CampaignReportTree(report_path=self._campaign_report_path)
            self.__campaign_report_tree.create_report_folder()

        # Add CampaignReportTree instance in the global_config
        self.__global_config.campaignConfig["campaignReportTree"] = self.__campaign_report_tree

    def __init_reports(self, campaign_report_path,
                       device_name, campaign_name, campaign_relative_path,
                       campaign_type, user_email, metacampaign_uuid):

        # Create test report
        self.__test_report = Report(campaign_report_path,
                                    device_name,
                                    campaign_name,
                                    campaign_relative_path,
                                    campaign_type,
                                    user_email,
                                    metacampaign_uuid)

        # initialize test report files (TestCase sections)
        self.__test_report.initialize_results(self.__test_case_conf_list)

        # Store report path in report tree
        self.__campaign_report_tree.report_file_path = self.__test_report.report_file_path

        # Create debug report
        self.__debug_report = DebugReport(campaign_report_path)

    def __init_live_reporting(self, campaign_name, campaign_uuid, user_email, live_reporting_plugin):
        """
        Instantiate a live reporting interface

        :param campaign_uuid: uuid of the campaign
        :type campaign_uuid: str

        :param live_reporting_plugin: live reporting plugin to instantiate
        :type live_reporting_plugin: str

        """
        self._live_reporting_interface.init(self.campaign_report_path,
                                            campaign_uuid=campaign_uuid,
                                            live_reporting_plugin=live_reporting_plugin)
        self._live_reporting_interface.send_start_campaign_info(campaign_uuid, campaign_name, user_email)

    def __random_sort_list(self, ordering_list, random_list, Group):
        import random

        random_iteration = len(ordering_list)
        while random_iteration > 0:
            random_index = random.randrange(len(ordering_list))
            item = ordering_list[random_index]
            if isinstance(item, Group):
                random_list.extend(item.tc_list)
            else:
                random_list.append(item)
            ordering_list.remove(item)
            random_iteration -= 1

    def __randomize_test_cases(self, tc_ordered_list):
        """ __randomize_test_cases

        This method randomly re-order TestCases from tc_ordered_list.
        tc_ordered_list is not modified.
        :return a TestCase list randomly re-ordered
        """

        class Group():

            def __init__(self, tc_list):
                self.tc_list = tc_list

        tc_random_list = []

        ordering_list = []
        group_list = []
        group_id = None

        for tc in tc_ordered_list:
            if tc.is_random():
                # fill ordering list
                if tc.get_group_id() is None:
                    # insert groups if some where being iterated
                    if group_id is not None:
                        ordering_list.append(Group(group_list))
                        group_id = None
                        group_list = []
                    # insert test case
                    ordering_list.append(tc)
                else:
                    # test case is in a group
                    if group_id is tc.get_group_id():
                        group_list.append(tc)
                    else:
                        if group_id is not None:
                            ordering_list.append(Group(group_list))
                        group_id = tc.get_group_id()
                        group_list = [tc]
            else:
                # insert groups if some where being iterated
                if len(group_list) is not 0:
                    ordering_list.append(Group(group_list))

                # add random tests that where being iterated
                if len(ordering_list) is not 0:
                    self.__random_sort_list(ordering_list, tc_random_list, Group)

                # reinit ordering params
                group_id = None
                group_list = []
                ordering_list = []

                # add test case to tc list
                tc_random_list.append(tc)

        # add random test cases if some remains
        if len(group_list) is not 0:
            ordering_list.append(Group(group_list))
        if len(ordering_list) is not 0:
            self.__random_sort_list(ordering_list, tc_random_list, Group)

        return tc_random_list

    def __log_acs_param(self, acs_params, is_displayed=True):
        """
        Log all ACS input parameters
        """
        if is_displayed:
            self.__logger.info("Starting ACS with following parameters:")
        params = ""
        for name, value in sorted(acs_params.iteritems()):
            if value not in(None, "") and name != "device_name":
                # Log everything except empty param and device_name (it will be log by the device manager)
                if name == "campaign_name":
                    # For campaign_name (that can be a part of a path), formalize it to avoid duplication
                    params += "{0}={1}; ".format(name, value.replace("/", "\\"))
                elif name == "credentials":
                    # Ofuscated credentials
                    value = Obfuscated(str(value))
                else:
                    params += "{0}={1}; ".format(name, value)
                if is_displayed:
                    self.__logger.info("\t%s = %s" % (name, value))
        if is_displayed:
            self.__logger.info("")
        return params

    def _log_acs_param_extra(self, acs_params):
        """
        Log all ACS input parameters
        """
        params = self.__log_acs_param(acs_params, False)

        if platform.system() == "Windows":
            release = platform.release()
        elif platform.dist():
            release = "{0}_{1}".format(platform.dist()[0], platform.dist()[1])

        params += "; os={0}_{1}".format(platform.system(), release)
        params += "; python_vers={0}_{1}".format(platform.python_version(), platform.architecture()[0])
        params += "; hostname={0}".format(socket.getfqdn())
        params += "; version={0}".format(Util.get_acs_release_version())
        user_home = os.path.split(os.path.expanduser('~'))
        if user_home:
            params += "; user={0}".format(user_home[-1])
        LOGGER_FWK_STATS.info("event=START; {0}".format(params))

    def __log_stop_campaign(self, msg, tc_order=None):
        LOGGER_FWK_STATS.info("event=STOP_ON_{0}".format(msg.replace(" ", "_").upper()))
        msg = "CAMPAIGN STOPPED ON %s !" % str(msg).upper()
        self.__logger.info("")
        self.__logger.info(msg)
        self.__logger.info("")
        if tc_order is not None:
            self.__test_report.add_comment(tc_order, msg)

    def __init_configuration(self, **kwargs):
        """
            This function initializes global configuration.

            :param campaign_name: Campaign xml file to execute.
            :type campaign_name: str

            :param campaign_relative_path: Campaign relative path.
            :type campaign_relative_path: str

            :param bench_config: Bench Config file to use.
            :type bench_config: str

            :param flash_file_path: Flash file full path.
            :type flash_file_path: str
        """
        flash_file_path = kwargs["flash_file_path"]

        # Creates Global Parameters dictionary including
        # DUT config, Bench config, Campaign Config
        self.__init_configs(kwargs["bench_config"], flash_file_path)

        # Check UC catalogs
        self.__logger.info('Checking ACS use case catalogs integrity...')
        self.__global_config.usecaseCatalog = UseCaseCatalogParser().parse_catalog_folder()

        # Checks Test Step catalogs
        self.__logger.info('Checking ACS test step catalogs integrity...')
        TestStepCatalogParser().parse_catalog_folder()

        # Parse equipment catalog
        self.__logger.info('Checking ACS equipment catalog integrity...')
        # self.__file_parsing_manager.parse_equipment_catalog()

        # Parse bench config file (used in case of multi phone)
        self.__logger.info('Checking ACS bench config integrity...')
        bench_config = self.__file_parsing_manager.parse_bench_config()
        self.__global_config.benchConfig = bench_config

        # Parse campaign config file # Get all test cases of all sub campaigns
        self.__logger.info('Checking ACS campaign integrity...')
        campaign_gen = CampaignGeneratorFactory.get_campaign_generator(self.__global_config, kwargs.get("camp_gen"))
        campaign_config_file_path, self.__test_case_conf_list, self.__sub_campaigns_list = campaign_gen.load(**kwargs)

        self._campaign_elements.update({"bench_config": kwargs["bench_config"]})
        self._campaign_elements.update({"campaign_config": campaign_config_file_path})
        self._campaign_elements.update({"test_cases": self.__test_case_conf_list})
        self._campaign_elements.update({"sub_campaigns": self.__sub_campaigns_list})

    def _setup(self, **kwargs):
        """
            This function initializes all global variables used in acs execution.
            It parses the arguments given to CampaignEngine,
            parses XML files associated & read the campaign content
            for the TestCaseManager to execute.

            :param device_name: Device model under test.
            :type device_name: str

            :param serial_number: Device id or serial number of the DUT.
            :type serial_number: str

            :param campaign_name: Campaign xml file to execute.
            :type campaign_name: str

            :param campaign_relative_path: Campaign relative path.
            :type campaign_relative_path: str

            :param bench_config: Bench Config file to use.
            :type bench_config: str

            :param device_parameters: List of device parameters to override default values in Device_Catalog.
            :type device_parameters: list

            :param flash_file_path: Flash file full path.
            :type flash_file_path: str

            :param random_mode: Enable random mode if your campaign is configured to run random TC.
            :type random_mode: bool

            :param user_email: Valid user email.
            :type user_email: str

            :param credentials: Credentials in User:Password format.
            :type credentials: str

            :rtype: bool
            :return: True if setup is correctly done, else False
        """

        status = None

        device_name = kwargs["device_name"]
        serial_number = kwargs["serial_number"]
        campaign_name = kwargs["campaign_name"]
        campaign_relative_path = kwargs["campaign_relative_path"]
        device_parameters = kwargs["device_parameter_list"]
        random_mode = kwargs["random_mode"]
        user_email = kwargs["user_email"]
        credentials = kwargs["credentials"]
        log_level_param = kwargs["log_level"]

        # In case the uuid is not set, generate it to ensure that the campaign has an id
        # This id is used for reporting purpose
        self.__logger.info('Checking metacampaign UUID integrity...')
        metacampaign_uuid = kwargs["metacampaign_uuid"]
        valid_uuid = is_uuid4(metacampaign_uuid)
        if not valid_uuid:
            self.__logger.warning("Metacampaign UUID is empty or not a valid UUID4; a new one is generated ...")
        metacampaign_uuid = metacampaign_uuid if valid_uuid else str(uuid.uuid4())
        self.__logger.info("Metacampaign UUID is {0}".format(metacampaign_uuid))

        self.__init_configuration(**kwargs)

        # Init Campaign report path
        self.__init_report_path(campaign_name)
        # Instantiate a live reporting interface
        campaign_name = os.path.splitext(os.path.basename(campaign_name))[0]
        self.__init_live_reporting(campaign_name,
                                   metacampaign_uuid,
                                   user_email,
                                   kwargs.get("live_reporting_plugin"))

        self.__stop_on_critical_failure = Util.str_to_bool(
            self.__global_config.campaignConfig.get("stopCampaignOnCriticalFailure", "False"))
        self.__stop_on_first_failure = Util.str_to_bool(
            self.__global_config.campaignConfig.get("stopCampaignOnFirstFailure", "False"))

        # Provide the global configuration for equipment manager and device manager
        # They will use it to retrieve or set values in it.
        EquipmentManager().set_global_config(self.__global_config)
        DeviceManager().set_global_config(self.__global_config)

        # Initialize equipments necessary to control DUT (io card, power supply, usb hub)
        EquipmentManager().initialize()

        # Read serial number if given as ACS command line
        if serial_number not in ["", None]:
            # Priority to serialNumber from --sr parameter
            device_parameters.append("serialNumber=%s" % str(serial_number))
        # Load the device
        device = DeviceManager().load(device_name, device_parameters)[Util.AcsConstants.DEFAULT_DEVICE_NAME]
        # store the device config file
        device_conf_list = []
        for dev in DeviceManager().get_all_devices():
            device_config_file = dev.get_config("DeviceConfigPath")
            if device_config_file:
                device_conf_list.append(device_config_file)
        self._campaign_elements.update({"devices": device_conf_list})

        # Init the logger
        self.__init_logger(device.hw_variant_name, serial_number, self.campaign_report_path, metacampaign_uuid)

        self.__logger.info('Checking acs version : %s' % str(Util.get_acs_release_version()))

        if self.__test_case_conf_list:
            if random_mode:
                self.__test_case_conf_list = self.__randomize_test_cases(self.__test_case_conf_list)
            # Parse parameter catalog
            parameter_catalog_parser = ParameterCatalogParser()
            self.__global_config.__setattr__("parameterConfig", parameter_catalog_parser.parse_catalog_folder())

            # Retrieve MTBF custom parameter to align logging level between the console and the log file
            is_logging_level_aligned = Util.str_to_bool(
                self.__global_config.campaignConfig.get("isLoggingLevelAligned", "False"))
            # Set log level according to global_config file content
            if log_level_param:
                logging_level = log_level_param
            else:
                logging_level = self.__global_config.campaignConfig.get("loggingLevel", "DEBUG")
            ACSLogging.set_log_level(logging_level, is_logging_level_aligned)

            # Set campaign_type when it exists
            campaign_type = self.__global_config.campaignConfig.get("CampaignType")

            # Set credentials
            self.__global_config.__setattr__("credentials", credentials)

            # Init reports
            self.__init_reports(self.campaign_report_path,
                                device_name, campaign_name, campaign_relative_path,
                                campaign_type, user_email, metacampaign_uuid)

            # Creates Test case Manager object
            self.__test_case_manager = TestCaseManager(self.__test_report,
                                                       live_reporting_interface=self._live_reporting_interface)

            # Setup Test Case Manager
            tcm_stop_execution = self.__test_case_manager.setup(self.__global_config,
                                                                self.__debug_report,
                                                                self.__test_case_conf_list[0].do_device_connection)
            status = tcm_stop_execution
        else:
            status = AcsBaseException.NO_TEST

        return status

    def _send_create_testcase_info(self, execution_request_nb):
        """
            This function aims at creating all test cases reporting data
            at beginning of campaign so that max information is available
            as soon as possible
        :param execution_request_nb: nb of times to execute the campaign
        :type execution_request_nb: integer
        """
        tc_order = 1
        for execution_iteration in range(execution_request_nb):
            for tc_index, tc_conf in enumerate(self.__test_case_conf_list):
                uc_name = tc_conf.get_ucase_name()
                tc_name = tc_conf.get_name()
                tc_phase = tc_conf.get_phase()
                tc_type = tc_conf.get_type()
                tc_domain = tc_conf.get_domain()
                is_warning = tc_conf.get_is_warning()
                tc_parameters = tc_conf.get_params().get_params_as_dict()
                self._live_reporting_interface.send_create_tc_info(tc_name,
                                                                   uc_name,
                                                                   tc_phase,
                                                                   tc_type,
                                                                   tc_domain,
                                                                   tc_order,
                                                                   is_warning,
                                                                   tc_parameters)

                tc_order += 1
            # Only MAX_TC_NB_AUTHORIZED will be scheduled and executed by ACS
                if tc_order > MAX_TC_NB_AUTHORIZED:
                    break
            else:
                continue
            break

    def execute(self, is_arg_checking=True, **kwargs):
        """
            This function is the entry point of ACS solution when called by Test Runner.
            It parses the arguments given to CampaignEngine,
            parses XML files associated & read the campaign content
            for the TestCaseManager to execute.

            :param is_arg_checking: Whether or not ACS arguments are checked
            :type is_arg_checking: bool

            :param kwargs: ACS arguments
            :type kwargs: dict

        """

        error = None
        global_results = Util.ACSResult(verdict=Util.ExitCode.FAILURE)
        execution_iteration = 1
        # Index of test case inside  loop on campaign
        tc_order = 1
        stop_execution = False
        verdicts = {}
        acs_outcome_verdicts = {}
        acs_outcome_status = False
        self.__campaign_metrics.campaign_start_datetime = datetime.now()

        try:

            arg_checker = ArgChecker(**kwargs)

            if is_arg_checking:
                error = arg_checker.check_args(False)
                if error:
                    raise AcsBaseException("INVALID_PARAMETER", error)

            params = arg_checker.args

            campaign_name = params["campaign_name"]
            params["campaign_relative_path"] = os.path.dirname(campaign_name)
            execution_request_nb = params["execution_request_nb"]
            random_mode = params["random_mode"]
            device_parameters = params["device_parameter_list"]
            Paths.FLASH_FILES = params["flash_file_path"]

            # Log acs param
            self.__log_acs_param(params)

            # Check if device parameters is a list
            if not isinstance(device_parameters, list):
                device_parameters = []

            # Set test campaign status : campaign is in setup phase
            global_results.status = Util.Status.INIT
            setup_status = self._setup(**params)
            # setup successfully completed
            if setup_status is None:
                total_tc_to_execute = execution_request_nb * len(self.__test_case_conf_list)
                if total_tc_to_execute > MAX_TC_NB_AUTHORIZED:
                    self.__logger.warning("Total number of TCs ({0}) exceeds maximum number authorized ({1})."
                                          .format(total_tc_to_execute, MAX_TC_NB_AUTHORIZED))
                    self.__logger.warning("Only first {0} TCs will be executed".format(MAX_TC_NB_AUTHORIZED))
                    total_tc_to_execute = MAX_TC_NB_AUTHORIZED

                self.__campaign_metrics.total_tc_count = total_tc_to_execute
                # Send live report if enabled
                self._send_create_testcase_info(execution_request_nb)
                # Log extra acs param for metrics
                self._log_acs_param_extra(params)

                # Execute test cases of campaign
                # Set test campaign status : campaign is starting
                global_results.status = Util.Status.ONGOING
                while execution_iteration <= execution_request_nb and not stop_execution:
                    stop_execution, tc_order = self._execute_test_cases(verdicts, tc_order, acs_outcome_verdicts)
                    execution_iteration += 1
                    if random_mode:
                        self.__test_case_conf_list = self.__randomize_test_cases(self.__test_case_conf_list)
                    if tc_order > MAX_TC_NB_AUTHORIZED:
                        break
                if not stop_execution:
                    LOGGER_FWK_STATS.info("event=STOP_ON_EOC")
                    # Set test campaign status : campaign is completed
                    global_results.status = Util.Status.COMPLETED
                else:
                    # Set test campaign status : campaign has been interrupted during test suite execution
                    global_results.status = Util.Status.ABORTED
            # Exception occurred during setup
            else:
                self.__log_stop_campaign(setup_status)
                # Set test campaign status
                global_results.status = Util.Status.ABORTED

            (status, acs_outcome_status) = self._all_tests_succeed(verdicts, acs_outcome_verdicts)
            if status:
                global_results.verdict = Util.ExitCode.SUCCESS
        except (KeyboardInterrupt):
            LOGGER_FWK_STATS.info("event=STOP_ON_USER_INTERRUPT")
            self.__log_stop_campaign("USER INTERRUPTION")
            # Set test campaign status
            global_results.status = Util.Status.ABORTED
        except (SystemExit):
            LOGGER_FWK_STATS.info("event=STOP_ON_SYSTEM INTERRUPT")
            self.__log_stop_campaign("SYSTEM INTERRUPTION")
            # Set test campaign status
            global_results.status = Util.Status.ABORTED
        except Exception as exception:
            if isinstance(exception, AcsBaseException):
                error = str(exception)
                LOGGER_FWK_STATS.info("event=STOP_ON_EXCEPTION; error={0}".format(error))
                if self.__logger is not None:
                    self.__logger.error(error)
                else:
                    print(error)
            else:
                ex_code, ex_msg, ex_tb = Util.get_exception_info(exception)
                LOGGER_FWK_STATS.info("event=STOP_ON_EXCEPTION; error={0}".format(ex_msg))
                if self.__logger is not None:
                    self.__logger.error(ex_msg)
                    self.__logger.debug("Traceback: {0}".format(ex_tb))
                    self.__logger.debug("return code is {0}".format(ex_code))
                else:
                    print (ex_msg)
                    print ("Traceback: {0}".format(ex_tb))
                    print ("return code is {0}".format(ex_code))

            # add an explicit message in the last executed TC's comment
            if self.__test_report is not None:
                self.__test_report.add_comment(tc_order, str(exception))
                self.__test_report.add_comment(tc_order,
                                               ("Fatal exception : Test Campaign will be stopped. "
                                                "See log file for more information."))
            # Set test campaign status
            global_results.status = Util.Status.ABORTED
        finally:
            # Sending Campaign Stop info to remote server (for Live Reporting control)
            self._live_reporting_interface.send_stop_campaign_info(verdict=global_results.verdict,
                                                                   status=global_results.status)

            if self.__test_case_manager is not None:
                campaign_error = bool(global_results.verdict)
                try:
                    cleanup_status, global_results.dut_state = self.__test_case_manager.cleanup(campaign_error)
                except AcsBaseException as e:
                    cleanup_status = False
                    global_results.dut_state = Util.DeviceState.UNKNOWN
                    error = str(e)
                if self.__logger is not None:
                    if error:
                        self.__logger.error(error)
                    self.__logger.info("FINAL DEVICE STATE : %s" % (global_results.dut_state,))
                else:
                    if error:
                        print error
                    print ("FINAL DEVICE STATE : %s" % (global_results.dut_state,))
            else:
                cleanup_status = True

            if not cleanup_status:
                global_results.verdict = Util.ExitCode.FAILURE

            for verdict in verdicts:
                if not Util.Verdict.is_pass(verdicts[verdict]):
                    tc_name = str(verdict).split(self.VERDICT_SEPARATOR)[0]
                    tc_verdict = verdicts[verdict]
                    msg = "ISSUE: %s=%s\n" % (tc_name, tc_verdict)
                    sys.stderr.write(msg)

            # Wait for last LiveReporting action requests
            self._live_reporting_interface.wait_for_finish()

            if self.__test_report:
                # write  data in report files
                self.__write_report_info()

                # update the metacampaign result id in xml report file
                # this action is done at the end because the connection retry with live reporting server will done
                # throughout campaign execution
                self.__test_report.write_metacampaign_result_id(self._live_reporting_interface.campaign_id)

            if self.campaign_report_path is not None:
                # Archive test campaign XML report
                self.__logger.info("Archive test campaign report...")
                # Compute checksum
                _, archive_file = zip_folder(self.campaign_report_path, self.campaign_report_path)
                self._live_reporting_interface.send_campaign_resource(archive_file)

            # Display campaign metrics information to the user
            self._display_campaign_metrics(self.__campaign_metrics)

            # Close logger
            ACSLogging.close()

            if acs_outcome_status and cleanup_status:
                global_results.verdict = Util.ExitCode.SUCCESS
            else:
                global_results.verdict = Util.ExitCode.FAILURE

        return global_results

    def campaign_metrics(self):
        """
            Provide Campaign metrics
        :return: CampaignMetrics
        """
        return self.__campaign_metrics

    def _execute_test_cases(self, verdicts, tc_order, acs_outcome_verdicts):
        """
            Execute test cases of current campaign and update verdicts for current campaign iteration
        :param verdicts: dictionnary of verdicts of all campaign iterations
        :param tc_order: index of the test in the whole campaign iterations
        :param acs_outcome_verdicts: dictionnary of verdicts which take in account if TC is_warning
        :return: stop_execution, tc_order
        """
        # Flag to stop camapaign
        stop_execution = False
        # Index in current campaign execution
        tc_index = 0
        # Verdict of the current test case being executed
        verdict = None
        # Current TestCaseConf object
        tcase_conf = None
        # Run all Test Cases
        while tc_index < len(self.__test_case_conf_list):
            tcase_conf = self.__test_case_conf_list[tc_index]
            if tcase_conf is not None:
                # Logging test name and number to log info level
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "")
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Starting test: {0}: test number {1} of {2}".format(
                    tcase_conf.get_name(), tc_order, self.__campaign_metrics.total_tc_count))
                # Get test case object using its configuration file & use case catalog
                self.__update_report_info(tcase_conf, "FAILURE")
                # get test case class name
                tcase_class = tcase_conf.get_ucase_class()
                verdict = None
                if tcase_class is not None and tc_index > 0:
                    # Check if power cycle is required only if the test case class is instantiate
                    # Power cycle is not needed at first test case execution,
                    # as the device is already ready for the execution
                    # power cycle should not be done on few cases
                    if tcase_conf.do_device_connection:
                        status_power_cycle, status_power_cycle_msg = self.__test_case_manager.power_cycle_device()
                        if not status_power_cycle:
                            self.__logger.debug(status_power_cycle_msg)
                            self.__log_stop_campaign(DeviceException.DUT_BOOT_ERROR, tc_order)
                            stop_execution = True
                            break
                tc_msgs = tcase_conf.get_messages()
                if tc_msgs:
                    self.__test_report.add_comment(tc_order, "\n".join(tc_msgs))
                if tcase_conf.get_params().get_b2b_iteration() > 0:
                    if tcase_conf.get_valid():
                        # Execute test case
                        (verdict, tcm_status, warning_verdict) = self.__test_case_manager.execute(
                            tcase_class, tcase_conf, tc_order)
                        self.__campaign_metrics.tc_executed_count += 1
                        str_tcase_key = tcase_conf.get_name() + self.VERDICT_SEPARATOR + str(tc_order)
                        verdicts[str_tcase_key] = verdict
                        acs_outcome_verdicts[str_tcase_key] = warning_verdict
                        if verdict == Util.Verdict.PASS:
                            self.__campaign_metrics.pass_verdict_count += 1
                        elif verdict == Util.Verdict.FAIL:
                            self.__campaign_metrics.fail_verdict_count += 1
                        elif verdict == Util.Verdict.BLOCKED:
                            self.__campaign_metrics.blocked_verdict_count += 1
                        elif verdict == Util.Verdict.VALID:
                            self.__campaign_metrics.valid_verdict_count += 1
                        elif verdict == Util.Verdict.INVALID:
                            self.__campaign_metrics.invalid_verdict_count += 1
                        elif verdict == Util.Verdict.INCONCLUSIVE:
                            self.__campaign_metrics.inconclusive_verdict_count += 1
                        # Fill test report with statistics
                        self.__test_report.update_statistics_node()
                        # Display campaign metrics in txt format
                        self.__campaign_metrics.get_metrics()
                        # Check if test have been interrupted

                        if tcm_status is not None:
                            self.__log_stop_campaign(tcm_status, tc_order)
                            stop_execution = True
                            break
                        elif self.__stop_on_critical_failure and self.__test_case_manager.test_failed_on_critical:
                            # Perform a last power cycle to retrieve device logs
                            self.__test_case_manager.handle_critical_failure()
                            self.__log_stop_campaign("CRITICAL FAILURE", tc_order)
                            stop_execution = True
                            break
                        # If stopCampaignOnFirstFailure set to True and verdict is not PASS, aborting Campaign.
                        # If only one UC scheduled, not necessary to handle error as is.
                        elif (len(self.__test_case_conf_list) > 1
                              and Util.Verdict.is_pass(verdict)  # noqa
                              and self.__stop_on_first_failure):  # noqa
                            self.__log_stop_campaign(
                                "FIRST FAILURE (after %s use cases)" % str(len(verdicts)), tc_order)
                            stop_execution = True
                            break
                    else:
                        self.__logger.warning("Test case is invalid, it will not be executed")
                else:
                    warning_msg = "Test case has back to back iteration parameter is invalid (%s) , it will not be " \
                        "executed!" % (tcase_conf.get_name())
                    self.__test_report.add_comment(tc_order, warning_msg)
                    self.__logger.warning(warning_msg)
                    # send back test case result
            self.__update_report_info(tcase_conf, verdict)
            tc_index += 1
            tc_order += 1
            if tc_order > MAX_TC_NB_AUTHORIZED:
                break
            # ------------------------------ end of cases loop, campaign is finished ----------------------------

        # Trying to update report info with last executed test case if campaign execution is stopped
        if stop_execution:
            self.__update_report_info(tcase_conf, verdict)

        return stop_execution, tc_order

    def _all_tests_succeed(self, verdicts, verdicts_warning):
        """
            Tells from a verdict dictionnary it test all succeed
        :param verdicts: dictionnary
        :param verdicts_warning: dictionnary
        :return: bool
        """
        status = True
        status_acs_outcome = True
        # Check that all test cases are executed
        if not verdicts and not verdicts_warning:
            status = False
            status_acs_outcome = False
        elif (self.__campaign_metrics.total_tc_count > len(verdicts)
              and self.__campaign_metrics.total_tc_count > len(verdicts_warning)):  # noqa
            status = False
            status_acs_outcome = False
        else:
            # Check that all test cases are passed
            for tc_verdict in verdicts.values():
                if not Util.Verdict.is_pass(tc_verdict):
                    status = False
            # Check that all test cases are passed
            for tc_verdict in verdicts_warning.values():
                if not Util.Verdict.is_pass(tc_verdict):
                    status_acs_outcome = False
        return status, status_acs_outcome

    def __write_report_info(self):
        """
        Writes the updated information of the device into the Test Report

        - SwRelease
        - DeviceId
        - Imei
        - ModelNumber
        - FwVersion
        - BasebandVersion
        - KernelVersion
        - AcsAgentVersion
        - Device Properties file

        :rtype: None
        """
        try:
            # Retrieve all device properties
            prop_list = DeviceManager().get_device_properties(Util.AcsConstants.DEFAULT_DEVICE_NAME)

            # Create device info report files
            self.__test_report.build_deviceinfo_file(prop_list)

            # Update DeviceInfo node in campaign result file
            device_properties = self.__test_case_manager.get_device_instance().get_device_info()
            self.__test_report.update_device_info_node(device_properties)

            # Update FlashInfo node in campaign result file
            flash_device_properties = self.__test_case_manager.get_device_instance().flash_device_properties
            self.__test_report.update_flash_info_node(flash_device_properties)

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception as e:  # pylint: disable=W0703
            self.__logger.warning("Error occured when writing report info ! (%s)" % str(e))

    def __update_report_info(self, tcase, verdict):
        """
        Updates Report Info according to some UC and Verdict

        :type tc_name: TC object
        :param tc_name: TC object where information will be retrieve

        :type verdict: str
        :param verdict: Should be PASS | FAIL for most of cases
        """
        try:
            uc_name = tcase.get_ucase_name()

            # If SETUP_EMBEDDED and PASS, update ACS Agent Version on Test Report
            if uc_name == "LAB_SYSTEM_SETUP_EMBEDDED" and verdict == "PASS":
                # Update ACS Agent Version
                self.__logger.info("%s Test Case %s, updating AcsAgentVersion in Test Report ..."
                                   % (tcase.get_name(), str(verdict)))
                # Force retrieval of ACS Agent Version
                self.__test_case_manager.get_device_instance().retrieve_device_info()

            if self.__test_report:
                self.__write_report_info()

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception as e:  # pylint: disable=W0703
            self.__logger.warning("Error occured when updating report info ! (%s)" % str(e))

    def _display_campaign_metrics(self, campaign_metrics):
        """
        Displays Campaign metrics information to Info log level

        :type campaign_metrics: CampaignMetrics
        :param campaign_metrics: campaign metrics from where to get the information

        :return: None
        """
        if self.__logger is not None:
            self.__logger.log(ACSLogging.MINIMAL_LEVEL, "---EXECUTION METRICS---")
            self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Tests Number = {0}".format(campaign_metrics.total_tc_count))
            if campaign_metrics.pass_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Passed       = {0}".format(
                    campaign_metrics.pass_verdict_count))
            if campaign_metrics.fail_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Failed       = {0}".format(
                    campaign_metrics.fail_verdict_count))
            if campaign_metrics.blocked_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Blocked      = {0}".format(
                    campaign_metrics.blocked_verdict_count))
            if campaign_metrics.valid_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Valid        = {0}".format(
                    campaign_metrics.valid_verdict_count))
            if campaign_metrics.invalid_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Invalid      = {0}".format(
                    campaign_metrics.invalid_verdict_count))
            if campaign_metrics.inconclusive_verdict_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Inconclusive = {0}".format(
                    campaign_metrics.inconclusive_verdict_count))
            if campaign_metrics.tc_not_executed_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Not Executed = {0}".format(
                    campaign_metrics.tc_not_executed_count))
            if campaign_metrics.total_boot_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "DUT Boot(s)  = {0}".format(
                    int(campaign_metrics.total_boot_count)))
            if campaign_metrics.unexpected_reboot_count:
                self.__logger.log(ACSLogging.MINIMAL_LEVEL, "DUT Unexpected Reboots = {0}".format(
                    int(campaign_metrics.unexpected_reboot_count)))

            time_delta = datetime.now() - campaign_metrics.campaign_start_datetime
            if hasattr(time_delta, "total_seconds"):
                campaign_duration = time_delta.total_seconds()
            else:
                campaign_duration = (
                    (time_delta.microseconds + (time_delta.seconds + time_delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6)
            run_time = "%.2d:%.2d:%.2d" % (campaign_duration // 3600,
                                           (campaign_duration // 60) % 60,
                                           campaign_duration % 60)
            self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Exec Time    = {0}".format(run_time))

            self.__logger.log(ACSLogging.MINIMAL_LEVEL, "Local Report = {0}".format(
                self._get_campaign_report_filename_path()))

        event_msg = ["event=STOP",
                     "test_number={0}".format(campaign_metrics.total_tc_count),
                     "test_passed={0}".format(campaign_metrics.pass_verdict_count),
                     "test_failed={0}".format(campaign_metrics.fail_verdict_count),
                     "test_blocked={0}".format(campaign_metrics.blocked_verdict_count),
                     "test_valid={0}".format(campaign_metrics.valid_verdict_count),
                     "test_invalid={0}".format(campaign_metrics.invalid_verdict_count),
                     "test_inconclusive={0}".format(campaign_metrics.inconclusive_verdict_count),
                     "test_na={0}".format(campaign_metrics.tc_not_executed_count),
                     "test_time={0}".format(run_time)]
        LOGGER_FWK_STATS.info(";".join(event_msg))
