"""
Copyright (C) 2018 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

from acs.Device.DeviceManager import DeviceManager
from acs.Core.Equipment.EquipmentManager import EquipmentManager
from acs.UseCase.Misc.TEST_STEP_ENGINE import TestStepEngine


class UseCaseBase(TestStepEngine):
    """
    Base class for all use case implementation
    """

    def __init__(self, tc_conf, global_config):
        """
        Constructor
        """
        TestStepEngine.__init__(self, tc_conf, global_config)

        # Get Device Instance
        self._device = DeviceManager().get_device("PHONE1")
        self._dut_config = DeviceManager().get_device_config("PHONE1")

        self._device.inject_device_log("i", "ACS_TESTCASE", "INIT: %s" % self._name)
        # Get a reference of equipment manager
        self._em = EquipmentManager()

        # Get IO card instance. Default value is 'IO_CARD'
        io_card_name = self._dut_config.get("IoCard", "IO_CARD")
        self._io_card = self._em.get_io_card(io_card_name)

        # Get Global TC Parameters
        self._wait_btwn_cmd = float(self._dut_config.get("waitBetweenCmd"))

    def _run_test_steps(self, path, optional_step=True):
        return TestStepEngine._run_test_steps(self, path, optional_step=True)

    def initialize(self):
        verdict, msg = TestStepEngine.initialize(self)
        self._device.inject_device_log("i", "ACS_TESTCASE", "INITIALIZE: %s" % self._name)
        return verdict, msg

    def set_up(self):
        """
        Initialize the test
        """
        verdict, msg = TestStepEngine.set_up(self)
        self._device.inject_device_log("i", "ACS_TESTCASE", "SETUP: %s" % self._name)
        return verdict, msg

    def run_test(self):
        """
        Execute the test
        """
        verdict, msg = TestStepEngine.run_test(self)
        self._device.inject_device_log("i", "ACS_TESTCASE", "RUNTEST: %s" % self._name)
        return verdict, msg

    def tear_down(self):
        """
        End and dispose the test
        """
        verdict, msg = TestStepEngine.tear_down(self)
        self._device.inject_device_log("i", "ACS_TESTCASE", "TEARDOWN: %s" % self._name)
        return verdict, msg

    def finalize(self):
        verdict, msg = TestStepEngine.finalize(self)
        self._device.inject_device_log("i", "ACS_TESTCASE", "FINALIZE: %s" % self._name)
        return verdict, msg
