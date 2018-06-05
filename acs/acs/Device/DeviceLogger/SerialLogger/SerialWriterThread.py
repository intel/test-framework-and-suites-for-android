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
:summary: This file is writing data from serial connection
:since: 30/11/2011
:author: vgombert
"""
from Queue import Queue
from time import strftime
import threading


class SerialWriterThread():

    """
    Logger based on serial utility
    """

    def __init__(self, logger):
        # Output file
        self._output_file_path = None

        # Reader thread stop condition
        self._stop_event = threading.Event()

        # Internal buffer
        self._queue = Queue()

        self.__writer_thread = None

        # Logger
        self._logger = logger

    def stop(self):
        """
        Stop the writer thread
        """
        self._stop_event.set()

        if self.__writer_thread is not None:
            try:
                self.__writer_thread.join(5)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass
            finally:
                del self.__writer_thread
                self.__writer_thread = None
        return

    def start(self):
        """
        Start the write thread
        """
        self._stop_event.clear()
        self.__writer_thread = threading.Thread(target=self._run)
        self.__writer_thread.name = "SerialWriterThread"
        self.__writer_thread.daemon = True
        self.__writer_thread.start()

    def push(self, line):
        """
        Push data in the internal queue

        :type  line: string
        :param line: data to be written
        """
        self._queue.put_nowait(line)

    def set_output_path(self, output_path):
        """
        Set stdout file path

        :type  output_path: string
        :param output_path: path of the log file to be created
        """
        self._output_file_path = output_path

    def _run(self):
        """
        Runner thread method
        """
        # Create the output file if output file was specified
        if self._output_file_path is None:
            self._logger.info("No file specified for serial logger output")
            self._output_file_path = strftime("_%Y-%m-%d_%Hh%M.%S") + "_serial.log"
            self._logger.info("%s will be used." % self._output_file_path)

        while not self._stop_event.is_set():
            try:
                with open(self._output_file_path, "ab") as output_stream:
                    while not self._queue.empty():
                        try:
                            line = self._queue.get_nowait()
                            if len(line) > 0:
                                output_stream.write(line)
                                output_stream.flush()
                        except Exception as e:  # pylint: disable=W0703
                            self._logger.error(str(e))
            except (IOError, OSError, TypeError) as e:
                self._logger.error(str(e))
                break
