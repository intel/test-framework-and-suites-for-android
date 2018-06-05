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
:summary:
:since: 16/04/2013
:author: CBonnard
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
