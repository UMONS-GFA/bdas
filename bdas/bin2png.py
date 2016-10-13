__author__ = 'kaufmanno'

import datetime
import os
import sys

from parsing.bin2dtm import bin_to_dtm
from dateutil import tz
from parsing.dtm2png import read_dtm, plot_dtm

__author__ = 'kaufmanno'

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
                if sys.argv[i] == 'dtmfile':
                    dtm_filename = str(sys.argv[i+1])
                if sys.argv[i] == 'pngfile':
                    png_filename = str(sys.argv[i+1])
                if sys.argv[i] == 'timestep':
                    timestep = int(str(sys.argv[i+1]))
                if sys.argv[i] == 'mindate':
                    min_date = datetime.datetime.strptime(str(sys.argv[i+1]), '%d/%m/%Y %H:%M:%S')
                    min_date = min_date.replace(tzinfo=utc_tz)
                if sys.argv[i] == 'maxdate':
                    max_date = datetime.datetime.strptime(str(sys.argv[i+1]), '%d/%m/%Y %H:%M:%S')
                    max_date = max_date.replace(tzinfo=utc_tz)
                else:
                    pass
                i += 2
        else:
            status = -1
            sys.exit(status)
    else:
        status = -1
        sys.exit(status)

    if not(bin_filename == ''):
        if dtm_filename == '':
            dtm_filename = os.path.splitext(bin_filename)[0]+'.dtm'
        if png_filename == '':
            png_filename = os.path.splitext(bin_filename)[0]+'.png'

        bin_to_dtm(bin_filename, dtm_filename, timestep)
        d, channels = read_dtm(dtm_filename, min_date, max_date)
        plot_dtm(d, channels, png_filename)
    else:
        status = -1
        sys.exit(status)
    sys.exit(status)


if __name__ == '__main__':
    main()