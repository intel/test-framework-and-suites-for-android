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
import shutil
import sys
import tarfile
import time
from subprocess import Popen, PIPE


def extract_and_merge(tfile, path):
    path = path if os.path.isdir(path) else os.path.dirname(path)
    tar = tarfile.open(tfile)
    for tarinfo in tar.getmembers():
        if not (tarinfo.name.startswith('src') or tarinfo.name.endswith('xml')):
            ifp = tar.extractfile(tarinfo)
            ofp = open(os.path.join(path, ifp.name), 'wb')
            shutil.copyfileobj(ifp, ofp)
            ifp.close()
            ofp.close()
    tar.close()

    print("Start merge deqp tests.")
    p = Popen('ls %s' % os.path.join(path, "*-*.txt"), stdout=PIPE, shell=True)
    file_list = [i for i in p.communicate()[0].splitlines()]
    _dict = {}
    for i in file_list:
        f_n = i.split('/')[-1]
        h_n = f_n.split('-')[0]
        if h_n not in _dict:
            _dict[h_n] = 1
        else:
            _dict[h_n] += 1
    tmp_file = os.path.join(path, "_tmp.txt")
    for i in _dict:
        if _dict[i] > 1:
            os.system('ls %s | xargs cat | tee -a %s 2>&1 > /dev/null' %
                      (os.path.join(path, i + "-*.txt"), tmp_file))
            os.system('rm -rf %s' % os.path.join(path, i + "-*.txt"))
            os.system('mv %s %s' % (tmp_file, os.path.join(path, i + "-master.txt")))
            print('%s tests have been merged.' % i)

        p = Popen('cat %s | wc -l' % os.path.join(path, i + "-master.txt"), stdout=PIPE, shell=True)
        time.sleep(1)
        _dict[i] = p.communicate()[0].strip()
    print("Summary:" + str(_dict))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Extract all from tar compressed file\n' +
              'Usage: tar_extract.py TAR_FILE OUTPUT_PATH')
        exit(-1)
    extract_and_merge(sys.argv[1], sys.argv[2])
