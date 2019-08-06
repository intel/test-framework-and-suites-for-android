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

import os
import re
import sys
import traceback
from datetime import datetime
from inspect import stack

try:
    from lxml import etree
except ImportError:
    from xml import etree


from acs.Core.Report.ACSLogging import LOGGER_FWK, RAW_LEVEL
from acs.Core.PathManager import Paths
from acs.ErrorHandling.AcsConfigException import AcsConfigException
from acs.ErrorHandling.AcsBaseException import AcsBaseException
from acs.UtilitiesFWK.AcsSubprocess.AcsSubprocess import AcsSubprocess


# Non blocking readline
ON_POSIX = 'posix' in sys.builtin_module_names


class Singleton(type):

    """
    Add this class as __metaclass__ in your class if you need to use it as singleton

    .. code-block:: python

        from acs.UtilitiesFWK.Utilities import Singleton

        class myClass(object):
            __metaclass__ = Singleton
    """
    __instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance

    def instance(cls):
        cls()
        return cls.__instance


class Measurements(object):

    """
    This Class handles some common units measurement

    .. todo:: Implements Connection Speed units measurement chart or whatever makes sense

        (BPS_UNIT, KBPS_UNIT, MBPS_UNIT) = (['bits/sec', 'Bits/sec', 'bps', 'Bps'],
                                           ['kbits/sec', 'Kbits/sec', 'Kbps', 'kbps'],
                                           ['Mbits/sec', 'mbits/sec', 'Mbps', 'mbps'])

        class NetworkSpeed(object):

            BPS = ['bits/sec', 'Bits/sec', 'bps', 'Bps']
            ...

    """

    class Data(object):

        """
        This class provides Data measurements

        """

        KB = 1024
        MB = 1024 * KB
        GB = 1024 * MB
        TB = 1024 * GB
        PB = 1024 * TB


class AcsConstants(object):

    """
    This class contains global variable which can be used everywhere in acs framework
    Some string values are reused in acs framework
    This class will help avoiding variable mispelling
    """
    DEVICE_NAME_PREFIX = "PHONE"
    DEFAULT_DEVICE_NAME = "{0}1".format(DEVICE_NAME_PREFIX)

    NOT_AVAILABLE = "Not available"
    NOT_INSTALLED = "Not installed"
    NO_ERRORS = "No errors"


class Verdict(object):

    """ Verdict

        This class implements all the possible verdict a TC can have:
        - PASS
        - FAIL
        - BLOCKED
        - INTERRUPTED
    """
    (PASS, FAIL, BLOCKED, INTERRUPTED,
     INCONCLUSIVE, INVALID, VALID, NA) = ("PASS", "FAIL", "BLOCKED", "INTERRUPTED",
                                          "INCONCLUSIVE", "INVALID", "VALID", "NA")

    @classmethod
    def is_pass(cls, verdict):
        return verdict in [cls.PASS, cls.INCONCLUSIVE, cls.VALID]

    @classmethod
    def compute_verdict(cls, expected_verdict, obtained_verdict):
        """
        Compute the verdict regarding expected verdict.
        :type expected_verdict: string
        :param expected_verdict : The expected verdict

        :type obtained_verdict: string
        :param obtained_verdict : Verdict returned by the test case

        :rtype: string
        :return: Verdict (PASS, FAIL, BLOCKED)
        """

        # Initialize the reported verdict to obtained verdict
        reported_verdict = obtained_verdict

        if expected_verdict == obtained_verdict:
            reported_verdict = cls.PASS

        else:
            if expected_verdict == cls.BLOCKED:
                reported_verdict = cls.FAIL

            elif expected_verdict == cls.FAIL and obtained_verdict == cls.PASS:
                reported_verdict = cls.FAIL

        return reported_verdict


class Status(object):

    """ Status

        This class implements all the possible status value for a test campaign execution:
        - INIT
        - ONGOING
        - ABORTED
        - COMPLETED
    """
    (INIT, ONGOING, ABORTED, COMPLETED) = ("INIT", "ONGOING", "ABORTED", "COMPLETED")


