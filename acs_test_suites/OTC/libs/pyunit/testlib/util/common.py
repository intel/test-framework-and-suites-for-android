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
import Queue
import threading

from testlib.util.globalcontext import GlobalContext
from testlib.util.device import TestDevice, getAllSerial
from testlib.util.process import shell_command
from testlib.util.log import Logger

LOG = Logger.getlogger(__name__)


def add(x):
    return '"%s"' % str(x)


class RunThread(threading.Thread):
    def __init__(self, queue, serial, classes, methods):
        threading.Thread.__init__(self)
        self.__QUEUE__ = queue
        self.__SERIAL__ = serial
        self.__CLASS_NAME__ = classes
        self.__METHODS__ = methods

    def run(self):
        try:
            for tmpValue in self.__METHODS__:
                method = tmpValue.split("*")[0]
                args = tmpValue.split("*")[1:]
                for className in self.__CLASS_NAME__:
                    alias_method = getattr(className, method, None)
                    if alias_method:
                        break
                if alias_method:
                    if len(args) == 0:
                        cmd = 'alias_method(self.__SERIAL__)'
                    else:
                        cmd = 'alias_method(self.__SERIAL__, %s)' % ",".join(
                            map(add, args))
                    eval(cmd)
                else:
                    raise Exception("Undefined method %s" % method)
        except Exception, e:
            self.__QUEUE__.put(e)


