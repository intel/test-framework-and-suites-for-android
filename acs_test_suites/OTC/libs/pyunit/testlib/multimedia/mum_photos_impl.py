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

import datetime
import os
import sys
import time
from uiautomator import JsonRPCError
from testlib.multimedia.base import UiWindows
from testlib.multimedia.impl import ImplCommon
from testlib.util.common import g_common_obj
from testlib.util.otc_image import otcImage
from testlib.multimedia.multimedia_log import MultimediaLogger
logger = MultimediaLogger.instance()
BASE_PATH = os.path.dirname(__file__)


class PhotosImpl(ImplCommon):
    """
    Multi-media functions.
    """
    def __init__(self, cfg=None):
        self.d = g_common_obj.get_device()
        self.dut = self.d
        self.cfg = cfg

    def set_orientation_n(self):
        """
        @summary: set orientation as n
        """
        g_common_obj.set_vertical_screen()

    def relaunchPhotos(self):
        g_common_obj.adb_cmd_capture_msg("am broadcast -a \
                                         android.intent.action.MEDIA_MOUNTED --ez read-only false -d \
                                         file://storage/sdcard1")
        time.sleep(5)
        g_common_obj.launch_app_am("com.google.android.apps.photos",
                                   "com.google.android.apps.photos.localmedia.ui.LocalFoldersActivity")
        time.sleep(5)

    def launchPhotos(self, push_folder=""):
        if push_folder == "":
            push_folder = "sdcard1"
        test_file_folder = "otctest"
        g_common_obj.launch_app_am("com.google.android.apps.photos",
                                   ".home.HomeActivity")

        for _ in range(3):
            time.sleep(1)
            if self.d(resourceId='com.android.packageinstaller:id/permission_allow_button').exists:
                self.d(resourceId='com.android.packageinstaller:id/permission_allow_button').click()
                time.sleep(1)
            if self.d(textContains='Google Photos uses face').exists and \
                    self.d(textMatches='[O|o][N|n]').exists:
                logger.debug("back up & sync display, try to init photos")
                x = self.d.info['displayHeight'] / 2
                y = self.d.info['displayWidth'] / 2
                self.d.click(x, y)
            if self.d(textContains="Keep backup off").exists:
                self.d(textMatches="Keep off|KEEP OFF").click()
            if self.d(textStartsWith="Never show").exists:
                self.d(textStartsWith="Never show").click()
            if self.d(textMatches="SKIP|Skip").exists:
                self.d(textMatches="SKIP|Skip").click()
            if self.d(textMatches="CANCEL|Cancel").exists:
                self.d(textMatches="CANCEL|Cancel").click()
            if self.d(description="Photos, selected, tab, 2 of 3") \
                .exists or self.d(textContains=test_file_folder).exists:
                logger.debug("init completed")
                break
        for _ in range(3):
            if self.d(description='Show Navigation Drawer').exists:
                self.d(description='Show Navigation Drawer').click()
            if self.d(description='Navigate up').exists:
                self.d(description='Navigate up').click()
            if self.d(textContains="Device folders").exists:
                self.d(textContains="Device folders").click()
                break
            else:
                self.d.press.back()
            time.sleep(3)

        for _ in range(3):
            if not self.d(textContains=test_file_folder).exists:
                try:
                    self.d(scrollable=True).scroll.vert.to(textContains=push_folder)
                except Exception as e:
                    print "Error:", e
                if self.d(textContains=push_folder).exists:
                    test_file_folder = push_folder
                else:
                    self.relaunchPhotos()
        if not self.d(textContains=test_file_folder).exists:
            self.d(scrollable=True).scroll.vert.to(textContains=test_file_folder)
        try:
            self.d(text=test_file_folder).click()
            return True
        except:
            logger.debug("cannot open %s folder" % test_file_folder)
            return False

    def homeMenu(self):
        return self.d(className="android.widget.ImageButton", description="Open navigation drawer")

    def openPhotosFolders(self):
        self.homeMenu().click()
        self.d(text="On device").click()

    def getFolder(self, folderName):
        if self.d(text=folderName).exists:
            return self.d(text=folderName)
        else:
            self.d(scrollable=True).scroll.to(text=folderName)
            return self.d(text=folderName)

    def getLastChild(self, obj):
        i = 0
        while True:
            if obj.child(index=i).exists:
                i = i + 1
        return obj.child(index=i - 1)

    def openCategoryFolder(self, foldername):
        self.getFolder(foldername).click.wait()

    def openCameraFolder(self):
        self.launchPhotos()
        self.openPhotosFolders()
        self.getFolder("Camera").click.wait()

    def isVideo(self):
        self.d(resourceId="com.google.android.apps.plus:id/media_player_fragment_container").click()
        self.d(resourceId="com.google.android.apps.plus:id/videoplayer").click()
        ret = self.d(resourceId="android:id/pause").exists
        self.d.press.back()
        return ret

    def videoPlayback(self, x=1):
        return self.elementOpen(self.isVideo, x)

    def videoDelete(self):
        self.openCameraFolder()
        self.d(description="More options").click.wait()
        self.d(textContains="Delete all").click.wait()
        self.d(text="Delete").click.wait()
        time.sleep(4)
        self.homeMenu().wait.exists(timeout=10000)
        self.homeMenu().click()
        self.d(text="Trash").click()
        self.d(description="More options").click()
        self.d(text="Empty trash").click()
        self.d(text="Empty trash", resourceId="android:id/button1").wait.exists(timeout=10000)
        self.d(text="Empty trash", resourceId="android:id/button1").click()

    def isPic(self):
        return self.d(resourceId="com.google.android.apps.plus:id/edit").exists

    def elementOpen(self, testElementFunc, x=1):
        self.openCameraFolder()
        time.sleep(1)
        for i in range(1, x + 1):
            if not self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=i).exists:
                break
            self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=i).click()
            assert testElementFunc(), "failed"
            self.d.press.back()
        else:
            return
        uiChildlast = UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=i - 1).info)
        canRecogizeEnd = False
        if uiChildlast.getBottom() - self.d.info[u'displayHeight'] > uiChildlast.getHeight() / 2:
            canRecogizeEnd = True
        print "can recogize end:", canRecogizeEnd
        uiGrid = UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid").info[u"bounds"])
        uiChild1 = UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=1).info[u"bounds"])
        uiChild2 = UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid").
                             child(index=1).down().info[u"bounds"])
        print uiChild1
        print uiChild1.getMidPoint()
        print uiChild2
        print uiChild2.getMidPoint()
        sx, sy = uiGrid.getMidPoint()
        dy = uiChild1.getMidPoint()[1]
        dy = uiChild2.getMidPoint()[1] - dy
        print sx, sy, sx, sy - dy, dy, uiChild1.getHeight()
        lineNum = 1
        element = self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=1)
        for k in range(2, x + 1):
            element = element.right()
            if element is not None:
                uiChildi = UiWindows(element.info)
            else:
                break
            if uiChildi.getMidPoint()[0] > uiChild1.getMidPoint()[0]:
                lineNum = lineNum + 1
            else:
                break
        print "linenNum:", lineNum
        nums = i - 1
        print "numbs:", nums
        self.d.swipe(sx, sy, sx, sy - dy * 1.3, 50)
        j = 0
        while i <= x:
            if j == lineNum:
                self.d.swipe(sx, sy, sx, sy - dy, 50)
                if canRecogizeEnd:
                    print UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid")
                                    .child(index=5).info)
                    print UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid").
                                    child(index=5).info).getBottom()
                    print self.d.info[u'displayHeight']
                    assert UiWindows(self.d(resourceId="com.google.android.apps.plus:id/grid")
                                     .child(index=nums / lineNum).info) \
                        .getBottom() > self.d.info[u'displayHeight'], "Failed to find"
                j = 0
            j = j + 1
            print "open:", i
            self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=(nums / lineNum + 1) * j - 1).click()
            assert testElementFunc(), "failed"
            self.d.press.back()
            self.d(resourceId="com.google.android.apps.plus:id/grid").wait.exists(timeout=10000)
            i = i + 1

    def picOpen(self, x=1):
        return self.elementOpen(self.isPic, x)

    def picDelete(self):
        self.videoDelete()

    def openFist(self):
        self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=1).click()

    def playNextPic(self):
        self.d(scrollable=True).scroll.horiz()

    def checkAlbum(self):
        self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=1).click()
        time.sleep(0.5)
        assert self.d(resourceId="com.google.android.apps.plus:id/edit").exists or \
            self.d(resourceId="com.google.android.apps.plus:id/media_player_fragment_container").exists, "failed"
        self.d.press.back()

    def checkDifferentAlbums(self):
        notFolder = 0
        for i in range(50):
            if not self.d(resourceId="com.google.android.apps.plus:id/tiles").child(index=i) \
                .child(resourceId="com.google.android.apps.plus:id/collection_title").exists:
                notFolder = notFolder + 1
                if notFolder > 4:
                    break
                continue
            notFolder = 0
            self.d(resourceId="com.google.android.apps.plus:id/tiles").child(index=i) \
                .child(resourceId="com.google.android.apps.plus:id/collection_title").click()
            self.checkAlbum()
            self.d.press.back()

    def editPicture(self):
        self.d(resourceId="com.google.android.apps.plus:id/edit").click()
        i = 0
        while self.d(resourceId="com.google.android.apps.plus:id/filter_list").child(index=i).exists:
            self.d(resourceId="com.google.android.apps.plus:id/filter_list").child(index=i).click()
            j = 0
            while self.d(resourceId="com.google.android.apps.plus:id/filter_parameter_panel_container") \
                .child(index=j).exists:
                self.d(resourceId="com.google.android.apps.plus:id/filter_parameter_panel_container") \
                    .child(index=j).click()
                time.sleep(3)
                j = j + 1
            j = 0
            while self.d(resourceId="com.google.android.apps.plus:id/preset_list").child(index=j).exists:
                self.d(resourceId="com.google.android.apps.plus:id/preset_list").child(index=j).click()
                time.sleep(3)
                j = j + 1
            self.d(resourceId="com.google.android.apps.plus:id/cancel_button").click()
            i = i + 1
        self.d(text="Done").click()

    def more_options(self):
        self.d(className="android.view.View", index=1).click.wait()
        self.d(description="More options", className="android.widget.ImageButton").click.wait()

    def slideshow(self, duration):
        """click more options and slideshow"""
        difftime = 0
        starttime = datetime.datetime.now()
        print "duration: %d" % duration
        while difftime < duration:
            self.d(className="android.view.View", index=1).click.wait()
            self.d(description="More options", className="android.widget.ImageButton").click.wait()
            self.d(text="Slideshow").click.wait()
            time.sleep(180)
            self.d.press.back()
            time.sleep(2)
            endtime = datetime.datetime.now()
            difftime = (endtime - starttime).seconds
            print difftime

    def display_image(self, display_number):
        """display image"""
        self.d(className="android.view.View", index=1).click.wait()
        for i in range(display_number):
            self.playNextPic()

    def setTimeToSec(self, time):
        time = time.split(":")
        i = 1
        temp = 0
        for s in time[::-1]:
            temp += int(s) * i
            i *= 60
        return int(temp)

    def playback_video_un_QR_code_photoplus(self, playTime=0, videoIndex=0, flag=False, stoptime=-1):
        x = self.d.info["displayWidth"]
        y = self.d.info["displayHeight"]
        print "stoptime is ", stoptime
        stoptime = int(stoptime)
        time.sleep(3)
        while self.d(className="android.widget.ImageButton", description="Navigate up").exists:
            self.d.press("back")
        self.homeMenu().click()
        self.d(text="On device").click()
        time.sleep(2)
        test_file_folder = "otctest"
        if self.d(text=test_file_folder).exists:
            pass
        elif self.d(text="sdcard1").exists:
            test_file_folder = "sdcard1"
        else:
            try:
                self.d(scrollable=True).scroll.to(text=test_file_folder)
            except Exception as e:
                print e
                assert False, "Can't find %s folder!" % test_file_folder
            time.sleep(2)
        self.d(text=test_file_folder).click()
        time.sleep(1)
        assert self.d(resourceId="com.google.android.apps.plus:id/tile_row").child(index=videoIndex).exists or \
            self.d(resourceId="com.google.android.apps.plus:id/grid") \
            .child(index=videoIndex).exists, "There is no video in photo"
        try:
            if self.d(resourceId="com.google.android.apps.plus:id/tile_row").exists:
                self.d(resourceId="com.google.android.apps.plus:id/tile_row").child(index=videoIndex).click()
            if self.d(resourceId="com.google.android.apps.plus:id/grid").exists:
                self.d(resourceId="com.google.android.apps.plus:id/grid").child(index=videoIndex).click()
        except JsonRPCError:
            assert False, "There is no video in photo"
        for i in range(20):
            if self.d(resourceId="com.google.android.apps.plus:id/delete").exists:
                break
            elif self.d(text="DONE").exists:
                self.d(resourceId="com.google.android.apps.plus:id/tile_row").child(index=videoIndex).click()
                time.sleep(2)
                self.d(resourceId="com.google.android.apps.plus:id/tile_row").child(index=videoIndex).click()
            else:
                time.sleep(1)
        assert self.d(resourceId="com.google.android.apps.plus:id/delete").exists, "enter play page failed"
        ttInt = 0
        if flag:
            videoLength = playTime
        else:
            self.d(description="More options").click()
            self.d(text="Details").click()
            if self.d(text="Duration").exists:
                tt = self.d(resourceId="com.google.android.apps.plus:id/exif_detail_list") \
                    .child(index=2).child(index=1).text
            else:
                tt = "00:10"
            print "Total play time is : " + str(tt)
            videoLength = self.setTimeToSec(tt)
            self.d.press.back()
            print "videoLength is ", videoLength
        print "Can't play video. status is ", self.d(text="Can't play video.").exists
        assert not self.d(text="Can't play video.").exists, "show Can't play video."
        time.sleep(2)
        self.d.click(x / 2, y / 2)
        time.sleep(1)
        node = (0, y / 2 - 100, x, y / 2 + 100)
        timeNow = time.time()
        while True:
            assert not self.d(text="Can't play video.").exists, "show Can't play video."
            img0 = otcImage.cropScreenShot(self.d, node, save=True)
            if time.time() - timeNow <= videoLength:
                self.d.click(x / 2, y / 2)
            ct = None
            tt = None
            for i in range(10):
                if self.d(resourceId="android:id/time_current").exists and self.d(resourceId="android:id/time").exists:
                    try:
                        ct = self.d(resourceId="android:id/time_current").text
                        tt = self.d(resourceId="android:id/time").text
                    except Exception as e:
                        print e
                        self.d.click(x / 2, y / 2)
                        continue
                    break
                else:
                    print str(i) + "times,don't find current time or total time"
                    self.d.click(x / 2, y / 2)
            if ct and tt:
                ctInt = self.setTimeToSec(ct)
                ttInt = self.setTimeToSec(tt)
                print "Total play time is : " + str(tt) + " current play time is " \
                    + str(ct) + " videoLength is " + str(videoLength)
                print "current time is ", ctInt, "total time is ", ttInt, "ctInt < ttInt is ", ctInt <= ttInt
                assert ctInt <= ttInt or (ttInt == 0 and ctInt > 0), "current time is over than total time"
                time.sleep(3)
                img1 = otcImage.cropScreenShot(self.d, node)
                ssim = float(otcImage.calc_similar(img0, img1))
                print "ssim is ", ssim
                assert ssim <= 0.99, "video playback has been False"
            print "stoptime and stoptime > videoLength is", stoptime and stoptime > videoLength
            if stoptime >= videoLength or stoptime == -1:
                useStopTime = videoLength
            else:
                useStopTime = stoptime
            print "useStopTime=", useStopTime
            if time.time() - timeNow + 8 > useStopTime:
                print "play time", time.time() - timeNow
                break
        self.dut.press.back()
        if not self.d(text="otctest").exists:
            self.dut.press.back()

    def enter_photo_plus_from_home(self):
        '''
        former name : enterPhotoPlusFromHome
        '''
        self.dut.press.back()
        g_common_obj.launch_app_from_home_sc("Photos")
        time.sleep(3)
        assert self.d(text="Photos").exists, "enter photo plus from home failed"

    def launchPhotoPlus(self):
        g_common_obj.launch_app_am("com.google.android.apps.plus", '.phone.ConversationListActivity')
        time.sleep(3)

    def enter_image_in_photo_plus(self, line=0, position=0):
        self.d(resourceId="com.google.android.apps.plus:id/tiles").child(index=line).child(index=position).click()
        time.sleep(3)

    def get_photo_plus_image_show(self):
        img0 = None
        for index in range(10):
            print "try " + str(index) + "times to find image show node"
            try:
                node = self.d(resourceId="com.google.android.apps.plus:id/photo_hashtag_fragment_container")
                img0 = otcImage.getWidgetImage(self.d, node)
            except:
                print "savePic Failed"
            if img0:
                break
        return img0

    def get_photo_plus_image_show_string(self, img0=None):
        pass

    def check_image_in_photo_plus(self, fileName, ssim=0.8):
        img0 = self.get_photo_plus_image_show()
        if ".webp" in fileName:
            fileName = fileName.replace(".webp", ".jpg")
        print fileName
        import Image
        img1 = Image.open(fileName)
        dealSsim = otcImage.calc_similar(img0, img1)
        assert dealSsim > ssim, "display failed. ssim is " + str(dealSsim) + "expected values is" + str(ssim)

    def view_image_in_photo_plus(self, fileName, ssim, line=0, position=0):
        self.enter_image_in_photo_plus(line, position)
        time.sleep(3)
        return self.check_image_in_photo_plus(fileName, ssim)

    def view_image_detail(self, line=0, position=0):
        self.enter_image_in_photo_plus(line, position)
        self.d.click(765, 76)
        self.d(text="Details").click()
        results = {}
        for i in range(5):
            try:
                key = self.d(resourceId="com.google.android.apps.plus:id/exif_detail_list") \
                    .child(index=i).child(index=0).text
                value = self.d(resourceId="com.google.android.apps.plus:id/exif_detail_list") \
                    .child(index=i).child(index=1).text
            except:
                key = None
                value = None
                print "found None , loop %s times" % str(i)
            try:
                key = key.decode('utf-8')
                value = value.decode('utf-8')
            except:
                reload(sys)
                sys.setdefaultencoding('utf-8')
                key = key.decode('utf-8')
                value = value.decode('utf-8')
            print "key is ", key
            print "value is ", value
            if key:
                results[key] = value
                print "key is [" + key + "] value is " + value
            else:
                break
        return results

    def push_image_photo_plus(self, number):
        fileMap = {}
        for count in range(1, number + 1):
            orgFileName = count % 50
            if orgFileName == 0:
                orgFileName = 50
            self.push_file(str(orgFileName) +
                           ".png", "autotest/imageFile/num_image", str(count) + ".png", "/sdcard/otctest")
            fileMap[count] = orgFileName
            print str(count) + ".png ", orgFileName
        g_common_obj.adb_cmd_capture_msg("am broadcast -a \
                                         android.intent.action.MEDIA_MOUNTED --ez read-only false -d file://sdcard")
        return fileMap

    def get_photo_index_in_photo_plus(self, total, number):
        index = total - number
        line = index / 3
        pos = index % 3
        return line, pos

    def enter_photo_plus_on_device(self):
        self.d(resourceId="android:id/home").click()
        time.sleep(3)
        assert self.d(text="On Device").exists, "enter photo plus home failed"
        self.d(text="On Device").click()
        time.sleep(3)
        assert self.d(text="otctest").exists, "enter photo plus on devices failed"

    def enter_menu_page(self):
        self.d(resourceId="android:id/action_bar") \
            .child_by_description("More options", className="android.widget.ImageButton").click()
        assert self.d(text="Help").exists, "enter photo plus menu failed"

    def enter_slide_show(self):
        self.d(text="Slideshow").click()

    def check_slide_show(self):
        last = None
        times = 0
        while True:
            time.sleep(3)
            words = self.get_photo_plus_image_show_string()
            if last and last in words:
                times = times + 1
                print "times is ", times
                if times > 2:
                    assert str(words) == "1", 'slide show stopped at image ' + str(words)
            else:
                times = 0
            last = words

    def check_slide_stopped(self):
        last = None
        times = 5
        sameTime = 0
        for t in range(times):
            time.sleep(3)
            words = self.get_photo_plus_image_show_string()
            if last and last in words:
                sameTime = sameTime + 1
                print sameTime
            last = words
        assert sameTime > 2, "slide not stopped"

    def zoom_in_out_image(self, ssim=0.99):
        img0 = self.get_photo_plus_image_show()
        words0 = self.get_photo_plus_image_show_string(img0)
        self.d.click(400, 550)
        self.d.click(400, 550)
        time.sleep(3)
        img1 = self.get_photo_plus_image_show()
        words1 = self.get_photo_plus_image_show_string(img1)
        sim = float(otcImage.calc_similar(img0, img1))
        print "ssim is " + str(sim) + " expected values is " + str(ssim)
        print "before is " + str(words0) + " after values is " + str(words1)
        assert not sim > ssim, "double click,image not zoom in,ssim is " + str(sim) + " expected values is " + str(ssim)
        assert not (words0 not in words1 and words1 not in words0), \
            "double click,image zoom display failed ,before is " \
            + str(words0) + " after values is " + str(words1)

    def exit_photo_plus(self):
        self.dut.press.back()
        time.sleep(3)
        assert not self.d(resourceId="com.google.android.apps.plus:id/tiles",
                          packageName="com.google.android.apps.plus").exists, "exit photo plus to home failed"

    def push_file(self, originalName, originalPath, fileName=None, path="/sdcard/otctest"):
        if not fileName:
            fileName = originalName
        g_common_obj.adb_cmd_common("push %s/%s %s/%s" % (originalPath, originalName, path, fileName))