class Global(object):

    """
    Global returning use case verdict
    """
    # Code to return in case of success execution
    SUCCESS = 0
    # Code to return in case of a valid measurement/execution,
    # but needs user's actions to determine if test run is SUCCESS or FAILURE
    VALID = 1
    # Code to return in case of further user's analysis is required to determine if test run is SUCCESS or FAILURE
    INCONCLUSIVE = 2
    # Code to return in case of failed execution
    FAILURE = -1
    # Code to return in case the test cannot be run
    BLOCKED = -2
    # Code to return in case the result is known to be wrong/inaccurate
    INVALID = -3
    # Code to return in case the test is not applicable to run, like dependence hardware is not available
    NA = -4


class Verdict2Global(object):

    """

    """

    map = {
        Verdict.PASS: Global.SUCCESS,
        Verdict.VALID: Global.VALID,
        Verdict.FAIL: Global.FAILURE,
        Verdict.BLOCKED: Global.BLOCKED,
        Verdict.INTERRUPTED: Global.BLOCKED,
        Verdict.INCONCLUSIVE: Global.INCONCLUSIVE,
        Verdict.INVALID: Global.INVALID,
        Verdict.NA: Global.NA
    }


def global_to_bool(value):
    """
     Convert Global result to boolean result
    :param value:
    :return:
    """
    return value == Global.SUCCESS


def error_to_verdict(error):
    """
     Convert Error to Verdict
    :param error:
    :return:
    """
    verdict = {y: x for x, y in Verdict2Global.map.iteritems()}
    return verdict[error]


class Error(object):

    """ Error

    This class implements the error structure:
    - Code: Error code (0 is a success, else a failure)
    - Msg: String giving more details for both success & failures
    """
    Code = Global.SUCCESS
    Msg = AcsConstants.NO_ERRORS

    @property
    def Verdict(self):
        return error_to_verdict(self.Code)


class ExitCode(object):

    """Global exit code value"""
    SUCCESS = 0
    FAILURE = -1

    @staticmethod
    def getExitCodeMsg(result):
        msg = None
        for key, value in ExitCode.__dict__.items():
            if not key.startswith('_') and value == result:
                msg = key
                break
        return msg


class DeviceState(object):

    """
    Global power state value

    Device Power States Enum::

        * OFF ("POWEROFF")
        * ON ("POWERON")
        * COS ("CHARGING")
        * NC ("NOCHANGE")
        * UNKNOWN ("UNKNOWN_STATE")

    .. note:: The ``NOCHANGE`` State can be obtained according two different cases,

        * On User demand, in **Bench_Config**, *finalDutState* field.
        * Before the device is initialized (sort of DISCOVERING mode)

    """

    OFF = "POWEROFF"
    ON = "POWERON"
    COS = "CHARGING"
    NC = "NOCHANGE"
    UNKNOWN = "UNKNOWN_STATE"

    @classmethod
    def isDeviceState(cls, device_state):
        """
        Check if if the passed State is included in available States or not

        :param device_state: The Device State

        :return: the validation
        :rtype: bool
        """
        return device_state in cls.availableState()

    @classmethod
    def availableState(cls):
        """
        Available Device's States

        :return: A tuple of Device's states
        """
        return cls.OFF, cls.ON, cls.COS, cls.NC


class ACSResult(object):

    """ ACS result structure which contains :
        - a verdict
        - a dut state value
        - a status
    """

    def __init__(self, verdict=Global.FAILURE, dut_state=DeviceState.NC, status=""):
        self.verdict = verdict
        self.dut_state = dut_state
        self.status = status


class TestConst(object):

    """
    Constants that recurs in test cases or test steps as per parameter names,
    parameter values, etc...
    """
    # True and False string representation
    STR_TRUE = "true"
    STR_FALSE = "false"
    STR_ON = "on"
    STR_OFF = "off"
    STR_YES = "yes"
    STR_NO = "no"
    STR_ON_1 = "1"
    STR_OFF_0 = "0"
    STR_RESTORE = "restore"
    STR_ENABLE = "enable"
    STR_DISABLE = "disable"
    STR_TRUE_SET = [STR_TRUE, STR_ON, STR_YES, STR_ON_1]
    STR_FALSE_SET = [STR_FALSE, STR_OFF, STR_NO, STR_OFF_0]
    STR_BOOL_SET = [STR_TRUE, STR_FALSE, STR_ON, STR_OFF, STR_YES, STR_NO, STR_ON_1, STR_OFF_0]
    # Constant type
    STR_STRING = "string"
    STR_BOOL = "boolean"
    STR_INTEGER = "integer"
    STR_FLOAT = "float"


