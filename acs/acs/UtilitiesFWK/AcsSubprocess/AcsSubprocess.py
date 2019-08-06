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

import sys
from AcsSubprocessBase import enqueue_output

# Non blocking readline
ON_POSIX = 'posix' in sys.builtin_module_names


enqueue_output = enqueue_output


class AcsSubprocess(object):

    """
    AcsSubprocess factory that will return windows or linux implementation
    """

    def __new__(cls, *args, **kwargs):
        """
        Constructor that will return proper implementation based on the OS
        """
        if ON_POSIX:
            # Load linux subprocess execution module
            from AcsSubprocessLin import AcsSubprocessLin as subprocess_engine
        else:
            # Load windows subprocess execution module
            from AcsSubprocessWin import AcsSubprocessWin as subprocess_engine

        # return super(AcsSubprocess, cls).__new__(subprocess_engine)(*args, **kwargs)
        return subprocess_engine(*args, **kwargs)


if __name__ == "__main__":
    # pylint: disable=invalid-name
    import logging
    import time
    from Queue import Empty
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    test = AcsSubprocess("adb logcat", logging, max_empty_log_time=1, silent_mode=False)
    result, log = test.execute_sync(2)

    proc, output_queue = test.execute_async(True)
    time.sleep(1)
    while True:
        try:
            line = output_queue.get_nowait()
            logging.info("{0}".format(line))
        except Empty:
            break

    sys.exit(0)
