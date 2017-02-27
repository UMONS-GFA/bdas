import glob
import os
import sys
import logging
import datetime
import pandas as pd
from influxdb import DataFrameClient
from time import gmtime
from parsing import bin2df
from bdas.settings import influx_host, influx_port, influx_user, influx_password

bin_path = '../DownloadDAS/'
processed_dir = '/processed/'
mask = 'R013*'
log_file = '../DownloadDAS/logs/bin_to_influx.log'
influx_dbname = ''

status = 0
utc_tz = datetime.timezone.utc



def bin_to_influx(bin_filename, last_date):
    df, metadata, status = bin2df.bin_to_df(bin_filename)
    if status == 0:
        df2 = df[df.index > last_date]
        if df2.size > 0:
            for col in df2.columns:
                df3 = pd.DataFrame({'date': df2[col].index, 'value': df2[col].values, 'sensor': col,
                                    'das': metadata['NetId']})
                df3.set_index('date', inplace=True)
                client.write_points(df3, 'measurement', {'sensor': metadata['NetId'] + '-' + col})
    return status

if __name__ == "__main__":
    i = 1
    if not os.path.exists(bin_path + '/logs/'):
        os.makedirs(bin_path + '/logs/')
    logging_level = logging.DEBUG
    logging.Formatter.converter = gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
    logging.info('_____ Started _____')

    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'mask':
                    mask = str(sys.argv[i+1])
                elif sys.argv[i] == 'binpath':
                    bin_path = str(sys.argv[i+1])
                elif sys.argv[i] == 'dbname':
                    influx_dbname = str(sys.argv[i+1])
                else:
                    logging.warning('*** Unknown argument : ' + sys.argv[i])
                    pass
                i += 2
        else:
            logging.error('*** Parsing failed : arguments should be given by pairs [key value]...')
            status = 2
            logging.info('_____ Ended _____')
            sys.exit(status)
    else:
        logging.warning('*** No argument found...')

    bin_filenames = sorted(glob.iglob(bin_path+mask+'.bin'))
    logging.info('%d bin files to process...' % len(bin_filenames))

    if len(bin_filenames) > 0:
        client = DataFrameClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
        if not os.path.exists(bin_path + processed_dir):
            processed_path = bin_path + processed_dir
            os.makedirs(processed_path)
        for f in bin_filenames:
            bin2df.get_metadata(f)
            last_measurement = client.query('select last(*) from "measurement";')
            if not last_measurement:
                ld = datetime.datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=datetime.timezone.utc)
            else:
                ld = last_measurement['measurement'].index.to_pydatetime()[0]
            status = bin_to_influx(f, ld)
            if status == 0 or status == 1:
                os.rename(f, os.path.dirname(f) + processed_dir + os.path.basename(f))
            else:
                logging.warning('%s could not be processed...' % f)

    else:
        status = 1
        logging.warning('No files to process...')

    logging.info('_____ Ended _____')
    sys.exit(status)
