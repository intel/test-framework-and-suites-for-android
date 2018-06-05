#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Design pattern implementation
"""


class Singleton(object):

    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Other than that, there are
    no restrictions that apply to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    Limitations: The decorated class cannot be inherited from.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        if not hasattr(self, '_instance'):
            self._instance = self._decorated()
        return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


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
