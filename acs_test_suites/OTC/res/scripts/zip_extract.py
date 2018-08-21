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
import sys
import shutil
import zipfile


def extract(zfile, path, ofile):
    with zipfile.ZipFile(zfile, 'r') as z:
        with z.open(path) as ifp, open(ofile, 'wb') as ofp:
            shutil.copyfileobj(ifp, ofp)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Extract a file from zip compressed file\n' +
              'Usage: zip_extract.py ZIP_FILE PATH_IN_ZIP OUTPUT_PATH')
        exit(-1)
    extract(sys.argv[1], sys.argv[2], sys.argv[3])
