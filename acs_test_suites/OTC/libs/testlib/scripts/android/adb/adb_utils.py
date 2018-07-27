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

from testlib.utils.connections.adb import Adb as connection_adb
from testlib.utils.connections.local import Local as connection_local
from testlib.scripts.android import android_utils
import re
import time
from dateutil.parser import parse
import os


class Sqlite:

    @staticmethod
    def generate_update_query(db, table, columns, values, where_columns, where_values):

        """ description:
                forms the <update> query from given parameters

                db = path to db on the device
                table = table on which the update will be performed
                columns = list of the columns to be updated
                values = list of values to be used for update
                where_columns = list of columns to be used for
                    identifying the entry(ies) in table
                where_value = list of values to be used for identifying
                    the entry(ies) in table
            tags:
                utils, sqlite, query, update
        """

        query = "sqlite3 {0} \"update {1} set ".format(db, table)
        i = 0
        for column in columns:
            query += "{0} = '{1}', ".format(column, values[i])
            i += 1
        query = query.strip().strip(',')

        query += " where "
        i = 0
        for column in where_columns:
            query += "{0} = '{1}' and ".format(column, where_values[i])
            i += 1
        query = query.strip().rsplit(' ', 1)[0]
        query += "\";"

        return query

    @staticmethod
    def generate_select_query(db, table, columns, where_columns, where_values):

        """ description:
                forms the <select> query from given parameters

                db = path to db on the device
                table = table on which the update will be performed
                columns = list of the columns to be selected
                where_columns = list of columns to be used for
                    identifying the entry(ies) in table
                where_value = list of values to be used for identifying
                    the entry(ies) in table
            tags:
                utils, sqlite, query, select
        """
        query = "sqlite3 {0} \"select ".format(db)
        for column in columns:
            query += "{0}, ".format(column)
        query = query.strip(" ").strip(",")
        query += " from {0} where ".format(table)
        i = 0
        for column in where_columns:
            query += "{0} = '{1}' and ".format(column, where_values[i])
            i += 1
        query = query.strip(" and ")
        query += "\";"
        return query


def get_android_version(serial=None, full_version_name=False):

    """ description:
            gets the android version

        tags:
            utils, adb, android, version
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    version = adb_connection.get_prop("ro.build.version.release").strip()
    if full_version_name:
        return version
    if version == "L" or re.match("5.", version):
        version = "L"
    elif re.match("4.4", version):
        version = "K"
    elif version == "m" or re.match("6.", version):
        version = "M"
    return version


def is_prop_set(prop, value, serial=None):
    """
        description:
            check if the prop has the given <value>

        tags:
            utils, adb, prop, value, check
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    return value == adb_connection.get_prop(prop).strip()


def is_power_state(serial=None, state="ON"):

    """ description:
            gets the check the power state of the device

        tags:
            utils, adb, android, power state
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    power_state = "Display Power: state={0}".format(state)
    power_cmd = "dumpsys power"
    return power_state in adb_connection.parse_cmd_output(cmd=power_cmd, grep_for=power_state)


def get_serial(serial=None):

    """ description:
            gets the serial of the device

        tags:
            utils, adb, android, serial
    """

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    serial_no = adb_connection.get_prop("ro.serialno").strip()
    return serial_no


def stay_on(serial=None):

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    adb_connection.parse_cmd_output(cmd="svc power stayon true")


def get_bios_version(serial=None):

    """ description:
            gets bios version from the device

        tags:
            utils, adb, android, bios
    """

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    bios = adb_connection.parse_cmd_output(cmd="cat /sys/devices/virtual/dmi/id/bios_version")
    return bios


def get_running_activities(serial=None):

    """ description:
            gets the running activities

        tags:
            utils, adb, android, activities
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    activities = adb_connection.parse_cmd_output(cmd="dumpsys activity", grep_for="Run #0").split("\n")
    return activities[1].strip().split(" ")[4].strip()


def is_uiautomator_started(serial=None):

    """ description:
            checks if uiautomator RPC server is started on the device

        tags:
            utils, adb, android, version
    """
    # if serial:
    #     adb_connection = connection_adb(serial=serial)
    # else:
    #     adb_connection = connection_adb()
    local_connection = connection_local()
    stdout, stderr = local_connection.run_cmd(command="curl -d \
                                          '{\"jsonrpc\":\"2.0\",\
                                            \"method\":\"deviceInfo\",\
                                            \"id\":1}' \
                                          localhost:9008/jsonrpc/0")
    return "android" in stdout


def folder_exists(folder, serial=None):

    """ description:
            checks if the folder is found on the device

        tags:
            utils, adb, android, folder, exists
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    return "No such file or directory" not in\
           adb_connection.parse_cmd_output(cmd="ls {0}".format(folder), grep_for=folder)


def file_exists(file_path, serial=None):

    """ description:
            checks if the file is found on the device

        tags:
            utils, adb, android, file, exists
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    out = adb_connection.parse_cmd_output(cmd="ls {0}".format(file_path), grep_for=file_path)
    return file_path in out and "No such file or directory" not in out


