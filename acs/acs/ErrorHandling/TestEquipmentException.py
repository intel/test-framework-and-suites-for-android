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

:summary: Exception class that should be used when an issue occurs due to test environment
(Wifi router, Cellular simulator, IO cards ...)

:since: 2013/09/05
:author: ssavrimoutou
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
