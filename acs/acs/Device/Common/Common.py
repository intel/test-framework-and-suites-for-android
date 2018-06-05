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
:summary: Common utilities used inside Device module and sub-module.
:since: 03/08/2011
:author: sfusilie
"""


class Global(object):

    """Global return value"""
    SUCCESS = 0
    FAILURE = -1


def get_class(kls):
    """
    Load class from module path

    :type   kls: string
    :param  kls: module + class path

    :rtype:     class instance
    :return:    Instance of the class
    """

    parts = kls.split('.')
    module_path = ".".join(parts[:-1])
    module = __import__(module_path, fromlist=[])
    for comp in parts[1:]:
        module = getattr(module, comp)
    return module
