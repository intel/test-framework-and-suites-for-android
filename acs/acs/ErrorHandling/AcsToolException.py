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

:summary: Exception class that should be used when an issue occurs with the ACS framework
(sequencer, parser ...)

:since: 2013/09/05
:author: ssavrimoutou
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
