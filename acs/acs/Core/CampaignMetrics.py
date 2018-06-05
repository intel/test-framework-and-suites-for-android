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
:summary: Implements campaign metrics
:since: 03/09/2013
:author: ssavrimoutou
"""
from datetime import datetime, timedelta

from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.UtilitiesFWK.Utilities import Singleton
import lxml.etree as ElementTree


CAMPAIGN_METRICS_TAG = "Statistics"
CAMPAIGN_START_DATE_TAG = "StartExecutionDate"
CAMPAIGN_START_TIME_TAG = "StartExecutionTime"
EXECUTION_TIME_TAG = "ExecutionTime"

TOTAL_BOOT_COUNT_TAG = "TotalBootCount"
BOOT_FAILURE_COUNT_TAG = "BootFailureCount"
UNEXPECTED_REBOOT_COUNT = "UnexpectedRebootCount"
CONNECT_FAILURE_COUNT_TAG = "ConnectFailureCount"
CRITICAL_FAILURE_COUNT_TAG = "CriticalFailureCount"
TIME_TO_FIRST_CRITICAL_FAILURE_TAG = "TimeToCriticalFailure"
MTBF_TAG = "MeanTimeBeforeFailure"

PASS_RATE_TAG = "PassRate"
FAIL_RATE_TAG = "FailRate"
BLOCKED_RATE_TAG = "BlockedRate"
VALID_RATE_TAG = "ValidRate"
INVALID_RATE_TAG = "InvalidRate"
INCONCLUSIVE_RATE_TAG = "InconclusiveRate"
EXECUTION_RATE_TAG = "ExecutionRate"


class CampaignMetrics(object):

    """
    This class computes all metrics during campaign execution (execution time, mtbf, boot failure...)
    """
    __metaclass__ = Singleton

    def __init__(self):
        self._logger = LOGGER_FWK
        self.__campaign_metrics = {CAMPAIGN_START_DATE_TAG: "---",
                                   CAMPAIGN_START_TIME_TAG: "---",
                                   EXECUTION_TIME_TAG: 0,
                                   TOTAL_BOOT_COUNT_TAG: 0,
                                   UNEXPECTED_REBOOT_COUNT: 0,
                                   BOOT_FAILURE_COUNT_TAG: 0,
                                   CONNECT_FAILURE_COUNT_TAG: 0,
                                   CRITICAL_FAILURE_COUNT_TAG: 0,
                                   TIME_TO_FIRST_CRITICAL_FAILURE_TAG: "---",
                                   MTBF_TAG: "---",
                                   PASS_RATE_TAG: 0.0,
                                   FAIL_RATE_TAG: 0.0,
                                   BLOCKED_RATE_TAG: 0.0,
                                   VALID_RATE_TAG: 0.0,
                                   INVALID_RATE_TAG: 0.0,
                                   INCONCLUSIVE_RATE_TAG: 0.0,
                                   EXECUTION_RATE_TAG: 0.0}

        self.__campaign_start_datetime = None

        self.__mtbf_ref_datetime = None
        self.__tbf_table = []

        self.total_tc_count = 0
        self.__tc_executed_count = 0
        self.tc_skipped_count = 0
        self.pass_verdict_count = 0
        self.fail_verdict_count = 0
        self.blocked_verdict_count = 0
        self.valid_verdict_count = 0
        self.invalid_verdict_count = 0
        self.inconclusive_verdict_count = 0

    @property
    def unexpected_reboot_count(self):
        """
        Get the campaign start date
        """
        return self.__campaign_metrics.get(UNEXPECTED_REBOOT_COUNT, 0)

    @unexpected_reboot_count.setter
    def unexpected_reboot_count(self, value):
        self.__campaign_metrics[UNEXPECTED_REBOOT_COUNT] = value

    @property
    def campaign_start_date(self):
        """
        Get the campaign start date
        """
        return self.__campaign_metrics[CAMPAIGN_START_DATE_TAG]

    @property
    def campaign_start_time(self):
        """
        Get the campaign start time
        """
        return self.__campaign_metrics[CAMPAIGN_START_TIME_TAG]

    @property
    def campaign_start_datetime(self):
        """
        Get the campaign start datetime
        """
        return self.__campaign_start_datetime

    @campaign_start_datetime.setter
    def campaign_start_datetime(self, value):
        """
        set the the campaign start datetime
        """
        self.__campaign_start_datetime = value
        self.__campaign_metrics[CAMPAIGN_START_DATE_TAG] = value.strftime("%d/%m/%Y")
        self.__campaign_metrics[CAMPAIGN_START_TIME_TAG] = value.strftime("%H:%M:%S")

    @property
    def total_boot_count(self):
        """
        Get the number of boot performed by the framework during the campaign execution
        """
        return self.__campaign_metrics[TOTAL_BOOT_COUNT_TAG]

    @total_boot_count.setter
    def total_boot_count(self, value):
        """
        set the number of boot performed by the framework
        """
        self.__campaign_metrics[TOTAL_BOOT_COUNT_TAG] = value

    @property
    def boot_failure_count(self):
        """
        Get the number of boot failure during the campaign execution
        """
        return self.__campaign_metrics[BOOT_FAILURE_COUNT_TAG]

    @boot_failure_count.setter
    def boot_failure_count(self, value):
        """
        set boot failure count
        """
        self.__campaign_metrics[BOOT_FAILURE_COUNT_TAG] = value

    @property
    def connect_failure_count(self):
        """
        Get the number of device connection failure during the campaign execution
        """
        return self.__campaign_metrics[CONNECT_FAILURE_COUNT_TAG]

    @connect_failure_count.setter
    def connect_failure_count(self, value):
        """
        set device connection failure count
        """
        self.__campaign_metrics[CONNECT_FAILURE_COUNT_TAG] = value

    @property
    def critical_failure_count(self):
        """
        Get the number of critical failure during the campaign execution
        """
        return self.__campaign_metrics[CRITICAL_FAILURE_COUNT_TAG]

    @property
    def mtbf(self):
        """
        Get the mean time between critical failures
        """
        return self.__campaign_metrics[MTBF_TAG]

    @property
    def time_to_first_critical_failure(self):
        """
        Get the elapsed time between campaign's start and first critical failure
        """
        return self.__campaign_metrics[TIME_TO_FIRST_CRITICAL_FAILURE_TAG]

    def add_critical_failure(self):
        """
        Increment critical failure count, and update related data (mtbf and time to first critical)
        """
        # increment critical failure count
        self.__campaign_metrics[CRITICAL_FAILURE_COUNT_TAG] += 1

        # if it is the first critical failure, compute time to first critical
        if self.critical_failure_count == 1:
            time_to_fcf = datetime.now() - self.__campaign_start_datetime
            time_to_fcf_sec = (time_to_fcf.seconds + time_to_fcf.days * 24 * 3600)
            self.__campaign_metrics[TIME_TO_FIRST_CRITICAL_FAILURE_TAG] = str(timedelta(seconds=time_to_fcf_sec))

        # add a deltatime in "time between failure" table, if possible
        if self.__mtbf_ref_datetime is not None:
            tbf = datetime.now() - self.__mtbf_ref_datetime
            tbf_sec = (tbf.seconds + tbf.days * 24 * 3600)
            self.__tbf_table.append(tbf_sec)

        # update mtbf
        self.__campaign_metrics[MTBF_TAG] = self.__compute_mtbf()

    def set_mtbf_ref_time(self):
        """
        Reset reference datetime for mtbf. This datetime is used on critical failure to compute tbf
        """
        self.__mtbf_ref_datetime = datetime.now()

    def __compute_mtbf(self):
        """
        This function return the mean time between failure
        """
        # If no critical failure or only one, MTBF cannot be computed
        if len(self.__tbf_table) == 0:
            mtbf = "---"

        # Compute MTBF
        else:
            # Computes mtbf in seconds
            mtbf_sec = sum(self.__tbf_table) / len(self.__tbf_table)

            # Convert mtbf in datetime for display
            mtbf = str(timedelta(seconds=mtbf_sec))

        return mtbf

    @property
    def execution_time(self):
        """
        Get execution time (time since campaign beginning), as a datetime string

        :return: execution time
        :rtype: str
        """
        return self.__campaign_metrics.get(EXECUTION_TIME_TAG)

    @property
    def tc_not_executed_count(self):
        return self.total_tc_count - self.tc_executed_count

    @property
    def tc_executed_count(self):
        return self.__tc_executed_count

    @tc_executed_count.setter
    def tc_executed_count(self, value):
        self.__tc_executed_count = value

    @property
    def execution_rate(self):
        """
        :return: execution rate
        :rtype: str
        """
        return self.__campaign_metrics.get(EXECUTION_RATE_TAG)

    @property
    def pass_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[PASS_RATE_TAG]

    @property
    def fail_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[FAIL_RATE_TAG]

    @property
    def blocked_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[BLOCKED_RATE_TAG]

    @property
    def valid_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[VALID_RATE_TAG]

    @property
    def invalid_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[INVALID_RATE_TAG]

    @property
    def inconclusive_rate(self):
        self.__compute_verdict_statistics()
        return self.__campaign_metrics[INCONCLUSIVE_RATE_TAG]

    def __compute_execution_time(self):
        """
        Compute the execution time
        """
        exec_time = datetime.now() - self.__campaign_start_datetime
        self.__campaign_metrics[EXECUTION_TIME_TAG] = (exec_time.seconds + exec_time.days * 24 * 3600)

    def __compute_execution_rate(self):
        """
        Compute the execution rate
        """
        if self.total_tc_count > 0:
            execution_rate = (float(self.tc_executed_count) / float(self.total_tc_count)) * 100
        else:
            execution_rate = 0

        # Store it in statistics dict
        self.__campaign_metrics[EXECUTION_RATE_TAG] = execution_rate

    def __compute_verdict_statistics(self):
        """
        This function computes the report statistics to be included in the XML test report (PASS, FAIL, INC rates)
        """
        pass_rate = 0
        fail_rate = 0
        block_rate = 0
        valid_rate = 0
        invalid_rate = 0
        inconclusive_rate = 0

        if self.tc_executed_count > 0:
            # Compute Pass, Fail, Blocked rates
            pass_rate = round(100 * self.pass_verdict_count / float(self.tc_executed_count), 1)
            fail_rate = round(100 * self.fail_verdict_count / float(self.tc_executed_count), 1)
            block_rate = round(100 * self.blocked_verdict_count / float(self.tc_executed_count), 1)
            valid_rate = round(100 * self.valid_verdict_count / float(self.tc_executed_count), 1)
            invalid_rate = round(100 * self.invalid_verdict_count / float(self.tc_executed_count), 1)
            inconclusive_rate = round(100 * self.inconclusive_verdict_count / float(self.tc_executed_count), 1)

        # Update metrics dict
        self.__campaign_metrics[PASS_RATE_TAG] = pass_rate
        self.__campaign_metrics[FAIL_RATE_TAG] = fail_rate
        self.__campaign_metrics[BLOCKED_RATE_TAG] = block_rate
        self.__campaign_metrics[VALID_RATE_TAG] = valid_rate
        self.__campaign_metrics[INVALID_RATE_TAG] = invalid_rate
        self.__campaign_metrics[INCONCLUSIVE_RATE_TAG] = inconclusive_rate

    def get_metrics(self, output_format="dict", **options):
        """
        This function returns the campaign metrics in following format:
            - txt : return the metrics formatted in text
            - xml : returns the metrics as an xml object (lxml.etree)
            - dict: returns the metrics as a dictionary

        :type output_format: str
        :param output_format: The format to return the metrics.
                              Supported output format are: dict (default value), xml, txt

        :param options: (optional) all sort of extra parameters (ie. log_metrics, ...)

        :rtype: Depending on the output format (txt, dict, xml obj)
        :return: The campaign metrics
        """

        # Compute execution time, rate, and statistics to fill internal dict

        self.__compute_execution_time()
        self.__compute_execution_rate()

        self.__compute_verdict_statistics()

        # Format metrics
        campaign_metrics = self.__campaign_metrics.copy()
        # Format as string percentage (stupid but necessary)
        campaign_metrics[PASS_RATE_TAG] = "%.01f%%" % campaign_metrics[PASS_RATE_TAG]
        campaign_metrics[FAIL_RATE_TAG] = "%.01f%%" % campaign_metrics[FAIL_RATE_TAG]
        campaign_metrics[BLOCKED_RATE_TAG] = "%.01f%%" % campaign_metrics[BLOCKED_RATE_TAG]
        campaign_metrics[VALID_RATE_TAG] = "%.01f%%" % campaign_metrics[VALID_RATE_TAG]
        campaign_metrics[INVALID_RATE_TAG] = "%.01f%%" % campaign_metrics[INVALID_RATE_TAG]
        campaign_metrics[INCONCLUSIVE_RATE_TAG] = "%.01f%%" % campaign_metrics[INCONCLUSIVE_RATE_TAG]
        campaign_metrics[EXECUTION_RATE_TAG] = "%.01f%%" % campaign_metrics[EXECUTION_RATE_TAG]
        # Format execution time
        campaign_metrics[EXECUTION_TIME_TAG] = str(timedelta(seconds=campaign_metrics[EXECUTION_TIME_TAG]))

        # prepare metrics as a string
        campaign_metrics_str = "%s: " % CAMPAIGN_METRICS_TAG
        campaign_metrics_str += ', '.join("%s=%r" % campaign_metrics_element
                                          for campaign_metrics_element
                                          in campaign_metrics.iteritems())

        if options.get('log_metrics', False):
            # TODO: Shouldn't be INFO level instead of DEBUG ?
            self._logger.debug(campaign_metrics_str)

        if output_format == "txt":
            # Return the campaign metrics in text format
            campaign_metrics = campaign_metrics_str

        elif output_format == "xml":
            # Return the campaign metrics in xml format
            xml_campaign_metrics = ElementTree.Element(CAMPAIGN_METRICS_TAG)
            for metric_element in campaign_metrics.iterkeys():
                child_tag = ElementTree.SubElement(xml_campaign_metrics, metric_element)
                child_tag.text = str(campaign_metrics[metric_element])
            campaign_metrics = xml_campaign_metrics

        return campaign_metrics


# Code used for testing
if __name__ == "__main__":
    campaign_metric = CampaignMetrics.instance()
    campaign_metric.campaign_start_datetime = datetime.now()
    print(ElementTree.tostring(campaign_metric.get_metrics("xml"), pretty_print=True))
    print(campaign_metric.get_metrics("txt"))
    print(campaign_metric.get_metrics())
