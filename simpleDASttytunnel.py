#!/usr/bin/python3
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort, EOL
import socket
import busconnection as bc
import sys
import das

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...

comport = '/dev/ttyUSB0'
netid = '255'
serconn = bc.NanoDasConnectionSerial(comport)
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
    while 1:
        cmd = ConnectedClient.recv(4)  # receive command from client
        if not cmd:
            break
        check=cmd.decode('ascii').replace('\r','')
        if check != '':
            print('Received command', cmd.decode('ascii'), 'from', address)
            #LocalSerialDas.connection.flushInput() # Empty Das connection output buffer
            LocalSerialDas.connection.write(cmd)  # send command to local Das
        data = LocalSerialDas.connection.read()  # receive data from local Das
        while EOL not in data:
            data += LocalSerialDas.connection.read()  # receive data from remote host
        print('Received data from das ', netid, ' on device :', comport)
        print(data.decode('ascii'))
        ConnectedClient.send(data)  # send data to client
    ConnectedClient.close()

LocalSerialDas.connection.close()