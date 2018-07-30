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
:summary: Equipment manager
:since: 10/03/2011
:author: ymorel
"""

import inspect
import os
import time
import weakref
from xml import sax
from xml.sax.handler import ContentHandler

from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.TestEquipmentException import TestEquipmentException
from acs.Core.Report.ACSLogging import LOGGER_EQT, LOGGER_EQT_STATS
from acs.UtilitiesFWK.Utilities import Global, str_to_bool, get_class
from acs.Core.PathManager import Paths


# Equipments types in equipment catalogs
POWER_SUPPLY_TYPE = "PowerSupply"
IO_ADAPTER_TYPE = "IOAdapters"
IO_CARD_TYPE = "IOCard"
USB_HUB_TYPE = "USBHub"
EQT_MODEL_KEY = "Model"
KEYBOARD_EMULATOR_TYPE = "KeyboardEmulator"

# Parameters in DeviceCatalog or overriden in BenchConfig
IO_ADAPTER_INSTANCE_NAME_DEVICE_PARAM = "IoAdapter"
IO_CARD_INSTANCE_NAME_DEVICE_PARAM = "IoCard"
POWER_SUPPLY_INSTANCE_NAME_DEVICE_PARAM = "PowerSupply"
USB_HUB_INSTANCE_NAME_DEVICE_PARAM = "USBHub"
KEYBOARD_EMULATOR_INSTANCE_NAME_DEVICE_PARAM = "KeyboardEmulator"

# Equipment manager common functions #


class EquipmentManager(object):
    """
    EquipmentManager class:
        this class is a singleton and manages all instantiated equipments
    """

    # The singleton instance
    __instance = None

    # Dictionary of all equipment instances. The key is the bench name
    # of the equipment
    __equipment_instances = {}
    __power_supplies = None
    __io_adapters = None
    __io_cards = None
    __usb_hubs = None
    __keyboard_emulators = None

    # The global configuration
    __global_cfg = None
    __power_supply_required_by_user = False
    __io_card_required_by_user = False

    # Logger
    __logger = LOGGER_EQT

    def __new__(cls):
        """
        Constructor that always returns the same instance of EquipmentManager
        """
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def set_global_config(cls, global_config):
        """
        Sets the global configuration to use
        :type global_config: global configuration
        :param global_config: the global configuration to use
        """
        cls.__global_cfg = global_config
        cls.__power_supply_required_by_user = str_to_bool(
            global_config.campaignConfig.get("isControlledPSUsed", "false"))
        cls.__io_card_required_by_user = str_to_bool(
            global_config.campaignConfig.get("isIoCardUsed", "false"))

    @classmethod
    def get_global_config(cls):
        """
        Gets global configuration
        :rtype: global configuration
        :return: the global configuration if it has been set before
        :raise AcsConfigException if global configuration has not been set yet
        """
        if cls.__global_cfg is None:
            msg = "Global configuration should be set before using " \
                  "EquipmentManager"
            cls.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR,
                                     msg)
        else:
            return cls.__global_cfg

    @classmethod
    def get_logger(cls):
        """
        Gets the equipment manager logger
        """
        return cls.__logger

    def __get_equipment_type_dic(self, eqt_model, eqt_type):
        """
        Gets the equipment type dictionary associated to the type parameter
        of an equipment in the bench configuration, checks that eqt_model
        is an eqt_type equipment
        :type eqt_model: str
        :param eqt_model: the model of the equipment
        :type eqt_type: str
        :param eqt_type: the equipment type of the equipment
        :rtype: dict
        :return: the equipment type part of the dictionary
        """
        eqt_catalog = self.get_global_config().equipmentCatalog
        eqt_types = eqt_catalog.keys()
        eqt_type_dic = None

        if eqt_type not in eqt_types:
            msg = "Can't find '" + eqt_type + "' in equipment catalog"
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)
        else:
            if eqt_model in eqt_catalog[eqt_type].keys():
                eqt_type_dic = eqt_catalog[eqt_type]

        if eqt_type_dic is None:
            msg = "Can't find '" + eqt_model + "' in equipment catalog"
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

        return eqt_type_dic

    def delete_equipment(self, bench_name):
        """
        Deletes instance of the equipment and removes it from the
        equipment dictionary
        :type bench_name: str
        :param bench_name: the bench configuration name of the equipment
        """
        # Search for the equipment in equipment catalog dictionary
        self.get_logger().debug("Remove %s", bench_name)
        # Get equipment instance if it exists
        eqt_ref = self.__equipment_instances.pop(bench_name, None)
        if eqt_ref is not None:
            # Remove all refs to the equipment in the equipment dictionary
            # For example, the same power supply can be referenced by his name
            # and by its outputs
            for key in self.__equipment_instances.keys():
                eqt = self.__equipment_instances[key]
                if eqt == eqt_ref:
                    self.__equipment_instances.pop(key)
                del eqt
            self.get_logger().debug("%s deleted", bench_name)
        else:
            self.get_logger().debug("No %s instance found", bench_name)

    def delete_all_equipments(self):
        """
        Deletes all instantiated equipments and removes them from equipment
        dictionary
        """
        self.get_logger().debug("Delete all equipments")
        for name in self.__equipment_instances.keys():
            eqt = self.__equipment_instances.pop(name)
            del eqt
            self.get_logger().debug("%s deleted", name)

    def get_equipment(self, bench_name):
        """
        Gets the instance of an equipment if it exists.
        :param bench_name: name of equipment in benchconfig
        :rtype: object
        :return: the instance of the equipment if it exists,
        else returns None
        """
        return self.__equipment_instances.get(bench_name, None)

    #
    # Bluetooth network simulators specific functions #
    #
    def get_bluetooth_network_simulator(self, bench_name):
        """
        Gets the instance of a bluetooth network simulator
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IBTNetSim
        :return: the instance of the requested
            bench bluetooth network simulator
        """

        self.get_logger().debug(
            "Get bluetooth network simulator %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog
        # and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "BT network simulator is not configured in your bench config"
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG,
                                     msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model,
                                                "BTNetworkSimulator")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.__logger.debug(msg)
        else:  # Try to create the bluetooth network simulator
            if eqt_model == "AGILENT_N4010A":
                self.get_logger().debug("Create Agilent N4010A")
                from acs_test_scripts.Equipment.NetworkSimulators.BT.AgilentN4010A.AgilentN4010A import AgilentN4010A  # NOQA

                eqt = AgilentN4010A(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown bluetooth network simulator model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)
            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=bluetooth_network_simulator".format(
                inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Cellular network simulators specific functions #
    #
    def get_cellular_network_simulator(self, bench_name, rat=None, visa=False):
        """
        Gets the instance of a cellular network simulator
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :type rat: str
        :param rat: extra parameter used for 8960 equipment to specify RAT used
        note it can be overridden by another value for other equipment
        :type visa: boolean
        :param visa: extra parameter used in case we want to use
        the visa version of an equipment (in test step for instance)
        :rtype: ICellNetSim
        :return: the instance of the requested bench cellular network simulator
        """
        self.get_logger().debug("Get cellular network simulator %s",
                                bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog
        # and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Cellular network simulator is not configured" + \
                "in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG,
                                     msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model.replace("_VISA", ""),
                                                "CellularNetworkSimulator")

        # Check if equipment already exists or not
        # and return the existing one if any
        # Prepare argument dictionary
        eqt = self.get_equipment(bench_name)
        arg_dict = {
            "name": bench_name,
            "model": eqt_model,
            "eqt_params":
            eqt_dic, "bench_params": bench_dic
        }
        if rat is not None:
            arg_dict["rat"] = rat
        # as visa equipment and non visa equipment
        # can have the same equipment name,
        # we want to be sure to have the good interface
        # for the equipment (visa or not visa)
        from acs_test_scripts.TestStep.Utilities.Visa import VisaEquipmentBase
        # CMW500 is visa compliant in all cases so do not delete it
        if eqt_model not in ["RS_CMW500", "RS_CMW500_VISA"]:
            if isinstance(eqt, VisaEquipmentBase) ^ visa:
                self.delete_equipment(bench_name)
                eqt = None

        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the cellular network simulator
            if eqt_model in ["AGILENT_8960", "AGILENT_8960_VISA"]:
                self.get_logger().debug("Create %s" % eqt_model)
                if visa:
                    from acs_test_scripts.Equipment.NetworkSimulators.Cellular.Agilent8960.Agilent8960Visa import Agilent8960  # NOQA
                else:
                    from acs_test_scripts.Equipment.NetworkSimulators.Cellular.Agilent8960.Agilent8960 import Agilent8960  # NOQA
                eqt = Agilent8960(**arg_dict)
            elif eqt_model == "RS_CMU200":
                self.get_logger().debug("Create RS CMU200")
                from acs_test_scripts.Equipment.NetworkSimulators.Cellular.RsCmu200.RsCmu200 import RsCmu200  # NOQA
                eqt = RsCmu200(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "AGILENT_E6621A":
                self.get_logger().debug("Create Agilent E6621A")
                from acs_test_scripts.Equipment.NetworkSimulators.Cellular.AgilentE6621A.AgilentE6621A import AgilentE6621A  # NOQA
                # Import the equipment class to instantiate the equipment
                eqt = AgilentE6621A(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model in ["RS_CMW500", "RS_CMW500_VISA"]:
                from acs_test_scripts.Equipment.NetworkSimulators.Cellular.RsCmw500.RsCmw500 import RsCmw500  # NOQA
                self.get_logger().debug("Create %s" % eqt_model)
                # Import the equipment class to instantiate the equipment
                eqt = RsCmw500(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "ANRITSU_M8475A":
                from acs_test_scripts.Equipment.NetworkSimulators.Cellular.AnritsuM8475A.AnritsuM8475A import AnritsuM8475A  # NOQA
                self.get_logger().debug("Create %s" % eqt_model)
                # Import the equipment class to instantiate the equipment
                eqt = AnritsuM8475A(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown cellular network simulator model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=cellular_network_simulator".format(
                inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # WLAN network simulators specific functions #
    #
    def get_wlan_network_simulator(self, bench_name):
        """
        Gets the instance of a WLAN network simulator
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IWLanNetSim
        :return: the instance of the requested bench WLAN network simulator
        """
        self.get_logger().debug("Get WLAN network simulator %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog
        # and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "WLan network simulator is not configured " + \
                "in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG,
                                     msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model,
                                                "WLanNetworkSimulator")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the WLAN network simulator
            if eqt_model == "ANRITSU_8860":

                self.get_logger().debug("Create Anritsu 8860")
                from acs_test_scripts.Equipment.NetworkSimulators.WLan.Anritsu8860.Anritsu8860 import Anritsu8860

                eqt = Anritsu8860(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown WLAN network simulator model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=wlan_network_simulator".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # GPS network simulators specific functions  #
    #
    def get_gps_network_simulator(self, bench_name):
        """
        Gets the instance of a GPS network simulator
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IGPSNetSim
        :return: the instance of the requested bench WLAN network simulator
        """
        self.get_logger().debug("Get GPS network simulator %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "GPSNetworkSimulator is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "GPSNetworkSimulator")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the WLAN network simulator
            if eqt_model == "SPIRENT_GSS6700":
                self.get_logger().debug("Create Spirent GSS6700")
                from acs_test_scripts.Equipment.NetworkSimulators.GPS.SpirentGSS6700.SpirentGSS6700 import SpirentGSS6700  # NOQA

                eqt = SpirentGSS6700(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown GPS network simulator model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=gps_network_simulator".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # AP configuration specific functions #
    #
    def get_configurable_ap(self, bench_name):
        """
        Gets the instance of a configurable AP
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype:
        :return: the instance of the requested bench configurable AP
        """
        self.get_logger().debug("Get configurable AP %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Configurable access point is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "ConfigurableAccessPoint")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the configurable AP
            if eqt_model == "DLINK_DAP2553":
                self.get_logger().debug("Create D-Link DAP2553")
                from acs_test_scripts.Equipment.ConfigurableAP.DLinkDAP2553.DLinkDAP2553 import DLinkDAP2553

                eqt = DLinkDAP2553(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "CISCO_1250":
                self.get_logger().debug("Create Cisco 1250")
                from acs_test_scripts.Equipment.ConfigurableAP.Cisco1250.Cisco1250 import Cisco1250

                eqt = Cisco1250(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "CISCO_1260":
                self.get_logger().debug("Create Cisco 1260")
                from acs_test_scripts.Equipment.ConfigurableAP.Cisco1260.Cisco1260 import Cisco1260

                eqt = Cisco1260(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "CISCO_WAP4410N":
                self.get_logger().debug("Create Cisco WAP4410N")
                from acs_test_scripts.Equipment.ConfigurableAP.CiscoWAP4410N.CiscoWAP4410N import CiscoWAP4410N

                eqt = CiscoWAP4410N(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "CISCO_WRVS4400N":
                self.get_logger().debug("Create Cisco WRVS4400N")
                from acs_test_scripts.Equipment.ConfigurableAP.CiscoWRVS4400N.CiscoWRVS4400N import CiscoWRVS4400N

                eqt = CiscoWRVS4400N(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "CISCO_AP541N":
                self.get_logger().debug("Create Cisco AP541N")
                from acs_test_scripts.Equipment.ConfigurableAP.CiscoAP541N.CiscoAP541N import CiscoAP541N

                eqt = CiscoAP541N(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "AP_CONTROLLER":
                self.get_logger().debug("Create AccessPoint Controller")
                from acs_test_scripts.Equipment.ConfigurableAP.APController.APController import APController

                eqt = APController(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "ASUS_AC66U":
                self.get_logger().debug("Create AccessPoint Controller")
                from acs_test_scripts.Equipment.ConfigurableAP.AsusAC66U.AsusAC66U import AsusAC66U

                eqt = AsusAC66U(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown configurable AP model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=configurable_ap".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_all_configurable_aps(self):
        """
        Gets a list of all instances of configurable APs
        :rtype: list
        :return: the instances of all bench configurable APs
        """
        self.get_logger().debug("Get all configurable APs")
        config_aps = list()

        # Get all the equipment names included in the benchConfig
        eq_names = self.get_global_config().benchConfig.get_parameters_name()

        for eq_name in eq_names:

            # Identify the Configurable AP equipments
            bench_dic = \
                self.get_global_config().benchConfig.get_parameters(eq_name)
            eqt_model = bench_dic.get_param_value("Model", "undef")
            if eqt_model in ["DLINK_DAP2553", "CISCO_1250", "CISCO_1260",
                             "CISCO_WAP4410N", "CISCO_WRVS4400N",
                             "CISCO_AP541N", "AP_CONTROLLER", "ASUS_AC66U"]:
                config_aps.append(self.get_configurable_ap(eq_name))

        return config_aps

    #
    # Sniffer specific functions #
    #

    def get_sniffer(self, bench_name):
        """
        Gets the instance of a Sniffer
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: ISniffer
        :return: the instance of the requested Sniffer
        """
        self.get_logger().debug("Get sniffer %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Sniffer is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "Sniffer")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the sniffer
            if eqt_model == "TCPDump":
                self.get_logger().debug("Create TCPDump Sniffer")
                from acs_test_scripts.Equipment.Sniffer.TCPDump.TCPDump import TCPDump

                eqt = TCPDump(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "WireShark":
                self.get_logger().debug("Create WireShark Sniffer")
                from acs_test_scripts.Equipment.Sniffer.WireShark.WireShark import WireShark

                eqt = WireShark(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown Sniffer model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=sniffer".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # RF Attenuator specific functions #
    #

    def get_rf_attenuator(self, bench_name):
        """
        Gets the instance of a RF attenuator
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype:
        :return: the instance of the requested bench RF attenuator
        """
        self.get_logger().debug("Get RF attenuator %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get bench dictionary
        bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "RF Attenuator is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "RFAttenuator")

        # Check if equipment already exists or not and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the RF Attenuator
            if eqt_model in ["VaunixLDALinux", "VaunixLDAWindows"]:
                self.get_logger().debug("Create RF Attenuator Vaunix LDA")
                from acs_test_scripts.Equipment.RFAttenuator.VaunixLDA.VaunixLDA import VaunixLDA

                eqt = VaunixLDA(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "MC_RCDAT":
                self.get_logger().debug("Create RF Attenuator MCRCDAT")
                from acs_test_scripts.Equipment.RFAttenuator.McRCDAT.McRCDAT_ACS import McRCDAT_ACS

                eqt = McRCDAT_ACS(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown RF attenuator model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=rf_attenuator".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # P2P Client specific functions #
    #

    def get_p2p(self, bench_name):
        """
        Gets the instance of Wifi p2p client
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: P2P_Client
        :return: the instance of the requested Wifi P2P Client
        """
        self.get_logger().debug("Get P2P %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get bench dictionary
        bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "P2P is not configured in you bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "P2P")

        # Check if equipment already exists or not and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the P2P Client
            if eqt_model == "P2pClient":
                self.get_logger().debug("Create P2P Client")
                from acs_test_scripts.Equipment.WifiP2p.P2pClient.P2pClient import P2pClient

                eqt = P2pClient(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "P2pSupplicant":
                self.get_logger().debug("Create P2P Supplicant")
                from acs_test_scripts.Equipment.WifiP2p.P2pSupplicant.P2pSupplicant import P2pSupplicant

                eqt = P2pSupplicant(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown P2P model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)
            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=p2p".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_rf_matrix(self, eqt_name):
        """
        Gets the instance of a RF matrix

        :type eqt_name: str
        :param eqt_name: the name of the equipment in the BenchConfig
        :rtype: object
        :return: the instance of the requested bench Computer
        """
        self.get_logger().debug("Get RF matrix %s", eqt_name)
        # Check that eqt_eqt_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(eqt_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            eqt_model = "USB-4SPDT-A18"
        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(eqt_name)

        if eqt is not None:
            msg = eqt_name + " already exists, return existing instance"
            self.get_logger().debug(msg)

        else:  # Try to create the Computer Object
            if eqt_model == "USB-4SPDT-A18":
                from acs_test_scripts.Equipment.RFMatrix.RFMatrix import RFMatrix

                eqt = RFMatrix(eqt_name, eqt_model, bench_dic)
            else:
                msg = "Unknown RF matrix model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[eqt_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=rfmatrix".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Computer specific functions #
    #
    def get_computer(self, eqt_name):
        """
        Gets the instance of a Computer

        :type eqt_name: str
        :param eqt_name: the name of the equipment in the BenchConfig
        :rtype: object
        :return: the instance of the requested bench Computer
        """
        self.get_logger().debug("Get Computer %s", eqt_name)
        # Check that eqt_eqt_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(eqt_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Local or remote computer is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(eqt_name)

        if eqt is not None:
            msg = eqt_name + " already exists, return existing instance"
            self.get_logger().debug(msg)

        else:  # Try to create the Computer Object
            if eqt_model == "LOCAL_COMPUTER":
                from acs_test_scripts.Equipment.Computer.LocalComputer.LocalComputer import LocalComputer

                eqt = LocalComputer(eqt_name, eqt_model, bench_dic)
            elif eqt_model == "REMOTE_COMPUTER":
                from acs_test_scripts.Equipment.Computer.RemoteComputer.RemoteComputer import RemoteComputer

                eqt = RemoteComputer(eqt_name, eqt_model, bench_dic)
            else:
                msg = "Unknown Computer model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[eqt_name] = eqt

        LOGGER_EQT_STATS.info("Create equipment={0};type=computer".format(
            inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def __get_equipment_instances(self, equipment_type, equipment_instances_dict, equipment_required=False):
        """
        Gets a list of all equipment instances of given type and configured in bench configuration file
        If dictionnary is etmpy,  instantiates all instances of benchconfig and fill dictionnary
        :rtype: dict
        :return: a dictionary containing all available instances of given equipment type
        """
        if equipment_instances_dict is None:
            equipment_models = {}
            equipment_instances_dict = {}
            # Retreive a dictionnary of the benchconfig
            bench_cfg = self.get_global_config().benchConfig.get_dict()
            # Retreive a dictionnary of the equipments catalog
            eqt_catalog = self.get_global_config().equipmentCatalog
            # Search for equipment type given in parameter
            for eqt_type, eqt_type_dict in eqt_catalog.iteritems():
                if eqt_type == equipment_type:
                    # Store all models of equipment type given in param
                    equipment_models = eqt_type_dict.keys()
                    break
            # Search for an  equipment of given type in benchconfig
            for eqt_name, eqt_dict in bench_cfg.iteritems():
                try:
                    # Data is encapsulated in a dict (once again....)
                    model = eqt_dict[EQT_MODEL_KEY]['value']
                    if model in equipment_models:
                        # FIXME : beware for now __instantiate_equipment is not generic enough to be used in all cases
                        # if using __get_equipment_instances you should check if you eq need a specific getter
                        # a story should be created to rework all EquipmentManager
                        if equipment_type == POWER_SUPPLY_TYPE:
                            eqt = self.get_power_supply(eqt_name)
                            # history: eqt.init() done here
                            eqt.init()
                        elif equipment_type == IO_CARD_TYPE:
                            eqt = self.get_io_card(eqt_name)
                            # history: eqt.init() already done inside get_io_card
                        elif equipment_type == IO_ADAPTER_TYPE:
                            eqt = self.get_io_adapter(eqt_name)
                        else:
                            eqt = self.__instantiate_equipment(eqt_name, equipment_type)
                            if eqt is not None:
                                eqt.init()
                        # Store equipment type instances in equipment dictionary
                        equipment_instances_dict[eqt_name] = eqt

                # If no model found, we are in the phones section of benchconfig
                # (the benchonfig dict is a raw data parsed...unfortunatelly)
                # So nothing to parse if key not found
                except KeyError:
                    pass
            if equipment_instances_dict == {} and equipment_required:
                msg = "No %s found in your bench config !" % equipment_type
                raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR, msg)
        return equipment_instances_dict

    def get_power_supplies(self):
        """
        Gets a list of all power supplies instances configured in bench
        configuration file
        :rtype: dict
        :return: a dictionary containing all available power supplies
        """
        return self.__get_equipment_instances(POWER_SUPPLY_TYPE, self.__power_supplies,
                                              self.__power_supply_required_by_user)

    def get_usb_hubs(self):
        """
        Gets a list of all usb hubs instances configured in bench
        configuration file
        :rtype: dict
        :return: a dictionary containing all available usb hubs
        """
        return self.__get_equipment_instances(USB_HUB_TYPE, self.__usb_hubs)

    def get_io_adapters(self):
        """
        Gets a list of all io adapter instances configured in bench
        configuration file
        :rtype: dict
        :return: a dictionary containing all available io adapter
        """
        return self.__get_equipment_instances(IO_ADAPTER_TYPE, self.__io_adapters)

    def get_io_cards(self):
        """
        Gets a list of all relay cards instances configured in bench
        configuration file
        :rtype: dict
        :return: a dictionary containing all available power supplies
        """
        return self.__get_equipment_instances(IO_CARD_TYPE, self.__io_cards,
                                              self.__io_card_required_by_user)

    def get_keyboard_emulators(self):
        """
        Gets a list of all keyboard emulators instances configured in bench
        configuration file
        :rtype: dict
        :return: a dictionary containing all available keyboard emulators
        """
        return self.__get_equipment_instances(KEYBOARD_EMULATOR_TYPE, self.__keyboard_emulators)

    def get_power_supply(self, bench_name):
        """
        Gets a power supply
        :type bench_name: str
        :param bench_name: the bench configuration name of the power supply
        :rtype: IPowerSupply
        :return: the instance of the requested power supply
        """
        self.get_logger().debug("Get power supply %s", bench_name)
        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)

        else:
            # Check that bench_name is in bench configuration and get
            # bench dictionary
            bench_dic = self.get_global_config().benchConfig. \
                get_parameters(bench_name)

            # Look for equipment in equipment catalog and get equipment type
            # catalog
            eqt_model = bench_dic.get_param_value("Model")
            if not eqt_model:
                msg = "PowerSupply is not configured in your bench config."
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

            eqt_dic = self.__get_equipment_type_dic(eqt_model, "PowerSupply")
            if eqt_model == "AGILENT_66311D":
                self.get_logger().debug("Create Agilent 63311D")
                from acs_test_scripts.Equipment.PowerSupplies.Agilent66311D.Agilent66311D import Agilent66311D

                eqt = Agilent66311D(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "AGILENT_66319D":
                self.get_logger().debug("Create Agilent 63319D")
                from acs_test_scripts.Equipment.PowerSupplies.Agilent66319D.Agilent66319D import Agilent66319D

                eqt = Agilent66319D(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "AGILENT_66321D":
                self.get_logger().debug("Create Agilent 63321D")
                from acs_test_scripts.Equipment.PowerSupplies.Agilent66321D.Agilent66321D import Agilent66321D

                eqt = Agilent66321D(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "AGILENT_E364xA":
                self.get_logger().debug("Create Agilent E364xA")
                from acs_test_scripts.Equipment.PowerSupplies.AgilentE364xA.AgilentE364xA import AgilentE364xA

                eqt = AgilentE364xA(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "Keithley2200_20_5":
                self.get_logger().debug("Create Keithley 2200_20_5")
                from acs_test_scripts.Equipment.PowerSupplies.Keithley2200_20_5.Keithley2200_20_5 import Keithley2200_20_5  # NOQA

                eqt = Keithley2200_20_5(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "NPC108":
                self.get_logger().debug("Create NPC108")
                from acs_test_scripts.Equipment.PowerSupplies.NPC108.NPC108 import NPC108

                eqt = NPC108(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "DLI_WPS5":
                self.get_logger().debug("Create WEB_POWER_SWITCH")
                from acs_test_scripts.Equipment.PowerSupplies.Dli_WebPowerSwitch5.Dli_WebPowerSwitch5 import Dli_WebPowerSwitch5  # NOQA

                eqt = Dli_WebPowerSwitch5(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown power supply model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipment catalog
            self.__equipment_instances[bench_name] = eqt

            # Add outputs for each new power supply, outputs are keys to get
            # power supply from equipment dictionary
            ps_params = sorted(bench_dic.get_parameters_name())

            for param in ps_params:
                if "OUTPUT" in param:
                    output_params = bench_dic.get_parameters(param)
                    ps_alias = output_params.get_param_value("Type")
                    self.__equipment_instances[ps_alias] = eqt

            if eqt_model != "NPC108":
                eqt = weakref.proxy(eqt)

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=power_supply".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_artifact_manager(self, bench_name):
        """
        Gets the Artifact Manager equipment
        :type bench_name: str
        :param bench_name: the name of the equipment in bench configuration file
        :rtype: IArtifactManager
        :return: the instance of the requested ArtifactManager equipment
        """
        eqt = self.__instantiate_equipment(bench_name, "Tool", "ArtifactManager")
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=artifact_manager".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_instant_logger(self, bench_name):
        """
        Gets the Instant Logger equipment
        :type bench_name: str
        :param bench_name: the name of the equipment in bench configuration file
        :rtype: INSTANTLogger
        :return: the instance of the requested Instant logger equipment
        """
        eqt = self.__instantiate_equipment(bench_name, "LOGGER", "INSTANTLogger")
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=instant logger".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_io_adapter(self, bench_name):
        """
        Gets the IO adapter equipment
        :type bench_name: str
        :param bench_name: the bench configuration name of the IO adapter
        :rtype: IIOAdapter
        :return: the instance of the requested IO adapter equipment
        """

        self.get_logger().debug("Get IO adapter %s", bench_name)
        # Look for equipment in equipment catalog and get equipment type catalog
        # Looks for equipment model in IOAdapters section
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            # Check that bench_name is in bench configuration and get
            # bench dictionary
            bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)
            # declared known ioadapter
            # TODO: Export this dictionary in the equipment catalog. Story to be created
            io_adapter = {"DLN4S": "Equipment.IOAdapters.Diolan.DLN4S.DLN4S", }
            # Look for equipment in equipment catalog and get equipment type
            # catalog
            eqt_model = bench_dic.get_param_value("Model")
            if not eqt_model:
                msg = "IO adapter is not configured in your bench config."
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

            eqt_dic = self.__get_equipment_type_dic(eqt_model, "IOAdapters")
            if eqt_model in io_adapter:
                self.get_logger().debug("Create %s" % eqt_model)
                # get instance of io card
                eqt_class = get_class(io_adapter[eqt_model])
                eqt = eqt_class(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown IO adapter model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Initialize equipment
            eqt.init()

            # Register new equipment in equipment dictionary
            self.__equipment_instances[bench_name] = eqt
            # Alias for Digital Input Output equipment
            # For the moment only one instance is used and exists at a time
            # self.__equipment_instances["ACB"] = eqt

        if eqt is not None:
            LOGGER_EQT_STATS.info(
                "Create equipment={0};type=io_adapter".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
            return weakref.proxy(eqt)

    def get_io_card(self, bench_name):
        """
        Gets the IO card equipment
        :type bench_name: str
        :param bench_name: the bench configuration name of the IO card
        :rtype: IIOCard
        :return: the instance of the requested IO card equipment
        """

        self.get_logger().debug("Get IO card %s", bench_name)
        # Look for equipment in equipment catalog and get equipment type catalog
        # Looks for equipment model in IOCard section
        eqt = self.get_equipment(bench_name)
        if self.__io_card_required_by_user:  # Try to create the IO card equipment if used
            # Check that bench_name is in bench configuration and get
            # bench dictionary
            bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)
            # Look for equipment in equipment catalog and get equipment type
            # catalog
            eqt_model = bench_dic.get_param_value("Model")
            if eqt is not None:
                msg = bench_name + " already exists, return existing instance"
                self.get_logger().debug(msg)
            else:
                # declared known iocard
                # TODO: Export this dictionary in the equipment catalog. Story to be created
                io_card = {"ACBP": "Equipment.IOCards.ACB.ACBP.ACBP",
                           "ACBN": "Equipment.IOCards.ACB.ACBN.ACBN",
                           "ACBE": "Equipment.IOCards.ACB.ACBE.ACBE",
                           "ACBT": "Equipment.IOCards.ACB.ACBT.ACBT",
                           "ACBMD": "Equipment.IOCards.ACB.ACBMD.ACBMD",
                           "EMT311": "Equipment.IOCards.ACB.EMT311.EMT311",
                           "EMT340": "Equipment.IOCards.ACB.EMT340.EMT340",
                           "JSB291": "Equipment.IOCards.JWorks.JSB291.JSB291",
                           "JSB291_64": "Equipment.IOCards.JWorks.JSB291.JSB291",
                           "MDAC": "Equipment.IOCards.MDAC.MDAC.MDAC",
                           "USB_RLY08": "Equipment.IOCards.USBRly08.USBRly08.USBRly08",
                           "USB_RLY08_REV1": "Equipment.IOCards.USBRly08Rev1.USBRly08.USBRly08",
                           "EMT350": "acs_test_scripts.Equipment.IOCards.ACB.EMT350.EMT350",
                           "USBRELAY32": "Equipment.IOCards.USBRELAY32.USBRELAY32.USBRELAY32"
                           }
                if not eqt_model:
                    msg = "IO card is not configured in your bench config."
                    self.get_logger().error(msg)
                    raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

                eqt_dic = self.__get_equipment_type_dic(eqt_model, "IOCard")
                if eqt_model in io_card:
                    self.get_logger().debug("Create %s" % eqt_model)
                    # get instance of io card
                    eqt_class = get_class(io_card[eqt_model])
                    eqt = eqt_class(bench_name, eqt_model, eqt_dic, bench_dic)
                else:
                    msg = "Unknown IO card model: " + eqt_model
                    self.get_logger().error(msg)
                    raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

                # Initialize equipment
                eqt.init()

                # wait some second to avoid over protect with some power supply
                time.sleep(5)

                # Register new equipment in equipment dictionary
                self.__equipment_instances[bench_name] = eqt
                # Alias for Digital Input Output equipment
                # For the moment only one instance is used and exists at a time
                # self.__equipment_instances["ACB"] = eqt
        else:
            self.get_logger().warning("IO Card disabled in campaign file (isIoCardUsed=False)")

        if eqt is not None:
            LOGGER_EQT_STATS.info(
                "Create equipment={0};type=io_card".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
            return weakref.proxy(eqt)

    def get_ethernet_commutator(self, bench_name):
        """
        Get the Ethernet commutator equipment

        :type bench_name: str
        :param bench_name: the bench configuration name of the Ethernet commutator equipment
        :rtype: EthernetCommutator object
        :return: the instance of the requested EthernetCommutator equipment
        """
        self.get_logger().debug("Get ethernet commutator equipment: %s" % bench_name)
        # Check that bench_name is in bench configuration and get bench dictionary from the Equipment Catalog
        bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)
        eqt_model = bench_dic.get_param_value("Model", "ETHERNET_COMMUTATOR")

        # Check if equipment already exists or not, and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the equipment
            self.get_logger().debug("Create Ethernet Commutator Equipment")

            from acs_test_scripts.Equipment.EthernetCommutator.EthernetCommutator.EthernetCommutator import EthernetCommutator  # NOQA

            eqt_dic = self.__get_equipment_type_dic(eqt_model, "EthernetCommutator")
            eqt = EthernetCommutator(bench_name, eqt_model, eqt_dic, bench_dic)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=ethernet_commutator".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_keyboard_emulator(self, bench_name):
        """
        Instantiate a keyboard emulator equipment of type KeyboardEmulator
        :type bench_name: str
        :param bench_name: the bench configuration name of the equipmenbt instance
        :rtype: KeyboardEmulator
        :return: the instance of the requested KeyboardEmulator equipment
        """
        eqt = self.__instantiate_equipment(bench_name, KEYBOARD_EMULATOR_TYPE)
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=keyboard_emulator".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_bluetooth_headset(self, bench_name):
        """
        Gets the instance of Bluetooth headset equipment
        :type bench_name: str
        :param bench_name: the bench configuration name of the BT headset
        :rtype: IBTHeadset
        :return: the instance of the requested BT headset equipment
        """
        self.get_logger().debug("Get BT headset %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "BT Headset is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "BluetoothHeadset")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the BT Headset
            if eqt_model == "NokiaBH214":
                self.get_logger().debug("Create NokiaBH214 Headset")
                from acs_test_scripts.Equipment.BTHeadset.NokiaBH214.NokiaBH214 import NokiaBH214

                eqt = NokiaBH214(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "SonySBH20":
                self.get_logger().debug("Create SonySBH20 Headset")
                from acs_test_scripts.Equipment.BTHeadset.SonySBH20.SonySBH20 import SonySBH20

                eqt = SonySBH20(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "NokiaBH111":
                self.get_logger().debug("Create NokiaBH111 Headset")
                from acs_test_scripts.Equipment.BTHeadset.NokiaBH111.NokiaBH111 import NokiaBH111

                eqt = NokiaBH111(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown BT Headset model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        # initialize equipment
        eqt.init()

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=bluetooth_headset".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_bluetooth_mouse(self, bench_name):
        """
        Gets the instance of Bluetooth mouse
        :type bench_name: str
        :param bench_name: the bench configuration name of the BT mouse
        :rtype: BtMouse
        :return: the instance of the requested BT Mouse
        """
        self.get_logger().debug("Get BT mouse %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "BT Mouse is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "BluetoothMouse")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the BT Headset
            if eqt_model == "HPMouseZ8000":
                self.get_logger().debug("Create HPMouseZ8000 Headset")
                from acs_test_scripts.Equipment.Bluetooth.HPMouseZ8000.HPMouseZ8000 import HPMouseZ8000

                eqt = HPMouseZ8000(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                from acs_test_scripts.Equipment.Bluetooth.Mouse.BtMouse import BtMouse

                eqt = BtMouse(bench_name, eqt_model, eqt_dic, bench_dic)

        # Register new equipment in equipments dictionary
        self.__equipment_instances[bench_name] = eqt

        # initialize equipment
        eqt.init()

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=bluetooth_mouse".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Attenuation box specific functions #
    #
    def get_attenuation_box(self, bench_name):
        """
        Gets the instance of an attenuation box
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IAttBox
        :return: the instance of the requested bench attenuation box
        """
        self.get_logger().debug("Get attenuation box %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Attenuation box is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "AttenuationBox")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the network simulator
            if eqt_model == "AGILENT_L4491A":
                self.get_logger().debug("Create Agilent L4491A")
                # @UnresolvedImport
                from acs_test_scripts.Equipment.AttBox.AgilentL4491A.AgilentL4491A import AgilentL4491A

                eqt = AgilentL4491A(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown attenuation box model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=attenuation_box".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Switching matrix specific functions #
    #
    def get_switching_matrix(self, bench_name):
        """
        Gets the instance of a switching matrix
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: ISwitchingMatrix
        :return: the instance of the requested bench switching matrix
        """
        self.get_logger().debug("Get switching matrix %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Switching matrix is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "SwitchingMatrix")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the network simulator
            if eqt_model == "SEMI_AUTO":
                self.get_logger().debug("Create SemiAuto switching matrix")
                from acs_test_scripts.Equipment.SwitchingMatrix.SemiAuto.SemiAuto import SemiAuto  # @UnresolvedImport

                eqt = SemiAuto(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown switching matrix model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=switching_matrix".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_wired_headset(self, bench_name):
        """
        Gets the instance of an wired headset
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IWiredHeadset
        :return: the instance of the requested bench wired headset
        """
        self.get_logger().debug("Get wired headset %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Wired headset matrix is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "WiredHeadset")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            # Try to create the wired headset
            if eqt_model == "AkgK370":
                msg = "Create " + eqt_model
                self.get_logger().debug(msg)
                from acs_test_scripts.Equipment.Headset.WiredHeadset.WiredHeadset import WiredHeadset

                eqt = WiredHeadset(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown wired headset model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=wired_headset".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    #
    # Audio analyzers specific functions #
    #
    def get_audio_analyzer(self, bench_name):
        """
        Gets the instance of an audio analyzer
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IAudioAnalyzer
        :return: the instance of the requested bench audio analyzer
        """
        self.get_logger().debug("Get audio analyzer %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Audio analyzer matrix is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "AudioAnalyzer")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the network simulator
            if eqt_model == "RS_UPV":
                self.get_logger().debug("Create RS UPV audio analyzer")
                from acs_test_scripts.Equipment.AudioAnalyzer.RsUpv.RsUpv import RsUpv

                eqt = RsUpv(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "APx585":
                self.get_logger().debug("Create APx585 audio analyzer")
                from acs_test_scripts.Equipment.AudioAnalyzer.APx585.APx585 import APx585

                eqt = APx585(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown audio analyzer model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=audio_analyzer".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    #
    # VSWR tuners specific functions #
    #
    def get_tuner(self, bench_name):
        """
        Gets the instance of a VSWR tuner
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: IVSWRTuner
        :return: the instance of the requested bench VSWR tuner
        """
        self.get_logger().debug("Get tuner %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "VSWR Tuner is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "VSWRTuner")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the network simulator
            if eqt_model == "MT982EU30":
                self.get_logger().debug("Create MT892EU30 VSWR tuner")
                from acs_test_scripts.Equipment.Tuners.MT982EU30.MT982EU30 import MT982EU30  # @UnresolvedImport

                eqt = MT982EU30(bench_name, eqt_model, eqt_dic, bench_dic)
            elif eqt_model == "VirtualTuner":
                self.get_logger().debug("Create virtual VSWR tuner")
                from acs_test_scripts.Equipment.Tuners.Virtual.VirtualTuner import VirtualTuner  # @UnresolvedImport

                eqt = VirtualTuner(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown VSWR tuner model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=tuner".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def get_logic_analyzer(self, bench_name):
        """
        Gets the instance of Logic Analyzer.
        :type bench_name: str
        :param bench_name: the bench configuration name of the BT mouse.
        :rtype: LogicAnalyzer
        :return: the instance of the requested Logic Analyzer.
        """
        self.get_logger().debug("Get Logic Analyzer %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Logic Analyzer is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "LogicAnalyzer")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the Logic Analyzer
            if eqt_model == "SALEAE_LOGIC16":
                self.get_logger().debug("Create SALEAE_LOGIC16 Logic Analyzer")
                from acs_test_scripts.Equipment.LogicAnalyzer.SaleaeLogic16.SaleaeLogic16 import SaleaeLogic16  # NOQA
                eqt = SaleaeLogic16(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown Logic Analyzer model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

        # Register new equipment in equipments dictionary
        self.__equipment_instances[bench_name] = eqt

        # initialize equipment
        eqt.init()

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=LogicAnalyzer".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    def configure_equipments(self, filename, criteria=None, directory=None):
        """
        Thanks to an equipment configuration file, the equipment manager
        configures equipment(s).

        :type filename: str
        :param filename: Equipment configuration Filename (without the extension)
        :type criteria: dict
        :param criteria: Dictionnary in which key refers to  an xml parameter,
         and value refers to xml parameter's value. Only commands that match
         all criteria will be retrieved and executed.
        :type directory: str
        :param directory: Equipment configuration directory

        :rtype: tuple
        :return: return code and output message to notify
        that commands have been executed or not
        """
        get_eqt = {
            "cellular": self.get_cellular_network_simulator,
            "wlan": self.get_wlan_network_simulator,
            "power": self.get_power_supply,
            "bluetooth": self.get_bluetooth_network_simulator}
        # instantiate equipment configuration manager
        eqt_config_mngr = _EquipmentConfigManager()
        # retrieve data from xml file
        eqt_config_mngr.retrieve_configuration(filename, criteria, directory)
        # retrieve equipment name which will be used
        eqt_name_list = eqt_config_mngr.get_equipment_handled()
        eqt_dict = {}
        # instantiate equipment
        for eqt_name in eqt_name_list:
            eqt_type = self.__get_equipment_type(eqt_name)
            eqt_dict[eqt_name] = \
                get_eqt[eqt_type](eqt_name)

        # connect to all equipment that will be configured
        for name in eqt_dict.keys():
            eqt_dict[name].init()
        # execute gpib sequence
        return eqt_config_mngr.run_sequence(eqt_dict)

    #
    # Temperature Chamber specific functions #
    #

    def get_temperature_chamber(self, bench_name):
        """
        Gets the temperature chamber equipment

        :type bench_name: str
        :param bench_name: the bench configuration name of the temperature chamber

        :rtype: TemperatureChamber
        :return: the instance of the requested temperature chamber
        """
        controller = None
        self.get_logger().debug("Get temperature chamber %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Temperature chamber is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "TemperatureChamber")

        eqt_controller = bench_dic.get_param_value("Controller")
        if eqt_controller is not None:
            controller = self.get_controller(eqt_controller)

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            if eqt_model == "TMT80":
                self.get_logger().debug("Create " + eqt_model)
                from acs_test_scripts.Equipment.TemperatureChamber.TMT80.TMT80 import TMT80

                eqt = TMT80(bench_name, eqt_model, eqt_dic, bench_dic, controller)
            else:
                msg = "Unknown temperature chamber model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=temperature_chamber".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Controller specific functions #
    #

    def get_controller(self, bench_name):
        """
        Gets the controller equipment

        :type bench_name: str
        :param bench_name: the bench configuration name of the controller

        :rtype: Controller
        :return: the instance of the requested controller
        """
        self.get_logger().debug("Get controller %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Controller is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "Controller")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            if eqt_model == "EUROTHERM2204E":
                self.get_logger().debug("Create " + eqt_model)
                from acs_test_scripts.Equipment.Controller.Eurotherm2204e.Eurotherm2204e import Eurotherm2204e

                eqt = Eurotherm2204e(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown Controller model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=controller".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # Thermal camera specific function #
    #
    def get_thermal_camera(self, bench_name):
        """
        Gets the thermal camera equipment

        :type bench_name: str
        :param bench_name: the bench configuration name of this equipment

        :rtype: ThermalCamera
        :return: the instance of the requested equipment
        """

        self.get_logger().debug("Get thermal camera %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "Thermal camera is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "ThermalCamera")
        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            if eqt_model == "FLIRA305sc":
                self.get_logger().debug("Create " + eqt_model)
                from acs_test_scripts.Equipment.ThermalCamera.FLIR.FLIRA305sc.FLIRA305sc import FLIRA305sc
                eqt = FLIRA305sc(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown thermal camera model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=thermal_camera".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # NFC robot specific functions  #
    #
    def get_nfc_robot(self, bench_name):
        """
        Gets the instance of a NFC robot
        :type bench_name: str
        :param bench_name: the bench name of the equipment
        :rtype: INFCRobot
        :return: the instance of the requested bench NFC robot
        """
        self.get_logger().debug("Get NFC robot %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "NFCRobot is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "NFCRobot")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the NFC robot
            if eqt_model == "MICROBOT":
                self.get_logger().debug("Create MICROBOT")
                from acs_test_scripts.Equipment.Robot.NFC.Microbot.Microbot import Microbot

                eqt = Microbot(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown NFC robot model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=nfc_robot".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # NFC tool specific functions  #
    #
    def get_nfc_tool(self, bench_name):
        """
        Gets the instance of a NFC tool

        :type bench_name: str
        :param bench_name: the bench name of the equipment

        :rtype: INFCTools
        :return: the instance of the requested bench NFC robot
        """
        self.get_logger().debug("Get NFC tool %s", bench_name)
        # Check that eqt_bench_name is in bench configuration and get
        # bench dictionary
        bench_dic = \
            self.get_global_config().benchConfig.get_parameters(bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt_model = bench_dic.get_param_value("Model")
        if not eqt_model:
            msg = "NFCTool is not configured in your bench config."
            self.get_logger().error(msg)
            raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

        eqt_dic = self.__get_equipment_type_dic(eqt_model, "NFCTool")

        # Check if equipment already exists or not
        # and return the existing one if any
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:  # Try to create the NFC tool
            if eqt_model == "GPSHELL":
                self.get_logger().debug("Create GPSHELL")
                from acs_test_scripts.Equipment.NFCTools.Gpshell.Gpshell import Gpshell

                eqt = Gpshell(bench_name, eqt_model, eqt_dic)
            elif eqt_model == "NFC_EMULATOR":
                self.get_logger().debug("Create NFC_EMULATOR")
                from acs_test_scripts.Equipment.NFCTools.NfcEmulator.NfcEmulator import NfcEmulator

                eqt = NfcEmulator(bench_name, eqt_model, eqt_dic)
            elif eqt_model == "MP_MANAGER":
                self.get_logger().debug("Create MP_MANAGER")
                from acs_test_scripts.Equipment.NFCTools.MPManager.MPManager import MPManager

                eqt = MPManager(bench_name, eqt_model, eqt_dic, bench_dic)
            else:
                msg = "Unknown NFC tool model: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipments dictionary
            self.__equipment_instances[bench_name] = eqt

        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=nfc_tool".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return weakref.proxy(eqt)

    #
    # PowerAnalyzerTool robot specific functions  #
    #
    def get_power_analyzer_tool(self, bench_name):
        """
        Get the Power analyzer tool equipment
        :type bench_name: str
        :param bench_name: the bench configuration name of the power analyzer tool
        :rtype: PowerAnalyzerTool
        :return: the instance of the requested power analyzer equipment
        """
        self.get_logger().debug("Get power analyzer tool equipment %s", bench_name)

        # Look for equipment in equipment catalog and get equipment type catalog
        # Looks for equipment model in IOCard section
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            # Try to create the PAT equipment
            # Check that bench_name is in bench configuration and get
            # bench dictionary
            bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)
            eqt_model = bench_dic.get_param_value("Model")

            eqt_dic = self.__get_equipment_type_dic(eqt_model, "PowerAnalyzerTool")

            if not eqt_model:
                msg = "Power analyzer tool is not configured in your bench config."
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

            if eqt_model in ["NIDAQ", "STUB"]:
                self.get_logger().debug("Create PowerAnalyzerTool")
                from acs_test_scripts.Equipment.PowerAnalyzerTool.PowerAnalyzerTool import PowerAnalyzerTool

                eqt = PowerAnalyzerTool(bench_name, eqt_model, eqt_dic)

                conf_file = bench_dic.get_param_value("ConfFile", "")
                if conf_file != "":
                    exec_path = Paths.EXECUTION_CONFIG
                    config_file = os.path.join(os.getcwd(), exec_path, conf_file)
                    eqt.init(config_file)
            else:
                msg = "Unknown power analyzer tool: " + eqt_model
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipment catalog
            self.__equipment_instances[bench_name] = eqt

        if eqt is not None:
            LOGGER_EQT_STATS.info(
                "Create equipment={0};type=power_analyzer_tool".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
            return weakref.proxy(eqt)

    def get_usb_hub(self, bench_name):
        """
        Instantiate a USB hub equipment of type USBHub
        :param bench_name: he bench configuration name of the equipment
        :return: equipment instance object
        """
        eqt = self.__instantiate_equipment(bench_name, "USBHub")
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=usb_hub".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_serial_com_port(self, bench_name):
        """
        Instantiate a serial interface with an auxiliary device
        :type bench_name: str
        :param bench_name: the bench configuration name of the equipment instance
        :rtype: SerialCommInterface
        :return: the instance of the requested serial communication equipment
        """
        eqt = self.__instantiate_equipment(bench_name, "SerialCommInterface")
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=device_serial".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def get_stm32f4(self, bench_name):
        """
        This method returns an Equipment of type STM32Fxx
        :param bench_name: the bench configuration name

        :rtype: STM32F4xx
        :return: the instance of the requested equipment
        """
        eqt = self.__instantiate_equipment(bench_name, "STM32Fxx")
        LOGGER_EQT_STATS.info(
            "Create equipment={0};type=device_serial".format(inspect.getmodule(eqt).__name__.split(".")[-1]))
        return eqt

    def __instantiate_equipment(self, bench_name, equipment_type, default_model=None):
        """
        Intantiate equipment according to its type and bench name
        :type bench_name: str
        :param bench_name: the bench configuration name

        :type equipment_type: str
        :param equipment_type: the type of the equipment

        :type default_model: str
        :param default_model: the default model to select if no model specified for this equipment

        :rtype: Equipment object
        :return: the instance of the requested equipment
        """
        self.get_logger().debug("Get %s/%s instance" % (equipment_type, bench_name))

        # Look for equipment in equipment catalog and get equipment type catalog
        eqt = self.get_equipment(bench_name)
        if eqt is not None:
            msg = bench_name + " already exists, return existing instance"
            self.get_logger().debug(msg)
        else:
            # Check that bench_name is in bench configuration and get
            # bench dictionary
            try:
                bench_dic = self.get_global_config().benchConfig.get_parameters(bench_name)
            except AcsConfigException:
                msg = "No %s/%s found in your bench config" % (equipment_type, bench_name)
                raise AcsConfigException(AcsConfigException.PROHIBITIVE_BEHAVIOR, msg)
            eqt_model = bench_dic.get_param_value("Model", default_model)

            eqt_dic = self.__get_equipment_type_dic(eqt_model, equipment_type)

            if not eqt_model:
                msg = "%s is not configured in your bench config." % equipment_type
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.INVALID_BENCH_CONFIG, msg)

            if eqt_model in eqt_dic:
                class_str = "Equipment.%s.%s.%s.%s" % (equipment_type, eqt_model, eqt_model, eqt_model)
                eqt_class = get_class(class_str)
                eqt = eqt_class(bench_name, eqt_model, eqt_dic, bench_dic)
                eqt.init()
            else:
                msg = "Unknown %s:%s" % (equipment_type, eqt_model)
                self.get_logger().error(msg)
                raise AcsConfigException(AcsConfigException.UNKNOWN_EQT, msg)

            # Register new equipment in equipment catalog
            self.__equipment_instances[bench_name] = eqt

        if eqt is not None:
            return weakref.proxy(eqt)

    def __get_equipment_type(self, equipment_name):
        """
        Returns the simulator type thanks to the simulator
        name.

        :type equipment_name: str
        :param equipment_name: equipment name.

        :rtype: str
        :return: Type of the simulator:
            - I{cellular} : cellular newtork simulator
            - I{wlan} : wifi/wlan simulator
            - I{power} : power supply
            - I{bluetooth} : bluetooth simulator
        """
        eqt_name = str(equipment_name)
        if eqt_name.find("NETWORK_SIMULATOR") != -1:
            return "cellular"
        elif eqt_name.find("WLAN_NETWORK_SIMULATOR") != -1:
            return "wlan"
        elif eqt_name.find("POWER_SUPPLY") != -1:
            return "power"
        elif eqt_name.find("BT_NETWORK_SIMULATOR") != -1:
            return "bluetooth"
        else:
            msg = "Unknown simulator in equipment configuration: " + eqt_name
            raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, msg)

    def initialize(self):
        """
            Initialize equipments used by DeviceModel
        """
        # FIXME this func should not be called as getting equipments is done by DeviceController
        self.get_io_cards()
        self.get_power_supplies()
        self.get_usb_hubs()
        self.get_keyboard_emulators()


class _EquipmentConfigManager:
    """
    Class managing equipment configuration
    """

    def __init__(self):
        """
        Constructor
        """
        self.__data = []

    def retrieve_configuration(self, filename, criteria=None, directory=None):
        """
        Retrieve equipment configuration from file.

        :type filename: str
        :param filename: Equipment configuration Filename (without the extension)

        :type criteria: dict
        :param criteria: Dictionary in which key refers to an xml parameter, and value refers to xml parameter's value.

        .. important:: Only commands that match all criteria will be retrieved.

        :type directory: str
        :param directory: Equipment configuration directory

        :rtype: None
        :return: None

        """
        reader = None
        if directory is None:
            reader = _EquipmentConfigFileReader(filename)
        else:
            reader = _EquipmentConfigFileReader(filename, directory)
        reader.retrieve_configuration(self, criteria)

    def add_command(self, eqt_name, command):
        """
        Add a gpib command to this equipment configuration.

        :type eqt_name: str
        :param eqt_name: name of the equipment
        (corresponding to the equipment name in the bench config).

        :type command: str
        :param command: str representing a complete gpib command.

        :return: None

        """
        self.__data.append((eqt_name, command))

    def get_equipment_handled(self):
        """
        Returns the list of all equipment which will be configured.

        :rtype: list
        :return: List of all equipment name retrieved from the equipment configuration file.

        """
        eqt_list = []
        for command in self.__data:
            eqt_name = command[0]
            if eqt_name not in eqt_list:
                eqt_list.append(eqt_name)
        return eqt_list

    def run_sequence(self, equipment_dict):
        """
        Run the sequence of GPIB command thanks to the equipment manager.

        :type equipment_dict: dict
        :param equipment_dict: Dictionary containing all equipment instance that will be used.
            Key refers to equipment name.

        :rtype: tuple
        :return: return code and output message

        """

        # Check if gpib command list is not empty
        if not self.__data:
            return Global.FAILURE, "No GPIB command found !"

        # create a dictionary in order to automatically
        # retrieve the equipment from the equipment manager
        for data in self.__data:
            # retrieve equipment name, type and the
            # command to execute
            eqt_name = data[0]
            cmd = data[1]
            # retrieve the good instance of simulator
            if eqt_name in equipment_dict:
                eqt = equipment_dict[eqt_name]
            else:
                raise TestEquipmentException(
                    TestEquipmentException.UNKNOWN_EQT,
                    "Unknown equipment: " + eqt_name)
            # send command
            eqt.send_command(cmd)

        return Global.SUCCESS, "No errors"


class _EquipmentConfigFileReader:
    """
    Class retrieving data from equipment configuration file.
    """

    class FileHandler(ContentHandler):

        def __init__(self, eqt_mgmt, criteria):
            ContentHandler.__init__(self)
            self.__data = eqt_mgmt
            self.__criteria = criteria

        def startElement(self, name, attrs):
            """
            This method is overwriting the startElement's method
            from ContentHandler's class.
            """
            if name == "GPIBCommand":
                eqt_attr = attrs.getValue("equipment")
                cmd_attr = attrs.getValue("command")
                criteria_match = True
                for criterion in self.__criteria.keys():
                    value = str(self.__criteria[criterion])
                    if criterion in attrs:
                        retrieved_value = attrs.getValue(criterion)
                    else:
                        raise TestEquipmentException(
                            TestEquipmentException.INVALID_PARAMETER,
                            "Xml parameter %s not defined" % criterion)
                    if value != retrieved_value:
                        criteria_match = False
                        break
                if criteria_match:
                    self.__data.add_command(eqt_attr, cmd_attr)

        def get_retrieved_data(self):
            """
            Returns data after having parsed the xml limits file.

            :rtype: EquipmentConfigMgmt
            :return: Object containing equipment configuration data.
            """
            return self.__data

    # end of inner class: FileHandler

    EQUIPMENT_CONF = os.path.join(Paths.CONFIGS, "EquipmentConfiguration")

    def __init__(self, filename, directory=EQUIPMENT_CONF):
        """
        Constructor

        :type filename: str
        :param filename: file name without extension
        of an equipment configuration file.
        """

        self.__filename = filename
        self.__directory = directory
        self.__data = None

    def retrieve_configuration(self, eqt_mgmt, criteria=None):
        """
        Retrieves equipment configuration from test conditions filename,
        and store retrieved values in an instance of C{EquipmentConfigMgmt}.

        :type eqt_mgmt: EquipmentConfigMgmt
        :param eqt_mgmt: instance of EquipmentConfigMgmt

        :type criteria: dict
        :param criteria: Dictionnary in which key refers to  an xml parameter,
         and value refers to xml parameter's value. Only commands that match
         all criteria will be retrieved.

        :return: None
        """
        try:
            _criteria = criteria
            if criteria is None:
                _criteria = {}
            handler = _EquipmentConfigFileReader.FileHandler(eqt_mgmt, _criteria)
            directory = "."
            if self.__directory is not None:
                directory = os.path.join(".", self.__directory)
            file_to_parse = os.path.join(directory, self.__filename + ".xml")
            sax.parse(file_to_parse, handler)
        except IOError:
            raise TestEquipmentException(
                TestEquipmentException.INVALID_PARAMETER,
                "Unknown equipment configuration file: " + file_to_parse)
        except TestEquipmentException as excp:
            raise TestEquipmentException(
                TestEquipmentException.DEFAULT_ERROR_CODE,
                excp.get_error_message() + " in file " + self.__filename)
