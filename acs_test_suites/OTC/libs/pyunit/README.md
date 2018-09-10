## PyUnit

PyUnit is a sub-test-framework using standard Python *unittest* style.

### Source Code
* python test script and library: `acs_test_suites/OTC/libs/pyunit`
* ACS TestCase xml: `acs_test_suites/OTC/TC/PY_UNIT`

### Code Structure
* **testlib**: common library for test case
* **test_data**: store test config, path can export as `TEST_DATA_ROOT`
* **tests**: test case folder

---
### Running PyUnit Test Cases without ACS
#### pre-setup
create global config in `/etc/oat/sys.conf` with below content:
```
[wifisetting]
name =YOUR_AP_NAME
security = WPA/WPA2 PSK
passwd = AP_APSSOWRD
ssid =SSID_NAME

[google_account]
user_name = GOOGLE_ACCOUNT_EMAIL
password = PASSOWRD
```

#### running test case
All the test is defined in python [unittest](https://docs.python.org/2/library/unittest.html) flavor.

So you can execute test case using `unittest` or `nosetests`, example:

```bash
export TEST_DATA_ROOT=$PWD/test_data/Graphics_System/
# run single case
python -m unittest tests.Graphics_System.GLES.dEQP_GLES.RundEQP.test_OpenGLES_32_Support_dumpsys_SurfaceFlinger
# run all tests in a class
python -m unittest tests.Graphics_System.GLES.dEQP_GLES.RundEQP
# run all tests in a file
nosetests -s tests/Graphics_System/GLES/dEQP_GLES.py
```
---
### PyUnit Test in ACS Framework

#### ACS Test Case xml

`acs_test_suites/OTC/TC/PY_UNIT/Graphics_System/GLES/test_OpenGLES_32_Support_dumpsys_SurfaceFlinger.xml`

```xml
<?xml version="1.0" ?>
<TestCase>
    <UseCase>PY_UNIT</UseCase>
    <Discription>test_OpenGLES_32_Support_dumpsys_SurfaceFlinger</Discription>
    <Parameters>
        <Parameter>
            <Name>TEST_DATA_ROOT</Name>
            <Value>test_data/Graphics_System/</Value>
        </Parameter>
        <Parameter>
            <Name>TEST_CASE</Name>
            <Value>tests.Graphics_System.GLES.dEQP_GLES.RundEQP.test_OpenGLES_32_Support_dumpsys_SurfaceFlinger</Value>
        </Parameter>
    </Parameters>
</TestCase>
```
Note:

* `UseCase` should set to `PY_UNIT`
* `TEST_DATA_ROOT` is the *test_data* folder of your domain
* `TEST_CASE`: standard python method path


#### ACS UseCase: `PY_UNIT`
*source code*

`acs_test_scripts/UseCase/Misc/PY_UNIT.py`

*What has been done in this UseCase*
1. export `TEST_DATA_ROOT` env obtained from xml
2. Find and run python `unittest.TestCase` specified in `TEST_CASE`
3. Parse execution result and return as ACS case result

---
### Writing test case using PyUnit
File: `tests/{domain}/{sub-domain}/{pytest}.py`

```python
from testlib.util.uiatestbase import UIATestBase
from testlib.chromecast.chromecastconnection_impl import ChromeCastImpl

class ChromeCast(UIATestBase):
    def setUp(self):
       super(ChromeCast, self).setUp()
        self._chromecast = ChromeCastImpl()

    def tearDown(self):
       super(ChromeCast, self).tearDown()

    def test_adapter_scanning(self):  # real test case
        ''' refer TC test_AdapterScanning '''
        self._chromecast.launch_app_am()
        self._chromecast.goto_castscreen()
        ...
```

#### import notes about writing a test case
1. make sure each folder has a `__init__.py` file to keep it as a module
2. All test class should inherit from `UIATestBase` or its subclass
3. If you need customized `setUp` or `tearDown` method, `super` is needed here
4. Code in test case should be clear to reflect test step defination, details implement put in library folder `testlib/{domain}/{pyfile}.py`

---
### PyUnit Library

Example: `testlib/bluetooth/bluetooth.py`

```python
import time
from testlib.util.common import g_common_obj
from testlib.util.log import Logger

class BluetoothSetting(object):
    def __init__(self):
       self.d = g_common_obj.get_device()  # uiautomator object
       self.adb = g_common_obj  # adb wrapper
        self.log = Logger.getlogger(self.__class__.__name__)

    def launch(self):
        ''' launch Bluetooth Settings page '''
        self.adb.adb_cmd("am start -W com.android.settings")
        time.sleep(1)
        if self.d(scrollable=True).exists:
            self.d(scrollable=True).scroll.to(text="Bluetooth")
        self.d(text="Bluetooth").click.wait()

```

---

### PyUiautomator

* is a Python wrapper of [Android uiautomator](https://developer.android.com/training/testing/ui-testing/uiautomator-testing.html) testing framework
* github: https://github.com/xiaocong/uiautomator
* install: `pip install uiautomator`

We make use a lot of *PyUiautomator* to manipulate UI object in Android System.

##### usage:

```python
from uiautomator import device as d

d.screen.on()
d(text="Clock").click()
```

For more detail, refer to [doc](https://github.com/xiaocong/uiautomator#table-of-contents)
