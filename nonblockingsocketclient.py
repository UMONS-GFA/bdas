# Warning : Don't forget to start the server before running this script
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'


import sys
import socket
import time
from settings import LocalHost, LocalPort

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Sock.setblocking(1)

data = bytearray()
timeout = 0.8

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
        cmd = '#HE'
cmd += '\n\r'
cmd = bytearray(cmd.encode('ascii'))
Sock.setblocking(0)
while 1:
    print('Command :', cmd.decode())
    Sock.send(cmd)
    #beginning time
    starttime = time.time()
    while 1:
        #if you got some data, then break after timeout
        if data and time.time()-starttime > timeout:
            break

        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-starttime > timeout*5:
            break
        #recv something
        try:
            recvdata = Sock.recv(64)
            if recvdata:
                data += recvdata
                sdata = recvdata.decode('ascii')
                #print('Received', sdata)
                #change the beginning time for measurement
                begin = time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    print('Message received', data.decode('ascii'))
    data = bytearray()
    cmd = input('Type command (type #HE for help).\n\r')
    if not cmd or cmd.lower() == 'exit':
        break
    else:
        cmd += '\n\r'
        cmd = bytearray(cmd.encode('ascii'))
Sock.close()
