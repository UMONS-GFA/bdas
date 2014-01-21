__author__ = 'Olivier Kaufmann'
import busconnection as bc
import time
import datetime

DEBUG = True

endline = '\r'

class Das(object):
    netid = ''
    connection = bc.DasConnection()

    def __init__(self, netid='255', conn=bc.DasConnectionSerial('/dev/ttyUSB0')):
        self.netid = netid
        self.connection = conn

    def scan(self):
        output = ''
        command = '-999' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Scanning ports')
        self.connection.write(command)
        while output == '':
            #TODO: handle multiple das
            output = self.connection.read(22)
        output = output.decode('utf-8')
        return output

    def connect(self):
        output = ''
        command = '-%s' % self.netid + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        while output == '':
            self.connection.write(command)
            time.sleep(1)
            while self.connection.inwaiting() > 0:
                output += self.connection.read(1).decode('utf-8')
            print('.')
        return output

    def listen(self, timelapse):
        output = ''
        print('Listening port %s' % self.netid)
        while output == '':
            time.sleep(timelapse)
            while self.connection.inwaiting() > 0:
                output += self.connection.read(1).decode('utf-8')
            print('.')
        return output

    def set_no_echo(self):
        self.connect()
        output = bytearray()
        recvdata = bytearray()
        command = '#E0' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set no echo')
        self.connection.write(command)
        k= 0
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    if k == 0:
                        k += 1
                    else:
                        break
        output = output.decode('utf-8')
        return output

    def set_echo_data(self):
        self.connect()
        output = ''
        command = '#E1' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set echo data')
        self.connection.write(command)
        while output == '':
            output = self.connection.read(3)
        output = output.decode('utf-8')
        return output

    def set_echo_data_and_time(self):
        self.connect()
        output = ''
        command = '#E2' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set echo data and time')
        self.connection.write(command)
        while output == '':
            output = self.connection.read(3)
        output = output.decode('utf-8')
        return output

    def set_date_and_time(self):
        self.connect()
        output = bytearray()
        y = datetime.datetime.now().year
        m = datetime.datetime.now().month
        d = datetime.datetime.now().day
        h = datetime.datetime.now().hour
        n = datetime.datetime.now().minute
        s = datetime.datetime.now().second
        command = '#SD %04i %02i %02i %02i %02i %02i' % (y, m, d, h, n, s) + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def set_integration_period(self, integration_period):
        self.connect()
        output = bytearray()
        command = '#SR ' + integration_period + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set integration period')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def set_das_netid(self, netid):
        self.connect()
        output = bytearray()
        command = '#SI %03i' % netid + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set das netid')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def set_station_id(self, station_id):
        self.connect()
        output = bytearray()
        recvdata = bytearray()
        command = '#SS %04i' % station_id + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Set station id')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def get_das_info(self):
        self.connect()
        output = bytearray()
        command = '#RI ' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Get das info')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def set_configuration(self, station_id, netid, integration_period, nbr_instr, cal1, cal2, cal3, cal4):
        self.connect()
        command = "#ZR %04i %03i %04i %01i %04i %04i %04i %04i" % (station_id, netid, integration_period, nbr_instr,
                                                                   cal1, cal2, cal3, cal4) + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print("Set das configuration")
        self.connection.write(command)

    def get_memory_info(self):
        self.connect()
        output = bytearray()
        command = '#RM ' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Get memory info')
        self.connection.write(command)
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        output = output.decode('utf-8')
        return output

    def flash_das(self):
        self.connect()
        output = bytearray()
        command = '#ZF ' + endline
        if DEBUG is True:
            print(repr(command))
        command = command.encode('ascii')
        print('Flash memory and configuration')
        self.connection.write(command)
        #TODO: implement 60 seconds counter
        while 1:
            recvdata = self.connection.read(1)
            if recvdata:
                output += recvdata
                if recvdata.decode('ascii') == '\r':
                    break
        print("Please wait 60 seconds")
        output = output.decode('utf-8')
        return output

    def download(self, filename):
        site = 'site'
        data = ''
        bpos = '1'
        info = 'interruption 2013 05 24 19 35 12'
        timestep = 1.0
        self.connect()
        command = '#XB' + endline
        command = command.encode('ascii')
        print('Downloading')
        n = 0
        b = bytes()
        while (b.__len__() == 0) & (n < 5):
            self.connection.write(command)
            print('.')
            b = self.connection.read(1)
            # Given a string representing one Unicode character, return an integer representing the
            # Unicode code point of that character
            n += 1


        #reading begin message
        i = 0
        while b == b'\xfd':
            i += 1
            b = self.connection.read(1)
            print(b)

        if (i % 3 == 0) & (i > 0):
            nchannels = int(i / 3)
            print('Number of channels :' + str(nchannels))
            eot = False
        else:
            print('format error : unexpected number of leading 0xFD!:' + str(i))
            nchannels = 0
            eot = True
            exit()

        b1 = self.connection.read(1)

        # reading FF FF
        if (b !=  b'\xff') | (b1 !=  b'\xff'):
            print('format error : unexpected values for the 2 bytes following 0xFD!')

        # reading D1 D2 D3 D4
        b = self.connection.read(4)
        print(b)
        #curtime = np.int(ord(b[3]) + 256 * ord(b[2]) + 256 * 256 * ord(b[1]) + 256 * 256 * 256 * ord(b[0]))
        curtime = b[3]+ 256 * b[2] + 256 * 256 * b[1] + 256 * 256 * 256 * b[0]
        curtime = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0), '%Y:%d:%m:%H'
           ':%M:%S') + datetime.timedelta(seconds=curtime)
        print('starting date:' + curtime.strftime('%d/%m/%Y %H:%M:%S'))

        # reading optional 00 00 00
        for i in range(3, nchannels + 1):
            b = self.connection.read(3)
           # b = str(b)
            b = b[2] + 256 *b[1] + 256 * 256 * b[0]
            #print(hex(b))
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
                        #channel.append(ord(sb[2]) + 256 * ord(sb[1]) + 256 * 256 * ord(sb[0]))
                        channel.append(sb[2] + 256 * sb[1] + 256 * 256 * sb[0])
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

    def next_download(self, filename):
        site = 'site'
        data = ''
        bpos = '1'
        info = 'interruption 2013 05 24 19 35 12'
        timestep = 1.0
        self.connect()
        command = '#XN' + endline
        command = command.encode('ascii')
        print('Downloading')
        n = 0
        b = bytes()
        while (b.__len__() == 0) & (n < 5):
            self.connection.write(command)
            print('.')
            b = self.connection.read(1)
            # Given a string representing one Unicode character, return an integer representing the
            # Unicode code point of that character
            n += 1


        #reading begin message
        i = 0
        while b == b'\xfd':
            i += 1
            b = self.connection.read(1)
            print(b)

        if (i % 3 == 0) & (i > 0):
            nchannels = int(i / 3)
            print('Number of channels :' + str(nchannels))
            eot = False
        else:
            print('format error : unexpected number of leading 0xFD!:' + str(i))
            nchannels = 0
            eot = True
            exit()

        b1 = self.connection.read(1)

        # reading FF FF
        if (b !=  b'\xff') | (b1 !=  b'\xff'):
            print('format error : unexpected values for the 2 bytes following 0xFD!')

        # reading D1 D2 D3 D4
        b = self.connection.read(4)
        print(b)
        #curtime = np.int(ord(b[3]) + 256 * ord(b[2]) + 256 * 256 * ord(b[1]) + 256 * 256 * 256 * ord(b[0]))
        curtime = b[3]+ 256 * b[2] + 256 * 256 * b[1] + 256 * 256 * 256 * b[0]
        curtime = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0), '%Y:%d:%m:%H'
           ':%M:%S') + datetime.timedelta(seconds=curtime)
        print('starting date:' + curtime.strftime('%d/%m/%Y %H:%M:%S'))

        # reading optional 00 00 00
        for i in range(3, nchannels + 1):
            b = self.connection.read(3)
           # b = str(b)
            b = b[2] + 256 *b[1] + 256 * 256 * b[0]
            #print(hex(b))
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
                        #channel.append(ord(sb[2]) + 256 * ord(sb[1]) + 256 * 256 * ord(sb[0]))
                        channel.append(sb[2] + 256 * sb[1] + 256 * 256 * sb[0])
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
