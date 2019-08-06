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
# flake8: noqa: W503
import time

from acs.Device.Model.AndroidDevice.Agent.IAgent import IAgent
from acs.Device.Common.Common import Global
from acs.UtilitiesFWK.Utilities import AcsConstants
from acs.ErrorHandling.DeviceException import DeviceException


class AcsAgent(IAgent):

    """
    Class that will handle Acs embedded agent status for android implementation
    This class will be used by Android versions upper than KitKat
    """

    def __init__(self, device):
        """
        Constructor
        :type logger: logging
        :param logger: the logger to use in this module
        """
        self._logger = device._logger
        self._device = device
        self._agentv2_version = None
        self._user_package_name = "com.intel.acs.agentv2.user"
        self._system_package_name = "com.intel.acs.agentv2.system"
        self.is_started = False

    @property
    def version(self):
        """
        Get the ACS Agent Version that has been retrieve through retrieve_version()
        :rtype: str
        :return: ACS Agents version
        """
        if self._agentv2_version is None:
            self.update_version()
        # return V2, as agent V1 will soon be removed
        return self._agentv2_version

    def update_version(self):
        """
        Get the ACS Agent version deployed on device
        :return: None
        """
        # Get agent user version
        agentv2_user_version = str(self._device.get_apk_version(self._user_package_name)
                                   or AcsConstants.NOT_INSTALLED).replace(" (user)", "")

        # Check if version of agents user and system are the same (Intel device only)
        if self._device.has_intel_os():
            # Get agent user version
            agentv2_system_version = str(self._device.get_apk_version(self._system_package_name)
                                         or AcsConstants.NOT_INSTALLED).replace(" (system)", "")

            if agentv2_user_version != agentv2_system_version:
                self._logger.warning(
                    "ACS agent user ({0}) and system ({1}) versions are different! ".format(agentv2_user_version,
                                                                                            agentv2_system_version))
                self._logger.warning(
                    "Same version of agents shall be installed on the device else ue commands will not work properly !")

        # Store the user agent version
        self._agentv2_version = agentv2_user_version

    def start(self):
        """
        Try to start the Android embedded agent.
        :rtype: boolean
        :return: True if agent is started, False otherwise
        """

        self._logger.debug("Trying to start ACS agent V2 (user) ...")
        acs_agent_activity = "com.intel.acs.agentv2.common.framework.ServiceStarterActivity"
        cmd_user = "adb shell am start -n {0}/{1}".format(self._user_package_name, acs_agent_activity)
        output = self._device.run_cmd(cmd_user, self._device.get_uecmd_timeout(), force_execution=True)

        # In case of intel device start also system agent
        if output[0] == Global.SUCCESS and self._device.has_intel_os():
            self._logger.debug("Trying to start ACS agent V2 (system) ...")
            cmd_system = "adb shell am start -n {0}/{1}".format(self._system_package_name, acs_agent_activity)
            output = self._device.run_cmd(cmd_system, self._device.get_uecmd_timeout(), force_execution=True)

        return output[0] == Global.SUCCESS

    def stop(self):
        """
        Try to stop the Android embedded Service.
        :rtype: boolean
        :return: True if AcsAgentService is stopped, False otherwise
        """
        # stop service
        cmd = "adb shell am broadcast -a intel.intent.action.acs.stop_service"
        self._device.run_cmd(cmd, self._device.get_uecmd_timeout(), force_execution=True)
        time.sleep(0.5)

        # kill agent process (user)
        cmd = "adb shell am force-stop {0}".format(self._user_package_name)
        output = self._device.run_cmd(cmd, 2, force_execution=True)

        # kill agent process (system) (Intel device only)
        if output[0] == Global.SUCCESS and self._device.has_intel_os():
            cmd = "adb shell am force-stop {0}".format(self._system_package_name)
            output = self._device.run_cmd(cmd, 2, force_execution=True)
        return output[0] is Global.SUCCESS

    def wait_for_agent_started(self, timeout=None):
        """
        Wait for acs agent to start before timeout.
        If no timeout is set, it will get value of device parameter **acsAgentStartTimeout**.

        :type timeout: float
        :param timeout: Value before which agent shall be started before.

        :rtype: bool
        :return: True if agent is started, False otherwise
        """
        is_started = False
        if not timeout:
            timeout = self._device.get_config("acsAgentStartTimeout", 60.0, float)

        # check that service is ready
        uecmd_phonesystem = self._device.get_uecmd("PhoneSystem")

        end_time = time.time() + timeout
        while time.time() < end_time and not is_started:
            # wait before checking service start
            time.sleep(self._device.get_config("waitBetweenCmd", 5.0, float))
            # check that service is ready
            try:
                is_started = uecmd_phonesystem.is_acs_agent_ready()
            except DeviceException:
                # No answer from the device
                is_started = False

        # Update is_started attribute
        self.is_started = is_started
        return self.is_started

    def __is_service_running(self, package_name):
        """
        Check if the service of the given package is running
        :param package_name: Name of the package to check
        :return: boolean True if service is running else False
        """
        service_is_running = False

        cmd = "adb shell ps | grep {0}".format(package_name)
        result, output_msg = self._device.run_cmd(cmd,
                                                  self._device.get_uecmd_timeout(),
                                                  force_execution=True,
                                                  wait_for_response=True)

        if result == 0 and "{0}.service".format(package_name) in str(output_msg):
            service_is_running = True

        return service_is_running

    def is_running(self):
        """
        Check if agent is running
        :return: boolean
        :return: True if Acs agent is running, False otherwise
        """
        agent_is_running = self.__is_service_running(self._user_package_name)

        if agent_is_running and self._device.has_intel_os():
            # In case the device has an Intel os with root access, the system apk shall be installed
            # And ACS shall check if the system service is running
            agent_is_running = self.__is_service_running(self._user_package_name)

        return agent_is_running

    def get_intent_action_cmd(self, is_system=False):
        """
        Get intent action command line
        :param is_system: boolean to notify that the command is system or user.
                            By default we consider that the command is user
        :return: string containing the intent action command line
        """
        intent_action_cmd = "intel.intent.action.acs.cmd.user"
        if is_system:
            intent_action_cmd = "intel.intent.action.acs.cmd.system"
        return intent_action_cmd
