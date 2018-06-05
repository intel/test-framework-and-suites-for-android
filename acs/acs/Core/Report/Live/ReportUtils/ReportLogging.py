"""
:copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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
:summary: This file implements the logging mechanism of ReportUtils
:since: 05/10/2015
:author: ssavrimoutou
"""
import os
import sys
import logging
from acs.Core.BenchConf import BenchConf
from acs.UtilitiesFWK.EnhSysLogHandler import EnhSysLogHandler
from acs.UtilitiesFWK.UuidUtilities import is_uuid4

RAW_LEVEL = 60
MAX_LOGGER_NAME = 20

REPORT_FILE_NAME = "taas_reporting_service.log"


TAAS_LOGGER_NAME = "TAAS"
TAAS_METRICS_LOGGER_NAME = "TAAS_METRICS"
REPORT_LOGGER_NAME = "REPORTING_SERVICE"

LOGGER_REPORT = logging.getLogger("{}.{}".format(TAAS_LOGGER_NAME, REPORT_LOGGER_NAME))
LOGGER_REPORT_METRICS = logging.getLogger("{}.{}".format(TAAS_METRICS_LOGGER_NAME, REPORT_LOGGER_NAME))

FORMATTER_DATE_CONF = "%d/%m %H:%M:%S"
FORMATTER_CONF = ("%(asctime)s.%(msecs)03d\t{0} %(name){1}s\t  "
                  "%(levelname)s\t%(message)s").format("ACS", str(MAX_LOGGER_NAME))
STATS_FORMATTER_CONF = ("%(asctime)s.%(msecs)03d\t{service} %(name){max_len}s\t  "
                        "%(levelname)s\t{session_id}%(message)s")


def push_metrics(**kwargs):
    """
    Push data to metrics server
    :param kwargs: data to push as method input
    """
    # Insert bench config data into the data metrics only for start_campaign
    if "event" in kwargs and kwargs["event"] == "start_campaign":
        kwargs.update(BenchConf.instance().get_properties())
    # Push data to metrics server
    LOGGER_REPORT_METRICS.info("; ".join(["{}={}".format(x, y) for x, y in kwargs.iteritems()]))


class AltCustomFormatter(logging.Formatter):

    def format(self, record):
        try:
            if record.levelno == RAW_LEVEL:
                return record.msg
            else:
                if record.name.startswith(TAAS_METRICS_LOGGER_NAME):
                    record.name = record.name.split("%s." % TAAS_METRICS_LOGGER_NAME)[1]
                elif record.name.startswith(TAAS_LOGGER_NAME):
                    record.name = record.name.split("%s." % TAAS_LOGGER_NAME)[1]
                if len(record.name) > MAX_LOGGER_NAME:
                    record.name = '..' + record.name[len(record.name) - MAX_LOGGER_NAME:]
                return logging.Formatter.format(self, record)
        except TypeError as ex:
            sys.stderr.write(ex.message)


class ReportLogging(object):

    """
    This class instantiates logger for report service
    """

    @staticmethod
    def init(stats_server="sdlunk.tl.intel.com", stats_port=514, session_id=None, report_dir=None):
        """
        Initialize loggers for report service
        :return:
        """
        if report_dir:
            LOGGER_REPORT.setLevel(logging.DEBUG)
            LOGGER_REPORT.propagate = False
            LOGGER_REPORT.handlers = []
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(AltCustomFormatter(FORMATTER_CONF, FORMATTER_DATE_CONF))
            stdout_handler.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(os.path.join(report_dir, REPORT_FILE_NAME))
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(AltCustomFormatter(FORMATTER_CONF, FORMATTER_DATE_CONF))
            LOGGER_REPORT.addHandler(file_handler)
            LOGGER_REPORT.addHandler(stdout_handler)

        if stats_server and stats_port and is_uuid4(session_id):
            stats_formatter = STATS_FORMATTER_CONF.format(service=TAAS_METRICS_LOGGER_NAME,
                                                          session_id="testRequestId={}; ".format(session_id),
                                                          max_len=str(MAX_LOGGER_NAME))
            LOGGER_REPORT_METRICS.setLevel(logging.DEBUG)
            LOGGER_REPORT_METRICS.propagate = False
            sys_log_handler = EnhSysLogHandler(address=(stats_server, stats_port))
            sys_log_handler.setFormatter(AltCustomFormatter(stats_formatter, FORMATTER_DATE_CONF))
            LOGGER_REPORT_METRICS.addHandler(sys_log_handler)

        return LOGGER_REPORT
