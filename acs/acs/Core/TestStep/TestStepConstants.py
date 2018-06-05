"""
:copyright: (c)Copyright 2013, Intel Corporation All Rights Reserved.
The source code contained or described here in and all documents related
to the source code ("Material") are owned by Intel Corporation or its
suppliers or licensors. Title to the Material remains with Intel Corporation
or its suppliers and licensors. The Material contains trade secrets and
proprietary and confidential information of Intel or its suppliers and
licensors.

The Material is protected by worldwide copyright and trade secret laws and
treaty provisions. No part of the Material may be used, copied, reproduced,
modified, published, uploaded, posted, transmitted, distributed, or disclosed
in any way without Intel's prior express written permission.

No license under any patent, copyright, trade secret or other intellectual
property right is granted to or conferred upon you by disclosure or delivery
of the Materials, either expressly, by implication, inducement, estoppel or
otherwise. Any license under such intellectual property rights must be express
and approved by Intel in writing.

:organization: INTEL MCG PSI
:summary: This module defines all constants used by TestStep
:since: 09/12/13
:author: ssavrim
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
