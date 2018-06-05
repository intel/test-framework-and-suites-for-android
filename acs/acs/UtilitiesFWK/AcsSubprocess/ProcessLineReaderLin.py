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
@summary: This module implements a linux linereader object used for select usage to have a non blocking readline
@since: 31/07/14
@author: sfusilie
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
