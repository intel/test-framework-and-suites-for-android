'''
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
'''
# import os
# import sys
import time
# import tempfile
# import random
# import math
import re
# import string
# import functools
# from PIL import Image
from testlib.util.log import Logger
# from testlib.util.process import shell_command, shell_command_ext
from testlib.util.common import g_common_obj
from testlib.util.config import TestConfig
from testlib.util.repo import Artifactory
# from testlib.graphics.tools import ConfigHandle
# from testlib.androidframework.common import EnvironmentUtils
# from testlib.graphics.compare_pic_impl import compare_pic
try:
    import pyqrcode
    import qrtools
except ImportError:
    pyqrcode = None
    qrtools = None


LOG = Logger.getlogger(__name__)
# EnvironmentUtils
ARTIFACTORY_ROOT = '/etc/oat/sys.conf'
VERSION_HISTORY = {
    '21': 'L',
    '22': 'L',
    '23': 'M',
    '24': 'N',
    '25': 'N',
    '26': 'O',  # O-MR0
    '27': 'O',  # O-MR1
    '28': 'P'
}
# WindowDisplayInfo
GET_WM_DENSITY = "wm density"
GET_WM_SIZE = "wm size"
DUMPSYS_CMD = "dumpsys display|grep DisplayDeviceInfo"
FULL_SCREEN_HINT = 'ImmersiveModeConfirmation'


class EnvironmentUtils(object):

    def get_android_version(self):
        """
        Get Android version:
        adb shell getprop | grep ro.build.version.sdk
        """
        cmd = 'getprop ro.build.version.sdk | grep -o [0-9]*'
        sdk_string = g_common_obj.adb_cmd_capture_msg(cmd)
        LOG.info("Android version is: %s" % VERSION_HISTORY[sdk_string])
        return VERSION_HISTORY[sdk_string]

    def get_resource_from_artifactory(self, conf_name, section, resource_name):
        # usage: get_resource_from_atifactory("tests.tablet.artifactory.conf", "content_picture", "wbmp")
        tc = TestConfig()
        arti_location = tc.getConfValue(ARTIFACTORY_ROOT, 'artifactory', 'location')
        resource_location = tc.getConfValue(conf_name, section, resource_name)
        return Artifactory(arti_location).get(resource_location)


environment_utils = EnvironmentUtils()


class PackageManager(object):

    def apk_install(self, file_path):
        SettingsCLI().set_key_value('global', 'package_verifier_enable', '0')
        SettingsCLI().set_key_value('secure', 'install_non_market_apps', '1')
        g_common_obj.adb_cmd_common('install -r -g %s' % file_path)
        time.sleep(10)

    def query_package_name(self, package_name):
        cmd = "pm list package | grep -I %s" % package_name
        msg = g_common_obj.adb_cmd_capture_msg(cmd)
        return True if package_name in msg else False


pkgmgr = PackageManager()


class SettingsCLI(object):

    def set_key_value(self, namespace, key, value):
        assert namespace in ['system', 'secure', 'global'],\
            "namespace is one of {system, secure, global}"

        cmd = 'settings get %s %s' % (namespace, key)
        output = g_common_obj.adb_cmd_capture_msg(cmd)
        assert output != 'null', 'Invalid key %s' % key

        cmd = 'settings put %s %s %s' % (namespace, key, value)
        output = g_common_obj.adb_cmd_capture_msg(cmd)

    def get_key_value(self, namespace, key):
        cmd = 'settings get %s %s' % (namespace, key)
        output = g_common_obj.adb_cmd_capture_msg(cmd)
        assert output != 'null', 'Invalid key %s' % key
        return output


class AdbImpl(object):

    def change_automatic_rotation(self, value=0):
        '''
        :param value: 0 to turn off auto rotation, 1 for turn it on.
        :return: None
        '''
        cmd = "content insert --uri content://settings/system\
         --bind name:s:accelerometer_rotation --bind value:i:%d" % value
        return g_common_obj.adb_cmd_capture_msg(cmd)

    def screen_rotation(self, value=0):
        '''
        :param value: 0 is default; 1 is 90 rotate; 2 is 180; 3 is -90.
        :return: None
        '''
        cmd = "content insert --uri content://settings/system\
         --bind name:s:user_rotation --bind value:i:%d" % value
        g_common_obj.adb_cmd_capture_msg(cmd)
        assert window_info.get_display_orientation() == int(value), "Display did not rotate."
        return True

    def unlock_screen(self):
        '''
        Unlock screen by via input keyevent 82
        :return: None
        '''
        print("Unlock screen via input keyevent 82")
        cmd = 'input keyevent 82; echo $?'
        return g_common_obj.adb_cmd_capture_msg(cmd).split('\r\n')


adb_impl = AdbImpl()


