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
:summary: Implement live reporting plugin loader
:since: 07/20/2015
:author: sfusilie
"""
from acs.UtilitiesFWK.Utilities import get_class
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class LiveRerportingPluginLoader(object):

    """
    Live reporting plugin loader
    """

    @staticmethod
    def load(live_reporting_module):
        """
        Load external ACS live reporting plugin. Must be available as python package.

        :param live_reporting_module: name of the module.class to instantiate. Must be "[module_name].[class_name]".
        :type live_reporting_module: str

        :return: plugin instance
        :raise NotImplementedError: if loader is not able to instantiate the "[module].[class]"
        """
        try:
            generator = get_class(live_reporting_module)
        except AcsConfigException as ex:
            raise NotImplementedError("Cannot load {0} plugin, implementation not found.".format(live_reporting_module),
                                      ex)
        return generator
