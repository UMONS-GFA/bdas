__author__ = 'kaufmanno'
"""
A DAS binary file to text file parser
This program lets you parse one or more binary file(s) and save it (them) as readable text file.

 """
import logging
import os
import sys

from parsing import parse_das_bin


def parse_bin_files_to_text_files(in_filename='', out_filename='', time_step=60, k_max=330000,
                                  date_as_secs_since_epoch=False, verbose_flag=False, sep=',', dtm_header=False,
                                  site='0000', netid='255', data='', bpos='1', date_format='%Y/%m/%d %H:%M:%S',
                                  jumper=2):
    ext = '.dtm'
    if in_filename == '':
        # if ask_files is true, asks for input and output files
        logging.info('No files to parse')
        sys.exit(0)
    else:
        if out_filename == '':
            out_filename = os.path.splitext(os.path.abspath(in_filename))[0]
        else:
            ext = os.path.splitext(os.path.abspath(out_filename))[1]
            out_filename = os.path.splitext(os.path.abspath(out_filename))[0]  # remove extension if stated

    if ext == '.dtm':
        date_as_secs_since_epoch = False
        sep = ' '
        dtm_header = True

    out_filename += ext

    outfile = open(out_filename, 'wt')

    k_tot = round((os.stat(in_filename).st_size - 40)/12, 0)
    logging.info('expected data rows : %s', str(k_tot))
    infile = open(in_filename, 'rb')
    status = parse_das_bin.parse_bin_to_text(infile, outfile, time_step, 0, k_tot, date_as_secs_since_epoch,
                                             verbose_flag, sep, dtm_header, site, netid, data, bpos, date_format, jumper)
    infile.close()
    outfile.close()
    return status

if __name__ == '__main__':
    parse_bin_files_to_text_files('/home/su530201/PycharmProjects/DownloadDAS/T002Full_20150915_1022.bin', '/home/su530201/temp', verbose_flag=True)
