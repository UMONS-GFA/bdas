__author__ = 'Arno'

#from testplotdtm import schmitt_trigger,moving_w_rate
#from pytsf import read_pluvio_tsf
import datetime
from bdas.draft import read_dtm, filter_dtm, read_cutecom_log
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import traceback
import glob
import scipy.signal

import os
# from obspy.core import Stream, Trace, read, AttribDict

def vidange(date,data,threshold=2000, delay = 55):
    date_vidange, data_vidange = [],[]
    incr = 0
    threshold_list=[threshold]
    for i in range(1,len(data)):
        if data[i]-data[i-1] > threshold_list[-1] and i - incr > delay:
            data_vidange.append(1)
            date_vidange.append(date[i])
            incr = i
            threshold_list.append(data[i-1]/7)
            # print(threshold_list)
        else:
            if len(threshold_list) < 10:
                set = len(threshold_list)
            else:
                set = 10
            stop = 0
            for j in reversed(threshold_list[-(set):]):
                if data[i]-data[i-1] > j and i - incr > delay and stop == 0:
                    data_vidange.append(1)
                    date_vidange.append(date[i])
                    incr = i
                    # print(j)
                    stop = 1

    return date_vidange,data_vidange

def flow(emptyidx,fullidx,vol = 0.275):
    date=[]
    volume = []
    div = 3600
    for i in range(len(fullidx)):
        try:
            volume.append(vol/((fullidx[i]-emptyidx[i]).total_seconds()/div))
            date.append(emptyidx[i]+(fullidx[i]-emptyidx[i])/2)
        except: traceback.print_exc()
    return volume, date

def filter_after_processing(date,data):

    peakidx = (data < np.roll(data,2)-2)
    peakidx = np.invert(peakidx, dtype=bool)
    data = np.array(data)[peakidx]
    date = np.array(date)[peakidx]
    peakidx2= (data > np.roll(data,2)+2)
    peakidx2 = np.invert(peakidx2, dtype=bool)
    data = np.array(data)[peakidx2]
    date = np.array(date)[peakidx2]
    return date,data

def irregular_timeseries(date,data,freq = 'minutes',normalize = 2.775):
    if freq == 'minutes':
        div = 60.
    if freq == 'hours':
        div = 3600.
    if freq == 'seconds':
        div = 1.
    if freq == 'seconds':
        div = 3600.*24.

    for i in range(1,len(date)-1):
        if (date[i]-date[i-1]).seconds > 2*(date[i-1]-date[i-2]).seconds and (date[i]-date[i-1]).seconds > 2*(date[i+1]-date[i]).seconds:
            data[i]=np.nan
        else :
            data[i] = data[i]*normalize/((date[i]-date[i-1]).total_seconds()/div)
    return date,data

def remove_bad_data(data):
    for i in range(len(data)-5):
        if data[i+3] - data[i] > 1000 and data[i-3] - data[i] > 1000 :
            data[i]=np.nan
    return data

def filter_pluvio(data,channel = 1,filter = 5000,roll = 2, check_max = None):
    data = data[((data[channel] < np.roll(data[channel],-roll)+filter) &  (data[channel] < np.roll(data[channel],roll)+filter))]
    data = data[((data[channel] > np.roll(data[channel],-roll)-filter) & (data[channel] > np.roll(data[channel],roll)-filter))]
    if check_max != None:
        data=data[data[channel] < check_max]
    return data

def find_large_emptying(data, channel = 1, filter = 100, roll=1):

    fullidx= data[data[channel] < np.roll(data[channel],-roll)-filter].index.tolist()
    emptyidx= data[data[channel] > np.roll(data[channel],roll)+filter].index.tolist()
    for i in range(len(np.array(fullidx))):

        try:
            if np.array(fullidx)[i]:
                j = i+1
                while np.array(fullidx)[j]:
                    fullidx[j] = False
                    j = j+1
        except : pass
    for i in range(len(np.array(emptyidx))):

        try:
            if np.array(emptyidx)[i]:
                j = i+1
                while np.array(emptyidx)[j]:
                    emptyidx[j] = False
                    j = j+1
        except : pass

    # for i in range(len(np.array(emptyidx))):
    #     try:
    #         if np.array(emptyidx)[i]:
    #             j = i+1
    #             while not np.array(emptyidx)[j]:
    #                 j = j+1
    #             # j = j-1
    #             idx = np.where(np.array(fullidx)[i:j])
    #             idx = idx[0] + i
    #             # print(i,idx,j)
    #             # if np.array(fullidx[i:i+j]).count(True) > 1:
    #             if len(idx)>1:
    #                 for k in idx[1:]:
    #                     fullidx[k]= False
    #             if len(idx) == 0:
    #                 emptyidx[i] = True
    #             #
    #             elif idx[0]- i < 8 :
    #                  fullidx[idx[0]], emptyidx[i] =  False, False
    #             i = j-1
    #     except : pass

    return emptyidx,fullidx

