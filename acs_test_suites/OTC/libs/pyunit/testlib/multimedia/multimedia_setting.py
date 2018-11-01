# coding: UTF-8
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
import os
import time
import subprocess
import thread
from testlib.util.common import g_common_obj
from testlib.util.repo import Artifactory
from testlib.util.config import TestConfig
from testlib.systemui.systemui_impl import SystemUI
from testlib.util.otc_image import otcImage
from testlib.multimedia.multimedia_log import MultimediaLogger
logger = MultimediaLogger.instance()

PHOTOS_PACKAGE_NAME = "com.google.android.apps.photos"
PHOTOS_ACTIVITY_NAME = ".home.HomeActivity"

d = g_common_obj.get_device()
x = d.info["displayWidth"]
y = d.info["displayHeight"]


def download_file(url, name):
    if "http" not in url and "ftp" not in url:
        file_path = os.path.join(url, name)
        file_path = file_path.replace("%20", " ")
        assert os.path.exists(file_path), "resource file not exist! path=%s" % file_path
        ret_file = file_path
    else:
        ret_file = Artifactory(url).get(name)
    if os.path.exists(ret_file):
        print "[Download]: Artifactory method"
        return ret_file
    assert 0, "Download filed!"


def download_content_with_wget(url, app_name):
    for _ in range(10):
        if os.path.isfile(app_name):
            print "%s exists" % app_name
            break
        cmd = "wget -c " + url + app_name
        os.system(cmd)
    assert os.path.isfile(app_name)


def verify_apps(package_name):
    result = g_common_obj.adb_cmd_common("shell pm list package | grep %s" % (package_name))
    if "package:%s\r\n" % package_name in result or result.endswith("package:%s" % package_name):
        print "%s app has been installed" % package_name
        return 1
    else:
        return 0


def install_verify_apps(apk_name, package_name, times=10):
    for _ in range(10):
        time.sleep(2)
        if verify_apps(package_name) == 1:
            return
        else:
            install_success_flag = 0

            def click_accept_button():
                device = g_common_obj.get_device()
                for i in range(10):
                    time.sleep(2)
                    if install_success_flag == 1:
                        return
                    elif device(textContains="Accept").exists:
                        device(textContains="Accept").click.wait()
                        return
            thread.start_new_thread(click_accept_button, ())
            g_common_obj.adb_cmd_common('install -r %s' % (apk_name))
            install_success_flag = 1


def setTimeToSec(time):
        time = time.split(":")
        i = 1
        temp = 0
        for s in time[::-1]:
            temp += int(s) * i
            i *= 60
        return int(temp)


def checkIputMethod():
    get_InputMethod_status_cmd = "shell dumpsys SurfaceFlinger | grep '| InputMethod'"
    input_method_status = g_common_obj.adb_cmd_common(get_InputMethod_status_cmd)
    return input_method_status


def clickScreen():
    logger.debug("Click screen center")
    orientation = d.orientation
    logger.debug("orientation=%s, x=%s, y=%s" % (orientation, x, y))
    if (orientation == "natural" or orientation == "upsidedown"):
        logger.debug("click (%s,%s)" % (x / 2, y / 2))
        d.click(x / 2, y / 2)
    else:
        logger.debug("click (%s,%s)" % (y / 2, x / 2))
        d.click(y / 2, x / 2)


def check_path_exist_in_dut(path):
    t_resut = execute_adb_command("shell ls %s" % path)
    logger.debug("check %s exist: %s" % (path, "No such file or directory" not in t_resut))
    return 0 if "No such file or directory" in t_resut else 1


def mkdirs_in_dut(path):
    if check_path_exist_in_dut(path):
        return
    mkdirs_in_dut(os.path.split(path)[0])
    execute_adb_command("shell mkdir %s" % path)
    assert check_path_exist_in_dut(path), " failed! path=%s" % path
    return True


def move_dut_file_path(original_path='', target_path=''):
    assert "No such file or directory" not in execute_adb_command("shell ls %s" % original_path), "file not exists!"
    if mkdirs_in_dut(target_path):
        logger.debug("target path exists")
    result = execute_adb_command("shell mv %s %s" % (original_path, target_path))
    assert "No such file or directory" not in result, "move file path failed"
    return target_path + original_path


