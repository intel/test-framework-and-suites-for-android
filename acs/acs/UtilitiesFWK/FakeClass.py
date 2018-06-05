#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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

@organization: INTEL MCG PSI
@summary: This module implements a fake class that expose any method
@since: 31/07/14
@author: sfusilie
"""

# pylint: disable=unused-argument


def nada(*args, **kwargs):
    """
    Function that is returning nothing
    """
    return


class FakeClass(object):

    """
    Class that will answer to any method call
    """

    def __init__(self, *args, **kwargs):
        """
        Permissive constructor
        """

        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, item):
        """
        Route all method call to nada function
        """
        return nada
