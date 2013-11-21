__author__ = 'Olivier Kaufmann'
# Warning : Don't forget to start the server before running this script

import sys
import socket

Sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
Host = 'mg3d.umons.ac.be'  # Insert remote server ip or name here
Port = 10001  # Insert TCP port open for communications here

Sock.connect((Host, Port))

print 'Socket connected'

if len(sys.argv) == 2:
        cmd = str(sys.argv[1])
else:
        cmd = '-005'
cmd += '\n\r'
print 'Command :', repr(cmd)
Sock.send(cmd)
data = Sock.recv(1024)
Sock.close()
print 'Received', repr(data)
