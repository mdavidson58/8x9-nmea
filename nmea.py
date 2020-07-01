import configparser
import socket
import sys
import serial
import operator
from pysnmp.hlapi import *
import pynmea2

# load configuration data

configfile = ['/data/package_config.ini']
config = configparser.ConfigParser()

if len(config.read(configfile)) != len(configfile):
    sys.stderr.write("Failed to open config file\n")


send_port = int(config.get('nmea_info','send_port'))
send_ip = config.get('nmea_info','send_ip')
ID = config.get('_cisco_mqtt_attributes','gw.serial')

sys.stderr.write( 'Dest IP = ' + send_ip + ' Dest Port = ' + str(send_port) + ' ID = ' + ID + '\n')

# open NMEA client socket
try:
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    clientSock.connect((send_ip, send_port))

except socket.error, errmsg:
    sys.stderr.write( 'Failed to open socket IP = ' + send_ip + ' port = ' + str(send_port) + ' Error Code: ' + str(errmsg[0]) + ' Message ' + errmsg[1] + '\n')
    sys.exit()

# Open accelerometer serial port
try:
    ser = serial.Serial('/dev/ttyS2')

except serial.SerialException as ex:
    sys.stderr.write('Error opening /dev/ttyS2\n')
    sys.exit()

while 1:

# read next record
    buf = ser.readline()

# delete \n
    tempbuf = buf.replace(" \n","")

# delete old checksum
    msg = tempbuf[:-4]

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
