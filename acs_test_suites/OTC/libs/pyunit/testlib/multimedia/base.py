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
import os
base_path = os.path.split(os.path.realpath(__file__))[0].split(os.sep)


def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


__TEMP_DIR = None


def getTmpDir():
    pathList = ["/var/log", "/tmp", "~/tmp"]
    for each in pathList:
        if os.access(each, os.R_OK | os.W_OK):
            path = each
            break
    else:
        path = "~/tmp"
    global __TEMP_DIR
    if __TEMP_DIR is None:
        __TEMP_DIR = os.path.join(path, "oat")
    path = os.path.expanduser(path)
    path = os.path.normpath(path)
    mkdirs(path)
    return path


class UiWindows(object):
    def __init__(self, bound):
        if u"top" not in bound:
            bound = bound[u"bounds"]
        self.t = bound[u"top"]
        self.l1 = bound[u"left"]
        self.r = bound[u"right"]
        self.b = bound[u"bottom"]

    def __str__(self):
        return "lefttop: %d, %d    rightbottom: %d, %d" % (self.l1, self.t, self.r, self.b)

    def getWidth(self):
        return self.r - self.l1

    def getHeight(self):
        return self.b - self.t

    def getMidPoint(self):
        return (self.l1 + self.r) / 2, (self.t + self.b) / 2

    def getTop(self):
        return self.t

    def getLeft(self):
        return self.l1
