import operator
import serial
import configparser
import socket
import time
import sys
from pysnmp.hlapi import *

# load configuration data

configfile = ['/data/package_config.ini']
config = configparser.ConfigParser()

if len(config.read(configfile)) != len(configfile):
     sys.stderr.write("Failed to open config file\n")

IP = config.get('router_info','IP')
OID = config.get('router_info','OID')
send_port = int(config.get('nmea_info','send_port'))
send_ip = config.get('nmea_info','send_ip')

sys.stderr.write( 'Dest IP = ' + send_ip + ' Dest Port = ' + str(send_port) + '\n')

# open NMEA client socket
try:
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	clientSock.connect((send_ip, send_port))

except socket.error, errmsg:
        sys.stderr.write( 'Failed to open socket IP = ' + send_ip + ' port = ' + str(send_port) + ' Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
	sys.exit()

# get SNMP data
def get(host, oid):

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in getCmd(SnmpEngine(),
                              CommunityData('public'),
                              UdpTransportTarget((host, 161)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid)),
                              lookupMib=False,
                              lexicographicMode=False):

        if errorIndication:
            sys.stderr.write(str(errorIndication) + '\n')
            break

        elif errorStatus:
            sys.stderr.write('%s at %s \n' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break

        else:
            for oid, val in varBinds:
		return val.prettyPrint()

ID = get(IP, OID)
sys.stderr.write("ID = " + str(ID) + '\n')

# Open accelerometer serial port
try:
	ser = serial.Serial('/dev/ttyS3')

except serial.SerialException as ex:
	sys.stderr.write('Error opening /dev/ttyS3\n')
	sys.exit()

while 1:

# read next record
	buf = ser.readline()

# delete \n
	tempbuf = buf.replace(" \n","")

# create custom NMEA message
	outbuf = "$PPCCA," + tempbuf.replace(" ",",") + "," + str(ID)

# calculate and add new checksum
	checksum = reduce(operator.xor, map(ord, outbuf), 0)
	outbuf = outbuf + "*" + hex(checksum).replace("0x","") + "\n"

	print (outbuf)

# send new NMEA mesasge
	try:
		clientSock.send(outbuf)

	except socket.error, errmsg:
		sys.stderr.write( 'Socket Send Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
		sys.exit()

clientSock.close()
