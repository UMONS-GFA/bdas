__author__ = 'Arno'
import bdas.draft.read_dtm as read_dtm
import datetime
import numpy as np
import glob
import pandas as pd
def filter_datum(data,date=None,max=4):
    data = data[data.index >= data.index[0]]
    data = data[data.index < datetime.datetime.now()]
    if date != None:
        data = data[data.index > date-datetime.timedelta(weeks=max)]
    return data

if __name__ == '__main__':
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\'
    files = glob.glob(directory+'R013Full_TOT_01202015.dtm')
    for file in files:
        datum,channels,das = read_dtm.read_dtm(file)
        datum,channels = filter_datum(datum,channels)
        read_dtm.plot_dtm(datum,channels,das)


