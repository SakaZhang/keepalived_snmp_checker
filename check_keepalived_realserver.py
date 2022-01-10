#!/usr/bin/env python3
import socket
import struct
import sys
import subprocess

RS_OK = 0
RS_WARNING = 1
RS_CRITICAL = 2
RS_UNKNOWN = 3
realServer_Ipaddr_Oid = "1.3.6.1.4.1.9586.100.5.3.4.1.4"
realServer_Port_Oid = "1.3.6.1.4.1.9586.100.5.3.4.1.5"
realServer_Status_Oid = "1.3.6.1.4.1.9586.100.5.3.4.1.6"
health_ok = []
health_warn = {}
realServerIp = {}
realServerStatus = {}


def getRealServerIp():
    try:
        for realserverip in subprocess.Popen('snmpwalk -v2c -c public 127.0.0.1 '
                                             + realServer_Ipaddr_Oid, shell=True,
                                             stdout=subprocess.PIPE).communicate():

            if realserverip is not None:
                timeout = realserverip.decode('utf-8')
                if timeout.find('Timeout') != -1:
                    print("get real server's ipaddress failed")
                    sys.exit(RS_UNKNOWN)

                s = realserverip.decode('utf-8').replace('SNMPv2-SMI::enterprises.9586.100.5.3.4.1.4.', '').replace(
                    '= Hex-STRING: ', '').split('\n')
                s = s[:len(s) - 1]

                for s_index in s:
                    flag, ip = s_index.split(" ", 1)
                    ip = int(ip.replace(' ', ''), 16)
                    ip = socket.inet_ntoa(struct.pack(">L", ip))
                    realServerIp[flag] = ip

    except Exception as err:
        print('1', err)
        sys.exit(RS_UNKNOWN)


def getRealServerPort():
    try:
        for realserverport in subprocess.Popen('snmpwalk -v2c -c public 127.0.0.1 '
                                               + realServer_Port_Oid, shell=True,
                                               stdout=subprocess.PIPE).communicate():
            if realserverport is not None:
                timeout = realserverport.decode('utf-8')
                if timeout.find('Timeout') != -1:
                    print("get real server's port failed")
                    sys.exit(RS_UNKNOWN)

                s = realserverport.decode('utf-8').replace('SNMPv2-SMI::enterprises.9586.100.5.3.4.1.5.', '').replace(
                    '= Gauge32: ', '').split('\n')
                s = s[:len(s) - 1]
                for s_index in s:
                    flag, port = s_index.split(" ", 1)
                    realServerIp[flag] = realServerIp[flag] + ':' + port

    except Exception as err:
        print('2', err)
        sys.exit(RS_UNKNOWN)


def setRealServerStatus():
    try:
        for realserverstatus in subprocess.Popen('snmpwalk -v2c -c public 127.0.0.1 '
                                                 + realServer_Status_Oid, shell=True,
                                                 stdout=subprocess.PIPE).communicate():
            if realserverstatus is not None:
                timeout = realserverstatus.decode('utf-8')
                if timeout.find('Timeout') != -1:
                    print("get real server's status failed")
                    sys.exit(RS_UNKNOWN)

                s = realserverstatus.decode('utf-8').replace('SNMPv2-SMI::enterprises.9586.100.5.3.4.1.6.', '').replace(
                    '= INTEGER: ', '').split('\n')
                s = s[:len(s) - 1]
                for s_index in s:
                    flag, status = s_index.split(" ", 1)
                    realServerStatus[realServerIp[flag]] = status

    except Exception as err:
        print('3', err)
        sys.exit(RS_UNKNOWN)


def checkHealth():
    for k, v in realServerStatus.items():
        if v == str(1):
            health_ok.append(v)
        else:
            health_warn[k] = v

    if len(health_ok) == len(realServerIp) and len(health_warn) == 0:
        print('all real server are ok')
        sys.exit(RS_OK)
    elif len(health_warn) == len(realServerIp):
        print('the all real servers are  down: ', health_warn)
        sys.exit(RS_CRITICAL)
    elif len(health_warn) != 0:
        print('there are some real server down: ', health_warn)
        sys.exit(RS_WARNING)
    else:
        print("Unknown err!\nThe real servers are: ", realServerIp, "\nTheir status are: ", realServerStatus)
        sys.exit(RS_UNKNOWN)


if __name__ == '__main__':
    getRealServerIp()
    getRealServerPort()
    setRealServerStatus()
    checkHealth()
