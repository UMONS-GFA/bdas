"""
A binary to txt parser
This program let you choose a binary file and propose to parse and save it as a readable text file.

 """
import os
import datetime
from tkinter import filedialog


def parse_bin_to_ascii(in_filename='', out_filename='', time_step=60, k_max=330000, date_as_secs_since_epoch=False,
                       verbose_flag=False, sep=',', ext='.txt', site='0000', netid='255', data='', bpos='1'):
    # in_filename : bin file to convert
    # out_filename : ascii file to create
    # if date_as_secs_since_epoch is true, converts to epoch otherwise to string date
    # if verbose_flag is true, prints messages while processing
    # sep is the separator in the output text file
    # ext is the outfile extension (choose .dtm for compatibility with edas44 format for mgr)

    status = 0
    dtm_format = False
    #status values (binary notation :)
    # 0 : no errors, no warnings
    # first byte : warnings
    # 1   2   4   8   16   32   64   128
    # 1 : Incorrect number of leading 0xFD
    # 2 : Extra 0x00 after leading 0xFD
    # 4 : Unexpected end of file
    # 8 : Doubled 0xFF 0xFF flag activated
    # second byte : errors
    # 256 : 3 consecutive 0xFF in date block
    # 512 : Unexpected values for the 2 bytes following 0xFD
    # 1024 : Unexpected values for the bytes following the date in date block

    if in_filename == '':
        # if ask_files is true, asks for input and output files
        ask_files = True
    else:
        ask_files = False
        if out_filename == '':
            out_filename = os.path.splitext(os.path.abspath(in_filename))[0]
        else:
            out_filename = os.path.splitext(os.path.abspath(out_filename))[0]  # remove extension if stated

    if ext == '.dtm':
        date_as_secs_since_epoch = False
        sep = ' '
        dtm_format = True

    out_filename += ext

    # if double_ff_flag is true, reads two successive ff as one single ff...
    double_ff_flag = False

    if k_max > 0:
        # if check_length is true, the process will end after kmax
        check_length_flag = True
    k = 1

    if ask_files:
        home = os.path.expanduser('~')
        in_filename = filedialog.askopenfilename(filetypes=('binary {*.bin}', 'Binary files'),
                                                 initialdir = home, initialfile = '')
        out_filename = os.path.splitext(os.path.basename(in_filename))[0]
        if dtm_format:
            outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.dtm}"),
                                               initialfile = out_filename + ext)
        else:
            outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*." + ext + "}"),
                                               initialfile = out_filename + ext)
    else:
        outfile = open(out_filename, 'wt')

    if verbose_flag:
        print('____________\nUTC time :' + datetime.datetime.utcnow().strftime('%Y %m %d %H:%M')
              + ' Parsing DAS bin file...')
        print('in_filename : ' + in_filename)
        print('out_filename : ' + out_filename)
        print('station : ' + site)
        print('DAS number : ' + netid)
        print('integration period : ' + str(time_step))
        if date_as_secs_since_epoch:
            print('date as seconds since epoch')
        else:
            print('date as string')

    k_tot = round((os.stat(in_filename).st_size - 40)/12, 0)
    infile = open(in_filename, 'rb')

    # reading begin message
    b = infile.read(1)
    i = 0
    while b == b'\xfd':
        i += 1
        b = infile.read(1)

    if (i % 3 == 0) & (i > 0):
        n_channels = int(i/3)
        if verbose_flag:
            print('Number of channels :' + str(n_channels))
        eot = False
    else:
        n_channels = round(i/3, 0)
        if verbose_flag:
            print('*** Warning : unexpected number of leading 0xFD!:' + str(i))
            print('*** Assuming ' + str(n_channels) + ' channels!')
        status += 1

    # looking for extra 00
    if b == b'\x00':
        infile.seek(1, 1)
        if verbose_flag:
            print('*** Warning : extra 0x00 after leading 0xFD!')
        status += 2

    infile.seek(-1, 1)
    b = infile.read(2)
    if dtm_format:
        ## write header
        s = '# SITE: ' + site
        outfile.writelines(s + '\n')
        s = '# UDAS: ' + netid
        outfile.writelines(s + '\n')
        s = '# CHAN: YYYY MO DD HH MI SS'
        for i in range(n_channels):
            s = s + ' ' + format(i + 1, '04d')
        outfile.writelines(s + '\n')
        s = '# DATA: ' + data
        outfile.writelines(s + '\n')
        s = '# BPOS: ' + bpos
        outfile.writelines(s + '\n')

    # reading date block FF FF
    if b == b'\xff\xff':
        date_block = True
    else:
        if verbose_flag:
            print('*** Error : Unexpected values for the 2 bytes following 0xFD!)')
            print(b)
        #date_block = False
        status += 512
        return status

    # reading D1 D2 D3 D4
    b = infile.read(4)
    while date_block:
        while b[0].to_bytes(1, 'big') == b'\xff':
            if b[1].to_bytes(1, 'big') == b'\xff':
                if not double_ff_flag:
                    double_ff_flag = True
                    if verbose_flag:
                        print('*** Warning : Doubled 0xFF 0xFF flag activated.')
                    status += 8
                b = b[2:4] + infile.read(2)

            else:
                print('*** Error : unexpected format, 3 consecutive 0xFF in date block !')
                status += 256
                return status
        secs_since_epoch = int.from_bytes(b, byteorder='big')
        cur_time = datetime.datetime.utcfromtimestamp(secs_since_epoch)
        if verbose_flag:
            print('Starting date:' + cur_time.strftime('%d/%m/%Y %H:%M:%S'))
        if dtm_format:
            s = '# INFO: interruption ' + cur_time.strftime('%Y %m %d %H %M %S') + '\n'
            outfile.writelines(s)

        # reading optional 00 00 00
        for i in range(3, n_channels + 1):
            b = infile.read(3)
            if b != b'\x00\x00\x00':
                print('*** Error : unexpected values for the bytes following the date in date block!')
                print(b)
                status += 1024
                return status
        b = infile.read(2)
        if b == b'\xff\xff':
            date_block = True
            b = infile.read(4)
        else:
            date_block = False

    # reading channels and writing dat file
    if not eot:
        #outfile = open(out_filename, 'wt+')
        try:
            ## write data
            infile.seek(-2, 1)
            while not eot:
                channel = []
                eot = True
                logged_event = False
                for j in range(n_channels):
                    sb = infile.read(3)
                    if len(sb) < 3:
                        if verbose_flag:
                            print('*** Warning : Unexpected end of file!')
                        if dtm_format:
                            s = '# INFO: End Of File\n'
                            outfile.writelines(s)
                        status += 4
                        return status
                    if sb[0] == 0xff:
                        if double_ff_flag:
                            b = infile.read(1)
                            sb = sb[0:1] + sb[2:3] + b
                            if verbose_flag:
                                print('Info : removing repeated ff')
                    if sb[1] == 0xff:
                        if double_ff_flag:
                            b = infile.read(1)
                            sb = sb[0:1] + sb[2:3] + b
                            if verbose_flag:
                                print('Info : removing repeated ff')
                    if sb[2] == 0xff:
                        if double_ff_flag:
                            b = infile.read(1)
                            sb = sb[0:2] + b  # TODO : Check this...
                            if verbose_flag:
                                print('Info : removing repeated ff')

                    # logged event ?
                    if (sb[0] == 0xff) and (sb[1] == 0xff):
                        logged_event = True
                        l = 0
                        infile.seek(-1, 1)
                        sb = b''
                        while l < 10:
                            b = infile.read(1)
                            if (b == b'\xff') and double_ff_flag:
                                b = infile.read(1)
                            sb += b
                            l += 1
                        event_time = datetime.datetime.utcfromtimestamp(int.from_bytes(sb[0:4], 'big'))
                        if verbose_flag:
                            print('Info : ' + event_time.strftime('%Y/%m/%d %H:%M:%S'), 'Event recorded')
                        if dtm_format:
                            s = '# INFO: interruption ' + event_time.strftime('%Y %m %d %H %M %S') + '\n'
                            outfile.writelines(s)
                        else:
                            if date_as_secs_since_epoch:
                                s = 'not implemented yet'  # TODO : implement this condition...
                            else:
                                s = event_time.strftime('%Y/%m/%d %H:%M:%S')
                            s += ' : Event recorded'
                            outfile.writelines(s + '\n')
                        eot = False
                        break
                    else:
                        channel.append(int.from_bytes(sb, byteorder='big'))
                        if channel[j] != 0xfefefe:
                            eot = False

                if not logged_event:
                    secs_since_epoch += time_step    # TODO : check workbook for stops and set date.
                    cur_time = datetime.datetime.utcfromtimestamp(secs_since_epoch)

                    if verbose_flag:
                        if k/1024-round(k/1024) == 0:
                            print(repr(round(100*k/k_tot, 1)) + ' % done', end='\r')
                        # print(cur_time.strftime('%Y/%m/%d %H:%M:%S'), map(hex, channel[0:n_channels]))
                    if date_as_secs_since_epoch:
                        s = str(secs_since_epoch)
                    else:
                        if dtm_format:
                            s = cur_time.strftime('%Y %m %d %H %M %S')
                        else:
                            s = cur_time.strftime('%Y/%m/%d %H:%M:%S')
                    if not eot:
                        for j in range(n_channels):
                            if dtm_format:
                                t = format(channel[j], '013.4f')
                                u = 13
                            else:
                                t = format(channel[j], '05d')
                                u = 5
                            s += sep + t[len(t) - u:len(t)]
                        outfile.writelines(s + '\n')
                    if (k > k_max) and check_length_flag:
                        if verbose_flag:
                            print('Too much rows...')
                        eot = True
                    k += 1
            if dtm_format:
                s = '# INFO: End Of File\n'
                outfile.writelines(s)

        finally:
            infile.close()
            outfile.close()
            print('Ending bin parsing.')
            return status