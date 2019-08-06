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


class BaseConf():

    """ BaseConf
        This class holds data retrieved from parsing xml data
    """

    def __init__(self):
        self._attrs = None
        self._raw_name = ""
        self._name = ""
        self._messages = []

    def get_attrs(self):
        """
        This function gets the attributes from xml files
        """
        return self._attrs

    def get_raw_name(self):
        """
        This function gets the raw name of an xml file
        """
        return self._raw_name

    def get_name(self):
        """
        This function gets the name of an xml file
        """
        return self._name

    def set_name(self, name):
        """
        This function sets the name of a TC
        :type: str
        :param name: name to be given
        """
        self._name = str(name)

    def get_messages(self):
        """
        Returns a list of messages from for test cases

        :return message list
        """
        return self._messages

    def add_message(self, message):
        """
        Adds a message or list of messages to a test case

        :type message: list, string
        :param message: message to be added to TestCaseConf
        """
        if message:
            if isinstance(message, list):
                self._messages.extend(message)
            else:
                self._messages.append(message)

    def clear_messages(self):
        """
        Clears the messages from a test case
        :return:
        """
        self._messages = []
