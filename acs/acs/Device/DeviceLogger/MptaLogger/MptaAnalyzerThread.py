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
import datetime
import fnmatch
import threading
import time


class MptaAnalyzerThread(object):

    def __init__(self):
        # Analyzer thread stop condition
        self._stop_event = threading.Event()

        # Messages to trigger
        self.__messages_to_trigger = {}

        # Message to received
        self.__message_to_receive = None
        self.__message_received = None
        self.__is_message_received = False

        # Lock object
        self.__lock_message_triggered = threading.RLock()
        self.__lock_message_received = threading.RLock()

        # Internal buffer
        self.__queue = Queue.Queue()

        self.__analyzer_thread = None
        self.__start_analyze = False

    def stop(self):
        self._stop_event.set()

        if self.__analyzer_thread is not None:
            try:
                self.__analyzer_thread.join(5)
            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException:
                pass
            finally:
                del self.__analyzer_thread
                self.__analyzer_thread = None

        return

    def start(self):
        self._stop_event.clear()
        self.__analyzer_thread = threading.Thread(target=self.__run)
        self.__analyzer_thread.name = "MptaAnalyzerThread"
        self.__analyzer_thread.daemon = True
        self.__analyzer_thread.start()
        return

    def push(self, line):
        self.__queue.put_nowait(line)

    def __run(self):
        self.__start_analyze = True
        while not self._stop_event.is_set():
            while not self.__queue.empty():
                line = self.__queue.get_nowait()
                if len(line) > 0:
                    self.__analyse_line(line)
            self._stop_event.wait(1)
        return

    def __analyse_line(self, line):
        buf = line
        msg = ''
        for i in range(len(buf)):
            msg += chr(buf[i])

        self.__lock_message_triggered.acquire()
        for trig_message in self.__messages_to_trigger:

            if fnmatch.fnmatch(msg, trig_message):
                # Message received, store log line
                line_timestamp = datetime.datetime.now(). \
                    strftime("%Y-%m-%d_%Hh%M.%S_")
                self.__messages_to_trigger[trig_message].append(line_timestamp + msg)
        self.__lock_message_triggered.release()

        # Check message to be received
        self.__lock_message_received.acquire()
        if self.__message_to_receive is not None:
            if msg.find(self.__message_to_receive) != -1:
                self.__message_received.append(msg)
                self.__is_message_received = True
        self.__lock_message_received.release()
        return

    def add_trigger_messages(self, messages):
        for message in messages:
            self.add_trigger_message(message)

    def add_trigger_message(self, message):
        self.__lock_message_triggered.acquire()
        self.__messages_to_trigger[message] = list()
        self.__lock_message_triggered.release()
        return

    def remove_trigger_message(self, message):
        if message in self.__messages_to_trigger:
            self.__lock_message_triggered.acquire()
            del self.__messages_to_trigger[message]
            self.__lock_message_triggered.release()

    def is_message_received(self, message, timeout):
        self.__lock_message_received.acquire()
        self.__is_message_received = False
        self.__message_received = list()
        self.__message_to_receive = message
        self.__lock_message_received.release()

        time_count = 0
        while (not self.__is_message_received) and (time_count <= timeout):
            time.sleep(1)
            time_count += 1

        self.__is_message_received = False
        self.__message_to_receive = None
        return self.__message_received

    def get_message_triggered_status(self, message):
        if message in self.__messages_to_trigger:
            return self.__messages_to_trigger[message]
        else:
            return None
