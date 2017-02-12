from os import path, mkdir, statvfs
import io
import sys
import serial
import time
import datetime
import logging
import binascii
import queue
import gzip
import socket

from struct import unpack_from
from threading import Thread, Lock

version = 0.28
debug = False

LocalHost = '0.0.0.0'
LocalPort = 10001
master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
master_connection = None
master_online = False
slave_device = '/dev/ttyACM0'
slave = None
n_channels = 4
calibration = []
calibration_file = ''
status = True
base_path = path.dirname(__file__)
if not path.isdir('logs'):
    mkdir('logs')
if not path.isdir('raw'):
    mkdir('raw')
file_name = 'raw/raw'
data_file = path.join(base_path, file_name + datetime.datetime.utcnow().strftime('_%Y%m%d_%H%M%S') + '.dat.gz')
log_file = path.join(base_path, 'logs/RaspArDAS.log')
chunk_size = 4096
if debug:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO
logging.Formatter.converter = time.gmtime
log_format = '%(asctime)-15s | %(process)d | %(levelname)s:%(message)s'
logging_to_console = False
if logging_to_console:
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(log_file), logging.StreamHandler()])
else:
    logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                        handlers=[logging.FileHandler(log_file)])
slave_queue = queue.Queue()  # what comes from ArDAS
master_queue = queue.Queue()  # what comes from Master (e.g. cron task running client2.py)
data_queue = queue.Queue()  # what should be written on disk
raw_data = False  # uses calibration
peer_download = False  # TODO: find a way to set peer_download to True if another RaspArDAS is downloading at startup
downloading = False
stop = False


def listen_slave():
    """This is a listener thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, downloading, slave_io, data_queue, n_channels, debug, slave_queue, master_queue, raw_data

    while not stop:
        # Read incoming data from slave (ArDAS)
        try:
            byte = b''
            msg = b''
            while byte != b'\r' and byte != b'$':
                byte = slave_io.read(1)
                msg += byte
            if byte == b'$':
                record = byte
                record += slave_io.read(32)
                crc = slave_io.read(4)
                record_crc = int.from_bytes(crc, 'big')
                msg_crc = binascii.crc32(record)
                if debug:
                    logging.debug('record : %s' % str(record))
                    logging.debug('record_crc : %d' % record_crc)
                    logging.debug('msg_crc : %d' % msg_crc)
                if msg_crc == record_crc:
                    crc_check = True
                else:
                    crc_check = False
                if crc_check:
                    instr = []
                    freq = []
                    station = int.from_bytes(record[1:3], 'big')
                    integration_period = int.from_bytes(record[3:5], 'big')
                    record_date = datetime.datetime.utcfromtimestamp(int.from_bytes(record[5:9], 'big'))
                    for i in range(n_channels):
                        instr.append(int.from_bytes(record[9+2*i:11+2*i], 'big'))
                        freq.append(unpack_from('>f', record[17+4*i:21+4*i])[0])
                    decoded_record = '%04d ' % station + record_date.strftime('%Y %m %d %H %M %S') \
                                     + ' %04d' % integration_period

                    if raw_data:
                        decoded_record += ' R'
                    else:
                        decoded_record += ' C'
                        val = [0.]*n_channels
                    for i in range(n_channels):
                        if raw_data:
                            decoded_record += ' %04d %11.4f' % (instr[i], freq[i])
                        else:
                            val[i]=calibration[i]['coefs'][0] + calibration[i]['coefs'][1]*freq[i] \
                                   + calibration[i]['coefs'][2]*freq[i]**2 + calibration[i]['coefs'][3]*freq[i]**3 \
                                   + calibration[i]['coefs'][4]*freq[i]**4
                            decoded_record += ' %04d %11.4f' % (instr[i], val[i])

                    decoded_record += '\n'
                    if master_connection and not raw_data:
                        cal_record = '%04d ' % station + record_date.strftime('%Y %m %d %H %M %S')
                        for i in range(n_channels):
                            s = '| %04d: %' + calibration[i]['format'] + ' %s '
                            cal_record += s % (instr[i], val[i], calibration[i]['unit'])
                        cal_record += '|\n'
                        slave_queue.put(cal_record.encode('utf-8'))
                    if debug:
                        logging.debug('Storing : ' + decoded_record)
                    # Send data to data_queue
                    data_queue.put(decoded_record.encode('utf-8'))
                else:
                    logging.warning('*** Bad crc : corrupted data is not stored !')

            else:
                if len(msg) > 0:
                    # Sort data to store on SD from data to repeat to master
                    try:
                        logging.debug('Slave says : ' + msg.decode('ascii'))
                    except:
                        logging.warning('*** listen_slave thread - Unable to decode slave message...')
                    if not downloading:
                        slave_queue.put(msg)
        except queue.Full:
            logging.warning('*** Data or slave queue is full!')
        except serial.SerialTimeoutException:
            pass
    logging.debug('Closing listen_slave thread...')


def talk_slave():
    """This is a talker thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, slave_io, master_queue

    while not stop:
        try:
            msg = master_queue.get(timeout=0.25)
            try:
                logging.debug('Saying to slave : ' + msg.decode('ascii'))
            except:
                logging.warning('*** talk_slave thread - Unable to decode master message...')
            slave_io.write(msg)
            slave_io.flush()
        except queue.Empty:
            pass
        except serial.SerialTimeoutException:
            logging.error('Could not talk to slave...')

    logging.debug('Closing talk_slave thread...')


