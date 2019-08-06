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

import time
import os
from lxml import etree

from acs.Core.CatalogParser.TestStepCatalogParser import TestStepCatalogParser
from acs.Core.TestStep.TestStepConstants import TestStepConstants
from acs.Core.TestStep.TestStepContext import TestStepContext
from acs.Core.TestStep.TestStepSet import TestStepSet
from acs.Core.TestStep.ParallelTestStepSet import ParallelTestStepSet
from acs.Core.TestStep.LoopTestStepSet import LoopTestStepSet
from acs.Core.TestStep.IfTestStepSet import IfTestStepSet
from acs.Core.TestStep.TestStepReport import TestStepReport
from acs.Core.TestBase import TestBase
from acs.UtilitiesFWK.Utilities import str_to_bool_ex, get_class, Global, Verdict, error_to_verdict
from acs.ErrorHandling.AcsBaseException import AcsBaseException
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.Core.Factory import Factory
from acs.Core.Report.ACSLogging import LOGGER_FWK_STATS


class TestStepEngine(TestBase):

    """
    Implements the Test Step Engine which is seen from ACS as a normal use case.

    It is the engine which will:

    * parse XML file containing the test step declaration
    * instantiate all the test steps and execute them
    * add test steps result in ACS reports

    .. uml::

        class TestBase {
            test_ok = False
            tc_order = 0
            initialize()
            set_up()
            run_test()
            tear_down()
            finalize()
        }

        class TestStepEngine {
            context
            initialize()
            set_up()
            run_test()
            tear_down()
            finalize()
        }

        TestBase <|- TestStepEngine
    """

    def __init__(self, tc_conf, global_config):
        """
        Called by ACS framework to create an instance of TestStepEngine.
        """
        TestBase.__init__(self, tc_conf, global_config)

        # if TEST_STEP_ENGINE_ENTRY is None or empty by default the use the current test case name
        tse_entry = self._tc_parameters.get_param_value(TestStepConstants.STR_PAR_TSE_ENTRY, self.get_name() + ".xml")

        # Get the Test Case XML file name
        self._testcase_file_name = os.path.normpath(os.path.join(self._execution_config_path, tse_entry))

        # Create an empty context, it will be passed over to the test steps
        self._context = TestStepContext()

        # Member variables to be used later
        self._xml_etree = None

        # dictionary containing test steps read from TestStep catalogs
        self._teststep_catalog_parser = TestStepCatalogParser()
        self._teststep_dictionary = {}

        # Skip tear_down & finalize steps if config error occurs
        self.__config_error = False

        # Initialize test case verdict
        self._error.Code = Global.SUCCESS
        self._error.Msg = ""

        # Create test step report
        self._teststep_report = TestStepReport(
            global_config.campaignConfig["campaignReportTree"].get_report_path())

        # Create the factory, used by test steps to request ACS objects (such as DeviceManager, for example)
        self._factory = Factory()

    def initialize(self):
        """
        Process the **<Initialize>** section of the XML file and execute defined test steps.
        """
        TestBase.initialize(self)
        # Check that given xml file exists
        self.__check_file_exists(self._testcase_file_name)

        # Load and parse the XML file
        # Done here as it could potentially raise exception
        self._xml_etree = self.__parse_xml_file(self._testcase_file_name)

        # Collects test steps from Acs TestStep Catalog and put them in a dictionary
        try:
            self._teststep_dictionary = self._teststep_catalog_parser.parse_catalog_folder()
        except AcsConfigException:
            self.__config_error = True
            raise

        # Process <Include> tags to include external files.
        test_steps_root = self._xml_etree.xpath(TestStepConstants.STR_PATH_ROOT)
        if test_steps_root:
            # Extract STR_PATH_INCLUDE tag from first found tag STR_PATH_ROOT
            # In a test case we shall have only one STR_PATH_ROOT, that is why we take the first element
            self._process_include_tag(TestStepConstants.STR_PATH_INCLUDE, test_steps_root[0])

        # Process TestStep parameters regarding definition from Parameters catalog
        self._process_test_step_parameters()

        # Store the test step catalog in the global configuration
        self._global_conf.__dict__["teststepCatalog"] = self._teststep_dictionary

        # Executes the test steps in the "Initialize" session
        # These steps are optional
        test_steps_execution_time = self._run_test_steps(
            "/".join([TestStepConstants.STR_PATH_ROOT, TestStepConstants.STR_PATH_INIT]), optional_step=True)

        if test_steps_execution_time:
            self._logger.info("Initialize execution time: %.2f secs" % (test_steps_execution_time,))

        return self._error.Code, self._error.Msg

    def set_up(self):
        """
        Process the **<Setup>** section of the XML file and execute defined test steps.
        """
        TestBase.set_up(self)
        # Executes the test steps in the "SetUp" session
        test_steps_execution_time = self._run_test_steps(
            "/".join([TestStepConstants.STR_PATH_ROOT, TestStepConstants.STR_PATH_SETUP]))

        if test_steps_execution_time:
            self._logger.info("Setup execution time: %.2f secs" % (test_steps_execution_time,))

        return self._error.Code, self._error.Msg

    def run_test(self):
        """
        Process the **<RunTest>** section of the XML file and execute defined test steps.
        """
        TestBase.run_test(self)

        # Executes the test steps in the "Run" section
        test_steps_execution_time = self._run_test_steps(
            "/".join([TestStepConstants.STR_PATH_ROOT, TestStepConstants.STR_PATH_RUN]))

        if test_steps_execution_time:
            self._logger.info("RunTest execution time: %.2f secs" % (test_steps_execution_time,))

        return self._error.Code, self._error.Msg

    def tear_down(self):
        """
        Process the **<TearDown>** section of the XML file and execute defined test steps.
        """
        TestBase.tear_down(self)

        if not self.__config_error:
            # Executes the test steps in the "TearDown" section
            test_steps_execution_time = self._run_test_steps(
                "/".join([TestStepConstants.STR_PATH_ROOT, TestStepConstants.STR_PATH_TEARDOWN]))
            if test_steps_execution_time:
                self._logger.info("TearDown execution time: %.2f secs" % (test_steps_execution_time,))

        return self._error.Code, self._error.Msg

    def finalize(self):
        """
        Clear all remaining objects created by the test.
        Process the **<Finalize>** section of the XML file and execute defined test steps.
        """
        TestBase.finalize(self)
        # Executes the test steps in the "Finalize" section if no previous error
        if not self.__config_error:
            test_steps_execution_time = self._run_test_steps(
                "/".join([TestStepConstants.STR_PATH_ROOT, TestStepConstants.STR_PATH_FINALIZE]), optional_step=True)
            if test_steps_execution_time:
                self._logger.info("Finalize execution time: %.2f secs" % (test_steps_execution_time,))

        return self._error.Code, self._error.Msg

    def _run_test_steps(self, path, optional_step=False):
        """
        Runs test steps created from the XML path identifying a "section" (Setup/RunTest/TearDown)

        :type path: str
        :param path: is the current XML path the fork tag is in

        :type optional_step: bool
        :param optional_step: is it optional steps

        :type path: str
        :param path: the XML Path identifying the section to process
        """

        def update_ts_report(ts_name, ts_verdict, ts_verdict_msg):
            """
            Parse the test step verdict until we get the test step verdict message
            Add it in the test step report

            :type ts_name: str
            :param ts_name: Name the test step

            :type ts_verdict: Utilities.Verdict object
            :param ts_verdict: Verdict of the test step

            :type ts_verdict_msg: str/list
            :param ts_verdict_msg: specific message from test step
            """
            if isinstance(ts_verdict_msg, str):
                # Add test step result into the test step report
                self._teststep_report.add_result(
                    ts_name, ts_verdict, ts_verdict_msg, self.get_name(), self.tc_order)
            else:
                # In other case ts_verdict_msg will contain list of nested test steps with their verdict as follow
                # [('Run.Fork Test1.MultiSuspend.SUSPEND', <UtilitiesFWK.Utilities.Error object at 0x033018F0>),
                #  ('Run.Fork Test1.MultiSuspend.SUSPEND', <UtilitiesFWK.Utilities.Error object at 0x03301750>)]
                for sub_ts_name, sub_ts_verdict_msg in ts_verdict_msg:
                    # it cannot be BLOCKED or FAILURE, if so it would have been process in exception
                    sub_ts_verdict = error_to_verdict(Global.SUCCESS)
                    update_ts_report(sub_ts_name, sub_ts_verdict, sub_ts_verdict_msg)

        # Kick off the process of test steps creation
        steps = self._create_test_steps_list(path, extra_pars=None, ts_name=os.path.basename(path),
                                             optional_nodes=optional_step)

        # Set start time
        run_start = time.time()

        # Execute each of the test steps
        if not steps:
            # Reset error if not test steps to execute
            self._error.Code = Global.SUCCESS
            self._error.Msg = ""
            pass
        else:
            for step in steps:
                step_name = step.name
                try:
                    step.run(self._context)
                    step_result = Global.SUCCESS
                    update_ts_report(step_name, error_to_verdict(step_result), step.ts_verdict_msg)
                    self._error.Code = step_result

                except (KeyboardInterrupt, SystemExit):
                    # In case of user interruption add it in the test step report then re-raise the exception
                    self._teststep_report.add_result(
                        step_name, Verdict.BLOCKED, AcsBaseException.USER_INTERRUPTION, self.get_name(), self.tc_order)
                    raise

                except Exception as test_step_error:
                    # Retrieve error code in case of Acs exception
                    if isinstance(test_step_error, AcsBaseException):
                        self._error.Code = test_step_error.get_error_code()
                        error_msg = test_step_error.get_error_message()
                    # In other case error is blocked
                    else:
                        self._error.Code = Global.BLOCKED
                        error_msg = "Unexpected error: {0}".format(repr(test_step_error))

                    # Add verdict of the test step before stopping execution
                    self._teststep_report.add_result(
                        step_name, self._error.Verdict, error_msg, self.get_name(), self.tc_order)
                    raise

                finally:
                    if self._error.Code != Global.SUCCESS:
                        # Add the test step name into the TC final verdict message
                        if isinstance(self._error.Msg, list):
                            self._error.Msg.append(step_name)
                        else:
                            # Add error message as a list to be well formatted in Web Report
                            self._error.Msg = ["Error occurred on following test step(s):", step_name]

                # If test step verdict is not Successfull and not an exception goes out of the loop
                if self._error.Code != Global.SUCCESS:
                    break

        # Return the execution time
        return time.time() - run_start

    def _create_test_steps_list(self, path, extra_pars=None, ts_name=None, optional_nodes=False):
        """
        Creates a list of test steps from the XML path.

        It implements a cascade mechanism to make nested items inherit parameters.

        Therefore this method can be recursively called and get passed outer parameters

        :type path: str
        :param path: is the current XML path the fork tag is in

        :type extra_pars: dict
        :param extra_pars: "inherited" parameters

        :type ts_name: str
        :param ts_name: the test step's parent name

        :type optional_nodes: bool
        :param optional_nodes: raise error if nodes are missing

        :rtype: list
        :return: list of test steps
        """

        # The initial empty list of test steps to be executed.
        # A test step is a TestStepBase hierarchy class (such as TestStep, TestStepSet,
        # ParallelTestSet, etc...
        test_steps = []

        # Finds the node given its path (using XPATH syntax)
        node = self._xml_etree.xpath(path)
        if node:
            # Here we get the first element, as the given 'path' MUST be unique in the test case file
            # i.e : TestCase/TestSteps/SetUp shall be unique in the TC file
            for step in node[0]:
                # Skip children that aren't actual Elements (e.g. text)
                if not isinstance(step.tag, basestring):
                    continue

                # Create an empty parameters dictionary to fill in with
                # use case / test step parameters
                pars = {}

                # If extra pars come from outside, add them first
                if isinstance(extra_pars, dict):
                    pars.update(extra_pars)

                # Then process the attributes of the current test step
                pars.update(step.attrib)

                if step.tag == TestStepConstants.STR_PATH_TEST_STEP:
                    self._process_test_step_tag(test_steps, pars, ts_name)
                elif step.tag == TestStepConstants.STR_PATH_FORK:
                    self._process_fork_tag(path, test_steps, pars, ts_name)
                elif step.tag == TestStepConstants.STR_PATH_LOOP:
                    self._process_loop_tag(path, test_steps, pars, ts_name)
                elif step.tag == TestStepConstants.STR_PATH_IF:
                    self._process_if_tag(path, test_steps, pars, ts_name)
        elif not optional_nodes:
            error_msg = "'%s' XPATH query didn't find any node " % path
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

        return test_steps

    def _process_fork_tag(self, path, test_steps, pars, ts_name=None):
        """
        Process **<Fork>** tag, to create parallel test steps.

        :type path: str
        :param path: is the current XML path the fork tag is in

        :type test_steps: list
        :param test_steps:  list of test steps

        :type pars: dict
        :param pars: the test step's parameters

        :type ts_name: str
        :param ts_name: the test step's parent name
        """

        fork_id = pars[TestStepConstants.STR_FORK_ID]
        new_path = "%s/%s[@Id='%s']" % (path, TestStepConstants.STR_PATH_FORK, fork_id)
        # Before passing the current attributes (in pars) remove
        # ForkId (just to avoid confusion)
        pars.pop(TestStepConstants.STR_FORK_ID, None)

        # Create test steps
        ts_name = "{0}.{1}".format(ts_name, fork_id) if ts_name else fork_id
        fork_steps = self._create_test_steps_list(new_path, pars, ts_name)

        # If STR_SERIALIZE is specified <Fork> behaves like a <TestStepSet>
        # Useful to switch parallel / serial just changing the attribute
        if (TestStepConstants.STR_SERIALIZE not in pars.keys()
                or not str_to_bool_ex(pars[TestStepConstants.STR_SERIALIZE])):
            fork_set = ParallelTestStepSet(self._conf, self._global_conf, pars, self._factory)
        else:
            fork_set = TestStepSet(self._conf, self._global_conf, pars, self._factory)

        fork_set.name = ts_name
        fork_set.add_steps(fork_steps)
        # Add the test step set to the test step list
        test_steps.append(fork_set)

    def _process_loop_tag(self, path, test_steps, pars, ts_name=None):
        """
        Process **<Loop>** tag, to create a loop on test steps.

        :type path: str
        :param path: is the current XML path the loop tag is in

        :type test_steps: list
        :param test_steps:  list of test steps

        :type pars: dict
        :param pars: the test step's parameters

        :type ts_name: str
        :param ts_name: the test step's parent name
        """

        loop_id = pars[TestStepConstants.STR_LOOP_ID]
        new_path = "{0}/{1}[@Id='{2}']".format(path, TestStepConstants.STR_PATH_LOOP, loop_id)

        # Before passing to child Test Step the current attributes (in extra_pars)
        # remove Loop specific attributes (Id and Nb of iterations)
        extra_pars = pars.copy()
        extra_pars.pop(TestStepConstants.STR_LOOP_ID)
        extra_pars.pop(TestStepConstants.STR_LOOP_NB_ITERATION)

        # Create test steps
        ts_name = "{0}.{1}".format(ts_name, loop_id) if ts_name else loop_id
        loop_steps = self._create_test_steps_list(new_path, extra_pars, ts_name)

        loop_set = LoopTestStepSet(self._conf, self._global_conf, pars, self._factory)

        loop_set.name = ts_name
        loop_set.add_steps(loop_steps)
        # Add the test step set to the test step list
        test_steps.append(loop_set)

    def _process_if_tag(self, path, test_steps, pars, ts_name=None):
        """
        Process **<If>** tag, to create a if on test steps.

        :type path: str
        :param path: is the current XML path the if tag is in

        :type test_steps: list
        :param test_steps:  list of test steps

        :type pars: dict
        :param pars: the test step's parameters

        :type ts_name: str
        :param ts_name: the test step's parent name
        """

        if_id = pars[TestStepConstants.STR_IF_ID]
        new_path = "{0}/{1}[@Id='{2}']".format(path, TestStepConstants.STR_PATH_IF, if_id)

        # Before passing to child Test Step the current attributes (in extra_pars)
        # remove If specific attributes (Id and Nb of iterations)
        extra_pars = pars.copy()
        extra_pars.pop(TestStepConstants.STR_IF_ID)
        extra_pars.pop(TestStepConstants.STR_IF_CONDITION)

        # Create test steps
        ts_name = "{0}.{1}".format(ts_name, if_id) if ts_name else if_id
        if_steps = self._create_test_steps_list(new_path, extra_pars, ts_name)

        if_set = IfTestStepSet(self._conf, self._global_conf, pars, self._factory)

        if_set.name = ts_name
        if_set.add_steps(if_steps)
        # Add the test step set to the test step list
        test_steps.append(if_set)

    def _process_test_step_tag(self, test_steps, pars, ts_name=None):
        """
        Process **<TestStep>** tag, to create test steps.

        :type test_steps: list
        :param test_steps: list of test steps

        :type pars: dict
        :param pars: test step's parameters

        :type ts_name: str
        :param ts_name: test step's parent name
        """
        if TestStepConstants.STR_TS_ID in pars.keys():
            test_step = self._create_test_step_instance(pars, ts_name)
        elif TestStepConstants.STR_SET_ID in pars.keys():
            test_step = self._create_test_step_set_instance(pars, ts_name)
        else:
            error_msg = "Either %s or %s <TestStep> attribute " \
                        " is mandatory " % (TestStepConstants.STR_TS_ID, TestStepConstants.STR_SET_ID)
            self._logger.error(error_msg)
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

        # Everything went fine, add the step to test step list
        test_steps.append(test_step)

    def _create_test_step_set_instance(self, pars, ts_name=None):
        """
        Create test step set instance

        :type pars: dict
        :param pars: the test step's parameters

        :type ts_name: str
        :param ts_name: the test step's parent name

        :rtype: :py:class:`~acs.Core.TestStep.TestStepSet`
        :return: the new instance of the test step set.
        """

        # It's probably a test step macro. check it
        macro_id = pars[TestStepConstants.STR_SET_ID]
        if macro_id is not None:
            new_path = "%s/%s[@Id='%s']" % (TestStepConstants.STR_PATH_ROOT,
                                            TestStepConstants.STR_PATH_TEST_STEP_SET,
                                            macro_id)
            # Before passing the current attributes (in pars) remove
            # MacroId (just to avoid confusion)
            pars.pop(TestStepConstants.STR_SET_ID, None)
            ts_name = "{0}.{1}".format(ts_name, macro_id) if ts_name else macro_id
            macro_steps = self._create_test_steps_list(new_path, pars, ts_name)

            # Create a test step set and add the macro steps to it
            step_set = TestStepSet(self._conf, self._global_conf, None, self._factory)
            step_set.name = ts_name
            step_set.add_steps(macro_steps)
        else:
            error_msg = "%s is None " % TestStepConstants.STR_SET_ID
            raise AcsConfigException(AcsConfigException.OPERATION_FAILED, error_msg)

        return step_set

    def _create_test_step_instance(self, pars, ts_name=None):
        """
        Create test step instance given its class name

        :type pars: dict
        :param pars: the test step's parameters

        :type ts_name: str
        :param ts_name: the test step's parent name

        :rtype: :py:class:`~acs.Core.TestStep.TestStepBase`
        :return: the new instance of the test step.
        """
        teststep_instance = None
        exception_code = None
        exception_msg = ""

        # Gets the test name and its class name
        teststep_name = pars.get(TestStepConstants.STR_TS_ID, "")
        if not teststep_name:
            raise AcsConfigException(AcsConfigException.INSTANTIATION_ERROR,
                                     "'Id' attribute is mandatory to identify the test step in the test step catalogs.")

        if teststep_name in self._teststep_dictionary:
            try:
                LOGGER_FWK_STATS.info("Create test_step={0}".format(teststep_name))
                cls_name = self._teststep_dictionary[teststep_name]["ClassName"]
                teststep_instance = get_class(cls_name)(self._conf, self._global_conf, pars, self._factory)
                teststep_instance.name = "{0}.{1}".format(ts_name, teststep_name) if ts_name else teststep_name
            except KeyError:
                exception_code = AcsConfigException.INVALID_PARAMETER
                exception_msg = "Unable to find class name of '{0}' test step.".format(teststep_name)
                exception_msg += " Check that the 'ClassName' of the test step, is not empty in the test step catalogs."
            except Exception as generic_exception:
                exception_code = AcsConfigException.INSTANTIATION_ERROR
                exception_msg = "Unable to instantiate '{0}' test step.".format(teststep_name)
                exception_msg += " Following error occurred : {0}".format(generic_exception)
            except AcsBaseException:
                raise

        else:
            exception_code = AcsConfigException.INVALID_PARAMETER
            exception_msg = \
                "Unable to find '{0}' test step in any test step catalogs (official or external).".format(teststep_name)
            exception_msg += " Check that it is declared in the test step catalogs"

        if teststep_instance:
            teststep_instance.call_by_engine()
        else:
            raise AcsConfigException(exception_code, exception_msg)

        return teststep_instance

    def _process_include_tag(self, path, node):
        """
        Include another XML file and add its nodes to node

        :type path: str
        :param path: the XML path

        :type node: Element
        :param node: the XML node to add the included information to
        """

        nodes = node.xpath(path)
        for elem in nodes:
            if TestStepConstants.STR_SRC in elem.attrib.keys():
                src = elem.attrib[TestStepConstants.STR_SRC]
                # Raise an exception in case file does not exists
                file_name = os.path.normpath(os.path.join(self._execution_config_path, src))
                self.__check_file_exists(file_name)

                # Parse the xml file to include
                to_include = self.__parse_xml_file(file_name)

                # User can add TestStep and/or TestStepSets in his include file
                teststeps_root_node = to_include.xpath("/" + TestStepConstants.STR_PATH_TEST_STEPS)
                if teststeps_root_node:
                    # TestSteps to include into the reference Test Step catalog
                    teststeps_to_include = self._teststep_catalog_parser.parse_catalog_file(file_name)

                    # Raise an exception if a test step is already defined
                    for teststep_name in teststeps_to_include.iterkeys():
                        if teststep_name in self._teststep_dictionary:
                            error_msg = "TestStep '%s' is defined more than one time !" % teststep_name
                            self.__config_error = True
                            raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR, error_msg)

                    self._teststep_dictionary.update(teststeps_to_include)

                # All the TestStepSet shall be defined in <TestStepSets/> node
                teststepsets_root_node = to_include.xpath("/" + TestStepConstants.STR_PATH_INCLUDE)
                if teststepsets_root_node:
                    # As xpath query has been done to get the root node of the xml file,
                    # we will have only one STR_PATH_INCLUDE tag. That is why we take the first element
                    for item in teststepsets_root_node[0]:
                        # Add all nodes to the root node which are not Comments
                        if isinstance(item.tag, basestring):
                            node.append(item)

    def __parse_xml_file(self, file_name):
        """
        Parse the xml file

        :type file_name: str
        :param file_name: File name to check

        :rtype: etree.ElementTree
        :return: parsed xml object

        :raise: AcsConfigException in case the file does not exists
        """
        try:
            parsed_xml_file = etree.parse(file_name)
            return parsed_xml_file
        except etree.XMLSyntaxError as xml_exception:
            error_msg = "Error occurred when parsing %s (%s)" % (file_name, str(xml_exception))
            self.__config_error = True
            raise AcsConfigException(AcsConfigException.XML_PARSING_ERROR, error_msg)

    def __check_file_exists(self, file_name):
        """
        Check that given file exists

        :type file_name: str
        :param file_name: File name to check

        :raise: AcsConfigException in case the file does not exists
        """
        if not os.path.isfile(file_name):
            error_msg = "%s file not found" % (file_name,)
            self.__config_error = True
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

    def _process_test_step_parameters(self):
        """
        Check and update parameters properties (PossibleValues, DefaultValue ...) regarding Parameters catalog
        """
        if self._teststep_dictionary:
            for teststep_name in self._teststep_dictionary.iterkeys():
                for ts_param in self._teststep_dictionary[teststep_name][TestStepConstants.STR_PARAMETERS].iterkeys():
                    # First check that the test step type refers to a known type defined in the Parameter catalog
                    ts_param_type = self._teststep_dictionary[teststep_name][TestStepConstants.STR_PARAMETERS][
                        ts_param].get(TestStepConstants.STR_PARAM_TYPE)
                    catalog_param_name = self._global_conf.parameterConfig.get(ts_param_type) if ts_param_type else None
                    if catalog_param_name:
                        # Update the TestStep type with the real type defined in the Parameter catalog
                        # i.e: If a TestStep has a type 'FLOAT', it will refer to a 'float' in the Parameter catalog
                        self._teststep_dictionary[teststep_name][TestStepConstants.STR_PARAMETERS][ts_param][
                            TestStepConstants.STR_PARAM_TYPE] = catalog_param_name.get(TestStepConstants.STR_PARAM_TYPE)
                    else:
                        raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                                 "TestStep parameter type '%s' is unknown !" % ts_param_type)

                    # Retrieve parameters properties
                    for param_property in [TestStepConstants.STR_PARAM_DEFAULT_VALUE,
                                           TestStepConstants.STR_PARAM_POSSIBLE_VALUES]:
                        ts_param_prop = self._teststep_dictionary[teststep_name][TestStepConstants.STR_PARAMETERS][
                            ts_param].get(param_property)

                        # In the catalog the properties are tuples to know if we can override the value or not
                        # i.e: 'DefaultValue': (True, '1.0')
                        override_param, catalog_param_prop = catalog_param_name.get(param_property)

                        if ts_param_prop is None or not override_param:
                            self._teststep_dictionary[teststep_name][TestStepConstants.STR_PARAMETERS][
                                ts_param][param_property] = catalog_param_prop

        else:
            self.__config_error = True
            self._logger.warning("TestStep dictionary referring to TestStep catalog is empty !")
