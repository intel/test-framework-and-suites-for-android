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

If more than one Andoird devices exist, please specified **serialNumber** parameter in *BenchConfig* file, here is an example:
```xml
<Phones>
	<Phone name="PHONE1"
		deviceModel="Android" >
	    <Parameter serialNumber="emulator-5555" />
	</Phone>
</Phones>
```

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

#### System_FastBoot
##### Rework NUC and attach relay card

Get a [relay card](http://www.robot-electronics.co.uk/usb-rly08b-8-channel-relay-module.html).

Open the chassis of the NUC, find the two contacts of power button switch, attach two wires respectively to each contact.

Attach the other side of the two wires to the relay card's **RLY1** channel's  **NO** and **C** ports respectively, fasten the screws on the port. There is no need to worry about the order of the two wires.

Connect the relay card with Linux host through USB bus.

##### Change privileges

Make sure the host has the right privileges(**read and write**) on the relay card by:
```
sudo chmod 666 /dev/ttyACM0
```
After this, create a rule in `/etc/udev/rules.d` to set the permission automatically:
```
# cd to the directory
cd /etc/udev/rules.d
# create a new rule file
sudo touch relay_card.rules
# edit the file
sudo vim relay_card.rules
# append a line
KERNEL=="ttyACM0", MODE="0666"
```

##### WiFi Configuration
Configure the AP manually to the desired configuration.

The AP parameters can be edited in the TC xml files in the below path:
`acs_test_suites/OTC/TC/TESTLIB/System_FastBoot/CELADON/*.xml`

Ex: `ssid=test_ap password=qwerasdf`

**Note**: Not all the test case of fastboot needs WiFi connection, just configure those already have ssid and password configuration.

##### Execution Command
```
python acs/acs/ACS.py -c OTC/CAMPAIGN/Celadon/System_FastBoot -b OTC/BENCHCFG/myBench_usb_fastboot
```
