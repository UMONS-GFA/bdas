__author__ = 'Olivier Kaufmann'

import serial
import socket
import sys
import os
#import das



class DasConnection(object):
    """ A generic test class for connecting to a DAS via RS-232, TCP, ..."""
    def __init__(self):
        pass

    def read(self, n=[]):
        pass

    def readline(self):
        pass

    def write(self, command):
        pass

    def inWaiting(self):
        pass


class DasConnectionSerial(DasConnection):
    ser = serial.Serial()

    def __init__(self,comport):
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
            self.ser.open()
        except:
            sys.stderr.write("Error opening serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)


    def __del__(self):
        self.ser.close()

    def read(self,n=[]):
        try:
            if n==[]:
                output=self.ser.read()
            else:
                output=self.ser.read(n)

        except:
            sys.stderr.write("Error reading on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output

    def readline(self):
        try:
            output=self.ser.readline()
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

    def inWaiting(self):
        try:
            output=self.ser.inWaiting()
        except:
            sys.stderr.write("inWaiting error on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output

class DasConnectionTCP(DasConnection):

    def __init__(self,address):
        super(DasConnectionTCP, self).__init__()
        self.ser=create_connection(address)
        try:
            self.ser.open()
        except:
            sys.stderr.write("Error opening serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)


    def __del__(self):
        self.ser.close()

    def read(self,n=[]):
        try:
            if n==[]:
                output=self.ser.read()
            else:
                output=self.ser.read(n)

        except:
            sys.stderr.write("Error reading on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output

    def readline(self):
        try:
            output=self.ser.readline()
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

    def inWaiting(self):
        try:
            output=self.ser.inWaiting()
        except:
            sys.stderr.write("inWaiting error on serial port %s\n" % (self.ser.portstr) )
            sys.exit(1)
        return output