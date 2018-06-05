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
@summary: This module implements a windows linereader object
@since: 31/07/14
@author: sfusilie
"""

from threading import Thread
from Queue import Queue, Empty


class ProcessLineReaderWin(object):

    """
    LineReader object to be use as select readable input
    """
    MAX_LINES_TO_READ = 500

    def __init__(self, name, process, stream):
        """
        :type   name: str
        :param  name: name of the process line reader object

        :type   process: process
        :param  process: process to read from

        :type   stream: int
        :param  stream: stream file descriptor
        """

        # Nice name to ease debugging between different ProcessLineReaderWin
        # We usually have 2: one for stdout, one for stderr
        self.name = name

        # Process to work on
        self._process = process

        # Stream to read data from
        self._stream = stream

        # Reader thread
        self._reader_thread = None

        # Internal buffer
        self._lines_queue = Queue()

        # Start reading
        self.start_read()

    def _read_worker(self):
        """
        Reader thread that will retrieve data from the stream
        """
        for line in iter(self._stream.readline, ''):
            line = line.rstrip("\n")
            if line:
                self._lines_queue.put(line)

        self._stream.close()

    def stop_read(self):
        """
        Notify the line reader that we want to stop reading
        """
        pass

    def start_read(self):
        """
        Notify the line reader that we want to start reading
        A new reader thread will be started to retrieve data from the stream
        """
        self._reader_thread = Thread(target=self._read_worker)
        self._reader_thread.name = "{0} process reader line thread".format(self.name)
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def read_lines(self):
        """
        Method to return lines from data read from file descriptor.
        Complete line are returned

        :return: Array of complete line
        """
        lines = []
        process_terminated = self._process.poll() is not None
        try:
            data = self._lines_queue.get_nowait()
            for line in data.splitlines():
                lines.append(line)
        except Empty:
            pass

        if not lines and process_terminated:
            # Nothing more to read
            lines = None

        return lines
