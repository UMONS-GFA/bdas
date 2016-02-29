import pandas as pd
from bdas.parsing import parsebintotxt as pdb
import datetime
import time
import logging
import json

__author__ = 'kaufmanno'
"""
Parsing a bin file to a pandas dataframe
"""


#def parse(x):
#    print(x)
#    return datetime.datetime.strptime(x, '%Y %m %d %H %M %S')


def bin_to_df(bin_file):
    """
    Parse a bin file to dtm
    @param bin_file : bin filename (with path)
    @param t_step : integration period
    """
    tmp_file = './temp'
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler('testparsedasbin.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')

    status = []
    logging.info('processing ' + bin_file + '.jsn')
    try:
        with open(bin_file+'.jsn') as jsn_file:
            metadata = json.load(jsn_file)
    except:
        logging.error('*** .jsn file is missing!')
        exit(1)
    logging.info('processing ' + bin_file)
    t_step = int(metadata['Integration'])
    status.append(pdb.parse_bin_files_to_text_files(in_filename=bin_file, out_filename=tmp_file, verbose_flag=True,
                                                    dtm_format=True, time_step=t_step))
    parse = lambda x: datetime.datetime.strptime(x, '%Y %m %d %H %M %S')
    df = pd.read_csv(tmp_file, sep=',', comment='#', parse_dates=[0], date_parser=parse)
    df.columns = ['date', metadata['Channels'][0], metadata['Channels'][1], metadata['Channels'][2], metadata['Channels'][3]]
    df = df.set_index('date')
    with open(bin_file+'.jsn') as bin_file:
        metadata = json.load(bin_file)
    logging.info('______ Ended ______')
    return df, metadata, status


if __name__ == '__main__':
    bfile = ''  # insert bin filename here
    bdf, md, st = bin_to_df(bfile)
    print(bdf)
