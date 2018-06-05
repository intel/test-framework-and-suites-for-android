__copyright__ = """ (c)Copyright 2013, Intel Corporation All Rights Reserved.
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
"""

__organization__ = "INTEL MCG PSI"
__author__ = "sis-cta-team@intel.com"

import fnmatch
import os


class FileUtilities():

    """
    This class is used to make file operations
    """

    def __init__(self):
        pass

    @staticmethod
    def find_file(root_dir, filename):
        """
        Get the location of a file from a root directory

        :param root_dir: where to start the search
        :type  root_dir: str.

        :param filename: file to locate
        :type  filename: str.

        :return: The full path to the filename/dirname we are looking for
        :rtype: str

        """
        result = []
        for root, _, filenames in os.walk(root_dir):
            for file_name in fnmatch.filter(filenames, filename):
                result.append(os.path.join(root, file_name))

        return result
