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


class TestStepConstants(object):

    """
    Define all constants for TestStep
    """

    STR_PAR_TSE_ENTRY = "TEST_STEP_ENGINE_ENTRY"
    STR_TS_ID = "Id"
    STR_SET_ID = "SetId"
    STR_FORK_ID = "Id"
    STR_LOOP_ID = "Id"
    STR_IF_ID = "Id"
    STR_LOOP_NB_ITERATION = "Nb"
    STR_IF_CONDITION = "Condition"
    STR_CLASS_ID = "ClassId"
    STR_ALIAS_NAME = "Name"
    STR_SERIALIZE = "Serialize"
    STR_PATH_TEST_STEPS = "TestSteps"
    STR_PATH_ROOT = "/TestCase/" + STR_PATH_TEST_STEPS
    STR_PATH_RUN = "RunTest"
    STR_PATH_INIT = "Initialize"
    STR_PATH_SETUP = "Setup"
    STR_PATH_TEARDOWN = "TearDown"
    STR_PATH_FINALIZE = "Finalize"
    STR_PATH_FORK = "Fork"
    STR_PATH_LOOP = "Loop"
    STR_PATH_IF = "If"
    STR_PATH_INCLUDE = "Include"
    STR_PATH_TEST_STEP = "TestStep"
    STR_PATH_TEST_STEP_SET = "TestStepSet"
    STR_SRC = "Src"

    STR_PARAMETERS = "Parameters"
    STR_PARAM_TYPE = "Type"
    STR_PARAM_IS_OPTIONAL = "isOptional"
    STR_PARAM_DEFAULT_VALUE = "DefaultValue"
    STR_PARAM_POSSIBLE_VALUES = "PossibleValues"
    STR_PARAM_BLANK = "Blank"
