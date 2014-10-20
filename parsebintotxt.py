"""
A binary to txt parser
This program let you choose a binary file and propose to parse and save it as a readable text file.

 """
import os
import datetime
from tkinter import filedialog

# if ask_files is true, asks for input and output files
ask_files = False
in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R013Full_20141010_0600.bin'
out_filename = '/home/su530201/PycharmProjects/DownloadDAS/R013Full_20141010_0600'

# time step between two data [s]
time_step = 1

# if double_ff_flag is true, reads 4 ff after the fd block instead of 2 ff...
double_ff_flag = True

# if check_length is true, the process will end after kmax
check_length_flag = True
k = 1
k_max = 350000

# if date_as_secs_since_epoch is true, converts to epoch otherwise to string date
date_as_secs_since_epoch = False

# verbose_flag
verbose_flag = False

# separator in text file
sep = ','

#outfile extension
ext = '.txt'

# dtm format for mgr compatibility
dtm_format = True
site = '0000'
netid = '255'
data = ''
bpos = '1'

if dtm_format:
    date_as_secs_since_epoch = False
    sep = ' '
    ext = '.dtm'

out_filename += ext

if ask_files:
    home = os.path.expanduser('~')
    in_filename = filedialog.askopenfilename(filetypes=('binary {*.bin}', 'Binary files'),
                                             initialdir = home, initialfile = '')
    out_filename = os.path.splitext(os.path.basename(in_filename))[0]
    outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.txt}"), initialfile = out_filename + ext)
else:
    outfile = open(out_filename, 'wt')

infile = open(in_filename, 'rb')

# reading begin message
b = infile.read(1)
i = 0
while b == b'\xfd':
    i += 1
    b = infile.read(1)
    if verbose_flag:
        print(b)

if (i % 3 == 0) & (i > 0):
    n_channels = int(i / 3)
    if verbose_flag:
        print('Number of channels :' + str(n_channels))
    eot = False
else:
    print('Format error : unexpected number of leading 0xFD!:' + str(i))
    n_channels = 0
    eot = True
    exit()

b1 = infile.read(1)

# looking for extra 00
if b == b'\x00':
    b = b1
    b1 = infile.read(1)
    if verbose_flag:
        print('Warning : extra 00 after leading 0xFD!')

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
if (b == b'\xff') and (b1 == b'\xff'):
    date_block = True
else:
    print('Format error : Date block not detected...')
    if verbose_flag:
        print('Unexpected values for the 2 bytes following 0xFD!)')
        print(b)
        print(b1)
    date_block = False
    exit()

# reading D1 D2 D3 D4
b = infile.read(4)
while date_block:
    while b[0].to_bytes(1, 'big') == b'\xff':
        if b[1].to_bytes(1, 'big') == b'\xff':
            double_ff_flag = True
            if verbose_flag:
                print('Doubled 0xFF 0xFF flag activated.')
            b1 = infile.read(2)
            b = b[2:4] + b1
        else:
            print('Error : unexpected format, 3 consecutive 0xFF in date block !')
            exit()
        secs_since_epoch = int.from_bytes(b, byteorder='big')
        cur_time = datetime.datetime.utcfromtimestamp(secs_since_epoch)
        if verbose_flag:
            print('starting date:' + cur_time.strftime('%d/%m/%Y %H:%M:%S'))
        if dtm_format:
            s = '# INFO: interruption ' + cur_time.strftime('%Y %m %d %H %M %S') + '\n'
            outfile.writelines(s)
        date_block = True

        # reading optional 00 00 00
        for i in range(3, n_channels + 1):
            b = infile.read(3)
            if b != b'\x00\x00\x00':
                print('format error : unexpected values for the bytes following the date section!')
                print(b)
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
                        print(event_time.strftime('%Y/%m/%d %H:%M:%S'), 'Event recorded')
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
                    print(cur_time.strftime('%Y/%m/%d %H:%M:%S'), map(hex, channel[0:n_channels]))
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
                if k > k_max:
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