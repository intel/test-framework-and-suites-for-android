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
:summary: This file implements a Test Step base class which involves a device
:since: 15/03/2013
:author: fbongiax
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
