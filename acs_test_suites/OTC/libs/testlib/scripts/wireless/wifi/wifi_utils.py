#!/usr/bin/env python

"""
Copyright (C) 2018 Intel Corporation
?
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
?
http://www.apache.org/licenses/LICENSE-2.0
?
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions
and limitations under the License.
?
SPDX-License-Identifier: Apache-2.0
"""

import time
import socket
import re
from testlib.utils.connections.adb import Adb as connection_adb
from testlib.utils.statics.android import statics


def get_mDhcpResults(ret_val, line):
    m = re.search(r'DHCP server \/*([\.\d]+)', line)
    if m is not None:
        ret_val['DHCP_server'] = m.group(1)

    m = re.search(r'Gateway \/*([\.\d]+)', line)
    if m is not None and ret_val['Gateway'] is None:
        ret_val['Gateway'] = m.group(1)
    return ret_val


def get_mLinkProperties(ret_val, line):
    # m = re.search(r'LinkAddresses: \[[\w\:\/]*?,?([\.\d]+)\/.*\]', line)
    m = re.search(r'LinkAddresses: \[(.*?)\]', line)
    m = re.search(r'(\d+\.\d+\.\d+\.\d+)\/\d+', m.group(1))
    if m is not None:
        ret_val['ip_address'] = m.group(1)

    m = re.search(r'LinkAddresses: \[(.*?)\]', line)
    # mask = None
    if m is not None:
        segment = m.group(1)
        ips = segment.split(",")
        for element in ips:
            m = re.search(r'\d+\.\d+\.\d+\.\d+\/(\d+)', element)
            if m is not None:
                # mask = m.group(1)
                ret_val['net_mask'] = m.group(1)
                break
    m = re.search(r'DnsAddresses:\s+\[([\.\d,]+?),?\]', line)
    if m is not None:
        ret_val['DNS_addresses'] = m.group(1)
    return ret_val


def get_key_mgmt(ret_val, line):
    line = line.strip()
    if 'key_mgmt' in line:
        ret_val['Security'] = line.split('=')[1]
    elif "KeyMgmt" in line:
        ret_val['Security'] = line.split(' Protocols:')[0].split(': ')[1]
    elif 'p2p_device_address' in line:
        ret_val['p2p_device_address'] = line.split('=')[1]
    elif 'pairwise_cipher' in line:
        ret_val['pairwise_cipher'] = line.split('=')[1]
    elif 'PairwiseCiphers' in line:
        ret_val['pairwise_cipher'] = line.split(': ')[1]
    elif 'group_cipher' in line:
        ret_val['group_cipher'] = line.split('=')[1]
    return ret_val


def get_mWifiInfo(ret_val, line):
    for element in line:
        if 'mWifiInfo SSID' in element:
            ret_val['SSID'] = element.split(': ')[1]
        elif 'Frequency' in element:
            ret_val['Frequency'] = element.split(': ')[1]
        elif 'Link speed' in element:
            ret_val['Link_speed'] = element.split(': ')[1]
        elif 'MAC' in element:
            ret_val['MAC'] = element.split(': ')[1]
        elif 'state' in element and 'Supplicant' not in element:
            ret_val['state'] = element.split(': ')[1]

    return ret_val


def get_connection_info(content):
    # imitialize the values
    ret_val = {'DHCP_server': None,
               'DNS_addresses': None,
               'Frequency': None,
               'Gateway': None,
               'Link_speed': None,
               'MAC': None,
               'SSID': None,
               'Security': None,
               'ip_address': None,
               'p2p_device_address': None,
               'state': None,
               'pairwise_cipher': None,
               'group_cipher': None,
               'net_mask': None}
    state_section_found = False
    for line in content.split("\n"):
        if not state_section_found:
            if "WifiStateMachine:" in line:
                state_section_found = True
            else:
                continue
        else:
            if "mWifiInfo" in line:
                get_mWifiInfo(ret_val, line.split(", "))
            elif "mNetworkInfo" in line:
                get_mWifiInfo(ret_val, line.split(", "))
            elif "mDhcpResults" in line:
                get_mDhcpResults(ret_val, line)
            elif "mLinkProperties" in line:
                get_mLinkProperties(ret_val, line)
            elif "key_mgmt=" in line:
                get_key_mgmt(ret_val, line)
            elif "KeyMgmt:" in line and "WifiService:" not in line:
                get_key_mgmt(ret_val, line)
            elif "p2p_device_address=" in line:
                get_key_mgmt(ret_val, line)
            elif "pairwise_cipher=" in line:
                get_key_mgmt(ret_val, line)
            elif "PairwiseCiphers:" in line:
                get_key_mgmt(ret_val, line)
            elif "group_cipher=" in line:
                get_key_mgmt(ret_val, line)
            elif "WifiConfigStore - Log Begin" in line:
                break
            else:
                continue
    print ret_val
    for key in ret_val.keys():
        if ret_val[key] == "":
            ret_val[key] = None

    return ret_val


def get_connection_content(serial=None, service="wifi"):
    # services supported: "wifi", "wifip2p"
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    wifi_conf = adb_connection.parse_cmd_output("dumpsys {}".format(service))
    return wifi_conf


