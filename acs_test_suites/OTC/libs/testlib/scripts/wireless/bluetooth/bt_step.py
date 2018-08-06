# !/usr/bin/env python

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

#######################################################################
#  @description: Bluetooth base step
#  @author:      adrian.palko@intel.com
#######################################################################
import os
import time

from testlib.scripts.android.adb.adb_step import step as adb_step
from testlib.utils.connections.adb import Adb as connection_adb
from uiautomator import Device, Adb


#  Bt step now inherit from adb_step and follow similar workflow as other
#  domains
class Step(adb_step):
    """
        Description:
            Base class for all bluetooth test steps
    """

    def __init__(self, **kwargs):

        adb_step.__init__(self, **kwargs)

        #  parse kwargs
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
        else:
            self.timeout = 10000
        if "serial" in kwargs:
            self.serial = kwargs["serial"]
        else:
            self.serial = None
        if "no_log" in kwargs:
            self.no_log = kwargs["no_log"]
        else:
            self.no_log = False

        #  constants for pass and error messages
        if self.serial:
            self._PASSM = "[ {} ] ".format(self.serial) + self.__class__.__name__ + " - [PASSED]"
            self._ERRORM = "[ {} ] ".format(self.serial) + self.__class__.__name__ + " - [FAILED]"
        else:
            self._PASSM = self.__class__.__name__ + " - [PASSED]"
            self._ERRORM = self.__class__.__name__ + " - [FAILED]"

        #  defaults pass and error messages
        self.passm = self._PASSM
        self.errorm = self._ERRORM

        #  replacing old uidevice available in testlib/external with standard
        #   uiautomator device class
        self.uidevice = Device(serial=self.serial)

        #  initialize adb connection with below to have backward compatibility
        self.adb_connection = Adb(serial=self.serial)

        #  Add Common ADB API to use instead of above hereafter
        self.adb_connection_common = connection_adb(**kwargs)

        if "version" in kwargs:
            self.version = kwargs["version"]
        else:
            self.version = self.adb_connection_common.get_prop('ro.build.version.release')

    def set_passm(self, pass_string):
        """
            Description:
                Helps you customize pass message
            Usage:
                BtStep.set_passm("BT switch turned on")
            :param pass_string: custom pass message
        """
        self.passm = self._PASSM + " {}".format(pass_string)

    def set_errorm(self, particular_string, error_string):
        """
            Description:
                Helps you customize error message
            Usage:
                BtStep.set_errorm("OFF", "Turning off BT failed")
            :param particular_string: additional error message
            :param error_string: custom error message
        """
        self.errorm = self._ERRORM + " {} -> {}".format(
            particular_string, error_string)

    def log_error_info(self):
        """
            Description:
                Save test artifacts when test fails
        """

        if self.no_log is False:
            try:
                #  construct name of file and take screenshot
                if self.serial:
                    serial_name = "_{}".format(self.serial)
                else:
                    serial_name = ""
                base = "%s_%s%s" % (time.strftime("%y-%m-%d_%h:%m:%s"),
                                    self.__class__.__name__, serial_name)
                screenshot_name = os.path.join(self.testlib_log_path,
                                               base + ".png")
                self.take_picture(screenshot_name)
                dump_file = os.path.join(self.testlib_log_path, base + ".uix")
                with open(dump_file, "w") as fp:
                    buf = self.uidevice.dump()
                    fp.write(buf.encode("UTF-8", errors="ignore"))
            except Exception, e:
                info_message = "Could not get screenshot: {}".format(e.message)
                if self.serial:
                    info_message = ("[ {} ] " + info_message).format(self.serial)
                self.logger.info(info_message)

    def take_picture(self, file_name):
        """
            Description:
                Take a screenshot with the provided file_name
            Usage:
                self.take_picture("Screenshot.png")
            :param file_name: path of file to be saved
        """
        self.uidevice.screenshot(file_name)
