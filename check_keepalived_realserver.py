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
                    ip = int(s_index[4:len(s_index) - 1].replace(' ', ''), 16)
                    ip = socket.inet_ntoa(struct.pack(">L", ip))
                    realServerIp[s_index[:3]] = ip

    except Exception as err:
        print('1', err)
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
                    realServerStatus[realServerIp[s_index[:3]]] = s_index[4:len(s_index)]

    except Exception as err:
        print('2', err)
        sys.exit(RS_UNKNOWN)


def checkHealth():
    for k, v in realServerStatus.items():
        if v == str(1):
            health_ok.append(v)
        else:
            health_warn[k] = v

    if len(health_ok) == len(realServerIp):
        print('all real server are ok')
        sys.exit(RS_OK)

    if len(health_warn) == len(realServerIp):
        print('the all real servers are  down: ', health_warn)
        sys.exit(RS_CRITICAL)

    if len(health_warn) != 0:
        print('there are some real server down: ', health_warn)
        sys.exit(RS_WARNING)


getRealServerIp()
setRealServerStatus()
checkHealth()
