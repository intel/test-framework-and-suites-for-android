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


class AcsToolException(AcsBaseException):

    """
    Exception class for I{Acs} exceptions.
    """

    SEQUENCER_ERROR = "Unexpected exception occurred in sequencer"
    """
    Define problems encountered during sequencer execution.
    """

    XML_PARSING_ERROR = "Xml parsing error"
    """
    Define problems encountered during xml file parsing.
    """

    PHONE_OUTPUT_ERROR = "Phone output error"
    """
    The value corresponding to an output phone error.
    """

    HOST_OPERATION_TIMEOUT = "A timeout has occurred"
    """
    A host operation has timeout.
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
        self._error_code = self._BLOCKED
