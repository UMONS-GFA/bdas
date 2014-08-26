"""
A binary to txt parser
This program let you choose a binary file and propose to parse and save it as a readable text file.

 """
import os
import datetime
from tkinter import filedialog

# if epoch is true converts to epoch otherwise to string date
epoch = True
# separator in text file
sep = ','


home = os.path.expanduser('~')
in_filename = filedialog.askopenfilename(filetypes=('binary {*.bin}', 'Binary files'),
                                         initialdir = home, initialfile = '')
out_filename = os.path.splitext(os.path.basename(in_filename))[0]
outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.txt}"), initialfile = out_filename + '.txt')

time_step = 60

infile = open(in_filename, 'rb')
#reading begin message
b = infile.read(1)
i = 0
while b == b'\xfd':
    i += 1
    b = infile.read(1)
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

b1 = infile.read(1)

# reading FF FF
if (b != b'\xff') | (b1 != b'\xff'):
    print('format error : unexpected values for the 2 bytes following 0xFD!')

# reading D1 D2 D3 D4
b = infile.read(4)
print(b)
cur_epoch = b[3] + 256 * b[2] + 256 * 256 * b[1] + 256 * 256 * 256 * b[0]
cur_time = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0),
                                      '%Y:%d:%m:%H:%M:%S') + datetime.timedelta(seconds=cur_epoch)
print('starting date:' + cur_time.strftime('%d/%m/%Y %H:%M:%S'))

# reading optional 00 00 00
for i in range(3, nchannels + 1):
    b = infile.read(3)
# b = str(b)
b = b[2] + 256 * b[1] + 256 * 256 * b[0]
#print(hex(b))
if b != 0x000000:
    print('format error : unexpected values for the bytes following the date section!')

# reading channels and writing dat file
if not eot:
    #outfile = open(out_filename, 'wt+')
    try:
        ## write header
        #s = '# SITE: ' + site
        #outfile.writelines(s + '\n')
        #s = '# UDAS: ' + self.netid
        #outfile.writelines(s + '\n')
        #s = '# CHAN: YYYY MO DD HH MI SS'
        #for i in range(nchannels):
        #    s = s + ' ' + format(i + 1, '04d')
        #outfile.writelines(s + '\n')
        #s = '# DATA: ' + data
        #outfile.writelines(s + '\n')
        #s = '# BPOS: ' + bpos
        #outfile.writelines(s + '\n')
        #s = '# INFO: ' + info
        #outfile.writelines(s + '\n')
        ## write data
        while not eot:
            channel = []
            eot = True
            for j in range(nchannels):
                sb = infile.read(3)
                #channel.append(ord(sb[2]) + 256 * ord(sb[1]) + 256 * 256 * ord(sb[0]))
                channel.append(sb[2] + 256 * sb[1] + 256 * 256 * sb[0])
                if channel[j] != 0xfefefe:
                    eot = False
            cur_time = cur_time + datetime.timedelta(seconds=time_step)
            cur_epoch = cur_epoch + time_step

            print(cur_time.strftime('%d/%m/%Y %H:%M:%S'), map(hex, channel[0:nchannels]))
            if epoch:
                s = str(cur_epoch)
            else:
                s = cur_time.strftime('%Y %m %d %H %M %S')
            #s=s[2:len(s)] # if date format YY mm dd HH MM SS
            if not eot:
                for j in range(nchannels):
                    t = format(channel[j], '05d')
                    s += sep + t[len(t) - 5:len(t)]
                outfile.writelines(s + '\n')

    finally:
        outfile.close()