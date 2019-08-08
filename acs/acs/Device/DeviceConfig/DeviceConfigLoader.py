#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
import os.path as path
import fnmatch

try:
    import lxml.etree as etree
except ImportError:
    import xml.etree as etree

import acs.UtilitiesFWK.Utilities as Utils
import acs.Core.PathManager as PathMgr
from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.ErrorHandling.AcsConfigException import AcsConfigException

from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.FileUtilities import FileUtilities


# Aliases
Paths = PathMgr.Paths
# In order not to access protected Class. Using factory instead
EtreeElementType = type(etree.Element("EtreeElementType"))
AcsConstants = Utils.AcsConstants

# ############### Grouping XML possible parsing errors ###############

# IOError : If the provided file is of the good type but invalid
# TypeError : If the provided file is an invalid type such as None
# XMLSyntaxError : speaking of itself

XMLParsingErrors = IOError, TypeError, etree.XMLSyntaxError,


def _error(msg, flag=AcsConfigException.XML_PARSING_ERROR):
    """
    Wraps ACS Exceptions mechanism into a single method

    :param msg: The Exception message
    :type msg: str

    :param flag: The Exception flag
    :type flag: str or None

    :raise AcsConfigException: When called

    """
    raise AcsConfigException(flag, msg)


def _override_filter(conf, conf_key=None, klass=None, callback=None):
    """
    This is a hack for DeviceModules Section as it is containing list

    TODO: ask if really can have more than 1 flashmodule, ... per model ? Why a list ?

    :param conf: The configuration dict
    :type conf: dict or AttributeDict

    :param conf_key: The Configuration key to look up
    :type conf_key: str

    :param klass: The python class to look for
    :type klass: tuple

    :param callback: The Callback to be called
    :type callback: callable

    """
    if ((conf_key or klass or callback) is None or
            not callable(callback) or
            not isinstance(conf, (dict, AttributeDict))):
        return

    device_modules = conf[conf_key].copy()
    for key, value in device_modules.iteritems():
        if isinstance(value, klass):
            conf[conf_key][key] = callback(value)


def _remove_prohibited_keys(data, keys=None, logger=LOGGER_FWK):
    """
    Removes all prohibited keys from data dictionary.

    :param data: The dictionary to be analyzed
    :type data: dict

    :param keys: The prohibited keys
    :type keys: list or tuple

    :param logger: (optional) A logger instance (from :mod:`logging` module)
    :type logger: logging.Logger

    """
    if not data or not keys:
        return

    for key in keys:
        if key in data:
            logger and logger.warning('[PROHIBITIVE BEHAVIOR] => Parameter {0} override is forbidden !'.format(key))
            logger and logger.warning('[PROHIBITIVE BEHAVIOR] => Parameter {0} ignored !'.format(key))
            del data[key]


def _strip(value):
    """
    little wrapper function

    :param value: The value to be stripped

    """
    if value and isinstance(value, basestring):
        return value.strip()
    return value


def _check_and_format_value(v):
    """
    Formats all Pythonic boolean value into XML ones

    :param v: The value to be checked

    """
    booleans = {'True': 'true', 'False': 'false'}
    clean = _strip(v)
    if clean in booleans:
        return booleans.get(clean)
    return clean


