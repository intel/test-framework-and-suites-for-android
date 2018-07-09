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
"""
Check artifact is in cache folder
Clean cache folder
"""
import os
import shutil
from acs.Core.Equipment.EquipmentManager import EquipmentManager

VERDICT = FAILURE
OUTPUT = "Artifact has not been retrieved"
artifact = TC_PARAMETERS("ARTIFACT_NAME")

if artifact:
    artifact = os.path.normpath(artifact)
    PRINT_INFO("Put in cache : %s" % artifact)
    artifact_manager = EquipmentManager().get_artifact_manager("ARTIFACT_MANAGER")
    cache_path = artifact_manager.cache_artifacts_path
    expected_downloaded_artifact = os.path.join(cache_path, artifact)
    if os.path.isfile(expected_downloaded_artifact):
        VERDICT = SUCCESS
        OUTPUT = "Artifact has been retrieved as %s" % (expected_downloaded_artifact)

    if os.path.isdir(cache_path):
        shutil.rmtree(cache_path)
else:
    OUTPUT = "missing artifact parameter !"