def connect_master():
    """This is a connection listener thread function.
    It waits for a connection from the master.
    This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, master_connection, master_socket, master_online

    while not stop:
        try:
            if not master_online:
                logging.info('Waiting for master...')
                master_connection, addr = master_socket.accept()
                logging.info('Master connected, addr: ' + str(addr))
                master_online = True
        except:
            logging.error('Master connection error!')

    if master_online:
        msg = b'\n*** Ending connection ***\n\n'
        master_connection.send(msg)
    master_connection.close()
    logging.debug('Closing connect_master thread...')


def listen_master():
    """This is a listener thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, master_connection, master_queue, master_online, raw_data

    while not stop:
        if master_online:
            try:
                byte = b''
                msg = b''
                while byte != b'\r':
                    byte = master_connection.recv(1)
                    msg += byte
                if msg[0:1] == b'\n':
                    msg = msg[1:]
                if len(msg) > 0:
                    try:
                        logging.debug('Master says : ' + msg.decode('ascii'))
                    except:
                        logging.warning('*** listen_master thread - Unable to decode master message...')
                    if msg[:-1] == b'#XB':
                        logging.info('Full download request')
                        full_download()
                    elif msg[:-1] == b'#XP':
                        logging.info('Partial download request')
                    elif msg[:-1] == b'#XS':
                        logging.info('Aborting download request')
                    elif msg[:-1] == b'#ZF':
                        logging.info('Reset request')
                    elif msg[:-1] == b'#CF':
                        logging.info('Change file request')
                        save_file()
                    elif msg[:-1] == b'#RC':
                        raw_data = not raw_data
                        if raw_data:
                            logging.info('Switching to raw data.')
                        else:
                            logging.info('Switching to calibrated data.')
                    elif msg[:-1] == b'#KL':
                        logging.info('Stop request')
                        stop = True
                    else:
                        master_queue.put(msg)
            except queue.Full:
                logging.error('Master queue is full!')
            except:
                logging.warning('Master connection lost...')
                master_online = False
    logging.debug('Closing listen_master thread...')


def talk_master():
    """This is a talker thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, downloading, master_connection, slave_queue, master_online

    while not stop:
        if master_online:
            try:
                if not downloading:
                    msg = slave_queue.get(timeout=0.25)
                    try:
                        logging.debug('Saying to master :' + msg.decode('utf-8'))
                        master_connection.send(msg)
                    except:
                        logging.warning('*** talk_master thread - Unable to decode slave message...')
                        master_connection.send(msg)

            except queue.Empty:
                pass
            except:
                logging.warning('Master connection lost...')
                master_online = False
    logging.debug('Closing talk_master thread...')


def write_disk():
    """This is a writer thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, sd_file_io, data_queue, sd_file_lock

    offset = sd_file_io.tell()
    while not stop:
        try:
            msg = data_queue.get(timeout=0.1)
            logging.debug('Data queue length : %d' % data_queue.qsize())
            if len(msg) > 0:
                logging.debug('Writing to disk :' + msg.decode('ascii'))
                sd_file_lock.acquire()
                sd_file_io.seek(offset)
                sd_file_io.write(msg)
                sd_file_io.flush()
                offset = sd_file_io.tell()
                sd_file_lock.release()
        except queue.Empty:
            pass
    sd_file_io.flush()
    logging.debug('Closing write_disk thread...')


def full_download():
    """This is a full_download function.
    """
    # NOTE : This doesn't work
    # NOTE : One solution could be to change file and send the previous one to avoid negative seeking in write mode
    global downloading, data_file, master_connection, chunk_size, sd_file_lock

    downloading = True
    offset = 0
    try:
        while True:
            sd_file_lock.acquire()
            sd_file_io.seek(offset)
            chunk = sd_file_io.read(chunk_size)
            offset = sd_file_io.tell()
            sd_file_lock.release()
            if not chunk:
                break
            else:
                master_connection.send(chunk)
    except IOError as error:
        logging.error('Download error :' + str(error))
    logging.info('Download complete.')
    downloading = False


def save_file():
    """This is a save_file function.
    """
    global base_path, data_file, sd_file_io, sd_file_lock, master_connection

    sd_file_lock.acquire()
    sd_file_io.close()
    logging.info('File ' + data_file + ' saved.')

    data_file = path.join(base_path, file_name + datetime.datetime.utcnow().strftime('_%Y%m%d_%H%M%S') + '.dat.gz')
    sd_file_io = gzip.open(data_file, "ab+")
    sd_file_lock.release()
    logging.info('New file ' + data_file + ' created.')

