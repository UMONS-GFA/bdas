__author__ = 'Olivier Kaufmann'

import settings
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

    def flushinput(self):
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
            if n == 0:
                output = self.ser.read()
            else:
                output = self.ser.read(n)

        except:
            sys.stderr.write("Error reading on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    #  readline eol doesn't work anymore  http://sourceforge.net/p/pyserial/support-requests/36/
    # is readline still useful ?
    def readline(self):
        try:
            output = self.ser.readline()
        except:
            sys.stderr.write("Error reading on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    def write(self, command):
        try:
            self.ser.write(command)
            self.ser.flush()
        except:
            sys.stderr.write("Error writing command on serial port %s\n" % self.ser.portstr)
            sys.exit(1)

    def inwaiting(self):
        try:
            output = self.ser.inWaiting()
        except:
            sys.stderr.write("inWaiting error on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    def flushinput(self):
        try:
            self.ser.flushInput()
        except:
            sys.stderr.write("flushInput error on serial port %s\n" % self.ser.portstr)
            sys.exit(1)

class DasConnectionTCP(DasConnection):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Host = settings.LocalHost
    Port = settings.LocalPort

    def __init__(self, Host=settings.LocalHost, Port=settings.LocalPort):
        super(DasConnectionTCP, self).__init__()

        try:
            self.sock.connect((self.Host, self.Port))
            #self.sock.setblocking(0)  # non blocking socket
        except socket.error as err:
            sys.stderr.write("Error %s when connecting to TCP port %s on host %s \n" % (err, self.Port, self.Host))
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
            output = self.sock.recv()
        except:
            sys.stderr.write("Error reading on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)
        return output

    def write(self,command):
        try:
            self.sock.send(command)
        except socket.error as err:
            sys.stderr.write("Error %s when writing command on TCP port %s on host %s \n" % (err, self.Port, self.Host))
            sys.exit(1)

    def inwaiting(self):
        try:
            #output=self.sock.listen()  # TODO : Verify this
            output=0
        except:
            sys.stderr.write("inWaiting error on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)
        return output

    def flushinput(self):
        try:
            self.sock.recv(1024)  # TODO : Improve this
        except:
            sys.stderr.write("flushOutput error on TCP port %s on host %s \n" % (self.Port, self.Host))
            sys.exit(1)