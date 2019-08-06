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

import sys


def open_inheritance_hack():
    # pylint: disable=R0903
    """

    In case of windows mark the file handle as non - inheritable to avoid process error
    Found this topics, to resolve the error :
        WindowsError: [Error 32] The process cannot access the file because it is being used by another process
    http://www.virtualroadside.com/blog/index.php/2013/02/06/problems-with-file-descriptors-being-inherited-by-default-in-python/
    http://stackoverflow.com/questions/11181519/python-whats-the-difference-between-builtin-and-builtins

    @return:
    """
    if sys.platform == 'win32':
        import __builtin__
        from ctypes import windll
        # pylint: disable=import-error
        import msvcrt

        __builtin__open = __builtin__.open

        def __open_inheritance_hack(*args, **kwargs):
            result = __builtin__open(*args, **kwargs)
            handle = msvcrt.get_osfhandle(result.fileno())  # @UndefinedVariable
            windll.kernel32.SetHandleInformation(handle, 1, 0)  # @UndefinedVariable
            return result

        __builtin__.open = __open_inheritance_hack
