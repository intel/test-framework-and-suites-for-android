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
