#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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

@organization: INTEL MCG PSI
@summary: This module implements Sphinx Auto-generator of Documentation
@since: 4/8/14
@author: sfusilie
"""
import re

from acs.Core.TestStep.TestStepConstants import TestStepConstants
from acs.UtilitiesFWK.Utilities import CAST_TYPE_DICTIONARY, str_to_bool
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class TestStepParameters(object):

    """
    Class which manages test steps parameters
    """
    DEFAULT = "DEFAULT"
    FROM_DEVICE = "FROM_DEVICE"
    REGEX_FROM_DEVICE = FROM_DEVICE + ":(?P<device_name>\S+):(?P<device_config_key>\S+)"
    FROM_BENCH = "FROM_BENCH"
    REGEX_FROM_BENCH = FROM_BENCH + ":(?P<bench_name>\S+):(?P<bench_config_key>\S+)"
    FROM_TC = "FROM_TC"
    REGEX_FROM_TC = FROM_TC + ":(?P<tc_param>\S+)"
    FROM_CTX = "FROM_CTX"
    REGEX_FROM_CTX = FROM_CTX + ":(?P<ctx_param>\S+)"
    CONCAT_KEYWORD = "[+]"
    LIST_KEYWORD = "[|]"

    """
    Contains test step and use case parameters
    """

    def __init__(self, factory):
        """
        Constructor
        """
        self._factory = factory

    def __getattr__(self, name):
        """
        Gets called if an object member hasn't been found.
        It creates the member with name and assign None to it

        :type name: string
        :param name: the name of the parameter to retrieve the value of
        """

        self.__dict__[name] = None
        return self.__dict__[name]

    @staticmethod
    def __cast_param_type(param_name, param_value, param_type):
        """
        Cast the parameter into the given type

        :type param_name: str
        :param param_name: Name of the parameter

        :type param_value: str
        :param param_value: Value of the parameter

        :type param_type: str
        :param param_type: Type of the parameter (it will be casted using CAST_TYPE_DICTIONARY)

        :return: casted parameter value
        """
        try:
            param_value = CAST_TYPE_DICTIONARY[param_type](param_value)
        except (ValueError, TypeError):
            error_msg = "Cannot convert value of '{0}' ({1}) into '{2}' !".format(
                param_name, param_value, param_type)
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        return param_value

    def _check_multiple_values(self, param_name, values, param_type, possible_values):
        """
        Given a list of values, check that each of them is valid
        """
        separator = "," if "," in values else ";"
        for value in values.split(separator):
            self.__check_possible_values(param_name, value.strip(), param_type, possible_values)

    @staticmethod
    def __check_possible_values(param_name, param_value, param_type, possible_values):
        """
        Considering that possible values is formatted as follow :
            possible_value=value1;value2;value3
            Split the possible_value in a list then check that param_value is in the list

            possible_value=[min_value:max_value]
            Split the possible_value in a range then check that param_value min_value <= param_value <= max_value

        Raise an AcsConfigException in case the value is not valid

        :type param_name: str
        :param param_name: Name of the parameter

        :type param_value: str
        :param param_value: Value of the parameter

        :type param_type: str
        :param param_type: Type of the parameter (it will be casted using CAST_TYPE_DICTIONARY)

        :type possible_values: str
        :param possible_values: Possible values
        """
        try:
            # Check that value is in list
            is_valid = param_value in [CAST_TYPE_DICTIONARY[param_type]
                                       (y.strip()) for y in possible_values.split(';')]
        except ValueError:
            is_valid = False

        try:
            # Check that value is in range
            if not is_valid:
                min_value, max_value = tuple(
                    [CAST_TYPE_DICTIONARY[param_type](y) for y in possible_values[1:-1].split(':')])
                is_valid = (min_value <= param_value <= max_value)
        except ValueError:
            is_valid = False

        if not is_valid:
            error_msg = "Value of '{0}' ({1}) is not in possible values {2}".format(
                param_name, param_value, possible_values)
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

    def infer_pars(self, pars):
        """
        Takes the dictionary pars and creates class members on the fly

        :type pars: dict
        :param pars: a list of parameters (aca the xml parameters / step attributes)
        """

        for name, value in pars.items():
            self.__dict__[name.lower()] = value

    def _read_from_default(self, name, global_conf):
        """
        Read value from the DefaultValue tag set defined in the description of the test step catalog
        """
        param_ref_value = None
        teststep_dictionary = self._factory.get_test_step_catalog(global_conf)
        # Update the parameter value using the default value
        ts_name = self.get_attr(TestStepConstants.STR_TS_ID.lower())
        if ts_name in teststep_dictionary:
            ts_parameters = teststep_dictionary[ts_name].get(TestStepConstants.STR_PARAMETERS)
            if ts_parameters:
                ts_param_name = name.upper()
                if ts_param_name in ts_parameters:
                    param_ref_value = ts_parameters[ts_param_name].get(TestStepConstants.STR_PARAM_DEFAULT_VALUE)

        return param_ref_value

    def _read_from_device_config(self, value):
        """
        Read value from the device config
        """
        param_ref_value = None
        from_device = re.match(self.REGEX_FROM_DEVICE, value)
        if from_device:
            device_config_key = from_device.group('device_config_key')
            device_config = self._factory.create_device_config(from_device.group('device_name'))
            if device_config_key not in device_config:
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                         "'{0:s}' device config key does not exist !".format(device_config_key))
            # Update the parameter value using the device config
            param_ref_value = device_config.get(device_config_key)
        return param_ref_value

    def _read_from_bench_config(self, value):
        """
        Read value from the bench config
        """
        param_ref_value = None
        from_bench = re.match(self.REGEX_FROM_BENCH, value)
        if from_bench:
            bench_config = self._factory.create_bench_config(from_bench.group("bench_name"))
            # Update the parameter value using the bench config
            param_ref_value = bench_config.get_param_value(from_bench.group("bench_config_key"))
        return param_ref_value

    def _read_from_test_case(self, tc_parameters, value, param_ref_value):
        """
        Read value from the test case parameter
        """
        if not tc_parameters:
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, "No test case parameters defined !")

        from_tc = re.match(self.REGEX_FROM_TC, value)
        if from_tc:
            ref_key = from_tc.group("tc_param")
            param_ref_value = tc_parameters.get_param_value(ref_key)
            if not param_ref_value:
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                         "'{0:s}' is not a test case parameter !".format(ref_key))
        return param_ref_value

    def _read_from_context(self, context, value):
        """
        Read value from the context
        """
        param_ref_value = None
        from_ctx = re.match(self.REGEX_FROM_CTX, value)
        if from_ctx:
            ref_key = from_ctx.group("ctx_param")
            param_ref_value = context.get_info(ref_key)
            if param_ref_value is None:
                raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                         "'{0:s}' does not exist in the context !".format(ref_key))
        return param_ref_value

    def _add_to_dict(self, name, param_ref_value):
        """
        Check that the value is valid then append the dictionary
        """
        if param_ref_value is not None:
            self.__dict__[name] = param_ref_value

    def __get_static_value(self, name, tc_parameters, global_conf, value):
        param_ref_value = None
        if value == self.DEFAULT:
            param_ref_value = self._read_from_default(name, global_conf)
        elif self.FROM_DEVICE in value:
            param_ref_value = self._read_from_device_config(value)
        elif self.FROM_BENCH in value:
            param_ref_value = self._read_from_bench_config(value)
        elif self.FROM_TC in value:
            param_ref_value = self._read_from_test_case(tc_parameters, value, param_ref_value)
        return param_ref_value

    def __is_static_available(self, value):
        return value == self.DEFAULT or self.FROM_DEVICE in value or self.FROM_BENCH in value or self.FROM_TC in value

    def replace_static_pars_refs(self, tc_parameters, global_conf):
        """
        Replace reference keys by its value. The user can set test Step parameters with following keys:
            DEFAULT
                will allow the user to set its parameter with value defined in the tag DefaultValue
                from the teststep_catalog

            FROM_DEVICE:device_name:device_config_key
                will allow the user to use value defined in the device configuration
                (Catalog, override of bench config or acs cmd line) of device_name.

            i.e: FROM_DEVICE:PHONE1:bootTimeout will get value of bootTimeout defined in the device catalog.
            Warning if the user overrides the value of bootTimeout in the bench config or in the acs cmd line.
            It will take the overridden value.
            This is applicable to all types of test step (Base, Device, Equipment)

            FROM_BENCH:equipment_name:bench_config_key
                will allow the user to use value in the bench config for equipment_name.

            i.e: FROM_BENCH:IO_CARD:SwitchOnOff will get the value of SwitchOnOff defined in the bench config
            for the equipment IO_CARD.
            This is applicable to all types of test step (Base, Device, Equipment)

            FROM_TC:tc_parameter
                will allow the user to use value set in the test case file.

        :type tc_parameters: :py:class:`~acs.Core.TCParameters`
        :param tc_parameters: the test case parameters
        :type global_conf: dict
        :param global_conf: global configuration containing info on usecase catalogs, test step catalogs ...

        """

        for name, value in self.__dict__.items():
            value = str(value)

            if self.CONCAT_KEYWORD in value:
                new_value = value
                for value_section in value.split(self.CONCAT_KEYWORD):
                    if self.__is_static_available(value_section):
                        # For each section of the parameter, try to compute it
                        compute = self.__get_static_value(name, tc_parameters, global_conf, value_section)
                        if compute is not None:
                            # If got a value, replace it
                            new_value = new_value.replace(value_section, str(compute))

                if not self.__is_dynamic_available(new_value):
                    # No more section to compute, clean the new value
                    # else keep concat keyword for dynamic computation
                    new_value = new_value.replace(self.CONCAT_KEYWORD, "")

                if new_value != value:
                    # If new value computed, store it
                    self._add_to_dict(name, new_value)
            elif self.LIST_KEYWORD in value:
                new_value = value
                for value_section in value.split(self.LIST_KEYWORD):
                    if self.__is_static_available(value_section):
                        # For each section of the parameter, try to compute it
                        compute = self.__get_static_value(name, tc_parameters, global_conf, value_section)
                        if compute is not None:
                            # If got a value, replace it
                            new_value = new_value.replace(value_section, str(compute))

                if new_value != value:
                    # If new value computed, store it
                    self._add_to_dict(name, new_value)
            else:
                new_value = self.__get_static_value(name, tc_parameters, global_conf, value)
                if new_value:
                    # If new value computed, store it
                    self._add_to_dict(name, new_value)

    def __get_dynamic_value(self, context, name, value):
        param_ref_value = None
        if self.FROM_CTX in value:
            param_ref_value = self._read_from_context(context, value)
        return param_ref_value

    def __is_dynamic_available(self, value):
        return self.FROM_CTX in value

    def replace_dynamic_pars_refs(self, context):
        """
        Replace reference keys by its value. The user can set test Step parameters with following keys:
            FROM_CTX:context_key
                will allow the user to use value set in the test step context.

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: the test case context
        """

        for name, value in self.__dict__.items():
            value = str(value)
            if self.CONCAT_KEYWORD in value:
                new_value = value
                for value_section in value.split(self.CONCAT_KEYWORD):
                    if self.__is_dynamic_available(value_section):
                        compute = self.__get_dynamic_value(context, name, value_section)
                        if compute is not None:
                            # If new value computed, store it
                            new_value = new_value.replace(value_section, str(compute))

                # Clean the pars
                new_value = new_value.replace(self.CONCAT_KEYWORD, "")
            elif self.LIST_KEYWORD in value:
                new_value = value
                for value_section in value.split(self.LIST_KEYWORD):
                    if self.__is_dynamic_available(value_section):
                        compute = self.__get_dynamic_value(context, name, value_section)
                        if compute is not None:
                            # If new value computed, store it
                            new_value = new_value.replace(value_section, str(compute))
            else:
                new_value = self.__get_dynamic_value(context, name, value)

            self._add_to_dict(name, new_value)

    def get_attr(self, name):
        """
        Return the value of the object member called name

        :type name: str
        :param name: the name of the parameter to retrieve the value of
        """
        return self.__dict__.get(name)

    def check_pars(self, global_conf):
        """
        Check that test step parameters are compliant with type defined in the Parameter Catalog
        Raise an AcsConfigException in case the parameter is not compliant

        :type global_conf: dict
        :param global_conf: global configuration containing info on usecase catalogs, test step catalogs ...
        """
        teststep_dictionary = self._factory.get_test_step_catalog(global_conf)
        test_step_name = self.get_attr(TestStepConstants.STR_TS_ID.lower())
        if teststep_dictionary is None:
            raise AcsConfigException(AcsConfigException.INSTANTIATION_ERROR,
                                     "TestStep catalog not found and is needed to check test step parameters!")

        if test_step_name and test_step_name in teststep_dictionary:
            for ts_param in teststep_dictionary[test_step_name][TestStepConstants.STR_PARAMETERS]:
                # Lower case is used be Parameters class
                ts_param_name = ts_param.lower()
                ts_param_value = self.get_attr(ts_param_name)
                blank_allow = teststep_dictionary[test_step_name][TestStepConstants.STR_PARAMETERS][ts_param].get(
                    TestStepConstants.STR_PARAM_BLANK)
                if blank_allow is not None:
                    blank_allow = str_to_bool(blank_allow)
                is_optional = teststep_dictionary[test_step_name][TestStepConstants.STR_PARAMETERS][ts_param].get(
                    TestStepConstants.STR_PARAM_IS_OPTIONAL)
                if is_optional is not None:
                    is_optional = str_to_bool(is_optional)

                # If is_optional, does not raise error if not set, just set value, then continue
                if ts_param_value is None and is_optional:
                    self.__dict__[ts_param_name] = None
                    continue

                # Raise an error in case the parameter is empty
                if ts_param_value is not None and (blank_allow or str(ts_param_value).strip() != ""):
                    # Get the type to cast the parameter
                    ts_param_type = teststep_dictionary[test_step_name][TestStepConstants.STR_PARAMETERS][
                        ts_param].get(TestStepConstants.STR_PARAM_TYPE)
                    # Get the possible values of the parameter
                    ts_possible_values = teststep_dictionary[test_step_name][TestStepConstants.STR_PARAMETERS][
                        ts_param].get(TestStepConstants.STR_PARAM_POSSIBLE_VALUES)

                    # Check if the cast is necessary
                    if str(type(ts_param_value).__name__) != ts_param_type:
                        # Cast the parameter into given type
                        value_to_check = self.__cast_param_type(ts_param, ts_param_value, ts_param_type)
                    else:
                        value_to_check = ts_param_value

                    # Check possible values
                    # Sometimes value_to_check is in fact a list of values (comma or semicolon separated),
                    # hence it's necessary to check each of them.
                    if ts_possible_values:
                        if isinstance(value_to_check, basestring):
                            self._check_multiple_values(ts_param, value_to_check, ts_param_type, ts_possible_values)
                        else:
                            self.__check_possible_values(
                                ts_param, value_to_check, ts_param_type, ts_possible_values)

                    # Update the parameter value
                    self.__dict__[ts_param_name] = value_to_check
                else:
                    raise AcsConfigException(
                        AcsConfigException.INVALID_PARAMETER,
                        "'{0:s}' parameter is mandatory and shall have a non empty value !".format(ts_param))
