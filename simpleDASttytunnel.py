#!/usr/bin/python3
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort
import socket
import busconnection as bc
import sys
import das

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...

comport = '/dev/ttyUSB0'
netid = '255'
serconn = bc.DasConnectionSerial(comport)
LocalSerialDas = das.Das()
LocalSerialDas.connection = serconn
LocalSerialDas.connect()

print('DAS connected on %s' % comport)

try:
    ServerSocket.bind((LocalHost, LocalPort))
    print('trying to connect on %s %s' % (LocalHost, LocalPort))

except socket.error as err:
    print('connection failed : %s' % err)
    sys.exit()

while 1:
        ServerSocket.listen(2)
        print('Server socket is listening...')
        ConnectedClient, address = ServerSocket.accept()
        print('Connected by ', address)

        cmd = ConnectedClient.recv(5)  # receive command from client
        if not cmd:
                break
        print('Received command', cmd.decode('ascii'), 'from', address)
#        LocalSerialDas.connection.flushOutput() # Empty Das connection output buffer TODO : check this, it looks like it doesn't do anything
        LocalSerialDas.connection.write(cmd)  # send command to local Das
        data = LocalSerialDas.connection.read(80)  # receive data from local Das
        print('Received data from das ', netid, ' on device :', comport)
        print(data.decode('ascii'))
        ConnectedClient.send(data)  # send data to client

ConnectedClient.close()
LocalSerialDas.connection.close()