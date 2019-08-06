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

import os
import platform
import socket
from acs.UtilitiesFWK.Patterns import Singleton
from acs.UtilitiesFWK.Utilities import get_acs_release_version


@Singleton
class BenchConf(object):

    """
    Configuration of the bench
    """
    hostname = socket.getfqdn()
    user = os.path.split(os.path.expanduser('~'))[-1]
    user_email = "no.name@example.com"
    fwk_version = get_acs_release_version()

    @property
    def os_version(self):
        release = None
        if platform.system() == "Windows":
            release = platform.release()
        elif platform.dist():
            release = "{0}_{1}".format(platform.dist()[0], platform.dist()[1])

        return "{0}_{1}".format(platform.system(), release) if release else platform.system()

    @property
    def python_version(self):
        return "{0}_{1}".format(platform.python_version(), platform.architecture()[0])

    def get_properties(self):
        return {
            "hostname": self.hostname,
            "user": self.user,
            "user_email": self.user_email,
            "os": self.os_version,
            "version": self.fwk_version,
            "python_version": self.python_version,
        }
