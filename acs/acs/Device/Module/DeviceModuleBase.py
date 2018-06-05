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
@summary: This module defines device module interface
@since: 4/7/14
@author: sfusilie
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