def is_apk_installed(apk_path, serial=None):

    """ description:
            checks if the apk is found on the device

        tags:
            utils, adb, android, file, exists
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    package_name = android_utils.get_package_name_from_apk(apk_path)

    command = "pm list packages"
    out = adb_connection.parse_cmd_output(cmd=command, grep_for=package_name)
    return package_name in out


def is_package_installed(package_name, serial=None):

    """ description:
            checks if the package is installed on the device

        tags:
            utils, adb, android, file, exists
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    command = "pm list packages"
    out = adb_connection.parse_cmd_output(cmd=command, grep_for=package_name)
    return package_name in out


def sqlite_count_query(db, table, where="1", serial=None):

    """ description:
            returns the count of the entries in the sqlite query

        tags:
            utils, adb, android, sqlite, query, count
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    query = "select count (*) from {0} where {1}".format(table, where)
    command = "sqlite3 {0} '{1}'".format(db, query)
    result = adb_connection.parse_cmd_output(cmd=command, dont_split=True)
    try:
        return int(result)
    except ValueError:
        return False


def check_file_size(value, name, file_path, serial=None):

    """ description:
            checks the size of the <name> file in Download folder has the
            given size <value>

        tags:
            utils, adb, android, file, size, download
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    cmd = "du -k {0} {1}".format(file_path, name)
    output_string = adb_connection.parse_cmd_output(cmd, timeout=5).strip().split()
    file_size = output_string[0]
    return file_size == str(value)


def get_file_size(name, file_path, serial=None):

    """ description:
            gets the size of the <name> file in Download folder

        tags:
            utils, adb, android, file, size, download
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    cmd = "du -k {0}{1}".format(file_path, name)
    output_string = adb_connection.parse_cmd_output(cmd, timeout=5).strip().split()
    file_size = output_string[0]
    return file_size


def check_download_completed(value, name, download_path="/storage/sdcard0/Download/", polling_time=10, max_time=600,
                             serial=None):
    # if serial:
    #   adb_connection = connection_adb(serial=serial)
    # else:
    #   adb_connection = connection_adb()
    value_units = float(value)
    # the file needs to be in the (1 - 999) megabytes interval for this to correctly work
    # also, it assumes that at least the 1st MB of the file is successfully downloaded
    # size needs to be provided in kilobytes
    if not folder_exists(download_path + name, serial=serial):
        return (False, "Download not started. Check server connectivity! Exiting...")
    time_passed = 0
    while time_passed <= max_time:
        size1 = float(get_file_size(name, file_path=download_path, serial=serial))
        time.sleep(polling_time)
        time_passed += polling_time
        size2 = float(get_file_size(name, file_path=download_path, serial=serial))
        if size1 == size2 and size2 < value_units:
            # raise error if the download is no longer progressing
            return (False, "Download Interrupted! Exiting...")
        elif size1 == size2 >= value_units:
            # change size1 == size2 == value_units to size1 == size2 >= value_units, since at simetimes the result
            # got from target may be > the result got from the host, it depends on the du app
            # all good if the final downloaded size equals the expected size
            return (True, "Download completed!")
    if time_passed > max_time:
        # Took longer than 10 minutes. Exiting..."
        return (False, "Download timed out...")


def check_download_progess(value, name, download_path="/storage/sdcard0/Download/", polling_time=10, serial=None):
    # if serial:
    #     adb_connection = connection_adb(serial=serial)
    # else:
    #    # adb_connection = connection_adb()
    value_units = float(value)
    # the file needs to be in the (1 - 999) megabytes interval for this to correctly work
    # also, it assumes that at least the 1st MB of the file is successfully downloaded
    # size needs to be provided in kilobytes
    if not folder_exists(download_path + name, serial=serial):
        return (False, "Download not started. Check server connectivity! Exiting...")
    # time_passed = 0
    # while time_passed <= max_time:
    size1 = float(get_file_size(name, file_path=download_path, serial=serial))
    time.sleep(polling_time)
    # time_passed += polling_time
    size2 = float(get_file_size(name, file_path=download_path, serial=serial))
    if size2 > size1:
        return (True, "Download is progressing")
    elif size1 == size2 and size2 < value_units:
        # raise error if the download is no longer progressing
        return (False, "Download Interrupted! Exiting...")
    elif size1 == size2 >= value_units:
        # change size1 == size2 == value_units to size1 == size2 >= value_units, since at simetimes the result
        # got from target may be > the result got from the host, it depends on the du app
        # all good if the final downloaded size equals the expected size
        return (True, "Download completed!")
    # if time_passed > max_time:
        # Took longer than 10 minutes. Exiting..."
    #    return (False, "Download timed out...")


def get_device_orientation_type(serial=None):

    """ description:
            gets the device orientation type

        tags:
            utils, adb, android, orientation
    """

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    device_type = "phone"
    height = 0
    width = 0
    cmd = "dumpsys display | grep mDefaultViewport=DisplayViewport"
    output_string = adb_connection.parse_cmd_output(cmd, dont_split=True).strip()

    m = re.search(r"deviceHeight=(\d+)", output_string)
    if m:
        height = int(m.group(1))

    m = re.search(r"deviceWidth=(\d+)", output_string)
    if m:
        width = int(m.group(1))

    if width > height:
        device_type = "tablet"
    # else remains set to 'phone'
    # also will return 'phone' as default if no values are found in dumpsys
    return device_type


def is_virtual_keyboard_on(serial=None):

    """ description:
            return true if virtual keybaord is displayed

        tags:
            utils, adb, android, vrtual keyboard
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    return len(adb_connection.parse_cmd_output(cmd="dumpsys input_method", grep_for="mInputShown=true")) > 0


