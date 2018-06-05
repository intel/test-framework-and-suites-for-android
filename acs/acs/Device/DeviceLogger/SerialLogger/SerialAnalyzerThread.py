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
:summary: This file expose the phone interface IPhone
:since: 06/05/2011
:author: sfusilie
"""
from Queue import Queue, Empty
import threading
import time


class SerialAnalyzerThread():

    """
    SerialAnalyzerThread: Thread to analyze every lines that are read from
    Serial port.
    The mechanism is similar to LogCatAnalyzerThread
    """

    def __init__(self, logger):
        # Analyzer thread stop condition
        self.__start_analyze = False

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
        self.__queue = Queue()

        self.__analyzer_thread = None

        # Logger
        self._logger = logger

    def stop(self):
        """
        Stop the Thread
        """
        self.__start_analyze = False

        if self.__analyzer_thread is not None:
            try:
                self.__analyzer_thread.join(5)
            except Exception:  # pylint: disable=W0703
                pass
            finally:
                del self.__analyzer_thread
                self.__analyzer_thread = None

        return

    def start(self):
        """
        Start the thread
        """
        self.__analyzer_thread = threading.Thread(target=self.__run)
        self.__analyzer_thread.name = "SerialAnalyzerThread"
        self.__analyzer_thread.daemon = True
        self.__analyzer_thread.start()

    def push(self, line):
        """
        Method to receive the line that are read from the serial port.
        This method is used by the SerialReaderThread

        :type  line: String
        :param line: Line read from the serial port
        """
        self.__queue.put_nowait(line)

    def __run(self):
        """
        Overloaded method that contains the instructions to run
        when the thread is started
        """
        self.__start_analyze = True
        while self.__start_analyze:
            while not self.__queue.empty():
                try:
                    line = self.__queue.get_nowait()
                    if len(line) > 0:
                        self.__analyse_line(line.rstrip('\r\n'))
                except Empty:
                    pass
            time.sleep(1)

    def __analyse_line(self, line):
        """
        Sub method to analyse every line read by the SerialReaderThread
        and store them if they match one of the trigger message

        :type  line: String
        :param line: Line read from the serial port
        """
        # For each line to analyze
        # for line in lines:

        # Check all messages to be triggered
        self.__lock_message_triggered.acquire()
        for trig_message in self.__messages_to_trigger:
            if line.find(trig_message) != -1:
                # Message received, store log line
                self.__messages_to_trigger[trig_message].append(line)

        self.__lock_message_triggered.release()

        # Check message to be received
        self.__lock_message_received.acquire()
        if self.__message_to_receive is not None:
            if line.find(self.__message_to_receive) != -1:
                self.__message_received.append(line)
                self.__is_message_received = True
        self.__lock_message_received.release()

    def add_trigger_messages(self, messages):
        """ Trigger a list of messages

        :type  messages: Array
        :param messages: messages to be triggered
        """
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
        """ Get the status of a message triggered

        :type  message: string
        :param message: message triggered

        :rtype: list of string
        :return: Array of message received, empty array if nothing
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
            self.__lock_message_received.acquire()
            self.__messages_to_trigger[message] = list()
            self.__lock_message_received.release()
