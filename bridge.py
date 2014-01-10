#!/usr/bin/python3
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort
import socket
import sys
import serial

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...

comport = '/dev/ttyUSB0'
netid = '255'
serconn = serial.Serial(
    port=comport,
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
    writeTimeout=1,
    interCharTimeout=1
)
cmd = bytearray()
data = bytearray()
recvcmd = bytearray(1)
recvdata = bytearray(1)
timeout = 1

print('Tunnel connected on %s' % comport)

try:
    ServerSocket.bind((LocalHost, LocalPort))
    print('trying to connect on %s %s' % (LocalHost, LocalPort))

except socket.error as err:
    print('connection failed : %s' % err)
    sys.exit()

ServerSocket.listen(2)
print('Server socket is listening...')
ConnectedClient, address = ServerSocket.accept()
print('Connected by ', address)
serconn.flushInput()  # Empty Das connection input buffer
serconn.flushOutput()  # Empty Das connection output buffer
ConnectedClient.setblocking(0)
cmdnewline = False
datanewline = False
while 1:
    # transfer command
    try:
        recvcmd = ConnectedClient.recv(1)  # receive command byte from client
        if recvcmd:
            cmd += recvcmd
            if recvcmd.decode('ascii') == '\n':
               cmdnewline = True
            elif recvcmd.decode('ascii') == '\r':
                if cmdnewline:
                    serconn.write(cmd)  # send data to client
                    print('received command : %s' % cmd.decode('utf-8'))
                    cmd = bytearray()
                cmdnewline = False
            else:
                cmdnewline = False
    except:
        pass
    # transfer data
    try:
        recvdata = serconn.read(1)  # receive data from local Das
        if recvdata:
            ConnectedClient.send(recvdata)  # send data to client
            data += recvdata
            if recvdata.decode('ascii') == '\n':
                datanewline = True
            elif recvdata.decode('ascii') == '\r':
                if datanewline:
                    print('sent data : %s ' % data.decode('utf-8'))
                    data = bytearray()
                datanewline = False
            else:
                datanewline = False
    except:
        pass
ConnectedClient.close()
serconn.close()