#!/usr/bin/python3
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort, RemoteHost, RemotePort
import socket
import sys
import serial
import time

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with remote server
ClientSocket.connect((RemoteHost, RemotePort))
ClientSocket.setblocking(0)

try:
    ServerSocket.bind((LocalHost, LocalPort))
    print('trying to connect on %s %s' % (LocalHost, LocalPort))

except socket.error as err:
    print('connection failed : %s' % err)
    sys.exit()

print('Tunnel opened...')
data = bytearray()
timeout = 0.3

while 1:
    ServerSocket.listen(2)
    print('Server socket is listening...')
    ConnectedClient, address = ServerSocket.accept()
    print('Connected by ', address)
    while 1:
        cmd = ConnectedClient.recv(255)  # receive command from client
        if not cmd:
            break
        print('Received command', cmd.decode('ascii'), 'from', address)
        ClientSocket.send(cmd)  # send command to remote host
        print('Sent command %s to %s:%d' % (cmd, RemoteHost, RemotePort))
        time.sleep(1)
        #beginning time
        starttime = time.time()
        counter = 0
        while 1:
            #if you got some data, then break after timeout
            if data and time.time()-starttime > timeout:
                break

            #if you got no data at all, wait a little longer
            elif time.time()-starttime > timeout*5:
                print('No response...')
                break
            #recv something
            try:
                recvdata = ClientSocket.recv(1024)  # receive data from remote host
                if recvdata:
                    counter += 1
                    data.append(recvdata)
                    print('. %d' % counter)
                    if counter == 64:
                        ConnectedClient.send(data())  # send data to client
                        counter = 0
                    sdata = recvdata.decode('ascii')
                    print(sdata)
                    #change the beginning time for measurement
                    starttime = time.time()
                else:
                    #sleep for sometime to indicate a gap
                    time.sleep(0.1)
                    print('Waiting...')
            except:
                pass
        print('Received data from', RemoteHost, ':', RemotePort)
        print(data.decode('utf-8'))
        ConnectedClient.send(data)  # send data to client
    ConnectedClient.close()