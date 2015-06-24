__author__ = 'Arno'

import datetime
import traceback
import glob
import sys
sys.path.append("c:/Python Scripts/uert")
import read_dtm
import filter_dtm

def append_dtm(files):
    first = True
    for file in files:
        try:
            print('reading '+file)
            datum,channels,das,data = read_dtm.read_dtm(file)
            data = filter_dtm.filter_datum(data)
            if first:
                full_data = data
                first = False
            else:
                full_data = full_data.append(data)

        except:
            traceback.print_exc()
            print('error in '+file)
    full_data.columns= ['1','2','3','4']
    # full_data = full_data.drop_duplicates(full_data.index, take_last=True)
    full_data = full_data.groupby(full_data.index).first()
    full_data = full_data.sort_index()
    # grouped= full_data.groupby(level=0)
    # full_data = grouped.last()
    return full_data        ## return only a pandas dataframe

if __name__ == '__main__':
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\append\\'
    files = glob.glob(directory+'R013Full*.dtm')
    # files = [directory+'test.dtm',directory+'test.dtm']
    # files = [directory+'R013Full_20150412_0600.dtm',directory+'R013Full_20150424_0600.dtm']

    full_data = append_dtm(files)
    print(full_data)
    full_data.to_csv(directory+'full.txt',sep=' ',index=None)