import os
import io
import serial
import time
import logging
import queue
from threading import Thread
# import PyCRC

version = 0.11
DEBUG = False
master_device = '/dev/ttyUSB0'
slave_device = '/dev/ttyACM0'
now = time.strftime('%Y%m%d%H%M%S', time.gmtime())
print(now)
data_file = 'raw' + now + '.dat'
status = True
base_path = os.path.dirname(__file__)
if not os.path.isdir('logs'):
    os.mkdir('logs')
logging_level = logging.DEBUG
logging.Formatter.converter = time.gmtime
log_format = '%(asctime)-15s | %(process)d | %(levelname)s:%(message)s'
logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler(os.path.join(base_path, 'logs/RaspArDAS.log')),
                              logging.StreamHandler()])
slave_queue = queue.Queue()  # what comes from ArDAS
master_queue = queue.Queue()  # what comes from Master (e.g. cron task running client2.py)
data_queue = queue.Queue()  # what should be written on disk
quiet = True
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
    global DEBUG, stop, downloading, slave_io, data_queue

    while not stop:
        # Read incoming data from slave (ArDAS)
        try:
            msg = slave_io.readline()
            if len(msg) > 0:
                # Sort data to store on SD from data to repeat to master
                if DEBUG:
                    logging.debug('Slave says : ' + msg)
                if msg[0] == '*':
                    # TODO: reformat data and check crc
                    logging.debug('Storing : ' + msg)
                    # Send data to data_queue
                    data_queue.put(msg)
                else:
                    # Repeat data to the master (if not in quiet mode)
                    # TODO: Implement a function in ardasX.ino to set/return status (quiet, peer_download...)
                    if not downloading:
                        slave_queue.put(msg)
        except queue.Full:
            pass
        except serial.SerialTimeoutException:
            pass
    logging.info('Closing listen_slave thread...')


def talk_slave():
    """This is a talker thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global DEBUG, stop, slave_io, master_queue

    while not stop:
        try:
            msg = master_queue.get(timeout=0.25)
            if DEBUG:
                logging.debug('Saying to Slave : ' + msg)
            slave_io.write(msg)
            slave_io.flush()
        except queue.Empty:
            pass
        except serial.SerialTimeoutException:
            logging.error('Could not talk to slave...')
    logging.info('Closing talk_slave thread...')


def listen_master():
    """This is a listener thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global DEBUG, stop, master_io, master_queue

    while not stop:
        try:
            msg = master_io.readline()
            if len(msg) > 0:
                if DEBUG:
                    logging.debug('Master says : ' + msg)
                if msg[:-1] == '#XB':
                    logging.info('Download request')
                    full_download()
                elif msg[:-1] == '#XP':
                    logging.info('Partial download request')
                elif msg[:-1] == '#XS':
                    logging.info('Aborting download request')
                elif msg[:-1] == '#ZF':
                    logging.info('Reset request')
                else:
                    master_queue.put(msg)
        except queue.Full:
            logging.error('Master queue is full!')
        except serial.SerialTimeoutException:
            pass
    logging.info('Closing listen_master thread...')


def talk_master():
    """This is a talker thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global DEBUG, stop, downloading, master_io, slave_queue

    while not stop:
        try:
            if not downloading:
                msg = slave_queue.get(timeout=0.25)
                if DEBUG:
                    logging.debug('Saying to Master :' + msg)
                master_io.write(msg)
                master_io.flush()
        except queue.Empty:
            pass
    logging.info('Closing talk_master thread...')


def write_disk():
    """This is a writer thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global DEBUG, stop, sd_file, data_queue

    while not stop:
        try:
            msg = data_queue.get(timeout=0.25)
            if len(msg) > 0:
                if DEBUG:
                    logging.debug('Writing to disk :' + msg)
                sd_file.writelines(msg)
                sd_file.flush()
        except queue.Empty:
            pass
    sd_file.flush()
    logging.info('Closing write_disk thread...')


def full_download():
    """This is a full_download function.
    """
    global downloading, data_file, master_io, master

    downloading = True
    msg = ''
    fid = os.open(data_file, os.O_RDONLY)
    offset = 0
    master.flush()
    fid_size = os.stat(data_file).st_size
    try:
        while offset < fid_size:
            msg = os.pread(fid, offset, 1)
            if msg != '':
                print('offset ' + str(offset) + '/' + str(fid_size) + '- msg :' + msg.decode('utf-8'))
            else:
                print('offset ' + str(offset) + '/' + str(fid_size) + ' - msg empty!')
            offset += 1
            #master.write(b'#')
            master.write(bytes(msg))
            master.flush()
    except IOError as e:

        logging.info('Download complete :' + str(e))


if __name__ == '__main__':
    try:
        slave = serial.Serial(slave_device, baudrate=9600, timeout=0.25)
        slave_io = io.TextIOWrapper(io.BufferedRWPair(slave, slave), newline='\r\n', line_buffering=True)
    except:
        logging.error('*** Cannot open serial connexion with slave!')
        status &= False
    try:
        master = serial.Serial(master_device, baudrate=57600, timeout=0.25)
        master_io = io.TextIOWrapper(io.BufferedRWPair(master, master), newline='\r', line_buffering=True)
    except:
        logging.error('*** Cannot open serial connexion with master!')
        status &= False
    try:
        sd_file = open(data_file, "at")
    except:
        logging.error('*** Cannot open file !')
        status &= False

    if status:
        try:
            # listen for a short time (e.g. 1 second) to check if another slave is talking to the master
            # TODO : Should the master broadcast a message every second when it is listening to a download from
            # a RaspArDAS to inhibit all others?
            # master_queue.put(b'#E0\r')
            disk_writer = Thread(target=write_disk)
            disk_writer.setDaemon(True)
            disk_writer.start()
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
            while not stop:
                # show a prompt
                cmd = input('Type exit to quit.\n> ')
                if cmd == 'exit':
                    stop = True
                else:
                    print('Unknown command.\n> ')
            logging.info('Exiting : Waiting for threads to end...')
            slave_listener.join()
            master_talker.join()
            master_listener.join()
            slave_talker.join()
            disk_writer.join()

        finally:
            logging.info('Exiting : closing file and communication ports...')
            slave.close()
            master.close()
            sd_file.close()
            logging.info('Exiting RaspArDAS')
    else:
        logging.info('Exiting RaspArDAS')
        try:
            slave.close()
        except:
            pass
        try:
            master.close()
        except:
            pass
        try:
            sd_file.close()
        except:
            pass