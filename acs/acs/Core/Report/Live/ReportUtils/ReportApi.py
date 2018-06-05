"""
@copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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

@organization: INTEL SSG/OTC/QSI/SIS/CTA
@summary: The module will play the role of proxy between the test framework
and the reporting service
@since: 28/09/15
@author: alouahax
"""
# pylama: ignore=E501
import uuid
import socket
import platform
import os
import copy
import getpass

from acs.Core.BenchConf import BenchConf
from acs.Core.Report.Live.ReportUtils.adapters.AdapterManager import AdapterManager
from acs.Core.Report.Live.IReport import IReport
from acs.Core.Report.Live.ReportUtils.RequestCache import request_cache
from acs.Core.Report.Live.ReportUtils.ReportLogging import ReportLogging
from acs.UtilitiesFWK.AttributeDict import AttributeDict
from acs.UtilitiesFWK.DateUtilities import utctime_iso8601
from acs.UtilitiesFWK.Utilities import Global
from acs.UtilitiesFWK.Utilities import Verdict


ISO8601_TIME_FORMAT = "YYYY-MM-DDTHH:mm:ss.SSSZ"
RERUN_PARENT_ORDER_BASE = 10000


def name2order(tc_name):
    ''' fack order for parent case '''
    return sum(map(ord, os.path.basename(tc_name)), RERUN_PARENT_ORDER_BASE)


class DataModel(object):

    """
    This object describes the status/verdict data model used by TCR
    reference link: https://wiki.ith.intel.com/display/DRD/Campaign+-+Data+model
    """

    STATUS = AttributeDict({
        "COMPLETED": "COMPLETED",
        "ABORTED": "CANCELLED",
        "CANCELLED": "CANCELLED",
        "INIT": "PENDING",
        "PENDING": "PENDING",
        "ONGOING": "RUNNING",
        "RUNNING": "RUNNING",
        "TIMEOUT": "TIMEOUT"
    })

    VERDICT = AttributeDict({
        "BLOCKED": "BLOCKED",
        "FAIL": "FAILED",
        "FAILED": "FAILED",
        "PASSED": "PASSED",
        "PASS": "PASSED",
        "VALID": "VALID",
        "INVALID": "INVALID",
        "INCONCLUSIVE": "INCONCLUSIVE",
        "NA": "NA"
    })


