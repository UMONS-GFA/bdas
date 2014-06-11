"""
Binary to txt parser

 """

import datetime
from tkinter import filedialog

def_dir = '/home/su530201/PycharmProjects/DownloadDAS/'
def_file = 'R002Full_20140603_1827'
#in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.bin'
#out_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.txt'
in_filename = filedialog.askopenfilename(filetypes=('Binary files', 'binary {*.bin}'),
                                         initialdir = def_dir, initialfile = def_file + '.bin')
outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.txt}"), initialfile = def_file + '.txt')

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
#curtime = np.int(ord(b[3]) + 256 * ord(b[2]) + 256 * 256 * ord(b[1]) + 256 * 256 * 256 * ord(b[0]))
cur_time = b[3] + 256 * b[2] + 256 * 256 * b[1] + 256 * 256 * 256 * b[0]
cur_time = datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (1970, 1, 1, 1, 0, 0),
                                      '%Y:%d:%m:%H:%M:%S') + datetime.timedelta(seconds=cur_time)
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

            print(cur_time.strftime('%d/%m/%Y %H:%M:%S'), map(hex, channel[0:nchannels]))
            s = cur_time.strftime('%Y %m %d %H %M %S')
            #s=s[2:len(s)] # if date format YY mm dd HH MM SS
            if not eot:
                for j in range(nchannels):
                    t = format(channel[j], '05d')
                    s += ' ' + t[len(t) - 5:len(t)]
                outfile.writelines(s + '\n')

    finally:
        outfile.close()