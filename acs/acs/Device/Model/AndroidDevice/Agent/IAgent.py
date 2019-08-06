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
