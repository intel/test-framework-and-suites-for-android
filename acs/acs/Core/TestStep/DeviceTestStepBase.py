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

from acs.Core.TestStep.TestStepBase import TestStepBase
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.DeviceException import DeviceException


class DeviceTestStepBase(TestStepBase):

    """
    Implements a base test step which involves a device.

    .. uml::

        class TestStepBase

        class DeviceTestStepBase {
            run(context)
        }

        TestStepBase <|- DeviceTestStepBase
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """

        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)

        self._device = self._factory.create_device(self._pars.device)
        self._config = self._factory.create_device_config(self._pars.device)

    def run(self, context):
        """
        Runs the test step.

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: test case context

        :raise: AcsConfigException, DeviceException
        """
        TestStepBase.run(self, context)

        if self._device is None:
            self._raise_config_exception("%s is not specified in the bench configuration" % self._pars.device,
                                         AcsConfigException.INVALID_BENCH_CONFIG)

        # Insert log into device logs as info "i"
        self._device.inject_device_log("i", "ACS_TESTSTEP", "RUNTESTSTEP - %s" % self._pars.id)

    def _raise_device_exception(self, msg, category=DeviceException.OPERATION_FAILED):
        """
        Raises a device exception; it can be used in inheriting classes to raise device exceptions in
        a consistent manner.
        """
        self._logger.error(msg)
        raise DeviceException(category, msg)
