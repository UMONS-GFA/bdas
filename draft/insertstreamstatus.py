__author__ = 'su530201'

import psycopg2 as pg
#import time
import logging

from settings import LogDB, UserLogDB, URLLogDBHost, URLLogDBPort, UserLogPwd


def connect_to_logDB():
    conn = None
    try:
        conn = pg.connect(database=LogDB, user=UserLogDB, host=URLLogDBHost, port=URLLogDBPort, password=UserLogPwd)
        logging.info('Connected to ' + LogDB + ' on ' + URLLogDBHost + ':' + URLLogDBPort)
    except pg.DatabaseError as e:
        logging.error(UserLogDB + ' cannot connect to the database ' + LogDB + ' on ' + URLLogDBHost + ':'
                      + URLLogDBPort + ': \n%s ' % e)
    finally:
        return conn


def insert_job(conn, timestamp, stream_name):
    status = False
    job_id = None
    cur = conn.cursor()
    try:
        sql = "INSERT INTO downloads(start_time, ref_stream, ref_status) VALUES (%s," \
              "(SELECT id FROM streams WHERE name = %s),(SELECT code FROM status WHERE description = %s));"  # Note: no quotes
        data = (timestamp, stream_name, 'Unknown')
        cur.execute(sql, data)
        conn.commit()
        logging.info('New job inserted in ' + LogDB)
        # job_id = cur.fetchone()[0]
        cur.execute('SELECT LASTVAL()')
        job_id = cur.fetchone()['lastval']
        cur.close()
        status = True
    except pg.DatabaseError as e:
        logging.error('Error while inserting job status into downloads table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status, job_id


def update_job_status(conn, job_id, timestamp, cmd_status):
    status = False
    cur = conn.cursor()
    try:
        sql = "UPDATE downloads SET end_time = %s, ref_status = " \
              "(SELECT code FROM status WHERE description = %s) WHERE id = %s"  # Note: no quotes
        data = (timestamp, cmd_status, job_id)
        cur.execute(sql, data)
        conn.commit()
        logging.info('Status logged to ' + LogDB)
        cur.close()
        status = True
    except pg.DatabaseError as e:
        logging.error('Error while updating job status into download_status table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status


def close_connection_to_logDB(conn):
    status = False
    try:
        conn.close()
        status = True
    except pg.DatabaseError as e:
        logging.error('Unable to close connection to ' + LogDB + ' :\n%s' % e)
        status = False
    finally:
        return status