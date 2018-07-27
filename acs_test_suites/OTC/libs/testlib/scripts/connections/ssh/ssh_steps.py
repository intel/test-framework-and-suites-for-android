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

from testlib.scripts.connections.ssh.ssh_step import step as ssh_step
from testlib.base.base_step import step as base_step


class command(ssh_step):

    """ description:
            runs the given command over ssh. to check the correct
                execution of the command, the stdout or stderr can be
                grepped for given string (if it is present or not)

        usage:
            command(command = "command_to_be_executed",
                    <stdout_grep = "text_to_exist_in_stdout>,
                    <stdout_not_grep = "text_not_to_exist_in_stdout>,
                    <stderr_grep = "text_to_exist_in_stderr>,
                    <stderr_not_grep = "text_not_to_exist_in_stderr>,)

        tags:
            ssh, command, grep, stdout, stderr
    """

    command = None

    def __init__(self, command, stdout_grep=None, stdout_not_grep=None, stderr_grep=None, stderr_not_grep=None,
                 **kwargs):
        self.command = command
        self.stdout_grep = stdout_grep
        self.stderr_grep = stderr_grep
        self.stdout_not_grep = stdout_not_grep
        self.stderr_not_grep = stderr_not_grep
        ssh_step.__init__(self, **kwargs)
        self.set_errorm("", "Executing adb command " + self.command)
        self.set_passm("Executing adb command " + self.command)

    def do(self):
        self.step_data = self.ssh_connection.run_cmd(self.command)

    def check_condition(self):
        stdout = self.step_data[0]
        stderr = self.step_data[1]
        if self.verbose:
            stds = "\n\tSTDOUT = \n\t" + stdout + \
                   "\tSTDERR = \n\t" + stderr + "\n"
        if self.stdout_grep:
            if self.verbose:
                error_mess = "\'" + self.stdout_grep + "\' not in stdout"
                error_mess += stds
                self.set_errorm("Executing " + self.command, error_mess)
                self.set_passm("Executing " + self.command + stds)
            return self.stdout_grep in stdout
        if self.stdout_not_grep:
            if self.verbose:
                error_mess = "\'" + self.stdout_not_grep + "\' in stdout"
                error_mess += stds
                self.set_errorm("Executing " + self.command, error_mess)
                self.set_passm("Executing " + self.command + stds)
            return self.stdout_not_grep not in stdout
        if self.stderr_grep:
            if self.verbose:
                error_mess = "\'" + self.stderr_grep + "\' not in stderr"
                error_mess += stds
                self.set_errorm("Executing " + self.command, error_mess)
                self.set_passm("Executing " + self.command + stds)
            return self.stderr_grep in stderr
        if self.stderr_not_grep:
            if self.verbose:
                error_mess = "\'" + self.stderr_not_grep + "\' in stderr"
                error_mess += stds
                self.set_errorm("Executing " + self.command, error_mess)
                self.set_passm("Executing " + self.command + stds)
            return self.stderr_not_grep not in stderr
        return True


class send_email(base_step):

    def __init__(self, host, user, password, recipients, subject, message=None, file_path=None,
                 html_content_type=False, **kwargs):
        self.host = host
        self.user = user
        self.passwd = password
        self.recipients = recipients
        self.subject = subject
        self.message = message
        self.file_path = file_path
        self.html = html_content_type
        base_step.__init__(self, **kwargs)

    def do(self):
        if self.file_path:
            email_command = "cat " + self.file_path
        else:
            email_command = "echo '" + self.message + "'"
        email_command += " | mailx "
        if self.html:
            email_command += "-a 'Content-Type: text/html'"
        email_command += "-s '" + self.subject + "' "
        for recipient in self.recipients:
            email_command += recipient + ", "
        email_command = email_command.strip(", ")
        command(command=email_command,
                host=self.host,
                user=self.user,
                password=self.passwd)()

    def check_condition(self):
        # TODO
        return True
