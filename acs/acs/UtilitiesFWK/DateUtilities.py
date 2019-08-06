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