def execute_adb_command(cmd):
    tmp_cmd = 'adb ' + cmd
    logger.debug("Execute command: {0}".format(tmp_cmd))
    tmp_process = subprocess.Popen(tmp_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    out, err = tmp_process.communicate()
    return out.strip()


class MultiMediaSetting:
    """
    Multi-media setting.
    """

    config = TestConfig()
    HOME_PACKAGE_NAME = "com.android.car.dialer"
    HOME_ACTIVITY_NAME = ".TelecomActivity"

    def __init__(self, config_file):
        self.config_file = config_file
        self.d = g_common_obj.get_device()
        self.x = self.d.info["displayWidth"]
        self.y = self.d.info["displayHeight"]
        resource_file_path = self.config.read(self.config_file, "config_path").get("resource_file_path")
        self.resource_file_path = self.config.read(resource_file_path, "artifactory").get("location")
        self.available_apk_dict = {}
        self.tag = 'MultiMediaSetting '

        if self.d(textContains="Drive safely").exists:
            logger.debug(self.tag + "Drive saftely exist , click owner")
            self.d(text="Owner").click()
            time.sleep(3)

    def get_main_path(self, config_path):
        return self.resource_file_path

    def get_package_and_activity_name(self, apk_name):
        apk_path_config = self.config.read(self.config_file, apk_name)
        return apk_path_config.get("package_name"), apk_path_config.get("activity_name")

    def install_apk(self, apk_name, times=5):
        apk_path_config = self.config.read(self.config_file, apk_name)
        if verify_apps(apk_path_config.get("package_name")) == 1:
            return False
        else:
            env_path = os.environ.get('TEST_DATA_ROOT')
            filepath = os.path.join(env_path, "app/", apk_path_config.get("file_name"))
            install_verify_apps(filepath, apk_path_config.get("package_name"), times)
            return True

    def launch_apk(self, apk_name):
        if apk_name not in self.available_apk_dict.keys():
            package_name, activity_name = self.get_package_and_activity_name(apk_name)
            assert package_name is not None and activity_name is not None, \
                "Can't find package or activity name! apk_name=%s, package_name=%s, activity_name=%s" \
                % (apk_name, package_name, activity_name)
            self.available_apk_dict[apk_name] = (package_name, activity_name)
        package_name, activity_name = self.available_apk_dict[apk_name]
        return g_common_obj.launch_app_am(package_name, activity_name)

    def stop_apk(self, apk_name):
        if apk_name not in self.available_apk_dict.keys():
            self.available_apk_dict[apk_name] = (self.get_package_and_activity_name(apk_name))
        package_name, _ = self.available_apk_dict[apk_name]
        return g_common_obj.stop_app_am(package_name)

    def push_file(self, cmd, datapath):
        if "http" not in datapath and "ftp" not in datapath:
            datapath = self.resource_file_path + datapath
        file_name = cmd.split("/")[-1].replace("\"", "")
        push_path = cmd.split("\" \"")[1].replace("\"", "")
        print push_path
        if "/storage/sdcard1" in push_path:
            mount_point = self.get_mount_point()
            print mount_point
            assert mount_point, "can not find SD card"
            if mount_point != "/storage/sdcard1":
                push_path = push_path.replace("/storage/sdcard1", mount_point)
                logger.debug(self.tag + "push path is : " + push_path)
        if "http" not in datapath and "ftp" not in datapath:
            file_path = os.path.join(datapath, file_name)
            file_path = file_path.replace("%20", " ")
            assert os.path.exists(file_path), "resource file not exist! path=%s" % file_path
            ret_file = file_path
        else:
            logger.debug("Start to download file... datapath=%s, file_name=%s" % (datapath, file_name))
            ret_file = Artifactory(datapath).get(file_name)
            logger.debug("Complete to download file!!!")
        if os.path.exists(ret_file):
            print "[Download]: Artifactory method"
            push_cmd = r"push '{0}' '{1}'".format(ret_file, push_path)
            self.execute_adb_command(push_cmd)
            return push_path
        else:
            assert 0, "Download filed!"

    def execute_adb_command(self, cmd):
        return execute_adb_command(cmd)

    def download_file_to_host(self, src_path):
        if "http" not in src_path and "ftp" not in src_path:
            src_path = self.resource_file_path + src_path
        if "http" not in src_path and "ftp" not in src_path:
            src_path = src_path.replace("%20", " ")
            assert os.path.exists(src_path), "resource file not exist! path=%s" % src_path
            ret_file = src_path
        else:
            src_head, src_name = os.path.split(src_path)
            logger.debug("Start to download file... src_path=%s" % src_path)
            ret_file = Artifactory(src_head).get(src_name)
            assert ret_file is not None and os.path.exists(ret_file), \
                "Download filed! ret_file=%s, src_path=%s" % (ret_file, src_path)
            logger.debug("Download success! ret_file=%s" % ret_file)
        return ret_file

    def push_file_to_dut(self, src_path, dst_path):
        logger.debug("push_file_to_dut--- dst_path=%s" % dst_path)
        if "/storage/sdcard1" in dst_path:
            mount_point = self.get_mount_point()
            if mount_point != "/storage/sdcard1":
                dst_path = dst_path.replace("/storage/sdcard1", mount_point)
        result = g_common_obj.adb_cmd_common("push \"%s\" \"%s\"" % (src_path, dst_path), 3000)
        logger.debug("push_file_to_dut--- result=%s" % result)
        return dst_path

    def push_file_new(self, src_path, dst_path):
        src_path = self.download_file_to_host(src_path)
        return self.push_file_to_dut(src_path, dst_path)

    def check_path_exist_in_dut(self, path):
        t_resut = self.executeCommandWithPopen("adb shell ls %s" % path).stdout.read()
        logger.debug("check_path_exist_in_dut--- t_resut=%s" % t_resut)
        return 0 if "No such file or directory" in t_resut else 1

    def mkdirs_in_dut(self, path):
        if self.check_path_exist_in_dut(path):
            return
        self.mkdirs_in_dut(os.path.split(path)[0])
        g_common_obj.adb_cmd_capture_msg("mkdir %s" % path)
        assert self.check_path_exist_in_dut(path), "mkdir failed! path=%s" % path

    def get_android_version(self):
        '''
        return Android verison of DUT
        '''
        from distutils.version import LooseVersion

        def cmp_version(v1, v2):
            return cmp(LooseVersion(v1), LooseVersion(v2))

        attr = "__android_version__"
        version = getattr(self, attr, None)
        if not version:
            prop = "ro.build.version.release"
            buf = g_common_obj.adb_cmd_capture_msg("getprop " + prop)
            v_str = buf.strip()
            if len(v_str) == 1 and v_str.isalpha():  # version in alpha
                version = v_str.upper()
            else:  # version in number
                if cmp_version(v_str, "8.0") >= 0:
                    version = 'O'
                elif cmp_version(v_str, "7.0") >= 0:
                    version = 'N'
                elif cmp_version(v_str, "6.0") >= 0:
                    version = 'M'
                else:
                    version = 'L'
            setattr(self, attr, version)
            print "android verson: ", version
        return version

    def get_paltform_hardware(self):
        """
        Returns:platform hardware info
        """
        hardware_prop = "ro.hardware"
        hardware_msg = g_common_obj.adb_cmd_capture_msg("getprop " + hardware_prop).strip()
        logger.debug("Current hardware info : %s" % hardware_msg)
        return hardware_msg

    def scroll_n_click(self, target):
        '''
        Scroll to UI element and click
        '''
        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(text=target)
        self.d(text=target).click()

    def clickScreen(self):
        return clickScreen()

    def mount_SD(self, mount):
        cmd = "am start -W com.android.settings"
        g_common_obj.adb_cmd(cmd)  # launch Settings
        if self.get_android_version() < 'M':
            self.scroll_n_click("Storage")
            if mount:
                self.scroll_n_click("Mount SD card")
            else:
                self.scroll_n_click("Unmount SD card")
                if self.d.exists(text="OK"):  # confirm the dialog
                    self.d(text="OK").click()
        else:
            if self.get_android_version() >= "N":
                self.scroll_n_click("Storage")
            else:
                self.scroll_n_click("Storage & USB")
            if mount:
                text = "Ejected"
                if self.d.exists(text=text):
                    self.d(text=text).click.wait()
                    self.d(textStartsWith="M").click()
            else:
                resourceId = "com.android.settings:id/unmount"
                if self.d.exists(resourceId=resourceId):
                    self.d(resourceId=resourceId).click()
        self.d.press.back()
        self.d.press.home()

    def set_enable_MTP(self, enable):
        if self.get_android_version() >= 'M':
            return
        logger.debug("enable MTP %s" % enable)
        prop = "persist.sys.usb.config"
        cmd = "getprop " + prop
        cur_conf = g_common_obj.adb_cmd_capture_msg(cmd)
        attr = '_sys_usb_config'
        if enable:
            prev_conf = getattr(self, attr, '')
            conf = prev_conf if 'mtp' in prev_conf else 'mtp,adb'
        else:
            setattr(self, '_sys_usb_config', cur_conf)
            functons = cur_conf.split(',')
            if 'mtp' in functons:
                functons.pop(functons.index('mtp'))
            conf = ','.join(functons)
        cmd = "setprop %s %s" % (prop, conf)
        g_common_obj.root_on_device()  # root first
        time.sleep(3)
        g_common_obj.adb_cmd_capture_msg(cmd)
        time.sleep(3)  # wait for adb reconnect

    def get_mount_point(self):  # NOQA
        logger.debug(self.tag + "start to get mount point")

        def get_mount_point_m():
            buf = g_common_obj.adb_cmd_capture_msg("sm list-volumes public")
            logger.debug(self.tag + "buf msg:" + buf)
            name = ''
            for l in buf.splitlines():
                if l.startswith("public"):
                    name = l.split()[-1]
                    break
            else:
                return None
            fuse_path = "/storage/" + name
            logger.debug(self.tag + "mount path:" + fuse_path)
            return fuse_path

        if self.get_android_version() >= 'M':  # mount point changed in M
            g_common_obj.root_on_device()
            time.sleep(3)
            # get the mount point of sd card
            mount_point = get_mount_point_m()

            if not mount_point:
                # enable adoptable storage
                # this must be set first, otherwise, "Set up" menu not appear
                g_common_obj.adb_cmd_capture_msg("sm set-force-adoptable true")
                time.sleep(3)
                # click "Set up" menu in notification
                self.d.open.notification()
                time.sleep(2)
                if self.d.exists(text="Set up"):
                    self.d(text="Set up").click.wait()
                    # enter "Set up your SD card" page
                    self.d(text="Use as portable storage").click()
                    self.d(text="Next").click.wait()
                    self.d(text="Done").click.wait()
                else:
                    self.d.press.home()

                mount_point = get_mount_point_m()
        else:
            buf = g_common_obj.adb_cmd_capture_msg("mount")
            mount_point = "/storage/sdcard1"
            if mount_point not in buf:
                mount_point = None
        if not mount_point:
            raise Exception("No mount point found, is SD card present?")
        return mount_point

    def setRotation(self, mode):
        self.d(description="More options",
               className="android.widget.ImageButton").click.wait()
        time.sleep(1)
        self.d(text=mode).click()
        time.sleep(1)

    def set_rotation(self, orientation='n'):
        """
            @summary: set orientation as n,l,r
        """
        if orientation == 'n':
            logger.debug("Set screen rotation to natural")
        elif orientation == 'l':
            logger.debug("Set screen rotation to left")
        elif orientation == 'r':
            logger.debug("Set screen rotation to right")
        else:
            logger.error("Set rotation failed, input arg error:{0}".format(orientation))
        self.d.orientation = orientation

    def get_play_time(self, s=60):
        logger.debug("get_play_time start")
        for i in range(s):
            if self.d(resourceId="android:id/time_current").exists:
                try:
                    ct = self.d(resourceId="android:id/time_current").text
                    tt = self.d(resourceId="android:id/time").text
                    ct = setTimeToSec(ct)
                    tt = setTimeToSec(tt)
                    return ct, tt
                except Exception as e:
                    print "Error:", e
                    continue
            else:
                print str(i + 1) + " times,don't find current time or total time"
                clickScreen()
                assert not self.d(textContains="Network not connected").exists, "Network not connected."
                assert not self.d(textContains="The remote media file is not reachable").exists,\
                    "The remote media file is not reachable."
                assert not self.d(textContains="error").exists, "Play error!"
                time.sleep(1)
        assert not self.d(textContains="OTC Alarm is triggered").exists, "OTC Alarm is triggered! wait time=%d" % (s)
        assert 0, "Play error! playback timeout %s s, network problem." % (s)
        return -1

    def get_progress_bar_bounds(self):
        logger.debug("get progress bar bounds")
        for _ in range(10):
            if not self.d(className="android.widget.SeekBar").exists:
                clickScreen()
            else:
                break
            time.sleep(1)
        bounds = self.d(className="android.widget.SeekBar").info["bounds"]
        progress_bar_bounds = {}
        progress_bar_bounds["y"] = bounds["top"] + (bounds["bottom"] - bounds["top"]) / 2
        progress_bar_bounds["x_start"] = bounds["left"] + 10
        progress_bar_bounds["x_end"] = bounds["right"] - 10
        return progress_bar_bounds

    def get_play_time_coordinate(self, percent):
        if "progress_bar_bounds" not in dir(self):
            self.progress_bar_bounds = self.get_progress_bar_bounds()
        x = self.progress_bar_bounds["x_start"] + \
            (self.progress_bar_bounds["x_end"] - self.progress_bar_bounds["x_start"]) * percent
        x = int(x)
        y = self.progress_bar_bounds["y"]
        y = int(y)
        logger.debug("progress_bar_bounds=%s, percent=%s" % (self.progress_bar_bounds, percent))
        return x, y

    def set_play_time(self, percent=0.5):
        x, y = self.get_play_time_coordinate(percent)
        self.d.click(x, y)

    def set_play_time_with_swipe(self, percent):
        ct, tt = self.get_play_time()
        ct = ct + 2
        if ct > tt:
            ct = tt
        start_x, start_y = self.get_play_time_coordinate(ct / float(tt))
        end_x, end_y = self.get_play_time_coordinate(percent)
        self.d.swipe(start_x, start_y, end_x, end_y)

    def unitConversion(self, t_str):
        if "G" in t_str:
            return float(t_str.replace("G", "")) * 1024
        if "M" in t_str:
            return float(t_str.replace("M", ""))
        if "K" in t_str:
            return float(t_str.replace("K", "")) / 1024

    def executeCommandWithPopen(self, cmd):
        if "adb" in cmd:
            serial = self.d.server.adb.device_serial()
            cmd = cmd.replace("adb", "adb -s %s" % serial)
        logger.debug("executeCommandWithPopen cmd=%s" % cmd)
        return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, shell=True)

    def clearLogs(self):
        self.executeCommandWithPopen("adb logcat -c")

    def check_logs(self, check_str, check_time=5):
        self.check_log_flag = 0
        while(self.check_log_flag == 0 and check_time >= 0):
            self.fdp = self.executeCommandWithPopen("adb logcat -d | grep \"%s\"" % check_str)
            t_str = self.fdp.stdout.read()
            logger.debug("t_str=%s" % t_str)
            if check_str in t_str:
                self.check_log_flag = 1
                return True
            time.sleep(5)
            check_time -= 5
        return False

    def checkLogs_start(self, check_str):
        if thread.start_new_thread(self.check_logs, (check_str,)):
            return True
        else:
            return False

    def checkLogs_end(self, check_str):
        logger.debug("self.check_log_flag=%s" % self.check_log_flag)
        if self.check_log_flag != 1:
            self.check_log_flag = -1
            assert self.check_log_flag == 1, "%s string not in log!!!" % check_str

    def getS0I3(self):
        fdp = self.executeCommandWithPopen("adb shell cat /sys/kernel/debug/pmc_atom/sleep_state | grep Idle-S0I3")
        t_str = fdp.stdout.read()
        logger.debug(t_str)
        assert "Idle-S0I3" in t_str, "Can't find Idle-S0I3 !!!"
        return t_str

    def clearFolder(self, t_folder):
        if "/storage/sdcard1" in t_folder:
            mount_point = self.get_mount_point()
            logger.debug(mount_point)
            t_folder = t_folder.replace("/storage/sdcard1", mount_point)
        g_common_obj.adb_cmd_capture_msg(t_folder)

    def recent_app(self):
        self.d.press.recent()
        time.sleep(3)

    def click_recent_app(self, app_name):
        logger.debug("Start click recent app")
        for _ in range(5):
            self.recent_app()
            if self.d(text=app_name).exists:
                break
        assert self.d(text=app_name).exists, "not found " + str(app_name)
        bounds = self.d(text=app_name).bounds
        logger.debug("bounds=%s " % str(bounds))
        self.d.click(bounds.get("left"), bounds.get("top"))

    def remove_recent_app(self, app_name):
        for _ in range(5):
            self.recent_app()
            if self.d(text=app_name).exists:
                break
        assert self.d(text=app_name).exists, "not found " + str(app_name)
        x = self.d.info["displayWidth"]
        bounds = self.d(text=app_name).bounds
        logger.debug("bounds=%s " % str(bounds))
        self.d.swipe(bounds.get("left"), bounds.get("top"), x - 50, bounds.get("top"))
        time.sleep(2)
        assert not self.d(text=app_name).exists, "remove recent app " + str(app_name) + "failed"

    def launchAlarmAPP(self):
        g_common_obj.launch_app_am("videoplayer.app.instrument.otc.intel.com.otcalarm",
                                   "otc.intel.com.otcalarm.MainActivity")
        time.sleep(3)
        assert self.d(text="OtcAlarm").exists, "launch alarm app failed!"

    def waitAlarmTriiggered(self, wait_time=30, operation="Dismiss"):
        t_time = 2
        for _ in range(1, wait_time, t_time):
            time.sleep(t_time)
            if self.d(text="OTC Alarm is triggered!").exists:
                break
        assert self.d(text="OTC Alarm is triggered!").exists, "Alarm wait timeout!"
        if operation == "Snooze":
            self.d(textContains="Dismiss").click()
            self.launchAlarmAPP()
        else:
            self.d(textContains=operation).click()

    def getcheckIputMethod(self):
        return checkIputMethod()

    def press_home_car(self):
        g_common_obj.launch_app_am(self.HOME_PACKAGE_NAME, self.HOME_ACTIVITY_NAME)

    def getScreenshotToHost(self, file_name, mhost_path, base_path="/sdcard/Pictures/"):
        logger.debug(self.tag + "screenshot and save to :%s" % mhost_path)
        screenshot_cmd = "shell screencap %s%s " % (base_path, file_name)
        save_to_host_cmd = "pull %s%s %s" % (base_path, file_name, mhost_path)
        g_common_obj.adb_cmd_common(screenshot_cmd)
        g_common_obj.adb_cmd_common(save_to_host_cmd)


