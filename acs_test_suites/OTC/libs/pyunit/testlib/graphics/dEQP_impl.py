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
import re
from subprocess import Popen, PIPE
from testlib.util.log import Logger
from testlib.util.common import g_common_obj
from testlib.graphics.common import pkgmgr, window_info, environment_utils


LOG = Logger.getlogger(__name__)


class dEQPImpl(object):

    def __init__(self):
        self.os_ver = environment_utils.get_android_version()
        self.package_name = "com.drawelements.deqp"
        self.inside_output = "/storage/emulated/0/TestResult.qpa"
        self._mustpass_path = '/storage/emulated/0/'
        self._mustpass_list = ['vk-master.txt', 'egl-master.txt',
                               'gles2-master.txt', 'gles3-master.txt', 'gles31-master.txt']
        self._failure_log = os.path.join(g_common_obj.globalcontext.user_log_dir, 'deqp_failures.log')
        self._raw_deqp_result = os.path.join(g_common_obj.globalcontext.user_log_dir, 'deqp_test_result.log')
        self._extension_list = os.path.join(g_common_obj.globalcontext.user_log_dir, 'extension_list.log')

    def setup(self):
        self._check_dependency()

    def run_case(self, case_name, check_extensions=False, extension_name=''):

        _inside_output = self.inside_output
        # Add inside function for further check extension tests.

        def _get_extension_list():
            inside_content = g_common_obj.adb_cmd_capture_msg('cat %s' % _inside_output)
            return re.findall(r'\ +?<Text>(.+)</Text>', inside_content)
        # Start run deqp test.
        _results = {'Passed': 0, 'Failed': 0, 'Not supported': 0, 'Warnings': 0}
        LOG.debug("Testcase: %s" % (case_name))
        setlog_cmd = "setprop log.tag.dEQP DEBUG"
        cmd = "am start -S -n com.drawelements.deqp/android.app.NativeActivity -e cmdLine \"" \
              "deqp --deqp-log-filename=%s --deqp-case=%s\"" % (self.inside_output, case_name)
        g_common_obj.adb_cmd_capture_msg(repr(setlog_cmd))
        g_common_obj.adb_cmd_capture_msg(repr(cmd))
        # failures = ['Fail', 'ResourceError', 'Crash', 'Timeout', 'InternalError']
        s_time = time.time()
        while time.time() - s_time < 900:
            cur_window = window_info.get_current_focus_window()
            time.sleep(2)
            if self.package_name not in cur_window:
                LOG.debug("Test finished.")
                # Save deqp results to log.
                g_common_obj.adb_cmd_capture_msg('logcat -d -s dEQP > %s' % self._raw_deqp_result)
                # Handle results.
                logs = Popen('cat %s' % self._raw_deqp_result, shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
                for i in _results.keys():
                    chk_log = r"logcat -d -s dEQP | grep -oe '%s:\ \+[0-9]\+/[0-9]\+'" % i
                    try:
                        output = g_common_obj.adb_cmd_capture_msg(chk_log)
                        num = output.split(' ')[-1].split('/')[0]
                        _results[i] = int(num)
                    except ValueError as e:
                        raise Exception("Got error when running tests: %s" % e)

                assert sum(_results.values()) != 0, LOG.debug("Test not run.")

                LOG.debug("Raw summary: %s" % _results)
                if _results['Failed'] > 0:
                    raw_failures = re.findall(r'Test case .(dEQP-.*[\d|\w]).+\n.+?dEQP +: +Fail.+?.', logs)
                    head_name = raw_failures[0].split('.')[0].split('-')[-1].lower()
                    real_failures = []
                    for i in raw_failures:
                        _is_mustpass = "cat %s/%s-master.txt | grep -I \'%s\'" % (self._mustpass_path, head_name, i)
                        chk = g_common_obj.adb_cmd_capture_msg(_is_mustpass)
                        if chk == '':
                            _results['Failed'] -= 1
                            _results['Not supported'] += 1
                        else:
                            real_failures.append(i)
                    if len(real_failures) > 0:
                        f = open(self._failure_log, 'w')
                        for i in real_failures:
                            f.write(i + '\n')
                        f.close()
                    LOG.debug("Final summary: %s" % _results)
                # Handle event for extension list check.
                if check_extensions:
                    ext_list = _get_extension_list()
                    f = open(self._extension_list, 'w')  # Save extension list to logfile.
                    for el in ext_list:
                        f.write(el + '\n')
                    f.close()
                    LOG.info("Extension list saved in: %s" % self._extension_list)
                    assert extension_name in ext_list, "%s is not in this test." % extension_name
                    LOG.info("%s is found in this test." % extension_name)
                    return True
                else:
                    if _results['Failed'] == 0:
                        LOG.info("All tests passed.")
                        return True
                    else:
                        raise Exception("dEQP test failed, details refer to log file: %s" % self._failure_log)
            else:
                time.sleep(3)
        raise Exception("Test timeout.")

    def _check_dependency(self):
        g_common_obj.root_on_device()
        g_common_obj.remount_device()
        g_common_obj.adb_cmd_capture_msg("logcat -G 16M")
        g_common_obj.adb_cmd_capture_msg("logcat -c")
        selection = {'L': 'apk_l',
                     'M': 'apk_m',
                     'N': 'apk_n',
                     'O': 'apk_o',
                     'P': 'apk_p'}
        if not pkgmgr.query_package_name(self.package_name):
            try:
                file_path = environment_utils.get_resource_file(
                    'tests.common.dEQP.conf', 'dEQP', selection[self.os_ver])
                pkgmgr.apk_install(file_path)
            except KeyError as e:
                print("DEQP app version not match with android os: %s" % str(e))
            # Need to update above when new version is released.
        for i in self._mustpass_list:
            op = g_common_obj.adb_cmd_capture_msg('ls %s%s' % (self._mustpass_path, i))
            if 'No such file' in op or op == '':
                file_path = environment_utils.get_resource_file(
                    'tests.common.dEQP.conf', 'dEQP', i.split('-')[0] + '_mustpass')
                if not g_common_obj.push_file(file_path, self._mustpass_path):
                    raise Exception("Fail to push must pass list, please use script to get resource before test.")


deqp_impl = dEQPImpl()
