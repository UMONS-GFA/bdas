__author__ = 'su530201'
#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Olivier Kaufmann'

import serial, socket
import sys, os
#import das
import time,datetime
import numpy as np

class DASConnection(object):
    """ A generic test class for connecting to a DAS via RS-232, TCP, ..."""
    def __init__(self):
        pass

    def read(self,n=[]):
        pass

    def readline(self):
        pass

    def write(self,command):
        pass

    def scan(self):
        output=''
        command = '-999/r/l'
        print('Scanning ports')
        while (output==''):
            self.write(command)
            output=self.readline()
            print('.')
        return output

    def connect(self, aDAS):
        output=''
        command = '-%s/r/l'% aDAS.netId
        print('Connecting port %s'% aDAS.netId)
        while(output==''):
            self.write(command)
            time.sleep(1)
            while (self.inWaiting()>0):
                output += self.read(1)
            print('.')
        return output

    def listen(self, aDAS, timelapse):
        output=''

        print('Listening port %s'% aDAS.netId)
        while (output==''):
            time.sleep(timelapse)
            while (self.inWaiting()>0):
                output += self.read(1)
            print('.')
        return output

    def download(self,aDAS,filename):
        site='site'
        data=''
        bpos='1'
        info='interruption 2013 05 24 19 35 12'
        timestep=1.0
        self.connect(aDAS)
        output=''
        command = '#XB/r/l'
        print('Downloading')
        n=0
        b=[]
        while (b==[]) & (n<5):
            self.write(command)
            print('.')
            b=self.read(1)
            b=ord(b)
            print hex(b)
            n=n+1

       # reading begin message
        i=0
        while (b==0xFD):
            i+=1
            b=self.read(1)
            b=ord(b)
            print hex(b)


        if (i%3==0) & (i>0):
            nchannels=i/3
            print('Number of channels :'+str(nchannels))
            eot=False
        else:
            print('format error : unexpected number of leading 0xFD!:'+str(i))
            nchannels=0
            eot=True

        b1=self.read(1)
        b1=ord(b1)
        print hex(b1)   #            b=np.ubyte(self.ser.read(1))

        # reading FF FF
        if (b!=0xFF)|(b1!=0xFF):
            print('format error : unexpected values for the 2 bytes following 0xFD!')

        # reading D1 D2 D3 D4
        b=self.read(4)

        curtime=np.long(ord(b[3])+256*ord(b[2])+256*256*ord(b[1])+256*256*256*ord(b[0]))
        print hex(curtime)
        curtime=datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i'%(1970,01,01,01,00,00),'%Y:%d:%m:%H:%M:%S')+datetime.timedelta(seconds=curtime)
        print('starting date:'+curtime.strftime('%d/%m/%Y %H:%M:%S'))

        # reading optional 00 00 00
        for i in range (3,nchannels+1) :
            b=self.read(3)
            b=np.long(ord(b[2])+256*ord(b[1])+256*256*ord(b[0]))
            print hex(b)
            if (b!=0x000000):
                print('format error : unexpected values for the bytes following the date section!')

        # reading channels and writing dat file
        if not(eot):
            afile = open(filename, 'w+')
            try :
                ## write header
                s='# SITE: ' + site
                afile.writelines(s+'\n')
                s='# UDAS: ' + aDAS.netId
                afile.writelines(s+'\n')
                s='# CHAN: YYYY MO DD HH MI SS'
                for i in range(nchannels):
                    s=s + ' ' + format(i+1,'04d')
                afile.writelines(s+'\n')
                s='# DATA: ' + data
                afile.writelines(s+'\n')
                s='# BPOS: ' + bpos
                afile.writelines(s+'\n')
                s='# INFO: ' + info
                afile.writelines(s+'\n')
                ## write data
                while not(eot):
                    channel=[]
                    eot=True
                    for j in range(nchannels):
                        sb=self.ser.read(3)
                        channel.append(ord(sb[2])+256*ord(sb[1])+256*256*ord(sb[0]))
                        if channel[j]!=0xfefefe:
                            eot=False
                    curtime=curtime+datetime.timedelta(seconds=timestep)

                    print curtime.strftime('%d/%m/%Y %H:%M:%S'), map(hex,channel[0:nchannels])
                    s=curtime.strftime('%Y %m %d %H %M %S')
                    #s=s[2:len(s)] # if date format YY mm dd HH MM SS
                    if not(eot):
                        for j in range(nchannels):
                            t=format(channel[j],'05d')
                            s+=' '+t[len(t)-5:len(t)]
                        afile.writelines(s+'\n')

            finally :
                afile.close()

            output='Data downloaded to '+filename
        else:
            output='Data not downloaded ! : transmission not valid'
        return output

class DASConnectionSerial(DASConnection):
    ser = serial.Serial()

    def __init__(self,comport):
        super(DASConnectionSerial, self).__init__()
        self.ser = serial.Serial(
            port=comport,#'/dev/pts/3' ou '/dev/ttyUSB0'
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

class DASConnectionTCP(DASConnection):

    def __init__(self,address):
        super(DASConnectionTCP, self).__init__()
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