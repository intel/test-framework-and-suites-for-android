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
