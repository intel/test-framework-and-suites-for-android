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
:summary: This file implements a Factory class to instantiate objects for test steps
:since 20/12/2013
:author: fbongiax
"""

import logging
from acs.Device.DeviceManager import DeviceManager
from acs.Core.Equipment.EquipmentManager import EquipmentManager
from acs.Core.Report.ACSLogging import LOGGER_TEST_STEP


class Factory(object):

    """
    Factory class that creates / returns objects for test steps.
    It abstracts from the direct call to other framework objects so to make easier stub them out
    """

    def create_device(self, device_id):
        """
        Returns a device
        """
        return DeviceManager().get_device(device_id)

    def create_device_config(self, device_id):
        """
        Returns a device config object
        """
        return DeviceManager().get_device_config(device_id)

    def create_bench_config(self, name):
        """
        Returns a bench config object
        """
        return self.create_equipment_manager().get_global_config().benchConfig.get_parameters(name)

    def create_logger(self, name):
        """
        Returns a logger object
        """
        return logging.getLogger(name)

    def create_test_step_logger(self):
        """
        Returns a logger object
        """
        return LOGGER_TEST_STEP

    def get_test_step_catalog(self, global_conf):
        """
        Returns the test step catalog
        """
        return global_conf.teststepCatalog

    def create_equipment_manager(self):
        """
        Returns an equipment manager
        """
        return EquipmentManager()
