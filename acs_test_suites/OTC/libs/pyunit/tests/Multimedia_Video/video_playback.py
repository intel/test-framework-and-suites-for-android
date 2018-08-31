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

from testlib.util.common import g_common_obj
from testlib.multimedia.mum_photos_impl import PhotosImpl
from testlib.multimedia.testcasebase import TestCaseBase
from testlib.multimedia.multimedia_setting import MultiMediaSetting, MultiMediaHandle, MultiMediaBasicTestCase


class VideoPlayBack(TestCaseBase):
    """
    @summary: Test Video PlayBack
    """

    def setUp(self):
        """
        @summary: set up
        @return: None
        """
        super(VideoPlayBack, self).setUp()
        self.d = g_common_obj.get_device()
        self._test_name = __name__
        print "[Setup]: %s" % self._test_name
        g_common_obj.stop_app_am("com.google.android.apps.plus")
        g_common_obj.stop_app_am("com.google.android.apps.photos")
        # Unlock screen
        g_common_obj.adb_cmd_capture_msg("input keyevent 82")

    def tearDown(self):
        """
        @summary: tear tearDown
        @return: None
        """
        super(VideoPlayBack, self).tearDown()
        print "[Teardown]: %s" % self._test_name
        g_common_obj.stop_exp_handle()
        time.sleep(3)

    def appPrepare2(self, case_name, model=1):
        cfg_file = os.path.join(os.environ.get('TEST_DATA_ROOT', ''), 'tests.tablet.mum_auto_video.conf')
        self.video = PhotosImpl(self.config.read(cfg_file, case_name))

        self.multimedia_handle = MultiMediaHandle()
        self.multimedia_setting = MultiMediaSetting(cfg_file)
        self.multimedia_setting.clearFolder(self.video.cfg.get("remove_video"))
        time.sleep(2)
        if model == 1:
            self.push_path = self.multimedia_setting.push_file(self.video.cfg.get("push_video"),
                                                               self.video.cfg.get("datapath"))

        self.multimedia_setting.install_apk("video_apk")
        self.multimedia_setting.install_apk("alarm_apk")
        self.video.set_orientation_n()
        # Unlock screen
        g_common_obj.adb_cmd_capture_msg(self.video.cfg.get("refresh_sd"))
        g_common_obj.adb_cmd_capture_msg("input keyevent 82")

    def videoPlayBack(self, case_name, t_bigfileskiptime=0):
        print "run case is " + str(case_name)
        self.appPrepare2(case_name)
        push_folder = os.path.split(os.path.split(self.push_path)[0])[-1]
        if self.multimedia_setting.get_android_version() == "O":
            self.multimedia_handle.launchVideoApp()
            self.multimedia_handle.videoPlayBack(self.push_path)
            assert self.multimedia_handle.checkVideoPlayBack(), 'video play failed'
        else:
            self.video.launchPhotos(push_folder)
            time.sleep(2)
            self.multimedia_handle.checkVideoPlayBackWithPhotoApp(stoptime=self.video.cfg.get("stop_time"),
                                                                  bigfileskiptime=t_bigfileskiptime)
        print "case " + str(case_name) + " is pass"

    def testVideoPlayBack(self, case_name):
        MultiMediaBasicTestCase().testVideoPlayBack(case_name)

    def checkVideoPlayBack(self, s=60):
        return self.multimedia_handle.checkVideoPlayBack(s)

    def testMPEG4_352_288_24fps_144kbps_aaclc_22_05kHz_38kbps_Mono_3GP(self):
        """
        This test used to test Video playback
        The test case spec is following:
        1. Launch play video app
        2. Play video
        """
        self.testVideoPlayBack("test_API_video_playback_008")

    def testVideoPlayback_MKV_VP8_640x360_25fps_Vorbis_44KHz_128Kbps(self):
        """
        This test used to test Video playback
        The test case spec is following:
        1. Launch photos
        2. Play video
        3. Former name: testVideoPlayBack_034
        """
        self.videoPlayBack("test_video_playback_034")

    def testPlayback_H264_HP_1080P_60fps_50Mbps_AAC_LC_48KHz_320Kbps_mp4(self):
        """
        This test used to test Video playback
        The test case spec is following:
        1. Launch play video app
        2. Play video
        """
        self.videoPlayBack("test_API_video_playback_035")
