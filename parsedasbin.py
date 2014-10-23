"""
A binary to txt parser
This program let you choose a binary file and propose to parse and save it as a readable text file.

 """
import datetime
import logging
import math


def round_sig_digits(x, sig_digits=2):
    if float(x) == 0.0:
        return 0.0
    else:
        return round(x, sig_digits-int(math.floor(math.log10(abs(x))))-1)


def parse_bin_to_text(in_stream, out_stream, time_step=60, k_max=330000, k_tot=0, date_as_secs_since_epoch=False,
                      verbose_flag=False, sep=',', dtm_format=False, site='0000', netid='255', data='', bpos='1',
                      date_format='%Y/%m/%d %H:%M:%S', jumper=2):
    # in_stream : bin stream to convert
    # out_stream : text stream to create
    # if date_as_secs_since_epoch is true, converts to epoch otherwise to string date
    # if verbose_flag is true, prints messages while processing
    # sep is the separator in the output text file
    # ext is the out_stream extension (choose .dtm for compatibility with edas44 format for mgr)
    # jumper is the DAS multiplier jumper (x2 by default)

    status = 0
    cur_time = 0
    #status values (binary notation :)
    # 0 : no errors, no warnings
    # first byte : warnings
    # 1   2   4   8   16   32   64   128
    # 1 : Incorrect number of leading 0xFD
    # 2 : Extra 0x00 after leading 0xFD
    # 4 : Unexpected end of file
    # 8 : Doubled 0xFF 0xFF flag activated
    # second byte : errors
    # 256 : 3 consecutive 0xFF in date block
    # 512 : Unexpected values for the 2 bytes following 0xFD
    # 1024 : Unexpected values for the bytes following the date in date block
    # 2048 : Date block missing in sector [0]

    # if double_ff_flag is true, reads two successive ff as one single ff...
    double_ff_flag = False

    if k_max > 0:
        # if check_length is true, the process will end after kmax
        check_length_flag = True
    elif k_tot > 0:
        k_max = k_tot
        check_length_flag = True
    k = 1

    # reading begin message
    b = in_stream.read(1)
    i = 0
    while b == b'\xfd':
        i += 1
        b = in_stream.read(1)

    if (i % 3 == 0) & (i > 0):
        n_channels = int(i/3)
        if verbose_flag:
            logging.info('Number of channels :' + str(n_channels))
        eot = False
    else:
        n_channels = int(round(i/3, 0))
        logging.warning('*** Unexpected number of leading 0xFD!:' + str(i) + '. Assuming ' + str(n_channels)
                        + ' channels!')
        status += 1
        eot = False

    # looking for extra 00
    if b == b'\x00':
        #in_stream.seek(1, 1)
        b = in_stream.read(1)
        logging.warning('*** Extra 0x00 after leading 0xFD!')
        status += 2

    if dtm_format:
        ## writing header
        s = '# SITE: ' + site
        out_stream.writelines(s + '\n')
        s = '# UDAS: ' + netid
        out_stream.writelines(s + '\n')
        s = '# CHAN: YYYY MO DD HH MI SS'
        for i in range(n_channels):
            s = s + ' ' + format(i + 1, '04d')
        out_stream.writelines(s + '\n')
        s = '# DATA:' + data
        out_stream.writelines(s + '\n')
        s = '# BPOS: ' + bpos
        out_stream.writelines(s + '\n')

    # reading date block FF FF
    #in_stream.seek(-1, 1)
    b += in_stream.read(1)
    if b == b'\xff\xff':
        date_block = True
    elif b == b'\x70\x61':
        #in_stream.seek(-2, 1)
        b += in_stream.read(45)
        if b == b'pas de bloc date en debut de secteur numero [0]':
            logging.error('*** Date block missing in sector [0]!')
            status += 2048
            return status
        else:
            logging.error('*** Unexpected values for the 2 bytes following 0xFD!:' + repr(b))
            status += 512
            return status

    else:
        logging.error('*** Unexpected values for the 2 bytes following 0xFD!:' + repr(b))
        #date_block = False
        status += 512
        return status

    # reading D1 D2 D3 D4
    b = in_stream.read(4)
    while date_block:
        while b[0].to_bytes(1, 'big') == b'\xff':
            if b[1].to_bytes(1, 'big') == b'\xff':
                if not double_ff_flag:
                    double_ff_flag = True
                    logging.warning('*** Doubled 0xFF flag activated.')
                    status += 8
                b = b[2:4] + in_stream.read(2)

            else:
                logging.error('*** Unexpected format, 3 consecutive 0xFF in date block !')
                status += 256
                return status
        secs_since_epoch = int.from_bytes(b, byteorder='big')
        cur_time = datetime.datetime.utcfromtimestamp(secs_since_epoch)
        if verbose_flag:
            logging.info('Starting date:' + cur_time.strftime('%d/%m/%Y %H:%M:%S'))
        if dtm_format:
            s = '# INFO: interruption ' + cur_time.strftime('%Y %m %d %H %M %S') + '\n'
            out_stream.writelines(s)

        # reading optional 00 00 00
        for i in range(3, n_channels + 1):
            b = in_stream.read(3)
            if b != b'\x00\x00\x00':
                logging.error('*** Unexpected values for the bytes following the date in date block!' + repr(b))
                status += 1024
                return status
        b = in_stream.read(2)
        if b == b'\xff\xff':
            date_block = True
            b = in_stream.read(4)
        else:
            date_block = False

    # reading channels form in_stream and writing to out_stream
    if not eot:
        try:
            #in_stream.seek(-2, 1)
            start_reading_data = True
            while not eot:
                channel = []
                eot = True
                logged_event = False
                for j in range(n_channels):
                    if start_reading_data:
                        sb = b + in_stream.read(1)
                        start_reading_data = False
                    else:
                        sb = in_stream.read(3)
                    if len(sb) < 3:
                        if verbose_flag:
                            logging.warning('*** Unexpected end of file!')
                        if dtm_format:
                            s = '# INFO: End Of File\n'
                            out_stream.writelines(s)
                        status += 4
                        return status
                    if sb[0] == 0xff:
                        if double_ff_flag:
                            b = in_stream.read(1)
                            sb = sb[0:1] + sb[2:3] + b
                            if verbose_flag:
                                logging.info('Info : removing repeated 0xFF')
                    if sb[1] == 0xff:
                        if double_ff_flag:
                            b = in_stream.read(1)
                            sb = sb[0:1] + sb[2:3] + b
                            if verbose_flag:
                                logging.info('Info : removing repeated 0xFF')
                    if sb[2] == 0xff:
                        if double_ff_flag:
                            b = in_stream.read(1)
                            sb = sb[0:2] + b  # TODO : Check this...
                            if verbose_flag:
                                logging.info('Info : removing repeated 0xFF')

                    # logged event ?
                    if (sb[0] == 0xff) and (sb[1] == 0xff):
                        logged_event = True
                        l = 0
                        #in_stream.seek(-1, 1)
                        b = sb[2].to_bytes(1, 'big')
                        sb = b''
                        while l < 10:
                            if (b == b'\xff') and double_ff_flag:
                                b = in_stream.read(1)
                            sb += b
                            l += 1
                            if l < 10:
                                b = in_stream.read(1)
                        event_time = datetime.datetime.utcfromtimestamp(int.from_bytes(sb[0:4], 'big'))
                        secs_since_epoch = int.from_bytes(sb[0:4], 'big')
                        if verbose_flag:
                            logging.info(event_time.strftime('%Y/%m/%d %H:%M:%S') + ' Interruption')
                        if dtm_format:
                            s = '# INFO: interruption ' + event_time.strftime('%Y %m %d %H %M %S') + '\n'
                            out_stream.writelines(s)
                        else:
                            if date_as_secs_since_epoch:
                                s = 'not implemented yet'  # TODO : implement this condition...
                            else:
                                s = event_time.strftime(date_format)
                            s += ' : Interruption'
                            out_stream.writelines(s + '\n')
                        eot = False
                        break
                    else:
                        channel.append(int.from_bytes(sb, byteorder='big'))
                        if channel[j] != 0xfefefe:
                            eot = False

                if not logged_event:
                    cur_time = datetime.datetime.utcfromtimestamp(secs_since_epoch)

                    if verbose_flag and k_tot > 0:
                        if k/1024-round(k/1024) == 0:
                            print(repr(round(100*k/k_tot, 1)) + ' % done', end='\r')
                        # print(cur_time.strftime('%Y/%m/%d %H:%M:%S'), map(hex, channel[0:n_channels]))
                    if date_as_secs_since_epoch:
                        s = str(secs_since_epoch)
                    else:
                        if dtm_format:
                            s = cur_time.strftime('%Y %m %d %H %M %S')
                        else:
                            s = cur_time.strftime(date_format)
                    if not eot:
                        for j in range(n_channels):
                            if dtm_format:
                                t = format(round_sig_digits(float(channel[j])/time_step*jumper, 7), '013.4f')
                                u = 13
                            else:
                                t = format(round_sig_digits(float(channel[j])/time_step*jumper, 7), '05d')
                                u = 5
                            s += sep + t[len(t) - u:len(t)]
                        out_stream.writelines(s + '\n')
                    if (k > k_max) and check_length_flag:
                        if verbose_flag:
                            logging.warning('Too much rows...')
                        eot = True
                    secs_since_epoch += time_step
                    k += 1
            if dtm_format:
                s = '# INFO: End Of File\n'
                out_stream.writelines(s)

        finally:
            if verbose_flag:
                if cur_time != 0:
                    logging.info('Ending date:' + cur_time.strftime('%d/%m/%Y %H:%M:%S'))
                    logging.debug('k : ' + str(k))
            logging.info('Ending bin parsing.')
            return status