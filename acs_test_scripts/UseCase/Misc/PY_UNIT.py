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
from acs_test_scripts.UseCase.UseCaseBase import UseCaseBase
from acs.UtilitiesFWK.Utilities import Global
from acs.Core.PathManager import Paths
from acs.Device.DeviceLogger.LogCatLogger.LogCatReaderThread import LogCatReaderThread  # NOQA
from acs.Core.Report.Live.LiveReporting import LiveReporting

import unittest
import tempfile
import shutil
import sys
import os
import re


ANDROID_TOMBSTONE_PATH = '/data/tombstones'
ANDROID_ANRLOGS_PATH = '/data/anr/traces.txt'


class Context:
    """
    GolbalContext injection, take from:
    testlib/util/globalcontext.py
    """

    def __init__(self, serial, root):
        self.device_serial = serial
        self.devicetype = "default"
        self.language = "en.US"
        self.user_log_dir = os.path.join(root, 'logs/')
        self.sc_tmp_dir = os.path.join(root, 'sc/')

        def create_dir(d):
            if not os.path.isdir(d):
                os.mkdir(d)

        create_dir(root)
        create_dir(self.user_log_dir)
        create_dir(self.sc_tmp_dir)

        self.anr_captured = False
        self.crash_captured = False


class PyUnit(UseCaseBase):

    """
    Generic use case that run python unittest class and extract the verdict
    from the unittest result
    """

    def _run_cmd(self, cmd, timeout=30):
        return self._device.run_cmd(cmd, timeout, silent_mode=True)

    def _setup(self):
        self._upload_folder = tempfile.mkdtemp()

        cmd_line = self._device.get_config("logcatCmdLine",
                                           "adb shell logcat -v threadtime")
        self._logcat = LogCatReaderThread(device_handle=self._device,
                                          logger=self._logger,
                                          logcat_cmd_line=cmd_line,
                                          enable_writer=True)
        self._logcat.set_output_path(self._get_rel_path('logcat.txt'))
        self._logcat.start()
        # user_log_dir
        user_log_dir = self._get_rel_path('logs')
        os.mkdir(user_log_dir)
        os.environ['PYUNIT_USER_LOG_DIR'] = user_log_dir

    def _cleanup(self):
        self._run_cmd('adb shell logcat -c')
        self._run_cmd('adb shell dmesg -c')
        self._run_cmd('adb shell rm ' + ANDROID_ANRLOGS_PATH)
        self._run_cmd('adb shell rm %s/*' % ANDROID_TOMBSTONE_PATH)
        self._run_cmd('rm -rf %s' % self._upload_folder)

    def _collect_logs(self):
        os.mkdir(self._get_rel_path('system'))

        def save_cmd_output(cmd):
            opath = self._get_rel_path('system/%s.txt' % cmd.replace(' ', '_'))
            ret, output = self._run_cmd('adb shell %s' % cmd)
            with open(opath, 'w') as fp:
                fp.write(output)

        def dumpsys(comp):
            save_cmd_output('dumpsys ' + comp)

        # dumpsys
        dumpsys('window')
        dumpsys('cpuinfo')
        dumpsys('diskstats')
        dumpsys('wifi')
        dumpsys('activity')
        dumpsys('meminfo')

        save_cmd_output('dmesg')
        save_cmd_output('ps')

        self._device.screenshot(filename=self._get_rel_path('screen.png'))

    def _upload(self):
        zip_file = shutil.make_archive(tempfile.mktemp(),
                                       'zip', self._upload_folder)
        lr = LiveReporting.instance()
        lr.send_test_case_resource(zip_file, display_name='logs')
        self._run_cmd('rm ' + zip_file)

    def _tear_down(self, upload=True):
        self._logcat.stop()
        if upload:
            self._collect_logs()
            self._upload()
        self._cleanup()

    def _get_rel_path(self, path):
        return os.path.join(self._upload_folder, path)

    def set_up(self):
        UseCaseBase.set_up(self)

        def path_join(*args):
            return os.path.normpath(os.path.join(*args))

        # get script root
        env_script_root = os.environ.get('PYUNIT_script_root', None)
        data_root_rel = self._tc_parameters.get_param_value('TEST_DATA_ROOT')

        if (env_script_root is not None):
            script_root = env_script_root
        else:
            matchobj = re.match(r'(.*)TC\/PY_UNIT\/(.*)', self._name, re.I)
            if (matchobj):
                extra_sub_folders = matchobj.group(1) + 'libs/pyunit/'
            else:
                raise Exception("Couldn't parse the script root path, \
                                please set PYUNIT_script_root!")
            script_root = path_join(Paths.EXECUTION_CONFIG, extra_sub_folders)
        test_data_root = path_join(script_root, data_root_rel)
        os.environ['TEST_DATA_ROOT'] = test_data_root
        sys.path.insert(1, script_root)

        # find case_name
        case_name = self._tc_parameters.get_param_value('TEST_CASE')
        self._logger.info("[PyUnit] case_name: " + case_name)
        module_name = '.'.join(case_name.split('.')[:-2])
        self._logger.info("[PyUnit] module_name: " + module_name)
        # load test case
        self.case_module = module_name
        loader = unittest.TestLoader()
        loader.discover(script_root, '*.py')
        self.suite = loader.loadTestsFromName(case_name)

        # Add additional paramters
        acs_params = {}
        crt = self._global_conf.campaignConfig.get("campaignReportTree")
        acs_params["report_path"] = crt.get_report_path()

        try:
            for suite in self.suite:
                if isinstance(suite, unittest.TestCase):
                    suite._acs_params = acs_params
                    break
                for test in suite:
                    test._acs_params = acs_params
        except:
            self._logger.error("SKIP set up acs_params.")

        self.runner = unittest.TextTestRunner(verbosity=0)
        return Global.SUCCESS, "SUCCESS"

    def run_test(self):
        '''
        Execute test case
        '''
        UseCaseBase.run_test(self)
        self._setup()

        result = self.runner.run(self.suite)
        ret = []
        if result.wasSuccessful():
            ret = Global.SUCCESS, "SUCCESS"
        else:
            if result.errors:
                ret = Global.FAILURE, result.errors[0][1]
            elif result.failures:
                ret = Global.FAILURE, result.failures[0][1]
            elif result.skipped:
                ret = Global.BLOCKED, result.skipped[0][1]
            else:
                ret = Global.BLOCKED, "unknown reason"
            self._logger.error(ret[1])
            # handling INCONCLUSIVE
            if ret[1].find("{INCONCLUSIVE}") != -1:
                ret = Global.INCONCLUSIVE, ""

        self._tear_down(ret[0] != Global.SUCCESS)
        return ret

    def tear_down(self):
        UseCaseBase.tear_down(self)
        return Global.SUCCESS, "SUCCESS"