class MultiMediaHandle:
    def __init__(self):
        self.d = g_common_obj.get_device()
        self.x = self.d.info["displayWidth"]
        self.y = self.d.info["displayHeight"]
        self.tag = "[MultiMediaHandle] "

    def launchVideoApp(self):
        SystemUI().unlock_screen()
        for _ in range(3):
            g_common_obj.launch_app_am("videoplayer.app.instrument.otc.intel.com.otcvideoplayer",
                                       "otc.intel.com.otcvideoplayer.InitActivity")
            time.sleep(3)
            if self.d(textContains="OtcVideoPlayer").exists:
                logger.debug(self.tag + "launch video app success!")
                return
        assert self.d(textContains="OtcVideoPlayer").exists, "launch video app failed!"

    def videoPlayBack(self, push_path):
        logger.debug(self.tag + "try to play :" + push_path)
        if self.d(description='More options').exists:
            logger.debug(self.tag + "click More option button")
            self.d(description='More options').click()
        time.sleep(1)
        if self.d(text="Open a local video").exists:
            logger.debug(self.tag + "select open a local video")
            self.d(text="Open a local video").click()
        for _ in range(10):
            if self.d(text="Open").exists:
                break
            time.sleep(1)
        time.sleep(3)
        if checkIputMethod() != '':
            self.d.press.back()
        time.sleep(1)
        self.d(className="android.widget.EditText").set_text(push_path)
        time.sleep(1)
        if checkIputMethod() != '':
            self.d.press.back()
        self.d(text="OK").click()
        time.sleep(1)
        assert not self.d(text="Can't play this video.").exists, "show Can't play video."
        assert not self.d(textContains="Network not connected").exists, "Network not connected."
        assert not self.d(textContains="The remote media file is not reachable") \
            .exists, "The remote media file is not reachable."
        return True

    def launchVLCApp(self):
        SystemUI().unlock_screen()
        for _ in range(3):
            g_common_obj.launch_app_am("org.videolan.vlc", ".gui.MainActivity")
            time.sleep(2)
            if self.d(textContains="Allow VLC to access").exists:
                self.d(resourceId="com.android.packageinstaller:id/permission_allow_button").click()
            if self.d(description="Open navigation drawer").exists:
                return
        assert self.d(resourceId="android:id/list").exists \
            or self.d(description="Open navigation drawer").exists, "launch VLC app failed!"

    def playVideoViaVLC(self, push_path, play_time=180):
        logger.debug(self.tag + "try to play :" + push_path)
        if not self.d(text="Video").exists:
            try:
                self.d(description="Open navigation drawer").click()
                time.sleep(1)
                self.d(text="Video").click()
            except:
                pass
        try:
            self.d(text=push_path).click()
        except:
            self.d(scrollable=True).scroll.to(text=push_path).click()
            pass
        time.sleep(1)

        current_view = self.get_activity()
        logger.debug("current activity view :%s" % current_view)
        if "VideoPlayerActivity" not in current_view:
            logger.debug("Launch " + push_path + " failed")
            return False

        for _ in range(3):
            if self.d(text="GOT IT").exists:
                logger.debug(self.tag + " 'GOT IT' is existed, click")
                self.d(text="GOT IT").click()
            elif self.d(text="Got it, dismiss this").exists:
                logger.debug(self.tag + " 'Got it, dismiss this' is existed, click")
                self.d(text="Got it, dismiss this").click()
            else:
                if self.d(text="Play").wait.exists(timeout=1000):
                    logger.debug(self.tag + "Launch " + push_path + " success")
                    break
                else:
                    clickScreen()
                    time.sleep(0.5)
            time.sleep(1)

        start_time = time.time()
        while time.time() - start_time < play_time:
            if not self.check_video_screen(otc_video_app=False, ssim_target=0.9):
                return False
            if not self.d(text="Play").exists:
                clickScreen()
                if not self.d(text="Play").exists:
                    logger.debug(self.tag + "Video play completed!")
                    return True
            logger.debug(self.tag + "Success play %s seconds" % int(time.time() - start_time))
        self.d.press.back()
        return True

    def playVideoviaOGallery(self, push_path):
        logger.debug(self.tag + "try to play %s" % push_path)
        play_cmd = "shell am start -a android.intent.action.VIEW -d file://%s " \
                   " -t video/* -n com.android.gallery3d/.app.MovieActivity" % (push_path)
        for _ in range(3):
            g_common_obj.adb_cmd_common(play_cmd)
            time.sleep(1)
            if self.d(resourceId="com.android.gallery3d:id/surface_view"):
                if self.d(text="Can't play this video.").exists:
                    logger.debug(self.tag + "cannot play this video.")
                    return False
                else:
                    logger.debug(self.tag + "Play this video success")
                    return True
        logger.debug(self.tag + "launch %s failed" % push_path)
        return False

    def checkVideoPlayHang(self, play_time=60):
        start_time = time.time()
        node = (0, 0, self.x, self.y)
        img_base = otcImage.cropScreenShot(self.d, node)
        while time.time() - start_time < play_time:
            if not self.d(resourceId="com.android.gallery3d:id/surface_view").exists:
                logger.debug(self.tag + "video play completed")
                return True
            time.sleep(10)
            img_cur = otcImage.cropScreenShot(self.d, node)
            ssim = float(otcImage.calc_similar(img_base, img_cur))
            img_base = img_cur
            logger.debug(self.tag + "Current picture similar is %s" % ssim)
            if ssim > 0.9:
                logger.debug(self.tag + "Video play may hang !")
                return False
            logger.debug(self.tag + "Success play %s seconds" % int(time.time() - start_time))
        logger.debug(self.tag + "video play successed play %s seconds" % play_time)
        return True

    def streamingVideoPlayBack(self, path, flag=1):
        self.d(className="android.widget.ImageButton").click()
        time.sleep(1)
        self.d(text="Open a local video").click()
        for _ in range(10):
            if self.d(textContains="Open").exists:
                break
            time.sleep(1)
        time.sleep(3)
        if checkIputMethod() != '':
            self.d.press.back()
        time.sleep(1)
        logger.debug(self.tag + "Try to play:" + path)
        self.d(className="android.widget.EditText").set_text(path)
        time.sleep(1)
        if checkIputMethod() != '':
            self.d.press.back()
        self.d(text="OK").click()
        time.sleep(10)
        if flag == 1:
            logger.debug("Check Streaming video play status")
            assert not self.d(text="Can't play this video.").exists, "show Can't play video."
            assert not self.d(textContains="Network not connected").exists, "Network not connected."
            assert not self.d(textContains="The remote media file is not reachable") \
                .exists, "The remote media file is not reachable."
            assert not self.d(textContains="Error:").exists, "Play stream video failed!"

    def clickOtcVideoPlayer_Control(self, wait_check=0, **ui_dump):
        '''
        Args:
            When cannot found Dump control,click the screen.
            **ui_dump: UI dump dict
            wait_check : if true and in
        Returns: True

        '''
        if ui_dump.keys() == "" and ui_dump.values() == "":
            logger.debug("No UI dumps input")
            return False
        if not self.d(**ui_dump).exists:
            clickScreen()
            if not self.d(**ui_dump).exists:
                logger.debug("Cannot find the ui dumps")
                return False
        else:
            logger.debug("Video screen is on")
        logger.debug("click {0} button".format(ui_dump))
        self.d(**ui_dump).click()
        if isinstance(int(wait_check), int):
            time.sleep(wait_check)
            return self.checkVideoPlayBack()
        return True

    def get_activity(self):
        activity_msg = None
        activity_msg = g_common_obj.adb_cmd_capture_msg('dumpsys activity |grep mResumedActivity')
        activity_list = []
        for i in range(len(activity_msg.split('\n'))):
            activity_name = activity_msg.split('\n')[i].strip().split()[3]
            logger.debug("Current Focus Activity:{0}".format(activity_name))
            activity_list.append(activity_name)
        return str(activity_list)

    def check_current_logcat_msg(self, msg, clear_log=False):
        if clear_log:
            execute_adb_command("logcat -c")
        time.sleep(1)
        msg_output = execute_adb_command("logcat -d |grep '%s'" % msg)
        if len(msg_output) > 0:
            logger.debug("Get %s in logcat" % msg)
            return True
        else:
            logger.debug("Cannot get %s in logcat" % msg)
            return False

    def click_otc_play_button(self):
        pause_button = self.d(resourceId="android:id/pause")
        if pause_button.exists:
            try:
                if str(pause_button.contentDescription) == "Play":
                    logger.debug(self.tag + "Get video pasue button, video is pause,click play button ")
                    pause_button.click()
            except:
                logger.debug("click play button exception")
                clickScreen()
                g_common_obj.adb_cmd_capture_msg("input keyevent KEYCODE_MEDIA_PLAY_PAUSE")

    def check_stop_and_play(self):
        """
        If video is stop , try to replay the video
        :return: None
        """
        current_time = self.d(resourceId="android:id/time_current")
        total_time = self.d(resourceId="android:id/time")
        Play_dump = self.d(resourceId="videoplayer.app.instrument.otc.intel.com.otcvideoplayer:id/videoView1Msg")
        pause_button = self.d(resourceId="android:id/pause")
        if current_time.exists and not Play_dump.exists:
            logger.debug(self.tag + "current play time show")
            if current_time.contentDescription == total_time.contentDescription:
                logger.debug("Video play completed.")
                pause_button.click()
            if pause_button.exists:
                try:
                    if str(pause_button.contentDescription) == "Play":
                        logger.debug(self.tag + "Get video pasue button, video is pause,click play button ")
                        pause_button.click()
                except:
                    logger.debug("click play button exception")
                    clickScreen()
                    g_common_obj.adb_cmd_capture_msg("input keyevent KEYCODE_MEDIA_PLAY_PAUSE")
        elif not current_time.exists:
            self.d.click(self.x / 2, self.y / 2)
            self.click_otc_play_button()

    def checkVideoPlayBack(self, s=30, done_flag=False, check_hang=True):
        logger.debug("checkVideoPlayBack play {0} seconds".format(s))
        play_view = "otcvideoplayer.SingleVideoActivity"
        play_status = False
        start_time = time.time()
        time.sleep(3)
        player_flag = self.d(resourceId="android:id/action_bar")
        current_time = self.d(resourceId="android:id/time_current")
        total_time = self.d(resourceId="android:id/time")
        pause_button = self.d(resourceId="android:id/pause")
        wait_to_play = self.d(textContains="Here will show playback result")
        Play_dump = self.d(resourceId="videoplayer.app.instrument.otc.intel.com.otcvideoplayer:id/videoView1Msg")
        completed_dump = self.d(resourceId="videoplayer.app.instrument.otc.intel.com.otcvideoplayer:id/videoView1Msg",
                                textContains="Completed:")
        if play_view not in self.get_activity():
            logger.error("Not video play view")
            return play_status
        while wait_to_play.exists:
            logger.debug("waite streaming to play")
            time.sleep(1)

        while start_time + s > time.time():
            # check video play screen
            if check_hang:
                try:
                    if str(pause_button.contentDescription) == "Pause":
                        if self.check_video_screen(otc_video_app=True):
                            logger.debug(self.tag + "screen is not hang")
                        else:
                            return False
                except Exception as e:
                    logger.debug(self.tag + "get pause button error:%s" % e)
                if self.check_current_logcat_msg("Failed to set layers in the composition"):
                    logger.error("Video screen show green, OAM-59329")
                    return False
                if self.check_current_logcat_msg(msg='Create Input surface failed'):
                    logger.error("Video screen show abnormal")
                    return False

            if Play_dump.exists:
                # check error info.
                if self.d(text="OTC Alarm is triggered!").exists:
                    logger.info("OTC Alarm is triggered!")
                    return True
                elif done_flag:
                    if completed_dump.exists and "Completed:" in str(completed_dump.text):
                        logger.debug("Video play completed.")
                        return True
                assert not self.d(textContains="Network not connected").exists, "Network not connected."
                assert not self.d(textContains="The remote media file is not reachable").exists, \
                    "The remote media file is not reachable."
                assert not self.d(textContains="error").exists, "Play error!"
            if not current_time.exists and player_flag.exists:
                logger.debug(self.tag + "No current play time, continue to play")
                if done_flag:
                    if completed_dump.exists or (current_time.contentDescription == total_time.contentDescription):
                        logger.debug("Video play completed.")
                        return True
                clickScreen()
                time.sleep(5)
            if current_time.exists and not Play_dump.exists:
                logger.debug(self.tag + "current play time show")
                if done_flag:
                    if current_time.contentDescription == total_time.contentDescription:
                        logger.debug("Video play completed.")
                        return True
                if pause_button.exists:
                    try:
                        if str(pause_button.contentDescription) == "Play":
                            logger.debug(self.tag + "Get video pasue button, video is pause,click play button ")
                            pause_button.click()
                    except:
                        logger.debug("click play button exception")
                        clickScreen()
                        g_common_obj.adb_cmd_capture_msg("input keyevent KEYCODE_MEDIA_PLAY_PAUSE")

            logger.debug(self.tag + "play video 5 seconds")
            time.sleep(5)
            logger.debug(self.tag + "Success play %s seconds" % int(time.time() - start_time))
            play_status = True
            logger.info(self.tag + "Play {0} seconds normally!".format(str(time.time() - start_time).split('.')[0]))
        return play_status

    def check_video_screen(self, node='', otc_video_app=False, ssim_target=0.98):
        logger.debug(self.tag + "Try check video play screen hang or black")
        if otc_video_app is True:
            node = (602, 359, 1302, 752)
        if node == '':
            node = (0, 0, self.x, self.y)
        logger.debug(self.tag + "Compare area : {0}".format(node))
        img_base = otcImage.cropScreenShot(self.d, node, imageName="savescreen_1.png", save=True)
        time.sleep(5)
        img_cur = otcImage.cropScreenShot(self.d, node, imageName="savescreen_2.png", save=True)
        ssim = float(otcImage.calc_similar(img_base, img_cur))
        logger.debug(self.tag + "Current picture similar is {0}".format(ssim))
        if ssim > ssim_target:
            logger.debug(self.tag + "Video play may hang or screen is black!")
            return False
        else:
            logger.debug(self.tag + "Video play normally")
            return True

    def checkVideoPlayBackWithComparePicture(self, stoptime=30, check_hang=True):
        logger.debug("checkVideoPlayBackWithComparePicture start, play " + str(stoptime) + ' seconds')
        stoptime = int(stoptime)
        video_current_time = "android:id/time_current"
        video_total_time = "android:id/time"
        start_time = time.time()
        check_screen_flag = 0
        while int(time.time() - start_time) < stoptime:
            time.sleep(10)
            if not self.d(resourceId=video_current_time).exists and not self.d(resourceId=video_total_time).exists:
                print " don't find current time or total time"
                time.sleep(1)
                self.d.click(self.x / 2, self.y / 2)
            if check_hang:
                self.check_stop_and_play()
                if self.check_current_logcat_msg("Failed to set layers in the composition"):
                    logger.error("Video screen show green, OAM-59329")
                    return False
                if self.check_current_logcat_msg(msg='Create Input surface failed'):
                    logger.error("Video screen show abnormal")
                    return False
                if not self.check_video_screen(otc_video_app=True):
                    check_screen_flag += 1
                if check_screen_flag >= 3:
                    logger.error("3 times check video hang")
                    return False
            logger.debug("Play video " + str(int((time.time() - start_time))) + " seconds normally.")
        return True

    def checkVideoPlayBackComplete(self, s=900, check_hang=True):
        logger.debug("check Video PlayBack Completed start, mostly play " + str(s) + ' seconds')
        stoptime = int(s)
        tt = -1
        start_time = time.time()
        check_screen_flag = 0
        while int(time.time() - start_time) < stoptime:
            time.sleep(10)
            if self.d(textContains="Completed").exists:
                logger.debug("Video PlayBack Completed")
                return True
            elif self.d(resourceId="android:id/time_current").exists and self.d(resourceId="android:id/time").exists:
                if self.d(resourceId="android:id/time_current").text == self.d(resourceId="android:id/time").text:
                    logger.debug("Video PlayBack Completed")
                    return True
            else:
                try:
                    if tt == -1:
                        for _ in range(10):
                            if self.d(resourceId="android:id/time").exists:
                                break
                            self.d.click(self.x / 2, self.y / 2)
                        tt = self.d(resourceId="android:id/time").text
                        tt = setTimeToSec(tt)
                    for _ in range(10):
                        if self.d(resourceId="android:id/time_current").exists:
                            break
                        self.d.click(self.x / 2, self.y / 2)
                    ct = self.d(resourceId="android:id/time_current").text
                    ct = setTimeToSec(ct)
                except Exception as e:
                    if self.d(textContains="Completed").exists:
                        logger.debug("Video PlayBack Completed")
                        return True
                    else:
                        assert False, e
            # check video play screen
            if check_hang:
                logger.debug("Try to check video hang or play abnormal")
                self.check_stop_and_play()
                if self.check_current_logcat_msg("Failed to set layers in the composition"):
                    logger.error("Video screen show green, OAM-59329")
                    return False
                if self.check_current_logcat_msg(msg='Create Input surface failed'):
                    logger.error("Video screen show abnormal")
                    return False
                if not self.check_video_screen(otc_video_app=True):
                    check_screen_flag += 1
                if check_screen_flag >= 3:
                    logger.error("3 times check video hang")
                    return False
            logger.debug("Play video " + str(int((time.time() - start_time))) + " seconds normally.")
        return False

    def checkVideoPlayBackWithPhotoApp(self, stoptime, bigfileskiptime=0, forceflag=0):
        bigfileskiptime = int(bigfileskiptime)
        if stoptime:
            stoptime = int(stoptime)
        else:
            stoptime = 120
        logger.debug("Start to check video play for {0} seconds".format(stoptime))
        start_time = time.time()
        video_current_time = "com.google.android.apps.photos:id/video_current_time"
        video_total_time = "com.google.android.apps.photos:id/video_total_time"
        play_flag = True
        while time.time() - start_time <= stoptime:
            for i in range(3):
                if self.d(resourceId="com.google.android.apps.photos:id/title").exists:
                    self.d(className="android.view.ViewGroup").click()
                elif not self.d(resourceId="com.google.android.apps.photos:id/photos_videoplayer_videolayout").exists:
                    logger.debug("%s times,click media file" % (i + 1))
                    try:
                        self.d(className="android.view.ViewGroup").click()
                    except:
                        self.d.click(self.d.info['displayHeight'] / 2, self.d.info['displayWidth'] / 2)
                    time.sleep(5)
            assert not self.d(textContains="Photos has stopped").exists, "Error! Photos has stopped!"
            play_flag = 0
            for i in range(10):
                if self.d(resourceId=video_current_time).exists or self.d(resourceId=video_total_time).exists:
                    logger.debug("{0} times, find current time and total time!!".format(str(i + 1)))
                    break
                else:
                    logger.debug("{0} times, don't find current time or total time!!".format(str(i + 1)))
                    play_flag += 1
                    self.d.click(self.x / 4, self.y / 2)
                    time.sleep(1)
                    if i == 1:
                        self.d.swipe(self.x / 2, 10, self.x / 2, self.y / 2 + 100, steps=50)
                        if self.d(textContains="otctest").exists or self.d(textContains="sdcard1").exists:
                            self.d(className="android.widget.ImageView").click()
                            time.sleep(3)
            assert not play_flag >= 4, "Cannot found current play time , play error!"
            if forceflag != 0:
                pass
            node = (0, self.y / 2 - 100, self.x, self.y / 2 + 100)
            img_0 = otcImage.cropScreenShot(self.d, node)
            time.sleep(15)
            img_1 = otcImage.cropScreenShot(self.d, node, imageName="savescreen.png", save=True)
            ssim = float(otcImage.calc_similar(img_0, img_1))
            logger.debug("ssim is {0}".format(ssim))
            if ssim > 0.99:
                if bigfileskiptime == 0:
                    assert ssim <= 0.99, "video playback failed"
            logger.debug("Run {0} seconds".format(str(time.time() - start_time).split('.')[0]))
        logger.debug("Long play {0} seconds completed".format(str(time.time() - start_time).split('.')[0]))
        return True


