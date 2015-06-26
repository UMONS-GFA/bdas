__author__ = 'Arno'

#from testplotdtm import schmitt_trigger,moving_w_rate
import sys
sys.path.append("c:/Python Scripts/uert")
from pygrav import read_pluvio_tsf
import filter_dtm
import datetime
import read_dtm
import read_cutecom_log
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import traceback
import glob
import scipy.signal

import os
# from obspy.core import Stream, Trace, read, AttribDict

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

def filter_pluvio(data,channel = 4,filter = 5000):
    # filtering = (df[0] > np.roll(df[0],-1)+filter)
    data = (data[data[channel] < np.roll(data[channel],-1)+filter])
    data = (data[data[channel] > np.roll(data[channel],-1)-filter])
    # for i in range(1,len(data)):
    #     filtering = (df[0] > np.roll(df[0],-1)+filter)
    #     if data[i] - data[i-1] > filter :
    #         data[i-1] = np.nan
    return data

def find_emptying(data, channel = 4, filter = 40, filter2 = 20):

    ### select cases when previous and next data are below present data
    ### in practice, works quite well when drip counter works fine... but hard when drip counter is troubleshooting
    # emptyidx= (data[channel] > np.roll(data[channel],-1)+filter1) & (data[channel] > np.roll(data[channel],2)+filter2) & (data[channel] > np.roll(data[channel],-2)+filter2)
    # fullidx= (-data[channel] > np.roll(-data[channel],-1)+filter1) & (-data[channel] > np.roll(-data[channel],2)+filter2) & (-data[channel] > np.roll(-data[channel],-2)+filter2)

    ### quite similar to previous case
    # emptyidx= (data[channel] > np.roll(data[channel],-5)+filter1) & (data[channel] > np.roll(data[channel],3)+filter2) & (data[channel] > np.roll(data[channel],-2)+filter2)
    # fullidx= (-data[channel] > np.roll(-data[channel],-5)+filter1) & (-data[channel] > np.roll(-data[channel],3)+filter2) & (-data[channel] > np.roll(-data[channel],-2)+filter2)

    ### using scipy signal peak finder, in theory is more efficient but in practice, parameters are hard to constraint
    # emptyidx = scipy.signal.find_peaks_cwt(data[channel],  np.arange(1,2), min_snr=0.1, noise_perc=0.5)
    # fullidx = scipy.signal.find_peaks_cwt(-data[channel],  np.arange(1,2), min_snr=0.1, noise_perc=0.5)
    #
    # emptyidx = [True if k in emptyidx_n else False for k in range(len(data[channel]))]
    # fullidx = [True if k in fullidx_n else False for k in range(len(data[channel]))]

    # emptyidx = scipy.signal.argrelextrema(data[channel], np.greater, mode = 'clip')
    # fullidx = scipy.signal.argrelextrema(data[channel], np.less, mode = 'clip')

    ### convolve data before filtering sometimes can help but quite useless most of the time
    # data[channel] = np.convolve(scipy.signal.hanning(11), data[channel], 'same')
    # emptyidx = scipy.signal.find_peaks_cwt(data[channel],  np.arange(1,2), noise_perc=0.1)
    # fullidx = scipy.signal.find_peaks_cwt(-data[channel],  np.arange(1,2), noise_perc=0.1)

    ### trying to keep only full if followed by empty and vice versa
    ### in practice, works quite well when drip counter works fine...
    # for i in range(len(fullidx_n)):
    #     if fullidx_n[i] < emptyidx_n[i]:
    #         pass
    #     elif not emptyidx_n[i] < fullidx_n[i] and not emptyidx_n[i+1] > fullidx_n[i] :
    #         pass
    # for i in range(len(emptyidx)):
    #     try:
    #         j = i
    #         while emptyidx[j] < fullidx[i] :
    #             j = j+1
    #         j = j
    #         idx = np.where(np.array(emptyidx)[i:j] < fullidx[i] )
    #         idx = idx[0] + i
    #         print(i,idx,j)
    #         # if np.array(fullidx[i:i+j]).count(True) > 1:
    #         if len(idx)>1 or len(idx) == 0:
    #             for k in idx:
    #                 fullidx[k]= np.nan
    #             emptyidx[i],emptyidx[j] = np.nan, np.nan
    #         i = j
    #     except : traceback.print_exc()
    # print(np.array(emptyidx),np.array(fullidx))


    ### most flexible case, especially when drip counter is not perfectly working
    ### BUT imperatively need post filtering as select to many cases (all ascending or descending data)
    emptyidx= (data[channel] > np.roll(data[channel],-1)+filter)
    fullidx= (-data[channel] > np.roll(-data[channel],-1)+filter)
    print(emptyidx)

    ### post filtering data to keep only first of an ascending/descending series
    i=0
    while not np.array(emptyidx)[i]:
        i+=1
    idx = np.where(np.array(fullidx)[:i])
    for k in idx:
        fullidx[k]= False
    for i in range(len(np.array(emptyidx))):
        try:
            if np.array(emptyidx)[i]:
                j = i+1
                while np.array(emptyidx)[j]:
                    emptyidx[j]=False
                    j = j+1

        except : traceback.print_exc()


    for i in range(len(np.array(fullidx))):
        try:
            if np.array(fullidx)[i]:
                j = i+1
                while np.array(fullidx)[j]:
                    fullidx[j] = False
                    j = j+1

        except : traceback.print_exc()


    for i in range(len(np.array(emptyidx))):
        try:
            if np.array(emptyidx)[i]:
                j = i+1
                while not np.array(emptyidx)[j]:
                    j = j+1
                # j = j-1
                idx = np.where(np.array(fullidx)[i:j])
                idx = idx[0] + i
                print(i,idx,j)
                # if np.array(fullidx[i:i+j]).count(True) > 1:
                if len(idx)>1:
                    for k in idx[1:]:
                        fullidx[k]= False
                if len(idx) == 0:
                    emptyidx[i] = False
                #
                elif idx[0]- i < 8 :
                     fullidx[idx[0]], emptyidx[i] =  False, False
                i = j-1
        except : traceback.print_exc()

    ### alternative method for filtering
    # for i in range(len(np.array(fullidx))):
    #     try:
    #         if np.array(fullidx)[i]:
    #             j = i+1
    #             while not np.array(fullidx)[j]:
    #                 j = j+1
    #             # j = j-1
    #             idx = np.where(np.array(emptyidx)[i:j])
    #             idx = idx[0] + i
    #             print(i,idx,j)
    #             # if np.array(fullidx[i:i+j]).count(True) > 1:
    #             if len(idx)>1:
    #                 for k in idx[1:]:
    #                     emptyidx[k]= False
    #             if len(idx) == 0:
    #                 fullidx[i] =  False
    #             elif j - idx[0] < 6:
    #                  fullidx[j], emptyidx[idx[0]] =  False, False
    #             i = j
    #     except : traceback.print_exc()

    return emptyidx,fullidx
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
def flow(date,emptyidx,fullidx,vol = 0.275):
    div = 3600
    volume = np.ones(len(np.where(np.array(emptyidx))[0]))*vol
    print(np.where(np.array(emptyidx)))
    date_empty = date[emptyidx]
    date_full = date[fullidx]
    print(date_empty,date_full)
    if date_full[0]< date_empty[0]:
        date_full = date_full.delete(0)
    print(len(date_full),len(date_empty),len(volume))
    for i in range(len(volume)):
        try:
            print((date_full[i]-date_empty[i]).seconds)

            volume[i] = vol/((date_full[i]-date_empty[i]).total_seconds()/div)
            print(volume[i])
        except: traceback.print_exc()
    print(volume)
    return volume, date_empty

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
    files = glob.glob(directory+'R013Full_20150528*.dtm')
    # files = glob.glob(directory+'*.dtm')
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
        data = filter_pluvio(data,filter = 1500)
        print('Filtering done')
        emptyidx,fullidx = find_emptying(data,filter = 9)

        # df = pd.DataFrame(np.array(channels[3]),index=datum)
        # print(df,df[0],df.columns)
        # peakidx= (df[0] > np.roll(df[0],1)+1) & (df[0] > np.roll(df[0],-1)+1)
        # peakidx = scipy.signal.find_peaks_cwt(df[0],  np.arange(1,2), min_snr=0.1, noise_perc=0.05)
        print(len(fullidx),len(emptyidx))
        # print(df[0])
        # plt.figure()
        # times = pd.date_range(data.index[0], data.index[-1], freq='5S' )
        plt.plot(data.index[emptyidx],data[4][emptyidx],'.',markersize=10)
        plt.plot(data.index[fullidx],data[4][fullidx],'.',markersize=10)
        plt.plot(data.index,data[4],'.-')
        # plt.plot(times,st2[0],'-')
        #st.plot()
        plt.show()
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


        vol = 0.275
        df = pd.DataFrame(np.ones(len(data.index[emptyidx]))*vol, index=data.index[emptyidx])
        volume,date_vol = flow(data.index,emptyidx,fullidx)
        df = pd.DataFrame(volume, index=date_vol)
        df = filter_pluvio(df,channel = 0 ,filter = 5 )
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
        # plt.show()

    # volume,date_vol = flow(data.index,emptyidx,fullidx)
    # print(date_vol,volume)
    # pluvio=True
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'))
    # if pluvio:
    #     PP_RCH ,DATE_PP_RCH = read_pluvio_tsf.data_pluvio_tsf('C:/Users\Arno\Documents\Pluvio\\',datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'),freq='hours')
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'),datetime.datetime.strftime(full_data.index[-1],'%d/%m/%Y'),DATE_PP_RCH,PP_RCH)
    full_data = full_data.sort_index()
    plt.plot(full_data.index,full_data[0],'-',markersize=10)
    full_data =full_data.resample('1H', how='mean')
    plt.plot(full_data.index,full_data[0],'-',markersize=10)
    # plt.plot(DATE_PP_RCH,PP_RCH,color='r', label = 'Precipitation')
    # plt.ylabel("volume (L)")
    plt.show()
    # print(datetime.datetime.strftime(full_data.index[0],'%d/%m/%Y'))
    full_data.to_csv(file[:-4]+'.flw',sep='\t',na_rep = "nan")