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
# @PydevCodeAnalysisIgnore
# pylint: disable=E0602,W0212
import acs.UtilitiesFWK.Utilities as Utils


exceptionName = TC_PARAMETERS("EXCEPTION_NAME")  # @UndefinedVariable


if exceptionName is not None:
    ucase_class = Utils.get_class(exceptionName)
    raise ucase_class(ucase_class.OPERATION_FAILED, exceptionName + " has been raised")