def get_battery_prop(prop=None, serial=None):

    """ description:
            gets the battery properties with dumpsys
        tags:
            utils, adb, android, dumpsys, battery
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    return adb_connection.parse_cmd_output(cmd="dumpsys battery", grep_for=prop, timeout=5).strip()


def get_battery_level(serial=None, path="dollar_cove_battery"):

    """ description:
            gets the battery level with dumpsys

        tags:
            utils, adb, android, dumpsys, battery, level
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    return adb_connection.parse_file(file_name="/sys/class/power_supply/{0}/capacity".format(path)).strip()


def input_keyevent(serial=None, key_number=None):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    command = "input keyevent " + str(key_number)
    return adb_connection.run_cmd(command=command)


def wait_for_file_with_text(text_contained, dir_to_search, serial=None):
    """description:
            waits for a file with certain text in the file name to be created in the given folder

    :param text_contained: text to grep for when looking for the file
    :param dir_to_search: where to look for the file
    :param serial: the DUT serial
    :return: the output if the file is found, None otherwise
    tags:
            utils, adb, android, file, wait, exist
    """

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    # Wait for up to 10 seconds for the file to appear
    for i in range(5):
        out = adb_connection.parse_cmd_output(cmd="ls -l {0}".format(dir_to_search),
                                              grep_for=text_contained)
        if text_contained in out:
            return out
        time.sleep(2)
    return None


def get_dut_date(serial=None, gmt_date=True):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    if gmt_date:
        p = adb_connection.run_cmd(command="date -u")
    else:
        p = adb_connection.run_cmd(command="date")
    date_dut = str(p.stdout.read())
    date_dut = parse(date_dut)
    return date_dut


def is_text_displayed(text_to_find, serial=None, wait_time=100, exists=True):
    remote_file = "/sdcard/window_dump.xml"

    if serial:
        adb_connection = connection_adb(serial=serial)
        local_file = "./window_dump_{0}.xml".format(serial)
    else:
        adb_connection = connection_adb()
        local_file = "./window_dump.xml"

    tries = 0
    pid = adb_connection.get_pid("uiautomator")
    if pid is not None:
        while pid and tries < 5:
            adb_connection.adb_root()
            adb_connection.kill_command(pid=pid)
            time.sleep(1)
            pid = adb_connection.get_pid("uiautomator")
            tries += 1

    current_time = 0
    while current_time < wait_time:
        adb_connection.run_cmd(command="uiautomator dump")

        adb_connection.get_file(remote=remote_file, local=local_file)

        adb_connection.run_cmd(command="rm {0}".format(remote_file))

        with open(local_file, "r") as f:
            read_data = f.read()
            if text_to_find in read_data:
                os.remove(local_file)
                if exists:
                    return True
        os.remove(local_file)
        current_time += 1

    if exists:
        return False
    return True


def is_view_displayed(view_to_find, serial=None, wait_time=100, exists=True):

    """ description:
            Return True if <view_to_find> is visible on screen.

        usage:
            adb_utils.is_view_displayed(view_to_find = {"Text": "text"})

        tags:
            adb, android, view, displayed
    """

    remote_file = "/sdcard/window_dump.xml"

    if serial:
        adb_connection = connection_adb(serial=serial)
        local_file = "./window_dump_{0}.xml".format(serial)
    else:
        adb_connection = connection_adb()
        local_file = "./window_dump_{0}.xml"

    tries = 0
    pid = adb_connection.get_pid("uiautomator")
    if pid:
        while pid and tries < 5:
            # p = adb_connection.adb_root()
            # p = adb_connection.kill_command(pid=pid)
            time.sleep(5)
            pid = adb_connection.get_pid("uiautomator")
            tries += 1

    current_time = 0

    while current_time < wait_time:
        adb_connection.run_cmd(command="uiautomator dump")
        adb_connection.get_file(remote=remote_file, local=local_file)

        adb_connection.run_cmd(command="rm {0}".format(remote_file))
        view = '{0}="{1}"'.format(view_to_find.keys()[0],
                                  view_to_find[view_to_find.keys()[0]])

        with open(local_file, "r") as f:
            read_data = f.read()
            if view in read_data:
                os.remove(local_file)
                if exists:
                    return True

        os.remove(local_file)
        current_time += 1
    if exists:
        return False
    return True


def get_product_name(serial=None):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    product_name = adb_connection.parse_cmd_output(cmd="cat /system/build.prop", grep_for="ro.product.name")
    if product_name:
        return product_name.split("=")[1]
    return False
