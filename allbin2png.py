__author__ = 'kaufmanno'

import datetime
import glob
import logging
import os
import sys
from time import gmtime

#from dateutil import tz

from parsing.bin2dtm import bin_to_dtm
from parsing.dtm2png import read_dtm, plot_dtm


status = 0
bin_path = './'
dtm_path = './'
png_path = './'
mask = '*'
#utc_tz = tz.gettz('UTC')
utc_tz = datetime.timezone.utc
bin_filename = ''
dtm_filename = ''
png_filename = ''
time_step = 60
min_date = datetime.datetime.fromtimestamp(0)
max_date = datetime.datetime.utcnow()
last_rec = 0

logging_level = logging.DEBUG
logging.Formatter.converter = gmtime
log_format = '%(asctime)-15s %(levelname)s:%(message)s'
logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler('./logs/allbin2png.log'), logging.StreamHandler()])
logging.info('_____ Started _____')

i = 1
if len(sys.argv) > 1:
    if len(sys.argv) % 2 == 1:
        while i < len(sys.argv)-1:
            if sys.argv[i] == 'mask':
                mask = str(sys.argv[i+1])
            elif sys.argv[i] == 'binpath':
                bin_path = str(sys.argv[i+1])
            elif sys.argv[i] == 'dtmpath':
                dtm_path = str(sys.argv[i+1])
            elif sys.argv[i] == 'pngpath':
                png_path = str(sys.argv[i+1])
            elif sys.argv[i] == 'timestep':
                time_step = int(str(sys.argv[i+1]))
            elif sys.argv[i] == 'mindate':
                min_date = datetime.datetime.strptime(str(sys.argv[i+1]), '%d/%m/%Y %H:%M:%S')
                min_date = min_date.replace(tzinfo=utc_tz)
            elif sys.argv[i] == 'maxdate':
                max_date = datetime.datetime.strptime(str(sys.argv[i+1]), '%d/%m/%Y %H:%M:%S')
                max_date = max_date.replace(tzinfo=utc_tz)
            #elif sys.argv[i] == 'lastrec':
            #    last_rec = int(str(sys.argv[i+1]))  # backwards time in seconds from the ending of dataset to start
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

bin_files = sorted(glob.iglob(bin_path+mask+'.bin'))
bin_files = [os.path.splitext(os.path.basename(i))[0] for i in bin_files]
png_files = sorted(glob.iglob(png_path+mask+'.png'))
png_files = [os.path.splitext(os.path.basename(i))[0] for i in png_files]
png_todo = list(set(bin_files)-set(png_files))
logging.info('%d images to create...' % len(png_todo))

if len(png_todo) > 0:
    for f in png_todo:
        bin_filename = bin_path+os.path.splitext(f)[0]+'.bin'
        dtm_filename = dtm_path+os.path.splitext(f)[0]+'.dtm'
        png_filename = png_path+os.path.splitext(f)[0]+'.png'

        bin_to_dtm(bin_filename, dtm_filename, time_step)
        d = []
        CC = []
        if last_rec == 0:
            d, CC = read_dtm(dtm_filename, min_date, max_date)
        else:
            d, CC = read_dtm(dtm_filename)
            print(max(d))
        if len(d) > 0:
            plot_dtm(d, CC, png_filename)
        else:
            logging.warning('*** Plot skipped %s' % bin_filename)
else:
    status = 1
logging.info('_____ Ended _____')
sys.exit(status)