def find_old_emptying(data, channel = 1, filter = 100, low = 20000, roll=1):
    fullidx = (data[channel] < low)
    for i in range(len(np.array(fullidx))):
        try:
            if np.array(fullidx)[i]:
                j = i+1
                while np.array(fullidx)[j]:
                    fullidx[j] = False
                    j = j+1
        except : pass
    emptyidx=[]
    idx = np.where(fullidx)[0]

    for k in range(len(idx)-1):
        if data[channel].loc[data.index[idx[k]]:data.index[idx[k+1]]].max() > filter*20 :
            maxi = data[channel].loc[data.index[idx[k]]:data.index[idx[k+1]]].idxmax()
            emptyidx.append(maxi)
        else:
            fullidx[idx[k+1]] = False
    fullidx = data[fullidx].index.tolist()
    fullidx = fullidx[1:]
    # fullidx = fullidx[fullidx==True].index.tolist()
    # try:
    #     if fullidx[0]<emptyidx[0]:
    #         fullidx = fullidx[1:]
    # except:
    #     pass
    # fullidx=[]
    # for k in range(len(emptyidx)-1):
    #     mini = data[channel].loc[emptyidx[k]:emptyidx[k+1]].idxmin()
    #     fullidx.append(mini)

    # emptyidx= (data[channel] > np.roll(data[channel],-roll)+filter)
    # for i in range(len(np.array(emptyidx))):
    #
    #     try:
    #         if np.array(emptyidx)[i]:
    #             j = i+1
    #             while np.array(emptyidx)[j]:
    #                 emptyidx[j] = False
    #                 j = j+1
    #     except : pass
    #
    # fullidx=[]
    # idx = np.where(emptyidx)[0]
    # print(idx)
    # for k in range(len(emptyidx)-1):
    #     mini = data[channel].loc[emptyidx[k]:emptyidx[k+1]].idxmin()
    #     fullidx.append(mini)
    #
    # for k in range(len(idx)-1):
    #     maxi = data[channel].loc[data.index[idx[k]]:data.index[idx[k+1]]].idxmax()
    #     emptyidx.append(maxi)


    return emptyidx,fullidx
