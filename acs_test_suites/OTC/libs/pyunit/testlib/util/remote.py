'''
Copyright (C) 2016 Intel Corporation
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
import json
import socket
import random
import requests
from testlib.util.device import TestDevice
from testlib.util.config import TestConfig
from testlib.util.log import Logger


logger = Logger.getlogger()
URL_BASE = None


def get_url_base():
    global URL_BASE
    if not URL_BASE:
        logger.info('get remote server from config')
        config = TestConfig()
        server = config.getConfValue(section='remote', key='server')
        if not server:
            msg = '\n'.join([
                'No remote server found',
                'Please add below section to /etc/oat/sys.conf :',
                '[remote]',
                'server=REMOTE-SERVER',
            ])
            raise Exception(msg)
        URL_BASE = 'http://%s' % server
    return URL_BASE


def request(method, url, params=None, data=None):
    url_base = get_url_base()
    if not url.startswith(url_base):
        fullurl = url_base + url
    else:
        fullurl = url
    logger.debug('request: %s %s params: %s data: %s'
                 % (method, url, params, data))
    m = getattr(requests, method)
    r = m(fullurl, params=params, data=json.dumps(data))
    if r.status_code != 200:
        logger.warning('request not success, code: %s, resp: %s'
                       % (r.status_code, r.text))
    return r.status_code, r.json()


class Service(object):
    def __init__(self, url):
        self.url = url
        self.acquired = False
        self.test_device = None
        self.data = None

    def acquire(self):
        acquire_url = self.url + '/acquire'
        hostname = socket.gethostname()
        data = {'by': hostname}
        code, r = request('put', acquire_url, data=data)
        if code != 200:
            return False
        self.acquired = True
        self.data = r['data']
        self.test_device = self._get_test_device(r['device']['href'])
        return True

    def release(self):
        release_url = self.url + '/release'
        code, r = request('put', release_url)
        if code != 200:
            return False
        else:
            return True

    def get_test_device(self):
        return self.test_device

    def get_service_data(self):
        return self.data

    def _get_test_device(self, url):
        '''
        get TestDevice from url
        '''
        code, r = request('get', url)
        serial = r['serial']
        adb_server_host = r['host']['host']
        adb_server_port = r['host']['adb_server_port']
        logger.info("TestDevice created, serial: %s, host: %s:%s" %
                    (serial, adb_server_host, adb_server_port))
        return TestDevice(serial=serial,
                          adb_server_host=adb_server_host,
                          adb_server_port=adb_server_port)


class RemoteManager(object):
    def __init__(self):
        self._acquires = []

    def get_service(self, name):
        '''
        get a service by name

        return (device, service_info)
        '''
        url = '/api/services/%s/avails' % name
        code, avails = request('get', url)
        if code != 200:
            raise Exception('get %s return %s' % (url, code))
        # in order not to over-use first device, adapt random here
        while avails:
            total = len(avails)
            i = random.randint(0, total - 1)
            avail = avails.pop(i)
            service = Service(avail['href'])
            success = service.acquire()
            if success:
                self._acquires.append(service)
                return service
        else:
            raise Exception("%s: can't acquire any available service" % name)

    def cleanup(self):
        for serv in self._acquires:
            if serv.acquired:
                serv.release()
