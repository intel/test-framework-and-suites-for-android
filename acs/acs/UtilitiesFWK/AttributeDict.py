#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


from acs.Core.Report.ACSLogging import LOGGER_FWK
from acs.UtilitiesFWK.Utilities import str_to_bool, str_to_dict


class AttributeDict(dict):

    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::

        >>> m = AttributeDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key, default_value=None, default_cast_type=str):
        """
        Return the value of the given device config name
        The type of the value can be checked before assignment
        A default value can be given in case the config name does not exist

        :type key: string
        :param key: name of the property value to retrieve

        :type default_value: object
        :param default_value: default_value of the property

        :type default_cast_type: type object
        :param default_cast_type: type to cast (int, str, list ...)
        By default cast into str type.

        :rtype: string or type of default_cast_type
        :return: config value
        """
        value = self.get(key, default_value)

        # In case the config value is not None, trying to cast the value
        if value is not None:
            # Cast the value to the given type
            # Stripping is done to suppress end and start spaces of values
            try:
                if default_cast_type == "str_to_bool":
                    value = str_to_bool(str(value).strip())
                elif default_cast_type == "str_to_dict":
                    value = str_to_dict(str(value))
                else:
                    value = default_cast_type(value)
            except ValueError:
                LOGGER_FWK.debug("Cannot convert {0} to {1}, return {2}".format(key, default_cast_type, default_value))
                value = default_value

        # Store new value
        # TODO: do not store the value for now because of side effects, need to see if it's expected behavior
        # self[key] = value
        return value
