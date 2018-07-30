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
@summary: Implement sys log handler that check server availability before sending the log
@since: 10/09/14
@author: sfusilie
"""
from logging import handlers
import socket


class EnhSysLogHandler(handlers.SysLogHandler):
    CONNECTION_AVAILABLE = True

    def __init__(self, address=('localhost', handlers.SYSLOG_UDP_PORT),
                 facility=handlers.SysLogHandler.LOG_USER, socktype=None):
        handlers.SysLogHandler.__init__(self, address, facility)
        self._check_server_connection()

    def _check_server_connection(self):
        try:
            # Check server availability
            socket.getaddrinfo(self.address[0], self.address[1])

            # Server available
            EnhSysLogHandler.CONNECTION_AVAILABLE = True
        except socket.gaierror:
            # Server not available, do nothing
            EnhSysLogHandler.CONNECTION_AVAILABLE = False

    def emit(self, record):
        if EnhSysLogHandler.CONNECTION_AVAILABLE:
            # Server available, send it the log
            try:
                handlers.SysLogHandler.emit(self, record)
            except BaseException:
                EnhSysLogHandler.CONNECTION_AVAILABLE = False
