'''
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
'''

import logging
import os
import threading
from testlib.util.log import Logger
from testlib.util.common import g_common_obj


class Singleton(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

    @classmethod
    def destory(cls):
        with cls.__singleton_lock:
            cls.__singleton_instance = None


class MultimediaLogger(Singleton):
    LOG_FILE = "multimedia_dbg.log"

    def __init__(self):
        self.format = None
        self.fileHandler = None
        self.logger = Logger.getlogger()
        self.handlers = []

    def addFileHandler(self, mode="a+", filename=None, loglevel=5):
        filename = filename if filename else \
            os.path.join(g_common_obj.get_user_log_dir(), MultimediaLogger.LOG_FILE)
        print "*****************************************************************"
        print g_common_obj.get_user_log_dir()
        loglevel = loglevel if loglevel else Logger.LOGLEVELS.get("DEBUG")
        self.format = logging.Formatter(
            "[%(asctime)s - tid:%(thread)d - Multimedia-debug - %(levelname)s] %(message)s")
        self.fileHandler = logging.FileHandler(filename=filename, mode=mode)
        self.fileHandler.setLevel(loglevel)
        self.fileHandler.setFormatter(self.format)
        self.handlers.append(self.fileHandler)
        self.logger._logobj.addHandler(self.fileHandler)

    def removeHandler(self, handler):
        if handler in self.logger._logobj.handlers:
            self.logger._logobj.removeHandler(handler)
        else:
            self.logger.error("Handler not in logger object. Skip to remove")

    def removeHanlders(self):
        for h in self.handlers:
            self.removeHandler(h)
        self.handlers = []

    def __getattr__(self, attr):
        ''' wrapper for jsonrpc methods '''
        return self.__dict__.get(attr) or getattr(self.logger, attr)