def find_emptying(data, channel = 1, filter = 100, roll=1, check_bad_fullidx = False):

    fullidx= (data[channel] < np.roll(data[channel],-roll)-filter)
    # idx = np.where(fullidx)[0]
    # for i in range(len(idx)-1):
    #     j = idx[i]+1
    #     while (np.array(fullidx)[j]) or (j < len(idx)):
    #         print(j)
    #         fullidx[j] = False
    #         j+=1
    #         i+=1
    #     i+=1
    for i in range(len(np.array(fullidx))):
        try:
            if np.array(fullidx)[i]:
                j = i+1
                while np.array(fullidx)[j]:
                    fullidx[j] = False
                    j = j+1
                i=j
        except : pass
    if check_bad_fullidx :
        idx = np.where(fullidx)[0]
        for i in range(len(idx)-1):
            try:
                # med = data[channel].loc[data.index[idx[i]:idx[i+1]]].median()
                # if med < (data[channel].loc[data.index[idx[i+1]]]+filter/20) :
                    tmp = ((data[channel].loc[data.index[idx[i]:idx[i+1]]] < np.roll(data[channel].loc[data.index[idx[i]:idx[i+1]]],-200)+10) & (data[channel].loc[data.index[idx[i]:idx[i+1]]] > np.roll(data[channel].loc[data.index[idx[i]:idx[i+1]]],-200)-10))
                    tmp_idx = np.where(tmp)[0]
                    if tmp_idx != []:
                        fullidx[idx[i+1]] = False
                        #fullidx[(data[channel].loc[data.index[idx[i]+20:idx[i+1]-20]].idxmin())]=True
                        fullidx[idx[i]+tmp_idx[0]] = True
                    # j = idx[i]+20
                    # fullidx[idx[i+1]] = False
                    # #while data[channel].loc[data.index[j]] > (data[channel].loc[data.index[idx[i+1]]] + filter/20):
                    # while data[channel].loc[data.index[j]] > (data[channel].loc[data.index[idx[i+1]-100:idx[i+1]-10]].min()):
                    #     # print(data[channel].loc[data.index[j]],(data[channel].loc[data.index[idx[i+1]]] + filter/10))
                    #     j = j+1
                    #     pass
                    # fullidx[j] = True
            except:
                traceback.print_exc()
                pass


    # for i in reversed(range(len(np.array(fullidx)))):
    #         if np.array(fullidx)[i]:
    #
    #             print('ij',i,j)
    #             j = i
    #             print('ijb',data[channel].loc[data.index[j]],data[channel].loc[data.index[i]])
    #             fullidx[j] = False
    #             while (not np.array(fullidx)[j]) and  (data[channel].loc[data.index[j]] < (data[channel].loc[data.index[i]] + filter/10)) :
    #                 fullidx[j] = False
    #                 j = j-1
    #             fullidx[j] = True
    #             i=j

    emptyidx=[]
    idx = np.where(fullidx)[0]

    for k in range(len(idx)-1):
        maxi = data[channel].loc[data.index[idx[k]]:data.index[idx[k+1]]].idxmax()
        emptyidx.append(maxi)
    if check_bad_fullidx:
        fullidx = fullidx[fullidx==True].index.tolist()
        fullidx = fullidx[1:]
    else :
        fullidx=[]
        for k in range(len(emptyidx)-1):
            mini = data[channel].loc[emptyidx[k]:emptyidx[k+1]].idxmin()
            fullidx.append(mini)

    # emptyidx= (data[channel] > np.roll(data[channel],-roll)+filter)
    # for i in range(len(np.array(emptyidx))):
    #
    #     try:
    #         if np.array(emptyidx)[i]:
    #             j = i+1
    #             while np.array(emptyidx)[j]:
    #                 emptyidx[j] = False
    #                 j = j+1
    #     except : pass
    #
    # fullidx=[]
    # idx = np.where(emptyidx)[0]
    # print(idx)
    # for k in range(len(emptyidx)-1):
    #     mini = data[channel].loc[emptyidx[k]:emptyidx[k+1]].idxmin()
    #     fullidx.append(mini)
    #
    # for k in range(len(idx)-1):
    #     maxi = data[channel].loc[data.index[idx[k]]:data.index[idx[k+1]]].idxmax()
    #     emptyidx.append(maxi)


    return emptyidx,fullidx

