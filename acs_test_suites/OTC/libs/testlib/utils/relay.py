#!/usr/bin/env python
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

import serial
import time
from testlib.utils.serial_to_usb import UsbKm232
from testlib.utils.connections.local import Local

RELAY_STATES = {}
RELAY_STATES["RLY08B"] = {"ON": "10", "OFF": "11"}
RELAY_STATES["URMC32"] = {"ON": "on", "OFF": "off"}
RELAY_STATES["USB_RLY08"] = {"ON": "10", "OFF": "11"}

WAIT_ON_OFF = {
    "PRESS": 0.2,
    "ON": 2,
    "OFF": 10,
    "FASTBOOT": 15,
    "DNX": 15
}
WAIT_ACTION = {
    "PRESS": 2,
    "ON": 10,
    "OFF": 30,
    "FASTBOOT": 10,
    "DNX": 10
}


class Relay(serial.Serial):

    relay_port = None
    relay_type = None

    def __init__(self, port=None, baudRate=9600, byteSize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE, stopBits=serial.STOPBITS_ONE, timeout=0,
                 xonxoff=False, rtscts=False, writeTimeout=10, dsrdtr=False,
                 interCharTimeout=None, relayType='RLY08B'):

        if "Numato_Lab_32_Channel" in port:
            relayType = 'URMC32'
        if relayType == 'URMC32':
            baudRate = 19200
        if (relayType != 'RLY08B') * (relayType != 'URMC32'):
            relayType = 'USB_RLY08'

        super(Relay, self).__init__(port, baudRate, byteSize, parity, stopBits,
                                    timeout, xonxoff, rtscts, writeTimeout, dsrdtr, interCharTimeout)
        self.relay_type = relayType

    def __write(self, command):
        super(Relay, self).write(command)
        self.flushInput()
        self.flushOutput()

    def on(self, relay_port):
        if self.relay_type == "URMC32":
            relay_port = str(relay_port) if int(relay_port) < 10 \
                else chr(55 + int(relay_port))
            command = "relay " + str(RELAY_STATES[self.relay_type]["ON"]) + \
                " " + relay_port + "\n\r"
        else:
            command = str(unichr(int(str(RELAY_STATES[self.relay_type]["ON"]) +
                                     str(relay_port))))
        self.__write(command)

    def off(self, relay_port):
        if self.relay_type == "URMC32":
            relay_port = str(relay_port) if int(relay_port) < 10 \
                else chr(55 + int(relay_port))
            command = "relay " + str(RELAY_STATES[self.relay_type]["OFF"]) + \
                " " + relay_port + "\n\r"
        else:
            command = str(unichr(int(str(RELAY_STATES[self.relay_type]["OFF"]) +
                                     str(relay_port))))
        self.__write(command)

    def on_off(self, timeout, relay_port):
        self.on(relay_port)
        time.sleep(timeout)
        self.off(relay_port)


class Kb_Relay(serial.Serial):

    relay_port = None

    def __init__(self, port=None, baudRate=9600, byteSize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE, stopBits=serial.STOPBITS_ONE, timeout=0,
                 xonxoff=False, rtscts=False, writeTimeout=10, dsrdtr=False,
                 interCharTimeout=None):

        super(Kb_Relay, self).__init__(port, baudRate, byteSize, parity, stopBits,
                                       timeout, xonxoff, rtscts, writeTimeout, dsrdtr, interCharTimeout)

    def write(self, command):
        super(Kb_Relay, self).write(command)
        self.flushInput()
        self.flushOutput()
# from testlib.utils.relay import Relayed_device
# rl = Relayed_device(relay_port = "/dev/ttyACM0", power_port = '0',
#                     v_up_port = '1', v_down_port = '2', kb_relay_port = "/dv/ttyUSB0")


