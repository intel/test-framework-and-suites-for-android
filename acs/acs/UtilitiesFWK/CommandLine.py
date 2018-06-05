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
:summary: Implements methods used over to execute command based on unix through python
:since: 25/09/2013
:author: ssavrimoutou
"""
import os
import sys


class CommandLine(object):

    """
    Class which implement simple methods based on unix command
    """
    # Dictionary to store full path of a shell command to avoid
    # searching in PATH each time we call which method
    __which_command_dict = {}

    @staticmethod
    def which(file_name):
        """
        Shows the full path of (shell) commands.
        Find full path of a command/file from PATH environment

        :rtype: string
        :return: Full path of the command
                Return None in case PATH environment is not defined or command not found
        """
        # Reformat command name regarding os
        file_name = file_name if os.name in ['posix'] else file_name + ".exe"

        if file_name in CommandLine.__which_command_dict.iterkeys():
            full_path_cmd = CommandLine.__which_command_dict[file_name]
        else:
            # Separator is different in Linux
            path_separator = ":" if os.name in ['posix'] else ";"
            full_path_cmd = None

            # Get PATH environment value
            os_env_path = os.environ.get("PATH")
            if os_env_path:
                for path in os_env_path.split(path_separator):
                    try:
                        if file_name in os.listdir(r'%s' % path):
                            full_path_cmd = os.path.join(path, file_name)
                            CommandLine.__which_command_dict[file_name] = full_path_cmd
                            break
                    except OSError:
                        # Skip if current path is not found
                        # It could arrives that some path defined in the PATH environment is not found.
                        continue

        return full_path_cmd

    @staticmethod
    def findfile(file2find):
        """
        Find the file named file2find in the sys.path + the current working dir.

        :type file2find: String
        :param file2find: filename to find in the
        :rtype: String or None
        :return: the full path name if found, None if not found
        """
        cwd = os.getcwd()
        paths = [cwd] + sys.path
        for dirname in paths:
            possible = os.path.join(dirname, file2find)
            if os.path.isfile(possible):
                return possible
        return None

    @staticmethod
    def exists(file2check):
        """
        CHeck if the given (path to) file named file2check exists.

        :type file2check: String
        :param file2check: file path to check
        :rtype: bool
        :return: True if the full path if found, False otherwise if not found
        """
        return os.path.exists(file2check)

    @staticmethod
    def chmod(file2use, mode):
        """
        Change the right mode to the (path to) file named file2use

        :type file2use: String
        :param file2use: file path to use

        :type mode: int
        :param mode: The octal standard linux mode to use

        :rtype: bool
        :return: True if the full path if found, False otherwise if not found
        """
        return os.chmod(file2use, mode)
