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


class Singleton(object):

    """
    class decorator for singleton.

    Usage:
    - use `.instance()' method to get singleton instance of the class
    - directly using `cls()` is forbidden, `TypeError` will raise

    Cautions:
    - instance class only call `__init__(self)` without any other arguments
    - can not inherit from decorated class

    """

    def __init__(self, clss):
        self._cls = clss

    def __call__(self):
        raise TypeError('Singleton should use \'instance()\' to get instance.')

    def __instancecheck__(self, instance):
        return isinstance(instance, self._cls)

    def instance(self):
        """
        Returns the singleton instance.
        """
        if not hasattr(self, '_instance'):
            self._instance = self._cls()
        return self._instance


class Cancel(object):

    """
    A class used to cancel operations
    """

    def __init__(self, callback=None):
        """
        :param callback: a method to call once cancel operation is done
        """
        self.__cancel = False
        self.__callback = callback

    @property
    def callback(self):
        return self.__callback

    @property
    def is_canceled(self):
        return self.__cancel

    def cancel(self):
        self.__cancel = True
