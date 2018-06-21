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
import unittest

from testlib.util.common import g_common_obj
from testlib.util.config import TestConfig


class CoreTestBase(unittest.TestCase):
    """
    Android Core Test Case Implementation

    """
    # Configuration parser
    config = TestConfig()

    def setUp(self):
        super(CoreTestBase, self).setUp()

        if 'TEST_DATA_ROOT' not in os.environ:
            raise Exception('env \'TEST_DATA_ROOT\' not defined !')

        # Contexts object is injected by nose reporter plugin.
        if hasattr(self, 'contexts'):
            g_common_obj.set_context(self.contexts)

    def tearDown(self):
        super(CoreTestBase, self).tearDown()
