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

:summary: Exception class that should be used when an issue occurs with the
user inputs (TC parameters, Campaign config, Bench config, targets...)

:since: 2013/09/05
:author: ssavrimoutou
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
