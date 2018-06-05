"""
:copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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
:summary: Implement campaign generator loader
:since: 07/20/2015
:author: sfusilie
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
