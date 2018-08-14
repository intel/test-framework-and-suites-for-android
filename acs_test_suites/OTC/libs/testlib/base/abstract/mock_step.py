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
# @description: Defines the mock class to test the astract step
# @author:      aurel.constantin@intel.com
#
##############################################################################

from testlib.base.base_step import step as base_step


class mock_step(base_step):
    """ Mock step used for mock testing. It prints out the step name and the parameters given to it.
        This step always passes.
    """
    def __init__(self, **kwargs):
        base_step.__init__(self, **kwargs)
        print "Calling mock step {0} with the following parameters: ".format(self.__class__.__name__)
        for key in kwargs:
            print "{0} = {1}".format(key, kwargs[key])
        if not kwargs:
            print "No parameters ware given"

    def do(self):
        pass

    def check_condition(self):
        return True
