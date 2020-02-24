# 8x9-nmea
Recive NMEA information from IR8x9 and resend it to UDP NMEA server with serial# of router.  Also packages accelerometer data as customer NMEA message
[router_info]

IP: 192.168.55.1. # IP address of router based upon GMM template subnet definition

OID: 1.3.6.1.4.1.9.3.6.3.0 # OID for pulling device name for Cisco devices

[nmea_info]

rcv_port: 6000 # port that will receive UDP NMEA information from router.

send_ip: 10.0.0.250 # IP address of destination UDP NMEA Server

send_port: 6001 # UDP Destination port for UDP NMEA server

The following lines must be configured via a GMM advanced template

gyroscope-reading enable

controller Cellular 0

   lte gps mode standalone

   lte gps nmea ip udp ${gw.ip} ${gw.ip_prefix}.${gw.ip_suffix?number + 2} 6000 stream 1
!
