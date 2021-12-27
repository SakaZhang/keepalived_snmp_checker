# keepalived_snmp_checker
A simple checker for keepalived_snmp to get realserver status and ipaddr.

The result will be printed on stdout, for nagios to parse.

Ofcourse, you can use Prometheus/Handler to collect metrics.
Snmp lib to see https://github.com/prometheus/snmp_exporter.
# usage
go build .

./keepalived_snmp_checker 127.0.0.1 # or your server ip

