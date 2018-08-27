ACS open source BKM document – Wi-Fi

Setup instructions:
1. Connect the NUC to the Linux host over USB.
2. Configure the AP manually to the desired configuration as per the test necessity.
3. Enter the NUC serial number in benchconfig xml file.
4. Run ACS command by mentioning campaign path and benchconfig path as below:
$ python ACS.py  -c OTC/CAMPAIGN/Celadon/WiFi -b OTC/BENCHCONFIG/bench_config_HW_campaigns
5. Run the campaign on the Linux host which will configure the NUC according to the parameter passed and connect to
the AP and test for ping for a desired time.

6. The parameters can be edited in the TC xml files in the below path
<otcqa-acs-opensource>/acs_test_suites/OTC/TC/TESTLIB/**.xml

Ex: ap_name=test_ap passphrase=qwerasdf dut_security=WPA mode=n channel_bw=20 hidden_ssid=0 channel_no=6 trycount=10

Dependencies:
1. Python 2.7
2. Ubuntu 14.04
3. NUC with ADB over USB enabled.

----------------------------------------------------------------------------------------------------------------------
ACS open source BKM document – Bluetooth

Setup instructions:
1. ACS Open source Bluetooth test cases usage:
2. Flash user debug builds on DUT and reference devices, enable developer options and usb debugging and make sure
virtual keypad is ON.
3. DUT and rooted reference devices are connected via adb to ACS installed host machine.
4. Adb devices will detect connected two reference devices through adb devices command.
5. Fill the connected two devices serial numbers in benchconfig xml
(<otcqa-acs-opensource>/acs_test_suites/OTC/BENCHCFG/bench_config_HW_campaigns.xml) file
6. Run ACS command by mentioning campaign path and benchconfig path as below:
$ python ACS.py -c OTC/CAMPAIGN/Celadon/BT -b OTC/BENCHCONFIG/bench_config_HW_campaigns.

Dependencies:
1. Python 2.7
2. Ubuntu 14.04
3. NUC (DUT) with adb enabled
4. Rooted reference device(NUC)

----------------------------------------------------------------------------------------------------------------------
ACS Open Source BKM – Storage

ACS Open source Storage test cases usage:
1. Flash user debug builds on DUT and reference devices, enable developer options and USB debugging.
2. Connect the NUC to the Linux host over USB.
3. Enter the Device Serial number in benchconfig xml (<otcqa-acs-opensource>/acs_test_suites/OTC/BENCHCFG/benchConfig
.xml) file.
4. Insert the micro SD card to the NUC.

5. Automation Execution:
$ python ACS.py -b OTC/BENCHCFG/benchConfig -c OTC/CAMPAIGN/Celadon/System_Storage_USB

Requirements:
1. ADB connection to the DUT.
2. Micro SD card.
3. Ubuntu 14.04 LTS
4. Python 2.7

Note:
1. The file extension of *.xml should not be mentioned in the command line. ACS auto picks the xml file. Manual entry
of xml extensions concatenates with the existing xml file and ACS fails to find the xml file.
2. It is recommended to enter the serial number in BenchConfig file if multiple devices are connected to the host
machine. For a single device connected to host machine, ACS runs automatically.
3. Recommended to check the device listed in ‘adb devices’ command and the device should not be in offline state before
 executing the automation suite.
4. Device serial number can be noted using the command adb devices in host machine.
5. It is not necessary to be root or super user to execute the automation suite.

---------------------------------------------------------------------------------------------------------------------