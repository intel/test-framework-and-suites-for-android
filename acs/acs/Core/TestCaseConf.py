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
:summary: Implements test case config
:since: 05/03/2013
:author: vdechefd
"""

from TCParameters import TCParameters
from BaseConf import BaseConf


class TestCaseConf(BaseConf):

    """ TestCaseConf
        This class holds data relative to a campaign test case
    """

    def __init__(self, tc_node, random, group_id):
        BaseConf.__init__(self)
        self._random = random
        self._group_id = group_id
        self._attrs = tc_node.attrib
        self._raw_name = self._attrs.get('Id', '')
        self._name = None
        self._params = None
        self._ucase_name = None
        self._ucase_class = None
        self._valid = True
        # Store the test case order in the execution flow
        self._tc_order = 0

        self._phase = None
        self._type = None
        self._domain = None

    @property
    def tc_order(self):
        """
        Public property
        """
        return self._tc_order

    @tc_order.setter
    def tc_order(self, tc_order):
        self._tc_order = tc_order

    @property
    def params(self):
        """
        Public property
        """
        return self._params

    @property
    def usecase_name(self):
        """
        Aliasing java-style property
        """
        return self.get_ucase_name()

    @property
    def is_provisioning(self):
        """
        This property tells whether a TC is of `provisioning` kind or not

        :return: Whether True or False
        """
        return self._params.is_provisioning

    @property
    def do_device_connection(self):
        """
        This property tells whether a TC want or not device connection

        :return: Whether True or False
        """
        return self._params.do_device_connection

    def is_random(self):
        """
        Public property
        """
        return self._random

    def get_ucase_name(self):
        if self._ucase_name is None:
            self._ucase_name = self._params.get_ucase_name()
        return self._ucase_name

    def get_ucase_class(self):
        if self._ucase_class is None:
            self._ucase_class = self._params.get_ucase_class()
        return self._ucase_class

    def set_ucase_class(self, uc_class):
        self._ucase_class = uc_class

    def get_group_id(self):
        return self._group_id

    def set_name(self, name):
        self._name = name
        self._params = TCParameters(name, self._attrs)

    def get_params(self):
        return self._params

    def set_valid(self, status=True):
        """
        Sets the execution status of the test, if false the test
        is not executed

        :type status: bool
        :param status: execution status of the test
        """
        self._valid = status

    def get_valid(self):
        """
        Returns the execution status of the test

        :type: bool
        :return: execution status
        """
        return self._valid

    def get_is_warning(self):
        """
        This function returns if the TC was tagged as warning
        :rtype:     bool
        :return:    Return True on warning test
        """
        return self._params.get_is_warning()

    def get_phase(self):
        if self._phase is None:
            self._phase = self._params.get_phase_node()
        return self._phase

    def get_type(self):
        if self._type is None:
            self._type = self._params.get_type_node()
        return self._type

    def get_domain(self):
        if self._domain is None:
            self._domain = self._params.get_domain_node()
        return self._domain