class Device(object):

    """
    A Device Class, representing a D.U.T with its :

    * Parameters
    * Overrides mechanisms
    * Parameters checker

    """

    ROOT_TAG = 'DeviceModel'
    SCHEMA_LOCATION_KEY = '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'
    DEPRECATED_OVERRIDE_MSG = 'Unsupported format detected in {0}'
    DEPRECATED_ELEMENT_MSG = '\n\t<Parameter name="{0}" value="{1}" {2} />'
    RECOMMENDED_ELEMENT_MSG = '\n\t<Parameter {0}="{1}" {2} />'
    PROHIBITIVE_KEYS = ('Name', 'DeviceConfigPath', 'device_modules', 'parameter_overloaded')

    @classmethod
    def dict2xml(cls, xml_map, parent, parameter_tag='Parameter'):
        """
        This class method maps into the given XML root node,
        all what is contained into inner configuration dict.

        It produces an XML node which can either pass or not validations

        :param xml_map: The XML map
        :type xml_map: dict or AttributeDict

        :param parent: The root/parent node
        :type parent: etree.Element

        :param parameter_tag: The Parameter `tag` name
        :type parameter_tag: str

        """
        def generic_processing():
            """
            This method's purpose is to structure inner actions only

            .. important:: For parameters details see parent definition (:meth:`DeviceConfigLoader.dict2xml`)

            """
            for key, value in xml_map.iteritems():
                if isinstance(value, (dict, AttributeDict)):
                    section = etree.Element(_tag=key)
                    parent.append(section)
                    cls.dict2xml(value, section, parameter_tag=parameter_tag)
                else:
                    parent.append(etree.Element(_tag=parameter_tag, attrib={key: value}))

        if not isinstance(parent, EtreeElementType):
            _error('Need A XML node as `parent` attribute ! Got => {0}'.format(type(parent)))

        # Hack for non-generic Implementation tag.
        if parent.tag == 'Implementation':
            parent.append(etree.Element(_tag=parameter_tag, attrib=xml_map))
        else:
            generic_processing()

    @classmethod
    def extract_schema(cls, node, schema_folder, file_only=True):
        """
        Class Method which extracts the XML Schema file reference if so.

        :param node: The XML Node or the XML file to be parsed into a node
        :type node: etree.Element

        :param schema_folder: If provided the value is concatenated to the schema basename if available
        :type schema_folder: str

        :param file_only: If set to True the schema is not loaded
        :type file_only: bool

        :return: Either the schema filename or its corresponding XML instance (
        :rtype: str or etree.XMLSchema

        """
        schema_files = []
        if isinstance(node, basestring) and path.isfile(node):
            node = etree.parse(node).getroot()

        schema_file = node.attrib.get(cls.SCHEMA_LOCATION_KEY)
        if schema_file and schema_folder and path.isdir(schema_folder):
            schema_file = PathMgr.absjoin(schema_folder, path.basename(schema_file))
            schema_files = os.listdir(schema_folder)

        try:
            self_name = node.base
        except AttributeError:
            self_name = "Unknown"

        if not schema_file or not path.isfile(schema_file):
            _error(("Your Configuration file : {0} does not define an"
                    " 'xsi:noNamespaceSchemaLocation' in root element!").format(self_name))

        if path.basename(schema_file) not in schema_files:
            _error("Your Device Model file : {0} does not define a Valid Schema"
                   " 'xsi:noNamespaceSchemaLocation' in root element!").format(self_name)

        if file_only:
            return schema_file
        try:
            return etree.XMLSchema(etree.parse(schema_file))
        except etree.Error as schema_error:
            _error(schema_error.message)

    @classmethod
    def extract_device_modules(cls, node):
        """
        Get DeviceModule Node(s) properties

        :param node: The root node
        :type node: etree.Element

        :return: A dict of DeviceModule's attributes
        :rtype: AttributeDict

        """
        # Extract device modules
        module_params = AttributeDict()
        for device_module in node.xpath(".//DeviceModule/*"):
            if device_module.tag not in module_params:
                # init module config as list
                module_params[device_module.tag] = []
            module_config = AttributeDict()
            module_config.class_name = device_module.get("className")
            module_config.config = device_module.get("config")

            # Handle parameter overload
            module_config.parameter_overloaded = {}
            for module_param in device_module.xpath("Parameter"):
                module_config.parameter_overloaded.update(module_param.attrib)

            # store config of the module
            module_params[device_module.tag].append(module_config)
            # Removing the node for post processing
            device_module.getparent().remove(device_module)
        return module_params

    @property
    def cli_parameters(self):
        """
        Property/Generator yielding the CLI parameter(s) from list to dict-style

        For example, -o bootTimeout="300" in CLI produces a list like this :

            .. code-block:: python

                [bootTimeout="300"]

        It becomes :

            .. code-block:: python

                {bootTimeout: "300"}

        """
        if isinstance(self._cli_params, list):
            for device_parameter in self._cli_params:
                split_device_param = device_parameter.split("=")
                # Set parameters which are correctly set in ACS command line
                # as follow : -o bootTimeout="300" or --op=bootTimeout="300" or
                # --override_device_parameter=bootTimeout="300"
                if len(split_device_param) == 2:
                    # Store device parameter name and value
                    yield split_device_param

    @property
    def device_extra_params(self):
        """
        Property holding All extra parameters found either in Bench Config file
        or CLI that are not referenced in the corresponding Device Model Schema.

        Since those parameters cannot be validated, we just update device configuration with it !

        :return: The Current Device's configuration
        :rtype: AttributeDict

        """
        if not self._device_extra_params:
            self._device_extra_params = {}
            self._device_extra_params.update(self._bench_unknown_parameters)
            self._device_extra_params.update(self._cli_unknown_parameters)
        return self._device_extra_params

    @property
    def device_only_params(self):
        """
        Get a map with only parameters, no sections !

        :return: A map with only parameters
        :rtype: AttributeDict()

        """
        if not self._device_only_params:
            # Store the Current Device's configuration
            self._device_only_params = AttributeDict()
            self._load_params_only(self.device_conf, self._device_only_params)

            # Updating all unchecked extra parameters
            self._device_only_params.update(self.device_extra_params)

        if 'description' in self.device_extra_params:
            del self.device_extra_params['description']

        return self._device_only_params

    @property
    def device_model_final(self):
        """
        Property computing/holding the final Device Model XML node,
        rebuild from its mapped AttributeDict

        :return: The final Device Model XML node
        :rtype: etree.Element

        """
        if self._device_model_final is None:
            self._device_model_final = etree.Element(_tag=self.ROOT_TAG)
            # Hack to match XSD, ACS input is not compliant!
            xml_map = self.device_conf.copy()

            dm_key = 'device_modules'

            if dm_key in xml_map:
                _override_filter(xml_map, conf_key=dm_key, klass=(list,), callback=lambda v: v[0] if v else None)
                xml_map['DeviceModule'] = xml_map[dm_key]

            for unexpected_key in self.PROHIBITIVE_KEYS:
                if unexpected_key in xml_map:
                    del xml_map[unexpected_key]

            self.dict2xml(xml_map, self._device_model_final)
        return self._device_model_final

    @property
    def device_model_name(self):
        """
        Computes the Current Device Model name

        :return: Current Device Model name
        :rtype: str

        """
        if not self._device_model_name:
            if self._device_name == AcsConstants.DEFAULT_DEVICE_NAME:
                # For PHONE1 we need to retrieve the device model name
                if self._device_model_name and "multi" not in self._device_model_name:
                    pass
                elif ((not self._device_model_name or "multi" in self._device_model_name)
                      and self.bench_conf  # noqa
                      and "Name" in self.bench_conf):  # noqa
                    # Device model name is not specified or in "multi" mode
                    # Get it from bench config
                    self._device_model_name = self.bench_conf.Name
                else:
                    _error("No device model specified/configured. Cannot instantiate the device.")
            else:
                # For any other phone than phone1, the information comes from the bench config.
                self._device_model_name = self.bench_conf.Name
        return self._device_model_name

    @property
    def device_root_node(self):
        """
        Property holding the Device root's node

        :return: The device root's node
        :rtype: etree.Element

        .. note:: Consider etree.Element as an `etree._Element` instance factory

            The real Class is **etree._Element**

        """
        if self._device_root_node is None and self._device_tree_node is not None:
            self._device_root_node = self._device_tree_node.getroot()

        if self._device_root_node is None:
            _error("Device catalog is corrupted! Unable to parse {0}".format(self.device_conf_filename))

        return self._device_root_node

    @property
    def device_schema(self):
        """
        Property holding the Device associated XML Schema instance

        :return: The device XML Schema instance
        :rtype: etree.XMLSchema

        """
        return self._device_schema

    @property
    def device_conf_filename(self):
        """
        Property holding the Device configuration filename (full path)

        :return: The Device configuration filename
        :rtype: str

        """
        if not self._device_conf_filename:
            device_model, catalog_path = self.device_model_name, Paths.DEVICE_MODELS_CATALOG
            device_config_filename = "{0}.xml".format(device_model)

            files = FileUtilities.find_file(catalog_path, device_config_filename)
            files_count = len(files)
            error = None
            if files_count == 0:
                error = ("Device {0} not found in the catalog {1} !".format(device_model, catalog_path),
                         AcsConfigException.FILE_NOT_FOUND)
            elif files_count > 1:
                error = ("Device {0} found multiple times in the catalog {1}. "
                         "{2}".format(device_model, catalog_path, "\n at ".join(files)),
                         AcsConfigException.PROHIBITIVE_BEHAVIOR)
            else:
                self._device_conf_filename = files[0]
            if error:
                _error(*error)
        return self._device_conf_filename

    @property
    def device_conf(self):
        """
        Property holding the Current Device's configuration

        :return: The Current Device's configuration
        :rtype: AttributeDict

        """
        return self._device_conf

    @property
    def bench_contains_errors(self):
        """
        Property holding whether or not
        the Bench Configuration file is properly filled in.

        :return: Whether or not the Bench Configuration file is properly filled in
        :rtype: bool

        """
        return len(self._bench_conf_deprecated) > 0

    @property
    def bench_root_node(self):
        """
        Property holding the Bench root's node

        :return: The Bench root's node
        :rtype: etree.Element

        .. note:: Consider etree.Element as an `etree._Element` instance factory

            The real Class is **etree._Element**

        """
        if self._bench_root_node is None and self._bench_tree_node is not None:
            self._bench_root_node = self._bench_tree_node.getroot()
        return self._bench_root_node

    @property
    def bench_device_node(self):
        """
        Property holding the Current Device Bench Phone's node

        :return: The Current Device Bench Phone's node
        :rtype: etree.Element

        .. note:: Consider etree.Element as an `etree._Element` instance factory

            The real Class is **etree._Element**

        """
        if self._bench_tree_node is not None:
            xpath = "//Phone[@name='{0}']".format(self._device_name)
            self._bench_device_node = self._bench_tree_node.xpath(xpath)
        return self._bench_device_node

    # noinspection PyUnresolvedReferences
    @property
    def bench_conf_global(self):
        """
        Property holding the Global Bench Configuration instance

        .. seealso:: Constructor parameters.

        :return: The Global Bench configuration instance
        :rtype: AttributeDict

        """
        if not self._bench_conf_global:
            self._bench_conf_global = self._global_config.benchConfig
        return self._bench_conf_global

    @property
    def bench_conf_filename(self):
        """
        Property holding the Bench Configuration filename (abspath)

        :return: The Bench configuration filename
        :rtype: str

        """
        if not self._bench_conf_filename:
            self._bench_conf_filename = self.bench_conf_global.file
        return self._bench_conf_filename

    @property
    def bench_conf(self):
        """
        Property holding the Current Device's Bench configuration

        :return: The Current Device's Bench configuration
        :rtype: AttributeDict

        """
        return self._bench_conf

    def __init__(self, name, device_model_name, global_config, cli_params):
        """
        Constructor

        :param global_config: The Global configuration
        :type global_config: AttributeDict or dict

        """
        # ################ Global #################

        # Global Configuration instance (grouping all needed parameters)
        self._global_config = global_config

        # ################ CmdLine #################

        # Command line parameters
        self._cli_params = cli_params

        # Unknown Parameter(s) found in the Command line arguments (``-o``)
        self._cli_unknown_parameters = {}

        # ################ Device #################

        # The current Device's name
        self._device_name = name

        # The Device parameters only (no sections)
        self._device_only_params = {}

        # The Device extra unchecked parameters reference
        self._device_extra_params = {}

        # The Device Model's map with its sections (dict)
        self._device_conf_sections = None

        # The Device Model name
        self._device_model_name = device_model_name

        # The Device Model final XML node
        self._device_model_final = None

        # Device Configuration etree.ElementTree
        self._device_tree_node = None

        # Device Configuration root node (etree.Element)
        self._device_root_node = None

        # Device Configuration filename (abspath)
        self._device_conf_filename = None

        # Device configuration instance (AttributeDict)
        self._device_conf = None

        # Device's XML Schema reference
        self._device_schema = None

        # ################ Bench #################

        # Unknown Parameter(s) found in the BenchConfig file
        self._bench_unknown_parameters = {}

        # Global Bench Configuration instance
        self._bench_conf_global = None

        # Bench Configuration etree.ElementTree
        self._bench_tree_node = None

        # Bench Configuration root node (etree.Element)
        self._bench_root_node = None

        # Bench Configuration `Phone` node (etree.Element)
        # for the given Device Model name
        self._bench_device_node = None

        # Bench Configuration filename (abspath)
        self._bench_conf_filename = None

        # Bench configuration instance (AttributeDict)
        self._bench_conf = None

        # Bench configuration instance (AttributeDict)
        self._bench_conf_deprecated = AttributeDict()

    def _load_params_only(self, conf, data):
        """
        Loads in memory into `data` parameter
        only the DUT parameters (without sections)

        :param conf: The Device Model Configuration
        :type conf: dict or AttributeDict

        """
        dm_key = 'device_modules'
        for key, value in conf.iteritems():
            is_device_modules = key == dm_key
            if is_device_modules:
                _override_filter(conf, conf_key=dm_key, klass=(AttributeDict, dict), callback=lambda v: [v])
            if isinstance(value, (dict, AttributeDict)) and not is_device_modules:
                self._load_params_only(value, data)
            else:
                data[key] = value

    def _load_cli_conf(self):
        """
        Loads Overridden Device Configuration parameters from CLI into a dict

        Some keys are not allowed in CLI overridden parameters::

            1. "Name" => Used for the whole process, `DeviceModel alias` (**INTERNAL USE ONLY**)
            2. "DeviceConfigPath" => The associated Bench configuration file path (**INTERNAL USE ONLY**)
            3. "DeviceModel" => There's no point in overriding this property

        """
        _remove_prohibited_keys(self._cli_params, self.PROHIBITIVE_KEYS + ("DeviceModel",))

    def _load_device_conf(self):
        """
        Loads The Device Configuration from its XML representation into a dict

        """
        try:
            self._device_tree_node = etree.parse(self.device_conf_filename)
        except XMLParsingErrors:
            _error("Corrupted file {0}: {1}".format(self.device_conf_filename, Utils.get_exception_info()[1]))

        self._parse_device_node()
        self._device_schema = self.extract_schema(self.device_root_node,
                                                  schema_folder=Paths.FWK_DEVICE_MODELS_CATALOG, file_only=False)

    def _load_bench_conf(self):
        """
        Loads The Bench Configuration from its XML representation into a dict

        """
        self._bench_conf = AttributeDict()

        # New way of defining device parameters == as defined in the device catalog
        try:
            self._bench_tree_node = etree.parse(self.bench_conf_filename)
        except XMLParsingErrors:
            _error("Corrupted file {0}: {1}".format(self.bench_conf_filename, Utils.get_exception_info()[1]))

        node = self.bench_device_node
        if node is not None and len(node) > 0:
            # To load proper device config, need to get device model name
            device_conf = self.device_conf
            if device_conf:
                self._device_model_name = device_conf.get("DeviceModel")
            if self._device_model_name in ('', "", None, 'multi'):
                self._device_model_name = node[0].get("deviceModel")

            conf = self._parse_bench_node(node[0])
            if conf:
                self._bench_conf.update(conf)

    def _parse_device_node(self):
        """
        Parses XML Device Catalog file and maps it into a python structure (dict)

        :return: A dict mapping XML configuration
        :rtype: AttributeDict

        """
        def extract_params(s_node):
            """
            Get Section properties

            :param s_node: The Section node
            :type s_node: etree.Element

            :return: A dict of Section's attributes
            :rtype: AttributeDict

            """
            params = AttributeDict()
            for attrs in s_node.xpath(".//Parameter"):
                params.update(attrs.attrib)
            return params

        buf_params = AttributeDict()
        # Storing value to avoid recomputing each call
        device_model_name = self.device_model_name

        if device_model_name:
            buf_params["Name"] = device_model_name

        if self.device_conf_filename:
            buf_params["DeviceConfigPath"] = self.device_conf_filename

        node = self.device_root_node
        buf_params['device_modules'] = self.extract_device_modules(node)
        for section_node in list(node):
            buf_params[section_node.tag] = extract_params(section_node)

        self._device_conf = buf_params

    def _parse_bench_node(self, node):
        """
        Parses XML `Phone` node(s) from Bench Catalog file and maps it into a python structure (dict)

        :return: A dict mapping XML configuration
        :rtype: AttributeDict

        :raise AcsConfigException.INVALID_BENCH_CONFIG: If a (or more) deprecated parameter(s)
            is/are found in a Phone node

        """
        LOGGER_FWK.info('Loading optional device model parameters from CLI and/or BenchConfig '
                        'for {0} ({1})...'.format(self._device_name, self._device_model_name))
        buf_params = AttributeDict()
        # Storing value to avoid recomputing each call
        device_model_name = self.device_model_name

        if device_model_name:
            buf_params["Name"] = device_model_name

        if self.device_conf_filename:
            buf_params["DeviceConfigPath"] = self.device_conf_filename

        # Get phone properties
        for attrs in node.xpath(".//Parameter"):
            name, value, description = attrs.get("name"), attrs.get("value"), attrs.get("description")

            if name in self.PROHIBITIVE_KEYS:
                # Do not allow to override internal keys
                # as it would lead to nasty & unexpected behavior !!
                continue

            # Not supported anymore, raise AcsConfigException.INVALID_BENCH_CONFIG !!
            if name and value:
                buf_params[name] = value
                self._bench_conf_deprecated[name] = (value, description)
            else:
                buf_params.update(attrs.attrib)

        # Report Errors if so
        if self.bench_contains_errors:
            LOGGER_FWK.error(self._report_errors())
            _error('Invalid Bench Parameters format found! {0}'.format(', '.join(self._bench_conf_deprecated.keys())),
                   AcsConfigException.INVALID_BENCH_CONFIG)

        # Extracting device modules if so
        buf_params.device_modules = self.extract_device_modules(node)

        return buf_params

    def _override_through_sections(self, conf, key_lookup, value_lookup, unknown):
        """
        Implement Section Lookup through a dict.

        :param conf: The configuration dict
        :type conf: dict or AttributeDict

        .. important:: As the method returns nothing (None), you must pass a reference you hold as `conf` parameter.

            **This reference is modified inside the method only**

        :param key_lookup: The key to look up
        :type key_lookup: str

        :param value_lookup: The value to set
        :type value_lookup: object

        :param unknown: A dict designed to store unknown Key(s)/Value(s)
        :type unknown: dict or AttributeDict

        """
        for existing_key, v in conf.copy().iteritems():
            if isinstance(v, dict):
                self._override_through_sections(v, key_lookup, value_lookup, unknown)
                continue
            if existing_key != key_lookup:
                unknown[key_lookup] = value_lookup
            else:
                conf[key_lookup] = value_lookup

    def _override_parameters_cli(self):
        """
        Override device config with device parameters available in CLI parameters (**-o**) if applicable.

        """
        if self._device_name == AcsConstants.DEFAULT_DEVICE_NAME:
            for param, value in self.cli_parameters:
                self._override_through_sections(self.device_conf, param, value, self._cli_unknown_parameters)

    def _override_parameters_bench(self):
        """
        Override device config with device parameters available in bench config if applicable.

        """
        device_model_name = self.device_model_name
        device_name = self._device_name

        if self.bench_conf:
            do_the_override = False
            if device_name == AcsConstants.DEFAULT_DEVICE_NAME:
                if "Name" not in self.bench_conf:
                    # No device specified in the bench config for PHONE1
                    # Do the override then
                    do_the_override = True
                elif self.bench_conf.Name == device_model_name:
                    # Same device specified on the command line then in the bench config
                    # Do the override
                    do_the_override = True
                else:
                    warning_msg = ("Different device model specified on the command line ({0}) "
                                   "then in the bench config ({1}) for {2}! Related parameters specified "
                                   "in bench config will be ignored !").format(device_model_name,
                                                                               self.bench_conf.Name,
                                                                               AcsConstants.DEFAULT_DEVICE_NAME)
                    LOGGER_FWK.warning(warning_msg)
            else:
                # For other phones (PHONE2, ...) we do the override every time
                do_the_override = True

            if do_the_override:
                for key, value in self.bench_conf.iteritems():
                    if key == "device_modules":
                        for module, module_conf in value.iteritems():
                            self.device_conf.device_modules[module] = module_conf
                    else:
                        self._override_through_sections(self.device_conf, key, value, self._bench_unknown_parameters)

    def _validate(self):
        """
        Asserts that the given Device Model Configuration match its associated Contract

        :raise: AcsConfigException

        """
        try:
            self.device_schema.assertValid(self.device_model_final)
        except (etree.XMLSchemaParseError, etree.DocumentInvalid) as assert_error:
            flag = AcsConfigException.XML_PARSING_ERROR
            if isinstance(assert_error, etree.DocumentInvalid):
                flag = AcsConfigException.INVALID_PARAMETER
            _error(assert_error.message, flag)

    def _report_errors(self):
        """
        Reports all warnings found in BenchConfig, CLI, ...

        """
        report = None
        if self.bench_contains_errors:
            report = self.DEPRECATED_OVERRIDE_MSG.format(self.bench_conf_filename)
            report += '\n\nUnsupported format\n'
            report += '******************\n'
            for k, data in self._bench_conf_deprecated.iteritems():
                value, description = data
                report += self.DEPRECATED_ELEMENT_MSG.format(k, value,
                                                             'description="{0}"'.format(description)
                                                             if description else "")

            report += '\n\nExpected format (to copy in BenchConfig)\n'
            report += '****************************************\n'
            for k, data in self._bench_conf_deprecated.iteritems():
                value, description = data
                report += self.RECOMMENDED_ELEMENT_MSG.format(k, _check_and_format_value(value),
                                                              'description="{0}"'.format(description)
                                                              if description else "")

            report += '\n'

        return report

    def load(self):
        """
        Public method which acts as device configuration loader.

        :rtype: dict
        :return: A dict containing all device parameters

        """
        self._load_cli_conf()
        self._load_bench_conf()
        self._load_device_conf()

        # Load the device config from the device catalog
        if not self.device_conf:
            _error("ACS single mode : No device config found for device {0} !".format(self._device_model_name),
                   AcsConfigException.INVALID_PARAMETER)

        # Override Current DUT parameters from Bench ...
        self._override_parameters_bench()
        # ... and CLI
        self._override_parameters_cli()

        LOGGER_FWK.info('Checking device model integrity...')

        # Asserts All Device Model is valid (Parameters)
        self._validate()

        return self.device_only_params


