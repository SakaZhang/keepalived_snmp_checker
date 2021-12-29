package main

import (
	"fmt"
	"github.com/gosnmp/gosnmp"
	"net"
	"os"
	"strings"
	"time"
)

var (
	realServerIP        = make(map[string]string)
	realServerIPADDROid = "1.3.6.1.4.1.9586.100.5.3.4.1.4"
	realServerStatusOid = "1.3.6.1.4.1.9586.100.5.3.4.1.6"
	printRealServer     = make(map[string]int)
	health_ok           []int
	health_warn         = make(map[string]int)

	RS_OK       = 0
	RS_WARNING  = 1
	RS_CRITICAL = 2
	RS_UNKNOWN  = 3
)

func InitSnmpPoller() (poller gosnmp.GoSNMP) {
	poller.Target = "127.0.0.1"
	poller.Community = "public"
	poller.Version = gosnmp.Version2c
	poller.Retries = 3
	poller.Timeout = 3 * time.Second
	poller.MaxOids = 60
	poller.Port = 161
	return poller
}

func getRealServerIPADDR(poller gosnmp.GoSNMP, oid string) {
	err := poller.BulkWalk(oid, setRealServerIPADDR)
	if err != nil {
		fmt.Printf("Walk RealServerIpaddr err:%v\n", err)
		os.Exit(RS_UNKNOWN)
	}
}

func setRealServerIPADDR(pdu gosnmp.SnmpPDU) error {
	switch pdu.Type {
	case gosnmp.OctetString:
		b := pdu.Value.([]byte)
		realServerIP[pdu.Name] = net.IP.String(b)
	}

	return nil
}

func getRealServerStatus(poller gosnmp.GoSNMP, oid string) {
	err := poller.BulkWalk(oid, setRealServerStatus)
	if err != nil {
		fmt.Printf("Walk RealServerStatus err:%v\n", err)
		os.Exit(RS_UNKNOWN)
	}
}

func setRealServerStatus(pdu gosnmp.SnmpPDU) error {
	switch pdu.Type {
	case gosnmp.Integer:
		v := pdu.Value.(int)
		for key, value := range realServerIP {
			if strings.TrimPrefix(key, ".1.3.6.1.4.1.9586.100.5.3.4.1.4.") == strings.TrimPrefix(pdu.Name, ".1.3.6.1.4.1.9586.100.5.3.4.1.6.") {
				printRealServer[value] = v
			}
		}
	}
	return nil
}

func main() {

	pollerIpaddr := InitSnmpPoller()
	err := pollerIpaddr.Connect()
	if err != nil {
		fmt.Printf("checker connect err: %v\n", err)
		os.Exit(RS_UNKNOWN)
	}
	defer pollerIpaddr.Conn.Close()

	pollerStatus := InitSnmpPoller()
	err = pollerStatus.Connect()
	if err != nil {
		fmt.Printf("checker connect err: %v\n", err)
		os.Exit(RS_UNKNOWN)
	}
	defer pollerStatus.Conn.Close()
	getRealServerIPADDR(pollerIpaddr, realServerIPADDROid)
	getRealServerStatus(pollerStatus, realServerStatusOid)

	for k, v := range printRealServer {
		if v == 1 {
			health_ok = append(health_ok, v)

		} else {
			health_warn[k] = v
		}
	}

	if len(health_ok) == len(printRealServer) {
		fmt.Printf("all realservers are ok.")
		os.Exit(RS_OK)
	}

	if len(health_warn) == len(printRealServer) {
		fmt.Printf("all realserver are down.check it. "+"realserers:%v\n ", health_warn)
		os.Exit(RS_CRITICAL)
	}

	if len(health_warn) != 0 {
		fmt.Printf("there are some realservers down. realservers: %v\n", health_warn)
		os.Exit(RS_WARNING)
	}
}
