__author__ = 'Olivier Kaufmann'

from settings import RemoteHost, RemotePort
import serial
import socket
import sys
#import os


class DasConnection(object):
    """ A generic test class for connecting to a DAS via RS-232, TCP, ..."""
    def __init__(self):
        pass

    def read(self, n=1024):
        pass

    def readline(self):
        pass

    def write(self, command):
        pass

    def inwaiting(self):
        pass


class DasConnectionSerial(DasConnection):
    ser = serial.Serial()

    def __init__(self, comport):
        super(DasConnectionSerial, self).__init__()
        self.ser = serial.Serial(
            port=comport,  # '/dev/pts/3' ou '/dev/ttyUSB0'
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            #timeout=1,
            #writeTimeout=1,
            interCharTimeout=1
        )
        try:
            self.ser.isOpen()
        except:
            sys.stderr.write("Error opening serial port %s\n" % self.ser.portstr)
            sys.exit(1)

    def __del__(self):
        self.ser.close()

    def read(self, n=0):
        try:
            if n==0:
                output=self.ser.read()
            else:
                output = self.ser.read(n)

        except:
            sys.stderr.write("Error reading on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    def readline(self):
        try:
            output = self.ser.readline()
        except:
            sys.stderr.write("Error reading on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output

    def write(self,command):
        try:
            self.ser.write(command)
            self.ser.flush()
        except:
            sys.stderr.write("Error writing command on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)

    def inwaiting(self):
        try:
            output=self.ser.inWaiting()
        except:
            sys.stderr.write("inWaiting error on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output

class DasConnectionTCP(DasConnection):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Host = RemoteHost
    Port = RemotePort

    def __init__(self,address):
        super(DasConnectionTCP, self).__init__()

        try:
            self.sock.connect((self.Host, self.Port))
        except:
            sys.stderr.write("Error connecting to TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)


    def __del__(self):
        self.sock.close()

    def read(self, n=[]):
        try:
            if n == []:
                output = self.sock.recv()  # TODO : verify this
            else:
                output = self.sock.recv(n)  # TODO : verify if recvfrom_into() is more appropriate

        except:
            sys.stderr.write("Error reading on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)
        return output

    def readline(self):
        try:
            output=self.sock.recv()
        except:
            sys.stderr.write("Error reading on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)
        return output

    def write(self,command):
        try:
            self.sock.send(command)
        except:
            sys.stderr.write("Error writing command on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)

    def inwaiting(self):
        try:
            output=self.sock.listen()  # TODO : Verify this
        except:
            sys.stderr.write("inWaiting error on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)
        return output