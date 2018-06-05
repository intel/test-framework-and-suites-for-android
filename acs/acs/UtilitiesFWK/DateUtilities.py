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
:summary: Implements methods around date purpose
:since: 06/05/2014
:author: ssavrimoutou
"""
import arrow
from datetime import datetime
from acs.Core.Report.ACSLogging import LOGGER_FWK

DEFAULT_TIMEZONE = 'Europe/Paris'


def utctime_iso8601():
    """
     Provide UTC ISO8601 now time
    @return: arrow date object
    """
    return arrow.utcnow().to('local')


def utctime():
    """
    Return UTC time

    :rtype: datetime.datetime
    :return: UTC time based on datetime lib
    """
    return datetime.utcnow()


def localtime():
    """
    Return host local time

    :rtype: datetime.datetime
    :return: Local time based on datetime lib
    """
    return datetime.now()


def timezone():
    """
    Return host timezone

    :rtype: str
    :return: Timezone (i.e: 'Europe/Paris')
    """
    # Trying to get local timezone
    try:
        import tzlocal
        host_localtimezone = str(tzlocal.get_localzone())
    except Exception as tzlocal_exception:
        # Set default host time
        host_localtimezone = DEFAULT_TIMEZONE
        LOGGER_FWK.warning("Cannot get host timezone ! "
                           "Use default timezone ('{0}') => {1}".format(host_localtimezone, str(tzlocal_exception)))
    return host_localtimezone
