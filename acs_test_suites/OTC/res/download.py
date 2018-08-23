#!/usr/bin/python2
"""
Copyright (C) 2018 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""
import os
import csv
import sys
import time
import shutil
import hashlib
import requests
import argparse


TARGET_ROOT = os.path.expanduser('~/.acs-resources')
TEMP_ROOT = os.path.join(TARGET_ROOT, '.tmp')


def mkdirp(path):
    ''' make sure parent path is created '''
    if os.path.isdir(path):
        dir_path = path
    else:
        dir_path = os.path.dirname(path)
    os.system('mkdir -p ' + dir_path)


mkdirp(TEMP_ROOT)


class Item(object):
    domain = ''
    dst = ''
    src = ''
    cmd = ''

    def __init__(self, d):
        self.domain = d['Domain']
        self.dst = d['Relative Path']
        self.src = d['Original Source']
        self.cmd = d['Convert Commands']

        self.__src = os.path.join(TEMP_ROOT, self._hash_src())
        self.__dst = os.path.join(os.path.expanduser(TARGET_ROOT), self.dst)

    def process(self):
        print('process %s:%s' % (self.domain, self.dst))
        mkdirp(self.__src)
        mkdirp(self.__dst)
        self._download()
        if self.cmd:
            cmds = [
                'export src="%s"' % self.__src,
                'export dst="%s"' % self.__dst,
                self.cmd
            ]
            real_cmd = ';'.join(cmds)
            print('Running cmd: ' + real_cmd)
            os.system(real_cmd)
        else:
            shutil.copy(self.__src, self.__dst)

    def _hash_src(self):
        hash_object = hashlib.md5(self.src)
        return hash_object.hexdigest()

    def _download(self):
        print('downloading file: ' + self.src)
        if os.path.isfile(self.__src):
            print('using file from cache...')
            return
        tempfile = self.__src + '_download'
        fp = open(tempfile, 'wb')
        start_time = time.time()
        r = requests.get(self.src, stream=True)
        content_length = r.headers.get('content-length')
        total_size = int(content_length) if content_length else None
        current_size = 0
        for data in r.iter_content(chunk_size=4096):
            fp.write(data)
            current_size += len(data)
            duration = time.time() - start_time
            speed_KB = (current_size / 1024.0) / duration
            pecentage = ('%.2f%%' % (100.0 * current_size / total_size)) \
                if total_size else 'unknown'
            sys.stdout.write('\r ... %s, %.2f MB, %.2f KB/s, time: %ds' %
                             (pecentage, current_size / (1024 * 1024.0),
                              speed_KB, duration))
            sys.stdout.flush()

        fp.close()
        print('\nDone')
        shutil.move(tempfile, self.__src)


def load_table():
    fname = 'resources.csv'
    fp = open(fname)
    reader = csv.DictReader(fp)
    return [Item(d) for d in reader]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to download resource')
    parser.add_argument('-d', dest='domain', metavar='DOMAIN',
                        help='only download specified domain')
    args = parser.parse_args()

    # change to script root folder
    script_root = os.path.abspath(os.path.dirname(__file__))
    os.chdir(script_root)
    # process file list
    items = load_table()
    for item in items:
        # domain filter
        if args.domain and item.domain != args.domain:
            continue
        item.process()
