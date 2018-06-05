#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@copyright: (c)Copyright 2015, Intel Corporation All Rights Reserved.
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
@summary: All that concern uuid
@since: 9/29/2015
@author: cbonnard
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
