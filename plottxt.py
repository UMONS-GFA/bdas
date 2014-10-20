__author__ = 'su530201'
""" plot a parsed downloaded DAS file...
"""
import numpy as np
import pandas as pd
#import matplotlib.pyplot as Plt
import datetime
from tkinter import filedialog
from tkinter import *
#import csv

date_as_string = False
verbose_flag = False

root = Tk()
root.withdraw()  # this will hide the main window

def_dir = '/home/su530201/PycharmProjects/DownloadDAS/'
def_file = 'R012Full_20141012_0400'

in_filename = filedialog.askopenfilename(filetypes=('Text files', 'text {*.txt}'), initialdir = def_dir,
                                         initialfile = def_file + '.txt')

if date_as_string:
    data = pd.read_csv(in_filename, parse_dates=True, index_col=0, header=None)
else:
    data = pd.read_csv(in_filename, index_col=0, header=None)
    #d.append(datetime.datetime.utcfromtimestamp(int(row[0])))

print(data)
data.plot()
#ts = pd.DataFrame(data)
#ts.plot(subplots=True)
