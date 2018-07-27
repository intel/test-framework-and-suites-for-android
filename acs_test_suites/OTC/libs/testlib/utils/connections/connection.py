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


class Connection(object):

    def __init__(self):
        pass

    def open_connection(self):
        raise NotImplementedError("Method not overwritten")

    def close_connection(self):
        raise NotImplementedError("Method not overwritten")

    def get_file(self, remote, local):
        raise NotImplementedError("Method not overwritten")

    def put_file(self, local, remote):
        raise NotImplementedError("Method not overwritten")

    def run_cmd(self, command, mode="synch"):
        raise NotImplementedError("Method not overwritten")

    def kill_command(self, pid):
        raise NotImplementedError("Method not overwritten")

    def kill_all(self, pids):
        raise NotImplementedError("Method not overwritten")

    def cd(self, path):
        raise NotImplementedError("Method not overwritten")

    def set_env(self, var_name, var_value):
        raise NotImplementedError("Method not overwritten")

    def unset_env(self, var_name):
        raise NotImplementedError("Method not overwritten")


if __name__ == "__main__":
    pass
