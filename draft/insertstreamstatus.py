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


def insert_stream_status(conn, timestamp, stream_name, cmd_status):
    status = False
    cur = conn.cursor()
    try:
        SQL = "INSERT INTO download_status(timestamp, stream, status) VALUES (%s,%s,%s);" # Note: no quotes
        data = (timestamp, stream_name, cmd_status)
        cur.execute(SQL, data)
        conn.commit()
        logging.info('Status logged to ' + LogDB)
        cur.close()
        status = True
    except pg.DatabaseError as e:
        logging.error('Unable to insert status into download_status table : \n%s' % e)
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