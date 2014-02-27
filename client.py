# Warning : Don't forget to start the server before running this script
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'


import sys
import socket
import time
from settings import LocalHost, LocalPort

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

data = bytearray()
timeout = 0.2

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
    cmd = input('Type command (type #HE for help or exit to quit).\n> ')
cmd += '\r'
cmd = bytearray(cmd.encode('ascii'))
Sock.setblocking(0)
newline = False
while 1:
    Sock.send(cmd)
    #beginning time
    starttime = time.time()
    while 1:
        #if you got some data, then break after timeout
        if data and time.time()-starttime > timeout:
            break

        #if you got no data at all, wait a little longer
        elif time.time()-starttime > timeout*3:
            break
        #recv something
        try:
            recvdata = Sock.recv(1)
            if recvdata:
                data += recvdata
                starttime = time.time()
                if recvdata.decode('ascii') == '\n':
                    datanewline = True
                elif recvdata.decode('ascii') == '\r':
                    if datanewline:
                        print(data.decode('utf-8'))
                        data = bytearray()
                    datanewline = False
                else:
                    datanewline = False
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    data = bytearray()
    cmd = sys.stdin.readline()
    if cmd.lower() == 'exit\n':
        break
    else:
        cmd += '\r'
        cmd = bytearray(cmd.encode('ascii'))
Sock.close()
