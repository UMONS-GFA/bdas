__author__ = 'Arno'
import read_dtm
import numpy as np
import glob
import pandas as pd
def filter_datum(data):
    data = data[data.index >= data.index[0]]
    return data

if __name__ == '__main__':
    directory = 'C:/Users\Arno\Documents\Compteur de gouttes\\'
    files = glob.glob(directory+'R013Full_TOT_01202015.dtm')
    for file in files:
        datum,channels,das = read_dtm.read_dtm(file)
        datum,channels = filter_datum(datum,channels)
        read_dtm.plot_dtm(datum,channels,das)


