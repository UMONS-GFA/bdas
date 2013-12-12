#!/usr/bin/python3
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort
import socket
import busconnection as bc
import sys
import das

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients

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

        cmd = ConnectedClient.recv(255)  # receive command from client
        if not cmd:
                break
        print('Received command', str(cmd), 'from', address)
        LocalSerialDas.connection.write(cmd)  # send command to local Das
        data = LocalSerialDas.connection.read(255)  # receive data from local Das
        print('Received data from das ', netid, ' on device :', comport)
        print(str(data))
        ConnectedClient.send(data)  # send data to client

ConnectedClient.close()
LocalSerialDas.connection.close()