__author__ = 'Olivier Kaufmann'

from settings import LocalHost, LocalPort, RemoteHost, RemotePort, EOL
import socket


ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with connecting clients
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # for socket reuse if interrupted (avoid [Errno 98] Address already in use) TODO : check whether this works...
ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket for communication with remote server

ServerSocket.bind((LocalHost, LocalPort))
ServerSocket.listen(1)

ClientSocket.connect((RemoteHost, RemotePort))
print('Tunnel opened...')
ConnectedClient, address = ServerSocket.accept()
print('Connected by ', address)

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
        else:
            while b'\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe\xfe' not in data: # generalize for less than 4 channels
                data += ClientSocket.recv(1024) # receive data from remote host
        print('Received data from', RemoteHost, ':', RemotePort)
        print(repr(data))
        ConnectedClient.send(data)  # send data to client
        print('Data sent to ', address)
ConnectedClient.close()
ClientSocket.close()
