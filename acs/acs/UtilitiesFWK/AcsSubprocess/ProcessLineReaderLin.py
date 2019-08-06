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

import os


class ProcessLineReaderLin(object):

    """
    LineReader object to be use as select readable input
    """

    # Size of the buffer (in bytes) to be read
    READ_BUFFER_SIZE = 8192

    def __init__(self, fd):
        """
        :type fd: int
        :param fd: stream file descriptor
        """
        # File descriptor where read operation will be done
        self._fd = fd
        # Internal buffer used to store incomplete line
        self._buf = ""

    def fileno(self):
        """
        Method for select operator.
        DO NOT CHANGE method name / type

        :return: File descriptor
        """
        return self._fd

    def read_lines(self):
        """
        Method to return lines from data read from file descriptor.
        Complete line are returned, incomplete one are buffered

        :return: Array of complete line
        """
        lines = []

        # Read data from file descriptor
        data = os.read(self._fd, self.READ_BUFFER_SIZE)

        if data:
            # Append and store read data with previous incomplete line
            self._buf += data

            if "\n" in data:
                # Line(s) is/are ready to be splitted
                # Split all data
                tmp = self._buf.split('\n')

                # Extract complete lines and incomplete one
                lines, self._buf = tmp[:-1], tmp[-1]
        elif self._buf:
            # No more data, return latest data we put in our internal buffer
            lines = [self._buf]
            self._buf = ""
        else:
            # No more data at all, return None
            lines = None

        return lines
