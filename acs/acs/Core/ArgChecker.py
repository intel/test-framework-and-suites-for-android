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

import os
import re

from acs.Core.PathManager import Paths
from acs.UtilitiesFWK.Utilities import Obfuscated


class ArgChecker:

    def __init__(self, **kwargs):

        self._params = {"serial_number": "",
                        "bench_config": "Bench_Config",
                        "flash_file_path": None,
                        "execution_request_nb": 1,
                        "random_mode": False,
                        "user_email": "no.name@example.com",
                        "credentials": "",
                        "metacampaign_uuid": "",
                        "device_parameter_list": None,
                        "log_level": "DEBUG"}

        self._params.update(kwargs)

    def _check_email(self, email):
        """
        Check if given parameter is a valid email

        :type email: str
        :param email: Input email

        :rtype: str
        :return: Email validation status
        """
        error_msg = None
        expr = "^[^@]+@[^@]+\.[^@]+$"

        # Test matching correct email
        matches_str = re.compile(expr).search(str(email))
        if matches_str is None:
            error_msg = "{0} is not a valid email address".format(email)

        return error_msg

    def _get_file_path(self, file_path):
        path_possibilities = [file_path,
                              os.path.join(Paths.EXECUTION_CONFIG, file_path),
                              os.path.join(Paths.EXECUTION_CONFIG, "{0}.xml".format(file_path))]

        for file_path in path_possibilities:
            if os.path.isfile(file_path):
                return file_path

        return None

    def _check_campaign(self, campaign):
        """
        Check if campaign argument is given and at
        right place

        :type campaign: str
        :param campaign: Input campaign

        :rtype: string
        :return: Campaign validation status
        """

        error_msg = None

        # Check mandatory parameters
        if campaign is None:
            error_msg = "{0} campaign file argument is missing".format(campaign)
        else:
            # Check files path
            campaign_path = self._get_file_path(campaign)
            if not campaign_path:
                error_msg = "{0} campaign file cannot be find in {1} execution folder".format(campaign,
                                                                                              Paths.EXECUTION_CONFIG)
        return error_msg

    def _check_benchConfig(self, benchConfig):
        """
        Check if benchConfig argument is given and at
        right place

        :type benchConfig: str
        :param benchConfig: Input benchConfig

        :rtype: string
        :return: BenchConfig validation status
        """

        error_msg = None

        # Check files path
        benchConfig_path = self._get_file_path(benchConfig)
        if not benchConfig_path:
            error_msg = "{0} benchConfig file cannot be find in {1} execution folder".format(benchConfig,
                                                                                             Paths.EXECUTION_CONFIG)
        return error_msg

    def _check_flashfile(self, flashFile):
        """
        Check if flashFile argument is valid

        :type flashFile: str
        :param flashFile: Input flashFile

        :rtype: string
        :return: flashFile validation status
        """

        error_msg = []
        global_error_msg = None

        if flashFile is not None:
            for flash_file in flashFile.split(";"):
                flash_file = os.path.abspath(flash_file)
                if not os.path.isfile(flash_file):
                    error_msg.append("{0}".format(flash_file))

            if error_msg:
                error_msg.append("flash file(s) do(es) not exist")
                global_error_msg = ", ".join(error_msg)

        return global_error_msg

    def _check_credentials(self, credentials):
        """
        Check if credentials argument is valid

        :type credentials: str
        :param credentials: Input credentials

        :rtype: string
        :return: credentials validation status
        """

        error_msg = None

        # Check credentials format
        if credentials is not None:
            if not isinstance(credentials, Obfuscated):
                credentials = Obfuscated(str(credentials))

            check_credentials = credentials.split(":", 1)
            if len(check_credentials) != 2:
                error_msg = "Bad authentication format ! It should be formatted as follow: {userid}:{pwd}"

            # Check credentials format (userid and password present)
            elif [x for x in check_credentials if not x]:
                error_msg = "Bad authentication format ! userid or pwd could not be null"

        return error_msg

    def check_args(self, is_credential_checked=True):
        """
        Check all given arguments

        :type is_credential_checked: bool
        :param is_credential_checked: whether creds are checked, knowing that they are when ACS called from test runner.

        :rtype: string
        :return: arguments validation status
        """

        error_msg = None

        campaign_name = self._params["campaign_name"]
        flash_file_path = self._params["flash_file_path"]
        user_email = self._params["user_email"]
        bench_config = self._params["bench_config"]
        credentials = self._params["credentials"]

        error_msg = self._check_campaign(campaign_name)
        if error_msg:
            return error_msg

        error_msg = self._check_benchConfig(bench_config)
        if error_msg:
            return error_msg

        error_msg = self._check_flashfile(flash_file_path)
        if error_msg:
            return error_msg

        error_msg = self._check_email(user_email)
        if error_msg:
            return error_msg

        if is_credential_checked:
            error_msg = self._check_credentials(credentials)
            if error_msg:
                return error_msg

    @property
    def args(self):
        """
        Return list of arguments

        :rtype: dict
        :return: dictionary of all arguments with default values
        """
        return self._params
