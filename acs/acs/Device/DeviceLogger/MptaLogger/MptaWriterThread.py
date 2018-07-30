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
:summary: This file expose the device interface IDevice
:since: 06/05/2011
:author: sfusilie

"""
import Queue
import threading

BIN_EXT = '.bin'


class MptaWriterThread(object):

    def __init__(self):
        # Internal buffer
        self.__queue = Queue.Queue()

        # Writer thread stop condition
        self._stop_event = threading.Event()

        self.__writer_thread = None
        self.__bin_filename = ''
        self.__file = None
        self.__filename = None
        self.__start_writting = False

    def set_output_file(self, filename):
        self.__filename = filename
        return

    def start(self):
        self._stop_event.clear()
        self.__writer_thread = threading.Thread(target=self.__run)
        self.__writer_thread.name = "MptaWriterThread"
        self.__writer_thread.daemon = True
        self.__writer_thread.start()

    def stop(self):
        self._stop_event.set()

        if self.__writer_thread is not None:
            try:
                self.__writer_thread.join(30)

            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException:  # pylint: disable=W0703
                pass
            finally:
                del self.__writer_thread
                self.__writer_thread = None

        return

    def push(self, line):
        self.__queue.put_nowait(line)

    def __run(self):
        # get output file name
        self.__bin_filename = self.__filename + BIN_EXT

        try:
            self.__file = open(self.__bin_filename, 'wb')
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            # raise MptaLoggerThreadError(-1, "MptaLoggerThread file creation failed")
            pass

        self.__start_writting = True
        while not self._stop_event.is_set():
            while not self.__queue.empty():
                line = self.__queue.get_nowait()
                if len(line) > 0 and self.__file is not None:
                    self.__file.write(line)
                    self.__file.flush()
            self._stop_event.wait(1)

        # close log file
        if self.__file is not None:
            self.__file.flush()
            self.__file.close()
            self.__file = None

        return
