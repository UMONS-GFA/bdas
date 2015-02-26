__author__ = 'su530201'
""" plot a parsed downloaded DAS file...
"""
import numpy as np
import matplotlib.pyplot as plt
import datetime
from tkinter import filedialog
from tkinter import *


def schmitt_trigger(ts, low, high, threshold):
    filtered = []
    fd = []
    is_high = False
    is_low = False
    state = np.NaN
    for i in ts:
        d = 0
        if i < low:
            is_low = True
            state = 0
        elif i > high:
            is_high = True
            state = 1
        if is_low and i > threshold:
            is_low = False
            state = 1
            d = 1
        elif is_high and i < threshold:
            is_high = False
            state = 0
            d = 0
        filtered.append(state)
        fd.append(d)
    return filtered, fd

def moving_w_rate(ts, ws):
    rate = []
    hw = ws//2  # hw : half window
    for i in range(0, len(ts)):
        if i < hw | i > len(ts)-hw:
            rate.append(np.NaN)
        else:
            n_cycles = np.sum(ts[i-hw:i+hw])
            #t = 2*hw
            rate.append(n_cycles)
    return rate

root = Tk()
root.withdraw()  # this will hide the main window
def_dir = '/home/su530201/PycharmProjects/DownloadDAS/'
def_file = 'R013Full_20150103_0700'
filtering = False
#in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.bin'
#out_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.txt'
in_filename = filedialog.askopenfilename(filetypes=(('Dtm files', 'dtm {*.dtm}')), initialdir = def_dir,
                                         initialfile = def_file + '.dtm')
infile = open(in_filename, 'rt')
data = infile.readlines()
#data = data[7:]
d, C, CC, n_channels = [], [], [], 4
print('Parsing data...')
for l in data:
    if '#' not in l:
        d.append(datetime.datetime.strptime(l[:19], '%Y %m %d %H %M %S'))
        C.append([float(l[20:33]), float(l[34:47]), float(l[48:61]), float(l[62:75])])

print('Rearranging data...')
for i in range(len(C[0])):
    tmp = []
    for j in range(len(C)):
        tmp.append(C[j][i])
    CC.append(tmp)

if filtering:
    print('Filtering data...')
    CC[1], CC[2] = schmitt_trigger(CC[0], 30000, 45000, 37500)
    #CC[1], CC[2] = schmitt_trigger(CC[3], 4500, 5500, 5000)
    CC[3] = moving_w_rate(CC[2], 1440)
    CC[1] = np.cumsum(CC[2])

fig = plt.figure()
ax1 = fig.add_subplot(4, 1, 1)
ax1.plot(d, CC[0], '-k', linewidth=2)
ax2 = fig.add_subplot(4, 1, 2, sharex=ax1)
ax2.plot(d, CC[1], '-b', linewidth=2)
ax3 = fig.add_subplot(4, 1, 3, sharex=ax1)
ax3.plot(d, CC[2], '-r', linewidth=2)
ax4 = fig.add_subplot(4, 1, 4, sharex=ax1)
ax4.plot(d, CC[3], '-g', linewidth=2)
ax1.set_xlim(left=d[0], right=d[-1])
ax1.set_xlabel('Time')
plt.show()