if __name__ == '__main__':
    pluvio = False
    # root = Tk()
    # root.withdraw()  # this will hide the main window
    # def_dir = '/home/su530201/PycharmProjects/DownloadDAS/'
    # def_file = 'R013Full_20150412_0600'
    # #in_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.bin'
    # #out_filename = '/home/su530201/PycharmProjects/DownloadDAS/R002Full_20140603_1827.txt'
    # in_filename = filedialog.askopenfilename(filetypes=([('Dtm files', 'dtm {*.dtm}'),('Log files','log {*.log}')]), initialdir = def_dir,
    #                                          initialfile = def_file + '.dtm')
    d, C, CC, n_channels = [], [], [], 4
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\append\\'
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\'
    # directory = 'C:/Users\Arno\Documents\Compteur de gouttes\calibration\\'
    files = glob.glob(directory+'R013Full_2015*.dtm')
    # files = glob.glob(directory+'05_T001Full_20151006_1537.dtm')
    # files = glob.glob(directory+'10_T001Full_20151007_0719.dtm')
    # files = glob.glob(directory+'15_T001Full_20151008_0901.dtm')
    # directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\'
    # files = glob.glob(directory+'test.dtm')
    first = True

    for file in files:
        print('Parsing data... '+file)
        try:
            datum,channels,das,data = read_dtm.read_dtm(file)
        except:
            datum,channels = read_cutecom_log.read_log(file)

        # datum,channels = filter_dtm.filter_datum(datum,channels)
        # print(data)
        data = filter_dtm.filter_datum(data)
        # print(datum[-1],channels[2][-1])
        print('Filtering data...')

        # channels[0] = filter_pluvio(channels[0])
        #channels[2] = filter_pluvio(channels[2],filter = 5000)
        # channels[3] = filter_pluvio(channels[3])
        data = filter_pluvio(data,channel=1,filter = 15000)
        print('Filtering done')
        emptyidx,fullidx = find_emptying(data,channel=1,filter = 3000)

        # df = pd.DataFrame(np.array(channels[3]),index=datum)
        # print(df,df[0],df.columns)
        # peakidx= (df[0] > np.roll(df[0],1)+1) & (df[0] > np.roll(df[0],-1)+1)
        # peakidx = scipy.signal.find_peaks_cwt(df[0],  np.arange(1,2), min_snr=0.1, noise_perc=0.05)
        print(len(fullidx),len(emptyidx))
        # print(df[0])
        # plt.figure()
        # times = pd.date_range(data.index[0], data.index[-1], freq='5S' )
        plt.plot(data.index[emptyidx],data[1][emptyidx],'.',markersize=10)
        plt.plot(data.index[fullidx],data[1][fullidx],'.',markersize=10)
        plt.plot(data.index,data[1],'.-')
        # plt.plot(times,st2[0],'-')
        #st.plot()
        # plt.show()
        # # print('kkkkk',df.index[peakidx],'lll',df[0][peakidx])
        # date,data1 = irregular_timeseries(data.index[peakidx],np.ones(len(data.index[peakidx])),freq='hours',normalize=0.275)
        # # plt.plot(date,data,'-',markersize=10)
        # plt.ylabel("volume (L)")
        #
        # date,data1= filter_after_processing(date,data1)
        # # plt.plot(np.array(date)[np.roll(peakidx2,-2)],np.array(data)[np.roll(peakidx2,-2)],'.',markersize=10)
        # plt.plot(date,data1,'-',markersize=10)
        # plt.ylabel("volume (L)")
        # plt.show()


        vol = 0.35 # test_lab
        vol = 3.0 # test_lab
        vol = 2.775 # val d'enfer
        df = pd.DataFrame(np.ones(len(data.index[emptyidx]))*vol, index=data.index[emptyidx])
        volume,date_vol = flow(data.index,emptyidx,fullidx,vol=vol)
        df = pd.DataFrame(volume, index=date_vol)
        # df = filter_pluvio(df,channel = 2 ,filter = 1 )
        # df = pd.DataFrame(np.ones(len(peakidx))*vol, index=times[peakidx])
        # st[0][peakidx].plot(kind='scatter')
        # df = df.resample('1H', how='sum')
        # full_data = append_data(df)
        if first :
            full_data = df
            first = False
        else:
            # print(full_data,df)
            full_data = full_data.append(df)
            # full_data = full_data.drop_duplicates(cols=full_data.index, take_last=True)
            full_data = full_data.groupby(full_data.index).first()

        # print(df.index)
        # df.plot(kind='bar')
        # plt.plot(df.index,df[0],'-',markersize=10)
        # plt.ylabel("volume (L)")
        plt.show()

    # volume,date_vol = flow(data.index,emptyidx,fullidx)
    # print(date_vol,volume)
    # pluvio=True
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'))
    if pluvio:
        PP_RCH ,DATE_PP_RCH = read_pluvio_tsf.data_pluvio_tsf('C:/Users\Arno\Documents\Pluvio\\',datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'),freq='hours')
        fig = plt.figure()
        ax = fig.add_subplot(2,1,1)
    else:
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'),DATE_PP_RCH,PP_RCH)
    full_data = full_data.sort_index()
    ax.plot(full_data.index,full_data[0],'-',markersize=10)
    full_data =full_data.resample('1H', how='mean')
    ax.plot(full_data.index,full_data[0],'-',markersize=10)
    if pluvio :
        ax2 = fig.add_subplot(2,1,2)
        ax2.plot(DATE_PP_RCH,PP_RCH,color='r', label = 'Precipitation')
    # plt.ylabel("volume (L)")
    plt.show()
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'))
    full_data.to_csv(file[:-4]+'big.flw',sep='\t',na_rep = "nan")