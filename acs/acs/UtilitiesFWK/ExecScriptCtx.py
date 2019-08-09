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

from os import path

from acs.UtilitiesFWK.Utilities import Global, AcsConstants, internal_shell_exec
from acs.Device.DeviceManager import DeviceManager
from acs.Core.Equipment.EquipmentManager import EquipmentManager
from acs.Core.PathManager import Paths


def init_ctx(global_dict, logger, global_config):
    # VERDICT GLOBALS
    global_dict["VERDICT"] = Global.FAILURE
    global_dict["OUTPUT"] = ""
    global_dict["FAILURE"] = Global.FAILURE
    global_dict["SUCCESS"] = Global.SUCCESS

    # LOG GLOBALS
    global_dict["PRINT_DEBUG"] = logger.debug
    global_dict["PRINT_INFO"] = logger.info
    global_dict["PRINT_ERROR"] = logger.error
    global_dict["PRINT_WARNING"] = logger.warning

    # DEVICE GLOBALS
    device = DeviceManager().get_device(AcsConstants.DEFAULT_DEVICE_NAME)
    global_dict["DEVICE_MANAGER"] = DeviceManager()
    global_dict["DEVICE"] = device
    global_dict["DEVICE_LOGGER"] = device.get_device_logger()

    # EQUIPMENT GLOBALS
    global_dict["EQUIPMENT_MANAGER"] = EquipmentManager()
    io_card_name = device.config.get("IoCard", "IO_CARD")
    global_dict["IO_CARD"] = EquipmentManager().get_io_card(io_card_name)

    # REPORT GLOBALS
    global_dict["REPORT_PATH"] = device.get_report_tree().get_report_path()
    global_dict["ACS_REPORT_FILE_PATH"] = device.get_report_tree().report_file_path

    # ACS GLOBALS
    global_dict["PATH_MANAGER"] = Paths
    global_dict["LOCAL_EXEC"] = internal_shell_exec
    global_dict["BENCH_CONFIG"] = global_config.benchConfig
    global_dict["EXECUTION_CONFIG_PATH"] = path.abspath(Paths.EXECUTION_CONFIG)
    global_dict["CREDENTIALS"] = global_config.credentials
