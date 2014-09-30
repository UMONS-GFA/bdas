__author__ = 'su530201'

"""
A DAS log to txt parser
This program let you choose a log file (i.e. from cutecom) and propose to parse and save it as a readable text file.

 """
import os
import time, datetime
from tkinter import filedialog
from tkinter import *

root = Tk()
root.withdraw()  # this will hide the main window

# if epoch is true converts to epoch otherwise to string date
epoch = True
# separator in text file
sep = ','


home = os.path.expanduser('~')
#initdir=home
#initfile=''
init_dir ='/home/su530201/PycharmProjects/bdas'
init_file = 'test_debit_2.log'
date_format = '%Y %m %d %H %M %S'

in_filename = filedialog.askopenfilename(filetypes=('DAS_log_file {*.log}', 'Log files'),
                                         initialdir = init_dir, initialfile = init_file)
out_filename = os.path.splitext(os.path.basename(in_filename))[0]
outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.txt}"), initialfile = out_filename + '.txt')

time_step = 60

try:
    infile = open(in_filename, 'rt')
    data = infile.readlines()
    #print(data)
    d, C, n_channels = [], [], 4  # TODO: generalize for variable channel count
    for l in data:
        if len(l) == 70:
            d.append(l[1:20])
            C.append([int(l[21:27]), int(l[33:39]), int(l[45:51]), int(l[57:63])])
            #if epoch:
            #    s = str(int(time.mktime(time.strptime(d[len(d)-1], date_format))))
            #else:
            #    s = datetime.datetime.strptime(d[len(d)-1],date_format)
            #        #s=s[2:len(s)] # if date format YY mm dd HH MM SS
            s = str(d[len(d)-1])
            for j in range(n_channels):
                t = format(C[len(C)-1][j], '05d')
                s += sep + t[len(t) - 5:len(t)]
            outfile.writelines(s + '\n')

finally:
    infile.close()
    outfile.close()