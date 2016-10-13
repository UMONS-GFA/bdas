__author__ = 'kaufmanno'

import time
import os.path
import sys

dl_expectedduration = 180
basepath = os.path.dirname(__file__)
outfile = ''
print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime())+'\nPartial Download command file creation...')
if len(sys.argv) == 3:
    dasnr = sys.argv[1]
    dasname = sys.argv[2]
    try:
        i = int(dasnr)
    except:
        print('Error argument should be a DAS number')
        exit()

    now = time.gmtime()
    oneweekago = time.gmtime(time.time()-7*24*60*60)

    try :
        outfile = os.path.abspath(os.path.join(basepath, '..', 'DownloadDAS', 'CommandFiles',
                                               'PartialDownloadDAS%s%03d.cmd' % (dasname, i)))
        cmdlines=['-%03d' % i, '#E0', '#RI', '#XP %04d %02d %02d %02d %02d %02d %04d %02d %02d %02d %02d %02d'
                  % (oneweekago.tm_year, oneweekago.tm_mon, oneweekago.tm_mday, oneweekago.tm_hour, oneweekago.tm_min,
                     oneweekago.tm_sec,now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec),
                  '%s%03doneweek' % (dasname, i), dl_expectedduration]

        with open(outfile, mode='wt', encoding='utf-8') as myfile:
            myfile.write('\n'.join(cmdlines))
        print('*** Command file updated ***')
    except:
        print('Error : unable to write file %s' % outfile)
else:
    print('Usage: createweekcmd dasnumber dasnameprefix\nExample : createweekcmd 2 "R"')

print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')