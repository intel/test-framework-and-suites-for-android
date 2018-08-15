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
import re
import math
import time
from testlib.util.common import g_common_obj
from testlib.graphics.common import window_info


class DisplayMetricsReportImpl(object):

    """ DisplayMetricsReportImpl """
    DUMPSYS_CMD = "dumpsys display|grep DisplayDeviceInfo"
    GET_SIZE = "wm size"
    GET_DENSITY = "wm density"
    density_range = [120, 160, 213, 240, 280, 320, 360, 400, 420, 480, 560, 640]
    flag = False

    def __init__(self):
        self.device = g_common_obj.get_device()

    def __get_dumpsys_size(self):
        """
        run commands 'adb shell dumpsys | grep DisplayDeviceInfo' to get dumpsys size,such as 1280 x 800
        """
        msg = g_common_obj.adb_cmd_capture_msg(repr(self.DUMPSYS_CMD))
        m = re.search(r'\d+\s*x\s*\d+', msg)
        dumpsys_size = m.group()
        return dumpsys_size

    def get_dumpsys_hight(self):
        dumpsys_size = self.__get_dumpsys_size()
        size_list = dumpsys_size.split(" ")
        if len(size_list) > 0:
            dumpsys_hight = int(size_list[0].strip())
            return dumpsys_hight
        else:
            assert len(size_list) > 0, "[FAILURE] dumpsys high is %s" % size_list

    def get_dumpsys_width(self):
        dumpsys_size = self.__get_dumpsys_size()
        size_list = dumpsys_size.split(" ")
        if len(size_list) > 0:
            dumpsys_width = int(size_list[2].strip())
            return dumpsys_width
        else:
            assert len(size_list) > 0, "[FAILURE] dumpsys width is %s" % size_list

    def __get_size(self):
        """
        run commands 'adb shell wm size ' to get real size
        """
        output = g_common_obj.adb_cmd_capture_msg(repr(self.GET_SIZE))
        m = re.search(r'Physical size:\s*\w+x\w+', output)
        size = m.group().split(":")[1].strip()
        return size

    def get_hight(self):
        size = self.__get_size()
        size_list = size.split("x")
        if len(size_list) > 0:
            height = int(size_list[0])
            return height
        else:
            assert len(size_list) > 0, "[FAILURE] size list is %s" % size_list

    def get_width(self):
        size = self.__get_size()
        size_list = size.split("x")
        if len(size_list) > 0:
            width = int(size_list[1])
            return width
        else:
            assert len(size_list) > 0, "[FAILURE] size list is %s" % size_list

    def compare_dumpsys_size_with_real_size(self):
        """
        compare dumpsys size with real size
        """
        dumpsys_hight = self.get_dumpsys_hight()
        hight = self.get_hight()
        dumpsys_width = self.get_dumpsys_width()
        width = self.get_width()
        print("[Debug] dumpsys_hight is %s,real height is %s" % (dumpsys_hight, hight))
        print("[Debug] dumpsys_width is %s,real width is %s" % (dumpsys_width, width))
        assert dumpsys_hight == hight and dumpsys_hight >= 600, \
            "[FAILURE] dumpsys hight is not equal to real hight:dumpsys hight is %d,real hight is %d"\
            % (dumpsys_hight, hight)
        assert dumpsys_width == width and dumpsys_width >= 600, \
            "[FAILURE] dumpsys width is not equal to  real width:dumpsys width is %d,real width is %d"\
            % (dumpsys_width, width)

    def compare_dumpsys_density_with_real_density(self):
        """
        compare dumpsys density with real density
        """
        dumpsys_density = window_info.get_dumpsys_density()
        density = window_info.get_wm_density()
        print("[Debug] dumpsys_density is %s,real density is %s" % (dumpsys_density, density))
        assert dumpsys_density == density and dumpsys_density > 0, \
            "[FAILURE] dumpsys density is not equal to  real density:dumpsys density is %d,real density is %d"\
            % (dumpsys_density, density)

    def judge_density_in_range(self):
        """
        judge if dumpsys density is in [120,160,213,240,280,320,360,400,480,560,640]
        """
        dumpsys_density = window_info.get_dumpsys_density()
        print("[Debug] dumpsys_density is %s,density range is %s" % (dumpsys_density, self.density_range))
        for i in range(0, int(len(self.density_range))):
            if dumpsys_density == int(self.density_range[i]):
                self.flag = True
                break
        assert self.flag, \
            "[FAILURE] dumpsys_density is not in density_range, dumpsys_density is %d" % dumpsys_density

    def judge_dpi(self):
        """
        judge if dumpsys density is closest to the dumpsys dpi,171.235 x 439.351 dpi
        """
        min = 0
        closest_density = 0
        dumpsys_dpi = window_info.get_dumpsys_dpi()
        dumpsys_dpi_x = float(dumpsys_dpi.split(" ")[0].strip())
        dumpsys_dpi_y = float(dumpsys_dpi.split(" ")[2].strip())
        dumpsys_hight = self.get_dumpsys_hight()
        dumpsys_width = self.get_dumpsys_width()
        denominator = math.sqrt((dumpsys_hight / dumpsys_dpi_x) ** 2 + (dumpsys_width / dumpsys_dpi_y) ** 2)
        numerator = math.sqrt(dumpsys_hight ** 2 + dumpsys_width ** 2)
        dumpsys_dpi = numerator / denominator
        print("dumpsys_dpi is %s" % dumpsys_dpi)
        dumpsys_density = window_info.get_dumpsys_density()
        for i in range(0, len(self.density_range)):
            if i == 0:
                min = abs(dumpsys_dpi - self.density_range[i])
            tmp = abs(dumpsys_dpi - self.density_range[i])
            if tmp <= min:
                min = tmp
                closest_density = self.density_range[i]
        print("[Debug] closest density is %s" % (closest_density))
        assert closest_density == dumpsys_density, \
            "[FAILURE]the dumpsys_density is not the closest to dumpsys dpi,the closest density is %s )"\
            % closest_density

    def compare_refresh_rate(self):
        msg = g_common_obj.adb_cmd_capture_msg(repr(self.DUMPSYS_CMD))
        m = re.search(r'\d+.\d+\s*fps', msg)
        if m is not None:
            refresh_rate = float(m.group().strip().split(" ")[0])
            diff = abs(refresh_rate - 60)
            print("[Debug] diff is %s" % diff)
            assert diff < 1, "[FAILURE] The value of string freshRate is %s ,greater(less) than 60." % refresh_rate

    def check_display(self):
        output = g_common_obj.adb_cmd_capture_msg("dumpsys window | grep mScreenOn")
        assert output.find("mScreenOnFully=false") != -1, "[FAILURE] Display is still on after time-out."
        print("[Debug] screen status is %s" % output)
        time.sleep(1)
        out = g_common_obj.adb_cmd_capture_msg("dumpsys display |grep mActualBacklight")
        if out is not None:
            actualBacklight = int(out.split("=")[1])
        print("[Debug] actual back light is %s" % actualBacklight)
        assert actualBacklight == 0, "[FAILURE] Device backlight not dim out after time-out."

    def calculate_screen_aspect_ratio(self):
        width = window_info.get_wm_width()
        hight = window_info.get_wm_hight()
        if width > hight:
            ratio = float(width) / hight
        else:
            ratio = float(hight) / width
        assert ratio > 1.3333 and ratio < 1.86,\
            "[FAILURE]The screen ratio is not right,it shold be between 1.3333 and 1.86,but now it is %s" % ratio

    def check_color_depth(self):
        output = g_common_obj.adb_cmd_capture_msg("dumpsys SurfaceFlinger | grep 'FB TARGET'")
        print("[Debug] FB TARGET is %s" % output)
        assert output.find("8888") != -1, "[FAILURE] The format of this layer is not BGRA_8888."


d_metricsreport_impl = DisplayMetricsReportImpl()
