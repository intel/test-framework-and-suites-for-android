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
:summary: Manager callable everywhere, storing and updating device properties
:since: 30/10/2012
:author: dgonza4x
"""


class DevicePropertiesManager(object):

    """
    DevicePropertiesManager class:
    Manager callable everywhere, storing and updating device properties.
    Give to output files (Campaign result, device_info.xml) needed data.

    The singleton instance
    """
    __instance = None

    """
    Device properties storage
    """
    __prop = {}

    def __new__(cls):
        """
        Constructor that always returns the same instance of DevicePropertiesManager
        """

        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def update_or_store_property(self, key, value):
        """
        Update or store a device property and its associated value,
        if it's different from None.
        To be used if you are sure that the property has been correctly
        retrieved.

        :param key: property's name (can't be an empty string or None)
        :type key: str

        :param value: property's value
        :type value: object

        :rtype: boolean
        :return: True if value as been stored or updated, False otherwise
        """
        if value is None or key is None or len(key) == 0:
            return False

        self.__prop[key] = value
        return True

    def update_or_store_properties(self, properties):
        """
        Update or store a set of device properties and its associated
        values.
        To be used if you are sure that the properties have been correctly
        retrieved.

        :param properties: set of properties and their associated values
        :type properties: dict

        :return: None
        """
        for key in properties.keys():
            self.update_or_store_property(key, properties.get(key))

    def is_properties_stored(self, property_names, value_not_empty=False):
        """
        Check is the set of properties have been already stored.
        Each property not stored will be returned as a list.

        :param property_names: set of property's name
        :type property_names: list

        :param value_not_empty: optionnal parameter, used for testing that stored
        value is different from empty string
        :type value_not_empty: boolean

        :rtype: list
        :return: list of properties not stored in DevicePropertiesManager.
        """
        result = []
        if isinstance(property_names, list):
            for key in property_names:
                if not (key in self.__prop):
                    if(value_not_empty is False or
                       value_not_empty and self.__prop[key] not in ["", None]):
                        result.append(key)
        return result

    def get_properties(self, property_names):
        """
        Retrieve property values from given list of property name.

        :param property_names: list of property names
        :type property_names: list

        :rtype: dict
        :return: Associated value for each property.
        Each property not stored in DevicePropertiesManager will have their value set to None.
        Returns None if input param is incorrect.
        """
        result = {}
        if isinstance(property_names, list):
            for key in property_names:
                if key is not None and key != "":
                    result[key] = self.__prop.get(key, None)
        return result

    def get_all_properties(self):
        """
        Retrieve all properties stored in DavicePropertiesManager.

        :rtype: dict
        :return: properties name and their associated values.
        """
        return self.__prop
