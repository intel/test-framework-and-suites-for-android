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
from testlib.graphics.common import window_info


class RundEQP(UIATestBase):

    def setUp(self):
        super(RundEQP, self).setUp()

    def tearDown(self):
        super(RundEQP, self).tearDown()

    def test_OpenGLES_32_Support_dumpsys_SurfaceFlinger(self):
        print("[RunTest]: %s" % self.__str__())
        assert window_info.check_dumpsys_SurfaceFlinger_info(keyword="gles", assertword="OpenGL ES 3.2"), \
            "OpenGL ES version is not 3.2!"
