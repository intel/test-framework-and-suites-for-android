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
@summary: The module will send live events to server based on REST API
@since: 04/09/15
@author: nbrissox
"""
# pylama: ignore=E501
import os
import json
import traceback

import requests
from requests import RequestException
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.models import Response

from acs.Core.Report.Live.ReportUtils.ReportLogging import LOGGER_REPORT
from acs.Core.Report.Live.ReportUtils.utils import StatusCode

try:
    from requests.packages.urllib3.util import Retry
except (NameError, ImportError, AttributeError):
    Retry = None


class HTTPRESTSession(requests.Session):

    """
    This is a base Class which implements
    some retrial & authentication (basic) mechanism.

    """

    # Define Authentication Class to be used (cf. requests/auth.py & doc)
    _authentication = HTTPBasicAuth
    # Define all point(s) to be mounted
    _mount_points = ('http', 'https')
    # Define the maximum retries count
    _DEFAULT_RETRIES_COUNT = 10
    _DEFAULT_CONNECT_COUNT = _DEFAULT_RETRIES_COUNT
    _DEFAULT_READ_COUNT = _DEFAULT_RETRIES_COUNT
    _DEFAULT_REDIRECT_BEHAVIOR = None

    if Retry:
        # Define all HTTP methods on which it should apply
        _DEFAULT_METHOD_WHITE_LIST = Retry.DEFAULT_METHOD_WHITELIST & {'POST'}
        _DEFAULT_BACKOFF_FACTOR = Retry.BACKOFF_MAX
    else:
        _DEFAULT_METHOD_WHITE_LIST = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST'])
        _DEFAULT_BACKOFF_FACTOR = 120

    _DEFAULT_STATUS_FORCE_LIST = {500, 503}
    _DEFAULT_RAISE_ON_REDIRECT = True

    def __init__(self, *args, **options):
        """
        Constructor

        :param args: All data related to authentication
        :param options: All data related to Retry mechanism
            (cf. requests.packages.urllib3.util.retry.Retry)

        """
        super(HTTPRESTSession, self).__init__()
        # Init logger
        self.logger = LOGGER_REPORT
        # Handle authentication
        self.auth = self._authentication(*args)
        # noinspection PyTypeChecker
        # Handle retries
        opts = {'max_retries': self._DEFAULT_RETRIES_COUNT}
        if Retry:
            opts['max_retries'] = Retry(**self._defaulted(options))

        adapter = HTTPAdapter(**opts)
        for mount_point in self._mount_points:
            self.mount(mount_point, adapter)

    def _defaulted(self, options):
        """
        This method takes into consideration default options,
        but some or all could be overridden.

        """
        default = {
            'total': self._DEFAULT_RETRIES_COUNT,
            'connect': self._DEFAULT_CONNECT_COUNT,
            'read': self._DEFAULT_READ_COUNT,
            'redirect': self._DEFAULT_REDIRECT_BEHAVIOR,
            'method_whitelist': self._DEFAULT_METHOD_WHITE_LIST,
            'status_forcelist': self._DEFAULT_STATUS_FORCE_LIST,
            'backoff_factor': self._DEFAULT_BACKOFF_FACTOR,
            'raise_on_redirect': self._DEFAULT_RAISE_ON_REDIRECT,
        }
        default.update(options)
        return default

    def _handle_payload_format(self, payload):
        """
        Handle the payload format.
        As REST expects JSON format,
        any non-string type shall be converted.

        :param payload: The payload to serialize/format

        :return:The serialized/formatted payload

        """
        if not isinstance(payload, basestring):
            try:
                payload = json.dumps(payload, sort_keys=True)
            except (TypeError, ValueError) as exception:
                self.logger and self.logger.warning(exception)
        return payload

    def request(self, method, url,
                params=None,
                payload=None,
                headers=None,
                cookies=None,
                files=None,
                auth=None,
                timeout=None,
                allow_redirects=True,
                proxies=None,
                hooks=None,
                stream=None,
                verify=None,
                cert=None):
        """
        Overridden method to include logging actions & some common behaviors

        Parameters:

            - cf. requests documentation

        """

        resp, response = None, None
        try:
            self.logger and self.logger.debug('sending "{0}" request at'
                                              ' {1} with parameters {2} {3}'.format(method, url, payload, files))

            response = super(HTTPRESTSession, self).request(method, url,
                                                            params=params,
                                                            data=payload,
                                                            headers=headers,
                                                            cookies=cookies,
                                                            files=files,
                                                            auth=auth,
                                                            timeout=timeout,
                                                            allow_redirects=allow_redirects,
                                                            proxies=proxies,
                                                            hooks=hooks,
                                                            stream=stream,
                                                            verify=verify,
                                                            cert=cert)
            response.raise_for_status()
            resp = response.json()
        except requests.exceptions.Timeout as exception:
            resp = {"errorCode": StatusCode.TIMEOUT,
                    "errorMessage": "Timed out {}".format(exception)}
        except requests.exceptions.ConnectionError as exception:
            resp = {"errorCode": StatusCode.CONNECTION_ERROR,
                    "errorMessage": "Connection error {}".format(exception)}
        except requests.exceptions.HTTPError as exception:
            resp = {"errorCode": StatusCode.HTTP_CODE_ERROR.format(status_code=exception.response.status_code),
                    "errorMessage": "Http error {}".format(exception)}
        except Exception as exception:
            resp = {"errorCode": StatusCode.UNEXPECTED_ERROR,
                    "errorMessage": "Unexpected Error {}".format(exception)}

        # Gathering debugging context when an Error occurs
        if resp and "errorMessage" in resp:
            self.logger and self.logger.error(resp['errorMessage'])
            context = {
                'method': method,
                'url': url,
                'headers': headers,
                # Getting detailed error
                'tb': traceback.format_exc()
            }
            # trying to get extra data about potential Response if any

            if response is not None and isinstance(response, Response):
                try:
                    content = response.content
                except (RequestException, RuntimeError) as error:
                    content = error.message
                if content:
                    self.logger and self.logger.error(content)

                # Getting all extra data from Response
                context['response'] = {
                    'links': response.links,
                    'reason': response.reason,
                    'elapsed': response.elapsed,
                    'content': content
                }
            try:
                # Try to dumps nicely for human reading...
                resp['errorMessage'] += json.dumps(context, indent=4)
                # According JSON documentation only those 3 kinds of Exceptions may be raised
            except (ValueError, TypeError, OverflowError):
                # Get builtin representation in the worst case
                resp['errorMessage'] += repr(context)

        return resp

    def send_start_event(self, url, payload, **options):
        """
        Send a Start event.

        :param basestring url: The REST Api URL
        :param payload: The payload of data to be pushed to the REST Api.
        :param dict options: Any additional options for the request (proxies, cert, ...)
            cf. requests documentation

        :return: The Request response object or None

        """
        return self.request("post", url, payload=self._handle_payload_format(payload), **options)

    def send_stop_event(self, url, payload, **options):
        """
        Send a Stop event.

        :param url: The REST Api URL
        :param payload: The payload of data to be pushed to the REST Api.
        :param dict options: Any additional options for the request (proxies, cert, ...)
            cf. requests documentation

        :return: The Request response object or None

        """

        return self.request("put", url, payload=self._handle_payload_format(payload), **options)

    def send_update_event(self, url, payload, **options):
        """
        Send an Update event.

        :param url: The REST Api URL
        :param payload: The payload of data to be pushed to the REST Api.
        :param dict options: Any additional options for the request (proxies, cert, ...)
            cf. requests documentation

        :return: The Request response object or None

        """
        return self.request("put", url, payload=self._handle_payload_format(payload), **options)

    def send_get_request(self, url, **options):
        """
        Send a Get Request

        :param url: The REST Api URL
        :param dict options: Any additional options for the request (proxies, cert, ...)
            cf. requests documentation

        :return: The Request response object or None
        """
        return self.request("get", url, **options)

    def send_resource_event(self, url, resources, payload, **options):
        """
        Send a resource event.

        :param url: The REST Api URL
        :param resources: A list of resources (files, archives, ...)
            to be pushed onto the REST Api.
        :param dict options: Any additional options for the request (proxies, cert, ...)
            cf. requests documentation

        :return: The Request response object or None
        """
        file2push = resources['file'] if "file" in resources else resources

        if isinstance(file2push, basestring):
            # If the file does not exists, warning gently.
            if not os.path.exists(resources):
                error_msg = "Resource {} does not exist!".format(resources)
                self.logger and self.logger.error("Unexpected Error! {}".format(error_msg))
                return {"errorCode": StatusCode.UNEXPECTED_ERROR, "errorMessage": str(error_msg)}
            file2push = file(file2push, 'rb')
        # Checking that the file input is of the good type,
        # if for any reason it does not match, warning gently.
        if not isinstance(file2push, file):
            error_msg = "Resource {} seems to be a corrupted file!".format(resources)
            self.logger and self.logger.error(self.logger, "Unexpected Error! {}".format(error_msg))
            return {"errorCode": StatusCode.UNEXPECTED_ERROR, "errorMessage": str(error_msg)}

        return self.request("post", url, files={'file': file2push}, payload=payload, **options)
