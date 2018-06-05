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
:summary: equipment interface implementation
:since: 28/07/2010
:author: ymorel
"""

import ctypes
import os
import signal
import subprocess
import platform
from threading import Thread
from subprocess import Popen
from acs.ErrorHandling.TestEquipmentException import TestEquipmentException
from acs.Core.Report.ACSLogging import ACS_LOGGER_NAME, EQT_LOGGER_NAME
from acs.Core.Factory import Factory


class IEquipment(object):

    """
    Virtual interface with equipments
    """

    def get_name(self):
        """
        Gets the name of the equipment in bench configuration file
        :rtype: str
        :return: the name of the equipment in bench configuration file
        """
        raise TestEquipmentException(TestEquipmentException.FEATURE_NOT_IMPLEMENTED)

    def get_model(self):
        """
        Gets the model of the equipment
        :rtype: str
        :return: the model of the equipment
        """
        raise TestEquipmentException(TestEquipmentException.FEATURE_NOT_IMPLEMENTED)

    def get_eqt_dict(self):
        """
        Gets the part of the dictionary from equipment catalog associated
        to the equipment
        :rtype: dict
        :return: the dictionary containing equipment catalog parameters of
        the equipment
        """
        raise TestEquipmentException(TestEquipmentException.FEATURE_NOT_IMPLEMENTED)


class IDrivedEquipment(object):

    """
    Virtual interface with drived equipments
    """

    def load_driver(self):
        """
        Loads the driver of the equipment
        """
        raise TestEquipmentException(TestEquipmentException.FEATURE_NOT_IMPLEMENTED)

    def unload_driver(self):
        """
        Unloads the driver of the equipment
        """
        raise TestEquipmentException(TestEquipmentException.FEATURE_NOT_IMPLEMENTED)


class EquipmentBase(IEquipment):

    """
    Basic IEquipment realization
    """

    _log_prefix_key = 'equipment'

    def __init__(self, name, model, params, factory=None):
        """
        Constructor
        :type name: str
        :param name: the name of the equipment
        :type model: str
        :param model: the model of the equipment
        :type params: dict
        :param params: the dictionary containing the equipment catalog
        parameters of the equipment
        """
        IEquipment.__init__(self)
        self.__name = name
        self.__model = model
        self.__params = params
        self._factory = factory or Factory()
        self._logger = self._factory.create_logger("%s.%s.%s" % (ACS_LOGGER_NAME, EQT_LOGGER_NAME, self.whoami,))

    def get_logger(self):
        """
        Gets the internal logger of the equipment
        """
        return self._logger

    def get_name(self):
        """
        Gets the name of the equipment
        :rtype: str
        :return: the name of the equipment in bench configuration file
        """
        return self.__name

    def get_model(self):
        """
        Gets the model of the equipment
        :rtype: str
        :return: the model of the equipment
        """
        return self.__model

    def get_eqt_dict(self):
        """
        Gets the part of the dictionary from equipment catalog associated
        to the equipment
        :rtype: dict
        :return: the dictionary containing equipment catalog parameters of
        the equipment
        """
        return self.__params

    @property
    def logger(self):
        """
        Accessor to the internal logger of the equipment

        .. note:: This is more pythonic way of accessing private or protected attribute
            proposed as an alternative only

        """
        return self._logger

    @property
    def whoami(self):
        """
        Use the bench configuration name and the model of the equipment to build
        a unique identification str for the equipment
        :rtype: dict
        :return: a unique identification str for the equipment
        """
        bench_num = ""
        name = self.get_name()
        i = len(self.get_name()) - 1
        while i >= 0:
            if name[i:].isdigit():
                bench_num += name[i]
            else:
                break
            i += 1

        if bench_num == "":
            name = self.get_model()
        else:
            name = self.get_model() + " (" + bench_num + ")"

        return name


class DllLoader(EquipmentBase, IDrivedEquipment):

    """
    Class that loads a unique DLL at a time and handles the unload
    of this DLL when object is deleted
    """

    def __init__(self, name, model, params):  # pylint: disable=W0231
        """
        Constructor: initializes class attributes
        :type name: str
        :param name: the bench configuration name of the equipment
        :type model: str
        :param model: the model of the equipment
        :type params: dict
        :param params: the dictionary containing equipment catalog parameters
        of the equipment
        """
        EquipmentBase.__init__(self, name, model, params)
        self.__system = platform.system()
        self.__dll_object = None
        self.__dll_path = None
        self.__build_dll_path()

    def __del__(self):
        """
        Destructor
        """
        self.unload_driver()

    def __build_dll_path(self):
        """
        Builds the path to the DLL to use as a driver from equipment catalog parameters
        """
        dll_path = ""
        path_keys = self.get_eqt_dict().keys()
        # Get default folder path if any
        if "DefaultFolderPath" in path_keys:
            dll_path = self.get_eqt_dict()["DefaultFolderPath"]
            # Get specific path and overwrite default path if any
        path_keys = self.get_eqt_dict()[self.get_model()].keys()
        if "FolderPath" in path_keys:
            dll_path = self.get_eqt_dict()[self.get_model()]["FolderPath"]
            # Get binary name and possible end of path
        binary_path = self.get_eqt_dict()[self.get_model()]["Binary"]
        # Build final path
        self.__dll_path = os.path.join(dll_path, binary_path)

    def load_driver(self, calling_convention="STANDARD"):  # pylint: disable=W0221
        """
        This function loads a DLL dynamically. If the DLL has already been
        loaded, the DLL is reloaded.
        :type calling_convention: str
        :param calling_convention: the calling convention used in the DLL to export
        functions. Possible values:
            - STANDARD: uses standard C calling convention (default)
            - STDCALL: uses stdcall calling convention (Windows only)
        :raise TestEquipmentException: failed to load the DLL
        """
        try:
            self.get_logger().debug("Load driver %s", self.__dll_path)

            # Update PATH environment variable with DLLs location
            dll_path_dirname = os.path.dirname(self.__dll_path)
            if dll_path_dirname not in os.environ["PATH"]:
                os.environ["PATH"] = "%s;%s" % (os.environ["PATH"], dll_path_dirname)

            if self.__dll_object is not None:
                self.unload_driver()
            if calling_convention == "STANDARD":
                self.__dll_object = ctypes.cdll.LoadLibrary(os.path.normpath(self.__dll_path))
            elif calling_convention == "STDCALL":
                self.__dll_object = ctypes.windll.LoadLibrary(os.path.normpath(self.__dll_path))
            else:  # Unavailable calling convention
                self.get_logger().error(
                    "Unavailable C calling convention (%s) for dll: %s",
                    calling_convention,
                    self.__dll_path)
                raise TestEquipmentException(TestEquipmentException.C_LIBRARY_ERROR,
                                             "Failed to load driver: unavailable C calling convention")
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_error = "Failed to load DLL %s (%s)" % (str(self.__dll_path), str(ex))
            self.get_logger().error(msg_error)
            raise TestEquipmentException(TestEquipmentException.C_LIBRARY_ERROR, msg_error)

    def unload_driver(self):
        """
        This function unloads the loaded library if any. If no library has
        been loaded, nothing is done.
        :raise TestEquipmentException: failed to unload driver or unsupported platform
        """
        try:
            if self.__dll_object is not None:
                self.get_logger().debug("Unload %s driver", self.get_name())
                if self.__system == "Windows":
                    # noinspection PyProtectedMember
                    ctypes.windll.kernel32.FreeLibrary(self.__dll_object._handle)
                    self.__dll_object = None
                elif self.__system == "Linux":
                    self.__dll_object = None
                else:
                    self.get_logger().error("Unsupported platform")
                    raise TestEquipmentException(TestEquipmentException.PLATFORM_ERROR,
                                                 "Unsupported platform")
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            msg_error = "Failed to unload DLL %s (%s)" % (str(self.__dll_path), str(ex))
            self.get_logger().error(msg_error)
            raise TestEquipmentException(TestEquipmentException.C_LIBRARY_ERROR, msg_error)

    def get_dll(self):
        """
        Gets the DLL handle
        :rtype: ctypes.cdll
        :return: the handle of the loaded DLL, None if no DLL has been loaded
        """
        return self.__dll_object


class DaemonLoader(EquipmentBase, IDrivedEquipment):

    """
    Class that loads a daemon that allows user to communicate with
    the equipment
    """

    def __init__(self, name, model, params):  # pylint: disable=W0231
        """
        Constructor: initializes class attributes
        :type name: str
        :param name: the bench configuration name of the equipment
        :type model: str
        :param model: the model of the equipment
        :type params: dict
        :param params: the dictionary containing equipment catalog
        parameters of the equipment
        """
        EquipmentBase.__init__(self, name, model, params)
        self.__binary_path = None
        self.__binary = None
        self.__build_binary_path()

    def __del__(self):
        """
        Destructor
        """
        self.unload_driver()

    def __build_binary_path(self):
        """
        Builds the path to the binary file to use as a driver from equipment catalog parameters
        """
        bin_path = ""
        path_keys = self.get_eqt_dict().keys()
        # Get default folder path if any
        if "DefaultFolderPath" in path_keys:
            bin_path = self.get_eqt_dict()["DefaultFolderPath"]
            # Get specific path and overwrite default path if any
        path_keys = self.get_eqt_dict()[self.get_model()].keys()
        if "FolderPath" in path_keys:
            bin_path = self.get_eqt_dict()[self.get_model()]["FolderPath"]
            # Get binary name and possible end of path
        binary_path = self.get_eqt_dict()[self.get_model()]["Binary"]
        # Build final path
        self.__binary_path = os.path.join(bin_path, binary_path)

    def load_driver(self):
        """
        This function starts the program that must act as the equipment driver.
        :raise TestEquipmentException: failed to load driver
        """
        try:
            self.get_logger().debug(
                "Load %s driver from %s",
                self.get_name(),
                self.__binary_path)
            if self.__binary is not None:
                self.unload_driver()
            self.__binary = Popen(self.__binary_path)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.get_logger().error(
                "Failed to start daemon driver from %s",
                str(self.__binary_path))
            raise TestEquipmentException(
                TestEquipmentException.DAEMON_DRIVER_ERROR,
                "Failed to start daemon driver from " + str(self.__binary_path))

    def unload_driver(self):
        """
        This function stops the program started to act as the equipment driver
        :raise TestEquipmentException: failed to stop the daemon driver
        """
        try:
            self.get_logger().debug("Unload driver")
            if self.__binary is not None:
                # pylint: disable=E1101
                self.__binary.terminate()
                self.__binary = None
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.get_logger().error(
                "Failed to stop daemon driver started from %s",
                str(self.__binary_path))
            raise TestEquipmentException(
                TestEquipmentException.DAEMON_DRIVER_ERROR,
                "Failed to stop daemon driver started from " +
                str(self.__binary_path))

    def _get_binary_path(self):
        """
        Gets the path to the binary file that acts as the equipment driver
        :rtype: str
        :return: the path to the binary file that acts as the equipment driver
        """
        return self.__binary_path


class ExeRunner(EquipmentBase):

    """
    Class that run executable file
    """
    NOT_TERMINATED = 3

    def __init__(self, name, model, params):
        """
        Constructor: initializes class attributes
        :type name: str
        :param name: the bench configuration name of the equipment
        :type model: str
        :param model: the model of the equipment
        :type params: dict
        :param params: the dictionary containing equipment catalog parameters
        of the equipment
        """
        EquipmentBase.__init__(self, name, model, params)
        self.__system = platform.system()
        self.__exe_path = None
        self.__binary_path = None
        self.__process = None
        self.__msg_stdout = ""
        self.__msg_stderr = ""
        self.__build_exe_path()
        self.__return_code = ExeRunner.NOT_TERMINATED

    def __build_exe_path(self):
        """
        Builds the path to the EXE to use from equipment catalog parameters
        """
        exe_path = ""
        defaultfolderpath = False
        folderpath = False

        path_keys = self.get_eqt_dict().keys()
        # Get default folder path if any
        if "DefaultFolderPath" in path_keys:
            exe_path = self.get_eqt_dict()["DefaultFolderPath"]
            defaultfolderpath = True

        # Get specific path and overwrite default path if any
        path_keys = self.get_eqt_dict()[self.get_model()].keys()
        if "FolderPath" in path_keys:
            exe_path = self.get_eqt_dict()[self.get_model()]["FolderPath"]
            folderpath = True

        if not defaultfolderpath and not folderpath:
            raise TestEquipmentException(TestEquipmentException.BINARY_FOLDER_PATH_ERROR,
                                         "Existing binary folder path is needed")

        # Get binary name and possible end of path
        self.__binary_path = self.get_eqt_dict()[self.get_model()]["Binary"]

        # Build final path
        self.__exe_path = str(os.path.join(exe_path, self.__binary_path))

    def start_exe(self, param_cmd_line=None, timeout=None, waitendprocess=True):
        """
        Execute command line

        :type param_cmd_line: str
        :param param_cmd_line: command line to send to executable to control equipment

        :type timeout: int
        :param timeout: waiting before killing the process

        :type waitendprocess: boolean
        :param waitendprocess:  if true: wait the end of the process, false no waiting

        :rtype: tuple
        :return: A tuple containing (see below)

        ::
            * stdout as C{str}: the message returned by the executable
            * return code as C{str}: the executable exit code

        """
        self.__msg_stdout = ""
        self.__msg_stderr = ""
        self.__return_code = ExeRunner.NOT_TERMINATED
        if param_cmd_line is not None:
            cmd_line = "%s %s" % (self.__exe_path, param_cmd_line)
        else:
            cmd_line = "%s" % self.__exe_path

        args = cmd_line
        self._logger.info(args)

        def target():
            """
            Execute exe in thread
            """
            self.__process = subprocess.Popen(args, shell=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)

            if waitendprocess:
                outputs = self.__process.communicate()
                self.__msg_stdout = str(outputs[0])
                self.__msg_stderr = str(outputs[1])
                self.__return_code = self.__process.returncode
                if self.__msg_stdout:
                    self._logger.info(self.__msg_stdout)
            else:
                # Thread execute for print executable log with a non blocking method
                def _print_exe_log():
                    try:
                        while self.__process is not None:
                            line = self.__process.stdout.readline()
                            if line != "":
                                self._logger.info("%s" % line[:-1])
                    except (ValueError, IOError):
                        # pipe was closed
                        pass

                thread_print = Thread(target=_print_exe_log)
                thread_print.start()

        # Execution threader => if executable don't respond before timeout, it is killed
        thread = Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.get_logger().error(
                "No response of the executable, process %s killed",
                str(self.__binary_path))
            if platform.system() == "Windows":
                subprocess.Popen("taskkill /F /T /PID %i" % self.__process.pid, shell=True)
            else:
                os.killpg(self.__process.pid, signal.SIGTERM)

        if self.__msg_stderr != "":
            self._logger.error(self.__msg_stderr)
            raise TestEquipmentException(TestEquipmentException.SPECIFIC_EQT_ERROR, "std_err :" + self.__msg_stderr)

        return self.__msg_stdout, self.__return_code, self.__process
