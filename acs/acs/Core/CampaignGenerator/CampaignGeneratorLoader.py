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

import importlib


class CampaignGeneratorLoader(object):

    """
    Campaign generator loader
    """

    @staticmethod
    def load(generator_module, global_config):
        """
        Load external ACS generator plugin. Must be available as python package.

        :param generator_module: name of the module.class to instantiate. Must be "[module_name].[class_name]".
        :type generator_module: str

        :param global_config: ACS global config
        :type global_config: dict

        :return: generator instance
        :raise NotImplementedError: if loader is not able to instantiate the "[module].[class]"
        """
        try:
            module_split = generator_module.split(".")
            lib = importlib.import_module(module_split[0])
            generator_class = getattr(lib, module_split[1])
            generator = generator_class(global_config)
        except (ImportError, AttributeError) as ex:
            raise NotImplementedError("Cannot load {0} plugin, implementation not found.".format(generator_module),
                                      ex)
        return generator
