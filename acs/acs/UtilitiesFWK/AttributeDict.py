#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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

@organization: INTEL MCG PSI
@summary: This module implements AttributeDict class
@since: 4/3/14
@author: sfusilie
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
