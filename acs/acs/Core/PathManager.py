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
:summary: Implements classes managing paths in ACS
:since: 09/04/2014
:author: cbresoli
"""

import os

# Aliases
path = os.path


def find(*paths, **options):
    """
    Return the first existing path found from the provided list

    :param paths: A list of potential existing paths
    :type paths: list

    :param options: Any extra options taken by the function
    :type options: dict

    .. note:: For now you can pass your custom Exception as `error_handler` parameter.

        This Exception is raised only if not existing path is found!

    :return: The first existing found path or empty string ""
    :rtype: str

    """
    for p in paths:
        if path.exists(p):
            found = p
            break
    else:
        error_handler = options.get('error_handler')
        if error_handler and issubclass(error_handler, Exception):
            raise error_handler("No existing path found for {0}".format(paths))
        found = ""
    return found


def absjoin(*args):
    """
    Custom join + abspath (abspath does a normpath too)

    :param args: Non Keyword arguments to be joined together
    :type args: tuple, list

    :return: An absolute & normed joined path
    :rtype: str

    """
    return path.abspath(path.join(*args))


__SELF_DIR = path.dirname(__file__)
ACS_REPO_BASEDIR = absjoin(__SELF_DIR, '..', '..', '..')
ACS_SRC_DIR = absjoin(__SELF_DIR, '..')


class Folders(object):

    """
    This class contains all default folders name of ACS source
    It should be used every where we need to use an ACS folder
    """

    CATALOGS = "_Catalogs"
    CONFIGS = "_Configs"
    EMBEDDED = "_Embedded"
    EXECUTION_CONFIG = os.environ.get("ACS_EXECUTION_CONFIG_PATH", "_ExecutionConfig")
    REPORTS = os.environ.get("ACS_REPORTS_PATH", "_Reports")
    TEMPLATES = "_Templates"
    TOOLS = "_Tools"
    IMAGES = "_ReferenceImages"

    CORE = "Core"
    GUI_TEXT = "GuiText"

    TEST_SCRIPTS = "acs_test_scripts"
    TEST_SUITES = "acs_test_suites"

    ACS_CACHE = absjoin(path.expanduser('~'), '.acs')

    DEVICE_CATALOG = "Device"
    DEVICE_MODELS = "Models"
    DEVICE_CAPABILITIES = "Capabilities"
    USECASE_CATALOG = "UseCase"
    TESTSTEP_CATALOG = "TestStep"
    PARAMETER_CATALOG = "Parameter"
    EQUIPMENT_CATALOG = "Equipment"
    EXTRA_LIB_FOLDER = "ExtraLibs"

    ROOT_DUT_NAME = "PHONE"

    AP_LOGS = "AP_LOGS"
    BP_LOGS = "MODEM_LOGS"
    SERIAL_LOGS = "SERIAL"
    PTI_LOGS = "PTI"
    LOGCAT_LOGS = "LOGCAT"
    DEBUG_LOGS = "DEBUG_LOGS"


class Paths(object):

    """
    This class contains all default paths used by ACS source
    It should be used every where we need to use an ACS path
    """

    CATALOGS = absjoin(ACS_SRC_DIR, Folders.CATALOGS)
    EMBEDDED = absjoin(ACS_SRC_DIR, Folders.EMBEDDED)
    EXECUTION_CONFIG = absjoin(ACS_SRC_DIR, Folders.EXECUTION_CONFIG)
    EXTRA_LIB_FOLDER = absjoin(EXECUTION_CONFIG, Folders.EXTRA_LIB_FOLDER)
    REPORTS = absjoin(ACS_SRC_DIR, Folders.REPORTS)
    TEMPLATES = absjoin(ACS_SRC_DIR, Folders.TEMPLATES)
    TOOLS = absjoin(ACS_SRC_DIR, Folders.TOOLS)
    IMAGE = absjoin(ACS_SRC_DIR, Folders.IMAGES)

    GUI_TEXT = absjoin(ACS_SRC_DIR, Folders.CORE, Folders.GUI_TEXT)

    TEST_SCRIPTS = absjoin(ACS_REPO_BASEDIR, Folders.TEST_SCRIPTS)

    TEST_SUITES = find(
        # Development mode (repo)
        absjoin(ACS_REPO_BASEDIR, Folders.TEST_SUITES),
        # Production mode (Buildbot)
        EXECUTION_CONFIG
    )

    CONFIGS = absjoin(TEST_SUITES, Folders.CONFIGS)

    CACHE_PUSH_REPORTS = absjoin(Folders.ACS_CACHE, 'UncompleteReportPush')

    FWK_USECASE_CATALOG = absjoin(CATALOGS, Folders.USECASE_CATALOG)
    TEST_SCRIPTS_USECASE_CATALOG = absjoin(TEST_SCRIPTS, Folders.CATALOGS, Folders.USECASE_CATALOG)

    FWK_DEVICE_CATALOG = absjoin(CATALOGS, Folders.DEVICE_CATALOG)
    FWK_DEVICE_CAPABILITIES_CATALOG = absjoin(FWK_DEVICE_CATALOG, Folders.DEVICE_CAPABILITIES)
    FWK_DEVICE_MODELS_CATALOG = absjoin(FWK_DEVICE_CATALOG, Folders.DEVICE_MODELS)

    DEVICE_CATALOG = absjoin(TEST_SUITES, Folders.CATALOGS, Folders.DEVICE_CATALOG)
    DEVICE_MODELS_CATALOG = absjoin(DEVICE_CATALOG, Folders.DEVICE_MODELS)
    FWK_TESTSTEP_CATALOG = absjoin(CATALOGS, Folders.TESTSTEP_CATALOG)
    TEST_SCRIPTS_TESTSTEP_CATALOG = absjoin(TEST_SCRIPTS, Folders.CATALOGS, Folders.TESTSTEP_CATALOG)

    FWK_PARAMETER_CATALOG = absjoin(CATALOGS, Folders.PARAMETER_CATALOG)
    PARAMETER_CATALOG = absjoin(TEST_SCRIPTS, Folders.CATALOGS, Folders.PARAMETER_CATALOG)

    EQUIPMENT_CATALOG = absjoin(TEST_SCRIPTS, Folders.CATALOGS, Folders.EQUIPMENT_CATALOG)

    FLASH_FILES = None


class Files(object):

    @property
    def acs_output_name(self):
        if self._acs_output_name:
            value = self._acs_output_name
        else:
            value = "acs_output"
        return value

    @acs_output_name.setter
    def acs_output_name(self, value):
        self._acs_output_name = value

    TCR_LIVE_REPORTING = "TCR_live_reporting.log"

    REPORT_STYLE = "report.xsl"


if __name__ == '__main__':
    print(Paths.TEST_SUITES)