class Dictionary(dict):

    """
    Dictionary

    This class implements dictionaries.

    """

    _re_attribute = re.compile(ur'\b(attribute[1-6])\b', re.IGNORECASE)

    def __init__(self, indict=None, **attributes):

        indict = indict or {}
        # set any attributes here - before initialisation
        # these remain as normal attributes

        for name, value in attributes.iteritems():
            if self._re_attribute.match(name):
                setattr(self, name, value)

        super(Dictionary, self).__init__(indict)

        self.__initialised = True
        # after initialisation, setting attributes is the
        # same as setting an item

    def __getattr__(self, item):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    def __setattr__(self, item, value):
        """Maps attributes to values.
        Only if we are initialised
        """
        # this test allows attributes to be set in the __init__ method
        if '_Dictionary__initialised' not in self.__dict__:
            return super(Dictionary, self).__setattr__(item, value)
        # any normal attributes are handled normally
        elif item in self.__dict__:
            super(Dictionary, self).__setattr__(item, value)
        else:
            self.__setitem__(item, value)


def format_exception_info():
    """
    formats Exception info

    This function implements the formatting of exception info.

    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    return traceback.format_exception(exc_type, exc_value, exc_tb)


def get_exception_info(exception=None):
    """
    This function implements the getter of exception info.

    .. note:: This method is useful for ACS defined exception, because they
    implement two specific class attributes.
    Otherwise the returned values are set accordingly.

    :rtype: list
    :return: Error Code and Error Message and String formatted traceback
    """
    exc_value, exc_tb = sys.exc_info()[1:]

    try:
        ex_error_code = exc_value.get_error_code()
        ex_error_msg = exc_value.get_error_message()
        ex_error_tb = str(traceback.format_tb(exc_tb))
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        ex_error_code = Global.FAILURE
        ex_error_msg = str(exc_value)
        ex_error_tb = str(traceback.format_tb(exc_tb))
    finally:
        sys.exc_clear()

    if not ex_error_msg and exception:
        ex_error_msg = "{0}".format(exception)

    return ex_error_code, ex_error_msg, ex_error_tb


def get_class(kls):
    """
    Instantiate a class according to a module path + class name

    :type   kls: string
    :param  kls: module path + class name

    :rtype:     module
    :return:    Instance of the class
    """
    try:
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        try:
            mod = __import__(module)
        except ImportError as AttributeError:
            mod = __import__('acs.' + module)
            parts.insert(0, 'acs')
        for comp in parts[1:]:
            mod = getattr(mod, comp)
    except (ImportError, IndexError, AttributeError) as exc:
        msg = "Cannot import class: '%s' (%s)" % (kls, repr(exc))
        raise AcsConfigException(AcsConfigException.INVALID_PARAMETER, msg)
    return mod


def str_to_bool(text):
    """
    This function evaluates a string (True, False) into a boolean value

    :type text: str
    :param text: String to be evaluated

    :rtype: bool
    :return: True or False

    >>> str_to_bool("True")
    True
    >>> str_to_bool("TRUE")
    True
    >>> str_to_bool("False")
    False
    >>> str_to_bool("FALSE")
    False

    """
    return text.lower() == 'true'


def is_bool(text):
    """
    This function checks if a string is a boolean
    ("True" or "False")

    :type   text: string
    :param  text: string to be tested

    :rtype:     bool
    :return:    True if it is a boolean, False otherwise

    >>> is_bool("True")
    True
    >>> is_bool("False")
    True
    >>> is_bool("1")
    False
    >>> is_bool("miqmhdflk")
    False

    """
    return text.lower() == 'true' or text.lower() == 'false'


def str_to_bool_ex(text):
    """
    Accepts as bool value one of the boolean representation
    such as [true, on, 1, yes] for True and [false, off, 0, no] for False
    if none of the above is matched it returns None

    :type   text: string
    :param  text: string representing a boolean value

    :rtype:     bool
    :return:    Boolean value True or False

    >>> str_to_bool_ex("true")
    True
    >>> str_to_bool_ex("1")
    True
    >>> str_to_bool_ex("yes")
    True
    >>> str_to_bool_ex("on")
    True
    >>> str_to_bool_ex("false")
    False
    >>> str_to_bool_ex("off")
    False
    >>> str_to_bool_ex("0")
    False
    >>> str_to_bool_ex("no")
    False

    """
    if str(text).lower() in TestConst.STR_TRUE_SET:
        value = True
    elif str(text).lower() in TestConst.STR_FALSE_SET:
        value = False
    else:
        value = None

    return value


def strip_list(items):
    """
    Strip each element of the array
    """
    return [x.strip() for x in items]


def split_and_strip(item, char=','):
    """
    Take a string and creates an array of stripped elements
    """
    items = item.split(char)
    return strip_list(items)


def is_number(text):
    """
    This function checks if a string is a number,
    positive or negative value.

    :type   text: string
    :param  text: string to be tested

    :rtype: boolean
    :return: True if is a number, else False
    """
    try:
        float(text)
        return True
    except ValueError:
        return False


def forced_str(value):
    """
    convert an object to an str in any case
    avoiding any unicode crash during conversion

    :type   value: object
    :param  value: object to be cast in str

    :rtype: str
    :return: str value of the object
    """
    try:
        value = str(value)
    except UnicodeEncodeError:
        # obj is unicode
        value = str(unicode(value).encode('unicode_escape'))
    return value


def str_to_dict(text):
    """
    This function converts a string to a dictionary

    :type   text: string
    :param  text: string to be converted
    String to be converted should be as follow :
        string_to_convert="key1:value1,key2:value2..."
        result={'key1':'value1', 'key2':'value2'}

    :rtype: dict
    :return: string converted to a dictionary
    """
    string_to_dict = {}
    splitted_text = [str(x).split(":") for x in str(text).split(",")]
    for dict_element in splitted_text:
        if dict_element[0]:
            string_to_dict.update({dict_element[0]: dict_element[1]})
    return string_to_dict


def str_to_list(text):
    """
    This function converts a string to a list

    :type   text: string
    :param  text: string to be converted
    String to be converted should be as follows :
        string_to_convert="value1[|]value2[|]..."
        result=[value1, value2, ...]

    :rtype: list
    :return: string converted to a list
    """
    import ast

    params_list = []
    if text.strip() != "":
        for params_section in text.split("[|]"):
            # Use ast.literal_eval to convert substrings that are string representations of other data types
            try:
                params_list.append(ast.literal_eval(params_section))
            except SyntaxError:
                # If there is any issue in the formatted string containing a list of
                # values (format not recognized), user shall be informed.
                _, error_msg, _ = get_exception_info()
                msg = "Fail to read the string list: %s - Exception = %s." % \
                    (text, error_msg) + \
                    "List shall have following format: value1|value2|...|valuen"
                raise AcsConfigException(
                    AcsConfigException.READ_PARAMETER_ERROR, msg)

            except ValueError:
                # If this section is a string without spaces,
                # and user didn't delimit it with quotes,
                # then it will throw an exception.
                # Let's be nice and add the quotes automatically
                # so we don't make users clutter the XML files
                # with quotes inside of quotes.
                # We're not doing anything to tolerate
                # unquoted strings with spaces --
                # those will throw an unhandled exception.
                params_list.append(ast.literal_eval("'%s'" % params_section))

    return params_list


def time_from_seconds(seconds):
    """
    Convert an amount of seconds into its corresponding (d, h, m, s) match.

    :param seconds: the time in seconds
    :type seconds: str | int | float
    :return: time(day(s), hour(s), minute(s), second(s))
    :rtype: tuple
    """
    if not isinstance(seconds, float):
        # Will raise if passed type is not correct
        seconds = float(seconds)

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    return d, h, m, s


def readable_time_from_seconds(seconds):
    """
    Format the time tuple into human readable string

    :param seconds: the time in seconds
    :type seconds: str | int | float
    :return: formatted string
    :rtype: str
    """
    return '{0} day(s {1} hours {2} minutes {3} seconds'.format(*time_from_seconds(seconds))


def dec2bin(d, nb=8):
    """
        Convert dec to binary
    """
    if d == 0:
        return "0".zfill(nb)
    if d < 0:
        d += 1 << nb
    b = ""
    while d != 0:
        d, r = divmod(d, 2)
        b = "01"[r] + b
    return b.zfill(nb)


def char2hexa(string_to_convert):
    """
    Convert a string into a succession of hexadecimal values
    that corresponds to each char of the string
    """
    hexa = ""
    for c in string_to_convert:
        hexa += "%02x" % ord(c)

    return hexa


def int_to_bcd(int_number):
    """
    Convert a int number to a BCD format

    :param int_number: number in int or a string that represents an int number without sign (+-)
    :type int_number: str | int
    :return: bcd_number
    :rtype: int
    """
    binary_dict = {'0': "0000",
                   '1': "0001",
                   '2': "0010",
                   '3': "0011",
                   '4': "0100",
                   '5': "0101",
                   '6': "0110",
                   '7': "0111",
                   '8': "1000",
                   '9': "1001",
                   'None': ""}
    bcd_number = ""
    for i in str(int_number):
        try:
            bcd_number += binary_dict[i]
        except KeyError:
            raise AcsBaseException(AcsBaseException.INVALID_PARAMETER,
                                   "The number \"%s\" to be converted to BCD contains "
                                   "other char than digits <0..9>" % (str(int_number)))
    return int(bcd_number, 2)


def enum(*names):
    """
    Enum definition

    Written by Zoran Isailovski (under PSF License)
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/413486
    """
    assert names, "Empty enums are not supported"

    class EnumClass(object):

        """ Internal class """
        __slots__ = names

        def __iter__(self):
            return iter(constants)

        def __len__(self):
            return len(constants)

        def __getitem__(self, i):
            return constants[i]

        def __repr__(self):
            return 'Enum' + str(names)

        def __str__(self):
            return 'enum ' + str(constants)

        def values(self):
            return tuple(self.__slots__)

    class EnumValue(object):

        """ Internal class """
        __slots__ = '__value'

        def __init__(self, value):
            self.__value = value
        Value = property(lambda self: self.__value)
        EnumType = property(lambda self: EnumType)

        def __hash__(self):
            return hash(self.__value)

        def __cmp__(self, other):
            # C fans might want to remove the following assertion
            # to make all enums comparable by ordinal value {;))
            assert self.EnumType is other.EnumType, \
                "Only values from the same enum are comparable"
            return cmp(self.__value, other.__value)  # pylint: disable=W0212

        def __invert__(self):
            return constants[maximum - self.__value]

        def __nonzero__(self):
            return bool(self.__value)

        def __repr__(self):
            return str(names[self.__value])

    maximum = len(names) - 1
    constants = [None] * len(names)
    for i, each in enumerate(names):
        val = EnumValue(i)
        setattr(EnumClass, each, val)
        constants[i] = val
    constants = tuple(constants)
    EnumType = EnumClass()
    return EnumType


class BenchConfigParameters(object):

    """
    BenchConfigParameters' class.
    """

    def __init__(self, dictionnary, dict_name="bench_config", bench_config_file=None):
        """
        Constructor of the class.

        :type dictionnary: dict
        :param dictionnary: Dictionnary.
        """
        self.__dict = dictionnary
        self.__dict_name = dict_name
        self.__bench_config_file = bench_config_file

    @property
    def file(self):
        return self.__bench_config_file

    def get_dict(self):
        """
            Retreive internal dictionnary

        :return: dictionnary
        """
        return self.__dict

    def get_name(self):
        """
        Returns name of parameters' set.

        :rtype: string
        :return: Name of parameters' set.
        """
        return self.__dict_name

    def get_parameters(self, key):
        """
        Returns parameters associated to the key,
        or raise AcsConfigException if the key doesn't exist
        or return an empty dict if the key doesn't refer to any parameters.

        :type key: string
        :param key: Key that refers to parameters.

        :rtype: object
        :return: Instance of BenchConfigParameters.
        """

        try:
            # Store default empty dictionary
            parameters_dict = BenchConfigParameters({}, key)
            if isinstance(self.__dict[key], dict):
                for sub_key in self.__dict[key].iterkeys():
                    if isinstance(self.__dict[key][sub_key], dict):
                        parameters_dict = BenchConfigParameters(self.__dict[key], key)
                        break

            return parameters_dict
        except Exception:
            raise AcsConfigException(AcsConfigException.DATA_STORAGE_ERROR,
                                     "Bad key name (%s)." % (str(key)))

    def get_param_value(self, key, default_value=None, attribute="value"):
        """
        Returns the value associated to a given key.
        If key isn't present, raise an AcsConfigException.

        :type key: string
        :param key: parameter's name.

        :type default_value: String
        :param default_value: Default value if parameter is not present

        :type attribute: String
        :param attribute: the key attribute where the value is read from, by default it will read "value" attribute

        :rtype: string
        :return: parameter's value.
        """
        try:
            param = None
            param = self.__dict[key]
            return param[attribute]
        except Exception:  # pylint: disable=W0703
            if default_value is not None:
                return default_value
            elif param is None:
                raise AcsConfigException(AcsConfigException.DATA_STORAGE_ERROR,
                                         "Bad parameter's name (%s)." % (str(key)))
            else:
                raise AcsConfigException(AcsConfigException.DATA_STORAGE_ERROR,
                                         "No attribute [%s] value found for parameter %s."
                                         % (str(attribute), str(key)))

    def get_description(self, key):
        """
        Returns the description associated to a given key.
        If key isn't present, raise an AcsConfigException.
        If no description is associated to the key, an empty string is returned.
        """
        try:
            param = self.__dict[key]
            return param['description']
        except (AttributeError, KeyError) as error:  # pylint: disable=W0703
            if isinstance(error, KeyError):
                raise AcsConfigException(AcsConfigException.DATA_STORAGE_ERROR,
                                         "Bad parameter's name (%s)."
                                         % (str(key)))
            else:
                return ""

    def get_parameters_name(self):
        """
        Returns the list of keys in the current node.
        """

        return self.__dict.keys()

    def has_parameter(self, key):
        """
        Returns if the key exists or not in the dictionary.
        """

        return key in self.__dict


def get_conversion_toolbox():
    """
    Returns a new instance of ConversionToolBox.

    :rtype: object
    :return: New instance of ConversionToolBox class.
    """
    from acs_test_scripts.Lib.ConversionToolBox.ConversionToolBox import ConversionToolBox

    conversion_tool_box_path = os.path.join(Paths.CONFIGS, "ConversionToolBox")

    return ConversionToolBox("wcdma_conversion.xml",
                             "gsm_conversion.xml",
                             "wifi_conversion.xml",
                             conversion_tool_box_path)


def get_method_name():
    """
    Returns the name of the method which is calling this get_method_name.

    :rtype: str
    :return: caller method name.
    """
    s = stack()[1]
    name = s[3].strip()
    return name


def check_keys(dictionary, keys):
    """
    Check if keys are in given dictionary, raise an error if not.

    :type dictionary: dict
    :param dictionary: dict to test

    :type keys: string
    :param keys: keys to check

    :rtype: list
    :return: list of missing keys
    """
    key_list = []
    for element in keys:
        if element not in dictionary:
            LOGGER_FWK.error(
                "KEY %s missing on your dictionary" % element)
            key_list.append(element)

    return key_list


def get_acs_release_version():
    """
    gets the ACS release version contained in the version.txt file.
    """
    acs_version = AcsConstants.NOT_AVAILABLE
    try:
        filepath = os.path.join(os.getcwd(), "version.txt")

        if os.path.isfile(filepath):
            # Read the content of the acs version.txt file
            f = open(filepath, "r")
            text = f.read()
            f.close()

            if text not in [None, ""]:
                expr_version = ".*release.id=@(?P<version>([ -\\.a-zA-Z0-9]*))@"
                matches_str = re.compile(expr_version).search(text)
                if matches_str is not None:
                    # version found !
                    acs_version = matches_str.group("version")
                    if acs_version in [None, ""]:
                        print ("Unable to parse ACS version ! (%s)" % str(text))
                        acs_version = AcsConstants.NOT_AVAILABLE
                else:
                    print ("Impossible to retrieve ACS Version ! (%s)" % str(text))
        else:
            acs_version = "engineering version"

    except Exception as e:  # pylint: disable=W0703
        print ("Error occured when getting ACS version ! (%s)" % str(e))
        acs_version = AcsConstants.NOT_AVAILABLE

    return acs_version


def is_test_case_file(file_name):
    """
    Check if the given file is a test case

    :param file_name: string
    :param file_name: File to check

    :rtype: boolean
    :return: If the file is a test case or not
    """

    status = False

    try:
        # MUST BE xml file
        if file_name.endswith(".xml"):
            file_doc = etree.parse(file_name)

            if str(file_doc.getroot().tag) == 'TestCase':
                status = True
    except BaseException:
        status = False

    return status


def is_bench_config_file(file_name):
    """
    Check if the given file is a BenchConfig

    :param file_name: string
    :param file_name: File to check

    :rtype: boolean
    :return: If the file is a bench config or not
    """

    status = False

    try:
        # MUST BE xml file
        if file_name.endswith(".xml"):
            file_doc = etree.parse(file_name)

            if str(file_doc.getroot().tag) == 'BenchConfig':
                status = True
    except BaseException:
        status = False

    return status


def is_campaign_config_file(file_name):
    """
    Check if the given file is a CampaignConfig

    :param file_name: string
    :param file_name: File to check

    :rtype: boolean
    :return: If the file is a campaign config or not
    """

    status = False

    try:
        # MUST BE xml file
        if file_name.endswith(".xml"):
            file_doc = etree.parse(file_name)

            if str(file_doc.getroot().tag) == 'Campaign':
                status = True
    except BaseException:
        status = False

    return status


def is_report_file(file_name):
    """
    Check if the given file is a report file

    :param file_name: string
    :param file_name: File to check

    :rtype: boolean
    :return: If the file is a test report or not
    """
    status = False
    try:
        # MUST BE xml file
        if file_name.endswith(".xml"):
            file_doc = etree.parse(file_name)
            if str(file_doc.getroot().tag) == 'TestReport':
                status = True
    except Exception:
        status = False

    return status


def get_timestamp():
    """
    format current time Y-m-d_HhM.S.m

    :rtype: String or None
    :return: The formatted time
    """
    return datetime.now().strftime("%Y-%m-%d_%Hh%M.%S.%f")[:-5]


def get_config_value(config_dict, config_dict_name, config_name, default_value=None, default_cast_type=str):
    """
    Return the value of the given config name
    The type of the value can be checked before assignment
    A default value can be given in case the config name does not exist

    :type config_name: string
    :param config_name: name of the property value to retrieve

    :type default_value: string
    :param default_value: default_value of the property

    :type default_cast_type: type object
    :param default_cast_type: type to cast (int, str, list ...)
    By default cast into str type.

    :rtype: string or type of default_cast_type
    :return: config value
    """

    # Read the config value from dut config dictionary
    config_value = config_dict.get(config_name, default_value)

    # In case the config value is not None, trying to cast the value
    if config_value is not None:
        # Cast the value to the given type
        # Stripping is done to suppress end and start spaces of values
        try:
            if default_cast_type == "str_to_bool":
                config_value = str_to_bool(str(config_value).strip())
            elif default_cast_type == "str_to_dict":
                config_value = str_to_dict(str(config_value).strip())
            else:
                config_value = default_cast_type(config_value)
        except ValueError:
            debug_msg = "Wrong value used for dictionary %s entry: '%s'. Returning default value '%s' !" \
                        % (str(config_dict_name), str(config_name), str(default_value))
            LOGGER_FWK.debug(debug_msg)

            config_value = default_value

    return config_value


def compute_timeout_from_file_size(file_path, min_timeout=0):
    """
    Compute a timeout depending the file's size.

    :type file_path: str
    :param file_path: File from which a timeout will be computed

    :type min_timeout: int
    :param min_timeout: Minimum timeout (in sec) to set if the file size is too small

    :rtype: int
    :return: timeout (in sec) computed from the file size
    """
    if os.path.isfile(file_path):
        app_size = os.path.getsize(file_path)
        timeout = int(app_size / 1024 / 4)
        if timeout < min_timeout:
            # Set a minimum installation timeout
            timeout = min_timeout
        LOGGER_FWK.debug("app size: %dB,  timeout: %ds" % (app_size, timeout))
    else:
        timeout = min_timeout

    return timeout


def format_cmd_args(cmd_args):
    """
    Return well formatted command.

    :type cmd_args: str
    :param cmd_args: command to be formatted

    :return: Properly formatted command to execute
    :rtype: str
    """
    return AcsSubprocess(command_line=cmd_args, logger=None).command


def run_local_command(args, get_stdout=True, logger=LOGGER_FWK):
    """
    Launch a local asynchronized process

    :type args: list, str
    :param args: command line arguments

    :type get_stdout: bool
    :param get_stdout: display or not stdout command in ACS logs

    :type  logger: logger object
    :param logger: logger to be used to log messages

    :rtype: tuple (process, q)
    """
    run_job = AcsSubprocess(command_line=args, logger=logger, stdout_level=RAW_LEVEL)
    return run_job.execute_async(get_stdout)


def internal_shell_exec(cmd, timeout, log_stdout=True, silent_mode=False, logger=LOGGER_FWK, cancel=None):
    """
    Execute the input command regardless the Host OS
    and return the result message

    The execution is synchronized

    If the timeout is reached, return an exception

    :type  cmd: str
    :param cmd: Command to be run
    :type  timeout: int
    :param timeout: Script execution timeout in sec
    :type  cancel: Cancel
    :param cancel: a Cancel object that can be used to stop execution, before completion or timeout(default None)
    :type  log_stdout: bool
    :param log_stdout: Specify if stdout log of the cmd will be logged (NOT USED ANYMORE)
    :type  silent_mode: bool
    :param silent_mode: Display logs in ACS logger
    :type  logger: logger object
    :param logger: logger to be used to log messages

    :return: Execution status & output string (and optionally C{dict})
    :rtype: tuple(int, str)
    """
    run_job = AcsSubprocess(command_line=cmd,
                            logger=logger,
                            silent_mode=silent_mode,
                            stdout_level=RAW_LEVEL,
                            stderr_level=RAW_LEVEL)  # adb pull returns its stdout on stderr.
    # This is to avoid having ERROR logs

    result, output = run_job.execute_sync(timeout, cancel)
    return Global.SUCCESS if result else Global.FAILURE, output


def FINDKEY(d, val):
    """
    Method to find a key in a dict from a given value v

    :param dict d: container
    :param object val: the value to be looked for

    :return: A list of found key(s) or empty
    """
    return [c for c, v in d.iteritems() if v == val]


# Dictionary  to allow simple cast of a parameter
CAST_TYPE_DICTIONARY = {"str": str,
                        "file": os.path.normpath,
                        "scriptfile": os.path.normpath,
                        "int": int,
                        "float": float,
                        "bool": str_to_bool,
                        "dict": str_to_dict,
                        "list": str_to_list}


class Obfuscated(str):

    def __str__(self):
        return '*' * len(self)


def compute_checksum(path_to_check):
    """
    Compute checksum for all files in the given path and save it in a file
    :type path_to_check: str
    :param path_to_check: The path to the folder to compute checksum.
    :rtype hash_code: list of tuple
    :return list of [(file, checksum)]
    """
    hash_code = []

    import hashlib
    for root, dirnames, filenames in os.walk(path_to_check):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            with open(filepath, 'rb') as f:
                hash_code += [(filepath.replace(path_to_check + os.sep, ""),
                               hashlib.sha256(f.read()).hexdigest())]

    return hash_code
