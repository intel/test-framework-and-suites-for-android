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
@since: 4/3/14
@author: sfusilie
"""
import imp
import os
import logging
import sys

from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.Device.Common.Common import get_class
from acs.Core import PathManager
from acs.Core.Report.ACSLogging import ACS_LOGGER_NAME, LOGGER_DEVICE_STATS, LOGGER_FWK


class DeviceModuleFactory(object):

    """
    Factory that will create device module base on the name and the device configuration.
    """

    @staticmethod
    def _load_module(module_path):
        """
        Load a module according to module namespace.
        It will look first for the module path from EXECUTION_CONFIG folder
        Else, if not found, it will load it from python path

        :type module_path: str
        :param module_path: Namespace + class name to instantiate
                           (for instance: 'Device.Module.Common.Flash.DummyFlashModule.DummyFlashModule')
        """
        module = None
        if os.path.isdir(PathManager.Paths.EXTRA_LIB_FOLDER) and module_path:
            # First check in the execution folder extra lib folder if the module is available
            # If it is, it means a patch is needed on the module and we are taking
            # it from execution folder
            module_full_path = PathManager.Paths.EXTRA_LIB_FOLDER
            sys.path.append(module_full_path)
            for module_name in module_path.split(".")[:-1]:
                module_full_path = os.path.join(module_full_path, module_name)

            if os.path.isfile(module_full_path + ".py"):
                module = imp.load_source(module_name, module_full_path + ".py")
            elif os.path.isfile(module_full_path + ".pyc"):
                # pylint: disable=W0631
                module = imp.load_compiled(module_name, module_full_path + ".pyc")

            if module:
                module = getattr(module, module_name)()

        if not module:
            # If the module is not in execution folder, load it from std python path
            module = get_class(module_path)()

        return module

    @staticmethod
    def _load_conf(module, conf_file):
        """
        Load module configuration.
        It will look first at the file in the EXECUTION_CONFIG folder
        Else, if not find, it will load the configuration based on the module path


        :type module: object
        :param module: Module instance

        :type conf_file: str
        :param conf_file: Configuration file to load
        """
        execution_conf_patch_path = os.path.join(PathManager.Paths.EXECUTION_CONFIG, conf_file)
        if os.path.isfile(execution_conf_patch_path):
            # We found a module conf in the execution folder, we use it instead of default one
            configuration_file = execution_conf_patch_path
        else:
            module_conf = os.path.join(module.path, conf_file)
            if os.path.isfile(module_conf):
                configuration_file = module_conf
            else:
                raise AcsConfigException("Cannot find \"{0}\" device module configuration: {1}".format(module.path,
                                                                                                       conf_file))

        return configuration_file

    @staticmethod
    def _instantiate_module(module_name, module_conf):
        """
        Method that will load device module and its configuration

        :type module_name: str
        :param module_name: Name of the module to instantiate (e.g.: "FlashModule")

        :type module_conf: dict
        :param module_conf: Configuration of the module as defined in the device catalog or bench config
        """
        try:
            module = DeviceModuleFactory._load_module(module_conf.class_name)
        except ImportError as exception:
            raise AcsConfigException("Cannot instantiate \"{0}\" module from \"{1}\": {2}".format(module_name,
                                                                                                  module_conf.class_name,
                                                                                                  exception))
        conf_path = DeviceModuleFactory._load_conf(module, module_conf.config)
        if conf_path:
            module.configuration_file = conf_path
        return module

    @staticmethod
    def _update_parameter(module, module_configuration, module_name):
        """
        Overload device parameter if device module conf was overloaded in bench config

        :type module: object
        :param module: module instance

        :type module_configuration: Attribute_dict
        :param module_configuration: Module configuration

        :type module_name: str
        :param module_name: name of the module
        """
        if module_configuration.get("parameter_overloaded"):
            # Overload module parameter
            for parameter_name, parameter_value in module_configuration.parameter_overloaded.items():
                if module.configuration.get(parameter_name) is not None:
                    # Overload parameter value
                    module.configuration[parameter_name] = parameter_value
                else:
                    # Parameter does not exist, raise the issue
                    raise AcsConfigException(AcsConfigException.INVALID_PARAMETER,
                                             "Device module parameter \"{0}\" is not define for device module \"{1}\""
                                             .format(parameter_name, module_name))

    @staticmethod
    def create(module_name, device, global_conf):
        """
        Create and return list of device module.

        :type module_name: str
        :param module_name: name of the module to be created

        :type device: py:class:`~acs.Device.Model.IDevice.py`
        :param module_name: device instance that request the module creation

        :type global_conf: dict
        :param global_conf: ACS global configuration

        :rtype: list of module
        """
        modules = []
        if device.config.device_modules and module_name in device.config.device_modules:
            module_configurations = device.config.device_modules[module_name]
            if not module_configurations:
                raise AcsConfigException("Cannot load \"{0}\" device module".format(module_name),
                                         "Cannot find module configuration.")
            for module_configuration in module_configurations:
                module = DeviceModuleFactory._instantiate_module(module_name, module_configuration)
                module.device = device
                module.logger = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, module_name.upper()))
                module.global_conf = global_conf
                module.name = module_name
                module.load_conf()
                DeviceModuleFactory._update_parameter(module, module_configuration, module_name)
                LOGGER_FWK.debug("Create Module '{0}' based on : {1}".format(module_name,
                                                                             module_configuration.class_name))
                LOGGER_FWK.debug("Module default parameters values are:")
                for key, value in module.configuration.items():
                    LOGGER_FWK.debug("\t {0}  : {1}".format(key, value))
                LOGGER_DEVICE_STATS.info(
                    "Create device_module={0}; device_module_class={1}; device_module_conf={2}".format(module_name,
                                                                                                       module_configuration.class_name,
                                                                                                       module_configuration.config))
                modules.append(module)
        return modules
