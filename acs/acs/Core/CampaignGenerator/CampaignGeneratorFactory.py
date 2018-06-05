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

:organization: INTEL SSG/OTC/QSI
:summary: Implement campaign generator factory
:since: 07/07/2015
:author: sfusilie
"""

from acs.Core.CampaignGenerator.CampaignGeneratorLoader import CampaignGeneratorLoader
from acs.Core.CampaignGenerator.DefaultCampaignGenerator import DefaultCampaignGenerator


class CampaignGeneratorFactory(object):

    @staticmethod
    def get_campaign_generator(global_config, generator_plugin=None):
        """
        Instantiante
        :param global_config: acs global config
        :type global_config: dict

        :param generator_plugin: name of the plugin to be used if not None. Must be "[module_name].[class_name]".
        :type generator_plugin: str

        :return: campaign generator instance
        """
        if not generator_plugin:
            generator = DefaultCampaignGenerator(global_config)
        else:
            generator = CampaignGeneratorLoader.load(generator_plugin, global_config)

        return generator
