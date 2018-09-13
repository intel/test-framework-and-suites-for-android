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
:summary: Entry point of ACS Host Part
:author: sfusilie

"""
# pylama:ignore=E501
from optparse import OptionParser, OptionGroup
import os
import sys

# fix pkg import error in source code folder
pkg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from CampaignEngine import CampaignEngine  # noqa
from acs.Core.PathManager import Paths  # noqa
from acs.Device.DeviceConfig.DeviceConfigLoader import DeviceConfigLoader  # noqa
from acs.Core.CampaignGenerator.FailedTestCampaignGenerator import FailedTestCampaignGenerator  # noqa
from acs.Core.ArgChecker import ArgChecker  # noqa
import acs.UtilitiesFWK.Utilities as Util  # noqa


def check_python_version():
    """
    :return:
    """
    version_info = sys.version_info

    needed_release = [2]
    needed_version = [6, 7]
    if ((version_info[0] not in needed_release) or
            (version_info[1] not in needed_version)):
        print >> sys.stderr, "ACS Error:"
        print >> sys.stderr, "- Cannot find a suitable python interpreter"
        print >> sys.stderr, "- At least Python %d.%d is required!" % (needed_release[0], needed_version[0])
        print >> sys.stderr, "- please check your python environment!"
        sys.exit(1)


def display_acs_version(option, opt_str, value, parser):
    """
    :param option:
    :param opt_str:
    :param value:
    :param parser:
    :return:
    """
    print "ACS " + Util.get_acs_release_version()
    sys.exit(0)


def extract_failed_tests(option, opt_str, value, parser):
    """
    :param option:
    :param opt_str:
    :param value:
    :param parser:
    :return:
    """
    rargs = parser.rargs
    failed_folder_path = " ".join(rargs)
    if len(rargs) > 1 or not rargs:
        parser.error("'%s' is not a valid PATH" % failed_folder_path)
        sys.exit(0)
    if not os.path.isdir(failed_folder_path):
        failed_folder_path = os.path.join(Paths.REPORTS, failed_folder_path)
        if not os.path.isdir(failed_folder_path):
            parser.error("'%s' is not a valid PATH" % failed_folder_path)
            sys.exit(0)
    campaign_generator = FailedTestCampaignGenerator(failed_folder_path)
    (verdict, verdict_msg) = campaign_generator.create_test_campaign()
    if verdict != Util.Global.SUCCESS:
        parser.error(verdict_msg)
        sys.exit(-1)
    sys.exit(0)


def display_device_models(option, opt_str, value, parser):
    """
    :param option:
    :param opt_str:
    :param value:
    :param parser:
    :return:
    """
    devices = DeviceConfigLoader.retrieve_device_model_list()
    for device_model in devices:
        print device_model
    sys.exit(0)


def setup_arg_parser():
    """
    :return:
    """
    usage = "usage: %prog -h"
    parser = OptionParser(usage=usage)

    mandatory_group = OptionGroup(parser, "MANDATORIES")

    mandatory_group.add_option("-c", "--campaign", "--cp",
                               help="Campaign file to execute.",
                               metavar="TEST_CAMPAIGN",
                               dest="campaign_name")

    parser.add_option_group(mandatory_group)

    optional_group = OptionGroup(parser, "OPTIONS")

    optional_group.add_option("-d", "--device_model", "--dm",
                              help="Device model under test. "
                                   "To use ACS in multiple devices mode, "
                                   "either set this option as 'multi' or ignore it (-d option) "
                                   "and in both cases define your devices in the Bench Config file.",
                              metavar="DEVICE_MODEL",
                              type="choice", choices=DeviceConfigLoader.retrieve_device_model_list(),
                              dest="device_name")

    optional_group.add_option("-f", "--flash_file", "--ff",
                              help="Flash file full path (.json, .zip or flash.xml)."
                                   "This path will be used by flash use case as default value.",
                              metavar="FLASH_FILE",
                              default=None,
                              dest="flash_file_path")

    optional_group.add_option("-b", "--bench_config", "--bc",
                              help="Bench Config file to use. [default: %default].",
                              metavar="BENCH_CONFIG",
                              default="Bench_Config",
                              dest="bench_config")

    optional_group.add_option("-n", "--run_nb", "--nb",
                              help="Campaign execution iteration number if more than one run is required.",
                              metavar="NUMBER",
                              type="int", default=1,
                              dest="execution_request_nb")

    optional_group.add_option("-r", "--random_mode",
                              help="Enable random mode if your campaign is configured to run random TC.",
                              action="store_true", default=False,
                              dest="random_mode")

    optional_group.add_option("-s", "--device_id", "--sr",
                              help="Serial number of the DUT (used to identify it when communicating with it)",
                              metavar="SERIAL_NUMBER",
                              default="",
                              dest="serial_number")

    optional_group.add_option("--rf", "--report_folder",
                              help="Folder where ACS report will be created",
                              metavar="REPORT_FOLDER",
                              default=None,
                              dest="report_folder")

    optional_group.add_option("-o", "--override_device_parameter", "--op",
                              help="Override device parameters defined in both Bench_Config and Device_Catalog. "
                                   "The user can modify several parameters at the same time, as follow :"
                                   " -o monkeyPort=\"80\" -o bootTimeout=\"10\" -o serialNumber=\"Medfield12345678\"",
                              action="append", default=[],
                              type="string",
                              metavar="DEVICE_PARAMETER=DEVICE_VALUE",
                              dest="device_parameter_list")

    optional_group.add_option("--cr", "--creds",
                              help="Credentials in \"user:password\" format",
                              metavar="CREDENTIALS",
                              default=None,
                              dest="credentials")

    optional_group.add_option("--camp_gen",
                              help="Specify another campaign generator to be used.",
                              type="string",
                              dest="camp_gen")

    optional_group.add_option("--live_reporting",
                              help="Specify a live reporting plugin to be used.",
                              type="string",
                              dest="live_reporting_plugin")

    parser.add_option_group(optional_group)
    reporting_group = OptionGroup(parser, "REPORTING OPTIONS")

    reporting_group.add_option("-u", "--user",
                               help="Valid user email.",
                               metavar="EMAIL",
                               default="no.name@example.com",
                               dest="user_email")

    reporting_group.add_option("--metacampaign_uuid", "--uuid",
                               metavar="METACAMPAIGN_UUID",
                               default="",
                               dest="metacampaign_uuid")

    reporting_group.add_option("--log_level", "--ll",
                               help="change the log level for the stdout after ACS is initialised. "
                               "Available log levels are (from higher filtering to lower): CRITICAL, ERROR, "
                               "WARNING, MINIMAL, INFO and DEBUG",
                               metavar="LOG_LEVEL", default="",
                               dest="log_level")

    parser.add_option_group(reporting_group)

    misc_group = OptionGroup(parser, "MISCS")

    misc_group.add_option("--device_models",
                          help="List the supported device models.",
                          action="callback", callback=display_device_models)

    misc_group.add_option("--eft", "--extract_failed_tests",
                          help="Auto generates a campaign with only failed tests from input results folder.",
                          metavar="CAMPAIGN_REPORT_FOLDER",
                          action="callback",
                          callback=extract_failed_tests,
                          dest="extract_failed")

    misc_group.add_option("-v", "--version",
                          help="Print the current ACS Version.",
                          action="callback", callback=display_acs_version)

    parser.add_option_group(misc_group)

    return parser


def main():
    ''' main '''
    # Check python version
    check_python_version()

    try:
        # Init arg parser
        arg_parser = setup_arg_parser()

        # Parse cmd line
        (options, args) = arg_parser.parse_args()

        # Checking all args
        arg_checker = ArgChecker(**vars(options))
        error_msg = arg_checker.check_args()

        if error_msg:
            arg_parser.error(error_msg)

        engine = CampaignEngine(report_folder=options.report_folder)
        results = engine.execute(False, **vars(options))

        msg = Util.ExitCode.getExitCodeMsg(results.verdict)
        if msg is not None:
            print "ACS OUTCOME: %s" % (msg,)
        else:
            print "ACS OUTCOME: UNKNOWN EXIT CODE : %s" % (results.verdict,)

        sys.exit(results.verdict)

    except KeyboardInterrupt:
        exit("Killed by user")


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