class Common(object):
    """
    Common class is a lightweight wrapper to make using test case
    common utilities eaiser.

    """
    _inst = None

    def __new__(cls, *args, **kwargs):
        if not cls._inst:
            cls._inst = super(Common, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self, context=None):
        self.globalcontext = GlobalContext()
        # TODO: override default context setting here
        # if context object is not null.
        self.default_device = None
        self.default_test_device = None
        self.d = self.get_device()

    def close_background_apps(self):
        d = self.get_device()
        d.press.recent()
        time.sleep(2)
        app_thumb_id = "com.android.systemui:id/app_thumbnail_image"
        task_view_thumb_id = "com.android.systemui:id/task_view_thumbnail"
        if d(resourceId=app_thumb_id).exists:
            while d(resourceId=app_thumb_id).exists:
                d(resourceId=app_thumb_id).drag.to(resourceId=app_thumb_id,
                                                   steps=50)
                if d(text="Remove from list").exists:
                    d(text="Remove from list").click.wait()
            assert not d(resourceId=app_thumb_id).exists
        elif d(resourceId=task_view_thumb_id).exists:
            dismiss_task_id = "com.android.systemui:id/dismiss_task"
            for i in range(100):
                if d(resourceId=task_view_thumb_id).exists:
                    d(resourceId=dismiss_task_id).click.wait()
                else:
                    break
            assert not d(resourceId=task_view_thumb_id).exists

    def set_context(self, context):
        """
        This method is used to setting global context object upon the
        conetext object injected by noseruner.

        The purpose of not using context object injected by noserunner directly
        is to de-couple with name convensions defined in noserunner. Otherwise
        this will introduce batch name revision if noserunner changed some
        properties' name.
        """

        if (context.user_log_dir is not None):
            self.globalcontext.user_log_dir = context.user_log_dir
            LOG.debug('User log directory was set to: %s according to context object' %
                      self.globalcontext.user_log_dir)

        if (context.device_config['deviceid'] is not None):
            self.globalcontext.device_serial = context.device_config['deviceid']
            LOG.debug('Device serial was set to : %s according to context object ' %
                      self.globalcontext.device_serial)

    def get_device(self, serial=None):
        if serial:
            return TestDevice(serial).get_device()
        elif 'preferred_device' in os.environ:
            return TestDevice(os.environ['preferred_device']).get_device()

        if not self.default_device:
            self.default_device = self.get_test_device().get_device()
        return self.default_device

    def get_device_name(self):
        d = self.get_device()
        device_info = d.info
        device_name = device_info.get("productName")
        return device_name

    def get_test_device(self, serial=None):
        if serial:
            return TestDevice(serial)

        if not self.default_test_device:
            self.default_test_device = TestDevice(
                self.globalcontext.device_serial)
        return self.default_test_device

    def get_user_log_dir(self):
        return self.globalcontext.user_log_dir

    def get_curr_lang(self):
        return self.globalcontext.language

    def get_device_type(self):
        return self.globalcontext.devicetype

    def shell_cmd(self, cmdstr, time_out=30):
        return shell_command(cmdstr, time_out)[0]

    def adb_cmd(self, cmdstr, time_out=90):
        return self.get_test_device().adb_cmd(cmdstr, time_out)

    def adb_cmd_capture_msg(self, cmdstr, time_out=90):
        return self.get_test_device().adb_cmd_capture_msg(cmdstr, time_out)

    def adb_cmd_common(self, cmdstr, time_out=90):
        return self.get_test_device().adb_cmd_common(cmdstr, time_out)

    def sync_file_from_content_server(self, cmd, datapath):
        return self.get_test_device().sync_file_from_content_server(cmd, datapath)

    def start_exp_handle(self):
        """
        Common routine to capture and handle system execeptions.
        Expect to be called when test case start.

        """
        self.globalcontext.anr_captured = False
        self.globalcontext.crash_captured = False

    def stop_exp_handle(self):
        """
        Stop the exception handle.
        Expect to be called when test case tear down.

        """
        LOG.debug("stop exception catch")
        d = self.get_device()
        if d(textContains="isn't responding.").exists:
            self.save_exp_info()
            d(text="OK").click()
            self.globalcontext.anr_captured = True
        if d(textContains="has stopped").exists:
            self.save_exp_info()
            d(text="OK").click()
            self.globalcontext.anr_captured = True

    def assert_exp_happens(self):
        """
        Assert if common exception hanppens like force close.

        """

        # Run all registered watchers to ensure they have chances to run if
        # no UI action is taking when user call assert_exp_happens
        d = self.get_device()
        if d(textContains="isn't responding.").exists:
            self.save_exp_info()
            d(text="OK").click()
            self.globalcontext.anr_captured = True
        if d(textContains="has stopped").exists:
            self.save_exp_info()
            d(text="OK").click()
            self.globalcontext.anr_captured = True
        assert not self.globalcontext.anr_captured
        assert not self.globalcontext.crash_captured

    def save_exp_info(self):
        pre_time = time.strftime(
            "%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))
        path = self.globalcontext.user_log_dir + pre_time
        LOG.debug("it's the folderpath" + path)
        create_folder_cmd = "mkdir -m 777 " + path
        LOG.debug(create_folder_cmd)
        os.system(create_folder_cmd)
        self.get_logcat_and_save(path)
        self.take_screenshot(path + "/screenshot.png")

    def get_logcat_and_save(self, path):
        get_log_cmd = "logcat -d >" + path + "/logcat.log"
        self.adb_cmd(get_log_cmd)

    def back_home(self):
        d = self.get_device()
        d.press.back()
        d.press.back()
        d.press.home()

    def launch_app_am(self, packagename, activityname):
        """
        Launch app from am command
        Parameter packagename is the app's package name to be launched
        Parameter activityname is the app's entry point name
        """
        cmdstr = 'am start -S -n %s/%s' % (packagename, activityname)

        return self.adb_cmd(cmdstr)

    def stop_app_am(self, packagename):
        """
        Stop app rom am command
        Parameter packagename is the app's package name to be stopped

        """
        cmdstr = "am force-stop %s" % packagename
        return self.adb_cmd(cmdstr)

    def launch_app_from_home_sc(self, appname, appgallery="Apps", inspection=None):
        """
        Launch App from app gallery
        Parameter appname is the app's widget name in app gallery
        Parameter appgallery is the widget name of app in home screen
        Parameter inspection is the text to validate if given app launched

        Please be aware that this fucntion assumes:
        1) There is a app gallery icon in home screen;
        2) Your app widget could be found in home screen.

        If your app meets above 2 assumtions, then it could be a convenient function
        call for you. Otherwise you may consider write your own app launch steps or
        using launch_app_am function instead.

        """
        iffind = False
        d = self.get_device()
        self.back_home()
        if d(description="Apps").exists:
            d(description="Apps").click()
        else:
            d(description="Apps list").click()
        if d(text="Widgets").exists:
            d(text="Widgets").click()
            d(text="Apps").click()
            if d(scrollable=True):
                d(scrollable=True).scroll.horiz.toBeginning(steps=20)
        for _ in range(10):
            if d(text=appname).exists:
                d(text=appname).click()
                iffind = True
                break
            try:
                d(scrollable=True).scroll.horiz()
            except Exception, e:
                print e
        if not iffind:
            for _ in range(10):
                if d(text=appname).exists:
                    d(text=appname).click()
                    iffind = True
                    break
                d(scrollable=True).scroll.horiz.backward()
        assert iffind is True
        if (inspection is not None):
            assert d(textMatches=inspection)

    def root_on_device(self):
        self.get_test_device().root_on_device()

    def root_off_device(self):
        self.get_test_device().root_off_device()

    def reboot_device(self):
        self.get_test_device().reboot_device()

    def remount_device(self):
        self.get_test_device().remount_device()

    def pull_file(self, local_path, remote_path):
        return self.get_test_device().pull_file(local_path, remote_path)

    def push_file(self, local_path, remote_path):
        return self.get_test_device().push_file(local_path, remote_path)

    def take_screenshot(self, scname):
        """
        Take screen shot from DUT and save it into file scname in host.
        """
        d = self.get_device()
        d.screenshot(scname)

    def set_vertical_screen(self):
        d = self.get_device()
#        width = d.info["displayWidth"]
#        height = d.info["displayHeight"]
#        orientation = d.info["displayRotation"]
#        if width > height and orientation == 0:
#            d.orientation = "r"
#        elif width > height and orientation > 0 :
#            d.orientation = "n"
        d.orientation = 'natural'
        d.freeze_rotation()

    def restart_server(self):
        """
        restart_server

        """
        d = self.get_device()
        d.server.stop()
        d.server.start()

    def getAllSerial(self):
        return getAllSerial()

    def getDevices(self, devNum=1):
        serial = os.environ['preferred_device'] if 'preferred_device' in os.environ else None
        return self.get_test_device(serial).getDevices(devNum)


class TestRun():
    def __init__(self, *className):
        self.__QUEUE__ = Queue.Queue()
        self.__CLASS_NAME__ = list(className)

    def sync_run(self, serial, *methods):
        if isinstance(serial, list):
            serialList = serial
        elif isinstance(serial, str):
            serialList = serial.split(" ")

        __count_th = threading.activeCount()
        for deviceSerial in serialList:
            runThread = RunThread(
                self.__QUEUE__, deviceSerial, self.__CLASS_NAME__, methods)
            runThread.setDaemon(True)
            runThread.start()

        while True:
            if threading.activeCount() <= __count_th:
                break
            if self.__QUEUE__.qsize() > 0:
                raise Exception(self.__QUEUE__.get())
            time.sleep(0.2)


g_common_obj = Common()
