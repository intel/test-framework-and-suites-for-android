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

from uuid import UUID


def is_uuid4(val):
    """
    Check that string is a uuid4
    :param val: value to be checked
    :type: val: str or uuid object

    >>> is_uuid4(None)
    False
    >>> is_uuid4("non_uuid")
    False
    >>> is_uuid4(uuid.uuid1())
    False
    >>> is_uuid4(uuid.uuid4().hex)
    True
    >>> is_uuid4(str(uuid.uuid4()))
    True
    >>> is_uuid4(uuid.uuid4())
    True
    """

    if val is None:
        return False

    try:
        if isinstance(val, UUID):
            val = val.hex
        uuid_to_test = UUID(val, version=4)
    except ValueError:
        status = False
    else:
        status = (str(uuid_to_test) == val or uuid_to_test.hex == val)

    return status


if __name__ == "__main__":
    import doctest
    doctest.testmod()
