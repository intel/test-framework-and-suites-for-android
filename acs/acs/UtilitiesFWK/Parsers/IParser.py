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
@summary: This module implements the interface for a parser class
@since: 07/08/14
@author: kturban
"""

__organization__ = "INTEL MCG PSI"
__author__ = "sis-cta-team@intel.com"

import abc


class IParser(object):

    """
    Parser module interface
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def keys(self):
        """
        Get all keys of the parsed contents

        :return: list of keys
        :rtype: list.
        """

    @abc.abstractmethod
    def get(self, path, default_value=None):
        """
        Get the value on specified key from parsed content

        :param path: key value or xpath like path
        :type  key: str.

        :return: content found at the key specified
        :rtype: Depends on key content
        """

    @abc.abstractmethod
    def get_parsed_content(self):
        """
        Get all the parsed content

        :rtype: depends on file
        :return: parsed content
        """
