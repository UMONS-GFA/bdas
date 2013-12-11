# Warning : Don't forget to start the server before running this script
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'


import sys
import socket
from settings import LocalHost, LocalPort

#Host = '10.107.10.41'  # Insert remote server ip or name here
#Port = 10001  # Insert TCP port open for communications here
Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('trying to connect...')

try:
    Sock.connect((LocalHost, LocalPort))
except socket.error as err:
    print('connection failed : %s ' % err)
    sys.exit()

print('Socket connected')

if len(sys.argv) == 2:
        cmd = str(sys.argv[1])
else:
        cmd = '#E1'
cmd += '\n\r'
print('Command :', cmd.encode('utf-8'))
Sock.send(bytearray(cmd,'ascii'))
data = str(Sock.recv(255))
Sock.close()
print('Received', str(data.encode('utf-8')))
