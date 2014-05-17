# Warning : Don't forget to start the server before running this script
#-*- coding: utf8 -*-

__author__ = 'Olivier Kaufmann'


import sys
import socket
import time
from settings import LocalHost, LocalPort, EOL

Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

data = bytearray()
timeout = 0.2

print('trying to connect...')

try:
    Sock.connect((LocalHost, LocalPort))
except socket.error as err:
    print('connection failed : %s ' % err)
    sys.exit()

print('Socket connected')#HE

if len(sys.argv) == 2:
    cmd = str(sys.argv[1])
else:
    cmd = input('Type command (type #HE for help or exit to quit).\n> ')
cmd = bytearray(cmd.encode('ascii'))
cmd += EOL
Sock.setblocking(False)
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
                t=0
                data += recvdata
                starttime = time.time()
                if b'\xfd' in data:
                    data=data[data.find(b'\xfd'):-1]
                    print ('*** Downloading data ... ***')
                    f=open('out.bin','wb')
                    f.close()
                    f=open('out.bin','ab')
                    k=0
                    nxfe=0 # number of terminating \xfe
                    eod=False # end of download
                    while not eod:
                        if k/256-round(k/256)==0 :
                            print(repr(round(k/1024,1)) + ' Kb',end='\r')
                        f.write(data)  # write data to file
                        if data==b'\xfe':
                            nxfe+=1
                            if nxfe==12: # generalize for less than 4 channels
                                eod=True
                        else:
                            nxfe=0
                        if not eod:
                            try :
                                data = Sock.recv(1) # receive data from remote host
                                k+=1
                            except :
                                data=b''
                                #print('Waiting for data...',end="\r")
                    print('*** Download complete! ***')
                    f.close()
                    data = b''
                    datanewline = False
                elif recvdata.decode('ascii') == '\n':
                    datanewline = True
                elif recvdata.decode('ascii') == '\r':
                    if datanewline:
                        print(data.decode('utf-8'))
                        data = bytearray()
                    datanewline = False
                else:
                    sys.stdout.write(data)
                    datanewline = False
            else:
                #sleep for sometime to indicate a gap
                t+=1
                time.sleep(0.1)
                print("Waiting cycles..." + t,"\r")
        except:
            pass
    data = bytearray()
    cmd=input("> ")
    #print(">")
    #cmd = sys.stdin.readline()
    #cmd=cmd[:-1]
    if cmd.lower() == 'exit':
        break
    else:
        cmd = bytearray(cmd.encode('ascii'))
        cmd += EOL
Sock.close()
