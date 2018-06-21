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
import requests
import fcntl
import string
import random
import hashlib
from ConfigParser import ConfigParser
from os.path import exists, join, expanduser, basename, dirname, getsize

from testlib.util.log import Logger
from testlib.util.process import shell_command

LOG = Logger.getlogger(__name__)
REMOTE_PROTOCAL = ['http://', 'https://']
ARTI_LOCAL_REPO = join(expanduser('~'), '.oat-artifactory')


class FileLockException(Exception):
    # Error codes:
    ERROR_CODE = 1


def gen_short(src, length=9, chars=string.ascii_letters + string.digits, prime=694847539):
    """
    Return a string of `length` characters chosen pseudo-randomly from
    `chars` using `value` as the seed and `prime` as the multiplier.
    """
    base = len(chars)
    value = len(src) + random.randint(1, 100)
    domain = base ** length
    assert(1 <= value <= domain)
    n = value * prime % domain
    digits = []
    for _ in xrange(length):
        n, c = divmod(n, base)
        digits.append(chars[c])
    return ''.join(digits)


def file_lock(fd):
    try:
        fcntl.flock(fd.fileno(), fcntl.LOCK_EX)
    except IOError as e:
        raise FileLockException(e)


def file_unlock(fd):
    fcntl.flock(fd.fileno(), fcntl.LOCK_UN)


def _checksum_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as fd:
        while True:
            data = fd.read(8192)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def _revert_path(file_path):
    return file_path.replace(':', '_')


def _read_url_content(file_url):
    raw = requests.get(file_url)
    if raw.status_code == 200:
        return str(raw.text).strip('\n')
    else:
        return None


def _download_file(file_url, local_path):
    raw = requests.get(file_url, stream=True, verify=False)
    # raw = requests.get(file_url, stream=True)
    if not raw:
        return False
    with open(local_path, 'wb') as fd:
        file_lock(fd)
        if not getsize(local_path):
            for chunk in raw.iter_content(chunk_size=1024):
                if chunk:
                    fd.write(chunk)
                    fd.flush()
        file_unlock(fd)
    return True


class _ArtifactoryCached:

    """Artifactory Local Cached Repository"""

    def __init__(self, arti_url=''):
        self._conf = ConfigParser()
        self._conf_file = join(ARTI_LOCAL_REPO, 'config')
        self._section = arti_url or 'localhost'
        if not exists(self._conf_file):
            if not exists(dirname(self._conf_file)):
                os.mkdir(dirname(self._conf_file))
        else:
            self._conf.read(self._conf_file)
        # add section
        if not self._conf.has_section(self._section):
            self._conf.add_section(self._section)
        # rewrite config
        self._conf.write(open(self._conf_file, 'w'))

    def refresh(self, file_path='', file_local=''):
        self._conf.read(self._conf_file)
        self._conf.set(self._section, _revert_path(file_path), file_local)
        self._conf.write(open(self._conf_file, 'w'))

    def fetch(self, file_path, md5_str):
        """return (old, new)"""
        self._conf.read(self._conf_file)
        try:
            _local_path = self._conf.get(
                self._section, _revert_path(file_path))
            if not _local_path:
                return (None, None)
            if not exists(_local_path):
                return (None, None)
            if _checksum_md5(_local_path) != md5_str:
                return (_local_path, None)
            return (None, _local_path)
        except Exception:
            return (None, None)


class Artifactory:

    """Unified Artifactory Access Library"""

    def __init__(self, arti_url='', username='', password=''):
        self._cache = _ArtifactoryCached(arti_url)
        self._drive = arti_url if arti_url else ''
        self._remote = self.__getHost(arti_url)
        self._username = username
        self._password = password

    def __getHost(self, arti_url):
        if not arti_url:
            return False
        for _prot in REMOTE_PROTOCAL:
            if arti_url.startswith(_prot):
                return True
        return False

    def __makeUrl(self, file_path):
        if self._remote:
            return '/'.join([self._drive, file_path])
        else:
            return join(self._drive, file_path)

    def _get_remote_md5_http_protocol(self, file_path):
        url = self.__makeUrl(file_path)
        md5 = None
        try:
            headers = {'User-Agent': 'ACS',
                       "Accept-Encoding": "gzip,text",
                       "Accept": "application/json,text/html",
                       "X-Result-Detail": "info"}
            res = requests.get(url, headers=headers, stream=True, verify=False)
            md5 = res.headers.get('X-Checksum-Md5')
        except:
            pass
        return md5

    def _get_remote_md5(self, file_path):
        md5 = self._get_remote_md5_http_protocol(file_path)
        if (md5):
            return md5
        file_path_md5 = file_path + '.md5'
        try:
            line = _read_url_content(self.__makeUrl(file_path_md5))
            md5_str = line.split(' ')[0]
            if md5_str is not None:
                return md5_str
            file_path_md5sums = join(dirname(file_path), 'MD5SUMS')
            lines = _read_url_content(self.__makeUrl(file_path_md5sums))
            for line in lines.splitlines():
                value, key = line.split(' ')
                if key == basename(file_path):
                    return value
        except:
            pass
        return None

    def get(self, file_path=None):
        if file_path is None:
            return None
        if self._remote:
            local_path = None
            md5_str = self._get_remote_md5(file_path)
            old_path, local_path = self._cache.fetch(file_path, md5_str)
            if local_path:
                LOG.debug('%s is found in local cache !' % file_path)
                return local_path

            LOG.debug('start to download %s from artifactory !' % file_path)
            local_path = join(ARTI_LOCAL_REPO, gen_short(file_path))
            if not exists(local_path):
                os.mkdir(local_path)
            local_path_file = join(local_path, basename(file_path))
            if old_path is not None:
                old_path_file = join(old_path, basename(file_path))
            if _download_file(self.__makeUrl(file_path), local_path_file):
                LOG.debug('complete to download %s !' % file_path)
                if md5_str and _checksum_md5(local_path_file) != md5_str:
                    LOG.debug('check MD5 value failed on file: %s !' %
                              file_path)
                    shell_command('rm -rf %s' % local_path)
                    return None
                self._cache.refresh(file_path, local_path_file)
                if old_path is not None:
                    shell_command('ln -sf %s %s' %
                                  (local_path_file, old_path_file))
                return local_path_file
            else:
                LOG.debug('failed to download %s!' % file_path)
                return None
        else:
            return self.__makeUrl(file_path)
