#!/usr/bin/env python
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

from testlib.base.base_step import step as base_step
from testlib.utils.connections.local import Local as connection_local


class step(base_step):
    '''helper class for all local (host machine) test steps'''
    local_connection = None

    def __init__(self, **kwargs):
        self.local_connection = connection_local(**kwargs)
        base_step.__init__(self, **kwargs)
