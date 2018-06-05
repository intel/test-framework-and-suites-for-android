"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

:organization: INTEL MCG PSI
:summary: This file implements the UC base class
:since: 22/04/2010
:author: sfusilie
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