class DeviceConfigLoader(object):

    """
    Loads the Device Model Configuration from Paths.DEVICE_MODELS_CATALOG
    Checks that the Device Model Configuration match ACS contracts (XML Schema, xsd)

    # #########################################################################################################
    # ############################################ Cooking recipe #############################################
    # #########################################################################################################

    # + Keep reference to CLI parameters (dict)

    # + Load Bench XML file (The Device Model name may be override from BenchConfig file)
    # + Map it to dict

    # + Load Device XML file
    # + Map it to dict
    # + Extract and keep a reference on original Device Model XML Schema

    # + Override overall dict keeping Order (device, bench, CLI) and Sections (Connection, DeviceModule, ...)

    # + Map it to XML Device Model node (in memory)
    # + Assert XML Device Model match its Schema

    # !! The overall configurations dict should be able to produce a dict without Device sections !!

    # #########################################################################################################

    """

    @classmethod
    def retrieve_device_model_list(cls):
        """
        Retrieves from the Device_Catalog files all referenced/available Models.

        :return: A sorted Devices Models list
        :rtype: list

        """
        device_name_list = []
        for root, dirnames, filenames in os.walk(Paths.DEVICE_MODELS_CATALOG):
            for filename in fnmatch.filter(filenames, '*.xml'):
                device_name_list.append(os.path.splitext(filename)[0])

        device_name_list.append("multi")

        return sorted(device_name_list)

    @property
    def devices(self):
        """
        Property computing/holding the devices name(s)

        :return: A sorted list of DUT 's name(s)
        :rtype: list

        """
        if not self._devices:
            # First load device(s) config from the bench config
            # Retrieve sorted device list defined in the bench configuration file
            prefix = AcsConstants.DEVICE_NAME_PREFIX
            parameters = self.bench_conf_global.get_parameters_name()
            devices = [d for d in parameters if prefix in d]
            # Nothing found ! Using default (PHONE1)
            self._devices = (sorted(devices)
                             if devices and len(devices) > 1
                             else [AcsConstants.DEFAULT_DEVICE_NAME])

        return self._devices

    # noinspection PyUnresolvedReferences
    @property
    def device_conf_global(self):
        """
        Property holding the Global Device Configuration instance

        .. seealso:: Constructor parameters.

        :return: The Global Device configuration instance
        :rtype: AttributeDict

        """
        if not self._device_conf_global:
            self._device_conf_global = self._global_config.deviceConfig
        return self._device_conf_global

    # noinspection PyUnresolvedReferences
    @property
    def bench_conf_global(self):
        """
        Property holding the Global Bench Configuration instance

        .. seealso:: Constructor parameters.

        :return: The Global Bench configuration instance
        :rtype: AttributeDict

        """
        if not self._bench_conf_global:
            self._bench_conf_global = self._global_config.benchConfig
        return self._bench_conf_global

    def __init__(self, global_config):
        """
        Constructor

        :param global_config: The Global configuration
        :type global_config: AttributeDict or dict

        """
        # ################ Global #################

        # Global Configuration instance (grouping all needed parameters)
        self._global_config = global_config

        # Global Devices Configurations (All Phones' configuration are grouped in it)
        self._configs = {}

        # ################ CmdLine #################

        # Command line parameters
        self._cli_params = None

        # ################ Device #################

        # Device(s) name(s) list
        self._devices = []

        # Global Device Configuration instance
        self._device_conf_global = None

        # The Device Model name
        self._device_model_name = None

        # ################ Bench #################

        # Global Bench Configuration instance
        self._bench_conf_global = None

    def load(self, device_model, cli_params):
        """
        Public method which acts as device configuration loader.

        :type device_model: str
        :param device_model: The Device Model's name (e.g.: Dummy)

        :type cli_params: list
        :param cli_params: A list of parameters and their value to override (Got from command line)

        :rtype: dict
        :return: A dict containing all device parameters

        """
        if device_model:
            self._device_model_name = device_model
        elif len(self.devices) > 1:
            self._device_model_name = device_model = 'multi'
        else:
            dut = self.bench_conf_global.get_dict().get(AcsConstants.DEFAULT_DEVICE_NAME, {})
            self._device_model_name = device_model = dut.get('deviceModel')

        for name in self.devices:

            # ie. Phone1, Phone2, ...
            device = Device(name, device_model, self._global_config, cli_params)
            model_conf = device.load()
            self._configs[name] = model_conf

            if name == AcsConstants.DEFAULT_DEVICE_NAME:
                # Store PHONE1 also in deviceConfig to avoid to break use cases
                self.device_conf_global.update(self._configs)

            # Store current configuration in the deviceConfig dictionary
            self.device_conf_global.update({name: model_conf})

        return self._configs