class MultiMediaBasicTestCase:

    config = TestConfig()

    def __init__(self):
        self.d = g_common_obj.get_device()
        self.x = self.d.info["displayWidth"]
        self.y = self.d.info["displayHeight"]
        self.cfg_file = os.path.join(os.environ.get('TEST_DATA_ROOT', ''),
                                     'tests.tablet.mum_auto_video.conf')
        self.multimedia_handle = MultiMediaHandle()
        self.multimedia_setting = MultiMediaSetting(self.cfg_file)
        self.hardware = self.multimedia_setting.get_paltform_hardware()
        self.tag = '[Multimedia Baisc Test Case]'

    def tearDown(self):
        """
        @summary: tear tearDown
        @return: None
        """
        super(MultiMediaBasicTestCase, self).tearDown()
        g_common_obj.adb_cmd_capture_msg(self.cfg_case.get("remove_video"))

    def appPrepare(self, case_name, model=1):
        logger.debug(self.tag + "get source file :{0}".format(case_name))
        self.cfg_case = self.config.read(self.cfg_file, case_name)
        g_common_obj.adb_cmd_common("root")
        g_common_obj.adb_cmd_common("logcat -c")
        g_common_obj.adb_cmd_capture_msg(" rm -rf /sdcard/DCIM/Camera/*")
        g_common_obj.adb_cmd_capture_msg(self.cfg_case.get("remove_video"))

        if model == 1:
            self.push_path = self.multimedia_setting.push_file(self.cfg_case.get("push_video"),
                                                               self.cfg_case.get("datapath"))

        self.multimedia_setting.install_apk("video_apk")
        self.multimedia_setting.install_apk("alarm_apk")
        g_common_obj.set_vertical_screen()
        # Unlock screen
        g_common_obj.adb_cmd_capture_msg("input keyevent 82")

    def checkVideoPlayBackHandle(self):
        ct, tt = self.multimedia_setting.get_play_time()
        logger.debug("ct=%d, tt=%d" % (ct, tt))
        if tt - ct >= 50:
            return self.multimedia_handle.checkVideoPlayBackWithComparePicture(20)
        else:
            return self.multimedia_handle.checkVideoPlayBack()

    def testVideoPlayBack(self, case_name, check_hang=True):
        print "run case is " + str(case_name)
        self.appPrepare(case_name)
        self.multimedia_handle.launchVideoApp()
        time.sleep(2)
        self.multimedia_handle.videoPlayBack(self.push_path)
        ct, tt = self.multimedia_setting.get_play_time()
        if tt - ct >= 50:
            assert self.multimedia_handle.checkVideoPlayBackWithComparePicture(60, check_hang=check_hang), \
                "Video play failed"
        else:
            assert self.multimedia_handle.checkVideoPlayBackComplete(900, check_hang=check_hang), "Video play failed"
        logger.debug("case is pass")
        return True

    def testVideoPlayBackLongIterationTimes(self, case_name):
        print "run case is " + str(case_name)
        self.appPrepare(case_name)
        self.multimedia_handle.launchVideoApp()
        long_play = False
        if self.cfg_case.get("iteration_times"):
            iteration_times = self.cfg_case.get("iteration_times")
            logger.info("Try to play video {0} times".format(iteration_times))
            long_play = True
        else:
            iteration_times = 1
        for iteration in range(int(iteration_times)):
            self.multimedia_handle.videoPlayBack(self.push_path)
            ret = 0
            try:
                for _ in range(10):
                    ct, tt = self.multimedia_setting.get_play_time()
                    if tt - ct >= 50:
                        self.multimedia_handle.checkVideoPlayBackWithComparePicture(20)
                    ret = self.multimedia_handle.checkVideoPlayBackComplete(300)
                    if ret == 1:
                        break
            except Exception as e:
                print "Error:", e
            if ret != 1:
                ct_end, tt_end = self.multimedia_setting.get_play_time()
                logger.debug("Play video %s minutes,not completed " % (ct_end / 60))
            logger.info("{0} iteration play completed, total {1} times".format(iteration + 1, iteration_times))
            if not long_play:
                break
            else:
                continue
        logger.info("Long play {0} seconds completed".format(iteration_times))
        print "case " + str(case_name) + " is pass"

    def testStreamingVideoPlayBack(self, case_name):
        print "run case is " + str(case_name)
        self.appPrepare(case_name, 2)
        loop = 2
        error_count = 0
        error_message = ""
        for i in range(2):
            try:
                self.multimedia_handle.launchVideoApp()
                time.sleep(2)
                self.multimedia_handle.streamingVideoPlayBack(self.cfg_case.get("video_path"))
                assert self.multimedia_handle.checkVideoPlayBack(), 'video play failed'
            except Exception as e:
                error_message += "[%d]:%s    " % (i, e)
                error_count += 1
                assert error_count < loop, ("Error:", error_message)
        print error_message
        print "case " + str(case_name) + " is pass"

    def videoPlayControlProcess(self, case_name, suspend=True):
        self.appPrepare(case_name)
        self.multimedia_handle.launchVideoApp()
        time.sleep(2)
        self.multimedia_handle.videoPlayBack(self.push_path)
        time.sleep(1)
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_setting.set_play_time(0.5)
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/rew")
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/ffwd")
        self.multimedia_setting.set_play_time_with_swipe(0.2)
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/pause")
        self.multimedia_setting.set_rotation("l")
        self.multimedia_handle.checkVideoPlayBack(check_hang=False)
        self.multimedia_setting.set_rotation("n")
        self.multimedia_handle.checkVideoPlayBack(check_hang=False)
        if self.multimedia_handle.checkVideoPlayBack(check_hang=False):
            logger.debug("case is pass")
        else:
            assert False, "case is Fail"

    def videoPlayCodecProcess(self, case_name, msg=''):
        self.appPrepare(case_name)
        self.multimedia_handle.launchVideoApp()
        time.sleep(2)
        self.multimedia_handle.videoPlayBack(self.push_path)
        time.sleep(1)
        assert self.multimedia_handle.check_current_logcat_msg(msg, clear_log=False), 'cannot get %s' % msg
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_setting.set_play_time(0.5)
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/rew")
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/ffwd")
        self.multimedia_setting.set_play_time_with_swipe(0.2)
        assert self.checkVideoPlayBackHandle(), 'video play failed'
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/pause")
        if self.multimedia_handle.checkVideoPlayBack(check_hang=False):
            logger.debug("case is pass")
        else:
            assert False, "case is Fail"

    def streamingVideoPlayControlProcess(self, case_name):
        print "run case is " + str(case_name)
        self.appPrepare(case_name, 2)
        self.multimedia_handle.launchVideoApp()
        time.sleep(2)
        self.multimedia_handle.streamingVideoPlayBack(self.cfg_case.get("video_path"))
        time.sleep(10)
        self.multimedia_setting.set_play_time(0.3)
        assert self.multimedia_handle.checkVideoPlayBack(), 'video play failed'
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/rew")
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/ffwd")
        self.multimedia_setting.set_play_time_with_swipe(0.2)
        self.multimedia_handle.checkVideoPlayBack()
        self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/pause")
        print "case " + str(case_name) + " is pass"

    def streamingVideoPlayControlProcessLong(self, case_name):
        print "run case is " + str(case_name)
        self.appPrepare(case_name, 2)
        self.multimedia_handle.launchVideoApp()
        time.sleep(2)
        self.multimedia_handle.streamingVideoPlayBack(self.cfg_case.get("video_path"))
        start_time = time.time()
        timeout = self.cfg_case.get("play_time")
        logger.info("Long play {0} seconds".format(timeout))
        time.sleep(10)
        iteration = 0
        while time.time() - start_time < int(timeout):
            self.multimedia_setting.set_play_time(0.3)
            self.multimedia_handle.checkVideoPlayBack()
            self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/rew")
            self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/ffwd")
            self.multimedia_setting.set_play_time_with_swipe(0.2)
            self.multimedia_handle.checkVideoPlayBack()
            self.multimedia_handle.clickOtcVideoPlayer_Control(resourceId="android:id/pause")
            iteration += 1
            logger.info("{0} iteration control completed, run {1} seconds"
                        .format(iteration, str(time.time() - start_time).split('.')[0]))
        logger.info("Long play {0} seconds completed".format(timeout))
        print "case " + str(case_name) + " is pass"

    def videoPlayControlProcess_Complete_pasue(self, case_name):
        """

        Args:
            case_name: videoPlayControlProcess

        Returns:True or Flase
        steps: 1. Open video
            2. Play clip to the end
            3. Play Pasuse
        """
        logger.debug("run case is {0}".format(case_name))
        pause_count = 3
        self.push_path = "/sdcard/otctest/ToS_2160p_29.97fps_HEVC_35000kbps_10bits_noHDR_Barcoded.mp4"
        try:
            self.appPrepare(case_name)
            self.multimedia_handle.launchVideoApp()
            self.multimedia_handle.videoPlayBack(self.push_path)
            # Play clip to the end
            assert self.multimedia_handle.checkVideoPlayBackComplete() == 1, "Play %s failed" % self.push_path
            # Play Pasuse
            self.multimedia_handle.launchVideoApp()
            self.multimedia_handle.videoPlayBack(self.push_path)
            self.multimedia_handle.checkVideoPlayBack()
            for _ in range(pause_count):
                self.multimedia_handle.clickOtcVideoPlayer_Control(wait_check=30, resourceId="android:id/pause")
        except Exception as e:
            logger.debug("error info: {0}".format(e))
            return False
        logger.debug("case {0} is pass".format(case_name))
        return True

    def testVideoPlayBackViaVLC(self, case_name, change_file_flag=False):
        logger.debug(self.tag + "run case is {0}".format(case_name))
        self.appPrepare(case_name)
        self.multimedia_handle.launchVLCApp()
        assert self.multimedia_handle.playVideoViaVLC(self.push_path.split('/')[-1]), "case is failed"
        if change_file_flag:
            self.multimedia_handle.launchVLCApp()
            n_path = move_dut_file_path(self.push_path, '/sdcard/otctest/')
            g_common_obj.adb_cmd_capture_msg(self.cfg_case.get("refresh_sd"))
            assert self.multimedia_handle.playVideoViaVLC(n_path.split('/')[-1]), "case is failed"
        logger.debug(self.tag + "run {0} is pass".format(case_name))

    def testVideoPlayBackViaGallery(self, case_name):
        logger.debug(self.tag + "run case is {0}".format(case_name))
        self.appPrepare(case_name)
        assert self.multimedia_handle.playVideoviaOGallery(self.push_path), "Play video failed"
        assert self.multimedia_handle.checkVideoPlayHang(play_time=30), "case is failed"
        logger.debug(self.tag + "run {0} is pass".format(case_name))
