Bdas settings
=============

.. settings:: DATABASES

``DATABASE``
------------

InfluxDB is used. This can be configured using the following::

    DATABASE = {
        'HOST': '127.0.0.1',
        'PORT': 8086,
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'NAME': 'mydatabase'
    }

``BIN_DIR``
-----------

Directory of the data which have to be treated::

    BIN_PATH = 'DownloadDAS/'

``PROCESSED_DIR``
-----------------

Directory where data treated are moved ::

    PROCESSED_DIR = 'processed/'

``LOG_DIR``
-----------

Log dir of the process::

    LOG_DIR = 'DownloadDAS/logs/'

``LOG_FILE``
------------

Log file of the process::

    LOG_FILE = 'bin_to_influx.log'

``MASK``
--------

The mask filters the data you want to process in the bin path::

    MASK = 'R*'


