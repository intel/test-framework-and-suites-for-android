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
@summary: Utility method for parsing dict
@since: 07/08/14
@author: kturban
"""
from acs.ErrorHandling.AcsToolException import AcsToolException
from functools import reduce

UNSUPPORTED_XPATH_REQUEST = ['@', '[', ']', '=']


class ParsedElement(object):

    """
    Parsed element representation

    It converts a regular object (str, int, float, dict) as ParsedElement representation

    in case of str, int, float:
    tag and text attribute will contain the object value

    in case of dict:
    this class only handle dict with ONE key
    tag attribute will contains the main key
    text attribute will contains the value associated to the key
    """
    tag = ''
    text = ''
    attrib = {}

    def __init__(self, obj):
        if obj:
            if isinstance(obj, (str, int, float)):
                self.tag = obj
                self.text = obj
            # dict must content only content one key
            elif isinstance(obj, dict):
                error_msg = "Cannot convert {0} to ParsedElement object: too many keys!".format(obj)
                if len(obj.keys()) != 1:
                    raise AcsToolException(AcsToolException.INVALID_PARAMETER, error_msg)
                self.tag = obj.keys()[0]
                self.text = obj[self.tag]


def get_dict_value_from_path(dic, path, default_value=None):
    """
    Get a value in a dictionary, using given path.
    :param path: the path where the value is set in dic, as a list of keys
                 (ex: /key1/key2/key3 will search for dic['key1']['key2']['key3'] )
    :type  path: list
    :param dic: the dictionary to search value into
    :type  dic: dict
    :param default_value:
    :param default_value: object
    :return: value read from dic at path, or default_value if path does not exist in dic
    """
    def custom_get(obj, key):
        data = {}
        if not key or key == '*':
            data = obj
        else:
            try:
                data = obj.get(key)
                if data is None:
                    data = {}
            except AttributeError:
                # no get method for this object : ignore it
                pass
        return data
    if any([prohibited for prohibited in UNSUPPORTED_XPATH_REQUEST if prohibited in path]):
        raise AcsToolException('{0} xpath request is too complex to be handled by this parser'.format(path))
    path = path.replace('//', '/')
    # get all keys from path
    keys = path.split('/')
    value = reduce(custom_get, keys, dic)
    if value in ({}, None):
        value = default_value
    return value


def convert_as_list_of_elements(obj):
    """
    To get a list of LXML Element like object
    """
    list_of_elements = []
    if obj:
        if isinstance(obj, unicode):
            list_of_elements = [ParsedElement(str(obj))]
        elif isinstance(obj, (str, int, float)):
            list_of_elements = [ParsedElement(obj)]
        elif isinstance(obj, (list, tuple)):
            list_of_elements = [ParsedElement(x) for x in obj]
        elif isinstance(obj, dict):
            # each key is like a node
            # each key value is like text node
            list_of_elements = [ParsedElement({x: y}) for x, y in obj.items()]
    return list_of_elements


if __name__ == '__main__':
    print get_dict_value_from_path({'test': {'toto': 'value'}}, '//test')
    result = get_dict_value_from_path({'test': {'toto': 'value',
                                                'titi': {'akey': 'avalue'}}}, '/test')
    like_xml_list = convert_as_list_of_elements(result)
    for elmt in like_xml_list:
        print "tag {0}".format(elmt.tag)
        print "txt {0}".format(elmt.text)
        print "attrib {0}".format(elmt.attrib)

    print get_dict_value_from_path({'test': {'toto': 'value'}}, '/test/')
    print get_dict_value_from_path({'test': {'toto': 'value'}}, '/test/*')
    print get_dict_value_from_path({}, '/test')
    print get_dict_value_from_path({'test': {'toto': 'value'}}, '/test/toto')
    print get_dict_value_from_path({'test': {'toto': 'value'}}, '/test/toto/')
    print get_dict_value_from_path({'test': {'toto': 'value'}}, '/test/toto/*')
