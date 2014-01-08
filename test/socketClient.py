# Warning : Don't forget to start the server before running this script
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'


import sys
import socket
from settings import RemoteHost, RemotePort

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('trying to connect...')

try:
    Sock.connect((RemoteHost, RemotePort))
except socket.error as err:
    print('connection failed : %s ' % err)
    sys.exit()

print('Socket connected')

if len(sys.argv) == 2:
        cmd = str(sys.argv[1])
else:
        cmd = '#E1'
cmd += '\n\r'
cmd = bytearray(cmd.encode('ascii'))
while 1:
    print('Command :', cmd.decode())
    Sock.send(cmd)
    data = Sock.recv(80)
    sdata = data.decode('ascii')
    print('Received', sdata)
    input('Press any key to send command again')
Sock.close()
