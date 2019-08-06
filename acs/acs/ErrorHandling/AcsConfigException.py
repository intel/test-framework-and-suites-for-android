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


class AcsConfigException(AcsBaseException):

    """
    Exception class for I{Acs Configuration} exceptions.
    """

    UNKNOWN_EQT = "Unknown equipment."
    """
    The value corresponding to an unknown equipment in the catalog.
    """

    FILE_NOT_FOUND = "File not found."
    """
    The value is corresponding to a file that hasn't been found.
    """

    ALGORITHM_FAILURE = "Algorithm failure."
    """
    Define an error detected during an algorithm execution, like for instance a
    conversion failure, a bad value that makes the algorithm non applicable,
    and so on.
    """

    XML_PARSING_ERROR = "Xml parsing error."
    """
    Define problems encountered during xml file parsing.
    """

    YAML_PARSING_ERROR = "Yaml parsing error."
    """
    Define problems encountered during yaml file parsing.
    """

    READ_PARAMETER_ERROR = "Read parameter error occurred."
    """
    The value corresponding to a read parameter error.
    """

    DATA_STORAGE_ERROR = "Data storage error."
    """
    The value is corresponding to errors encountered on internal storage
    objects.
    """

    INVALID_CAMPAIGN_CONFIG = "Invalid campaign configuration."
    """
    The value corresponding to an error in the campaign config.
    """

    INVALID_BENCH_CONFIG = "Invalid bench configuration."
    """
    The value corresponding to an error in the bench config.
    """

    INVALID_TEST_CASE_FILE = "Invalid test case file."
    """
    The value corresponding to an error in the test case file.
    """

    EXTERNAL_LIBRARY_ERROR = "External library error"
    """
    Define problems encountered with external library.
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
