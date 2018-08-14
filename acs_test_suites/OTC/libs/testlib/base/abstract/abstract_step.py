#!/usr/bin/env python
##
"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?
SPDX-License-Identifier: Apache-2.0
"""
##

##############################################################################
#
# @filename:    abstract_step.py
# @description: Defines the decorator class to implement the astract step
# @author:      aurel.constantin@intel.com
#
##############################################################################

from testlib.base.abstract import abstract_utils
from testlib.base import base_utils


class abstract_step(object):
    __metaclass__ = base_utils.SingletonType

    def __init__(self, use_module):
        self.target_module = abstract_utils.import_module(use_module)

    def __call__(self, original_class):
        return abstract_utils.get_obj(self.target_module, original_class.__name__)
