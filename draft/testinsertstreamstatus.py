import insertjobstatus as ijs

__author__ = 'su530201'

import logging
import time


def main():
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S', level=logging_level,
                        handlers=[logging.FileHandler('testinsertstreamstatus.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')
    conn = ijs.connect_to_logDB()
    logging.info('_____ Connected _____')
    status = input('Enter status :')
    while len(status) > 0:
        cur_time = time.gmtime()
        timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', cur_time)+"'"
        #ijs.insert_stream_status(conn, timestamp, 'R014', status)
        status = input('Enter status :')
    ijs.close_connection_to_logDB(conn)
    logging.info('_____ Ended _____')

if __name__ == '__main__':
    main()


