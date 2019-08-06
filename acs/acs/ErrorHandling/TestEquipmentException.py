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

from acs.ErrorHandling.AcsBaseException import AcsBaseException


class TestEquipmentException(AcsBaseException):

    """
    Exception class for I{Equipment} exceptions.
    """
    COMMAND_LINE_ERROR = "Command line error occurred"
    """
    The value corresponding to command line error.
    """

    BINARY_FOLDER_PATH_ERROR = "Binary path not found error occurred"
    """
    The value corresponding to binary path not found error.
    """

    CONNECTION_ERROR = "Connection error occurred"
    """
    The value corresponding to connection error.
    """

    CONNECTION_LOST = "Lost connection error"
    """
    The value corresponding to a loss connection.
    """

    CONNECTIVITY_ERROR = "Connectivity error occurred"
    """
    The value corresponding to connectivity error.
    """

    DAEMON_DRIVER_ERROR = "Daemon driver error occurred"
    """
    The value corresponding to a daemon driver error.
    """

    C_LIBRARY_ERROR = "C Library error occurred"
    """
    The value corresponding to a I{C} library error.
    """

    VISA_LIBRARY_ERROR = "Visa Library error occurred"
    """
    The value corresponding to a I{PyVisa} library error.
    """

    MEASUREMENT_ERROR = "Measurement error occurred"
    """
    The value corresponding to a measurement error.
    """

    PLATFORM_ERROR = "Platform error occurred"
    """
    The value corresponding to a platform error.
    """

    PROPERTY_ERROR = "Property error occurred"
    """
    The value corresponding to a property error
    (wrong name or value).
    """

    READ_PARAMETER_ERROR = "Read parameter error occurred"
    """
    The value corresponding to a read parameter error.
    """

    SMS_EXCEPTION = "The SMS operation failed"
    """
    The value corresponding to a sms error.
    """

    TELNET_ERROR = "Telnet error occurred"
    """
    The value corresponding to a telnet error.
    """

    TRANSPORT_ERROR = "Transport error occurred"
    """
    The value corresponding to a transport error.
    """

    CRC_ERROR = "CRC error occurred"
    """
    The value corresponding to a CRC error.
    """

    CONTROLLER_ERROR = "Controller error occurred"
    """
    The value corresponding to a controller error.
    """

    TUNER_ERROR = "Tuner error occurred"
    """
    The value corresponding to a tuner error.
    """

    VERDICT_ERROR = "Verdict error occurred"
    """
    The value corresponding to a verdict error.
    """

    SPECIFIC_EQT_ERROR = "Equipment error occurred"
    """
    The value corresponding to a specific equipment error.
    This is based on returned error code of the equipment.
    """

    UNKNOWN_EQT = "Unknown equipment"
    """
    The value corresponding to an unknown equipment in the catalog.
    """

    def __init__(self, generic_error_msg, specific_msg=None):
        """
        Initializes this instance.

        :type generic_error_msg: str
        :param generic_error_msg: this object's generic error message.
        :type specific_msg: str
        :param specific_msg: specific additional error message.
            Optional parameter, defaults to C{None}.
        """
        AcsBaseException.__init__(self, generic_error_msg, specific_msg)
        # This exception family is (in most cases) non DUT related so do not fail on it
        self._error_code = self._BLOCKED
