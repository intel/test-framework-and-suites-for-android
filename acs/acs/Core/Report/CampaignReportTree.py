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
:summary: Entry point for Campaign report folder.
        This class will give access to
        the folder created in _Reports for the current campaign session.
:since: 14/10/2011
:author: ssavrimoutou
"""

import os

from ACSLogging import LOGGER_FWK
from acs.Core.PathManager import Folders
import acs.UtilitiesFWK.Utilities as Util


class CampaignReportTree(object):

    """
    CampaignReportTree class gives the access to folder created in _Reports for the current campaign
    """

    def __init__(self, campaign_name=None, report_path=None):
        """
        Constructor of CampaignReportTree
        """
        # Report file name
        self.__report_file_path = None

        # Retrieve logger instance
        self._logger = LOGGER_FWK

        self._report_path = report_path
        self._campaign_name = campaign_name
        self._hw_variant_name = None

        self.__campaign_report_path = None

    def create_report_folder(self):
        """
        Create report folder path from either a path specified by report_path
        or by creating one by computing timestamp, campaign and hw variant name.
        """
        if not self.__campaign_report_path:
            # Initialize the report path

            # Create the report folder for the current campaign
            if self._report_path is None:
                # No path specified (from ACS cmd line)
                # We are going to generate one report folder name
                # Adding timestamp
                campaign_folder_name = Util.get_timestamp()

                if self._hw_variant_name:
                    # Adding hw variant
                    campaign_folder_name += "_" + self._hw_variant_name

                if self._campaign_name:
                    # Adding current campaign name
                    campaign_name = os.path.splitext(os.path.basename(self._campaign_name))[0]
                    campaign_folder_name += "_" + campaign_name

                campaign_report_path = os.path.join(os.getcwd(), Folders.REPORTS, campaign_folder_name)
            else:
                # Path specified (from ACS cmd line
                # Use it!
                campaign_report_path = self._report_path

            index = 1
            campaign_report_path_orig = campaign_report_path
            while os.path.exists(campaign_report_path):
                # Increment the folder name until it does not exists
                campaign_report_path = campaign_report_path_orig + "_" + str(index)
                index += 1
            os.makedirs(campaign_report_path)
            self._logger.info("Campaign report path is %s" % campaign_report_path)
            # Store the path of the folder
            self.__campaign_report_path = campaign_report_path

    def set_hw_variant_name(self, value):
        """
        Set hardware variant name that will be use to generate report folder name
        """
        self._hw_variant_name = value

    @property
    def report_file_path(self):
        return self.__report_file_path

    @report_file_path.setter
    def report_file_path(self, value):
        self.__report_file_path = value

    def get_report_path(self, device_name=None):
        """
        Returns the path to the folder of the current campaign

        :rtype: String
        :return: Path to the campaign report folder.
        """
        report_path = self.__campaign_report_path
        if device_name:
            report_path = os.path.join(report_path, device_name)
            # To avoid unnecessary exception.
            # We create the folder if it not exists
            if not os.path.exists(report_path):
                os.makedirs(report_path)
        return report_path

    def get_subfolder_path(self, subfolder_name, device_name=None):
        """
        Returns the path to the subfolder in the current campaign folder
        If the subfolder does not exist we create it

        :type: String
        :param: Subfolder name

        :rtype: String
        :return: The path to the subfolder
        """

        subfolder_path = os.path.join(self.get_report_path(device_name),
                                      subfolder_name)

        # To avoid unnecessary exception.
        # We create the folder if it not exists
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        return subfolder_path

    def create_subfolder(self, subfolder_name):
        """
        Create the given subfolder in the campaign report folder

        :type: String
        :param: Subfolder name

        :rtype: String
        :return: The path of the created subfolder
        """

        subfolder_path = os.path.join(self.get_report_path(),
                                      subfolder_name)

        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)
        else:
            self._logger.info(
                "Subfolder %s already exists in %s" %
                (subfolder_name, self.get_report_path()))

        return subfolder_path
