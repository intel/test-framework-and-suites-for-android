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