class WindowDisplayInfo(object):

    def __init__(self):
        self.device = g_common_obj

    def get_dumpsys_density(self):
        """
        run commands 'adb shell dumpsys display| grep DisplayDeviceInfo' to get dumpsys density,such as density 160
        """
        msg = g_common_obj.adb_cmd_capture_msg(repr(DUMPSYS_CMD))
        m = re.search(r'density\s*\w+', msg)
        if m is not None:
            dumpsys_density = int(m.group().strip().split(" ")[1])
        return dumpsys_density

    def get_wm_size(self):
        """
        run commands 'adb shell wm size' to get real size,e.g.:Physical size: 1080x1920
        """
        for _ in range(0, 3):
            density = g_common_obj.adb_cmd_capture_msg(repr(GET_WM_SIZE))
            if density.find("Override") == -1:
                break
            else:
                g_common_obj.adb_cmd_capture_msg("wm size reset")
        output = g_common_obj.adb_cmd_capture_msg(repr(GET_WM_SIZE))
        m = re.search(r'Physical size:\s*\d+x\d+', output)
        if m is not None:
            size = m.group().split(":")[1].strip()
            print(size)
        return size

    def get_wm_density(self):
        """
        run commands 'adb shell wm density' to get real density
        """
        for _ in range(0, 3):
            density = g_common_obj.adb_cmd_capture_msg(repr(GET_WM_DENSITY))
            if density.find("Override") == -1:
                break
            else:
                g_common_obj.adb_cmd_capture_msg("wm density reset")
        output = g_common_obj.adb_cmd_capture_msg(repr(GET_WM_DENSITY))
        m = re.search(r'Physical density:\s*\w+', output)
        if m is not None:
            density = int(m.group().split(":")[1].strip())
        return density

    def get_wm_width(self):
        size = self.get_wm_size()
        width = int(size.split("x")[0].strip())
        print(width)
        return width

    def get_wm_hight(self):
        size = self.get_wm_size()
        hight = int(size.split("x")[1].strip())
        print(hight)
        return hight

    def get_dumpsys_dpi(self):
        """
        run commands 'adb shell dumpsys display| grep DisplayDeviceInfo' to get dpi,such as 149.824 x 149.411 dpi
        """
        msg = g_common_obj.adb_cmd_capture_msg(repr(DUMPSYS_CMD))
        m = re.search(r'\w+.\w*\s*x\s*\w+.\w*\s*dpi', msg)
        if m is not None:
            dumpsys_dpi = m.group()
        return dumpsys_dpi

    def get_dumpsys_backlight(self):
        msg = g_common_obj.adb_cmd_capture_msg("dumpsys display |grep mActualBacklight")
        if msg is not None:
            actualBacklight = int(msg.split("=")[1].strip())
            print("[Debug] actualBacklight is %s" % actualBacklight)
            return actualBacklight

    def disable_fullscreen_hint(self):
        cmd = "dumpsys window|grep mCurrentFocus"
        strings = g_common_obj.adb_cmd_capture_msg(cmd)
        if FULL_SCREEN_HINT in strings:
            time.sleep(1)
            self.device.swipe(self.device.info['displayWidth'] / 2, 0,
                              self.device.info['displayWidth'] / 2, self.device.info['displayHeight'], steps=20)

    def get_current_focus_window(self):
        """get current activity focus window"""
        cmd = "dumpsys window|grep mCurrentFocus"
        pattern = r"(?P<PKG_NAME>[\w.]+)/(?P<ACT_NAME>[\w.]+)}"
        packagename, activityname = '', ''
        for _ in range(3):
            msg = g_common_obj.adb_cmd_capture_msg(cmd)
            match = re.search(pattern, msg)
            if not match:
                time.sleep(1)
                continue
            packagename = match.group('PKG_NAME')
            activityname = match.group('ACT_NAME')
            break
        return packagename, activityname

    def get_display_orientation(self, displayId=0):
        '''
        Get display orientation value.
        :param displayId: Specify display id, 0 is build-in screen, 1 is external display.
        :return: 0 is natural orientation(Portrait); 1 is landscape orientation; 2 is 180 degree; 3 is 270 degree.
        '''
        cmd = "dumpsys display | grep mBuiltInDisplayId=%s -B4 | head -n1 | cut -d\'=\' -f2" % displayId
        display_id_str = "Primary display" if displayId == 0 else "External display"
        display_mode = int(g_common_obj.adb_cmd_capture_msg(cmd))
        display_mode_str = ["Portrait", "landscape", "180 degree rotation", "270 degree rotation"][display_mode]
        LOG.debug("%s now is in %s mode." % (display_id_str, display_mode_str))
        return display_mode

    def get_layer_number(self):
        cmd = "dumpsys SurfaceFlinger | grep -io num.*Layers\=[0-9]* | cut -d '=' -f2"
        return g_common_obj.adb_cmd_capture_msg(cmd).splitlines()

    def check_dumpsys_SurfaceFlinger_info(self, matchCase=False, keyword=None, assertword=None):
        para = 'I' if matchCase else 'i'
        cmd = "dumpsys SurfaceFlinger | grep -%s '%s'" % (para, keyword)
        result = g_common_obj.adb_cmd_capture_msg(cmd)
        print("-----Get SurfaceFlinger info-----:\n %s" % result)
        return True if assertword in result else False


window_info = WindowDisplayInfo()
