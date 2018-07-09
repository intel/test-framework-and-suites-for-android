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
:summary: This module handle XML file transformation

"""
import sys
import os
import fnmatch
import traceback
import lib

try:
    from lxml import etree
except ImportError:
    from xml import etree

from acs.Core.PathManager import Paths

# Avoid to access directly the protected Class (etree._ElementTree)
# using factory instead
PublicElementTree = type(etree.ElementTree())
PublicElement = type(etree.Element('ElementType'))


class BenchConfigInvalid(etree.DocumentInvalid):
    """
    Custom Exception

    """

    def __init__(self, error, filename=None, verbose=0):
        super(BenchConfigInvalid, self).__init__(error)

        self.filename = filename
        self.verbose = verbose

    def __unicode__(self):
        uni = ur'{0}'.format(self.filename)
        if self.verbose == 1:
            uni = ur'{0}\nError : {1}'.format(uni, self.message)
        elif self.verbose == 2:
            uni = ur'{0}\nError : {1}\nTraceback :\n{2}'.format(uni, self.message, traceback.format_exc())
        return uni

    __str__ = __repr__ = __unicode__


class BadNodeFoundError(BenchConfigInvalid):
    """
    Custom Exception

    """

    def __init__(self, error, filename=None, node=None, verbose=1):
        super(BadNodeFoundError, self).__init__(error, filename=filename, verbose=verbose)

        self.node = node

    def __unicode__(self):
        uni = super(BadNodeFoundError, self).__unicode__()
        uni = ur'{0} node found !\n{1}'.format(self.node.tag
                                               if self.node is not None and hasattr(self.node, 'tag')
                                               else "", uni)
        return uni


class ElementTreeTransformation(lib.PartialTransformation, PublicElementTree):

    """
    An XML element tree node which format the BenchConfig.xml file
    `//Phone//Parameter` nodes properly.

    .. note:: Each `Parameter` node in the `Phone` node which are of the form :

        .. code-block:: xml

            <Parameter name="bootTimeout" value="100" />

        **becomes**,

        .. code-block:: xml

            <Parameter bootTimeout="100" />

        .. important:: if a description attribute is present **it's kept as is**

        .. code-block:: xml

            <Parameter DeviceModel="SALTBAY_64-Android-LLP"
                       description="Device model is compulsory to execute ACS in multi mode" />

    """
    # The xmlns:xsi & xsi:noNamespaceSchemaLocation root attributes key name.
    XSD_XSI_ATTR = '{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation'

    @staticmethod
    def attributes2parameters(node, node_tag='Phone', tag='Parameter',
                              allowed=('name', 'description', 'devicemodel')):
        """
        Converts all non-allowed node's attribute(s) into Whatever(Parameter) node(s)

        :param node: A Phone node (<Phone> ... </Phone>)
        :type node: etree._Element

        """
        if node.tag != node_tag:
            raise etree.Error('[COLLECT PARENT ATTR ERROR] : {0}'.format(etree.tostring(node)))

        attrs = node.attrib
        for key, value in dict(attrs).iteritems():
            lowered = str(key).lower()
            if lowered not in allowed:
                # Adding a Parameter node with its attributes to be put into node body
                node.append(etree.Element(_tag=tag, attrib={key: value}))
                # Deleting undesired attributes for this node
                del attrs[key]

    @staticmethod
    def correct_misused_parameters(phone_node, param, looked_for=None):
        """
        Corrects all misused Parameter(s)

        :param phone_node: The XML Phone node (Parameter's parent)
        :type phone_node: etree.Element

        :param param: The Parameter node
        :type param: etree.Element

        :param looked_for: What to look for as a list
        :type looked_for: tuple

        """
        looked_for = looked_for or ('deviceModel', 'DeviceModel',)
        # Looking for misused Parameter node
        for looked in looked_for:
            if looked in param.attrib:
                # Setting the deviceModel attribute to the Phone node
                phone_node.attrib['deviceModel'] = param.get(looked)
                # Removing the Parameter node from Phone node
                phone_node.remove(param)

    @staticmethod
    def correct_typo_parameters(param, typos=None):
        """
        Corrects all typos in Parameters

        :param param: The Parameter node
        :type param: etree.Element

        :param typos: What typo to seek for as a list
        :type typos: tuple

        """
        typos = typos or (
            ('PhoneNumber', 'phoneNumber'),
            ('retrieveSerailTrace', 'retrieveSerialTrace'),
            ('serialHwFlowControl', 'serialHdwFlowControl')
        )
        # Looking for typos in Parameter node's attributes
        for data in typos:
            typo, correction = data
            if typo in param.attrib:
                # Setting the `correction` attribute name to the ¨Parameter node
                param.attrib[correction] = param.get(typo)
                # Removing the typo attribute from Parameter node
                del param.attrib[typo]

    @staticmethod
    def removed_unused_parameters(phone_node, param, to_delete=None):
        """
        Removes all unused Parameter node(s)

        :param param: The Parameter node
        :type param: etree.Element

        :param to_delete: A list of keys which are to be removed
        :type to_delete: tuple

        """
        to_delete = to_delete or (
            'PowerSupply',
            'ProvisioningMode',
            'powerCycleOnFailure',
            'EnableReflash',
            'adbRootTimeToWait',
            'retrieveAPLog',
            'useHardShutdown',
            'useSoftShutdown',
            'cleanDeviceCrashLog',
        )
        # Deleting unused Parameter nodes
        for delete in to_delete:
            for key in param.attrib:
                # If match
                if lib.strip(delete).lower() == lib.strip(key).lower():
                    # Removing the Parameter node from Phone node
                    phone_node.remove(param)

    @property
    def valid(self):
        """
        Property holding whether the self node is valid or not

        :return: Whether the self node is valid
        :rtype: bool

        """
        root = self.getroot()
        valid = root.tag == self._pattern
        return valid

    def __init__(self, **kwargs):
        """
        Constructor

        :param args: any non-keyword argument
        :type args: tuple

        :param kwargs: any keyword argument (options)
        :type kwargs: dict

        """
        super(ElementTreeTransformation, self).__init__(**kwargs)
        self._write_options = dict(encoding='iso-8859-1', pretty_print=True, xml_declaration=True)
        self._pattern = kwargs.pop('pattern')

        # Parsing the XML file
        self.parse(self._pathname)

    def transform(self, *args, **options):
        """
        Formatting behavior implementation

        :param args: any non-keyword argument
        :type args: tuple

        :param options: any keyword argument (options)
        :type options: dict

        """
        modified = False
        # Iterating over all Phone node(s)
        for phone_node in self.findall('//Phone'):
            if not modified:
                modified = True

            # Converting bad types into proper XML ones
            for param in list(phone_node):

                if not isinstance(param, PublicElement):
                    continue

                if param.tag == 'DeviceModel':
                    raise BadNodeFoundError('', filename=self._pathname, node=param)

                # Converting all bad Parameter node(s) into expected ones
                lib.transform_node_attributes(param.attrib)
                # Deleting unused Parameter nodes
                self.removed_unused_parameters(phone_node, param)
                # Looking for typos in Parameter node's attributes
                self.correct_typo_parameters(param)
                # Looking for misused Parameter node
                self.correct_misused_parameters(phone_node, param)

            # All attributes found in the Phone node not matching allowed ones
            # is/are converted into Parameter node(s) appended to the Phone node
            self.attributes2parameters(phone_node)

        if modified:
            # Indenting properly the root document before writing
            self.xml_indent(self.getroot())
            # Writing back formatted file
            self.write(self._pathname, **self._write_options)


class XMLTransformation(lib.PartialTransformation):

    """
    Wrapper class which takes the top-level folder.
    Recurse over files (matching XML pattern) calling an ElementTreeTransformation instance
    with provided arguments.

    """

    Element = ElementTreeTransformation

    def __init__(self, **kwargs):
        """
        Constructor

        :param args: any non-keyword argument
        :type args: tuple

        :param kwargs: any keyword argument (options)
        :type kwargs: dict

        """
        super(XMLTransformation, self).__init__(**kwargs)

        self._valid = []
        self._xml_error = []
        self._unknown_error = []
        self._xml_bad_nodes_error = []

    def report(self, total_count):
        """
        Reports

        :param total_count: The total element analyzed count
        :type total_count: int

        """
        (valid_count, xml_error_count,
         unknown_error_count, xml_bad_nodes_error) = (len(self._valid), len(self._xml_error),
                                                      len(self._unknown_error), len(self._xml_bad_nodes_error))
        matching_count = valid_count + xml_error_count

        self._logger.info('\nTotal Matching XML analyzed files : {0}/{1}'.format(matching_count, total_count))
        self._logger.info('Details below :')

        if self._valid:
            self._logger.info('\n\nTotal Valid XML analyzed files : {0}/{1}'.format(valid_count, matching_count))
            self._logger.info('Success XML files details below :\n\n')

        for valid in self._valid:
            self._logger.info('XML file ({0}) VALIDATED !'.format(valid.pathname))

        if self._xml_error:
            self._logger.error('\n\nTotal Invalid XML analyzed files : {0}/{1}'.format(xml_error_count, matching_count))
            self._logger.error('Errors details below :\n\n')

        for error in self._xml_error:
            self._logger.error('XML file ({filename}) error : {error}'.format(**error))

        if self._xml_bad_nodes_error:
            self._logger.error('\n\nTotal Invalid files for BAD NODES reasons : {0}/{1}'.format(xml_bad_nodes_error,
                                                                                                total_count))
            self._logger.error('BAD NODES Errors details below :\n\n')

        for error in self._xml_bad_nodes_error:
            self._logger.error(repr(error))

        if self._unknown_error:
            self._logger.error('\n\nTotal Invalid files for UNKNOWN reasons : {0}/{1}'.format(unknown_error_count,
                                                                                              total_count))
            self._logger.error('UNKNOWN Errors details below :\n\n')

        for error in self._unknown_error:
            self._logger.error('XML file ({filename}) error : {error}'.format(**error))

    def transform(self, *args, **options):
        """
        Formatting behavior implementation

        :param args: any non-keyword argument
        :type args: tuple

        :param options: any keyword argument (options)
        :type options: dict

        """
        total_count = 0
        for root, dirnames, filenames in os.walk(self._pathname):
            xml_files = [lib.absjoin(root, f) for f in fnmatch.filter(filenames, r'*.xml')]
            files_count = len(xml_files)
            total_count += files_count
            for idx in xrange(files_count):
                xml_file = xml_files[idx]
                try:
                    e_options = dict(
                        pathname=xml_file,
                        must_validate_schema=self._xsd_filename
                    )
                    e_options.update(options)
                    element = self.Element(**e_options)

                    if not element.valid:
                        continue

                    element.transform()

                    self._valid.append(element)
                except BadNodeFoundError as node_error:
                    self._xml_bad_nodes_error.append(node_error)
                except etree.DocumentInvalid as assert_error:
                    self._xml_error.append({'error': assert_error, 'filename': xml_file})
                except Exception as unhandled_error:
                    self._unknown_error.append({'error': unhandled_error, 'filename': xml_file})

        self.report(total_count)


def main(*args, **kwargs):
    """
    Entry point

    :param args: arguments
    :type args: tuple

    :param kwargs: Keyword arguments
    :type kwargs: dict

    :return: The execution status
    :rtype: int

    """
    execution_status = -1
    try:
        transformation = XMLTransformation(pathname=Paths.TEST_SUITES)
        transformation.transform(pattern='BenchConfig')
        execution_status = 0
    except Exception:
        # Raising back to get exception info
        execution_status = 1
        raise
    finally:
        return execution_status


# This should happen only if the script is called with an EXEC_SCRIPT TC
if 'SUCCESS' in globals():
    globals()['VERDICT'] = main()

# Standard call
elif __name__ == '__main__':
    sys.exit(main())
