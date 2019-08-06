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

from exceptions import Exception


class AcsBaseException(Exception):

    """
    A base class for all I{ACS} exceptions.
    This class provides facility methods for error messages management.
    """

    # Exception Return Codes
    # Those codes shall be aligned with Global defined in Utility/utilities.py
    _SUCCESS = 0
    _FAILURE = -1
    _BLOCKED = -2

    DEFAULT_ERROR_CODE = "Unknown error type"
    """
    The default value for error code.
    """

    FEATURE_NOT_IMPLEMENTED = "Feature not implemented"
    """
    The error to raise when a method or feature is not implemented.
    """

    FEATURE_NOT_AVAILABLE = "Feature not available"
    """
    The error to raise when a method or feature is not available.
    """

    INSTANTIATION_ERROR = "Instantiation error: could not create requested object"
    """
    The value corresponding to an error occurring when creating an
    instance of a class.
    """

    INVALID_PARAMETER = "Invalid parameter"
    """
    The value indicating that a parameter does not have an appropriate
    value.
    """

    OPERATION_FAILED = "Operation failed"
    """
    The value corresponding to an operation failed.
    """

    PROHIBITIVE_BEHAVIOR = "Prohibitive behavior"
    """
    The value is corresponding to a behavior
    detected by the usecase as an error.
    """

    TIMEOUT_REACHED = "A timeout has been reached"
    """
    The value corresponding to a reached timeout.
    """

    USER_INTERRUPTION = "User interruption"
    """
    The value is corresponding to a KeyboardInterrupt
    """

    NO_TEST = "No test to run"
    """
    The value is corresponding to test lack
    """

    CRITICAL_FAILURE = "CRITICAL FAILURE"
    """
    The value is corresponding to a critical failure
    """

    __CRITICAL_EXCEPTION = ["com.android.internal.telephony.itelephony does not exist",
                            "com.android.smoke.sms.iMessaging does not exist"]

    def __init__(self, generic_error_msg, specific_msg=None):
        """
        Initializes this instance.

        :type generic_error_msg: str
        :param generic_error_msg: this object's generic error message.
        :type specific_msg: str
        :param specific_msg: specific additional error message.
            Optional parameter, defaults to C{None}.
        """
        Exception.__init__(self)
        self.__generic_error_msg = generic_error_msg
        self.__specific_msg = specific_msg

        self._error_code = None
        self._error_msg = self.get_error_message()

    def get_error_code(self):
        """
        Returns the specific error code of this exception.
        :rtype: int
        :return: the specific error code of this exception.
        """
        return self._error_code

    def get_generic_error_message(self):
        """
        Returns the error message of this exception.
        :rtype: str
        :return: the error message of this exception.
        """
        return self.__generic_error_msg

    def get_specific_message(self):
        """
        Returns the specific additional error message of this exception.
        :rtype: str
        :return: the specific additional error message of this exception.
        """
        return str(self.__specific_msg)

    def get_error_message(self):
        """
        Returns the final error message of the exception.
        This message is composed of the exception error message +
        the specific additional error message.
        :rtype: str
        :return: the final error message to display.
        """
        # Initialize local variables
        final_message = "Unknown ACS exception"
        error_msg = self.get_generic_error_message()
        specific_msg = self.get_specific_message()

        if error_msg is not None:
            final_message = "%s: " % (self.__class__.__name__,)
            # Remove any trailing "." from the
            # previously computed message
            if specific_msg not in [None, "None"]:
                specific_msg = specific_msg.replace("\r", "")
                specific_msg = specific_msg.replace("\n", "")
                final_message += error_msg.rstrip(".")
                final_message += " (%s)." % specific_msg
            else:
                final_message += error_msg

        # Return the value
        return final_message

    def is_critical_exception(self, msg_to_parse):
        """
        Checks if the message passed in parameter is a critical error message.
        Parsing this message and checking several keywords determine if this
        message must raise a critical exception.
        :type message_to_parse: str
        :param message_to_parse: the message to parse to determine if it is a
        critical error message or not.
        :rtype: bool
        :return: True if this is a critical exception, else returns False.
        """
        if msg_to_parse is not None:

            if not isinstance(msg_to_parse, list):
                msg_to_parse = [msg_to_parse]

            for msg in msg_to_parse:
                msg = msg.lower()

                for item in AcsBaseException.__CRITICAL_EXCEPTION:
                    if msg.find(item) != -1:
                        return True
            return False

        # In any other case, consider this as critical as all UECmd shall
        # return something !
        return True

    def __str__(self):
        """
        return error message if object is casted as string.

        :rtype: string
        :return: error message
        """
        return self.get_error_message()
