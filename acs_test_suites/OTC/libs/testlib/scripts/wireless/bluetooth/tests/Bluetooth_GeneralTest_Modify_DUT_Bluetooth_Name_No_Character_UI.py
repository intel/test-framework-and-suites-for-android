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
#  @description: Modify the default Bluetooth name of DUT by no character
#  @author:      narasimha.rao.rayala@intel.com
#######################################################################

from testlib.base.base_utils import parse_args
from testlib.scripts.wireless.bluetooth import bluetooth_steps

bluetooth_steps.LogInfo("##### INITIALIZE ######")()

#  ############# Get parameters ############
args = parse_args()

#  Initialize version
DUT_VERSION = bluetooth_steps.GetAndroidVersion(serial=args["serial"], blocking=True)()

try:

    #  ########### Preconditions ###############
    #  #########################################

    bluetooth_steps.LogInfo("######## SETUP ########")()

    bluetooth_steps.StopPackage(serial=args["serial"], blocking=True)()
    bluetooth_steps.PressHome(serial=args["serial"], blocking=True)()

    #  ############ Actual Test ################
    #  #########################################

    bluetooth_steps.LogInfo("##### ACTUAL TEST #####")()

    bluetooth_steps.OpenBluetoothSettings(serial=args["serial"], use_intent=True, version=DUT_VERSION)()
    bluetooth_steps.ClickBluetoothSwitch(serial=args["serial"], state="ON", version=DUT_VERSION)()
    bluetooth_steps.WaitBtScanning(serial=args["serial"], version=DUT_VERSION)()
    bluetooth_steps.BtChangeDeviceName(serial=args["serial"], name="", version=DUT_VERSION)()

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
