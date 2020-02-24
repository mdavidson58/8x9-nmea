import configparser
import socket
import sys
import operator
from pysnmp.hlapi import *
import pynmea2

# Load Configuration data 
configfile = ['/data/package_config.ini']
config = configparser.ConfigParser()

if len(config.read(configfile)) != len(configfile):
	sys.stderr.write("failed to open config file\n")

IP = config.get('router_info','IP')
OID = config.get('router_info','OID')
send_port = int(config.get('nmea_info','send_port'))
rcv_port = int(config.get('nmea_info','rcv_port'))
send_ip = config.get('nmea_info','send_ip')

sys.stderr.write( 'Dest IP = ' + send_ip + ' Dest Port = ' + str(send_port) + '\n')
sys.stderr.write( 'Recv Port = ' + str(rcv_port) + '\n')
sys.stderr.write( 'OID = ' + OID + '\n')

# open NMEA client Socket
try:
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	clientSock.connect((send_ip, send_port))

except socket.error, errmsg:
	sys.stderr.write( 'Failed to open socket IP = ' + send_ip + ' port = ' + str(send_port) + ' Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n' )
	sys.exit()

# open NMEA server  Socket
try:
	listenSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
	listenSock.bind(('', rcv_port))
	sys.stderr.write('Listening on port ' + str(rcv_port) + '\n')

except socket.error, errmsg:
	sys.stderr.write( 'Failed to listen on socket Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
	sys.exit()

# Get SNMP Data
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
sys.stderr.write( 'ID = ' + str(ID) + '\n')

# write data
while 1:

	try:
		msg, address  = listenSock.recvfrom(1024)

# delete old checksum
		msg = msg[:-4]

# add new ID
		msg = msg + "," + str(ID)

# calculate and add new checksum
		checksum = reduce(operator.xor, map(ord, msg), 0)
		msg = msg + "*" + hex(checksum).replace("0x","") + "\n"

		print "Sending new NMEA msg = ", msg

        	try:                                                                            
	                clientSock.send(msg)                                                 
                                                                                        
	        except socket.error, errmsg:                                                    
	                sys.stderr.write( 'Socket Send Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
	                sys.exit()  

	except socket.error, errmsg:
		sys.stderr.write( 'Socket Rcv Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
		sys.exit()

clientSock.close()
listenSock.close()
