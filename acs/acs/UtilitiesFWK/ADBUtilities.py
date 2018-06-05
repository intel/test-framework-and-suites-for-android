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
:summary: Utilities class for ADB command
:author: vtinelli
:since: 27/04/2011
"""


import subprocess
import os
import select
import socket
import re
import time
import tempfile
import platform
import psutil
import random
import threading

from acs.ErrorHandling.AcsToolException import AcsToolException
from acs.UtilitiesFWK.Utilities import Global, internal_shell_exec


class ADBSocket():

    def __init__(self,
                 logger=None,
                 serial=None,
                 adb_ethernet=False,
                 device_ip=None,
                 adb_port=None,
                 hostname='localhost',
                 port=5037,
                 silent_mode=False):

        self.__silent_mode = silent_mode
        self._logger = logger

        self._adb_hostname = hostname

        self._adb_host_port = port
        self._adb_server_is_running = False

        self._use_adb_over_ethernet = adb_ethernet
        self._device_ip = str(device_ip)
        self._adb_target_port = str(adb_port)

        self.__lock = threading.Lock()
        self._adb_socket = None

        self._whoami = threading.currentThread().name

        if not self._use_adb_over_ethernet:
            if serial and serial != "":
                self._adb_serial = self._adb_format("host:transport:%s" % serial)
            else:
                self._adb_serial = self._adb_format("host:transport-usb")
        else:
            self._adb_serial = self._adb_format("host:transport:%s:%d" % (device_ip, adb_port))

    def _adb_format(self, cmd):
        """Prepare command sent to adb
        """
        clean_cmd = cmd.strip()

        # ADB command formatting
        if clean_cmd.startswith("adb"):
            clean_cmd = re.sub("^adb\s+", "", clean_cmd, 1)

        # Remove formatting from Binder
        clean_cmd = re.sub("^shell\s+", "shell:", clean_cmd, 1)
        clean_cmd = re.sub("^reboot", "reboot:", clean_cmd, 1)
        clean_cmd = re.sub("^root", "root:", clean_cmd, 1)
        clean_cmd = re.sub("^get-state", "host:get-state", clean_cmd, 1)

        # Compute checksum
        checksum = "%04x" % len(clean_cmd)

        # Build command sent to adb
        clean_cmd = checksum + clean_cmd

        return clean_cmd

    def _adb_send(self, cmd, adb_socket=None):
        """Execute a command
        """
        if adb_socket is None:
            adb_socket = self._adb_socket

        if self._logger and not self.__silent_mode:
            self._logger.debug("[ADB-SEND]: " + cmd)

        if adb_socket is not None:
            adb_socket.send(cmd)
        elif self._logger and not self.__silent_mode:
            self._logger.error("[ADB-SEND] No socket available (%s)" % (str(self._whoami)))

    def _adb_receive(self, timeout, show_output=True, adb_socket=None):
        """
        Receives and returns the result from the previously executed
        command before the given C{timeout}.

        :type timeout: int
        :param timeout: the maximum amount of time to wait.

        :type show_output: bool
        :param show_output: a boolean indicating whether we shall
        display any output or not

        :type adb_socket: socket
        :param adb_socket: the socket instance from which to read data

        :rtype: str
        :return: the socket output as string.
        """

        # Initialize local variables
        data = ""
        done = False
        if adb_socket is None:
            adb_socket = self._adb_socket

        # Begin timeout loop
        # We will wait until:
        # - timeout as been reached or
        # - there is no more data expected
        while timeout > 0 and done is False and adb_socket:
            t0 = time.time()
            # Wait for data in the input socket
            inputready, _outputready, _exceptready = \
                select.select([adb_socket], [], [], .1)
            # Read data from the socket
            for s in inputready:
                if s == adb_socket:
                    # Receive new data
                    newdata = adb_socket.recv(8192)
                    # Check whether we expect more data or not
                    # We expect more data if:
                    # - the data buffer is still empty or
                    # - we still have read some data from the socket
                    if data != "" and not newdata:
                        done = True
                    else:
                        data += newdata
            # Compute the new timeout value
            t1 = time.time()
            timeout -= (t1 - t0)

        # Log the data if we are asked to before returning it
        if self._logger and show_output and not self.__silent_mode:
            # Remove all CRLF by - to have all the log on a single line
            data_string = str(data).replace("\r\n", "-")
            self._logger.debug("[ADB-RETURN] (%d) %s ", timeout, data_string)

        # Return the data
        return data

    def _adb_parse_result(self, status):
        """Parse received result
        """

        if status:
            if (status[:4]) == "FAIL":
                return Global.FAILURE

            if (status[:4]) == "OKAY":
                return Global.SUCCESS

        if self._logger and not self.__silent_mode:
            self._logger.debug("[ADB-PARSE] Empty status %s", str(status))

        return Global.FAILURE

    def _adb_connect(self, status=""):
        """
        Connect to adb tcp server

        :type status: string
        :param status: status log

        """
        valid = Global.FAILURE
        status = ""
        error = ""
        is_socket_to_adb_server_ok = False
        try_nb = 0

        while not is_socket_to_adb_server_ok and try_nb < 3:
            try:
                # Disconnect before re-establishing the socket
                if self._adb_socket:
                    self._adb_disconnect()

                # ADB socket connection
                self._adb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._adb_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self._adb_socket.settimeout(1)
                self._adb_socket.connect((str(self._adb_hostname), int(self._adb_host_port)))

                if self._adb_socket:
                    valid, status = self.__adb_init(status)

                    if valid == Global.SUCCESS:
                        # ADB socket connection to ADB server is successful
                        # Go out the loop that handle retry connection
                        is_socket_to_adb_server_ok = True
                        break

            except socket.error as socket_ex:
                error = str(socket_ex)

            finally:
                # increment the connection retry number
                try_nb += 1

                if not is_socket_to_adb_server_ok:

                    self._logger.warning(
                        "[ADB-CONNECT] Connection error (%s, valid: %s, status: %s, error: %s, try: %d)" %
                        (str(self._whoami), valid, status, error, try_nb))

                    # ADB socket to ADB Server connection failure
                    # Disconnect adb socket connection
                    if self._adb_socket:
                        self._adb_disconnect()

                    valid = Global.FAILURE

                    # Wait before retry
                    if try_nb < 3:
                        time.sleep(1)

        if not is_socket_to_adb_server_ok:
            # ADB socket to ADB SERVER connection failure
            self._logger.error("[ADB-CONNECT] Connection error (%s)" % (str(self._whoami)))

        return valid, status

    def _adb_disconnect(self):
        """Disconnect from adb tcp server
        """
        sock_address = None

        try:
            if self._adb_socket:
                sock_address, _ = self._adb_socket.getsockname()

                if sock_address:
                    if sock_address != "0.0.0.0":
                        self._adb_socket.shutdown(socket.SHUT_RDWR)
                        self._adb_socket.close()
                    else:
                        self._logger.warning("[ADB-DISCONNECT] Socket address not available (%s, socket address: %s)" %
                                             (str(self._whoami), str(sock_address)))
                else:
                    self._logger.warning("[ADB-DISCONNECT] Socket address not valid (%s, socket address: %s)" %
                                         (str(self._whoami), str(sock_address)))
            else:
                self._logger.warning("[ADB-DISCONNECT] Already disconnected (%s)" % (str(self._whoami)))

        except socket.error as socket_ex:
            self._logger.error("[ADB-DISCONNECT] Disconnection error (error: %s, %s)" %
                               (str(socket_ex), str(self._whoami)))

        finally:
            self._adb_socket = None

    def adb_start(self, timeout=10):
        """Start adb server
        """

        self.__lock.acquire()
        cmd_line = "adb start-server"
        self._adb_server_is_running = False

        try:
            # WA to integrate the patch until all server are killed
            # self._adb_host_port = self.get_adb_server_port(port=self._adb_host_port,
            #                                               retry=5)
            os.environ["ANDROID_ADB_SERVER_PORT"] = str(self._adb_host_port)
            self.stop_adb_server()

            if self._logger:
                self._logger.debug("[ADB-SERVER] Starting ADB server on {0}...".format(self._adb_host_port))
            # below sleep time gives some time for adb to respond after
            # "stop_adb_server()"
            time.sleep(1)
            status, status_msg = internal_shell_exec(cmd_line, timeout)

            if status == Global.SUCCESS:
                self._adb_server_is_running = True
                if self._logger:
                    self._logger.debug("[ADB-SERVER] ADB server started")
            else:
                if self._logger:
                    self._logger.error("[ADB-SERVER] Starting failure (status: %s)" % str(status_msg))

        except Exception as error:  # pylint: disable=W0703
            if self._logger:
                self._logger.error("[ADB-SERVER] Starting failure; adb not found (cmd: %s, error: %s)" %
                                   (str(cmd_line), str(error)))
            raise
        finally:
            self.__lock.release()

    def stop_adb_server(self):
        try:
            cmd_line = "adb kill-server"

            if self._logger:
                self._logger.debug("[ADB-SERVER] Stopping ADB server ...")

            status, status_msg = internal_shell_exec(cmd_line, 5)

            if status == Global.SUCCESS:
                self._adb_server_is_running = False
            else:
                if self._logger:
                    self._logger.error("[ADB-SERVER] Stopping failure (status: %s)" % str(status_msg))

            if not self._adb_server_is_running:
                if self._logger:
                    self._logger.debug("[ADB-SERVER] ADB server stopped")

        except Exception as error:  # pylint: disable=W0703
            if self._logger:
                self._logger.error("[ADB-SERVER] Stopping failure; adb not found (cmd: %s, error: %s)" %
                                   (str(cmd_line), str(error)))
            raise

    def adb_stop(self):
        """Stop adb server
        """

        self.__lock.acquire()

        try:
            self.stop_adb_server()
        finally:
            self.kill_adb_instances()
            self.__lock.release()

    def adb_ethernet_start(self, ip_address, port, retries=3, timeout=10):
        """
        Start adb server and connect to adbd
        :type  ip_address: str
        :param ip_address: ip address of the device

        :type  port: str
        :param port: port number to connect to device adb client

        :type max_retry_number: int
        :param max_retry_number: max number of tries for adb connection with the device

        :rtype: bool
        :return: adb connection state (True if adb is connected else False)
        """
        is_connected = False
        current_try = 1
        if self._logger:
            self._logger.debug("[ADB-SERVER] starting and connecting over ETHERNET (IP: %s, Port: %s)..." %
                               (ip_address, port))

        while current_try <= retries and not is_connected:
            try:
                msg = "adb connect KO"
                cmd = "adb connect %s:%s" % (ip_address, port)
                result, return_msg = internal_shell_exec(cmd, timeout)

                if result == Global.SUCCESS:
                    if return_msg.startswith("unable"):
                        msg = "[ADB-SERVER] Fail to connect to DUT (%s)" % return_msg
                    elif "already" in return_msg or "connected" in return_msg:
                        # In ethernet, we also need check adb connection with adb shell presence
                        msg = "[ADB-SERVER] Connected to DUT (%s)" % return_msg

                        run_cmd_code, run_cmd_msg = self.run_cmd("adb shell echo", 10, True)

                        if run_cmd_code == Global.FAILURE:
                            msg += "/ adb shell NOK (%s)" % run_cmd_msg
                        else:
                            msg += "/ adb shell OK (%s)" % run_cmd_msg
                            is_connected = True
                    else:
                        msg = "[ADB-SERVER] Connection to DUT status is unknown (%s)" % return_msg
                else:
                    msg = "Connect to adb server has failed"

                if self._logger:
                    self._logger.debug(msg)

            except Exception as error:  # pylint: disable=W0703
                if self._logger:
                    self._logger.debug("[ADB-SERVER] started but fail to connect over ETHERNET (%s)" % str(error))

            finally:
                # increment the connection retry number
                current_try += 1

        return is_connected

    def adb_ethernet_stop(self, ip_address, port, timeout=10):
        """
        Stop adb server and disconnect from adbd
        """
        is_disconnected = False

        if self._logger:
            self._logger.debug("[ADB-SERVER] stopping and disconnecting over ETHERNET (IP: %s, Port: %s)..." %
                               (ip_address, port))

        try:
            cmd_line = "adb disconnect %s:%s" % (ip_address, port)
            status, return_msg = internal_shell_exec(cmd_line, timeout)

            if status == Global.SUCCESS:
                if return_msg.startswith("") or return_msg.startswith("No such"):
                    msg = "[ADB-SERVER] stopped and disconnected from DUT (%s)" % return_msg
                    is_disconnected = True
                else:
                    msg = "[ADB-SERVER] stopped but connection to DUT status is unknown (%s)" % return_msg
            else:
                msg = "[ADB-SERVER] Stop failure (status: %s)" % str(return_msg)

            if self._logger:
                self._logger.debug(msg)

        except Exception as error:  # pylint: disable=W0703
            if self._logger:
                self._logger.debug("[ADB-SERVER] fail to stop over ETHERNET (%s)" % str(error))

        return is_disconnected

    def adb_restart(self, timeout=10):
        """
        Restart adb server
        """

        if self._logger:
            self._logger.debug("[ADB-SERVER] Restart adb server")

        self.adb_stop()
        time.sleep(1)
        self.adb_start(timeout)
        time.sleep(1)

    def count_adb_instances(self):
        """
        Count adb instances
        """
        # add try except code to warn user about the new third party psutil
        # this should be removed later and the import
        # will be move at the beginning
        adb_proc_name = "adb.exe"
        if platform.system() != "Windows":
            adb_proc_name = "adb"

        instances = 0
        procs = psutil.get_process_list()
        for element in procs:
            try:
                if element.name == adb_proc_name:
                    instances += 1
            except psutil.error.NoSuchProcess:
                continue

        return instances

    def kill_adb_instances(self):
        """
        Kill adb instances
        """
        # add try except code to warn user about the new third party psutil
        # this should be removed later and the import
        # will be move at the beginning
        if self._logger:
            self._logger.debug("[ADB SERVER] Kill all adb instances")

        adb_proc_name = "adb.exe"
        if platform.system() != "Windows":
            adb_proc_name = "adb"

        procs = psutil.process_iter()
        for proc in procs:
            try:
                if proc.name == adb_proc_name:
                    proc.kill()
                    self._adb_server_is_running = False

            except (psutil.NoSuchProcess, psutil.AccessDenied) as err:
                excp_message = "exception pid:%s, reason:%s" % (str(err.pid), str(err.msg))
                self._logger.warning("Kill adb process failed ! (%s)" % excp_message)
                continue

    def __adb_init(self, status):  # @UnusedVariable
        # Hard-coded: it is sent for every adb command
        self._adb_send(self._adb_serial)

        # Host-to-host communication, select should be quick
        status = self._adb_receive(2)
        valid = self._adb_parse_result(status)

        if status.lower().startswith("fail0010device"):
            status = "[ADB-HOST] Lost ADB socket connection : %s" % status

        return valid, status

    def run_cmd(self, cmd, timeout,
                wait_for_response=True,
                silent_mode=None):
        """
        Execute the input command and return the result message
        If the timeout is reached, return an exception

        :type  cmd: string
        :param cmd: cmd to be run
        :type  timeout: integer
        :param timeout: Script execution timeout in ms

        :return: Execution status & output string
        :rtype: Integer & String
        """

        self.__lock.acquire()
        previous_mode = None

        if silent_mode is not None:
            previous_mode = self.__silent_mode
            self.__silent_mode = silent_mode

        status = "[ADB-HOST] Connection failed..."

        try:

            valid, status = self._adb_connect(status)

            if valid == Global.SUCCESS:

                del status
                del valid

                status = "[ADB-HOST] Prepare(2) failed..."
                clean_cmd = self._adb_format(cmd)

                status = "[ADB-HOST] Send(2) failed..."
                self._adb_send(clean_cmd)

                if wait_for_response:
                    status = "[ADB-HOST] Receive(2) failed..."
                    status = self._adb_receive(timeout)

                    valid = self._adb_parse_result(status)

                    if len(status[4:]) > 0:
                        ret_status = status[4:]
                    else:
                        ret_status = "No response from ADB"
                        if self._logger and not self.__silent_mode:
                            self._logger.debug("[ADB] No response on CMD: " + cmd)
                else:
                    valid = Global.SUCCESS
                    ret_status = "OKAY"
            else:
                # return status message
                ret_status = status

        except Exception as e:  # pylint: disable=W0703
            self._logger.debug(str(e))
            valid = Global.FAILURE
            ret_status = status
        finally:
            if previous_mode is not None:
                self.__silent_mode = previous_mode
            try:
                self._adb_disconnect()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                pass
            finally:
                self.__lock.release()

        return valid, ret_status

    def run_cmd_fork(self, cmd, timeout):

        path = tempfile.gettempdir()

        # Define all forbidden characters for windows in a file name
        forbidden_chars = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]

        cmd_name = cmd.rstrip()
        cmd_name = cmd_name.replace(" ", "_")
        # Delete all special characters from the command
        for char in forbidden_chars:
            cmd_name = cmd_name.replace(char, "")

        cmd_name = cmd_name[:30]
        rand_id = str(random.randint(0, 10000))
        filename = cmd_name + "_" + rand_id + ".log"
        fullfilename = os.path.join(path, filename)

        f_write = open(fullfilename, 'wb')
        f_read = open(fullfilename, 'rb')

        my_process = subprocess.Popen(cmd, stdout=f_write, shell=True)

        # pylint: disable=E1101
        while timeout > 0 and my_process.poll() is None:
            time.sleep(1)
            timeout -= 1

        if my_process.poll() is not None:
            # Process created by Popen is terminated
            if my_process.poll() == 0:
                # Process successfully terminated
                result = f_read.read()
                f_write.close()
                f_read.close()
                os.remove(fullfilename)

                # Process end of lines
                result = result.replace("\n", "")

                return Global.SUCCESS, result
            else:
                f_write.close()
                f_read.close()
                os.remove(fullfilename)

                # Process not terminated properly
                err_msg = "Command %s failed" % (str(cmd))
                return Global.FAILURE, err_msg
        else:
            # Close the process
            my_process.terminate()
            f_write.close()
            f_read.close()

            # Process hasn't finished to execute command.
            err_msg = "Command %s has timeout!" % (str(cmd))
            return Global.FAILURE, err_msg

    def _is_port_used(self, port):
        """
        Check is port is already used by a process
        """
        is_used = False
        try:
            is_used = not all([False for c in psutil.net_connections() if c.laddr[1] == port])
        except AttributeError:
            self._logger.warning("Please, update the version of psutil python module")
            self._logger.warning("Not able to verify if the adb server port is available")
        return is_used

    def get_adb_server_port(self, port=0, retry=3):
        """
        get an available port for adb server

        :type  port: Integer
        :param port: adb port to use
        :type  retry: Integer
        :param retry: maximum retry to get an available adb port

        :rtype: Integer
        :return: The port number used for ADB server connection
        """
        if not retry:
            error_msg = "Could not find an available port for adb server"
            raise AcsToolException(AcsToolException.OPERATION_FAILED, error_msg)

        def _get_available_port():
            """
            By opening port 0 the OS will give us a random port between
            1024 to 65535, we then close down the socket and return the number

            :rtype: Integer
            :return: The port number used for ADB server connection
            """
            port = None
            try:
                sock = socket.socket()
                sock.bind(('', 0))
                port = sock.getsockname()[1]
                sock.close()
            except socket.error as sock_ex:
                self._logger.error("Socket error: %s" % sock_ex)
                error_msg = "Could not find a free port to start adb server"
                raise AcsToolException(AcsToolException.OPERATION_FAILED, error_msg)
            return port

        if not port:
            port = _get_available_port()

        if self._is_port_used(port):
            self._logger.error("{0} is not availble, it's already used by a process".format(port))
            # try again until max retry is reached
            port = self.get_adb_server_port(port=None,
                                            retry=retry - 1)
        return port
