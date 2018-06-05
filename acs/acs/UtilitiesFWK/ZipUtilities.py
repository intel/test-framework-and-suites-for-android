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
:summary: Zip the source folder, get md5sum and push it to remote server
:author: jreynaud

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
