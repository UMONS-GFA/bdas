__author__ = 'Olivier Kaufmann'

import socket
ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with remote server

LocalHost = '127.0.0.1'  # local host IP
LocalPort = 10001  # local host port for communication with client
RemoteHost = 'rochefort.oma.be'
RemotePort = 10001

ServerSocket.bind((LocalHost,LocalPort))
ServerSocket.listen(1)

ClientSocket.connect((RemoteHost,RemotePort))
ConnectedClient, address = ServerSocket.accept()
print 'Connected by', address
while 1:
        cmd = ConnectedClient.recv(255)  # receive command from client
        if not cmd:
                break
        print 'Received command', repr(cmd), 'from', address
        ClientSocket.send(cmd)  # send command to remote host
        print 'Sent command', cmd, 'to', RemoteHost, ':', RemotePort
        data = ClientSocket.recv(1024)  # receive data from remote host
        print 'Received data from', RemoteHost, ':', RemotePort
        print data
        ConnectedClient.send(data)  # send data to client
ConnectedClient.close()
ClientSocket.close()
print 'Received', repr(data)
