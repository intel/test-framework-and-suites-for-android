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
