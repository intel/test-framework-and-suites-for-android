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
import time

from acs.Device.Common.Common import Global
from acs.UtilitiesFWK.Utilities import AcsConstants
from acs.ErrorHandling.DeviceException import DeviceException
from acs.Device.Model.AndroidDevice.Agent.IAgent import IAgent


class AcsAgentLegacy(IAgent):

    """
    Class that will handle Acs embedded agent status for android implementation
    """

    def __init__(self, device):
        """
        Constructor
        :type logger: logging
        :param logger: the logger to use in this module
        """
        self._logger = device._logger
        self._device = device
        self._agentv2_pkg = "com.intel.acs.agentv2"
        self._agentv2_service = "{0}.service".format(self._agentv2_pkg)
        self._agentv2_version = None
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
        # Get agent version
        agentv2_version = self._device.get_apk_version(self._agentv2_pkg)
        self._agentv2_version = agentv2_version if agentv2_version is not None else AcsConstants.NOT_INSTALLED

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

    def start(self):
        """
        Try to start the Android embedded agent.
        :rtype: boolean
        :return: True if agent is started, False otherwise
        """
        self._logger.debug("Trying to start ACS agent V2 ...")
        cmd = "adb shell am start -n com.intel.acs.agentv2/.common.framework.ServiceStarterActivity"
        output = self._device.run_cmd(cmd, self._device.get_uecmd_timeout(), force_execution=True)
        return output[0] is Global.SUCCESS

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
        # kill agent process
        cmd = "adb shell am force-stop com.intel.acs.agentv2"
        output = self._device.run_cmd(cmd, 2, force_execution=True)
        return output[0] is Global.SUCCESS

    def is_running(self):
        """
        Check if agent is running
        :return: boolean
        :return: True if Acs agent is running, False otherwise
        """
        cmd = "adb shell ps | grep {0}".format(self._agentv2_pkg)
        result, output_msg = self._device.run_cmd(cmd,
                                                  self._device.get_uecmd_timeout(),
                                                  force_execution=True,
                                                  wait_for_response=True)
        return result == 0 and self._agentv2_service in str(output_msg)

    def get_intent_action_cmd(self, is_system=False):
        """
        Get intent action command line
        :param is_system: boolean to notify that the command is system or user.
                            By default we consider that the command is user
        :return: string containing the intent action command line
        """
        return "intel.intent.action.acs.cmd"
