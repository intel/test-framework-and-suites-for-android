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
from acs.Core.Equipment.EquipmentManager import EquipmentManager

VERDICT = FAILURE
OUTPUT = "Fake Artifact cannot be created"
artifact = TC_PARAMETERS("ARTIFACT_NAME")

if artifact:
    artifact = os.path.normpath(artifact)
    PRINT_INFO("Create fake : %s" % artifact)
    artifact_manager = EquipmentManager().get_artifact_manager("ARTIFACT_MANAGER")
    cache_path = artifact_manager.cache_artifacts_path
    expected_downloaded_artifact = os.path.join(cache_path, artifact)
    if os.path.isfile(expected_downloaded_artifact):
        PRINT_INFO("Removing existing file : %s" % expected_downloaded_artifact)
        os.remove(expected_downloaded_artifact)

    with open(expected_downloaded_artifact, "w") as f:
        f.write("Fake Artifact")

    VERDICT = SUCCESS
    OUTPUT = "Fake artifact %s has been generated" % expected_downloaded_artifact
    PRINT_INFO("Fake artifact %s has been generated" % expected_downloaded_artifact)

else:
    OUTPUT = "missing artifact parameter !"
