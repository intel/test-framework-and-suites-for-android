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
@summary: TCR adapter to send request based on REST API

@since: 29/09/15
@author: ssavrimoutou
"""
# pylama: ignore=E501
from acs.Core.Report.Live.ReportUtils.protocols.Rest import HTTPRESTSession
from acs.Core.Report.ACSLogging import LOGGER_FWK

PUSH_EVENT_TIMEOUT = 30
PUSH_FILE_TIMEOUT = 3600
DEV_SERVER_API_URL = "http://tcr-d.sh.intel.com/1"
DEV_WEB_REPORTING_URL = "http://tcr-d.sh.intel.com/#"
PROD_SERVER_API_URL = "http://api.tcr.sh.intel.com/1"
PROD_WEB_REPORTING_URL = "https://tcr.sh.intel.com/#"


class TCRAdapter(HTTPRESTSession):

    def __init__(self, username='anonymous', password='anonymous', retry=None, **kwargs):
        """
        Constructor

        :param username: The credential username (anonymous)
        :param password: The credential password (anonymous)
        :param retry: The HTTP `Retry` options
            (cf. requests.packages.urllib3.util.retry.Retry)
        """
        super(TCRAdapter, self).__init__(username, password, **retry or {})
        dev_mode = kwargs.get('dev_report_mode', False)
        self._api_url = DEV_SERVER_API_URL if dev_mode else PROD_SERVER_API_URL
        self._web_reporting_url = DEV_WEB_REPORTING_URL if dev_mode else PROD_WEB_REPORTING_URL
        self.campaign_url = ""

    def __print_user_agent(self, header):
        """
        format header to correct string
        :param header: dict
        :return: formatted string
        """
        return ', '.join(['{}: {}'.format(k, v) for k, v in header.iteritems()])

    def start_campaign(self, header, payload):
        # Build the test report link to display in the logs
        campaign_id = header['requestId']
        user_agent = self.__print_user_agent(header)
        rest_api_url = "{0}{1}".format(self._api_url, '/campaigns')
        headers = {'content-type': 'application/json',
                   'User-Agent': "{}".format(user_agent)}
        # first check if campaign exists
        campaign_url = rest_api_url + '/' + campaign_id
        response = self.send_get_request(url=campaign_url,
                                         headers=headers)
        if 'errorCode' in response and '404' in response.get('errorCode'):
            # Not found, create it
            response = self.send_start_event(url=rest_api_url,
                                             payload=payload,
                                             timeout=PUSH_EVENT_TIMEOUT,
                                             headers=headers)
        else:  # already exists, just update
            response = self.send_update_event(url=campaign_url,
                                              payload=payload,
                                              timeout=PUSH_EVENT_TIMEOUT,
                                              headers=headers)

        # Display the campaign url if the request is correctly sent
        if response and response.get('id') == campaign_id:
            self.campaign_url = "{0}/campaigns/{1}/detail".format(self._web_reporting_url, campaign_id)
            LOGGER_FWK.info("Meta Campaign UUID will be: {0}".format(campaign_id))
            LOGGER_FWK.info("TEST_REPORT_URL: {0}".format(self.campaign_url))
        return response

    def send_campaign_resource(self, header, payload):
        campaign_id = header["requestId"]
        user_agent = self.__print_user_agent(header)
        file2push = payload["file"]
        rest_api_url = "{0}{1}{2}{3}".format(self._api_url, '/campaigns/', campaign_id, "/attachments")
        headers = {'User-agent': "{}".format(user_agent)}
        response = self.send_resource_event(url=rest_api_url,
                                            resources=file2push,
                                            payload=payload["data"],
                                            timeout=PUSH_FILE_TIMEOUT,
                                            headers=headers)
        return response

    def stop_campaign(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}{2}".format(self._api_url, '/campaigns/', header['requestId'])
        response = self.send_stop_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT,
                                        headers=headers)
        return response

    def create_testcase(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}".format(self._api_url, '/tests')
        response = self.send_start_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT,
                                         headers=headers)
        return response

    def create_bulk_testcases(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}".format(self._api_url, '/tests/bulk')
        response = self.send_start_event(url=rest_api_url, payload=payload, timeout=PUSH_FILE_TIMEOUT,
                                         headers=headers)
        return response

    def start_testcase(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        if "parentId" in payload:
            rest_api_url = "{0}{1}".format(self._api_url, '/tests')
            response = self.send_start_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT,
                                             headers=headers)
        else:
            rest_api_url = "{0}{1}{2}".format(self._api_url, '/tests/', header["requestId"])
            response = self.send_update_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT,
                                              headers=headers)
        return response

    def update_testcase(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}{2}".format(self._api_url, '/tests/', header["requestId"])
        response = self.send_update_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT,
                                          headers=headers)
        return response

    def send_testcase_resource(self, header, payload):
        user_agent = self.__print_user_agent(header)
        rest_api_url = "{0}{1}{2}{3}".format(self._api_url, '/tests/', header["requestId"], "/attachments")
        headers = {'User-agent': "{}".format(user_agent)}
        response = self.send_resource_event(url=rest_api_url,
                                            resources=payload["file"],
                                            payload=payload["data"],
                                            timeout=PUSH_FILE_TIMEOUT,
                                            headers=headers)
        return response

    def send_testcase_chart(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}{2}{3}".format(self._api_url, '/tests/', header["requestId"], "/charts")
        response = self.send_start_event(url=rest_api_url,
                                         payload={'options': payload["chart_info"]},
                                         timeout=PUSH_EVENT_TIMEOUT,
                                         headers=headers)
        return response

    def stop_testcase(self, header, payload):
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}{1}{2}".format(self._api_url, '/tests/', header["requestId"])
        response = self.send_stop_event(url=rest_api_url, payload=payload, timeout=PUSH_EVENT_TIMEOUT, headers=headers)
        return response

    def get_testcases(self, header, payload):
        campaign_uuid = header["requestId"]
        user_agent = self.__print_user_agent(header)
        headers = {'content-type': 'application/json',
                   'User-agent': "{}".format(user_agent)}
        rest_api_url = "{0}/campaigns/{1}/tests".format(self._api_url, campaign_uuid)
        response = self.send_get_request(url=rest_api_url, headers=headers)
        iteration = header.get('iteration', False)
        if not iteration and 'errorCode' not in response:  # filter out iteration cases
            response = filter(lambda t: t.get('depth', 0) == 0, response)
        return response
