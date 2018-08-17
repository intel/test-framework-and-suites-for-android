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

# import os
# import sys
import serial
import time

# import lib.utils.AtfSettings as AtfSettings

# create LOGGER
# LOGGER = AtfSettings.LOGGER


class UsbKm232():
    '''
    This class enables usage of UsbKm232 serial key emulator cable
    This class enables usage of UsbKm232 serial key emulator cable
    '''

    MAX_RSP_RETRIES = 10
    USB_QUEUE_DEPTH = 6
    BUFFER_CLEAR = '\x38'
    KEYS = {
        # row 1
        '`': 1,
        '1': 2,
        '2': 3,
        '3': 4,
        '4': 5,
        '5': 6,
        '6': 7,
        '7': 8,
        '8': 9,
        '9': 10,
        '0': 11,
        '-': 12,
        '=': 13,
        '<undef1>': 14,
        '<backspace>': 15,
        '<tab>': 16,
        'q': 17,
        'w': 18,
        'e': 19,
        'r': 20,
        't': 21,
        'y': 22,
        'u': 23,
        'i': 24,
        'o': 25,
        'p': 26,
        '[': 27,
        ']': 28,
        '\\': 29,
        # row 2
        '<capslock>': 30,
        'a': 31,
        's': 32,
        'd': 33,
        'f': 34,
        'g': 35,
        'h': 36,
        'j': 37,
        'k': 38,
        'l': 39,
        ';': 40,
        '\'': 41,
        '<undef2>': 42,
        '<enter>': 43,
        # row 3
        '<lshift>': 44,
        '<undef3>': 45,
        'z': 46,
        'x': 47,
        'c': 48,
        'v': 49,
        'b': 50,
        'n': 51,
        'm': 52,
        ',': 53,
        '.': 54,
        '/': 55,
        '[BUFFER_CLEAR]': 56,
        '<rshift>': 57,
        # row 4
        '<lctrl>': 58,
        '<undef5>': 59,
        '<lalt>': 60,
        ' ': 61,
        '<ralt>': 62,
        '<undef6>': 63,
        '<rctrl>': 64,
        '<undef7>': 65,
        '<lwin>': 70,
        '<rwin>': 71,
        '<win apl>': 72,
        '<insert>': 75,
        '<delete>': 76,
        '<undef16>': 78,
        '<larrow>': 79,
        '<home>': 80,
        '<end>': 81,
        '<undef23>': 82,
        '<uparrow>': 83,
        '<downarrow>': 84,
        '<pgup>': 85,
        '<pgdown>': 86,
        '<rarrow>': 89,
        # numpad
        '<numlock>': 90,
        '<num7>': 91,
        '<num4>': 92,
        '<num1>': 93,
        '<undef27>': 94,
        '<num/>': 95,
        '<num8>': 96,
        '<num5>': 97,
        '<num2>': 98,
        '<num0>': 99,
        '<num*>': 100,
        '<num9>': 101,
        '<num6>': 102,
        '<num3>': 103,
        '<num.>': 104,
        '<num->': 105,
        '<num+>': 106,
        '<numenter>': 107,
        '<undef28>': 108,
        # row 0
        '<esc>': 110,
        '<f1>': 112,
        '<f2>': 113,
        '<f3>': 114,
        '<f4>': 115,
        '<f5>': 116,
        '<f6>': 117,
        '<f7>': 118,
        '<f8>': 119,
        '<f9>': 120,
        '<f10>': 121,
        '<f11>': 122,
        '<f12>': 123,
        '<prtscr>': 124,
        '<scrllk>': 125,
        '<pause/brk>': 126,
        # mouse actions
        '<mouse_left>': 66,
        '<mouse_right>': 67,
        '<mouse_up>': 68,
        '<mouse_down>': 69,
        '<mouse_lbtn_On>': 73,
        '<mouse_rbtn_On>': 74,
        '<mouse_mbtn_On>': 77,
        '<mouse_scr_up>': 87,
        '<mouse_scr_down>': 88,
        '<mouse_slow>': 109,
        '<mouse_fast>': 111,
    }

    def __init__(self, km232_serial_device, verbose=False):
        '''
        This is the constructor and will initiate serial connection
        '''
        self.serial_device = km232_serial_device

        self.verbose = verbose
        if self.verbose:
            print("UsbKm232.serial_device= %s" % self.serial_device)
        # LOGGER.info("UsbKm232.serial_device= %s"%self.serial_device)
        if self.serial_device:
            tries = 5
            while tries > 0:
                try:
                    self.serial = serial.Serial(
                        self.serial_device, baudrate=9600)
                    self.serial.setTimeout(0.5)
                    self.serial.setWriteTimeout(0.5)
                except serial.SerialException, e:
                    # try maximum 5 times to initialize the serial
                    if tries == 1:
                        raise serial.SerialException(e)
                    tries = tries - 1
                    time.sleep(2)
                else:
                    tries = 0
        else:
            raise Exception("Error: UsbKm232 device: '{0}' not found. \
                            \nPlease verify board config file"
                            .format(self.serial_device))

    def release_key(self, release_ch):
        '''
        This function is used to define the release key sygnal
        '''
        return '%c' % (self.KEYS[release_ch] | 0x80)

    def get_response(self, orig_ch):
        '''
        Check response after sending character to UsbKm232.
        The response is the one's complement of the value sent.  This method
        blocks until proper response is received.
        In Params:
            - orig_ch: original character sent
        Raises:
          Exception: if response was incorrect or timed out
        '''
        count = 0
        rsp = self.serial.read(1)

        # LOGGER.debug("re-read rsp = " + str(rsp))
        if self.verbose:
            print("re-read rsp = " + str(rsp))

        while (len(rsp) != 1 or ord(orig_ch) != (~ord(rsp) & 0xff)) \
                and count < self.MAX_RSP_RETRIES:
            rsp = self.serial.read(1)

            # LOGGER.info("re-read rsp = " + str(rsp))
            if self.verbose:
                print("re-read rsp = " + str(rsp))

            time.sleep(1)
            count += 1
        if count == self.MAX_RSP_RETRIES:
            # in case no response receive try release previous key
            raise Exception("Failed to get correct response from UsbKm232")

        # LOGGER.info("UsbKm232: response [-] = \\0%03o 0x%02x"\
        #            % (ord(rsp), ord(rsp)))
        if self.verbose:
            print("UsbKm232: response [-] = \\0%03o 0x%02x"
                  % (ord(rsp), ord(rsp)))

    def send_list_of_commands(self, mylist, check=False, BUFFER_CLEAR=True):
        '''
        Write list of commands to UsbKm232.
        In Params:
            - mylist: list of encoded commands to send to the uart side of the
            UsbKm232
            - check: boolean determines whether response from UsbKm232 should be
            checked.
            - BUFFER_CLEAR: boolean determines whether
            keytroke BUFFER_CLEAR should be sent at end of the sequence
        '''
        for i, write_ch in enumerate(mylist):
            # LOGGER.debug("UsbKm232: writing  [%d] = \\0%03o 0x%02x" % \
            #             (i, ord(write_ch), ord(write_ch)))
            if self.verbose:
                print("UsbKm232: writing  [%d] = \\0%03o 0x%02x" %
                      (i, ord(write_ch), ord(write_ch)))

            self.serial.write(write_ch)
            if check:
                self.get_response(write_ch)
            time.sleep(.05)
        if BUFFER_CLEAR:
            # LOGGER.debug("UsbKm232: BUFFER_CLEARing keystrokes")
            if self.verbose:
                print("UsbKm232: BUFFER_CLEARing keystrokes")

            self.serial.write(self.BUFFER_CLEAR)
            if check:
                self.get_response(self.BUFFER_CLEAR)

    def generate_command_from_input(self, mystr):
        '''
        Write string to UsbKm232.
        In Params:
            - mystr: string to send across the UsbKm232
        '''
        rlist = []
        # LOGGER.debug("String to be typed on DUT = "+ mystr)
        if self.verbose:
            print("String to be typed on DUT = " + mystr)

        # check to see if string represent a key
        if mystr in self.KEYS:
            rlist.append(chr(self.KEYS['%s' % mystr]))
            rlist.append(self.release_key(mystr))
        else:
            for write_ch in mystr:
                rlist.append(chr(self.KEYS['%s' % write_ch]))
                rlist.append(self.release_key(write_ch))
        self.send_list_of_commands(rlist, check=False)

    def close(self):
        if self.verbose:
            print("Closing serial connection")
        if self.serial.isOpen():
            self.serial.close()
        if self.verbose:
            print("Connection closed.")
