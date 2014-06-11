import sys
import socket
import serial
import settings


class DasConnection(object):
    """ A generic test class for connecting to a DAS via RS-232, TCP, etc. """
    def __init__(self):
        pass

    def read(self, n=1024):
        """
        A method to read data
        @param n: number of bit to read
        """
        pass

    def readline(self):
        """ A method to read a line of data  """
        pass

    def write(self, command):
        """
        A method to send command
        @param command: command to send
        @return:
        """
        pass

    def inwaiting(self):
        pass

    def flushinput(self):
        """ A method to flush pending data """
        pass


class NanoDasConnectionSerial(DasConnection):
    """A serial DAS connection """
    ser = serial.Serial()

    def __init__(self, comport):
        super(NanoDasConnectionSerial, self).__init__()
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
        """
        A method to read data
        @param n: number of bit to read, 0 = no limit
        @return: bits read
        """
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
        """ A method to read a line of data  """
        try:
            output = self.ser.readline()
        except ValueError:
            sys.stderr.write("Error reading on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    def write(self, command):
        """
        A method to send command
        @param command: command to send
        """
        try:
            self.ser.write(command)
            self.ser.flush()
        except:
            sys.stderr.write("Error writing command on serial port %s\n" % self.ser.portstr)
            sys.exit(1)

    def inwaiting(self):
        """
        @return: Return the number of chars in the receive buffer.
        """
        try:
            output = self.ser.inWaiting()
        except:
            sys.stderr.write("inWaiting error on serial port %s\n" % self.ser.portstr)
            sys.exit(1)
        return output

    def flushinput(self):
        """ A method to flush pending data """
        try:
            self.ser.flushInput()
        except:
            sys.stderr.write("flushInput error on serial port %s\n" % self.ser.portstr)
            sys.exit(1)

class NanoDasConnectionTCP(DasConnection):
    """A TCP DAS connection """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = settings.LocalHost
    port = settings.LocalPort

    def __init__(self, host=settings.LocalHost, port=settings.LocalPort):
        super(NanoDasConnectionTCP, self).__init__()

        try:
            self.sock.connect((self.host, self.port))
            #self.sock.setblocking(0)  # non blocking socket
        except socket.error as err:
            sys.stderr.write("Error %s when connecting to TCP port %s on host %s \n" % (err, self.port, self.host))
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
            sys.stderr.write("Error reading on TCP port %s on host %s \n" % (self.port, self.host))
            sys.exit(1)
        return output

    def readline(self):
        """ A method to read a line of data  """
        try:
            output = self.sock.recv()
        except:
            sys.stderr.write("Error reading on TCP port %s on host %s \n" % (self.port, self.host))
            sys.exit(1)
        return output

    def write(self,command):
        """
        A method to send command
        @param command: command to send
        """
        try:
            self.sock.send(command)
        except socket.error as err:
            sys.stderr.write("Error %s when writing command on TCP port %s on host %s \n" % (err, self.port, self.host))
            sys.exit(1)

    def inwaiting(self):
        try:
            #output=self.sock.listen()  # TODO : Verify this
            output=0
        except:
            sys.stderr.write("inWaiting error on TCP port %s on host %s \n" % (self.port, self.host))
            sys.exit(1)
        return output

    def flushinput(self):
        """ A method to flush pending data """
        try:
            self.sock.recv(1024)  # TODO : Improve this
        except:
            sys.stderr.write("flushOutput error on TCP port %s on host %s \n" % (self.port, self.host))
            sys.exit(1)