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

from testlib.utils.ui.uiandroid import UIDevice as ui_device
# from testlib.base import base_utils
from testlib.utils.connections.adb import Adb as connection_adb
from testlib.scripts.android.adb import adb_utils


def check_google_account(serial=None):
    """
    description:
        check if a Google account is configured on DUT.
        Return True if the Google account is configured.

    usage:
        gms_utils.check_google_account()

    tags: google account, account, google, check google
    """
    if serial:
        uidevice = ui_device(serial=serial)
        adb_connection = connection_adb(serial=serial)
    else:
        uidevice = ui_device()
        adb_connection = connection_adb()

    string = "Starting: Intent { act=android.settings.SYNC_SETTINGS }"
    command = "am start -a android.settings.SYNC_SETTINGS"
    if (string in adb_connection.parse_cmd_output(cmd=command, grep_for="Starting: Intent")):
            if uidevice(text="Google").exists:
                uidevice.press.recent()
                uidevice.wait.update()
                if uidevice(text="Accounts").wait.exists(timeout=5000):
                    uidevice(text="Accounts").swipe.right()
                return True
            else:
                uidevice.press.recent()
                uidevice.wait.update()
                if uidevice(text="Accounts").wait.exists(timeout=5000):
                    uidevice(text="Accounts").swipe.right()
                return False
    else:
        print "The settings.SYNC_SETTINGS activity doesn't start"
        return False


def get_google_account_number(serial=None):
    """
    description:
        this fubction return the google account number configured on DUT
        Return 0 if there is no Google account configured.

    usage:
        gms_utils.get_google_account_number()

    tags: google account, account number, google, check google, account
    """

    db = "/data/system/users/0/accounts.db"
    table = "accounts"
    return adb_utils.sqlite_count_query(serial=serial, db=db, table=table)
