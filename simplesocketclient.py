# -*- coding: utf-8 -*-
"""
Created on Sat Oct 19 16:24:51 2013

@author: su530201
"""
# Warning : Don't forget to start server before running this script

import sys, socket

Sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
Host = 'mg3d.umons.ac.be' # Insert remote server ip or name here
Port = 10001 # Insert TCP port open for communications here

Sock.connect((Host,Port))

print 'Socket connected'

if len(sys.argv)==2:
        cmd=str(sys.argv[1])
else :
        cmd = '-005'
cmd=cmd+'\n\r'
print 'Command :',repr(cmd)
Sock.send(cmd)
data=Sock.recv(1024)
Sock.close()
print 'Received', repr(data)
