# keepalived_snmp_checker
A simple checker for keepalived_snmp to get keepalived realserver status and ipaddr.

The result will be printed on stdout, for nagios to parse.

Ofcourse, you can use Prometheus/Handler to collect metrics.

Snmp lib to see https://github.com/gosnmp/gosnmp.
# usage
go build .

./keepalived_snmp_checker 

