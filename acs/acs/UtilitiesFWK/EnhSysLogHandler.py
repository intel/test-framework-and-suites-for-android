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
