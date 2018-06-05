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
:summary: This file implements the logging mechanism of ACS
:since: 12/05/2010
:author: sfusilie

The below Variable ``DEBUG_FORMATER_CONF`` should help you for debugging purpose.

**To enable it**: Set the campaign logging level to **DEBUG** (Commonly, in the Campaign_Config.xml file).

then the log's outputs give you extra information on each line as below:

    .. code-block::

        " [%(module)s.%(funcName)s():%(lineno)s] "

    Gives you:

        ... [<python module>.<called function name>():<python module's file line number>] ...

"""
import logging
import os
import sys
from logging import handlers
from acs.UtilitiesFWK.EnhSysLogHandler import EnhSysLogHandler

RAW_LEVEL = 60
MAX_LOGGER_NAME = 13

STATS_FORMATER_CONF = ("%(asctime)s.%(msecs)03d\tACS_STATS %(name){0}s\t  "
                       "%(levelname)s\t%(message)s").format(str(MAX_LOGGER_NAME + 2))
STATS_WID_FORMATTER_CONF = ("%(asctime)s.%(msecs)03d\tACS_STATS %(name){0}s\t  "
                            "%(levelname)s\ttestRequestId={session_id} %(message)s")

FORMATER_CONF = ("%(asctime)s.%(msecs)03d\tACS %(name){0}s\t  "
                 "%(levelname)s\t%(message)s").format(str(MAX_LOGGER_NAME + 2))

DEBUG_FORMATER_CONF = ("%(asctime)s.%(msecs)03d\tACS %(name){0}s"
                       "\t  %(levelname)s\t [%(module)s.%(funcName)s():%(lineno)s] "
                       "\t%(message)s").format(str(MAX_LOGGER_NAME + 2))


FORMATER_DATE_CONF = "%d/%m %H:%M:%S"
ACS_LOGGER_NAME = "ACS"
ACS_STATS_LOGGER_NAME = "ACS_STATS"
ACS_FWK_LOGGER_NAME = "FWK"
TEST_SCRIPT_LOGGER_NAME = "TEST_SCRIPT"
TEST_STEP_LOGGER_NAME = "TEST_STEP"
EQT_LOGGER_NAME = "EQT"
WD_LOGGER_NAME = "WATCHDOG"

LOGGER_FWK = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, ACS_FWK_LOGGER_NAME,))
LOGGER_TEST_SCRIPT = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, TEST_SCRIPT_LOGGER_NAME,))
LOGGER_EQT = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, EQT_LOGGER_NAME,))
LOGGER_TEST_STEP = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, TEST_STEP_LOGGER_NAME,))
LOGGER_WD = logging.getLogger("%s.%s" % (ACS_LOGGER_NAME, WD_LOGGER_NAME))
LOGGER_STATS = logging.getLogger(ACS_STATS_LOGGER_NAME)
LOGGER_FWK_STATS = logging.getLogger("%s.FWK" % ACS_STATS_LOGGER_NAME)
LOGGER_DEVICE_STATS = logging.getLogger("%s.DEVICE" % ACS_STATS_LOGGER_NAME)
LOGGER_EQT_STATS = logging.getLogger("%s.%s" % (ACS_STATS_LOGGER_NAME, EQT_LOGGER_NAME,))
LOGGER_TEST_SCRIPT_STATS = logging.getLogger("%s.%s" % (ACS_STATS_LOGGER_NAME, TEST_SCRIPT_LOGGER_NAME,))


class AltCustomFormatter(logging.Formatter):

    def format(self, record):
        try:
            if record.levelno == RAW_LEVEL:
                return record.msg
            else:
                if record.name.startswith(ACS_STATS_LOGGER_NAME):
                    record.name = record.name.split("%s." % ACS_STATS_LOGGER_NAME)[1]
                elif record.name.startswith(ACS_LOGGER_NAME):
                    record.name = record.name.split("%s." % ACS_LOGGER_NAME)[1]
                if len(record.name) > MAX_LOGGER_NAME:
                    record.name = '..' + record.name[len(record.name) - MAX_LOGGER_NAME:]
                return logging.Formatter.format(self, record)
        except TypeError as ex:
            sys.stderr.write(ex.message)


class ACSLogging(object):

    """
    Initialize python logging module

    """
    MINIMAL_LEVEL = 21
    file_handler = None
    stdout_handler = None
    memory_handler = None
    sys_log_handler = None

    formater = AltCustomFormatter(FORMATER_CONF, FORMATER_DATE_CONF)
    log_level = logging.DEBUG

    @staticmethod
    def initialize(stats_server="localhost", stats_port=514):
        """
        Initialize ACS logger

        """
        # stdout handler configuration
        ACSLogging.stdout_handler = logging.StreamHandler(sys.stdout)
        ACSLogging.stdout_handler.setFormatter(ACSLogging.formater)
        ACSLogging.stdout_handler.setLevel(logging.DEBUG)

        # memory handler to store logs waiting for file handler creation
        ACSLogging.memory_handler = handlers.MemoryHandler(1024 * 2)
        ACSLogging.memory_handler.setFormatter(ACSLogging.formater)
        ACSLogging.memory_handler.setLevel(logging.DEBUG)

        acs_logger = logging.getLogger(ACS_LOGGER_NAME)
        acs_logger.setLevel(logging.DEBUG)
        acs_logger.handlers = []
        acs_logger.addHandler(ACSLogging.stdout_handler)
        acs_logger.addHandler(ACSLogging.memory_handler)
        acs_logger.name = ACS_LOGGER_NAME
        logging.addLevelName(RAW_LEVEL, "RAW")
        logging.addLevelName(ACSLogging.MINIMAL_LEVEL, "MINIMAL")

        LOGGER_STATS.setLevel(logging.DEBUG)
        LOGGER_STATS.propagate = False
        ACSLogging.sys_log_handler = EnhSysLogHandler(address=(stats_server, stats_port))
        ACSLogging.sys_log_handler.setFormatter(AltCustomFormatter(STATS_FORMATER_CONF, FORMATER_DATE_CONF))
        LOGGER_STATS.addHandler(ACSLogging.sys_log_handler)

    @staticmethod
    def set_output_path(logfile):
        """
        File handler configuration

        :param logfile: The log filename

        """
        if os.path.isfile(logfile):
            os.remove(logfile)

        # Create file handler
        ACSLogging.file_handler = logging.FileHandler(logfile)
        ACSLogging.file_handler.setFormatter(ACSLogging.formater)
        ACSLogging.file_handler.setLevel(logging.DEBUG)

        # File handler is now created, we can write logs that were created before
        ACSLogging.memory_handler.setTarget(ACSLogging.file_handler)
        ACSLogging.memory_handler.flush()
        # Remove memory handler
        logging.getLogger(ACS_LOGGER_NAME).removeHandler(ACSLogging.memory_handler)
        ACSLogging.memory_handler = None

        # Add file handler
        logging.root.addHandler(ACSLogging.file_handler)

    @staticmethod
    def set_log_level(level, is_logging_level_aligned):
        """
        Sets the logging level (cf :mod:`logging`)

        :param level: The logging level
        :type level: str

        :param is_logging_level_aligned: Tells if MTBF logging level is aligned
            between the console and the log file
        :type is_logging_level_aligned: bool

        """
        ACSLogging.log_level = logging._levelNames.get(level.upper(), logging.DEBUG)  # pylint: disable=W0212
        ACSLogging.stdout_handler.setLevel(ACSLogging.log_level)
        # For MTBF testing, we offer the possibility to align console and log file logging levels
        # The corresponding parameter in the Campaign Desc is not available for other users
        if is_logging_level_aligned:
            ACSLogging.file_handler.setLevel(ACSLogging.log_level)

        if ACSLogging.log_level == logging.DEBUG:
            # Change ACSLogging formatting to debug since 'log_level' is equal to DEBUG
            ACSLogging.set_debug_formater()

    @staticmethod
    def get_log_level():
        """
        Getter which returns the ACSLogging current logging level

        :return: The logging level
        :rtype: int

        """
        return ACSLogging.log_level

    @staticmethod
    def set_debug_formater(debug_formatter=DEBUG_FORMATER_CONF):
        """
        Sets/Adds Debug info on the logging module according parameter 'debug_formatter'

        By default, it adds: [module_name.function_name():line_number]

        :param debug_formatter: The debugging formatting
        :type debug_formatter: str

        """
        formater = AltCustomFormatter(debug_formatter, FORMATER_DATE_CONF)

        if ACSLogging.file_handler is not None:
            ACSLogging.file_handler.setFormatter(formater)

    @staticmethod
    def close():
        """
        Close the file handler/file

        """
        if ACSLogging.file_handler is not None:
            ACSLogging.file_handler.flush()
            ACSLogging.file_handler.close()

    @staticmethod
    def set_session_id(id):
        ACSLogging.sys_log_handler.setFormatter(
            AltCustomFormatter(STATS_WID_FORMATTER_CONF.format(str(MAX_LOGGER_NAME + 2),
                                                               session_id=id),
                               FORMATER_DATE_CONF))