def ping(ip, trycount=2, target_percent=50, timeout=15, serial=None):
    """ Descriptions:
            Pings the ip for a <trycount> times

        Returns True if the packet loss is less then or equal to the target_percent

        Usage:
            ping(serial = serial,
                   ip = "192.168.1.131" or "2001:1234:5678:9abc::1",
                   trycount = 30,
                   target_percent= 15)
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    if ":" in ip:
        ping_command = "ping6"
        command = ping_command + " -c " + \
            str(trycount) + " " + str(ip) + "%wlan0"
    else:
        ping_command = "ping"
        command = ping_command + " -c " + str(trycount) + " " + str(ip)
    ping_data = adb_connection.run_cmd(command=command,
                                       timeout=timeout,
                                       mode="sync")
    ping_output = ping_data.stdout.read().strip()
    matcher = re.compile(r'(\d+)% packet loss')
    match = matcher.search(ping_output)
    if not match:
        print "Ping output : ", ping_output
        return False, None, ping_output

    percent = match.groups()[0]
    verdict = float(percent) <= target_percent

    return verdict, percent, ping_output


def start_ping(ip, trycount=2, target_percent=50, timeout=15, serial=None):
    """ Descriptions:
            Pings the ip for a <trycount> times

        Returns True if the packet loss is less then or equal to the target_percent

        Usage:
            ping(serial = serial,
                   ip = "192.168.1.131" or "2001:1234:5678:9abc::1",
                   trycount = 30,
                   target_percent= 15)
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    if ":" in ip:
        ping_command = "ping6"
    else:
        ping_command = "ping"
    command = ping_command + " -c " + str(trycount) + " " + str(ip)
    ping_data = adb_connection.run_cmd(command=command,
                                       timeout=timeout,
                                       mode="sync")
    ping_output = ping_data.stdout.read().strip()
    matcher = re.compile(r'(\d+)% packet loss')
    match = matcher.search(ping_output)
    if not match:
        print "Ping output : ", ping_output
        return False, None, ping_output

    percent = match.groups()[0]
    verdict = float(percent) <= target_percent

    return verdict, percent, ping_output


def ip_to_int(ip):
    # conversion from IP string to integer
    val = 0
    i = 0
    for s in ip.split('.'):
        val += int(s) * 256 ** (3 - i)
        i += 1
    return val


def int_to_ip(val):
    # conversion from integer to IP string
    octets = []
    for i in range(4):
        octets.append(str(val % 256))
        val = val >> 8
    return '.'.join(reversed(octets))


def get_ip_range(serial=None):
    content = get_connection_content(serial=serial)
    connection_info = get_connection_info(content)
    mask = connection_info["net_mask"]
    ip_address = connection_info["ip_address"]
    if ip_address:
        ip = ip_to_int(ip_address)
        netmask = (0xffffffff << (32 - int(mask))) & 0xffffffff
        net_address = int_to_ip(ip & netmask)
        start = int_to_ip(ip_to_int(net_address) + 1)
        end = int_to_ip(ip_to_int(net_address) + pow(2, (32 - int(mask))) - 1)
        return start + "_" + end
    else:
        print "The device does not have an IP Address. Check connection to AP!"
        return False


def check_airplane_mode_on(serial=None):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    cmd = "dumpsys wifi | grep mAirplaneModeOn"
    out = adb_connection.parse_cmd_output(cmd=cmd)
    if "true" in out.strip():
        return True
    elif "false" in out.strip():
        return False
    else:
        return None


def check_wifi_state_on(serial=None):
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    # below sleep time will help get proper result when there is a sudden
    # toggle in wifi power state
    time.sleep(1)
    cmd = "dumpsys wifi | grep Wi-Fi"
    out = adb_connection.parse_cmd_output(cmd=cmd)
    if "enabled" in out.strip():
        return True
    elif "disabled" in out.strip():
        return False
    else:
        return None


def get_device_wlan0_ip(serial=None, platform=None):
    """
    returns the IP Address of the Wlan0 interface
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()

    if platform:
        platform = platform
    else:
        platform = statics.Device(serial=serial)

    get_interfaces_tool_ip = platform.get_interfaces_tool
    grep_for = "wlan0"
    if get_interfaces_tool_ip == "ifconfig":
        grep_for = "inet"

    wlan0_line = adb_connection.parse_cmd_output(cmd=platform.get_interfaces_tool,
                                                 grep_for=grep_for).split()
    return wlan0_line[-3]


def get_device_type(serial=None):
    """
    returns device type from getprop
    """
    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    product_name_line = adb_connection.parse_cmd_output(cmd="getprop",
                                                        grep_for="ro.product.device").split()
    # split getprop line into a list
    # this contains product name inside brackets, remove them below
    product_name = product_name_line[1]
    return product_name[1:-1]


def get_dut_ipv6_address(serial=None, static_ip=False):
    """
    Returns device ipv6 address from the ifconfig command output
    :param serial: the DUT serial
    :param static_ip: boolean, true if ip to get is static, false if it is dynamic
    :return: the ipv6 address from the output
    """
    if static_ip:
        grep_for_text = "global mngtmpaddr"
    else:
        grep_for_text = "global temporary"

    if serial:
        adb_connection = connection_adb(serial=serial)
    else:
        adb_connection = connection_adb()
    for i in range(5):
        ipv6_address_line = adb_connection.parse_cmd_output(cmd="ip -6 addr show wlan0",
                                                            grep_for=grep_for_text).split()

        if not ipv6_address_line:
            time.sleep(2)
        else:
            break
    ipv6_address = ipv6_address_line[1]
    if "/" in ipv6_address:
        ipv6_address = ipv6_address.split("/")[0]
    return ipv6_address


def is_valid_ipv6_address(address):
    """
    Checks if the supplied address is valid
    :param address: ipv6 address
    :return: True if valid, False otherwise
    """
    try:
        socket.inet_pton(socket.AF_INET6, address)
        return True
    except socket.error:
        return False
