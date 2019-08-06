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


class Global(object):

    """Global return value"""
    SUCCESS = 0
    FAILURE = -1


def get_class(kls):
    """
    Load class from module path

    :type   kls: string
    :param  kls: module + class path

    :rtype:     class instance
    :return:    Instance of the class
    """

    parts = kls.split('.')
    module_path = ".".join(parts[:-1])
    module = __import__(module_path, fromlist=[])
    for comp in parts[1:]:
        module = getattr(module, comp)
    return module
