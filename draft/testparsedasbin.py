__author__ = 'su530201'
import os
import time
import logging
import parsebintotxt as pdb
from tkinter import filedialog, messagebox
from tkinter import Tk

# Parsing a list of bin files to dtm


def main():
    logging_level = logging.DEBUG
    logging.Formatter.converter = time.gmtime
    log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler('testparsedasbin.log'), logging.StreamHandler()])
    logging.info('_____ Started _____')

    t_step = 5 #60
    home = os.path.expanduser('~')
    start_dir = home
    status = []
    root = Tk()
    root.withdraw()  # this will hide the main window
    list_of_bin_files = filedialog.askopenfilenames(filetypes=('binary {*.bin}', 'Binary files'),
                                                    initialdir = start_dir, initialfile = '')

    for i in list_of_bin_files:
        logging.info('processing ' + i)
        status.append(pdb.parse_bin_files_to_text_files(in_filename=i, verbose_flag=True, dtm_format=True,
                                                        time_step = t_step))
        if status[-1] < 256:
            if status[-1] > 0:
                messagebox.showwarning('Warning', 'Parsing of ' + i + ' ended with warning code ' + str(status[-1])
                                       + '.')
        else:
            messagebox.showerror('Error', 'Parsing of ' + i + ' ended with error code '+ str(status[-1]) + '!')


    logging.info('______ Ended ______')


if __name__ == '__main__':
    main()
