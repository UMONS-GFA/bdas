__author__ = 'kaufmanno'

import logging
import time
import reportjobstatus as rjs

def main():
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S', level=logging_level,
                        handlers=[logging.FileHandler('testinsertstreamstatus.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')
    conn = rjs.connect_to_logDB()
    logging.info('_____ Connected _____')
    command = input('Command :')
    status = 'Unknown'
    cur_time = time.gmtime()
    timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', cur_time)+"'"
    rjs_status, job_id = rjs.insert_job(conn, timestamp, command, status)
    print(job_id)

    while len(status) > 0:
        cur_time = time.gmtime()
        timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', cur_time)+"'"
        rjs.update_job_status(conn, job_id, timestamp, status)
        status = input('Enter status :')
    rjs.close_connection_to_logDB(conn)
    logging.info('_____ Ended _____')

if __name__ == '__main__':
    main()


