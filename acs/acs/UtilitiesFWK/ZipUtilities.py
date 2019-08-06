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

# pylint: disable=W0621, invalid-name, missing-docstring, old-style-class

import os
import zipfile

from acs.UtilitiesFWK.Utilities import Global
from acs.Core.Report.ACSLogging import LOGGER_FWK as LOGGER


def add_folder(zip_file, folder):
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.abspath(os.path.join(root, f))
            path_inside_zip = os.path.relpath(full_path, os.path.abspath(folder))
            LOGGER.info('File added: {0} as {1}'.format(full_path, path_inside_zip))
            zip_file.write(full_path, path_inside_zip)


def zip_folder(folder, filename):
    try:
        filename = filename + '.zip'
        try:
            zip_file = zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True)
        except RuntimeError:  # if ZIP_DEFLATED not support, fallback to default
            zip_file = zipfile.ZipFile(filename, 'w', allowZip64=True)
        LOGGER.info('Create zip file: {0}'.format(filename))
        add_folder(zip_file, folder)
        LOGGER.info("folder {0} has been properly zipped as {1}".format(folder, filename))
        zip_file.close()
        status = Global.SUCCESS
        out_file = os.path.abspath(filename)
    except IOError as error:
        LOGGER.error('Cannot create zip file: {0} - {1}'.format(filename, error))
        status = Global.FAILURE
        out_file = ""

    if status == Global.SUCCESS:
        LOGGER.info("ZIP FILE: {0}".format(out_file))
    return status, out_file
