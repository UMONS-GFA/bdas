# -*- coding: utf-8 -*-
__author__ = 'Arno'

import numpy as np
import datetime
import glob
import sys
import pandas as pd


def read_log(file,comment='#'):
    with open(file,'r') as myfile:
        rows=[list(map(str,L.strip().split(' '))) for L in myfile]
    datum=[]
    channels=[[],[],[],[]]
    for i in range(0,len(rows),2):
        if rows[i][0][0] == '*' :
            datum.append(datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i'%(float(rows[i][0][1:]),float(rows[i][1]),float(rows[i][2]),float(rows[i][3]),float(rows[i][4]),float(rows[i][5])),'%Y:%m:%d:%H:%M:%S'))
            for j in range(4):
                try:
                    channels[j].append(float(rows[i][j+6]))
                except:
                    channels[j].append(None)
    # parse = lambda x: datetime.datetime.strptime(x, '%Y %m %d %H %M %S')
    # data = pd.read_csv(file,sep= ' ',   parse_dates=[[0,1,2,3,4,5]],header=None, names=['Y','m','d','H','M','S','1','2','3','4'], comment=comment, skip_blank_lines=True ,date_parser=parse, engine="python",)
    # data.columns= ['date',1,2,3,4]
    # data = data.set_index('date')
    data = pd.DataFrame(np.array(channels).T)
    data.index = datum
    return data

def plot_dtm(datum,channels,channel_to_plot = [1,2,3,4],fmt='-',colors=['blue']):
    import matplotlib.pyplot as plt
    f, axarr = plt.subplots(len(channel_to_plot), sharex=True)
    for i in channel_to_plot:
        if len(colors)==1:
            axarr[i-1].plot(datum,channels[i-1],'.',color=colors[0])
        else:
            axarr[i-1].plot(datum,channels[i-1],'-',color=colors[i-1])
    plt.show()

if __name__ == '__main__':
    file = '/home/arnaud/calibration/2015-02-2.log'
    data = read_log(file,comment="!")
    #channel_to_plot = [3]
    #import matplotlib.pyplot as plt
    #f, axarr = plt.subplots(len(channel_to_plot), sharex=True)
    # for file in files:
    #     datum,channels= read_log(file)

    #     print(file)
    #     plot_dtm(datum,channels)


    #    for i in channel_to_plot:
    #       axarr.plot(datum,channels[i-1],'-')
    #plt.show()