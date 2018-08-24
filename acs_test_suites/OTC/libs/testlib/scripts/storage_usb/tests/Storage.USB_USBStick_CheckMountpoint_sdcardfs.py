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

from testlib.base.base_utils import parse_args
from testlib.scripts.storage_usb import storage_usb_steps

args = parse_args()

storage_usb_steps.CheckSDCardMount(serial=args["serial"])()
storage_usb_steps.CheckMountstats('sdcardfs',
                                  'mmcblk0p1',
                                  serial=args["serial"]
                                  )()
