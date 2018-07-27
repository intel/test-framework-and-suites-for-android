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
import os
import subprocess
import re
import signal
import shutil
import tempfile

from acs_test_scripts.UseCase.UseCaseBase import UseCaseBase
from acs.Core.Report.Live.LiveReporting import LiveReporting
from acs.UtilitiesFWK.Utilities import Global
from acs.Core.PathManager import Paths


class TimeoutError(Exception):
    """Exception to be thrown when action times out"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Testlib_UseCase(UseCaseBase):
    """
    Testlib usecase implementation
    """

    def __init__(self, tc_name, global_config):
        """
        Constructor
        """
        UseCaseBase.__init__(self, tc_name, global_config)
        self.except_log_files = ["placeholder.txt", "testlib_default.log"]

    def initialize(self):
        """
        Process the **<Initialize>** section of the XML file and execute defined test steps.
        """
        UseCaseBase.initialize(self)
        result, output = Global.SUCCESS, ""
        os.environ['uiautomator_jars_path'] = os.path.normpath(os.path.join(Paths.TEST_SCRIPTS, "Lib",
                                                                            "PythonUiautomator"))
        return result, output

    def __get_script_path(self, script_path):
        new_path = script_path
        if not os.path.exists(script_path):
            new_path = os.path.join(self._execution_config_path, script_path)

        if not os.path.exists(new_path):
            new_path = os.path.join(self._execution_config_path, os.path.dirname(self._name), script_path)

        if not os.path.exists(new_path):
            return Global.FAILURE, new_path
        else:
            return Global.SUCCESS, new_path

    def _run_process(self, test, serial, timeout, **kwargs):
        self.testlib_path = "/".join([Paths.TEST_SUITES, "OTC", "libs"])

        if "LOG_PATH" not in os.environ:
            os.environ['LOG_PATH'] = os.path.normpath(os.path.join(self.testlib_path, "testlib/logs"))

        if not os.path.exists(self.testlib_path):
            return Global.FAILURE, "TESTLIB PATH is not valid : %s" % self.testlib_path

        test_path = os.path.normpath(os.path.join(self.testlib_path, "testlib", test))

        # if the .py is not found, look for .pyc
        if not os.path.isfile(test_path):
            test_path = test_path + "c"
            if not os.path.isfile(test_path):
                return Global.FAILURE, "Cannot find %s" % test_path

        if "PYTHONPATH" in os.environ and os.environ['PYTHONPATH']:
            os.environ['PYTHONPATH'] = self.testlib_path + ":" + os.environ['PYTHONPATH']
        else:
            os.environ['PYTHONPATH'] = self.testlib_path
        # clean the log directory
        self.clean_testlib_logs()

        command = "python " + test_path + " --serial=" + serial
        for key, val in kwargs.iteritems():
            command += " --" + key.replace("_", "-") + " " + val if val else ""

        # This is to avoid when script-args is given with 'None' value or no value
        if not re.search('script-args', command):
            command += " --script-args None"

        command_list = command.split()
        for idx in range(len(command_list)):
            command_list[idx] = command_list[idx].replace("___", " ")
        # as mentioned below, the spaces in net_app_ssid were replaced with three underscores (net_ap_ssid =
        # net_ap_ssid.replace(" ", "___")) in order to prevent the name from being split and incorrectly introduced
        # in the command script args at this stage we reconstruct the command with script args so that ___ is
        # replaced back with white space
        subp = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
        self.output = ""
        self.error = ""

        def get_output(subp):
            with subp.stdout as o, subp.stderr as e:
                for line in iter(o.readline, b''):
                    self.output += line
                    print line,
                for line in iter(e.readline, b''):
                    self.error += line
                    print line,
            subp.wait()

        def handler(signum, frame):
            raise TimeoutError("timeout reached")

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(timeout)

        try:
            get_output(subp)
        except TimeoutError:
            self.output += "raise TimeoutError('Test timed out before {0} seconds')".format(timeout)
            self._logger.debug("Test timed out before {0} seconds".format(timeout))
            try:
                os.kill(subp.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                self._logger.debug("Killed testlib process due to timeout")
            except OSError:
                self._logger.debug("Testlib process already killed")

        signal.alarm(0)
        return self.output, self.error

    def clean_testlib_logs(self):
        folder = os.path.normpath(self.testlib_path + "/testlib/logs/")
        shutil.rmtree(folder, ignore_errors=True)

    def upload_testlib_logs(self):
        folder = os.path.normpath(self.testlib_path + "/testlib/logs/")
        try:
            zipfile = shutil.make_archive(tempfile.mktemp(), "zip", folder)
            lr = LiveReporting.instance()
            lr.send_test_case_resource(zipfile, display_name="logs")
            os.unlink(zipfile)
        except Exception:
            pass

    def _parse_file_for_resolution(self, output, error):

        if output == Global.FAILURE:
            self._logger.error(error)
            return Global.BLOCKED
        if "raise TimeoutError(" in output:
            return Global.BLOCKED
        if "raise BlockingError(" in output:
            return Global.BLOCKED
        if "[FAILED]" in output or 'raise FailedError(' in error:
            return Global.FAILURE
        if error:
            return Global.BLOCKED
        return Global.SUCCESS

    def run_test(self):
        UseCaseBase.run_test(self)

        test = self._tc_parameters.get_param_value("test")

        serial = self._device.retrieve_serial_number()

        adb_server_port = self._tc_parameters.get_param_value("adb-server-port", default_value=None)
        adb_local_port = self._tc_parameters.get_param_value("adb-local-port", default_value=None)
        script_args = self._tc_parameters.get_param_value("script-args", default_value=None)

        # Set Parameters specific to PHONE1 from benchConfig to script-args
        phone_number, sim_pin, wrong_pin, puk_code, carrier_name, voicemail_number = (None,) * 6

        # Updating few bench config values as a envrionmental values to use
        # inside the workflow
        google_account_email_id = self._device.get_config(
            "GoogleAccountEmailId")
        google_account_password = self._device.get_config(
            "GoogleAccountPassword")

        if google_account_email_id and google_account_password:
            os.environ.update({"GOOGLE_ACCOUNT_EMAIL_ID": google_account_email_id,
                               "GOOGLE_ACCOUNT_PASSWORD": google_account_password})

        try:
            phone_number = self._global_conf.deviceConfig['PHONE1'].phoneNumber
        except Exception:
            pass
        if phone_number:
            if not script_args:
                script_args = "number={0}".format(phone_number)
            else:
                script_args += " number={0}".format(phone_number)

        try:
            sim_pin = self._global_conf.deviceConfig['PHONE1'].simPin
        except Exception:
            pass
        if sim_pin:
            if not script_args:
                script_args = "sim_pin={0}".format(sim_pin)
            else:
                script_args += " sim_pin={0}".format(sim_pin)

        try:
            wrong_pin = self._global_conf.deviceConfig['PHONE1'].wrongPin
        except Exception:
            pass
        if wrong_pin:
            if not script_args:
                script_args = "wrong_pin={0}".format(wrong_pin)
            else:
                script_args += " wrong_pin={0}".format(wrong_pin)

        try:
            puk_code = self._global_conf.deviceConfig['PHONE1'].pukCode
        except Exception:
            pass
        if puk_code:
            if not script_args:
                script_args = "puk_code={0}".format(puk_code)
            else:
                script_args += " puk_code={0}".format(puk_code)

        try:
            carrier_name = self._global_conf.deviceConfig['PHONE1'].carrierName
        except Exception:
            pass
        if carrier_name:
            if not script_args:
                script_args = "carrier_name={0}".format(carrier_name)
            else:
                script_args += " carrier_name={0}".format(carrier_name)

        try:
            voicemail_number = self._global_conf.deviceConfig['PHONE1'].voiceMailNumber
        except Exception:
            pass
        if voicemail_number:
            if not script_args:
                script_args = "voicemail_number={0}".format(voicemail_number)
            else:
                script_args += " voicemail_number={0}".format(voicemail_number)

        # ---------------------------------------------------------------------

        serial2 = None
        # save the serialNumber if it is defined
        try:
            serial2 = self._global_conf.deviceConfig['PHONE2'].serialNumber

        except Exception:
            # the parameter is not defined; it will remain set to None
            pass

        if serial2 is not None and serial2 != "":
            if script_args is None:
                script_args = "serial2={0}".format(serial2)
            else:
                script_args += " serial2={0}".format(serial2)

        # ---------------------------------------------------------------------

        serial3 = None
        # save the serialNumber if it is defined
        try:
            serial3 = self._global_conf.deviceConfig['PHONE3'].serialNumber

        except Exception:
            # the parameter is not defined; it will remain set to None
            pass

        if serial3 is not None and serial3 != "":
            if script_args is None:
                script_args = "serial3={0}".format(serial3)
            else:
                script_args += " serial3={0}".format(serial3)

        # ---------------------------------------------------------------------

        serial4 = None
        # save the serialNumber if it is defined
        try:
            serial4 = self._global_conf.deviceConfig['PHONE4'].serialNumber

        except Exception:
            # the parameter is not defined; it will remain set to None
            pass

        if serial4 is not None and serial4 != "":
            if script_args is None:
                script_args = "serial4={0}".format(serial4)
            else:
                script_args += " serial4={0}".format(serial4)

        media_path = self._tc_parameters.get_param_value("media-path",
                                                         default_value=None)
        apks = self._tc_parameters.get_param_value("apks",
                                                   default_value=None)

        timeout = self._tc_parameters.get_param_value("timeout", default_value=1800, default_cast_type=int)
        wifi_ap_name = self._device.get_config("WiFi_Support_Ap_Name")

        if wifi_ap_name is not None:
            # Updating few bench config values as a envrionmental values to use
            # inside the workflow
            os.environ.update({"WIFI_CONFIGURABLE_AP_SSID": wifi_ap_name})
            if script_args is not None:
                # replace the given ap_name if it exists in script_args
                if "ap_name" in script_args:
                    script_args = re.sub(r"ap_name=[-\w]+", r"ap_name=" + wifi_ap_name, script_args)
                else:
                    script_args += " ap_name=" + wifi_ap_name
            # else:
                # script_args = "ap_name=" + wifi_ap_name

        # get the access point from bench config (ip and user name)
        ap_type = None
        ap_ip = None
        ap_username = None
        try:
            self._configurable_ap = self._em.get_computer("AccessPoint")
        except Exception:
            self._logger.warning("Invalid parameter for AccessPoint in Bench Config. Please update the AP Equipment "
                                 "name with: name='AccessPoint' and add the type of the AP 'ddwrt_atheros' or "
                                 "'ddwrt_broadcom'")
        try:
            ap_type = self._global_conf.benchConfig.get_parameters("AccessPoint").get_dict()["type"]["value"]
        except Exception:
            self._logger.warning("'type' parameter missing for 'AccessPoint. Please update the AP Equipment with: "
                                 "parameter 'type' with 'value' 'ddwrt_atheros' or 'ddwrt_broadcom'")

        try:
            ap_ip = self._global_conf.benchConfig.get_parameters("AccessPoint").get_dict()["IP"]["value"]
            ap_username = self._global_conf.benchConfig.get_parameters("AccessPoint").get_dict()["username"]["value"]
        except Exception:
            self._logger.warning("'IP' or 'username' parameter missing for 'AccessPoint. Please update the AP "
                                 "Equipment with: parameter 'IP' with '192.168.1.1' or something similar, "
                                 "parameter 'username' with the user name")

        # add ap_type to script_args as ap_module
        if ap_type is not None:
            if ap_type == "ddwrt_broadcom":
                ap_type = "ddwrt"
                # Updating few bench config values as a envrionmental values to use
                # inside the workflow
                os.environ.update({"ACCESS_POINT_TYPE": ap_type})
            if script_args is not None:
                if "ap_module" in script_args:
                    # replace the value
                    script_args = re.sub(r"ap_module=[-\w]+", r"ap_module=" + ap_type, script_args)
                else:
                    script_args += " ap_module={0}".format(ap_type)
            else:
                script_args = "ap_module={0}".format(ap_type)

        # add ap_ip to script_args
        if ap_ip is not None:
            if script_args is not None:
                if "ap_ip" in script_args:
                    # replace the value
                    script_args = re.sub(r"ap_ip=[\d\.]+", r"ap_ip=" + ap_ip, script_args)
                else:
                    script_args += " ap_ip={0}".format(ap_ip)
            else:
                script_args = "ap_ip={0}".format(ap_ip)

        # add ap_username to script_args
        if ap_username is not None:
            if script_args is not None:
                if "ap_username" in script_args:
                    # replace the value
                    script_args = re.sub(r"ap_username=[-\w]+", r"ap_username=" + ap_username, script_args)
                else:
                    script_args += " ap_username={0}".format(ap_username)
            else:
                script_args = "ap_username={0}".format(ap_username)

        # Updating few bench config values as a envrionmental values to use
        # inside the workflow
        if ap_ip and ap_username:
            os.environ.update({"ACCESS_POINT_IP": ap_ip, "ACCESS_POINT_USER_NAME": ap_username})

        # get the Internet Connected AP name & password from bench config
        net_ap_ssid = self._device.get_config("WiFi_Connection_Ap_Name")
        net_ap_password = self._device.get_config("WiFi_Connection_Passwd")
        net_ap_security = self._device.get_config("WiFi_Connection_Security_Mode")
        wv_toolbox = self._device.get_config("WV_Tool_Box")
        wv_keybox = self._device.get_config("WV_Key_Box")
        android_build_top = self._device.get_config("Android_Build_Top")
        boot_img = self._device.get_config("Boot_Img")

        if net_ap_ssid:
            # replace the given ap_name if it exists in script_args
            net_ap_ssid = net_ap_ssid.replace(" ", "___")
            # by default, when the SSID contains white spaces, it is split into composing words,
            # and only the 1st one is passed to script args, which breaks the configuration
            # therefore, we temporarily replace spaces with three underscores

            # Updating few bench config values as a envrionmental values to use
            # inside the workflow
            if net_ap_password:
                os.environ.update({"WIFI_CONNECTION_AP_SSID": net_ap_ssid,
                                   "WIFI_CONNECTION_PASSWORD": net_ap_password})
            if net_ap_security:
                os.environ.update({"WIFI_CONNECTION_SECURITY": net_ap_security})

            if script_args:
                if "net_ap_ssid" in script_args:
                    script_args = re.sub(r"net_ap_ssid=[-\w]+", r"net_ap_ssid={}".format(net_ap_ssid), script_args)
                else:
                    script_args += " net_ap_ssid=" + net_ap_ssid + "  "
            else:
                script_args = " net_ap_ssid=" + net_ap_ssid + "  "

            if net_ap_password:
                if script_args:
                    if "net_ap_password" in script_args:
                        # replace the given passphrase if it exists in script_args
                        script_args = re.sub(r"net_ap_password=[.^\s]+", r"net_ap_password=" + net_ap_password,
                                             script_args)
                    else:
                        script_args += " net_ap_password=" + net_ap_password
                else:
                    script_args = " net_ap_password=" + net_ap_password
            if net_ap_security:
                if script_args:
                    if "net_ap_security" in script_args:
                        # replace the given security mode if it exists in script_args
                        script_args = re.sub(r"net_ap_security=[-\w]+", r"net_ap_security=" + net_ap_security,
                                             script_args)
                    else:
                        script_args += " net_ap_security=" + net_ap_security + " "
                else:
                    script_args = " net_ap_security=" + net_ap_security + " "

        if wv_toolbox:
            # replace the given wv_toolbox if it exists in script_args
            wv_toolbox = wv_toolbox.replace(" ", "___")
            if script_args:
                if "wv_toolbox" in script_args:
                    script_args = re.sub(r"wv_toolbox=[-\w]+", r"wv_toolbox={}".format(wv_toolbox), script_args)
                else:
                    script_args += " wv_toolbox=" + wv_toolbox + "  "
            else:
                script_args = " wv_toolbox=" + wv_toolbox + "  "

            if wv_keybox:
                if script_args:
                    if "wv_keybox" in script_args:
                        # replace the given wv_keybox if it exists in script_args
                        script_args = re.sub(r"wv_keybox=[.^\s]+", r"wv_keybox=" + wv_keybox, script_args)
                    else:
                        script_args += " wv_keybox=" + wv_keybox
                else:
                    script_args = " wv_keybox=" + wv_keybox

        if android_build_top:
            # replace the given android_build_top if it exists in script_args
            android_build_top = android_build_top.replace(" ", "___")
            if script_args:
                if "android_build_top" in script_args:
                    script_args = re.sub(r"android_build_top=[-\w]+", r"android_build_top={}".format(
                        android_build_top), script_args)
                else:
                    script_args += " android_build_top=" + android_build_top + "  "
            else:
                script_args = " android_build_top=" + android_build_top + "  "

        if boot_img:
            # replace the given boot_img if it exists in script_args
            boot_img = boot_img.replace(" ", "___")
            if script_args:
                if "boot_img" in script_args:
                    script_args = re.sub(r"boot_img=[-\w]+", r"boot_img={}".format(boot_img), script_args)
                else:
                    script_args += " boot_img=" + boot_img + "  "
            else:
                script_args = " boot_img=" + boot_img + "  "

        # check if there is an "Equipment" named "RELAY"
        self._relay = None
        try:
            self._relay = self._global_conf.benchConfig.get_parameters("RELAY")
        except Exception:
            try:
                self._relay = self._global_conf.benchConfig.get_parameters("IO_CARD")
            except Exception:
                pass
        script_args_to_add = ""
        if self._relay:
            # get all existing attributes of the relay
            relay_attributes = self._relay.get_dict()
            if "Model" in relay_attributes:
                script_args_to_add += "relay_type={} ".format(relay_attributes["Model"]["value"])
            if "ComPort" in relay_attributes:
                script_args_to_add += "relay_port={} ".format(relay_attributes["ComPort"]["value"])
            if "SwitchOnOff" in relay_attributes:
                script_args_to_add += "power_port={} ".format(relay_attributes["SwitchOnOff"]["value"])
            if "VolumeUp" in relay_attributes:
                script_args_to_add += "v_up_port={} ".format(relay_attributes["VolumeUp"]["value"])
            if "VolumeDown" in relay_attributes:
                script_args_to_add += "v_down_port={} ".format(relay_attributes["VolumeDown"]["value"])
            if "USBVCCut" in relay_attributes:
                script_args_to_add += "USB_VC_cut={} ".format(relay_attributes["USBVCCut"]["value"])

            script_args_to_add += "flash_files={}".format(Paths.FLASH_FILES)

            if script_args_to_add != "":
                if not script_args:
                    script_args = ""
                script_args += " " + script_args_to_add

        ui_handlers_group = self._device.get_config("UI_Handlers_Group", default_value=None)
        if ui_handlers_group:
            os.environ['TESTLIB_UI_HANDLERS_GROUP'] = ui_handlers_group

        # create process for each test
        output, error = self._run_process(test,
                                          serial,
                                          adb_server_port=adb_server_port,
                                          adb_local_port=adb_local_port,
                                          script_args=script_args,
                                          media_path=media_path,
                                          apks=apks,
                                          timeout=timeout)
        # start the process
        result = self._parse_file_for_resolution(output, error)

        if result != Global.SUCCESS:
            self.upload_testlib_logs()

        return result, str(output) + " " + str(error)
