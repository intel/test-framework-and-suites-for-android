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

from acs.Core.TestStep.TestStepContext import TestStepContext
from acs.UtilitiesFWK.Utilities import AcsConstants
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.Core.TestStep.TestStepParameters import TestStepParameters


class TestStepBase(object):

    """
    Implements base test step. It must be ancestor of each test step.

    .. uml::

        class Parameters {
            infer_pars(pars)
            replace_static_pars_refs(tc_parameters, global_conf)
            replace_dynamic_pars_refs(context)
            get_attr(name)
            check_pars(global_conf)
        }

        class TestStepBase {
            name()
            run(context)
            call_by_engine()
        }

        TestStepBase *- Parameters : contains
    """

    def __init__(self, tc_conf, global_conf, ts_conf, factory):
        """
        Constructor
        :type tc_conf: :py:class:`~acs.Core.TCParameters`
        :param tc_conf: test case parameters
        :type  global_conf: object
        :param global_conf: global configuration data
        :type  ts_conf: object
        :param ts_conf: test steps parameters
        :type  factory: object
        :param factory: it's responsible for creating ACS objects needed by the test step
        """
        # Set the name of the test step
        self._name = self.__class__.__name__

        if tc_conf is not None:
            self._testcase_name = tc_conf.get_name()
            self._conf = tc_conf
            self._tc_parameters = tc_conf.get_params()
        else:
            self._testcase_name = "Unknown"
            self._conf = None
            self._tc_parameters = None

        self._factory = factory
        self._logger = self._factory.create_test_step_logger()

        if ts_conf is not None:
            # It can happen that ts_conf is already a TestStepContext. If that's the case
            # just use it (instead of create a new one)
            if isinstance(ts_conf, TestStepContext):
                self._ts_conf = ts_conf
            else:
                self._ts_conf = TestStepContext(ts_conf)
        else:
            self._ts_conf = None

        self._pars = TestStepParameters(self._factory)

        # Used for test step verdict message purpose
        self._ts_verdict_msg = AcsConstants.NO_ERRORS

        # New mechanism to infer parameters automatically
        # the test step will have an object _pars which will contain the use case and
        # test case variables as object members
        if self._tc_parameters is not None:
            self._pars.infer_pars(self._tc_parameters.get_params_as_dict())

        if self._ts_conf is not None:
            self._pars.infer_pars(self._ts_conf.ref_dict())

        self._global_conf = global_conf

        # Replaces references found for static fields (i.e. bench config, test case, etc..)
        # If an exception is raised it gets caught and raised in the run method.
        # This is to avoid the constructor to raise an exception.
        self._init_exc = None
        self._safe_replace_static_pars()

        self._context = None
        self._run_by_engine = False

    @property
    def ts_verdict_msg(self):
        """
        Name of the test step

        :rtype: str
        :return: return the name of the test step.
        """
        return self._ts_verdict_msg

    @ts_verdict_msg.setter
    def ts_verdict_msg(self, ts_verdict_msg):
        """
        :type ts_verdict_msg: str
        :param ts_verdict_msg: Test step nice name
        """
        self._ts_verdict_msg = ts_verdict_msg

    @property
    def name(self):
        """
        Name of the test step

        :rtype: str
        :return: return the name of the test step.
        """
        return self._name

    @name.setter
    def name(self, ts_name):
        """
        :type ts_name: str
        :param ts_name: Test step nice name
        """
        self._name = ts_name

    def _safe_replace_static_pars(self):
        """
        Calls _pars.replace_static_pars catching exceptions if any (to avoid raising it from the constructor)
        If an exception occurs, it will be raised in the run as first thing.
        """
        try:
            self._pars.replace_static_pars_refs(self._tc_parameters, self._global_conf)
        except AcsConfigException as exc:
            self._init_exc = exc

    def run(self, context):
        """
        Runs the test step

        :type context: :py:class:`~acs.Core.TestStep.TestStepContext`
        :param context: the test case context
        :raise: AcsConfigException
        """

        self._raise_init_exception_if_exists()

        full_class_name = "%s.%s" % (self.__module__, self.__class__.__name__)

        if self._run_by_engine:
            # log in acs logs
            self._logger.info("Executing %s step..." % (self._pars.id,))
        self._logger.debug("Using class %s ..." % (full_class_name,))

        self._context = context

        # Replace parameters references with their values (if any)
        self._pars.replace_dynamic_pars_refs(context)
        # Check parameter's value
        self._pars.check_pars(self._global_conf)

    def call_by_engine(self):
        """
        Set the test step has been run by the test step engine
        """
        self._run_by_engine = True

    def _raise_init_exception_if_exists(self):
        """
        If an ACS exception was caught in the constructor, now it's the good time to raise it
        """
        if self._init_exc:
            raise AcsConfigException(self._init_exc.get_generic_error_message(), self._init_exc.get_specific_message())

    def _raise_config_exception(self, msg, category=AcsConfigException.INVALID_PARAMETER):
        """
        Raise an exception; It can be used in inheriting classes to log and raise an exception
        in a consistent manner.
        """
        self._logger.error(msg)
        raise AcsConfigException(category, msg)
