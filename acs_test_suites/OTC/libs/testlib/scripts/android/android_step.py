#!/usr/bin/env python
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

from testlib.base.base_step import step as base_step
from testlib.base import base_utils
from testlib.utils.statics.android import statics
import datetime
from os.path import normpath
import __main__


class step(base_step):
    '''helper class for all android test steps'''

    def __init__(self, **kwargs):
        base_step.__init__(self, **kwargs)
        self.serial = None
        self.no_log = False

        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        if "platform" in kwargs:
            self.platform = kwargs["platform"]
        else:
            self.platform = None
        if "dessert" in kwargs:
            self.dessert = kwargs["dessert"]
        else:
            self.dessert = None
        if "no_log" in kwargs:
            self.no_log = kwargs["no_log"]

        # if self.no_log is True:
        #    self.device_info = None
        # else
        self.device_info = statics.Device(serial=self.serial, platform=self.platform, dessert=self.dessert)

        if self.serial not in self.passm:
            self.passm = self.passm.replace(" - [PASSED]", " [ {} ] - [PASSED]".format(self.serial))

        if self.serial not in self.errorm:
            self.errorm = self.errorm.replace(" - [FAILED]", " [ {} ] - [FAILED]".format(self.serial))

    def set_passm(self, pass_string):
        """
        Helps you customize pass message
        Example:
            step.set_passm("OK")
        """
        self.passm = "[ {0} ] ".format(self.serial) + \
            self.__class__.__name__ + " {0} - [PASSED]".format(pass_string)

    def set_errorm(self, particular_string, error_string):
        """
        Helps you customize error message
        Example:
            step.set_errorm("OK", "Pressing OK button failed")
        """
        self.errorm = "[ {0} ] ".format(self.serial) + \
            self.__class__.__name__ + " {0} - [FAILED] ".format(error_string)
        if particular_string == "":
            self.errorm = self.errorm + "-> {0}".format(particular_string)

    def log_error_info(self):
        # if no_log do nothing
        if self.no_log is True:
            return
        # save screenshot
        main_file = __main__.__file__.split('/')[-1]
        file_name = "{0}_{1}_{2}_{3}".format(datetime.datetime.now().time(),
                                             main_file,
                                             self.__class__.__name__,
                                             self.serial)
        prefix = normpath("/".join([self.testlib_log_path, file_name]))
        # save screenshot
        try:
            self.take_picture(prefix + ".png")
        except base_utils.DeviceNotFoundError, e:
            raise e
        except Exception:
            pass

        # call get_ui_dump
        self.get_ui_dump(file_name=prefix + ".xml")

        # save driver log
        try:
            self.get_driver_logs(prefix + ".drvlog")
        except Exception, e:
            pass
        # save dmesg
        try:
            self.get_failed_dmsg(prefix + ".dmsg")
        except Exception, e:
            pass

    def get_ui_dump(self, file_name):
        """
        Overwrite this method to take a screenshot in case of failed tests.
        """
        return None

    def take_picture(self, file_name):
        """
        Overwrite this method to take a screenshot in case of failed tests.
        """
        return None

    def get_driver_logs(self, file_name):
        """
        Overwrite this method to get driver logs in case of failed tests.
        """
        return None

    def get_failed_dmsg(self, file_name):
        """
        Overwrite this method to get driver logs in case of failed tests.
        """
        return None
