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
connection=bc.DasConnectionSerial(comport)
print('DAS connected on %s' % comport)
data='brol'

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

        cmd = str(ConnectedClient.recv(255))  # receive command from client
        if not cmd:
                break
        print('Received command', repr(cmd), 'from', address)
        # ClientSocket.send(cmd)  # send command to remote host
#        LocalSerialDas.send(cmd)  # send command to local Das
#        data=LocalSerialDas.connection.read(1024) # receive data from local Das
        #data = ClientSocket.recv(1024)  # receive data from remote host
#        print('Received data from das ', netid, ' on device :', comport)
#        print(repr(data))
        ConnectedClient.send(data)  # send data to client
ConnectedClient.close()
LocalSerialDas.connection.close()
print('Received', repr(data))
