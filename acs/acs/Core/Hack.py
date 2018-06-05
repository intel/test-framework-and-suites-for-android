"""

:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
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

:organization: INTEL MCG PSI
:summary: This file implements hacks unfortunately used in ACS
:author: cbresoli
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
