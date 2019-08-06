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

# flake8: noqa: W504
import os
from lxml import etree
from acs.Core.PathManager import Paths
from acs.Core.Report.ACSLogging import LOGGER_FWK
import acs.UtilitiesFWK.Utilities as Utils


ROOT_NODE = 'TestCase'
USECASE_NAME_NODE = "UseCase"
PHASE_NODE = "Phase"
TYPE_NODE = "Type"
DOMAIN_NODE = "Domain"

USECASE_CLASS_NAME_NODE = "ClassName"
B2B_ITERATION = 'b2bIteration'
B2B_CONTINUOUS_MODE = 'b2bContinuousMode'
PROVISIONING = 'IsProvisioning'
CONNECT_DEVICE = 'DeviceConnection'
CRITICAL = 'IsCritical'
ACCEPTANCE_CRITERIA = 'TcAcceptanceCriteria'
MAX_RETRY = 'TcMaxRetry'
MAX_ATTEMPT = 'TcMaxAttempt'
WARNING = 'isWarning'
DEFAULT_INT_VALUE = 1


class TCParameters():

    """ Parameters

        This class implements the TC parameters objects.
        This object parses all the information related to TC parameters.
    """

    def __init__(self, tcase_name, tc_attrs_override):
        self._name = str(tcase_name)
        self._attrs_override = tc_attrs_override
        self._file_extention = ".xml"
        self._execution_config_path = Paths.EXECUTION_CONFIG
        self.__tc_file_path = os.path.join(self._execution_config_path,
                                           tcase_name + self._file_extention)
        self._logger = LOGGER_FWK
        try:
            self._etree_document = etree.parse(self.__tc_file_path)
        except Exception as parse_ex:  # pylint: disable=W0703
            # Create an empty TestCase file to avoid crashes
            warning_msg = "Failed to parse Test case %s ! (%s)" % (str(tcase_name), str(parse_ex))
            self._logger.warning(warning_msg)
            dummy_testcase = "<TestCase><Parameters><Parameter>" \
                "<Name>DUMMY_PARAMETER</Name><Value>DUMMY_VALUE</Value>" \
                "</Parameter></Parameters></TestCase>"
            self._etree_document = etree.ElementTree(etree.fromstring(dummy_testcase))

        self._tc_parameters = {}
        self._tc_parameters_list = []
        self.get_tc_params()

    @property
    def is_provisioning(self):
        """
        This property tells whether a TC is of `provisioning` kind or not

        :return: Whether True or False
        """
        return self.get_testcase_property(prop_name=PROVISIONING,
                                          default_value=False,
                                          default_cast_type="str_to_bool")

    @property
    def do_device_connection(self):
        """
        This property tells whether a TC activate
        or not ACS FWK device connection

        :return: Whether True or False
        """
        return self.get_testcase_property(prop_name=CONNECT_DEVICE,
                                          default_value=True,
                                          default_cast_type="str_to_bool")

    def get_tc_params(self):
        """ get_tc_params

        This function parses the TC config XML file into a dictionary.

        """
        parameters = self._etree_document.xpath("//Parameters/Parameter")

        for parameter in parameters:
            names = parameter.xpath("./Name")
            for name in names:
                parameter_name = name.text
                self._tc_parameters[parameter_name] = ""
                try:
                    self._tc_parameters[parameter_name] = parameter.xpath("./Value")[0].text
                except IndexError:
                    message_empty = "Parameter " + parameter_name + " value is empty"
                    self._logger.warning(message_empty)
                    continue
                # Fill list to get parameters in order
                self._tc_parameters_list.append("%s=%s" % (parameter_name, self._tc_parameters[parameter_name]))

        return self._tc_parameters

    def get_tc_params_string(self):
        """ get_tc_params_string

        This function returns the list of parameters passed as a string.

        """
        return "; ".join(self._tc_parameters_list)

    def convert_parameter_value(self, tc_param_value, tc_param_name, default_cast_type=str):
        """
        convert value according to a cast type

        This function returns the value of a parameter.

        :type tc_param_value: string
        :param tc_param_value: value to convert

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: depends on default_cast_type
        :return: test case parameter value
        """
        if default_cast_type == "str_to_bool":
            if Utils.is_bool(str(tc_param_value)):
                tc_param_value = Utils.str_to_bool(str(tc_param_value))
            else:
                self._logger.warning("%s='%s', invalid value in campaign for test %s" %
                                     (tc_param_name, tc_param_value, self._name))
                tc_param_value = None
        elif default_cast_type is int or default_cast_type is float:
            if Utils.is_number(str(tc_param_value)):
                tc_param_value = default_cast_type(str(tc_param_value))
            else:
                tc_param_value = None
        else:
            tc_param_value = default_cast_type(tc_param_value)
        return tc_param_value

    def get_param_value(self, param, default_value=None, default_cast_type=str):
        """
        get a specific parameter value

        This function returns the value of a parameter.

        :type param: string
        :param param: parameter's name.

        :type default_value: String
        :param default_value: Default value if parameter is not present

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: depends on default_cast_type
        :return: test case parameter value
        """
        tc_param_value = self._tc_parameters.get(param, default_value)
        # In case the tc parameter value is not None, trying to cast the value
        if not tc_param_value or tc_param_value == "None":
            tc_param_value = default_value
        if default_cast_type != str:
            try:
                tc_param_value = self.convert_parameter_value(tc_param_value, param, default_cast_type)
            except ValueError:
                debug_msg = "Wrong value used for test case parameter '%s'. Returning default value '%s' !" % (
                    str(param), str(default_value))
                self._logger.debug(debug_msg)
                tc_param_value = default_value
        # also update the dict with this entry for later comparison
        self._tc_parameters[param] = tc_param_value
        return tc_param_value

    def get_params_as_dict(self):
        """
        get the whole parameter value as dict

        :rtype: dict
        :return: dict (param: param value)
        """
        return self._tc_parameters

    def get_description(self):
        """ get_description

        This function returns the description of a parameter.

        """
        description = self.get_testcase_property('Description', "No test case description")
        if description.upper() in ["NONE", ""]:
            description = "No test case description"
        return description

    def get_b2b_iteration(self):
        """ get_b2b_iteration

        This function returns the B2B iteration value.

        """
        return self.get_testcase_property(prop_name=B2B_ITERATION, default_value=1, default_cast_type=int)

    def get_name(self):
        """
        This function returns tc name.
        """
        return self._name

    def get_file_path(self):
        """
        Return the path of the parameter file
        """
        return self.__tc_file_path

    def get_testcase_property(self, prop_name, default_value=None, range_value=None, default_cast_type=str):
        """
        This function returns a test case property (not parameter)

        :type prop_name: str
        :param prop_name: node to select)

        :type default_value: default: None
        :param default_value: default value to return if empty

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: depends on default_cast_type
        :return: test case parameter value

        """
        # check if param is overridden in campaign
        property_value = None
        if prop_name in self._attrs_override:
            # Get param from campaign
            property_value = self._attrs_override[prop_name]
            property_value = self.convert_parameter_value(property_value, prop_name, default_cast_type)
        # specific condition about boolean
        if not property_value and property_value is not False:
            # Get param from test case
            property_value = self._etree_document.getroot().find(prop_name)
            if property_value is None:
                property_value = default_value
            else:
                property_value = self.convert_parameter_value(property_value.text, prop_name, default_cast_type)

        if range_value is not None and property_value not in range_value:
            property_value = default_value
            self._logger.warning("%s invalid value in " % (prop_name,) +
                                 "campaign for test %s, must be %s" % (self._name, ' or '.join(range_value)))
            self._logger.warning("initialize %s to default value %s" % (prop_name, default_value))
        return property_value

    def get_b2b_continuous_mode(self):
        """ get_b2b_continuous_mode

        This function returns the B2B continuous mode:
        - True means that only the runtest part of each UC will be repeated
        - False means that all 3 parts (Setup, Runtest & tearDown) will be repeated
        - The default value is False

        """

        # check if param is overridden in campaign
        return self.get_testcase_property(prop_name=B2B_CONTINUOUS_MODE,
                                          default_value=False, default_cast_type="str_to_bool")

    def get_ucase_name(self):
        """
        This function returns usecase name.
        """
        ucase_name = self.get_testcase_property(USECASE_NAME_NODE, None)
        return ucase_name

    def get_ucase_class(self):
        """
        This function returns usecase class if present.
        """
        ucase_class = None
        ucase_class_node = self.get_testcase_property(USECASE_CLASS_NAME_NODE, None)
        if ucase_class_node is not None:
            ucase_class = Utils.get_class(ucase_class_node)
        return ucase_class

    def get_pat_raw_data_saving_mode(self):
        """ get_pat_raw_data_saving_mode

        This function returns the Pat raw data saving mode:
        - True means that Pat raw data will be saved
        - False means that Pat raw data will be deleted
        - The default value is False

        """
        # If the node does not exists, return default value (False)
        # This is for backward compatibility
        return self.get_testcase_property(prop_name='SavePatRawData',
                                          default_value=False,
                                          default_cast_type="str_to_bool")

    def get_pat_power_calculation_mode(self):
        """ get_pat_power_calculation_mode

        This function returns the Pat power calculation mode:
        - True means that Patlib will calculate power from voltage & current
        - False means that only voltage & current rail are returned
        - The default value is False

        """
        # If the node does not exists, return default value (False)
        # This is for backward compatibility
        return self.get_testcase_property('PowerCalculation', False)

    def get_is_critical(self):
        """ get_is_critical

        This function returns if the UC was tagged as critical.
        """
        # check if param is overridden in campaign
        return self.get_testcase_property(prop_name=CRITICAL,
                                          default_value=False,
                                          default_cast_type="str_to_bool")

    def get_acceptance_criteria(self):
        """
        Get the acceptance criteria for this test case.

        :rtype: tuple (int, int)
        :return: tuple (max attempt, acceptance)
        """

        # check if param is overridden in campaign
        acceptance_criteria = self.get_testcase_property(prop_name=ACCEPTANCE_CRITERIA,
                                                         default_value=DEFAULT_INT_VALUE,
                                                         default_cast_type=int)
        max_attempt = self.get_testcase_property(prop_name=MAX_ATTEMPT,
                                                 default_value=0,
                                                 default_cast_type=int)
        if not max_attempt:
            max_attempt = self.get_testcase_property(prop_name=MAX_RETRY,
                                                     default_value=DEFAULT_INT_VALUE,
                                                     default_cast_type=int)
        return max_attempt, acceptance_criteria

    def get_tc_expected_result(self):
        """
        Get the expected result for this test case.

        :rtype: string
        :return: PASS, FAIL, BLOCKED
        """

        # Get the Tc expected result
        # check if param is overridden in campaign
        tc_expected_result = self.get_testcase_property(prop_name='TcExpectedResult',
                                                        range_value=Utils.Verdict2Global.map.keys(),
                                                        default_value=Utils.Verdict.PASS)

        return tc_expected_result

    def get_is_warning(self):
        """ get_is_warning

        This function returns if the TC was tagged as warning.
        """
        # check if param is overridden in campaign
        return self.get_testcase_property(prop_name=WARNING,
                                          default_value=False,
                                          default_cast_type="str_to_bool")

    def get_phase_node(self):
        """
        This function returns phase if present.
        """
        phase_node = self.get_testcase_property(PHASE_NODE, None)
        return phase_node

    def get_type_node(self):
        """
        This function returns type if present.
        """
        type_node = self.get_testcase_property(TYPE_NODE, None)
        return type_node

    def get_domain_node(self):
        """
        This function returns domain if present.
        """
        domain_node = self.get_testcase_property(DOMAIN_NODE, None)
        return domain_node
