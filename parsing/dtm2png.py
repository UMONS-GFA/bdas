__author__ = 'su530201'
# plotting a dtm file to png


import datetime
import logging
import matplotlib.pyplot as plt
from dateutil import tz


def read_dtm(dtmfile, min_date=datetime.datetime.utcfromtimestamp(0), max_date=datetime.datetime.utcnow()):
    utc_tz = tz.gettz('UTC')
    previous_date = datetime.datetime.utcfromtimestamp(0)
    previous_date = previous_date.replace(tzinfo=utc_tz)
    infile = open(dtmfile, 'rt')
    data = infile.readlines()
    d, C, CC, n_channels = [], [], [], 4
    logging.info('Parsing data...')
    for l in data:
        if '#' not in l:
            current_date = datetime.datetime.strptime(l[:19], '%Y %m %d %H %M %S')
            current_date = current_date.replace(tzinfo=utc_tz)
            if current_date < previous_date:
                logging.warning('*** Records going back in time !')
            if (min_date <= current_date <= max_date):
                d.append(datetime.datetime.strptime(l[:19], '%Y %m %d %H %M %S'))
                C.append([float(l[20:33]), float(l[34:47]), float(l[48:61]), float(l[62:75])])
            previous_date = current_date

    logging.info('Rearranging data...')
    CC = [list(i) for i in zip(*C)]
    return d, CC


def plot_dtm(d, CC, pngfile):
    xlabel_font_size = 8
    ylabel_font_size = 10
    logging.info('Plotting data...')
    fig = plt.figure()
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.plot(d, CC[0], '-k', linewidth=2)
    for xlabel_i in ax1.get_xticklabels():
        xlabel_i.set_fontsize(xlabel_font_size)
    for ylabel_i in ax1.get_yticklabels():
        ylabel_i.set_fontsize(ylabel_font_size)
    ax2 = fig.add_subplot(4, 1, 2, sharex=ax1)
    ax2.plot(d, CC[1], '-b', linewidth=2)
    for xlabel_i in ax2.get_xticklabels():
        xlabel_i.set_fontsize(xlabel_font_size)
    for ylabel_i in ax2.get_yticklabels():
        ylabel_i.set_fontsize(ylabel_font_size)
    ax3 = fig.add_subplot(4, 1, 3, sharex=ax1)
    ax3.plot(d, CC[2], '-r', linewidth=2)
    for xlabel_i in ax3.get_xticklabels():
        xlabel_i.set_fontsize(xlabel_font_size)
    for ylabel_i in ax3.get_yticklabels():
        ylabel_i.set_fontsize(ylabel_font_size)
    ax4 = fig.add_subplot(4, 1, 4, sharex=ax1)
    ax4.plot(d, CC[3], '-g', linewidth=2)
    for xlabel_i in ax4.get_xticklabels():
        xlabel_i.set_fontsize(xlabel_font_size)
    for ylabel_i in ax4.get_yticklabels():
        ylabel_i.set_fontsize(ylabel_font_size)
    ax4.set_xlim(left=d[0], right=d[-1])
    ax4.set_xlabel('Time')
    plt.tight_layout()
    fig = plt.gcf()
    fig.set_size_inches(24, 8)
    plt.savefig(pngfile, dpi=100)
