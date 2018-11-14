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


class platforms_list(object):
    m_platform_list = ["m_bxtp_abl"]
    o_platform_list = ["o_celadon", "o_cel_apl",
                       "o_gordon_peak", "o_gordon_peak_acrn"]
    p_platform_list = ["p_cel_apl", "p_gordon_peak",
                       "p_gordon_peak_acrn"]
    acrn_flash_list = ["o_gordon_peak_acrn", "p_gordon_peak_acrn"]
    bxt_flash_list = ["m_bxtp_abl", "o_gordon_peak", "p_gordon_peak"]
