#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
:summary: This class implements wrapping equipment calls to control device from ACS FWK
:since: 22/01/14
:author: cbonnard
"""
import time

import acs.Core.Equipment.EquipmentManager as EquipmentManager
from acs.UtilitiesFWK.Utilities import get_config_value, split_and_strip
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class DeviceController(object):

    """
    DeviceController class: This class implements wrapping equipment calls to control device from ACS FWK
    """

    RELAY_PUSH_DELAY = 0.2
    RELAY_RELEASE_DELAY = 0.2

    def __init__(self, phone_name, device_config, em_params, logger):
        """

        :param phone_name: instance name of phone in bench config
        :param device_config: device instance config
        :param em_params: specific config for energy management of power supply
        :param logger: logger of device
        """
        self._device_config = device_config
        self._phone_name = phone_name
        self._em_params = em_params
        self._logger = logger
        self._prss_pwr_btn_time_switch_off = self.__get_config("pressPowerBtnTimeSwitchOff", 10, int)
        self._prss_pwr_btn_time_switch_on = self.__get_config("pressPowerBtnTimeSwitchOn", 3, int)

        # Get a reference of equipment manager
        self._eqt_man = EquipmentManager.EquipmentManager()
        # Retrieve an instance of equipment io_adapter
        self.__io_adapter = self.__init_io_adapter()
        # Retrieve an instance of equipment io_card
        self.__io_card = self.__init_io_card()
        # Retrieve an instance of power supply.
        self.__power_supply = self.__init_power_supply()
        # Retrieve an instance of equipment usb hub
        self.__usb_hub = self.__init_usb_hub()
        # Retrieve an instance of equipment keyboard emulator
        self.__keyboard_emulator = self.__init_keyboard_emulator()

    def __init_keyboard_emulator(self):
        """
            Retreive an instance of keyboard emulator
            from equipment type and instance name
        :rtype : equipment
        :return: keyboard emulator instance
        """
        # use parameter USBHub of given DeviceModel
        # if parameter not defined, take first hub instance
        keyboard_emulator_name = self.__get_config(EquipmentManager.KEYBOARD_EMULATOR_INSTANCE_NAME_DEVICE_PARAM, "")
        if keyboard_emulator_name:
            keyboard_emulator = self._eqt_man.get_keyboard_emulator(keyboard_emulator_name)
        else:
            keyboard_emulators = self._eqt_man.get_keyboard_emulators().values()
            if keyboard_emulators:
                keyboard_emulator = keyboard_emulators[0]
            else:
                keyboard_emulator = None
        return keyboard_emulator

    def __init_power_supply(self):
        """
            Retreive an instance of power supply
            from equipment type and instance name
        :rtype : equipment
        :return: power supply instance
        """
        # use parameter PowerSupply of given DeviceModel
        # if parameter not defined, take first power supply instance
        ps_name = self.__get_config(EquipmentManager.POWER_SUPPLY_INSTANCE_NAME_DEVICE_PARAM, "")
        if ps_name:
            power_supply = self._eqt_man.get_power_supply(ps_name)
        else:
            power_supplies = self._eqt_man.get_power_supplies().values()
            if power_supplies:
                power_supply = power_supplies[0]
            else:
                power_supply = None
        return power_supply

    def __init_usb_hub(self):
        """
            Retreive an instance of usb hub
            from equipment type and instance name
        :rtype : equipment
        :return: usb hub instance
        """
        # use parameter USBHub of given DeviceModel
        # if parameter not defined, take first hub instance
        usb_hub_name = self.__get_config(EquipmentManager.USB_HUB_INSTANCE_NAME_DEVICE_PARAM, "")
        if usb_hub_name:
            usb_hub = self._eqt_man.get_usb_hub(usb_hub_name)
        else:
            usb_hubs = self._eqt_man.get_usb_hubs().values()
            if usb_hubs:
                usb_hub = usb_hubs[0]
            else:
                usb_hub = None
        return usb_hub

    def __init_io_adapter(self):
        """
            Retrieve an instance of io adapter
            from equipment type and instance name
        :rtype : equipment
        :return: io adapter instance
        """
        # use parameter IoAdapter of given DeviceModel
        # if parameter not defined, take first io adapter instance
        io_adapter_name = self.__get_config(EquipmentManager.IO_ADAPTER_INSTANCE_NAME_DEVICE_PARAM, "")
        if io_adapter_name:
            io_adapter = self._eqt_man.get_io_adapter(io_adapter_name)
        else:
            io_adapters = self._eqt_man.get_io_adapters().values()
            if io_adapters:
                io_adapter = io_adapters[0]
            else:
                io_adapter = None
            # configure default wall & batt id and bptherm for io card
        if io_adapter is not None:
            io_adapter.load_specific_dut_config(self._phone_name)

        return io_adapter

    def __init_io_card(self):
        """
            Retrieve an instance of io card
            from equipment type and instance name
        :rtype : equipment
        :return: io card instance
        """
        # use parameter IoCard of given DeviceModel
        # if parameter not defined, take first io card instance
        io_card_name = self.__get_config(EquipmentManager.IO_CARD_INSTANCE_NAME_DEVICE_PARAM, "")
        if io_card_name:
            io_card = self._eqt_man.get_io_card(io_card_name)
        else:
            io_cards = self._eqt_man.get_io_cards().values()
            if io_cards:
                io_card = io_cards[0]
            else:
                io_card = None
            # configure default wall & batt id and bptherm for io card
        if io_card is not None:
            io_card.load_specific_dut_config(self._phone_name)
            default_charger = self.__get_config("defaultWallCharger", "")
            if default_charger in [None, ""]:
                self._logger.warning("Default wall charger not configure , check your device catalog")
            else:
                io_card.set_default_wall_charger(default_charger)

            # Because some devices does not have battery, does not need to configure
            # EM Params yet on DeviceController init, so configure it only if necessary
            if self._em_params is not None:
                io_card = self.__configure_em_io(io_card)
            else:
                self._logger.debug("No battery info to configure for current device.")

        return io_card

    def __configure_em_io(self, io_card):
        """
            Configure iocard with some specific EM values and configuration

        :type io_card: equipment
        :param io_card: IO card to be used for configuration

        :rtype : equipment
        :return: Configured io card instance
        """
        # configure default battery type according to device catalog
        batt_info = self._em_params.get("BATTERY")
        if isinstance(batt_info, dict) and batt_info.get("BATTID_TYPE") is not None:
            batt_type = batt_info.get("BATTID_TYPE")
            io_card.set_default_battery_type(batt_type)
            # batt id and bptherm config only for EMT350
            if io_card.get_model() == "EMT350":
                io_card.set_default_batt_id_value(self._em_params.get("BATTERY").get("BATT_ID_VALUE"))
                io_card.set_default_bptherm_value(self._em_params.get("BATTERY").get("BPTHERM_VALUE"))

        return io_card

    def __get_config(self, config_name, default_value=None, default_cast_type=str):
        """
        Return the value of the given config name
        The type of the value can be checked before assignment
        A default value can be given in case the config name does not exist

        :type config_name: string
        :param config_name: name of the property value to retrieve

        :type default_value: string
        :param default_value: default_value of the property

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: string or type of default_cast_type
        :return: config value
        """

        return get_config_value(self._device_config, "device config", config_name, default_value, default_cast_type)

    def __get_keyboard_emulator(self, raise_exception=False):
        """
            Retreive keyboard emulator instance
        :param raise_exception: raise exception if equipment no defined
        :return: keyboard emulator equipment
        """
        if self.__keyboard_emulator is not None or not raise_exception:
            keyboard_emulator = self.__keyboard_emulator
        else:
            msg = "Missing keyboard emulator to control device!"
            self._logger.error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
        return keyboard_emulator

    def __get_iocard(self, raise_exception=False):
        """
            Retreive io card instance
        :param raise_exception: raise exception if equipment no defined
        :return: io card equipment
        """
        if self.__io_card is not None or not raise_exception:
            io_card = self.__io_card
        else:
            msg = "Missing io card to control device!"
            self._logger.error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
        return io_card

    def is_iocard_configured(self):
        """
            Indicate whether an IO_CARD is configured or not
        """
        return True if self.__io_card is not None else False

    def __get_ioadapter(self, raise_exception=False):
        """
        Retreive io adapter instance
        :param raise_exception: raise exception if equipment no defined
        :return: io adapter equipment
        """
        if self.__io_adapter is not None or not raise_exception:
            io_adapter = self.__io_adapter
        else:
            msg = "Missing io adapter to control device!"
            self._logger.error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
        return io_adapter

    def is_ioadapter_configured(self):
        """
            Indicate whether an IO_ADAPTER is configured or not
        """
        return True if self.__io_adapter is not None else False

    def __get_power_supply(self, raise_exception=False):
        """
            Retreive io card instance
        :param raise_exception: raise exception if equipment no defined
        :return: io card equipment
        """
        if self.__power_supply is not None or not raise_exception:
            power_supply = self.__power_supply
        else:
            msg = "Missing power supply to control device!"
            self._logger.error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
        return power_supply

    def __get_usb_hub(self, raise_exception=False):
        """
            Retreive usb hub instance
        :param raise_exception: raise exception if equipment no defined
        :return: usb hub equipment
        """
        if self.__usb_hub is not None or not raise_exception:
            usb_hub = self.__usb_hub
        else:
            msg = "Missing usb hub to control device!"
            self._logger.error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
        return usb_hub

    def write_keyboard_commands(self, commands, raise_exception=False):
        """
            Forward call to equipment
        :param commands: alphanumeric string or list of commands to be sent sequentially
        :param raise_exception: raise exception if equipment no defined for this function
        """
        keyboard_emulator = self.__get_keyboard_emulator(raise_exception)
        if keyboard_emulator is not None:
            keyboard_emulator.write_keys(commands)

    def press_power_button(self, duration, raise_exception=False):
        """
            Forward call to equipment
        :param duration: time of press on the button
        :param raise_exception: raise exception if equipment no defined for this function
        """
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            io_card.press_power_button(duration)

    def connect_usb_host_to_dut(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        status = False
        io_card = self.__get_iocard(raise_exception)
        usb_hub = self.__get_usb_hub(raise_exception)
        if usb_hub is not None:
            status = usb_hub.enable_port_usb_host_device()
        elif io_card is not None:
            status = io_card.usb_host_pc_connector(True)
        return status

    def disconnect_usb_host_to_dut(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        status = False
        io_card = self.__get_iocard(raise_exception)
        usb_hub = self.__get_usb_hub(raise_exception)
        if usb_hub is not None:
            status = usb_hub.disable_port_usb_host_device()
        elif io_card is not None:
            status = io_card.usb_host_pc_connector(False)
        return status

    def connect_battery_to_dut(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            status = io_card.battery_connector(True)
        else:
            status = False
        return status

    def disconnect_battery_from_dut(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            status = io_card.battery_connector(False)
        else:
            status = False
        return status

    def plug_device_power(self, raise_exception=False):
        """
            Forward call to equipment
            Prepare device by powering it without switching it on
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        power_supply = self.__get_power_supply(raise_exception)
        if power_supply is not None:
            # Assume that if no exception operation is ok
            power_supply.power_on()

        status = self.connect_battery_to_dut()

        return status

    def cut_device_power(self, raise_exception=False):
        """
            Forward call to equipment
            Cut all power equipment connected to device without switching it off
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        power_supply = self.__get_power_supply(raise_exception)
        if power_supply is not None:
            power_supply.power_off()

        status = self.disconnect_battery_from_dut()

        return status

    def poweron_device(self, raise_exception=False):
        """
        Forward call to equipment
        Assume that if no exception raised at lower call level result is successfull
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        status = False
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            io_card.press_power_button(self._prss_pwr_btn_time_switch_on)
            status = True

        return status

    def poweroff_device(self, raise_exception=False):
        """
        Forward call to equipment
        Assume that if no exception raised at lower call level result is successfull
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        status = False
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            io_card.press_power_button(self._prss_pwr_btn_time_switch_off)
            status = True

        return status

    def enable_provisioning_line(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            status = io_card.set_provisioning_mode(True)
        else:
            status = False
        return status

    def disable_provisioning_line(self, raise_exception=False):
        """
            Forward call to equipment
        :param raise_exception: raise exception if equipment no defined for this function
        :return: status of operation
        :rtype: bool
        """
        io_card = self.__get_iocard(raise_exception)
        if io_card is not None:
            status = io_card.set_provisioning_mode(False)
        else:
            status = False
        return status

    def release(self):
        """
            Release all equipments of the DeviceController
        """
        try:
            if self.__io_card is not None:
                self.__io_card.release()
            if self.__power_supply is not None:
                self.__power_supply.release()
            if self.__usb_hub is not None:
                self.__usb_hub.release()
            if self.__keyboard_emulator is not None:
                self.__keyboard_emulator.release()
        except Exception as e:
            self._logger.warning("Equipment does not define the release method: %s" % str(e))

    def press_key_combo(self, keycombo_list, raise_exception=False, push_delay=RELAY_PUSH_DELAY,
                        release_delay=RELAY_RELEASE_DELAY):
        """
        Forward call to equipment to press key combo

        :type keycombo_list: str
        :param keycombo_list: list of button to press on

        :type raise_exception: bool
        :param raise_exception: raise exception if equipment is not defined for this function

        :type push_delay: float
        :param push_delay: delay between button push

        :type release_delay: float
        :param release_delay: delay between button release
        """

        io_card = self.__get_iocard(raise_exception)
        keyboard_emulator = self.__get_keyboard_emulator(raise_exception)

        keycombo_list = split_and_strip(keycombo_list, ';')
        for keycombo in keycombo_list:
            # Button list shall be defined as follow: 'BUTTON1+BUTTON2,PRESS_DURATION'
            press_duration = ""

            if len(keycombo.split(',')) > 1:
                # button_list = BUTTON1+BUTTON2
                # press_duration = PRESS_DURATION
                button_list, press_duration = split_and_strip(keycombo, ',')
            else:
                # If NO PRESS_DURATION ,set a default duration
                button_list = keycombo

            press_duration = float(press_duration) if press_duration else 1.0

            # In case button list contains keyboard input : 'KEYBOARD:fffff,1'
            if "KEYBOARD:" in button_list:
                if keyboard_emulator:
                    keyboard_input = button_list.replace("KEYBOARD:", "")
                    for char in keyboard_input:
                        keyboard_emulator.write_keys(char)
                        time.sleep(press_duration)
            else:
                # In other case button list can be : 'POWER_BUTTON+VOLUME_UP,5' or 'VOLUME_DOWN,1'
                if io_card:
                    io_card.press_key_combo(split_and_strip(button_list, '+'), press_duration,
                                            push_delay=push_delay, release_delay=release_delay)

            # WARNING ! Keyboard input and button cannot be mixed as follow: KEYBOARD:f+VOLUME_UP+POWER_BUTTON,5
            # In this case you should separate commands: KEYBOARD:f,0.2;VOLUME_UP+POWER_BUTTON,5
        return True
