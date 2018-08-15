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
from testlib.util.common import g_common_obj
from testlib.util.uiatestbase import UIATestBase
from testlib.graphics.display_metrics_report_impl import d_metricsreport_impl


class DisplayMetricsReport(UIATestBase):

    def setUp(self):
        super(DisplayMetricsReport, self).setUp()
        g_common_obj.root_on_device()

    def tearDown(self):
        super(DisplayMetricsReport, self).tearDown()

    def test_Display_MetricsReport(self):
        print("[RunTest]: %s" % self.__str__())
        print("1.[Debug] compare dumpsys size with real size")
        d_metricsreport_impl.compare_dumpsys_size_with_real_size()
        print("2.[Debug] compare dumpsys density with real density")
        d_metricsreport_impl.compare_dumpsys_density_with_real_density()
        print("3.[Debug] judge if dumpsys density is in [120,160,213,240,280,320,360,400,480,560,640]")
        d_metricsreport_impl.judge_density_in_range()
