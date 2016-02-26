__author__ = 'Arno'

from . import filter_dtm
import datetime
import statsmodels.api as sm
from . import read_dtm
from . import read_cutecom_log
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import traceback
import glob
from .freq2flow import filter_pluvio,find_emptying,flow,irregular_timeseries
import scipy.signal
import os

def post_filter_pluvio(data,channel = 0,filter = 2,roll=5):
    # filtering = (df[0] > np.roll(df[0],-1)+filter)
    data = (data[data[channel] < np.roll(data[channel],-roll)+filter])
    data = (data[data[channel] > np.roll(data[channel],-roll)-filter])
    # for i in range(1,len(data)):
    #     filtering = (df[0] > np.roll(df[0],-1)+filter)
    #     if data[i] - data[i-1] > filter :
    #         data[i-1] = np.nan
    return data
if __name__ == '__main__':
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\calibration\\'
    files = glob.glob(directory+'*.dtm')

    file= files[0]
    vols = [0.35,2.735]
    filters = [12,2000]
    pre_filters = [1500,15000]

    calib = pd.DataFrame(columns = ['id_pump','tank','mean','std'])

    for file in files:
        (head,filename)=os.path.split(file)
        print('FILE = '+filename)
        for i in range(len(vols)):
            print('Parsing data... '+file)
            try:
                datum,channels,das,data = read_dtm.read_dtm(file)
            except:
                datum,channels = read_cutecom_log.read_log(file)

            data = filter_dtm.filter_datum(data)
            print('Filtering data...')
            data = filter_pluvio(data,channel=i+1,filter = pre_filters[i])
            print('Filtering done')
            print('Finding emptyings...')
            # if i == 0:
            #     cycle, data[i+1] = sm.tsa.filters.hpfilter(data[i+1])
            #     print(data[i+1])
            # else:
            #     cycle, data[i+1] = sm.tsa.filters.hpfilter(data[i+1],1)
            emptyidx,fullidx = find_emptying(data,channel=i+1,filter = filters[i])

            plt.plot(data.index[emptyidx],data[i+1][emptyidx],'.',markersize=10)
            plt.plot(data.index[fullidx],data[i+1][fullidx],'.',markersize=10)
            plt.plot(data.index,data[i+1],'.-')
            # plt.show()
            print(data.index[emptyidx])
            # df = pd.DataFrame(np.ones(len(data.index[emptyidx]))*vols[i], index=data.index[emptyidx])
            volume,date_vol = flow(data.index,emptyidx,fullidx,vol = vols[i])
            # print(volume)
            df = pd.DataFrame(volume, index=date_vol)
            df = filter_pluvio(df,channel=0,filter = pre_filters[i]/100)
            full_data = df
            first = False

            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            full_data = full_data.sort_index()
            ax.plot(full_data.index,full_data[0],'-',markersize=10)
            full_data = full_data[full_data.index > full_data.index[int(len(full_data[0].values))/3]]
            # full_data.columns=['flow']
            # filt = full_data[0].max()-full_data[0].mean()+1/5
            filt = full_data[0].std()
            print(full_data[0].std()/2)
            if filt > 0.1 :
                full_data = post_filter_pluvio(full_data[full_data[0]>0.3],filter=full_data[0].std()/2.,roll=1)

            cycle, trend = sm.tsa.filters.hpfilter(full_data[0])
            full_data['trend'] = trend
            full_data['cycle'] = cycle

            # df = pd.date_range(full_data.index.min(),full_data.index.max(),freq='1H')
            # full_data = full_data.reindex(df, fill_value= np.nan)
            print(full_data)
            # full_data = full_data.resample('1H', how='mean')
            ax.plot(full_data.index,full_data['trend'],'-',markersize=10)
            ax.plot(full_data.index,full_data[0],'-',markersize=10)

            plt.show()
            # flow_rate = [np.mean(full_data[0].dropna().values[int(len(full_data[0].values))/10:-int(len(full_data[0].values))/10]),np.std(full_data[0].dropna().values[int(len(full_data[0].values))/40:-int(len(full_data[0].values))/10])]
            # flow_rate = [np.mean(full_data[0].dropna().values),np.std(full_data[0].dropna().values)]
            # flow_rate = [np.mean(full_data[0].dropna().values[1:-1]),np.std(full_data[0].dropna().values[1:-1])]
            flow_rate = [np.mean(full_data['trend'].values),np.std(full_data['trend'].values)]
            # print(full_data[0].values)
            if i == 0:
                print('SMALL TANK')

                df = pd.DataFrame([[int(filename[:2]),'small',flow_rate[0],flow_rate[1]]],columns = ['id_pump','tank','mean','std'])
            else :
                print('LARGE TANK')

                df = pd.DataFrame([[int(filename[:2]),'large',flow_rate[0],flow_rate[1]]],columns = ['id_pump','tank','mean','std'])
            print('Mean flow rate = '+str(flow_rate[0]))
            print('Flow rate Standard deviation = '+str(flow_rate[1]))
            calib = calib.append(df)
            print(calib)

    calib.to_csv(directory+'calib_hp_df3.txt',sep='\t')
    # full_data.to_csv(file[:-4]+'.flw',sep='\t',na_rep = "nan")