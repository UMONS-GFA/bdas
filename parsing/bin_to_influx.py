import glob
import sys
import logging
import datetime
import pandas as pd
from os import path, makedirs, rename
from influxdb import DataFrameClient
from time import gmtime
from parsing import bin_to_df
from bdas.settings import DATABASE, BIN_DIR, PROCESSED_DIR, UNPROCESSED_DIR, LOG_DIR, LOG_FILE, MASK


def bin_to_influx(bin_filename, last_date):
    df, metadata, status = bin_to_df.bin_to_df(bin_filename)
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
    status = None
    log_path = path.join(BIN_DIR, LOG_DIR)
    if not path.exists(log_path):
        makedirs(log_path)
    processed_path = path.join(BIN_DIR, PROCESSED_DIR)
    if not path.exists(processed_path):
        makedirs(processed_path)
    logging_level = logging.DEBUG
    logging.Formatter.converter = gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(path.join(BIN_DIR, LOG_DIR, LOG_FILE)), logging.StreamHandler()])
    logging.info('_____ Started _____')

    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'MASK':
                    MASK = str(sys.argv[i+1])
                elif sys.argv[i] == 'binpath':
                    BIN_DIR = str(sys.argv[i+1])
                elif sys.argv[i] == 'dbname':
                    DATABASE['NAME'] = str(sys.argv[i+1])
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
        for f in bin_filenames:
            metadata = bin_to_df.get_metadata(f)
            if metadata is not None:
                if metadata['NetId'] is not None:
                    net_id = metadata['NetId']
                    first_channel = metadata['Channels'][0]
                    tag_to_search = net_id + '-' + first_channel
                    last_measurement = client.query('select last(*) from "measurement" where "sensor"= tag_to_search ;')
                    if not last_measurement:
                        ld = datetime.datetime(1970, 1, 1, 0, 0, 0).replace(tzinfo=datetime.timezone.utc)
                    else:
                        ld = last_measurement['measurement'].index.to_pydatetime()[0]
                    status = bin_to_influx(f, ld)
                    if status == 0 or status == 1:
                        rename(f, path.join(path.dirname(f), PROCESSED_DIR, path.basename(f)))
                        rename(f + '.jsn', path.join(path.dirname(f), PROCESSED_DIR, path.basename(f) + '.jsn'))
                    else:
                        logging.warning('%s could not be processed...' % f)
                        if not path.exists(path.join(BIN_DIR, UNPROCESSED_DIR)):
                            makedirs(path.join(BIN_DIR, UNPROCESSED_DIR))
                        rename(f, path.join(path.dirname(f), UNPROCESSED_DIR, path.basename(f)))
                        rename(f + '.jsn', path.join(path.dirname(f), UNPROCESSED_DIR, path.basename(f) + '.jsn'))
                else:
                    logging.warning('%s could not be processed because NetID is null' % f)
                    if not path.exists(path.join(BIN_DIR, UNPROCESSED_DIR)):
                        makedirs(path.join(BIN_DIR, UNPROCESSED_DIR))
                    rename(f, path.join(path.dirname(f), UNPROCESSED_DIR, path.basename(f)))
                    rename(f + '.jsn', path.join(path.dirname(f), UNPROCESSED_DIR, path.basename(f) + '.jsn'))

    else:
        status = 1
        logging.warning('No files to process...')

    logging.info('_____ Ended _____')
    sys.exit(status)
