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
import traceback
import os
import unittest

from testlib.util.common import g_common_obj
from testlib.util.config import TestConfig


class UIATestBase(unittest.TestCase):
    """
    Android UI Automataed Test Case Implementation

    """
    # Configuration parser
    config = TestConfig()

    def setUp(self):
        super(UIATestBase, self).setUp()

        if 'TEST_DATA_ROOT' not in os.environ:
            raise Exception('env \'TEST_DATA_ROOT\' not defined !')

        # Contexts object is injected by nose reporter plugin.
        if hasattr(self, 'contexts'):
            g_common_obj.set_context(self.contexts)

        user_log_dir = os.environ.get('PYUNIT_USER_LOG_DIR', None)

        if (user_log_dir):
            g_common_obj.globalcontext.user_log_dir = user_log_dir

        # Start the execption handling.
        g_common_obj.start_exp_handle()
        g_common_obj.back_home()

    def tearDown(self):
        super(UIATestBase, self).tearDown()
        # Stop the execption handling.
        g_common_obj.stop_exp_handle()
        g_common_obj.back_home()
        # Restart server
        # g_common_obj.restart_server()

    def assert_exp_happens(self):
        # Assert the execption hanppening
        g_common_obj.assert_exp_happens()

    @property
    def failureException(self):
        try:
            scname = os.path.join(g_common_obj.globalcontext.user_log_dir +
                                  "screenshot.png")
            g_common_obj.take_screenshot(scname)
        except Exception as e:
            print e.message, e.args
            traceback.print_exc()
