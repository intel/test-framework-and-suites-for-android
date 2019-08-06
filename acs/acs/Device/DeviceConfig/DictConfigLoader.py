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

from acs.UtilitiesFWK.AttributeDict import AttributeDict


class DictConfigLoader(object):

    """
    Create one config loader that will take param from current
    global config dict. We'll have to create a new config loader
    based on xml files when ready
    """

    @staticmethod
    def load(config):
        """
        Load global device conf to the device conf objects

        :type config: dict
        :param config: device global conf dictionary
        """
        device_conf = AttributeDict()
        for key, value in config.items():
            device_conf[key] = value

        return device_conf
