#!/usr/bin/python

from testlib.base import base_utils
# from testlib.external import uiautomator
# Replacing uiautomator with actual distributed uiautomator instead of one available locally
import uiautomator
from testlib.utils.connections.adb import Adb as connection_adb


class UIDevice(uiautomator.AutomatorDevice):
    __metaclass__ = base_utils.SingletonType

    def __init__(self, **kwargs):
        serial = None
        local_port = None
        self.verbose = False
        if "serial" in kwargs:
            serial = kwargs['serial']
        if "local_port" in kwargs:
            local_port = kwargs['local_port']
        if "verbose" in kwargs:
            self.verbose = kwargs['verbose']
        super(UIDevice, self).__init__(serial=serial, local_port=local_port)

    def dump(self, out_file=None, serial=None, compressed=False):
        if out_file:
            return_value = super(UIDevice, self).dump(filename=out_file, compressed=compressed)
        else:
            return_value = super(UIDevice, self).dump(compressed=compressed)
        if serial:
            adb_connection = connection_adb(serial=serial)
        else:
            adb_connection = connection_adb()
        adb_connection.run_cmd("rm /data/local/tmp/dump.xml", timeout=10)
        adb_connection.run_cmd("rm /data/local/tmp/local/tmp/dump.xml", timeout=10)
        return return_value
