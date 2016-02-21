""" Inserts ERT raw data into an hdf5 structure if not already present
"""

import os
import glob
import datetime
from ReadErtData import read_mertpd_txt
import pandas as pd

__author__ = 'kaufmanno'


def collect_files(path, mask, r_contact=True):
    list_of_files = glob.glob(path+'/'+mask)
    cols = ['timestamp','filename']
    r_contact_files = []
    rho_files = []
    for i in list_of_files:
        if i[-14:]=='_contact_R.txt':
            mdate = datetime.datetime.strptime(i[-29:-14],'%Y%m%d_%H%M%S')
            #r_contact_files.append([mdate, os.path.split(i)[1]])
            if r_contact:
                r_contact_files.append([mdate, i])
        else:
            mdate = datetime.datetime.strptime(i[-19:-4],'%Y%m%d_%H%M%S')
            #rho_files.append([mdate, os.path.split(i)[1]])
            rho_files.append([mdate, i])
    df_rho = pd.DataFrame(rho_files, columns=cols)
    df_rho.sort_values(axis=0, by='timestamp', inplace=True)
    df_rho.set_index('timestamp')
    return df, metadata  #returns two dataframes : rho files and contact resistance files in path matching the mask


def insert_in_hdf5(path, mask, hdf5_file):
    df_rho, df_r_contact = collect_files(path, mask)
    hdf = pd.HDFStore(hdf5_file)
    for index, row in df_rho.iterrows():
        fn = os.path.split(row['filename'])[1]
        grp='RawData/Seq_'+fn.split('_')[0]+'/Measures'
        try:
            x = len(hdf.select(grp, 'filename == "'+fn+'"', columns = ['a']).index)
        except: # if RawERT table already exists but file not appended yet
            data = read_mertpd_txt.read_mertpd_txt(row['filename'])
            hdf.put(grp, data, format='table', append=True, data_columns=True)
            x = -1
        if x == 0:  # if RawERT table does not exist yet in hdf5
            data = read_mertpd_txt.read_mertpd_txt(row['filename'])
            hdf.put(grp, data, format='table', append=True, data_columns=True)
        elif x > 0: # Dataset already exist in hdf5
            print('Dataset ' + fn + ' already in hdf file')
    if r_contact:
        for index, row in df_r_contact.iterrows():
            fn = os.path.split(row['filename'])[1]
            grp = 'RawERT/Seq_'+fn.split('_')[0]+'/R_Contact'
            try:
                x = len(hdf.select(grp, 'filename == "'+fn+'"',columns=['a']).index)
            except:
                data = pd.read_csv(row['filename'], index_col=0, sep='\t', header=0)
                if not 'time' in data.columns:
                    data['time'] = datetime.datetime.strptime(row['filename'][-29:-15],'%Y%m%d_%H%M%S')
                hdf.put(grp, data, format='table', append=True, data_columns=True)
                x = -1
            if x == 0:
                data = pd.read_csv(row['filename'], index_col=0 , sep='\t', header=0)
                if not 'time' in data.columns:
                    data['time'] = datetime.datetime.strptime(row['filename'][-29:-15],'%Y%m%d_%H%M%S')
                hdf.put(grp, data, format='table', append=True, data_columns=True)
            elif x > 0:
                print('Dataset ' +fn+ ' already in hdf file')
    return hdf

if __name__ == '__main__':
    pass