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

from Queue import Queue, Empty
import re
import threading
import time


class LogCatAnalyzerThread():

    """ Logger analyzer that will check input messages to check if
        they validate some criteria
    """

    def __init__(self, logger):
        # Analyzer thread stop condition
        self._stop_event = threading.Event()

        # Messages to trigger
        self.__messages_to_trigger = {}

        # Lock object
        self.__lock_message_triggered = threading.RLock()

        # Internal buffer
        self.__queue = Queue()

        # Working thread
        self.__analyzer_thread = None

        # Logger to be used to output messages
        self._logger = logger

        # Delay to wait before processing new item in the queue
        self.analyzer_loop_delay = 0.1

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

    def start(self):
        self._stop_event.clear()
        self.__analyzer_thread = threading.Thread(target=self.__run)
        self.__analyzer_thread.name = "LogCatAnalyzerThread"
        self.__analyzer_thread.daemon = True
        self.__analyzer_thread.start()

    def push(self, line):
        self.__queue.put_nowait(line)

    def __run(self):
        while not self._stop_event.is_set():
            while not self.__queue.empty():
                try:
                    line = self.__queue.get_nowait()
                    self.__analyze_line(line)
                except Empty:
                    pass
            self._stop_event.wait(self.analyzer_loop_delay)

    def __analyze_line(self, line):
        if line:
            line = line.rstrip('\r\n')
            # Check all messages to be triggered
            self.__lock_message_triggered.acquire()
            for trig_message in self.__messages_to_trigger:
                if trig_message.startswith("regex:"):
                    reg_ex = trig_message.split("regex:")[1]
                    try:
                        if re.search(reg_ex, line) is not None:
                            # Message received, store log line
                            self.__messages_to_trigger[trig_message].append(line)
                    except re.error as ex:
                        if self._logger is not None:
                            self._logger.error("Cannot compute regular expression \"%s\": %s" % (reg_ex, ex))
                elif line.find(trig_message) != -1:
                    # Message received, store log line
                    self.__messages_to_trigger[trig_message].append(line)

            self.__lock_message_triggered.release()

    def add_trigger_messages(self, messages):
        for message in messages:
            self.add_trigger_message(message)

    def add_trigger_message(self, message):
        """ Trigger a message

        :type  message: string
        :param message: message to be triggered
        """
        self.__lock_message_triggered.acquire()
        self.__messages_to_trigger[message] = list()
        self.__lock_message_triggered.release()

    def remove_trigger_message(self, message):
        """ Remove a triggered message

        :type  message: string
        :param message: message to be removed
        """
        if message in self.__messages_to_trigger:
            self.__lock_message_triggered.acquire()
            del self.__messages_to_trigger[message]
            self.__lock_message_triggered.release()

    def is_message_received(self, message, timeout):
        """ Check if a message is received

        :type  message: string
        :param message: message that we look for
        :type  timeout: int
        :param timeout: time limit where we expect to receive the message

        :return: Array of message received, empty array if nothing
        :rtype: list
        """
        remove_trigger_message = False
        if message not in self.__messages_to_trigger:
            self.add_trigger_message(message)
            remove_trigger_message = True

        messages_received = None
        begin_time = time.time()
        end_time = begin_time + float(timeout)

        while (not messages_received) and (time.time() < end_time):
            messages_received = self.get_message_triggered_status(message)
            time.sleep(0.2)

        if messages_received:
            # Clone the list to return as remove trigger message
            # is going to delete it
            messages_received = list(messages_received)

        if remove_trigger_message:
            self.remove_trigger_message(message)

        return messages_received

    def get_message_triggered_status(self, message):
        """ Get the status of a message triggered

        :type  message: string
        :param message: message triggered
        :return: Array of message received, empty array if nothing
        :rtype: list
        """
        if message in self.__messages_to_trigger:
            return self.__messages_to_trigger[message]
        else:
            return None

    def reset_trigger_message(self, message):
        """ Reset triggered message

        :type  message: string
        :param message: message to be reseted
        """
        if message in self.__messages_to_trigger:
            self.__lock_message_triggered.acquire()
            self.__lock_message_triggered.release()
