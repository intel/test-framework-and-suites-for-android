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

from acs.ErrorHandling.AcsConfigException import AcsConfigException

# pylint: disable=W0613
# pylint: disable=W0232


class ILogger():

    """
    Abstract class that defines the interface to be implemented
    by an external logger.
    """

    def set_output_file(self, path):
        """ Specify the path where log will be saved

        :type  path: string
        :param path: Path to the output log file
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def start(self):
        """
        Start the logging.
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def stop(self):
        """
        Stop the logging.
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def is_message_received(self, message, timeout):
        """
        Check if a message is received

        :type  message: string
        :param path: message that we look for
        :type  timeout: int
        :param timeout: time limit where we expect to receive the message

        :return: Array of message received, empty array if nothing
        :rtype: list
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def add_trigger_message(self, message):
        """
        Trigger a message

        :type  message: string
        :param path: message to be triggered
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def remove_trigger_message(self, message):
        """
        Remove a triggered message

        :type  message: string
        :param path: message to be removed
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def reset_trigger_message(self, message):
        """
        Reset triggered message

        :type  message: string
        :param path: message to be reseted
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def get_message_triggered_status(self, message):
        """
        Get the status of a message triggered

        :type  message: string
        :param path: message triggered
        :return: Array of message received, empty array if nothing
        :rtype: list
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)

    def reset(self):
        """
        Reset the logger, can be used on log issue
        """
        raise AcsConfigException(AcsConfigException.FEATURE_NOT_IMPLEMENTED)
