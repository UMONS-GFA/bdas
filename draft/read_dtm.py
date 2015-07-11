__author__ = 'Arno'

import numpy as np
import datetime
import glob
import pandas as pd
import sys
import matplotlib.pyplot as plt
sys.path.append("c:/Python Scripts/uert")
from pygrav import read_pluvio_tsf

def read_dtm(file):                     #TODO: remove datum and channels when pandas dataframes are supported in other scripts
    with open(file,'r') as myfile:
        rows=[list(map(str,L.strip().split(' '))) for L in myfile]
    datum=[]
    channels=[[],[],[],[]]
    parse = lambda x: datetime.datetime.strptime(x, '%Y %m %d %H %M %S')
    data = pd.read_csv(file,sep= ' ',  parse_dates=[[0,1,2,3,4,5]],header=None, names=['Y','m','d','H','M','S','1','2','3','4'], comment='#',date_parser=parse)
    data.columns= ['date',1,2,3,4]
    data = data.set_index('date')

    for i in range(len(rows)):
        if rows[i][1][0:4]=='UDAS':
            das = int(rows[i][2])
        if rows[i][0].isdigit() :
            datum.append(datetime.datetime.strptime('%04i:%02i:%02i:%02i:%02i:%02i'%(float(rows[i][0]),float(rows[i][1]),float(rows[i][2]),float(rows[i][3]),float(rows[i][4]),float(rows[i][5])),'%Y:%m:%d:%H:%M:%S'))
            for j in range(4):
                try:
                    channels[j].append(float(rows[i][j+6]))
                except:
                    channels[j].append(None)
    return datum,channels,das,data          ## datum: list, channels: list of lists, das: integer, data: dataframe with datum as index and channels as columns


def plot_dtm(datum,channels,das,channel_to_plot = [1,2,3,4],fmt='-',colors=['blue']):         ## obsolete when using pandas dataframes
    import matplotlib.pyplot as plt
    f, axarr = plt.subplots(len(channel_to_plot), sharex=True)
    for i in channel_to_plot:
        if len(colors)==1:
            axarr[i-1].plot(datum,channels[i-1],'-',color=colors[0])
        else:
            axarr[i-1].plot(datum,channels[i-1],'-',color=colors[i-1])
    plt.show()


if __name__ == '__main__':
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\'
    directory = 'C:/Users\Arno\Documents\\'
    files = glob.glob(directory+'test.dtm')
    files = glob.glob(directory+'R013Full_20150710_0600.dtm')
    # files = glob.glob(directory+'2015*DTM')
    print(files)
    for file in files:
        datum,channels,das,data = read_dtm(file)
        # plot_dtm(datum,channels,das)

    #plot is easy when using dataframes

    # data = data.drop(pd.Timestamp('2015-04-13 17:40:45'))
    # data = data[data.index < data.index[111]]
    # print(data)
    df = data[[data.columns[0]]]
    df.plot(subplots=True)
    plt.show()
