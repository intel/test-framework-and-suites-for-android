# flake8: noqa
"""
Copyright (C) 2017 Intel Corporation

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
import uuid
import os


uuid = str(uuid.uuid4())
print "UUID: " + uuid
cmd = ' '.join([
    'python ACS.py -d Dummy',
    '-b ACS_CI/BENCHCFG/Bench_Config',
    '-c ACS_CI/TC/FWK/NOVAR/CMD_OPTIONS/rerun/Campaign_rerun',
    '--ll DEBUG',
    '--uuid %s' % uuid
])

ret = os.system(cmd)
print ret
# then rerun
ret = os.system(cmd + ' --rerun')
ret = os.system(cmd + ' --rerun')
print ret