class ReportApi(IReport):

    """
    This module will be used to send events to TCR server
    It abstracts transport protocol and constructs message to send with a payload (effective data to send
    and a header (metadata to build a message to transport)
    """
    _additional_tc_results = {}
    _additional_tc_it_results = {}
    _campaign_start_time = None
    _campaign_id = None
    __test_cases = {}
    _test_id = None
    _test_it_id = None
    _test_parent_id = None
    _test_case_conf = {}
    _tc_device_info = {}
    _tc_start_time = None
    _tc_it_start_time = None
    _crash_events = []
    _dev_report_mode = False
    __report_logger = None
    __logger = None

    def __init__(self,
                 campaign_uuid,
                 dev_report_mode=False,
                 report_dir=None,
                 test_framework="ACS",
                 test_framework_version="",
                 rerun=False):

        # Initialize the adapter manager
        self._adapter_manager = AdapterManager.instance()
        self._adapter_manager.init(dev_report_mode=dev_report_mode)

        self._campaign_id = None
        self._test_framework = test_framework
        self._test_framework_version = test_framework_version
        self._dev_report_mode = dev_report_mode

        if report_dir:
            self.__logger = self._create_live_logger(campaign_uuid, report_dir)

        self._header = {'engine': self._test_framework,
                        'engineVersion': self._test_framework_version,
                        'hostname': socket.gethostname(),
                        'userAccount': getpass.getuser()}
        self._rerun = rerun
        self._rerun_tests = {}
        if self._rerun:
            # FIXME: bugs if Campaign have same name test case
            tcr_tests = self.get_testcases(campaign_uuid)
            rerun_tests = {}
            for tc in tcr_tests:
                if tc['phase'] != 'CORE' or tc['verdict'] not in ['PASSED', 'INCONCLUSIVE']:
                    rerun_tests[tc['testCase']] = tc
            self._rerun_tests = rerun_tests

    @property
    def campaign_id(self):
        return self._campaign_id

    @property
    def campaign_url(self):
        return self._adapter_manager.campaign_url

    @staticmethod
    def _handle_resource_file(resource, display_name, retention):
        payload = {'data': {},
                   'file': resource}
        if display_name:
            payload['data']['displayname'] = display_name
        if retention in ('SHORT', 'LONG'):
            payload['data']['retention'] = retention
        return payload

    @staticmethod
    def _create_live_logger(campaign_uuid, report_dir):
        """
        Create live reporting instance with a dedicated log file in the campaign report dire
        Disable requests log and write them in live reporting logger file

        :param campaign_uuid: uuid of the campaign
        :type campaign_uuid: str

        :param report_dir: campaign report folder
        :type report_dir: str

        :return: live logger report instance
        """

        logger = None

        if report_dir:
            report_logger = ReportLogging()
            logger = report_logger.init(session_id=campaign_uuid, report_dir=report_dir)
        return logger

    def _update_device_info(self, payload, info, iteration=False):
        """
        Update device info (build, ...) for current test case

        :param dict payload: The wrapping payload
        :param dict info: The Device info
        :param bool iteration: Has current test case the "iteration mode" enabled
        """
        if info and not iteration:
            self._tc_device_info = info
            payload.update(info)

    @request_cache
    def start_campaign(self, campaign_uuid, campaign_name, email):
        """
        Send start campaign event to the server

        :param campaign_uuid: campaign execution instance unique identifier
        :type campaign_uuid: str

        :param campaign_name: campaign name
        :type campaign_name: str

        :param email: user email
        :type email: str
        """
        if self._campaign_id:
            self.__logger and self.__logger.warning("Start campaign info message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        self._campaign_id = campaign_uuid
        # Create the campaign
        # Set it to "Running"
        self._campaign_start_time = utctime_iso8601()
        campaign_start_time = str(self._campaign_start_time.format(ISO8601_TIME_FORMAT))

        # Update BenchConf instance
        BenchConf.instance().user_email = email
        payload = {
            'id': campaign_uuid,
            'name': campaign_name,
            'userEmail': email,
            'type': 'test',
            'status': DataModel.STATUS.RUNNING,
            'verdict': DataModel.VERDICT.NA,
            'startTime': campaign_start_time,
        }
        header = {
            'requestId': campaign_uuid
        }
        header.update(self._header)
        return {'header': header, 'payload': payload}

    @request_cache
    def send_campaign_resource(self, resource, display_name=None, retention="SHORT"):
        """
        Push a resource onto TCR REST API for a given Campaign

        :param resource: Local resource to be pushed onto TCR at Campaign level.
        :type resource: str

        :param display_name (optional): Filename to be displayed in the UI
        :type display_name: str

        :param retention (optional): "SHORT" or "LONG"
        :type retention: str
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Campaign resource not pushed! Campaign ID does not exist!")
            return None

        header = {'requestId': self._campaign_id}
        header.update(self._header)
        payload = self._handle_resource_file(resource, display_name, retention)
        return {'header': header, 'payload': payload}

    @request_cache
    def stop_campaign(self, status, verdict, campaign_info=None):
        """
        Send stop campaign event to the server

        :param status: campaign status
        :type status: str

        :param verdict: campaign verdict
        :type verdict: str

        :param campaign_info: different campaign infos : (execution_rate, pass_rate, fail_rate and some campaign
        statistics)
        :type campaign_info: dict
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Stop campaign info message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        # compute test case stop time and duration
        stop_time = utctime_iso8601()
        exec_time = stop_time - self._campaign_start_time

        status = DataModel.STATUS[status]
        if status != DataModel.STATUS.CANCELLED:
            if verdict == Global.BLOCKED:
                verdict = DataModel.VERDICT.BLOCKED
            elif verdict == Global.FAILURE:
                verdict = DataModel.VERDICT.FAILED
            elif verdict == Global.SUCCESS:
                verdict = DataModel.VERDICT.PASSED
            else:
                verdict = DataModel.VERDICT.NA
        else:
            verdict = DataModel.VERDICT.NA

        campaign_info = campaign_info or {}
        payload = {"status": status,
                   "verdict": verdict,
                   "stopTime": str(stop_time.format(ISO8601_TIME_FORMAT)),
                   "duration": exec_time.total_seconds() * 1000,
                   "results": {
                       "executionRate": campaign_info.get("execution_rate", ""),
                       "passRate": campaign_info.get("pass_rate", ""),
                       "failRate": campaign_info.get("fail_rate", ""),
                       "blockedRate": campaign_info.get("blocked_rate", ""),
                       "validRate": campaign_info.get("valid_rate", ""),
                       "invalidRate": campaign_info.get("invalid_rate", ""),
                       "inconclusiveRate": campaign_info.get("inconclusive_rate", ""),
                       self._test_framework: campaign_info.get("stats", "")}}

        header = {'requestId': self._campaign_id}
        header.update(self._header)
        return {'header': header, 'payload': payload}

    @request_cache
    def create_testcase(self,
                        tc_name,
                        uc_name,
                        tc_phase,
                        tc_type,
                        tc_domain,
                        tc_order,
                        is_warning,
                        tc_parameters,
                        framework_version=None,
                        bulk=False):
        """
         Send http request to server to create test case entry

        :param tc_name: test case name
        :type tc_name: str

        :param uc_name: use case name
        :type uc_name: str

        :param tc_order: the test case order
        :type tc_order: int

        :param is_warning: is TC marked as warning or not
        :type is_warning: bool

        :param tc_parameters: parameters of the test case
        :type tc_parameters: str

        :param framework_version: the framework version
        :type framework_version: str

        :param bulk: true if you want to bulk your testcase creation
        :type bulk: bool

        """

        if not self._campaign_id:
            self.__logger and self.__logger.warning("Create test message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        if self._test_id in self.__test_cases.values():
            self.__logger and self.__logger.warning("Test case id is invalid for test {}".format(tc_name))
            return None

        tc_basename = os.path.basename(tc_name)
        test_case_name = tc_basename
        parent_id = None
        if tc_basename in self._rerun_tests and not self._is_rerun_parent(tc_order):
            o_test = self._rerun_tests.get(tc_basename)
            parent_id = o_test.get('id')
            self.__test_cases[name2order(tc_name) - 1] = parent_id
            tcr = self._adapter_manager.get_protocol()
            if not o_test.get('rerun', False):  # first rerun
                # clone previous result to child
                child_test = copy.deepcopy(o_test)
                child_test.pop('id')
                child_test.pop('depth')
                child_test.pop('index')
                child_test.pop('indexForDisplay')

                child_test['parentId'] = parent_id
                child_test['ignoreVerdict'] = True
                tcr.create_testcase(self._header, child_test)
            # clean some status in parent TC
            o_test.update({
                "status": DataModel.STATUS.PENDING,
                "verdict": DataModel.VERDICT.NA,
                "rerun": True,
                "startTime": None,
                "stopTime": None,
                "result": None,
                "effect": True,  # force TCR to include parent Test in passRate
            })
            header = {"requestId": parent_id}
            header.update(self._header)
            tcr.update_testcase(header, o_test)
            test_case_name = tc_basename + ' - rerun'

        tc_id = str(uuid.uuid4())
        user_home = os.path.split(os.path.expanduser('~'))
        if platform.system() == "Windows":
            release = platform.release()
        elif platform.dist():
            release = "{0}_{1}".format(platform.dist()[0], platform.dist()[1])

        payload = {
            "testCase": test_case_name,
            "id": tc_id,
            "type": tc_type,
            "domain": tc_domain,
            "phase": tc_phase,
            "engine": self._test_framework,
            "campaignId": self._campaign_id,
            "useCase": uc_name,
            "relativePath": os.path.dirname(tc_name),
            "status": DataModel.STATUS.PENDING,
            "verdict": DataModel.VERDICT.NA,
            "ignoreVerdict": is_warning,
            "bench": {
                "name": socket.getfqdn(),
                "user": user_home[-1],
                "os": "{0}_{1}".format(platform.system(), release),
                "{0}Version".format(str(self._test_framework).title()): framework_version or "",
                "pythonVersion": "{0}_{1}".format(platform.python_version(),
                                                  platform.architecture()[0])
            }
        }

        if parent_id:
            payload["parentId"] = parent_id
            payload['ignoreVerdict'] = True  # only care about parent Verdict

        if tc_parameters:
            self._test_case_conf.update({"parameters": tc_parameters})
            payload.update({self._test_framework: self._test_case_conf})

        self.__test_cases[tc_order - 1] = tc_id

        if not bulk:
            header = {"requestId": tc_id}
            header.update(self._header)
            return {"header": header, "payload": payload}
        else:
            # Return only the payload if you want to use the create_bulk_testcases method
            return payload

    @request_cache
    def create_bulk_testcases(self, tc_data):
        """
         Send http request to server to create a test case bulk

        :param tc_data: list of dict
        :type tc_data: list
        """
        tc_order = 1
        for elem in tc_data:
            if self._test_id is not None:
                if not self._campaign_id:
                    self.__logger and self.__logger.warning("Create test message not sent!"
                                                            "Campaign ID does not exist!")
                    return None

                if not elem.get("testCase"):
                    self.__logger and self.__logger.warning("Create test message not sent!"
                                                            "TestCase Name does not exist!")
                    return None
                # Update payload with mandatory element
                elem["id"] = str(uuid.uuid4())
                elem["engine"] = self._test_framework
                elem["campaignId"] = self._campaign_id
                elem["parentId"] = self._test_id

                # compute test case verdict for test campaign report tool
                if not elem.get("verdict") or elem.get("verdict") == Verdict.INTERRUPTED:
                    elem["status"] = DataModel.STATUS.CANCELLED
                    elem["verdict"] = DataModel.VERDICT.NA
                else:
                    elem["status"] = DataModel.STATUS.COMPLETED
                    elem["verdict"] = DataModel.VERDICT[elem.get("verdict")]
            else:
                elem.update(self.create_testcase(tc_name=elem.get("testCase"),
                                                 uc_name=elem.get("useCase"),
                                                 tc_order=tc_order,
                                                 tc_parameters=elem.get("parameters"),
                                                 bulk=True))
                tc_order += 1

        header = {"requestId": self._campaign_id}
        header.update(self._header)
        return {"header": header, "payload": tc_data}

    @request_cache
    def start_testcase(self, tc_name, tc_order=1, device_info=None, iteration=False):
        """
        Send start test case event to the server

        :param tc_name: test case name
        :type tc_name: str

        :param tc_order: the test case order
        :type tc_order: int

        :param device_info (optional): Additional device info of the dut.
        :type device_info: dict

        :param iteration (optional): True if the test case has at least two iterations and is the "parent" test case
        :type iteration: boolean
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Start test message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        if self._test_id and (self._test_it_id or not iteration):
            self.__logger and self.__logger.warning("Start test message not sent (test_id already exists: {}"
                                                    .format(tc_name))
            return None

        if self._rerun and not self._is_rerun_parent(tc_order) and not iteration:
            # update parent test case
            self.start_testcase(tc_name, name2order(tc_name), device_info=device_info)
            self._test_parent_id = self.__test_cases[name2order(tc_name) - 1]

        start_time = utctime_iso8601()

        # Set the correct start time according to step's kind
        if iteration:
            self._test_it_id = str(uuid.uuid4())
            self._tc_it_start_time = start_time
        else:
            self._test_id = self.__test_cases[tc_order - 1]
            self._tc_start_time = start_time

        payload = {
            "campaignId": self._campaign_id,
            "startTime": str(start_time.format(ISO8601_TIME_FORMAT)),
            "status": DataModel.STATUS.RUNNING
        }

        self._update_device_info(payload, device_info, iteration=iteration)

        if iteration:
            payload.update({"id": self._test_it_id,
                            "testCase": os.path.basename(tc_name),
                            "parentId": self._test_id})

        header = {'requestId': self._test_it_id if iteration else self._test_id}
        header.update(self._header)
        return {'header': header, 'payload': payload}

    @request_cache
    def update_testcase(self, crash_list=None, test_info=None, device_info=None, iteration=False, testId=None):
        """
        Update a test case (during b2b iterations) and send to TCR

        :param iteration (optional): True if the test case has at least two iterations and is the "parent" test case
        :type iteration: boolean


        :param crash_list (optional): Current crash list
        :type crash_list: crash id list

        :param test_info (optional): Additional test case result info (can test step, external test case results, ...)
                                    (Dictionary key = section name, data = json serializable value data)
        :type test_info: dict

        :param device_info (optional): Additional device info of the dut.
        :type device_info: dict

        :param testId: (optional) if provided, use this as ID
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Update test case message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        if not self._test_id or (not self._test_it_id and iteration):
            self.__logger and self.__logger.warning("There is no currently running test to update.")
            return None
        payload = {}

        # Update crash list events for current test case
        if crash_list:
            self._crash_events.extend(crash_list)
            payload["crashEvent"] = crash_list

        # Update additional test case result information for current test case and temporary result is prepared
        # to be sent to TCR
        if test_info:
            if iteration:
                self._additional_tc_it_results.update(test_info)
                payload["result"] = self._additional_tc_it_results
            else:
                self._additional_tc_results.update(test_info)
                payload["result"] = self._additional_tc_results

            self._update_device_info(payload, device_info, iteration=iteration)

        if testId:
            header = {'requestId': testId}
        else:
            header = {'requestId': self._test_it_id if iteration else self._test_id}
        header.update(self._header)
        return {'header': header, 'payload': payload}

    @request_cache
    def send_testcase_resource(self, resource, display_name=None, retention="SHORT", iteration=False):
        """
        Push a resource onto TCR REST API for a given Test Case.

        :param resource: Local resource to be pushed onto TCR at Test Case level.
        :type resource: str

        :param display_name (optional): Filename to be displayed in the UI
        :type display_name: str

        :param retention (optional): "SHORT" or "LONG"
        :type retention: str

        :param iteration (optional): True if the test case has at least two iterations
        :type iteration: bool
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Test case resource not pushed!"
                                                    "Campaign ID does not exist!")
            return None

        if not self._test_id or (not self._test_it_id and iteration):
            self.__logger and self.__logger.warning("There is no currently running test case to push resource to.")
            return None

        header = {'requestId': self._test_it_id if iteration else self._test_id}
        header.update(self._header)
        payload = self._handle_resource_file(resource, display_name, retention)
        return {'header': header, 'payload': payload}

    @request_cache
    def send_testcase_chart(self, chart_info, iteration=False):
        """
        Push chart attached to a test case

        :param data: data to build the chart on the server (title, series, axis ...)
        :type data: dict
        :param iteration (optional): True if the test case has at least two iterations
        :type iteration: bool
        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Test case resource not pushed!"
                                                    "Campaign ID does not exist!")
            return None

        if not self._test_id or (not self._test_it_id and iteration):
            self.__logger and self.__logger.warning("There is no currently running test case to push resource to.")
            return None

        header = {'requestId': self._test_it_id if iteration else self._test_id}
        header.update(self._header)
        payload = {'chart_info': chart_info}
        return {'header': header, 'payload': payload}

    @request_cache
    def stop_testcase(self, verdict, execution_nb, tc_parameters=None, tc_properties=None, tc_comments=None,
                      iteration=False,
                      device_info=None):
        """
        Send stop test case event to the server

        :param verdict: tc verdict
        :type verdict: str

        :param execution_nb: Number of test execution
        :type execution_nb: int

        :param tc_parameters (optional): dict of test execution parameters
        :type tc_parameters: dict

        :param tc_properties (optional): properties of the test case (b2b iteration, retries ..)
        :type tc_properties: dict

        :param tc_comments (optional): list of test execution comments
        :type tc_comments: list

        :param iteration (optional): True if the test case has at least two iterations and is the "parent" test case
        :type iteration: boolean

        :param device_info (optional): Additional device info of the dut.
        :type device_info: dict

        """
        if not self._campaign_id:
            self.__logger and self.__logger.warning("Stop test case info message not sent!"
                                                    "Campaign ID does not exist!")
            return None

        if not self._test_id or (not self._test_it_id and iteration):
            self.__logger and self.__logger.warning("There is no currently running test case to stop.")
            return None

        if self._rerun and self._test_id != self._test_parent_id and not iteration:
            bak_test_id = self._test_id
            bak_start_time = self._tc_start_time
            self._test_id = self._test_parent_id
            self.stop_testcase(verdict, execution_nb, tc_parameters=tc_parameters,
                               tc_properties=tc_properties, tc_comments=tc_comments,
                               device_info=device_info)
            self._test_id = bak_test_id
            self._tc_start_time = bak_start_time

        # compute test case verdict for test campaign report tool
        if verdict == Verdict.INTERRUPTED:
            status = DataModel.STATUS.CANCELLED
            verdict = DataModel.VERDICT.NA
        else:
            status = DataModel.STATUS.COMPLETED
            verdict = DataModel.VERDICT[verdict]

        # compute stop time and duration according to the step's kind start time (iteration or testcase)
        stop_time = utctime_iso8601()

        start_time = self._tc_it_start_time if iteration else self._tc_start_time
        exec_time = stop_time - start_time
        duration = exec_time.microseconds / 1000 + exec_time.seconds * 1000 + exec_time.days * 24 * 3600

        result_node = self._additional_tc_it_results if iteration else self._additional_tc_results

        if tc_parameters:
            self._test_case_conf.update({"parameters": tc_parameters})
        if tc_properties:
            self._test_case_conf.update({"properties": tc_properties})
        if tc_comments:
            self._test_case_conf.update({"comments": tc_comments})

        payload = {"status": status,
                   "verdict": verdict,
                   "stopTime": str(stop_time.format(ISO8601_TIME_FORMAT)),
                   "duration": duration,
                   "result": result_node,
                   "nbTries": execution_nb,
                   self._test_framework: self._test_case_conf}

        # Remove crash events if any for next test case
        if self._crash_events:
            self._crash_events = []

        self._update_device_info(payload, device_info, iteration=iteration)

        header = {'requestId': self._test_it_id if iteration else self._test_id}
        header.update(self._header)
        # Clean data
        if not iteration:
            # Clean external tc results (for next run)
            self._additional_tc_results = {}
            self._test_id = None
            self._tc_start_time = None
            self._tc_device_info = {}
        else:
            self._additional_tc_it_results = {}
            self._test_it_id = None
            self._tc_it_start_time = None
        return {'header': header, 'payload': payload}

    def get_testcases(self, campaign_id, iteration=False):
        '''
        Send get Campaign test cases

        :param campaign_id: campaign ID
        :iteration: whether to fetch iteration test case

        return a list of test case associated to this Campaign
        '''
        protocol = self._adapter_manager.get_protocol()
        header = {
            'requestId': campaign_id,
            'iteration': iteration
        }
        return protocol.get_testcases(header, payload=None)

    def is_rerun(self, tc_name):
        return os.path.basename(tc_name) in self._rerun_tests

    def _is_rerun_parent(self, tc_order):
        if self._rerun and tc_order > RERUN_PARENT_ORDER_BASE:
            return True
        else:
            return False
