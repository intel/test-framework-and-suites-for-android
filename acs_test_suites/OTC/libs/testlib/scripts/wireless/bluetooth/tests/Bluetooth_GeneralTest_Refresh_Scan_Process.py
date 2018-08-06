# !/usr/bin/env python
"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?

SPDX-License-Identifier: Apache-2.0

"""

#######################################################################
#  @description: Bluetooth Refresh Scan process
#  @author:      narasimha.rao.rayala@intel.com
#######################################################################

from testlib.base.base_utils import parse_args
from testlib.scripts.wireless.bluetooth import bluetooth_steps
from uiautomator import Device

bluetooth_steps.LogInfo("##### INITIALIZE ######")()

#  ############# Get parameters ############
args = parse_args()
#  ### mandatory parameters ###
script_args = args["script_args"]
if "serial2" not in script_args.keys():
    raise Exception("serial2 parameter is mandatory")
serial_dev = args["script_args"]["serial2"]
#  Initialize version
DUT_VERSION = bluetooth_steps.GetAndroidVersion(serial=args["serial"], blocking=True)()
DEV_VERSION = bluetooth_steps.GetAndroidVersion(serial=serial_dev, blocking=True)()
PAIRING_DEV_NAME = bluetooth_steps.GetBtMac(serial=serial_dev, blocking=True)()
d = Device(serial=args["serial"])
try:

    #  ########### Preconditions ###############
    #  #########################################

    bluetooth_steps.LogInfo("######## SETUP ########")()

    bluetooth_steps.StopPackage(serial=args["serial"], blocking=True)()
    bluetooth_steps.PressHome(serial=args["serial"], blocking=True)()
    bluetooth_steps.OpenBluetoothSettings(serial=serial_dev, use_intent=True, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.ClickBluetoothSwitch(serial=serial_dev, state="ON", version=DEV_VERSION, blocking=True)()
    bluetooth_steps.BtChangeDeviceName(serial=serial_dev, name=PAIRING_DEV_NAME, blocking=True)()
    #  ############ Actual Test ################
    #  #########################################

    bluetooth_steps.LogInfo("##### ACTUAL TEST #####")()
    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="ON", version=DUT_VERSION)()
    counter = 1
    while counter < 3:
        bluetooth_steps.BtSearchDevices(serial=args["serial"], dev_to_find=PAIRING_DEV_NAME, scan_timeout=60000,
                                        version=DEV_VERSION)()
        counter = counter + 1
finally:

    #  ########### Postconditions ##############
    #  #########################################

    bluetooth_steps.LogInfo("####### CLEANUP #######")()

    bluetooth_steps.StopPackage(serial=args["serial"], critical=False)()
    bluetooth_steps.PressHome(serial=args["serial"], critical=False)()
    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="OFF", version=DUT_VERSION, critical=False)()
    bluetooth_steps.StopPackage(serial=args["serial"], critical=False)()
    bluetooth_steps.PressHome(serial=args["serial"], critical=False)()
