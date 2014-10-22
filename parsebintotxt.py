"""
A DAS binary file to text file parser
This program let you choose one or more binary file(s) and propose to parse and save it (them) as readable text file.

 """
import os
import parsedasbin
from tkinter import filedialog


def parse_bin_files_to_text_files(in_filename='', out_filename='', time_step=60, k_max=330000,
                                   date_as_secs_since_epoch=False, verbose_flag=False, sep=',', ext='.txt', site='0000',
                                   netid='255', data='', bpos='1', date_format='%Y/%m/%d %H:%M:%S'):
    dtm_format = False
    if in_filename == '':
        # if ask_files is true, asks for input and output files
        ask_files = True
    else:
        ask_files = False
        if out_filename == '':
            out_filename = os.path.splitext(os.path.abspath(in_filename))[0]
        else:
            out_filename = os.path.splitext(os.path.abspath(out_filename))[0]  # remove extension if stated

    if ext == '.dtm':
        date_as_secs_since_epoch = False
        sep = ' '
        dtm_format = True

    out_filename += ext

    if ask_files:
        home = os.path.expanduser('~')
        in_filename = filedialog.askopenfilename(filetypes=('binary {*.bin}', 'Binary files'),
                                                 initialdir = home, initialfile = '')
        out_filename = os.path.splitext(os.path.basename(in_filename))[0]
        if dtm_format:
            outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*.dtm}"),
                                               initialfile = out_filename + ext)
        else:
            outfile = filedialog.asksaveasfile(filetypes=("Text files", "text {*." + ext + "}"),
                                               initialfile = out_filename + ext)
    else:
        outfile = open(out_filename, 'wt')

    k_tot = round((os.stat(in_filename).st_size - 40)/12, 0)
    infile = open(in_filename,'rb')
    parsedasbin.parse_bin_to_ascii(infile, outfile, time_step, 0, k_tot, date_as_secs_since_epoch,
                                   verbose_flag, sep, ext, site, netid, data, bpos, date_format)
    infile.close()
    outfile.close()

if __name__ == '__main__':
    parse_bin_files_to_text_files()
