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

from acs.UtilitiesFWK.Utilities import split_and_strip


class TestStepContext(object):

    """
    Implements test step context.
    A test step can read and write info in the context to share them with other
    test steps.

    .. uml::

        class TestStepContext {
            KEY_SEPARATOR = ":"
            get_info(key)
            get_nested_info(keys)
            set_info(key, info)
            set_nested_info(keys, info)
            del_info(key)
            add_infos(items)
            dict clone_dict(plus_items=None)
            ref_dict()
        }

    For example, a test step can retrieve some information (e.g. from a device) and
    save them in the context; another test step later, that needs that info, will
    retrieve it from the context and use it.
    """

    KEY_SEPARATOR = ":"

    def __init__(self, info=None):
        """
        Constructor

        :type info: dict
        :param info: initial set of context entries

        """
        if info is not None:
            self._objs = info
        else:
            self._objs = {}

    def get_info(self, key):
        """
        Returns the context info associated to key

        :type key: str
        :param key: the context info ID (it can be a complex key such as "key:subkey")

        :rtype: object
        :return: the data associated to key
        """
        keys = split_and_strip(key, self.KEY_SEPARATOR)
        return self.get_nested_info(keys)

    def get_nested_info(self, keys):
        """
        Retrieves the info from the context managing complex keys

        :type keys: list
        :param keys: list of nested keys

        :rtype: object
        :return: the data associated to keys
        """
        current_dict = self.ref_dict()
        for key in keys:
            value = current_dict[key] if key in current_dict else None
            if isinstance(value, dict):
                current_dict = value
        return value

    def set_info(self, key, info):
        """
        Set an info associated to key.
        If key doesn't exist in the collection a new item gets created.
        Otherwise the object associated to key gets updated

        :type key: str
        :param key: the context info ID (it can be a complex key such as "key:subkey")
        """
        keys = split_and_strip(key, self.KEY_SEPARATOR)
        self.set_nested_info(keys, info)

    def set_nested_info(self, keys, info):
        """
        Set an info associated to the keys seen as nested dictionaries.
        For example, if called like: set_nested_info(['a','b','c'], 100)
        if will create: {'a':{'b':{'c':100}}}

        :type keys: list
        :param keys: list of nested keys
        """
        current_dict = self.ref_dict()
        for key in keys[:-1]:
            value = current_dict[key] if key in current_dict else None
            if not value:
                current_dict[key] = {}
                current_dict = current_dict[key]
            else:
                current_dict = value
        # Get the last key in the keys list
        key = keys[len(keys) - 1]
        if isinstance(current_dict, dict):
            current_dict.update({key: info})

    def del_info(self, key):
        """
        Removes the item associated to key

        :type key: str
        :param key: the context info ID
        """
        if key in self._objs:
            del self._objs[key]

    def add_infos(self, items):
        """
        Adds the dictionary "item" into the context
        It doesn't directly affect the internal object.
        Instead it returns a new context object with the new added items
        """

        temp = dict(self._objs.items() + items.items())
        return TestStepContext(temp)

    def clone_dict(self, plus_items=None):
        """
        Returns a copy of the internal dictionary.
        If plus_items is not None it is added to the returned copy
        """
        if plus_items is not None:
            temp = dict(self._objs.items() + plus_items.items())
        else:
            temp = dict(self._objs)

        return temp

    def ref_dict(self):
        """
        Return a reference to the internal dictionary
        """

        return self._objs
