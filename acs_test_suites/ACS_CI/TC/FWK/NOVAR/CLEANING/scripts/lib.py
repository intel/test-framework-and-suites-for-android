#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
__copyright__ = """
Copyright (C) 2017 Intel Corporation

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

"""
:summary: Groups Common behavior Classes

"""
import logging
import abc

from os import path

logging.basicConfig(level=logging.DEBUG)


def absjoin(*paths):
    """
    A combination of :func:`os.path.abspath` and :func:`os.path.join` in order to produce
    a joined and absolute path from the given parts (*paths)

    :param paths: Path's parts to be joined
    :type paths: tuple

    :return: A joined and absolute path from given parts
    :rtype: str

    """
    return path.abspath(path.join(*paths))


def strip(value):
    """
    little wrapper function

    """
    if value and isinstance(value, basestring):
        return str(value).strip()
    return value


def check_and_format_value(v):
    """
    Formats all Pythonic boolean value into XML ones

    """
    booleans = {'True': 'true', 'False': 'false'}
    clean = strip(v)
    if clean in booleans:
        return booleans.get(clean)
    return clean


def transform_node_attributes(attributes):
    """
    Format node attributes to match desired behavior.

    :param attributes: A set of attributes (key, value) pair
    :type attributes: dict

    """
    attributes = attributes or {}
    name, value, description = None, None, None
    if 'name' in attributes:
        name = strip(attributes.pop('name'))
    if 'value' in attributes:
        value = strip(attributes.pop('value'))
    if 'description' in attributes:
        description = strip(attributes.pop('description'))

    if name:
        attributes[name] = value if value is not None else ""

    if description:
        attributes['description'] = description

    # Converting all bad casting type (Python style instead of XML)
    copy = dict(attributes).copy()
    for key, value in copy.iteritems():
        attributes[key] = check_and_format_value(value)


class PartialTransformation(object):

    """
    Acts as a partial class
    Implement basic Formatting behavior

    **Must be realized by sub-classes**

    """

    __metaclass__ = abc.ABCMeta

    # Class attributes

    _logger = logging.getLogger('CI - CLEANING')

    def __getattribute__(self, name):
        """
        Generalized behavior to clean any real path found

        :param name: The attribute name
        :type name: str

        :return: The matching attribute's value
        :rtype: object

        :raise AttributeError: When attribute name does not match

        """
        attribute = super(PartialTransformation, self).__getattribute__(name)
        if isinstance(attribute, basestring) and path.exists(attribute):
            clean_path = attribute.replace('\\', '/').strip()
            return ur'{0}'.format(clean_path)
        return attribute

    @property
    def pathname(self):
        """
        Property holding the filename's element

        :return: The element filename
        :rtype: str

        """
        return self._pathname

    def __init__(self, **kwargs):
        """
        Constructor

        :param args: any non-keyword argument
        :type args: tuple

        :param kwargs: any keyword argument (options)
        :type kwargs: dict

        """
        self._pathname = kwargs.get('pathname')
        self._xsd_filename = kwargs.get('must_validate_schema')

    def xml_indent(self, elem, level=0, indent=4):
        """
        Used to write properly indented XML files

        """
        i = '\n' + level * (' ' * indent)
        if len(elem):
            if not elem.text or not strip(elem.text):
                elem.text = i + '  '
            if not elem.tail or not strip(elem.tail):
                elem.tail = i
            for elem in elem:
                self.xml_indent(elem, level + 1, indent)
            if not elem.tail or not strip(elem.tail):
                elem.tail = i
        else:
            if level and (not elem.tail or not strip(elem.tail)):
                elem.tail = i

    @abc.abstractmethod
    def transform(self, *args, **options):
        """
        Formatting behavior implementation

        .. warning:: Must be define/override in sub-classes

        :param args: any non-keyword argument
        :type args: tuple

        :param options: any keyword argument (options)
        :type options: dict

        """
