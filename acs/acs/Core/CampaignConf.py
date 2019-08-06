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

from BaseConf import BaseConf
from acs.ErrorHandling.AcsConfigException import AcsConfigException
import os

RUN_NB_KEY = 'runNumber'


class CampaignConf(BaseConf):

    """
        This class holds parameters relative to the call of a sub campaign
    """
    DEFAULT_RUN_NUMBER_VALUE = "1"

    def __init__(self, sc_node, parent_campaign_list):
        BaseConf.__init__(self)
        self._attrs = sc_node.attrib
        self._raw_name = os.path.normpath(self._attrs.get('Id', ''))
        self._name = ""

        value = self._attrs.get(RUN_NB_KEY, self.DEFAULT_RUN_NUMBER_VALUE)
        self._run_number = self.__check_and_set_run_number(value)

        self._parent_campaign_list = parent_campaign_list

    def get_run_number(self):
        return self._run_number

    def __check_and_set_run_number(self, value):

        if (not value.isdigit()) or value == "0":
            # Inform user in ACS log that runNumber has a bad value
            error_msg = "Campaign config file issue: " + \
                "Wrong format or value for runNumber attribute (value used: '" + str(value) + \
                " for SubCampaign " + str(self._raw_name) + "), runNumber parameter should be a positive integer"
            # Raise an exception to stop the campaign as campaign config file
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, error_msg)

        return value

    def get_parent_campaign_list(self):
        return self._parent_campaign_list

    def check_campaign_sanity(self):
        if self._parent_campaign_list:
            # Check that we do not have the same campaign called before we create the campaign conf element
            if self._name in self._parent_campaign_list:
                # Inform user in ACS log that we have an infinite loop while calling sub campaigns
                error_msg = "Campaign config file issue: Infinite loop detected while calling SubCampaign '" + \
                    str(self._raw_name) + "'"
                # Raise an exception to stop the campaign as campaign config file
                raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR, error_msg)
        else:
            self._parent_campaign_list = []
