"""
@copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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

@organization: INTEL SSG/OTC/QSI/SIS/CTA
@summary: The module will play provide all information of the bench used to execute the campaign
@since: 28/09/15
@author: ssavrimoutou
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
    user_email = "no.name@intel.com"
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
