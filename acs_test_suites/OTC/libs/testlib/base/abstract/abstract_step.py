#!/usr/bin/env python
##
"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?
SPDX-License-Identifier: Apache-2.0
"""
##

##############################################################################
#
# @filename:    abstract_step.py
# @description: Defines the decorator class to implement the astract step
# @author:      aurel.constantin@intel.com
#
##############################################################################

import os
import inspect
from functools import wraps

from testlib.base.abstract import abstract_utils
from testlib.base import base_utils
from testlib.utils.statics.android.statics import get_dessert, get_device_type
from testlib.utils import logger


class abstract_step(object):
    __metaclass__ = base_utils.SingletonType

    def __init__(self, use_module):
        self.target_module = abstract_utils.import_module(use_module)

    def __call__(self, original_class):
        return abstract_utils.get_obj(self.target_module, original_class.__name__)


log = None
if "LOG_PATH" in os.environ:
    testlib_log_path = os.environ["LOG_PATH"]
else:
    import testlib
    testlib_log_path = os.path.dirname(testlib.__file__) + "/logs/"

log = logger.testlib_log(log_path=testlib_log_path, log_name="testlib_default")


class DeviceDecorator(object):
    # __metaclass__ = base_utils.SingletonType

    def __init__(self, obj):
        # Todo need to copy docstring, module and class/function names to
        # decorator
        self.obj = obj
        if inspect.isclass(self.obj):
            # print "class decorated"
            self.obj_name = self.obj.__name__
            self.obj_module = self.obj.__dict__["__module__"]
            self.obj_type = "class"
        elif inspect.isfunction(self.obj):
            # print "function decorated"
            self.obj_name = self.obj.func_name
            self.obj_module = self.obj.func_globals["__name__"]
            self.obj_type = "function"
        else:
            log.error("Unsupported object type")
            raise TypeError

    def __call__(self, *args, **kwargs):
        # print 'calling obj {name} with arguments {args} {kwargs}'.format(name=self.obj_name, args=args,
        # kwargs=kwargs)
        try:
            serial = kwargs["serial"]
        except KeyError:
            log.error("Serial number is missing in the arguments")
            raise KeyError

        dessert = get_dessert(serial)
        if dessert > "O":
            device_type = get_device_type(serial)
            device_name = device_type + "_" + dessert
        else:
            device_name = "automotive_O"
        module_path = ".".join(self.obj_module.split(".")[:-1])
        module_path = ".".join([module_path, device_name])
        module_path = ".".join(
            [module_path, self.obj_module.split(".")[-1:][0]])

        target_module = abstract_utils.import_module_from_path(module_path)
        if self.obj_type == "class":
            return abstract_utils.get_obj(target_module, self.obj_name)(*args, **kwargs)
        else:
            return abstract_utils.get_obj(target_module, self.obj_name, obj_type="function")(*args, **kwargs)


def inherite(argument):
    # Todo, need to check and raise Exception when used to inherite other than object of type 'function'
    # Todo, need to check called funciton body. If contains any code, inheritance should happen and should follow same
    # overide mechanism as class

    def real_decorator(function):
        @wraps(argument)
        def wrapper(*args, **kwargs):
            retval = argument(*args, **kwargs)
            return retval
        return wrapper
    return real_decorator


def applicable(*argument):
    # Todo need to copy docstring, module and class/function names to decorator
    def real_decorator(function_):
        # @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                serial = kwargs["serial"]
            except KeyError:
                log.error("Serial number is missing in the arguments")
                raise KeyError

            dessert = get_dessert(serial)
            device_type = get_device_type(serial)
            device_name = device_type + "_" + dessert

            if not any((True for id in argument if id in [dessert, device_type, device_name])):
                log.error("API is applicable only for {} and not applicable for {}".
                          format(argument, [dessert, device_type, device_name]))
                raise Exception
            retval = function_(*args, **kwargs)
            return retval
        return wrapper
    return real_decorator


def not_applicable(*argument):
    # Todo need to copy docstring, module and class/function names to decorator
    def real_decorator(function_):
        # @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                serial = kwargs["serial"]
            except KeyError:
                log.error("Serial number is missing in the arguments")
                raise KeyError

            dessert = get_dessert(serial)
            device_type = get_device_type(serial)
            device_name = device_type + "_" + dessert

            if any((True for id in argument if id in [dessert, device_type, device_name])):
                log.error("API is not applicable for {}".format(argument))
                raise Exception
            retval = function_(*args, **kwargs)
            return retval
        return wrapper
    return real_decorator


devicedecorator = DeviceDecorator
notapplicable = not_applicable
