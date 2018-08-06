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
#  @description: Bluetooth_GeneralTest_BT_on_off_iteratively.
#  @author:      narasimha.rao.rayala@intel.com
#######################################################################

from testlib.base.base_utils import parse_args
from testlib.scripts.wireless.bluetooth import bluetooth_steps

bluetooth_steps.LogInfo("##### INITIALIZE ######")()

#  ############# Get parameters ############
args = parse_args()
#  ### mandatory parameters ###
serial_dev = args["script_args"]["serial2"]
script_args = args["script_args"]
#  ### optional parameters ###

#  default values
action_dut = "Pair"
action_dev = "Pair"
initiator = "DUT"
action_initiator_first = True
scan_timeout = 60000
scan_max_attempts = 1
timeout_time = 60000
#  possible values for optional parameters
action_values = ["Pair", "onoff"]
initiator_values = ["dut", "dev"]
true_values = ["true", "t", "1", "yes", "y"]
iteration_values = ["1", "2", "3", "4", "5", "6", "7", "8"]
#  parse optional parameters
if "action_dut" in script_args.keys():
    if script_args["action_dut"] in action_values:
        action_dut = script_args["action_dut"]
    else:
        raise Exception("Possible values for action_dut: " + str(action_values))
if "action_dev" in script_args.keys():
    if script_args["action_dev"] in action_values:
        action_dev = script_args["action_dev"]
    else:
        raise Exception("Possible values for action_dev: " + str(action_values))
if "action_initiator" in script_args.keys():
    if script_args["action_initiator"] in action_values:
        action_initiator = script_args["action_initiator"]
    else:
        raise Exception("Possible values for action_initiator: " + str(action_values))
if "initiator" in script_args.keys():
    if script_args["initiator"].lower() in initiator_values:
        initiator = script_args["initiator"]
    else:
        raise Exception("Possible values for initiator: " + str(initiator_values))
if "iteration" in script_args.keys():
    if script_args["iteration"] in iteration_values:
        iteration = script_args["iteration"]
    else:
        raise Exception("Possible values for iteration_values: " + str(iteration_values))

#  Initialize version
DUT_VERSION = bluetooth_steps.GetAndroidVersion(serial=args["serial"], blocking=True)()
DEV_VERSION = bluetooth_steps.GetAndroidVersion(serial=serial_dev, blocking=True)()
DUT_NAME = bluetooth_steps.GetBtMac(serial=args["serial"], blocking=True)()
PAIRING_DEV_NAME = bluetooth_steps.GetBtMac(serial=serial_dev, blocking=True)()
try:

    #  ########### Preconditions ###############
    #  #########################################

    bluetooth_steps.LogInfo("######## SETUP ########")()
    #  DUT: turn on BT
    bluetooth_steps.StopPackage(serial=args["serial"], blocking=True)()
    bluetooth_steps.PressHome(serial=args["serial"], blocking=True)()
    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION, blocking=True)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="ON", version=DUT_VERSION, blocking=True)()
    #  DEV: turn on BT
    bluetooth_steps.StopPackage(serial=serial_dev, blocking=True)()
    bluetooth_steps.PressHome(serial=serial_dev, blocking=True)()
    bluetooth_steps.OpenBluetoothSettings(serial=serial_dev, use_intent=True, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.ClickBluetoothSwitch(serial=serial_dev, state="ON", version=DEV_VERSION, blocking=True)()

    #  DUT: wait scan, rename device and remove all paired devices
    bluetooth_steps.WaitBtScanning(serial=args["serial"], version=DUT_VERSION, blocking=True)()
    bluetooth_steps.BtChangeDeviceName(serial=args["serial"],
                                       name=DUT_NAME, version=DUT_VERSION, blocking=True)()
    bluetooth_steps.BtRemoveAllPairedDevices(serial=args["serial"], version=DUT_VERSION, blocking=True)()
    bluetooth_steps.CheckBtVisibility(serial=args["serial"], version=DUT_VERSION, blocking=True)()

    #  DEV: wait scan (should be already finished), rename device and remove all paired devices
    bluetooth_steps.WaitBtScanning(serial=serial_dev, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.BtChangeDeviceName(serial=serial_dev,
                                       name=PAIRING_DEV_NAME, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.BtRemoveAllPairedDevices(serial=serial_dev, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.CheckBtVisibility(serial=serial_dev, version=DEV_VERSION, blocking=True)()

    #  ############ Actual Test ################
    #  #########################################

    bluetooth_steps.LogInfo("##### ACTUAL TEST #####")()

    counter = 0
    while (counter < int(iteration)):
        if action_initiator == "onoff":
            bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="ON", version=DUT_VERSION)()
            bluetooth_steps.BtSearchDevices(serial=serial_dev, dev_to_find=DUT_NAME, scan_timeout=60000,
                                            version=DEV_VERSION)()
            bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="OFF", version=DUT_VERSION)()
        counter = counter + 1
finally:

    #  ########### Postconditions ##############
    #  #########################################

    bluetooth_steps.LogInfo("####### CLEANUP #######")()

    #  DUT: turn on BT if not already
    bluetooth_steps.StopPackage(serial=args["serial"], critical=False)()
    bluetooth_steps.PressHome(serial=args["serial"], critical=False)()
    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="OFF", version=DUT_VERSION, critical=False)()

    #  DEV: turn off BT if not already
    bluetooth_steps.StopPackage(serial=serial_dev, critical=False)()
    bluetooth_steps.PressHome(serial=serial_dev, critical=False)()
    bluetooth_steps.OpenBluetoothSettings(serial=serial_dev, use_intent=True, version=DEV_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=serial_dev, state="OFF", version=DEV_VERSION, critical=False)()
