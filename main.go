package main

import (
	"flag"
	"fmt"
	"github.com/gosnmp/gosnmp"
	"log"
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
)

func InitSnmpPoller(target string) (poller gosnmp.GoSNMP) {
	poller.Target = target
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
		log.Fatalf("Walk RealServerIpaddr err:%v\n", err)
		os.Exit(1)
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
		log.Fatalf("Walk RealServerStatus err:%v\n", err)
		os.Exit(1)
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
	flag.Parse()
	target := flag.Args()[0]
	pollerIpaddr := InitSnmpPoller(target)

	err := pollerIpaddr.Connect()
	if err != nil {
		log.Fatalf("checker connect err: %v\n", err)
	}
	defer pollerIpaddr.Conn.Close()

	pollerStatus := InitSnmpPoller(target)
	err = pollerStatus.Connect()
	if err != nil {
		log.Fatalf("checker connect err: %v\n", err)
	}
	defer pollerStatus.Conn.Close()

	for {
		time.Sleep(5 * time.Second)
		getRealServerIPADDR(pollerIpaddr, realServerIPADDROid)
		getRealServerStatus(pollerStatus, realServerStatusOid)
		fmt.Println(printRealServer)
	}
}
