"""
DAS txt to SQLite3 converter
This program reads a txt file and appends a SQLite3 database.

 """
__author__ = 'su530201'

import sqlite3
import datetime


def db_create(database_name='new.db'):
    conn = sqlite3.connect(database_name)

    c = conn.cursor()

    # Create table
    c.execute('''create table raw_recordings(download_session INTEGER, das TEXT, date TIMESTAMP, channel_1 REAL,
                 channel_2 REAL, channel_3 REAL, channel_4 REAL)''')

    conn.commit()
    c.close()


def db_update(database_name='new.db', in_filename=r'../DownloadDAS/R002Full_20140603_1827.txt'):
    conn = sqlite3.connect(database_name)

    c = conn.cursor()

    # Insert rows
    infile = open(in_filename, 'rt')
    data = infile.readlines()
    d = []

    for l in data:
        d.append([1, '002', datetime.datetime.strptime(l[:19], '%Y %m %d %H %M %S'), int(l[20:25]), int(l[26:31]), int(l[33:37]),
                  int(l[38:43])])

    print(d)
    for t in d:
        c.execute('insert into raw_recordings values (?,?,?,?,?,?,?)', t)

    # Save (commit) the changes
    conn.commit()

    # We can also close the cursor if we are done with it
    c.close()