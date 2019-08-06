#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
