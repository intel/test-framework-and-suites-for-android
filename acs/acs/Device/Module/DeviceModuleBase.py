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

from os import path
import inspect

from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.Parsers.Parser import Parser


class DeviceModuleBase(object):

    """
    Device module interface
    """

    def __init__(self):
        """
        DeviceModuleBase module
        """
        self.__device = None
        self.__logger = None
        self.__module_conf_file = None
        self.__module_config = None
        self.__global_conf = None
        self.__module_config = AttributeDict()
        self.__name = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, new_name):
        self.__name = new_name

    @property
    def configuration_file(self):
        return self.__module_conf_file

    @configuration_file.setter
    def configuration_file(self, new_conf):
        self.__module_conf_file = new_conf

    @property
    def configuration(self):
        return self.__module_config

    @property
    def path(self):
        return path.dirname(path.abspath(inspect.getfile(self.__class__)))

    @property
    def device(self):
        """
        Retrieve the device instance associated to that module
        """
        return self.__device

    @device.setter
    def device(self, new_device):
        """
        Set the device instance associated to that module
        """
        self.__device = new_device

    @property
    def logger(self):
        """
        Retrieve the logger associated to that module
        """
        return self.__logger

    @logger.setter
    def logger(self, new_logger):
        """
        Set the logger associated to that module
        """
        self.__logger = new_logger

    @property
    def global_conf(self):
        return self.__global_conf

    @global_conf.setter
    def global_conf(self, conf):
        self.__global_conf = conf

    def load_conf(self):
        """
        Load the configuration of the module.
        Need to be overloaded is you expect to use a specific configuration file.
        """
        if self.configuration_file and path.isfile(self.configuration_file):
            parser = Parser.get_parser(self.configuration_file)
            for module_conf in parser.get("/ModuleConfiguration/*"):
                if self.device.config.get(module_conf.tag):
                    # Parameter is available in the device config
                    # it may be an old override, take it for back compatibility
                    self.__module_config[module_conf.tag] = self.device.config[module_conf.tag]
                else:
                    self.__module_config[module_conf.tag] = module_conf.text
                    # If the XML parameter has some attributes - parse them
                    if len(module_conf.attrib) != 0:
                        self.__module_config.update(module_conf.attrib)
        else:
            self.logger.error("No module configuration to load!")
