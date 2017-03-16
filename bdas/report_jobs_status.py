__author__ = 'kaufmanno'
"""
A tool to report status of jobs (i.e. cron jobs) to a PostgreSQL database

 """

import psycopg2 as pg
import logging

from bdas.settings import LogDB, UserLogDB, URLLogDBHost, URLLogDBPort, UserLogPwd


def connect_to_logDB():
    conn = None
    try:
        conn = pg.connect(database=LogDB, user=UserLogDB, host=URLLogDBHost, port=URLLogDBPort, password=UserLogPwd)
        logging.info('Connected to ' + LogDB + ' on ' + URLLogDBHost + ':' + URLLogDBPort)
    except pg.DatabaseError as e:
        logging.error('*** ' + UserLogDB + ' cannot connect to the database ' + LogDB + ' on ' + URLLogDBHost + ':'
                      + URLLogDBPort + ': \n%s ' % e)
    finally:
        return conn


def insert_job(conn, timestamp, command, tags=()):
    status = None
    job_id = None
    cur = conn.cursor()
    try:
        sql = "INSERT INTO jobs(start_time, ref_command, ref_status) VALUES (%s," \
              "(SELECT id FROM commands WHERE name = %s),(SELECT code FROM status WHERE description = %s)) RETURNING id;" # Note: no quotes
        data = (timestamp, command, 'Unknown')
        cur.execute(sql, data)
        job_id = cur.fetchone()[0]
        conn.commit()
        logging.info('New job inserted in ' + LogDB)
        cur.close()
        status = True
        for tag in tags:
            logging.debug('Adding tag ' + tag)
            tag_status = add_tag(conn, job_id, tag)
            logging.debug('Tag status' + str(tag_status))
            #status = status and tag_status

    except pg.DatabaseError as e:
        logging.error('*** Error while inserting job status into jobs table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status, job_id


def add_tag(conn, job_id, tag_val=''):
    status = False
    cur = conn.cursor()
    if tag_val != '':
        tag, value = tag_val.split(':')
        logging.debug('tag : ' + tag + ' value : ' + value)
        if (tag is not None) and (tag != ''):
            try:
                sql = "INSERT INTO tags(job_id, tag, value) VALUES (%s,%s,%s)"
                data = (job_id, tag, value)
                cur.execute(sql, data)
                conn.commit()
                logging.info(tag + ' tag added with value ' + value + ' to job ' + job_id + ' in ' + LogDB)
                cur.close()
                status = True
            except pg.DatabaseError as e:
                logging.error('*** Error while adding tag ' + tag + ':' + value + ' to job ' + job_id + ' : \n%s' % e)
                conn.rollback()
                cur.close()
                status = False
            finally:
                return status
        else:
            logging.warning('*** Invalid tag, tag was not added.')
            return status
    else:
        logging.warning('*** Tag is empty.')
        return status


def update_job_status(conn, job_id, timestamp, job_status):
    status = False
    cur = conn.cursor()
    try:
        sql = "UPDATE jobs SET end_time = %s, ref_status = " \
              "(SELECT code FROM status WHERE description = %s) WHERE id = %s"  # Note: no quotes
        data = (timestamp, job_status, job_id)
        cur.execute(sql, data)
        conn.commit()
        logging.info('Status logged to ' + LogDB)
        cur.close()
        status = True
    except pg.DatabaseError as e:
        logging.error('*** Error while updating job status into jobs table : \n%s' % e)
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
        logging.error('*** Unable to close connection to ' + LogDB + ' :\n%s' % e)
        status = False
    finally:
        return status
