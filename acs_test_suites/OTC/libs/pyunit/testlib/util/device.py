# -*- coding:utf-8 -*-
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
from uiautomator import Device
from testlib.util.log import Logger
from testlib.util.process import shell_command
from testlib.util.process import shell_command_nomsg, shell_command_ext


LOG = Logger.getlogger(__name__)


def getAllSerial():
    """get all device serials found by command adb devices"""
    _, msgs = shell_command("adb devices")
    devices = [line for line in msgs if "\tdevice\n" in line]
    serials = sorted([dev.split()[0] for dev in devices], key=len)
    return serials


class TestDevice(object):
    """
    TestDevice wrapper adb command calls and UiAutomator device object.
    The purpose of this class is to hide device serial to be used and
    ensure individual test case doesn't need to take care what device
    serial to be used if multiple device connected to host. So that t

    """

    def __init__(self, serial=None,
                 adb_server_host=None, adb_server_port=None):
        self.serial = serial
        self.adb_server_host = adb_server_host
        self.adb_server_port = adb_server_port
        self.adb_prefix = 'adb '
        if self.adb_server_host:
            self.adb_prefix += '-H %s ' % self.adb_server_host
        if self.adb_server_port:
            self.adb_prefix += '-P %s ' % self.adb_server_port
        if self.serial:
            self.adb_prefix += '-s %s ' % self.serial
        self.uia_device = None

    def get_device(self):
        """
        Lightweight wrapper for uiautomator device object.

        Use this wrapper to avoid handle device serial in individual
            test case.
        """

        if self.uia_device:
            return self.uia_device

        if self.adb_server_host or self.adb_server_port:
            params = {
                'serial': self.serial,
                'adb_server_host': self.adb_server_host,
                'adb_server_port': self.adb_server_port,
            }
            self.uia_device = Device(**params)
        elif self.serial:
            self.uia_device = Device(self.serial)
        else:
            self.uia_device = Device()

        return self.uia_device

    def adb_cmd(self, cmdstr, time_out=15):
        """
        Lightweight wrapper for adb command call.

        Return adb command ret value.

        parameter cmdstr is the command line string run in adb shell

        """
        adbcmdstr = "%s shell %s" % (self.adb_prefix, cmdstr)
        LOG.debug('Execute adb command: %s' % adbcmdstr)
        return shell_command_nomsg(adbcmdstr, time_out)

    def adb_cmd_capture_msg_ext(self, cmdstr, time_out=None, callbk=None):
        """
        Lightweight wrapper for adb command call.

        Return adb command line's message output

        parameter cmdstr is the command line string run in adb shell

        """
        adbcmdstr = "%s shell %s" % (self.adb_prefix, cmdstr)
        LOG.debug('Execute adb command: %s' % adbcmdstr)
        _, out, _ = shell_command_ext(
            adbcmdstr, timeout=time_out, callbk=callbk)
        return out.strip('\r\n')

    def adb_cmd_capture_msg(self, cmdstr, time_out=15):
        """
        Lightweight wrapper for adb command call.

        Return adb command line's message output

        parameter cmdstr is the command line string run in adb shell

        """

        adbcmdstr = "%s shell %s" % (self.adb_prefix, cmdstr)
        LOG.debug('Execute adb command: %s' % adbcmdstr)
        _, msgs = shell_command(adbcmdstr, time_out)

        return ''.join(msgs).strip('\r\n')

    def adb_cmd_common(self, cmdstr, time_out=300):
        """
        Lightweight wrapper for adb command call.

        Return adb command line's message output

        parameter cmdstr is the command line string run in adb

        """

        adbcmdstr = "%s %s" % (self.adb_prefix, cmdstr)
        LOG.debug('Execute adb command: %s' % adbcmdstr)
        _, msgs = shell_command(adbcmdstr, time_out)

        return ''.join(msgs).strip('\r\n')

    def sync_file_from_content_server(self, cmd, datapath):
        """sync file from content server"""
        result = True
        cmds = cmd.replace("\"", "").split(" ")
        file_name = cmds[1].replace(" ", "")
        print "file name is %s" % file_name
        data = datapath + os.path.basename(file_name)
        print "data=", data
        if os.path.exists(file_name):
            print "file exists,not need download"
        else:
            print "file not exists,download file now"
            from fileDownloader import fileDownloader
            print 'download file :%s' % data
            import urllib2
            try:
                downloader = fileDownloader.DownloadFile(
                    data, file_name, timeout=3000)
                if downloader.checkExists():
                    if downloader.download():
                        print 'download file successful :%s' % data
                    else:
                        print 'download file failed :%s' % data
                        result = False
            except urllib2.HTTPError as e:
                print 'HTTPError message is :%s' % e.msg
                result = False
            except urllib2.URLError as e:
                print e.reason
                result = False
        if not result:
            self.adb_cmd_capture_msg(("rm -rf " + str(file_name)))
            assert False, "download file failed"

    def close_background_apps(self):
        """close background apps"""
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

    def back_home(self):
        """back to home"""
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
        cmdstr = "am start -S -n %s/%s" % (packagename, activityname)

        return self.adb_cmd(cmdstr)

    def stop_app_am(self, packagename):
        """
        Stop app rom am command
        Parameter packagename is the app's package name to be stopped

        """
        cmdstr = "am force-stop %s" % packagename
        return self.adb_cmd(cmdstr)

    def launch_app_from_home_sc(self, appname,
                                appgallery="Apps", inspection=None):
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
        time.sleep(1)
        d(descriptionStartsWith="Apps").click.wait()
        time.sleep(.5)
        if d(text="Widgets").exists:
            d(text="Widgets").click()
            d(text="Apps").click.wait()
            time.sleep(.5)
            if d(scrollable=True):
                d(scrollable=True).scroll.horiz.toBeginning(steps=20)
        for _ in range(100):
            if d(text=appname).exists:
                d(text=appname).click.wait()
                iffind = True
                break
            d(scrollable=True).scroll.to(text=appname)
        assert iffind, "App %s not found!" % appname
        if inspection is not None:
            assert d(textMatches=inspection)

    def skip_initial_screen_after_factory_reset(self):
        """
        Skip initial screen after factory reset.
        """
        d = self.get_device()
        if d(description="Start").exists:
            d(description="Start").click.wait()
            d(text="Skip").click.wait()
            d(text="Skip anyway").click.wait()
            if d(text="More").exists:
                d(text="More").click.wait()
            d(text="Next").click.wait()
            d.press.back()
            time.sleep(2)
            if d(text="Next").exists:
                d(text="Next").click.wait()
            if d(text="Next").exists:
                d(text="Next").click.wait()
            if d(text="Skip").exists:
                d(text="Skip").click.wait()
                d(text="Skip anyway").click.wait()
            while d(text="More").exists:
                d(text="More").click.wait()
            if d(text="Next").exists:
                d(text="Next").click.wait()
        if d(text="Finish").exists:
            d(text="Finish").click.wait()
        if d(text="Allow").exists:
            d(text="Allow").click.wait()
            time.sleep(1)
        while d(text="OK").exists:
            d(text="OK").click.wait()
        if d(text="GOT IT").exists:
            d(text="GOT IT").click.wait()

    def take_screenshot(self, scname):
        """
        Take screen shot from DUT and save it into file scname in host.
        """
        d = self.get_device()
        d.screenshot(scname)

    def restart_server(self):
        """
        restart_server
        """
        d = self.get_device()
        d.server.stop()
        d.server.start()

    def root_on_device(self):
        """
        android root on
        """
        adbcmdstr = self.adb_prefix + "root"
        LOG.debug('Execute adb root on')
        ret, _ = shell_command(adbcmdstr)
        time.sleep(5)
        return ret

    def root_off_device(self):
        """
        android root off

        """
        adbcmdstr = self.adb_prefix + "root off"
        LOG.debug('adb root off')
        ret, _ = shell_command(adbcmdstr)
        time.sleep(3)
        return ret

    def reboot_device(self):
        """
        android root on
        """
        adbcmdstr = self.adb_prefix + "reboot"
        LOG.debug('Execute adb reboot')
        ret, _ = shell_command(adbcmdstr)
        adbcmdstr = self.adb_prefix + "wait-for-device"
        LOG.debug('Waiting for device online')
        ret, _ = shell_command(adbcmdstr, timeout_second=90)
        return ret

    def remount_device(self):
        """remount device
        """
        adbcmdstr = self.adb_prefix + "remount"
        LOG.debug('Execute adb remount')
        _, _ = shell_command(adbcmdstr)

    def pull_file(self, local_path, remote_path):
        """download file from device"""
        adbcmdstr = "%s pull %s %s" % (
            self.adb_prefix, remote_path, local_path)
        exit_code, ret = shell_command(adbcmdstr, timeout_second=300)
        if exit_code != 0:
            error = ret[0].strip('\r\n') if len(ret) else "adb shell timeout"
            LOG.info("[ Pull file \"%s\" failed, error: %s ]" %
                     (remote_path, error))
            return False
        else:
            return True

    def push_file(self, local_path, remote_path):
        """upload file to device"""
        adbcmdstr = "%s push %s %s" % (
            self.adb_prefix, local_path, remote_path)
        exit_code, ret = shell_command(adbcmdstr, timeout_second=300)
        if exit_code != 0:
            error = ret[0].strip('\r\n') if len(ret) else "adb shell timeout"
            LOG.info("[ Push file \"%s\" failed, error: %s ]" %
                     (local_path, error))
            return False
        else:
            return True
