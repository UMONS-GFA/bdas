__author__ = 'su530201'
""" plot a parsed downloaded DAS file...
"""
import numpy as np
import matplotlib.pyplot as plt
import datetime
from tkinter import filedialog
from tkinter import *

root = Tk()
root.withdraw() #this will hide the main window

def_dir = '/home/su530201/PycharmProjects/DownloadDAS/'
def_file = 'R002Full_20140603_1827'
#in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.bin'
#out_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.txt'
in_filename = filedialog.askopenfilename(filetypes=(('Text files', 'text {*.txt}')), initialdir = def_dir, initialfile = def_file +'.txt')


#in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.txt'
infile = open(in_filename,'rt')
data = infile.readlines()
d=[]
C=[]
CC=[]
nchannels = 4
for l in data :
#    d.append(datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i' % (int(l[:4]), int(l[5:7]), int(l[8:10]), int(l[11:13]), int(l[14:16]), int(l[17:19])), '%Y:%d:%m:%H:%M:%S'))
    d.append(datetime.datetime.strptime(l[:19], '%Y %m %d %H %M %S'))
    C.append([int(l[20:25]), int(l[26:31]), int(l[33:37]), int(l[38:43])])

for i in range(len(C[0])):
    tmp = []
    for j in range(len(C)):
        tmp.append(C[j][i])
    CC.append(tmp)

fig = plt.figure()
ax1 = fig.add_subplot(4, 1 ,1)
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


