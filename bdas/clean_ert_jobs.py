__author__ = 'kaufmanno'
"""
A tool to report status of jobs (i.e. cron jobs) to a PostgreSQL database

 """

import psycopg2 as pg
import logging

from uert.kauf_db_settings import LogDB, UserLogDB, URLLogDBHost, URLLogDBPort, UserLogPwd


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


def get_ERT_jobs(conn):
    status = None
    jobs_id = ()
    cur = conn.cursor()
    try:
        sql = "SELECT job_id FROM tags WHERE tag = 'TASK' AND value = 'ERT';" # Note: no quotes
        data = ()
        cur.execute(sql, data)
        jobs_id = cur.fetchall()
        conn.commit()
        cur.close()
        status = True

    except pg.DatabaseError as e:
        logging.error('*** Error while inserting job status into jobs table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status, jobs_id


def delete_tags(conn, job_list):
    status = None
    cur = conn.cursor()
    try:
        sql = "DELETE FROM tags WHERE job_id IN " + str(job_list) # Note: no quotes
        data = (job_list)
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        status = True

    except pg.DatabaseError as e:
        logging.error('*** Error while deleting jobs from tags table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status


def delete_jobs(conn, job_list):
    status = None
    cur = conn.cursor()
    try:
        sql = "DELETE FROM jobs WHERE id IN " + str(job_list) # Note: no quotes
        data = (job_list)
        cur.execute(sql, data)
        conn.commit()
        cur.close()
        status = True

    except pg.DatabaseError as e:
        logging.error('*** Error while deleting jobs from jobs table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status


def test_list(conn, job_list):
    status = None
    out = None
    cur = conn.cursor()
    try:
        sql = "SELECT * FROM jobs WHERE id IN " + str(job_list) # Note: no quotes
        data = (str(job_list))
        cur.execute(sql, data)
        out = cur.fetchall()
        conn.commit()
        cur.close()
        status = True

    except pg.DatabaseError as e:
        logging.error('*** Error while deleting jobs from jobs table : \n%s' % e)
        conn.rollback()
        cur.close()
        status = False
    finally:
        return status, out


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


if __name__ == '__main__':
    import numpy as np

    conn = connect_to_logDB()
    status, job_list = get_ERT_jobs(conn)
    job_list = tuple(np.array(job_list).flatten())
    print(job_list)
    #status, out = test_list(conn, job_list)
    #print(out)
    status = delete_tags(conn, job_list)
    status = delete_jobs(conn, job_list)
    close_connection_to_logDB(conn)