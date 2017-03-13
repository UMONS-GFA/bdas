import glob
import sys
import logging
import datetime
import pandas as pd
from os import path, makedirs, rename
from influxdb import DataFrameClient
from time import gmtime
from parsing import bin2df
from bdas.settings import DATABASE, BIN_DIR, PROCESSED_DIR, LOG_DIR, LOG_FILE, MASK


def bin_to_influx(bin_filename, last_date):
    df = bin2df.bin_to_df(bin_filename)
    if df:
        df2 = df[df.index > last_date]
        if df2.size > 0:
            for col in df2.columns:
                df3 = pd.DataFrame({'date': df2[col].index, 'value': df2[col].values, 'sensor': col,
                                    'das': metadata['NetId']})
                df3.set_index('date', inplace=True)
                client.write_points(df3, 'measurement', {'sensor': metadata['NetId'] + '-' + col})
        return 0
    else:
        return 1

if __name__ == "__main__":
    i = 1
    status = None
    log_path = path.join(BIN_DIR, 'logs')
    processed_path = path.join(BIN_DIR, 'processed')
    if not path.exists(log_path):
        makedirs(log_path)
    logging_level = logging.DEBUG
    logging.Formatter.converter = gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(path.join(LOG_DIR, LOG_FILE)), logging.StreamHandler()])
    logging.info('_____ Started _____')

    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'MASK':
                    MASK = str(sys.argv[i+1])
                elif sys.argv[i] == 'binpath':
                    BIN_DIR = str(sys.argv[i+1])
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

    bin_filenames = sorted(glob.iglob(BIN_DIR+MASK+'.bin'))
    logging.info('%d bin files to process...' % len(bin_filenames))

    if len(bin_filenames) > 0:
        client = DataFrameClient(DATABASE['HOST'], DATABASE['PORT'], DATABASE['USER'],
                                 DATABASE['PASSWORD'], DATABASE['NAME'])
        if not processed_path:
            makedirs(processed_path)
        for f in bin_filenames:
            metadata = bin2df.get_metadata(f)
            if metadata is not None:
                net_id = metadata['NetId']
                last_measurement = client.query('select last(*) from "measurement" where "das"='+ net_id +';')
                if not last_measurement:
                    ld = datetime.datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=datetime.timezone.utc)
                else:
                    ld = last_measurement['measurement'].index.to_pydatetime()[0]
                check = bin_to_influx(f, ld)
                if check == 0:
                    rename(f, path.dirname(f) + PROCESSED_DIR + path.basename(f))
                else:
                    logging.warning('%s could not be processed...' % f)
    else:
        logging.warning('No files to process...')

    logging.info('_____ Ended _____')
    sys.exit(status)