class Relayed_device(object):

    def __init__(self,
                 relay_type="RLY08B",
                 relay_port=None,
                 power_port=None,
                 v_up_port=None,
                 v_down_port=None,
                 USB_VC_cut_port=None,
                 kb_relay_port=None,
                 kb_port=None,
                 always_allow_port=None,
                 allow_ok_port=None):
        if relay_port:
            self.relay = Relay(port=relay_port, relayType=relay_type)
            self.power_port = power_port
            self.v_up_port = v_up_port
            self.v_down_port = v_down_port
            self.USB_VC_cut_port = USB_VC_cut_port
            self.always_allow_port = always_allow_port
            self.allow_ok_port = allow_ok_port
        else:
            self.relay = None
        if kb_relay_port:
            self.kb_relay = Kb_Relay(port=kb_relay_port)
            self.kb_port = kb_port
            self.kb = UsbKm232(km232_serial_device=kb_port)
        elif kb_port:
            self.kb_port = kb_port
            self.kb = UsbKm232(km232_serial_device=kb_port)
        else:
            self.kb_relay = None
        self.local_connection = Local()

    def get_intel_usb_entries(self):
        return len(self.local_connection.parse_cmd_output(cmd="lsusb",
                                                          grep_for="8087").split("\n"))

    def press_power(self):
        self.relay.on_off(WAIT_ON_OFF["PRESS"], self.power_port)
        time.sleep(WAIT_ACTION["PRESS"])

    def long_press_power(self):
        self.relay.on_off(WAIT_ON_OFF["ON"], self.power_port)
        time.sleep(WAIT_ACTION["PRESS"])

    def long_press_power_shutdown(self, long_press_time=15):
        self.relay.on_off(long_press_time, self.power_port)
        time.sleep(WAIT_ACTION["PRESS"])

    def press_volume_up(self):
        self.relay.on_off(WAIT_ON_OFF["PRESS"], self.v_up_port)
        time.sleep(WAIT_ACTION["PRESS"])

    def press_volume_down(self):
        self.relay.on_off(WAIT_ON_OFF["PRESS"], self.v_down_port)
        time.sleep(WAIT_ACTION["PRESS"])

    def cut_usb_vc(self):
        self.relay.on(self.USB_VC_cut_port)

    def uncut_usb_vc(self):
        self.relay.off(self.USB_VC_cut_port)

    def power_on(self):
        self.relay.on_off(WAIT_ON_OFF["ON"], self.power_port)
        time.sleep(WAIT_ACTION["ON"])

    def power_off(self):
        self.relay.on_off(WAIT_ON_OFF["OFF"], self.power_port)
        time.sleep(WAIT_ACTION["OFF"])

    def relay_reboot(self):
        self.power_on()
        self.power_off()
        self.power_on()

    def enter_fastboot(self):
        self.relay.on(self.v_down_port)
        time.sleep(0.2)
        self.relay.on(self.power_port)
        time.sleep(WAIT_ON_OFF["ON"])
        self.relay.off(self.power_port)
        time.sleep(WAIT_ON_OFF["FASTBOOT"])
        self.relay.off(self.v_down_port)
        time.sleep(WAIT_ACTION["FASTBOOT"])

    def enter_dnx(self):
        self.relay.on(self.v_down_port)
        time.sleep(0.2)
        self.relay.on(self.v_up_port)
        time.sleep(0.2)
        self.relay.on(self.power_port)
        time.sleep(WAIT_ON_OFF["DNX"])
        self.relay.off(self.power_port)
        time.sleep(0.2)
        self.relay.off(self.v_up_port)
        time.sleep(0.2)
        self.relay.off(self.v_down_port)
        time.sleep(WAIT_ACTION["DNX"])

    def activate_kb(self, port):
        self.kb = UsbKm232(km232_serial_device=self.kb_port)
        usbs = self.get_intel_usb_entries()
        self.kb_relay.write(str(port))
        time.sleep(2)
        return self.get_intel_usb_entries() == usbs - 1

    def deactivate_kb(self):
        usbs = self.get_intel_usb_entries()
        self.kb_relay.write("-1")
        time.sleep(2)
        return self.get_intel_usb_entries() == usbs + 1

    def try_activate_kb(self, port, iterations=3):
        while iterations > 0:
            if self.activate_kb(port):
                return True
            self.deactivate_kb()
            iterations -= 1
            time.sleep(1)
        else:
            print "Could not activate KB!!!"
            return False

    def try_deactivate_kb(self, iterations=3):
        while iterations > 0:
            if self.deactivate_kb():
                return True
            iterations -= 1
            time.sleep(1)
        else:
            print "Could not deactivate KB!!!"
            return False

    def send_to_kb(self, sequence):
        self.kb = UsbKm232(km232_serial_device=self.kb_port)
        self.kb.generate_command_from_input(sequence)

    def allow_usb_debugging(self):
        self.relay.on_off(WAIT_ON_OFF["PRESS"], self.always_allow_port)
        time.sleep(WAIT_ACTION["ON"])
        self.relay.on_off(WAIT_ON_OFF["PRESS"], self.allow_ok_port)
        time.sleep(WAIT_ACTION["ON"])

    def close(self):
        if self.relay:
            self.relay.close()
        if self.kb_relay:
            self.kb_relay.close()

    def take_screenshot(self):
        self.relay.on(self.power_port)
        self.relay.on(self.v_down_port)
        time.sleep(WAIT_ACTION["PRESS"])
        self.relay.off(self.power_port)
        self.relay.off(self.v_down_port)
