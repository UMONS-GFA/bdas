"""
Example of usage of report job status function (connect, insert, update, close)
"""
__author__ = 'kaufmanno'


import logging
import reportjobstatus as rjs
import time
import sys


def main():
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler('testinsertstreamstatus.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')
    try:
        conn = rjs.connect_to_logDB()
        logging.info('_____ Connected _____')
    except:
        sys.exit(1)
    command = input('Command (=job set):')  # example FullDownloadDAST001
    status = 'Unknown'
    cur_time = time.gmtime()
    timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', cur_time)+"'"
    rjs_status, job_id = rjs.insert_job(conn, timestamp, command)
    print(rjs_status, job_id)

    while len(status) > 0:
        status = input('Enter status :')
        cur_time = time.gmtime()
        timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', cur_time)+"'"
        rjs.update_job_status(conn, job_id, timestamp, status)
    rjs.close_connection_to_logDB(conn)
    logging.info('_____ Ended _____')

if __name__ == '__main__':
    main()
