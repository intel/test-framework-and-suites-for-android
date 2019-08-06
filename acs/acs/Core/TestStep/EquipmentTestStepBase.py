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


class EquipmentTestStepBase(TestStepBase):

    """
    Implements a base test step which involves an equipment

    .. uml::

        class TestStepBase

        class EquipmentTestStepBase {
            run(context)
        }

        TestStepBase <|- EquipmentTestStepBase
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """
        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)
        self._equipment_manager = None
        self._equipment_parameters = None

    def run(self, context):
        """
        Runs the test step

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: test case context

        :raise: AcsConfigException, TestEquipmentException
        """
        TestStepBase.run(self, context)

        # Get access to the EquipmentManager instance
        self._equipment_manager = self._factory.create_equipment_manager()

        # Get all parameters of the equipment given in EQT parameter
        # Parameters will be accessible by using following method:
        # self._equipment_parameters.get_param_value(equipment_parameter_name)
        # i.e.: eqp_model = self._equipment_parameters.get_param_value("Model")
        self._equipment_parameters = self._global_conf.benchConfig.get_parameters(self._pars.eqt)
