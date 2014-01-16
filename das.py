__author__ = 'Olivier Kaufmann'
import busconnection as bc
import numpy as np
import time
import datetime


class Das(object):
    netid = ''
    connection = bc.DasConnection()

    def __init__(self, netid='255', conn=bc.DasConnectionSerial('/dev/ttyUSB0')):
        self.netid = netid
        self.connection = conn

    def scan(self):
        output = ''
        command = '-999\n\r'
        command = command.encode('ascii')
        print('Scanning ports')
        while output == '':
            self.connection.write(command)
            #TODO: handle multiple das
            output = self.connection.read(22)
            #output = self.connection.readline()
            print('.')
        output = output.decode('utf-8')
        return output

    def connect(self):
        output = ''
        command = '-%s\n\r' % self.netid
        command = command.encode('ascii')
        print('Connecting port %s' % self.netid)
        while output == '':
            self.connection.write(command)
            time.sleep(1)
            while self.connection.inwaiting() > 0:
                output += self.connection.read(1).decode('utf-8')
            print('.')
        return output

    def get_help(self):
        pass

    def set_no_echo(self):
        self.connect()
        output = ''
        command = '#E0\n\r'
        command = command.encode('ascii')
        print('Set no echo')
        while output == '':
            self.connection.write(command)
            output = self.connection.read(21)
        output = output.decode('utf-8')
        return output

    def set_echo_data(self):
        self.connect()
        output = ''
        command = '#E1\n\r'
        command = command.encode('ascii')
        print('Set echo data')
        while output == '':
            self.connection.write(command)
            output = self.connection.read(3)
        output = output.decode('utf-8')
        return output

    def set_echo_data_and_time(self):
        self.connect()
        output = ''
        command = '#E2\n\r'
        command = command.encode('ascii')
        print('Set echo data and time')
        while output == '':
            self.connection.write(command)
            output = self.connection.read(3)
        output = output.decode('utf-8')
        return output

    def set_date_and_time(self):
        pass

    def get_date_and_time(self):
        pass

    def set_integration_period(self):
        pass

    def get_integration_period(self):
        pass

    def set_das_netid(self):
        pass

    def get_das_netid(self):
        pass

    def set_station_number(self):
        pass

    def get_station_number(self):
        pass

    def set_das_info(self):
        pass

    def get_das_info(self):
        pass

    def get_last_data(self):
        pass

    def get_memory_info(self):
        pass

    def flash_das(self):
        pass

    def listen(self, timelapse):
        output = ''
        print('Listening port %s' % self.netid)
        while output == '':
            time.sleep(timelapse)
            while self.connection.inwaiting() > 0:
                output += self.connection.read(1).decode('utf-8')
            print('.')
        return output

    def download(self, filename):
        site = 'site'
        data = ''
        bpos = '1'
        info = 'interruption 2013 05 24 19 35 12'
        timestep = 1.0
        self.connect()
        command = '#XB\n\r'
        command = command.encode('ascii')
        print('Downloading')
        n = 0
        b = []
        while (b == []) & (n < 5):
            self.connection.write(command)
            print('.')
            b = self.connection.read(1)
            print(b)
            # Given a string representing one Unicode character, return an integer representing the
            # Unicode code point of that character.
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
            nchannels = int(i / 3)
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
        b = str(b)
        curtime = np.int(ord(b[3]) + 256 * ord(b[2]) + 256 * 256 * ord(b[1]) + 256 * 256 * 256 * ord(b[0]))
        print(type(curtime))
        print(str(curtime))
        print(hex(curtime))
        curtime = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0), '%Y:%d:%m:%H'
           ':%M:%S') + datetime.timedelta(seconds=curtime)
        print('starting date:' + curtime.strftime('%d/%m/%Y %H:%M:%S'))

        # reading optional 00 00 00
        for i in range(3, nchannels + 1):
            b = self.connection.read(3)
            b = str(b)
            b = np.int(ord(b[2]) + 256 * ord(b[1]) + 256 * 256 * ord(b[0]))
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
                s = '# UDAS: ' + self.netid
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
                        sb = str(sb)
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
