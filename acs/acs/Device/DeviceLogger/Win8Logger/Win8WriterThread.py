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
:summary: this file implements the win8 logger writer thread
:since: 22/02/2012
:author: rbertolini
"""

from Queue import Queue, Empty
import threading
import time


class Win8WriterThread():

    """
    Class describing the thread used to write logs read by the
    Win8ReaderThread.
    """

    def __init__(self):
        """
        Constructor of Win8WriterThread
        """
        self.__output_file_path = None
        self.__output_stream = None

        self.__start_writing = False

        # creating the internal queue.
        self.__queue = Queue()

        self.__writer_thread = None

    def start(self):
        """
        Start the writer thread
        """
        self.__writer_thread = threading.Thread(target=self.__run)
        self.__writer_thread.name = "Win8WriterThread"
        self.__writer_thread.start()

    def stop(self):
        """
        Stop gently the writer thread
        """
        self.__start_writing = False
        self.__writer_thread.join(5)

    def set_output_path(self, output_path):
        """Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self.__output_file_path = output_path
        return

    def push(self, line):
        """
        Push data in the internal queue of the writer

        :type line: string
        :param line: data to be pushed in the internal queue
        """
        self.__queue.put_nowait(line)

    def __run(self):
        first_write = False
        # Create the output file if output file was specified
        if self.__output_file_path is not None:
            # Close it if needed
            if self.__output_stream is not None and not self.__output_stream.closed:
                self.__output_stream.close()
            first_write = True

        self.__start_writing = True
        while self.__start_writing:
            while not self.__queue.empty():
                try:
                    line = self.__queue.get_nowait()
                    if len(line) > 0:
                        if first_write:
                            # create the file if it is the first time that there are logs
                            self.__output_stream = open(self.__output_file_path, "wb")
                            first_write = False
                        if self.__output_stream is not None:
                            self.__output_stream.write(line)
                            self.__output_stream.flush()
                except Empty:
                    pass
            time.sleep(1)

        # Close the output file
        if self.__output_stream is not None and not self.__output_stream.closed:
            self.__output_stream.flush()
            self.__output_stream.close()

        return
