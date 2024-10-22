import datetime
import json
import logging
import time
from os import path, rename

import pandas as pd
from parsing import parse_bin_to_txt as pdb
from bdas.settings import BIN_DIR, TEMP_FILE

__author__ = 'kaufmanno'


def get_metadata(filename):
    try:
        with open(filename +'.jsn') as bf:
            metadata = json.load(bf)
        return metadata
    except:
        logging.error('*** .jsn file is missing!')
        return None


def bin_to_df(bin_file):
    """
    Parse a bin file to a pandas dataframe
    @param bin_file : bin filename (with path)
    """

    # logging_level = logging.DEBUG
    # logging.Formatter.converter = time.gmtime
    # log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    # logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
    #                     handlers=[logging.FileHandler('testparsedasbin.log'), logging.StreamHandler()])
    # logging.info('_____ Started _____')
    metadata = get_metadata(bin_file)
    if metadata is None:
        logging.info('No metadata !')
        return None, None, 2
    else:
        logging.info('processing ' + bin_file)
        t_step = int(metadata['Integration'])
        tmp_file = path.join(BIN_DIR, TEMP_FILE)
        status = pdb.parse_bin_files_to_text_files(in_filename=bin_file, out_filename=tmp_file, verbose_flag=True,
                                                   dtm_header=True, sep=' ', time_step=t_step)
        parse = lambda x: datetime.datetime.strptime(x, '%Y %m %d %H %M %S')
        try:
            #df = pd.read_csv(tmp_file, sep=',', comment='#', parse_dates=[0], date_parser=parse)
            df = pd.read_csv(tmp_file, comment='#', sep=' ', parse_dates={'date': [0, 1, 2, 3, 4, 5]}, date_parser=parse,
                             header=None)
        except:
            logging.warning("Unable to read temp file ")
            return None, None, 2
        df.columns = ['date', metadata['Channels'][0], metadata['Channels'][1], metadata['Channels'][2],
                      metadata['Channels'][3]]
        df = df.set_index('date').tz_localize('UTC')
        metadata = get_metadata(bin_file)
        logging.info('______ Ended ______')
        return df, metadata, status

if __name__ == '__main__':
    bfile = ''  # insert bin filename here
    bdf, md, st = bin_to_df(bfile)
    print(bdf)
