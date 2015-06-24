__author__ = 'su530201'

import os
import sys
import datetime
from dateutil import tz
from bin2dtm import bin_to_dtm
from dtm2png import read_dtm, plot_dtm


def main():
    status = 0
    utc_tz = tz.gettz('UTC')
    bin_filename = ''
    dtm_filename = ''
    png_filename = ''
    timestep = 60
    min_date = datetime.datetime.fromtimestamp(0)
    max_date = datetime.datetime.utcnow()
    i = 1
    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'binfile':
                    bin_filename = str(sys.argv[i+1])
                    # logging.info('   Host : ' + LocalHost)
                if sys.argv[i] == 'dtmfile':
                    dtm_filename = str(sys.argv[i+1])
                    # logging.info('   Host : ' + LocalHost)
                if sys.argv[i] == 'pngfile':
                    png_filename = str(sys.argv[i+1])
                    # logging.info('   Host : ' + LocalHost)
                if sys.argv[i] == 'timestep':
                    timestep = int(str(sys.argv[i+1]))
                    # logging.info('   Host : ' + LocalHost)
                if sys.argv[i] == 'mindate':
                    min_date = datetime.datetime.strptime(str(sys.argv[i+1]),'%d/%m/%Y %H:%M:%S')
                    min_date = min_date.replace(tzinfo=utc_tz)
                    # logging.info('   Host : ' + LocalHost)
                if sys.argv[i] == 'maxdate':
                    max_date = datetime.datetime.strptime(str(sys.argv[i+1]),'%d/%m/%Y %H:%M:%S')
                    max_date = max_date.replace(tzinfo=utc_tz)
                    # logging.info('   Host : ' + LocalHost)
                else:
                    # logging.info('   Unknown argument : ' + sys.argv[i])
                    pass
                i += 2
        else:
            #logging.info('Parsing failed : arguments should be given by pairs [key value], ignoring arguments...')
            status = -1
            pass
    else:
        #logging.info('No argument found...')
        status = -1

    if not(bin_filename == ''):
        if dtm_filename == '':
            dtm_filename = os.path.splitext(bin_filename)[0]+'.dtm'
        if png_filename == '':
            png_filename = os.path.splitext(bin_filename)[0]+'.png'

        bin_to_dtm(bin_filename, dtm_filename, timestep)
        d, CC = read_dtm(dtm_filename, min_date, max_date)
        plot_dtm(d, CC, png_filename)
    else:
        status = -1

    return status

if __name__ == '__main__':
    status=main()
    print(status)