#!/usr/bin/python
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
import unittest
import re
import os
from testlib.util.log import Logger
from testlib.util.common import g_common_obj
from testlib.util.config import TestConfig


LOG = Logger.getlogger(__name__)


def _install(device, pkg_path):
    cmd = 'install %s' % pkg_path
    return device.adb_cmd_common(cmd)


def _uninstall(device, pkgname):
    cmd = 'uninstall %s' % pkgname
    return device.adb_cmd_common(cmd)


def _instrument(device, test_case, test_pkg, inst_componment):
    cmd = 'am instrument -w -r -e class %s %s/%s' % (
        test_case, test_pkg, inst_componment)
    ret = device.adb_cmd_capture_msg_ext(cmd, time_out=900)
    vmap = {}
    result_tag = 'INSTRUMENTATION_RESULT:'
    code_tag = 'INSTRUMENTATION_CODE:'
    code_match = re.search(code_tag, ret)
    result_match = re.search(result_tag, ret)
    if code_match and result_match:
        results = ret[result_match.end():code_match.start()]
        vmap['raw'] = results
        results = results.strip().replace('\r\n', ' ')
        index = results.index('=')
        key = results[0: index]
        value = results[(index + 1):]
        vmap[key] = value
    return vmap


class InstrumentedBaseImpl():
    """
    Android Instrumented Test Wrapper
    """
    inst_runner = 'android.test.InstrumentationTestRunner'
    test_pkg = None
    pkg_names = None
    pkg_files = None
    apk_repo_path = ''

    def intialize(self):
        self.device = g_common_obj.get_test_device()
        if self.pkg_files is None:
            return
        for _file in self.pkg_files:
            _install(self.device, os.path.join(self.apk_repo_path, _file))

    def finalize(self):
        if self.pkg_names is None:
            return
        for _pkg in self.pkg_names:
            _uninstall(self.device, _pkg)

    def instr_run(self, test_case):
        if self.test_pkg is None:
            return
        output = _instrument(self.device, test_case,
                             self.test_pkg, self.inst_runner)
        print "-----GFX_debug----output-------"
        print output
        print "---GFX_debug--output['raw']------"
        print output['raw']
        print "----GFX_debug-----output['stream']------------"
        print output['stream']
        print "-----GFX_debug-----output['stream'].find('.E')--------"
        print output['stream'].find('.E')
        print "------GFX_debug------output['stream'].find('.F')---------"
        print output['stream'].find('.F')
        assert 'stream' in output, 'invalid raw output:\n %s' % output['raw']
        assert output['stream'].find('.E') == -1, output['raw']
        assert output['stream'].find('.F') == -1, output['raw']


class InstrumentedCtsBaseImpl(InstrumentedBaseImpl):
    """
    Android CTS Instrumented Test Wrapper
    """
    # inst_runner = 'android.test.InstrumentationCtsTestRunner'
    inst_runner = 'android.support.test.runner.AndroidJUnitRunner'


class InstrumentationTestBase(unittest.TestCase):
    """
    Android Instrumenation Test Case Implementation

    """
    # Configuration parser
    config = TestConfig()

    def setUp(self):
        super(InstrumentationTestBase, self).setUp()

        # Contexts object is injected by nose reporter plugin.
        if hasattr(self, 'contexts'):
            g_common_obj.set_context(self.contexts)

        # Start the execption handling.
        g_common_obj.start_exp_handle()

    def tearDown(self):
        super(InstrumentationTestBase, self).tearDown()

        # Stop the execption handling.
        g_common_obj.stop_exp_handle()

    def assert_exp_happens(self):
        # Assert the execption hanppening
        g_common_obj.assert_exp_happens()
