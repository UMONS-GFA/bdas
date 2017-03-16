from parsing import parse_bin_to_txt as pdb

__author__ = 'bastinc'
"""
Parsing a bin file to dtm
"""
import time
import logging


def bin_to_dtm(bin_file, dtm_file, t_step=60):
    """
    Parse a bin file to dtm
    @param bin_file : bin_filename with path
    @param dtm_file : tm_filename with path
    @param t_step : integration period
    """
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler('testparsedasbin.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')

    status = []

    logging.info('processing ' + bin_file)
    status.append(pdb.parse_bin_files_to_text_files(in_filename=bin_file, out_filename=dtm_file, verbose_flag=True,
                                                    dtm_format=True, time_step=t_step))
    logging.info('______ Ended ______')
