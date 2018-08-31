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


from testlib.util.uiatestbase import UIATestBase
from testlib.multimedia.multimedia_log import MultimediaLogger


class TestCaseBase(UIATestBase):
    """
    Camera UI Automataed Test Case Implementation

    """

    def setUp(self):
        super(TestCaseBase, self).setUp()
        self.logger = MultimediaLogger.instance()
        self.logger.addFileHandler()

    def tearDown(self):
        super(TestCaseBase, self).tearDown()
        self.logger.debug("===== Set MultimediaLogger instance to None====")
        self.logger.removeHanlders()
        MultimediaLogger.destory()
