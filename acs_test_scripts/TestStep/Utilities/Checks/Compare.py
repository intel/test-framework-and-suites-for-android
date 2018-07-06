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
from acs.Core.TestStep.TestStepBase import TestStepBase
from acs.UtilitiesFWK.Utilities import is_number
from acs.ErrorHandling.AcsConfigException import AcsConfigException


class Compare(TestStepBase):
    """
    Check that two values satisfy the operation
    identified by the given operator
    """
    EQ = "EQUAL"
    NE = "NOT_EQUAL"
    GT = "GREATER"
    LT = "LESS"
    GE = "GREATER_OR_EQUAL"
    LE = "LESS_OR_EQUAL"
    IN = "IN"
    WITHIN_BOUNDS = "WITHIN_BOUNDS"

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        """
        TestStepBase.__init__(self, tc_conf, global_conf, ts_conf, factory)

    def run(self, context):
        """
        Runs the test step

        :type context: TestStepContext
        :param context: test case context
        """

        TestStepBase.run(self, context)

        assert self._pars.operator in [self.EQ, self.NE, self.GT,
                                       self.LT, self.GE, self.LE,
                                       self.IN, self.WITHIN_BOUNDS], \
            "Operator value is invalid (it should have been checked by the framework)"  # noqa

        if self._pars.operator == self.IN:
            passed = self._pars.first in self._pars.second
        else:
            passed = self._compare_using_math_operators()

        passed = self._invert_passed_if_needed(passed)

        if not passed:
            self._raise_config_exception(AcsConfigException.OPERATION_FAILED,
                                         "Comparison is not satisfied")

    def _compare_using_math_operators(self):
        interval_radius = None
        if self._pars.operator == self.WITHIN_BOUNDS:
            temp = self._pars.second.split(',')
            if len(temp) == 2:
                self._pars.second = temp[0]
                interval_radius = temp[1]
            else:
                self._raise_config_exception(
                    "Must have exactly 2 elements " +
                    "in a comma separated list for SECOND",
                    AcsConfigException.OPERATION_FAILED)
            if is_number(self._pars.first) \
                    and is_number(self._pars.second) \
                    and is_number(interval_radius):
                first = float(self._pars.first)
                second = float(self._pars.second)
                interval_radius = float(interval_radius)
            else:
                self._raise_config_exception(
                    "FIRST, SECOND and interval_radius" +
                    "(2nd element derived from separating SECOND) " +
                    "must be both numbers",
                    AcsConfigException.OPERATION_FAILED)

            msg = "Evaluate {0} {1} {2} with interval radius {3}; " \
                + "it's expected to be {4}"
            self._logger.info(msg.format(first, self._pars.operator, second,
                                         interval_radius, self._pars.pass_if))
        else:
            if is_number(self._pars.first) and is_number(self._pars.second):
                first = float(self._pars.first)
                second = float(self._pars.second)
            else:
                first = str(self._pars.first)
                second = str(self._pars.second)

            self._logger.info("Evaluate %s %s %s; it's expected to be %s" % (
                str(first),
                self._pars.operator,
                str(second),
                str(self._pars.pass_if)))

        return self._do_compare(first, second,
                                self._pars.operator, interval_radius)

    def _invert_passed_if_needed(self, passed):
        # if pass_if == False it means the test passes
        # if the condition is not verified
        if self._pars.pass_if is False:
            passed = not passed
        return passed

    def _do_compare(self, first, second, operator, interval_radius):
        """
        Execute comparison and returns True if it succeeds, or False otherwise
        """
        if operator == self.EQ:
            passed = first == second
        elif operator == self.NE:
            passed = first != second
        elif operator == self.LT:
            passed = first < second
        elif operator == self.GT:
            passed = first > second
        elif operator == self.LE:
            passed = first <= second
        elif operator == self.WITHIN_BOUNDS:
            passed = (second - interval_radius) <= first <= (second + interval_radius)  # noqa
        else:
            assert operator == self.GE
            passed = first >= second

        return passed
