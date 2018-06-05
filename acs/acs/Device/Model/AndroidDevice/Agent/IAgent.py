"""
@copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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

@organization: INTEL MCG PSI
@summary: This module implements Sphinx Auto-generator of Documentation
@since: 27/01/2015
@author: ssavrim
"""

import abc


class IAgent(object):

    """
    Agent module interface
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def version(self):
        """
        Get the ACS Agent Version that has been retrieve through retrieve_version()
        :rtype: str
        :return: ACS Agents version
        """

    @abc.abstractmethod
    def update_version(self):
        """
        Get the ACS Agent version deployed on device
        :return: None
        """

    @abc.abstractmethod
    def start(self):
        """
        Try to start the Android embedded agent.
        :rtype: boolean
        :return: True if agent is started, False otherwise
        """

    @abc.abstractmethod
    def stop(self):
        """
        Try to stop the Android embedded Service.
        :rtype: boolean
        :return: True if AcsAgentService is stopped, False otherwise
        """

    @abc.abstractmethod
    def wait_for_agent_started(self, timeout=None):
        """
        Wait for acs agent to start before timeout.
        If no timeout is set, it will get value of device parameter **acsAgentStartTimeout**.

        :type timeout: float
        :param timeout: Value before which agent shall be started before.

        :rtype: bool
        :return: True if agent is started, False otherwise
        """

    @abc.abstractmethod
    def is_running(self):
        """
        Check if agent is running
        :return: boolean
        :return: True if Acs agent is running, False otherwise
        """

    @abc.abstractmethod
    def get_intent_action_cmd(self, is_system=False):
        """
        Get intent action command line
        :param is_system: boolean to notify that the command is system or user.
                            By default we consider that the command is user
        :return: string containing the intent action command line
        """
