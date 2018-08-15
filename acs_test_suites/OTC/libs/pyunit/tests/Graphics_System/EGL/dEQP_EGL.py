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
from testlib.graphics.dEQP_impl import deqp_impl
from testlib.util.uiatestbase import UIATestBase


class RundEQP(UIATestBase):

    def setUp(self):
        super(RundEQP, self).setUp()
        deqp_impl.setup()

    def tearDown(self):
        super(RundEQP, self).tearDown()

    def test_EGL_get_proc_address_extension_32(self):
        print("[RunTest]: %s" % self.__str__())
        deqp_impl.run_case("dEQP-EGL.functional.get_proc_address.extension*")
