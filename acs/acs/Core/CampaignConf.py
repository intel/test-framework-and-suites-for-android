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
:summary: Implements campaign configuration associated with a subcampaign called in a campaign
:since: 15/03/2013
:author: lbavois
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
            error_msg = "Campaign config file issue: Wrong format or value for runNumber attribute (value used: '" + str(value) + \
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
