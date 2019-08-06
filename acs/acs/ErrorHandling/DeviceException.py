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


class DeviceException(AcsBaseException):

    """
    Exception class for I{Device} exceptions.
    """

    ADB_ERROR = "ADB command failed"
    """
    The value corresponding to adb command error.
    """

    CONNECTION_LOST = "Lost connection error"
    """
    The value corresponding to a loss connection.
    """

    DUT_SHUTDOWN_ERROR = "DUT shutdown error"
    """
    Define problems encountered during shutdown sequence.
    """

    DUT_BOOT_ERROR = "DUT boot error"
    """
    Define problems encountered during boot sequence.
    """

    FILE_SYSTEM_ERROR = "File system error"
    """
    The value corresponding to a file system error.
    """

    INTERNAL_EXEC_ERROR = "Internal command execution error"
    """
    The value corresponding to an error raised by internal exec command.
    """

    INVALID_DEVICE_STATE = "Invalid device state"
    """
    The value corresponding to an invalid device state.
    """

    OPERATION_SET_ERROR = "Empty operation set is defined !"
    """
    The value corresponding to an operation set error.
    """

    PHONE_OUTPUT_ERROR = "Phone output error"
    """
    The value corresponding to an output phone error.
    """

    PROHIBITIVE_MEASURE = "Prohibitive measure"
    """
    The value corresponding to bad measure that will be
    detected has an error in the usecase.
    """

    SCRIPT_ERROR = "Script error"
    """
    The value corresponding to an external script error.
    """

    SMS_EXCEPTION = "SMS exception"
    """
    The value corresponding to a sms exception.
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
        self._error_code = self._FAILURE
