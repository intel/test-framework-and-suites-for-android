"""
:copyright: (c)Copyright 2014, Intel Corporation All Rights Reserved.
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
:summary: This file implements a Test Step base class which involves an equipment
:since: 14/01/2014
:author: ssavrim
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
