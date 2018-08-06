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
#  @description: Pair request initiated by DUT , devices will Pair and
#                than UNPair
#  @author:      narasimha.rao.rayala@intel.com
#######################################################################

from testlib.base.base_utils import parse_args
from testlib.scripts.wireless.bluetooth import bluetooth_steps, bt_utils

bluetooth_steps.LogInfo("##### INITIALIZE ######")()

#  ############# Get parameters ############
args = parse_args()
script_args = args["script_args"]
#  mandatory param
if "serial2" not in script_args.keys():
    raise Exception("serial2 parameter is mandatory")
serial_dev = args["script_args"]["serial2"]
#  ### optional parameters ###

#  default values
action_dut = "Pair"
action_dev = "Pair"
initiator = "DUT"
action_initiator_first = True
scan_timeout = 60000
scan_max_attempts = 1
timeout_time = 60000


#  Initialize versions and names
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
    bluetooth_steps.WaitBtScanning(serial=serial_dev, timeout_appear=0, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.BtChangeDeviceName(serial=serial_dev,
                                       name=PAIRING_DEV_NAME, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.BtRemoveAllPairedDevices(serial=serial_dev, version=DEV_VERSION, blocking=True)()
    bluetooth_steps.CheckBtVisibility(serial=serial_dev, version=DEV_VERSION, blocking=True)()

    #  pair devices
    bt_utils.bt_pair_devices(serial=args["serial"],
                             dev=serial_dev,
                             dut_name=DUT_NAME,
                             dev_name=PAIRING_DEV_NAME,
                             action_dut=action_dut,
                             action_dev=action_dev,
                             perform_action_first_on_initiator=action_initiator_first,
                             pair_request_initiator=initiator,
                             scan_timeout=scan_timeout,
                             scan_max_attempts=scan_max_attempts,
                             time_to_wait_timeout_action=timeout_time,
                             version_dut=DUT_VERSION, version_dev=DEV_VERSION)

    #  ############ Actual Test ################
    #  #########################################

    bluetooth_steps.LogInfo("##### ACTUAL TEST #####")()

    bluetooth_steps.UnpairDevice(serial=args["serial"], device_name=PAIRING_DEV_NAME, version=DUT_VERSION)()
    bluetooth_steps.UnpairDevice(serial=serial_dev, device_name=DUT_NAME, version=DEV_VERSION)()

finally:

    #  ########### Postconditions ##############
    #  #########################################

    bluetooth_steps.LogInfo("####### CLEANUP #######")()

    #  DUT: turn on BT if not already
    bluetooth_steps.StopPackage(serial=args["serial"], critical=False)()
    bluetooth_steps.PressHome(serial=args["serial"], critical=False)()
    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="ON", version=DUT_VERSION, critical=False)()

    #  DEV: turn on BT if not already
    bluetooth_steps.StopPackage(serial=serial_dev, critical=False)()
    bluetooth_steps.PressHome(serial=serial_dev, critical=False)()
    bluetooth_steps.OpenBluetoothSettings(serial=serial_dev, use_intent=True, version=DEV_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=serial_dev, state="ON", version=DEV_VERSION, critical=False)()

    #  DUT: remove all paired devices and turn off BT
    bluetooth_steps.WaitBtScanning(serial=args["serial"], version=DUT_VERSION, critical=False)()
    bluetooth_steps.BtRemoveAllPairedDevices(serial=args["serial"], version=DUT_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="OFF", version=DUT_VERSION, critical=False)()
    bluetooth_steps.StopPackage(serial=args["serial"], critical=False)()
    bluetooth_steps.PressHome(serial=args["serial"], critical=False)()

    #  DEV: remove all paired devices and turn off BT
    bluetooth_steps.WaitBtScanning(serial=serial_dev, timeout_appear=0, version=DEV_VERSION, critical=False)()
    bluetooth_steps.BtRemoveAllPairedDevices(serial=serial_dev, version=DEV_VERSION, critical=False)()
    bluetooth_steps.ClickBluetoothSwitch(serial=serial_dev, state="OFF", version=DEV_VERSION, critical=False)()
    bluetooth_steps.StopPackage(serial=serial_dev, critical=False)()
    bluetooth_steps.PressHome(serial=serial_dev, critical=False)()
