__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort, RemoteHost, RemotePort, EOL
import socket
import sys
import time

ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with remote server

ServerSocket.bind((LocalHost, LocalPort))
ServerSocket.listen(1)

ClientSocket.connect((RemoteHost, RemotePort))
print('Tunnel opened...')
ConnectedClient, address = ServerSocket.accept()
print('Connected by ', address)
downloading=False
ClientSocket.setblocking(False)
while 1:
        cmd = ConnectedClient.recv(4)  # receive command from client
        if not cmd :
                break
        check=cmd.decode('ascii').replace(EOL.decode('ascii'),'')
        if check != '':
            print('Received command', repr(cmd), 'from', address)
            ClientSocket.send(cmd)  # send command to remote host
            print('Sent command', cmd, 'to', RemoteHost, ':', RemotePort)
        data = ClientSocket.recv(1024)  # receive data from remote host
        if cmd != b'#XB'+EOL:
            while EOL not in data:
                data += ClientSocket.recv(1024)  # receive data from remote host
            print('Received data from', RemoteHost, ':', RemotePort)
            print(repr(data))
        else:
            print('*** Waiting for download... ***')
            while b'\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd' not in data: # generalize for less than 4 channels
                data += ClientSocket.recv(64) # receive data from remote host
                sys.stdout.write('.')
                remdata=data[0:data.find(b'\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd')]
                ConnectedClient.send(data)  # send data to client
                print('Data sent to ', address)
                data=data[data.find(b'\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd\xfd'):-1]
            downloading=True
            print('*** Now downloading... ***')
            k=0
            while b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe' not in data: # generalize for less than 4 channels
                data += ClientSocket.recv(1024) # receive data from remote host
                print(repr(k),end='\r')
                time.sleep(0.2)
                msg=b'\x00'
                while msg!=b'\x01':
                    ConnectedClient.send(data)  # send data to client
                    msg = ConnectedClient.recv(1)
                data=b''
                k+=1024

            print('*** Download complete!***')
        if data != b'':
            ConnectedClient.send(data)  # send data to client
            print('Data sent to ', address)
ConnectedClient.close()
ClientSocket.close()
