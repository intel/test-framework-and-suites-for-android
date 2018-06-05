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
:summary: This file expose the device interface ILogger
:since: 11/03/2011
:author: sfusilie
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
