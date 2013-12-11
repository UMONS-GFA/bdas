__author__ = 'Olivier Kaufmann'
import busconnection as bc
import numpy as np
import time
import datetime


class Das(object):
    netId = ''
    connection = bc.DasConnection()

    def __init__(self, netid='255', conn=bc.DasConnectionSerial('/dev/ttyUSB0')):
        self.netId = netid
        self.connection = conn

    def scan(self):
        output = ''
        command = '-999\r\n'
        print('Scanning ports')
        while output == '':
            self.connection.write(command)
            output = self.connection.readline()
            print('.')
        return output

    def connect(self):
        output = ''
        command = '-%s\r\n' % self.netId
        print('Connecting port %s' % self.netId)
        while output == '':
            self.connection.write(command)
            time.sleep(1)
            while self.connection.inwaiting() > 0:
                output += str(self.connection.read(1))
            print('.')
        return output

    def listen(self, timelapse):
        output = ''

        print('Listening port %s' % self.netId)
        while output == '':
            time.sleep(timelapse)
            while self.connection.inwaiting() > 0:
                output += self.connection.read(1)
            print('.')
        return output

    def download(self, filename):
        site = 'site'
        data = ''
        bpos = '1'
        info = 'interruption 2013 05 24 19 35 12'
        timestep = 1.0
        self.connect()
        command = '#XB\r\n'
        print('Downloading')
        n = 0
        b = []
        while (b == []) & (n < 5):
            self.connection.write(command)
            print('.')
            b = self.connection.read(1)
            b = ord(b)
            print(hex(b))
            n += 1

            # reading begin message
        i = 0
        while b == 0xFD:
            i += 1
            b = self.connection.read(1)
            b = ord(b)
            print(hex(b))

        if (i % 3 == 0) & (i > 0):
            nchannels = i / 3
            print('Number of channels :' + str(nchannels))
            eot = False
        else:
            print('format error : unexpected number of leading 0xFD!:' + str(i))
            nchannels = 0
            eot = True

        b1 = self.connection.read(1)
        b1 = ord(b1)
        print(hex(b1))   # b=np.ubyte(self.ser.read(1))

        # reading FF FF
        if (b != 0xFF) | (b1 != 0xFF):
            print('format error : unexpected values for the 2 bytes following 0xFD!')

        # reading D1 D2 D3 D4
        b = self.connection.read(4)

        curtime = np.long(ord(b[3]) + 256 * ord(b[2]) + 256 * 256 * ord(b[1]) + 256 * 256 * 256 * ord(b[0]))
        print(hex(curtime))
        curtime = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0), '%Y:%d:%m:%H'
           ':%M:%S') + datetime.timedelta(seconds=curtime)
        print('starting date:' + curtime.strftime('%d/%m/%Y %H:%M:%S'))

        # reading optional 00 00 00
        for i in range(3, nchannels + 1):
            b = self.connection.read(3)
            b = np.long(ord(b[2]) + 256 * ord(b[1]) + 256 * 256 * ord(b[0]))
            print(hex(b))
            if b != 0x000000:
                print('format error : unexpected values for the bytes following the date section!')

        # reading channels and writing dat file
        if not eot:
            afile = open(filename, 'w+')
            try:
                ## write header
                s = '# SITE: ' + site
                afile.writelines(s + '\n')
                s = '# UDAS: ' + self.netId
                afile.writelines(s + '\n')
                s = '# CHAN: YYYY MO DD HH MI SS'
                for i in range(nchannels):
                    s = s + ' ' + format(i + 1, '04d')
                afile.writelines(s + '\n')
                s = '# DATA: ' + data
                afile.writelines(s + '\n')
                s = '# BPOS: ' + bpos
                afile.writelines(s + '\n')
                s = '# INFO: ' + info
                afile.writelines(s + '\n')
                ## write data
                while not eot:
                    channel = []
                    eot = True
                    for j in range(nchannels):
                        sb = self.connection.read(3)
                        channel.append(ord(sb[2]) + 256 * ord(sb[1]) + 256 * 256 * ord(sb[0]))
                        if channel[j] != 0xfefefe:
                            eot = False
                    curtime = curtime + datetime.timedelta(seconds=timestep)

                    print(curtime.strftime('%d/%m/%Y %H:%M:%S'), map(hex, channel[0:nchannels]))
                    s = curtime.strftime('%Y %m %d %H %M %S')
                    #s=s[2:len(s)] # if date format YY mm dd HH MM SS
                    if not eot:
                        for j in range(nchannels):
                            t = format(channel[j], '05d')
                            s += ' ' + t[len(t) - 5:len(t)]
                        afile.writelines(s + '\n')

            finally:
                afile.close()

            output = 'Data downloaded to ' + filename
        else:
            output = 'Data not downloaded ! : transmission not valid'
        return output
