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
@summary: This module is the AcsSubprocess factory
@since: 07/08/14
@author: sfusilie
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
