# Test Suite for Android
Test sutie for Android, verified on [Intel Celadon](https://01.org/projectceladon/).


## Setup
Prepare a Ubuntu host

1. Install ACS [depedencies](../../acs_setup_manager/README.txt).
2. Download test resources by `python acs_test_suites/OTC/res/download.py`
3. Create *pyunit* global [config](libs/pyunit/README.md#pre-setup).


## Execution
### General Execution Guide
##### Folder Structure & Test Campaign
```
acs_test_suites/OTC$tree -L 2
├── BENCHCFG   # Bench Config Folder
│   ├── benchConfig.xml
├── CAMPAIGN
│   └── Celadon  # Campaign folder for Celadon
├── libs  # Python library & test scripts
│   ├── pyunit
│   └── testlib
├── res  # Resource management
└── TC  # Test Case xml
    ├── PY_UNIT
    └── TESTLIB
```
Available test Campaign put in `CAMPAIGN/Celadon` folder:
```
AppTesting_AOSP.xml
BT.xml
Graphics_Display.xml
Graphics_System.xml
System_FastBoot.xml
system_os.xml
System_Storage_USB.xml
WiFi.xml
```

##### Running Test Campaign
In code root folder:

1. Android Device with adb connect to Host.
2. export ACS Execution Config path: `export ACS_EXECUTION_CONFIG_PATH={REPO}/acs_test_suites/`
3. run campaign using ACS framework, command template: `python acs/acs/ACS.py -c OTC/CAMPAIGN/Celadon/{CAMPAIGN_NAME} -b OTC/BENCHCFG/benchConfig`

**Note**: The file extension of `*.xml` should not be mentioned in the command line. ACS auto picks the xml file.
Take `AppTesting_AOSP.xml` for example, you should only set `CAMAPIGN_NAME` to `AppTesting_AOSP`.

### Special Setup

#### WiFi
##### WiFi Access Point
WiFI domain testing require a WiFi AP:

* With dual band support with manually configurable 802.11a/b/g/n/ac bands;
* channels width configuration (20MHz and 40 MHz);
* channel select configuration and Show/hide SSID configuration.

##### Configuration
Configure the AP manually to the desired configuration (Band, Channel, Security, Channel width, SSID broadcast) as per the test necessity.

The AP parameters can be edited in the TC xml files in the below path:
`acs_test_suites/OTC/TC/TESTLIB/**.xml`

Ex: `ap_name=test_ap passphrase=qwerasdf dut_security=WPA mode=n channel_bw=20 hidden_ssid=0 channel_no=6 trycount=10`

Enter the NUC serial number in BenchConfig xml file: `OTC/BENCHCFG/bench_config_HW_campaigns.xml`

##### Execution Command
```
python acs/acs/ACS.py -c OTC/CAMPAIGN/Celadon/WiFi -b OTC/BENCHCFG/bench_config_HW_campaigns
```

#### BT
##### setup

* Prepare *another* Android device with *ROOT* access as **reference device**
* make sure virtual keypad is ON
* DUT and reference device connect to host with USB adb
* Fill two devices' serial number in `BENCHCFG/bench_config_HW_campaigns.xml`

##### Execution Command
```
python acs/acs/ACS.py ACS.py -c OTC/CAMPAIGN/Celadon/BT -b OTC/BENCHCFG/bench_config_HW_campaigns
```

#### Storage_USB
##### setup
Insert a **micro SD card** to DUT.

##### Execution Command
```
python acs/acs/ACS.py -c OTC/CAMPAIGN/Celadon/System_Storage_USB -b OTC/BENCHCFG/benchConfig
```