if __name__ == '__main__':
    logging.info('*** SESSION STARTING ***\n')
    logging.info('RaspArDAS version ' + str(version) + '.')
    if len(sys.argv) > 1:
        i = 1
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'debug':
                    if str(sys.argv[i+1]) == 'on':
                        debug = True
                        logging.info('   Debug mode ON')
                    else:
                        logging.info('   Debug mode OFF')
                elif sys.argv[i] == 'slave':
                    slave_device = int(sys.argv[i+1])
                    logging.info('   Slave device : ' + str(slave_device))
                elif sys.argv[i] == 'calibration':
                    calibration_file = str(sys.argv[i+1])
                    logging.info('Calibration file: ' + calibration_file)
                else:
                    logging.info('   Unknown argument : ' + str(sys.argv[i]))
                i += 2
        else:
            logging.info('Parsing failed : arguments should be given by pairs [key value], ignoring arguments...')
    else:
        logging.info('No argument found... Using defaults.')

    try:
        st = statvfs('.')
        available_space = st.f_bavail * st.f_frsize / 1024 / 1024
        logging.info('Remaining disk space : %.1f MB' % available_space)
    except:
        pass
    logging.info('Saving log to ' + log_file)
    try:
        slave = serial.Serial(slave_device, baudrate=57600, timeout=0.1)
        slave.flush()
        slave_io = io.BufferedRWPair(slave, slave, buffer_size=128)  # FIX : BufferedRWPair does not attempt to synchronize accesses to its underlying raw streams. You should not pass it the same object as reader and writer; use BufferedRandom instead.
        logging.info('Saving data to ' + data_file)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with slave! : ' + str(e))
        status &= False
    try:
            logging.debug('Master binding on (%s, %d)...' % (LocalHost, LocalPort))
            master_socket.bind((LocalHost, LocalPort))
            master_socket.listen(1)
            logging.debug('Binding done!')
    except IOError as e:
        logging.error('*** Cannot open server socket!' + str(e))
        status &= False
    try:
        sd_file_io = gzip.open(data_file, 'ab+')
        # sd_file_io = io.BufferedRandom(sd_file, buffer_size=128)
    except IOError as e:
        logging.error('*** Cannot open file ! : ' + str(e))
        status &= False
    if calibration_file != '':
        try:
            with open(calibration_file, 'r') as cal:
                cal.readline() # header
                for i in range(n_channels):
                    calibration.append({})
                    s = cal.readline().rstrip('\n').split(sep='\t')
                    calibration[i]['sensor'] = s[0]
                    calibration[i]['variable'] = s[1]
                    calibration[i]['unit'] = s[2]
                    calibration[i]['format'] = s[3]
                    calibration[i]['coefs'] = []
                    for j in range(5):
                        calibration[i]['coefs'].append(float(s[4+j]))
                    logging.info('  Sensor: %s     variable: %s     unit: %s        coefs: %s'
                                 % (calibration[i]['sensor'], calibration[i]['variable'],
                                    calibration[i]['unit'], str(calibration[i]['coefs'])))
        except IOError as e:
            logging.error('*** Cannot read calibration file ! : ' + str(e))
            status &= False
    else:
        logging.info('Calibration : ')
        for i in range(n_channels):
            calibration.append({'sensor': '0000', 'variable': 'freq', 'unit': 'Hz', 'format': '%11.4f',
                                'coefs': [0., 1., 0., 0., 0.]})
            logging.info('  Sensor: %s     variable: %s     unit: %s        coefs: %s'
                         % (calibration[i]['sensor'], calibration[i]['variable'],
                            calibration[i]['unit'], str(calibration[i]['coefs'])))

    if status:
        try:
            # listen for a short time (e.g. 1 second) to check if another slave is talking to the master
            # TODO : Should the master broadcast a message every second when it is listening to a download from
            # a RaspArDAS to inhibit all others?
            # master_queue.put(b'#E0\r')
            disk_writer = Thread(target=write_disk)
            disk_writer.setDaemon(True)
            disk_writer.start()
            master_connector = Thread(target=connect_master)
            master_connector.setDaemon(True)
            master_connector.start()
            master_talker = Thread(target=talk_master)
            master_talker.setDaemon(True)
            master_talker.start()
            slave_talker = Thread(target=talk_slave)
            slave_talker.setDaemon(True)
            slave_talker.start()
            master_listener = Thread(target=listen_master)
            master_listener.setDaemon(True)
            master_listener.start()
            slave_listener = Thread(target=listen_slave)
            slave_listener.setDaemon(True)
            slave_listener.start()
            sd_file_lock = Lock()
            while not stop:
                pass
            logging.info('Exiting - Waiting for threads to end...')
            slave_listener.join()
            master_talker.join()
            master_listener.join()
            master_connector.join()
            slave_talker.join()
            disk_writer.join()

        finally:
            logging.info('Exiting - Closing file and communication ports...')
            try:
                slave
            except:
                pass
            else:
                slave.close()
            try:
                sd_file_io
            except:
                pass
            else:
                sd_file_io.close()
            logging.info('Exiting RaspArDAS')
            logging.info('*** SESSION ENDING ***\n\n')
    else:
        logging.info('Exiting RaspArDAS')
        try:
            slave.close()
        except:
            pass
        try:
            sd_file_io.close()
        except:
            pass
