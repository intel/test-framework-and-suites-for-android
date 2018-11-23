#!/usr/bin/env python
"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?

SPDX-License-Identifier: Apache-2.0
"""

import signal
import argparse
import sys
import time
import datetime
import multiprocessing
from multiprocessing.pool import Pool
import traceback


class BlockingError(Exception):
    """Error for blocking steps"""
    pass


class FailedError(Exception):
    """Error for critical steps"""
    pass


class Resolution():
    """Holds test step resolutions"""
    PASS = "[PASSED]"
    FAIL = "[FAILED]"
    BLOCKED = "[BLOCKED]"
    TIMEOUT = "[TIMEDOUT]"
    ERROR = "[ERROR]"


class GUIElementNotFoundError(Exception):
    """Exception ui tests"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LibraryUsageError(Exception):
    """Exception trown for incorrect library gunctions ussage"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TimeoutError(Exception):
    """Exception to be thrown when action times out"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DeviceNotFoundError(Exception):
    """Exception trown when device is not found"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class timeout:
    """
    Handles timeouts
    If called with process terminate/kill it
    If called with soutfile close it
    """

    def __init__(self, seconds=1, error_message='Timeout', process=None, soutfile=None):
        self.seconds = seconds
        self.error_message = error_message
        self.process = process
        self.soutfile = soutfile

    def handle_timeout(self, signum, frame):
        # Close file
        if self.soutfile is not None:
            self.soutfile.close()
        # terminte/kill process if did not returned
        if self.process is not None:
            print self.process.stderr.read()
            self.process.terminate()
            if self.process.poll() is None:
                self.process.kill()
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class SingletonType(type):
    """Helper class to define Singleton objects"""

    def __init__(self, name, bases, dict):
        super(SingletonType, self).__init__(name, bases, dict)
        self.instances = {}

    def __call__(self, *args, **kwargs):
        if "serial" in kwargs:
            if kwargs["serial"] not in self.instances:
                self.instances[kwargs["serial"]] = super(
                    SingletonType, self).__call__(*args, **kwargs)
            return self.instances[kwargs["serial"]]
        elif "use_module" in kwargs:
            if kwargs["use_module"] not in self.instances:
                self.instances[kwargs["use_module"]] = super(
                    SingletonType, self).__call__(*args, **kwargs)
            return self.instances[kwargs["use_module"]]
        try:
            return self.__instance
        except AttributeError:
            self.__instance = super(SingletonType, self).__call__(*args, **kwargs)
            return self.__instance


def parse_string(string, grep_for=None, multiple_grep=None, left_separator=None, right_separator=None, strip=False):
    """
    parses string given as argument
    greps lines containing grep_for string
    splits the string and return the text between
    left_separator and right_separator
    grep_for can be a string <=> multiple_grep == None
                 or an array <=> multiple_grep in ["OR","AND"]
    """

    if "\r\n" in string:
        new_line = "\r\n"
    else:
        new_line = "\n"
    if grep_for is not None:
        if multiple_grep is None:
            string = new_line.join(
                [line for line in string.split(new_line) if grep_for in line])
        elif multiple_grep == "OR":
            string = new_line.join(
                [line for line in string.split(new_line) if any(thing in line for thing in grep_for)])
        elif multiple_grep == "AND":
            string = new_line.join(
                [line for line in string.split(new_line) if all(thing in line for thing in grep_for)])
    if left_separator is not None:
        string = left_separator.join(
            [item for item in string.split(left_separator)][1:])
    if right_separator is not None:
        string = right_separator.join(
            [item for item in string.split(right_separator)][:-1])
    if strip:
        string = string.strip()
    return string


def get_args(args=sys.argv):
    '''
    Helper function for parsing arguments
    Usage:
        args = get_args(sys.argv)
    '''
    old_argv = sys.argv
    sys.argv = args

    parser = argparse.ArgumentParser(description='Process arguments for each script/runner')

    # connection arguments
    # serial
    parser.add_argument('-s', '--serial', dest='serial', help='Device serial')
    # ADB server port
    parser.add_argument('--adb-server-port', dest='adb_server_port', help='Port for ADB server')
    # ADB local port for uiautomator
    parser.add_argument('--adb-local-port', dest='adb_local_port', help='ADB local port for uiautomator')

    # script args
    parser.add_argument('--script-args', dest='script_args', help='Script arguments', nargs='+')

    args = parser.parse_args()

    sys.argv = old_argv
    return args


def parse_args(args=sys.argv):
    '''
        Helper function for parsing arguments
        Usage:
            args = parse_args(sys.argv)
        '''
    sys_args = vars(get_args())

    script_args = sys_args["script_args"]
    sys_args["script_args"] = {}
    try:
        if not (len(script_args) == 1 and script_args[0].upper() == 'NONE'):
            for entry in script_args:
                key, val = entry.split("=")
                sys_args["script_args"][key] = val
    except Exception:
        raise BlockingError(traceback.format_exc())
    return sys_args


class Sqlite(type):

    @staticmethod
    def create_query(query_db, query_type, query_table, key, value):
        query = "sqlite3 " + query_db + " \"" + query_type + " " + query_table + \
            " (name, value) values(\'" + key + "\'," + str(value) + ");\""

        return query


def get_time_string():
    ts = time.time()
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')


def get_ww():
    ts = time.time()
    return str(int(datetime.datetime.fromtimestamp(ts).strftime('%U')) + 1)


def error(msg, *args):
    return multiprocessing.get_logger().error(msg, *args)


class LogThreadExceptions(object):

    def __init__(self, callable):
        self.__callable = callable
        return

    def __call__(self, *args, **kwargs):
        try:
            result = self.__callable(*args, **kwargs)
        except Exception:
            error(traceback.format_exc())
            raise
        return result
    pass


class LoggingPool(Pool):

    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(self,
                                LogThreadExceptions(func),
                                args,
                                kwds,
                                callback)


def import_module(module_path):
    return __import__(name=module_path,
                      globals=globals(),
                      locals=locals(),
                      fromlist=["*"])


def getconfig(class_path, attribute, serial=None):
    from testlib.utils.statics.android.statics import get_dessert, get_device_type
    # from testlib.base.abstract import abstract_utils
    class_name = class_path.split(".")[-1]
    module_path = class_path.split(".")[:-1]
    module_path = ".".join(module_path)
    if serial:
        dessert = get_dessert(serial)
        device_type = get_device_type(serial)
        device_name = device_type + "_" + dessert

        module_name = module_path.split(".")[-1]
        module_path = ".".join(module_path.split(".")[:-1])
        module_path = ".".join([module_path, device_name])
        module_path = ".".join([module_path, module_name])

    target_module = import_module(module_path)

    class_obj = getattr(target_module, class_name)
    return getattr(class_obj, attribute)
