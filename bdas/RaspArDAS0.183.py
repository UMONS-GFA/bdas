from os import path, mkdir, statvfs
import io
import serial
import time
import logging
import queue
import gzip
from threading import Thread, Lock
import PyCRC

version = 0.183
DEBUG = False
master_device = '/dev/ttyUSB0'
slave_device = '/dev/ttyACM0'
data_file = 'raw.dat.gz'
status = True
base_path = path.dirname(__file__)
if not path.isdir('logs'):
    mkdir('logs')
chunk_size = 4096
if DEBUG:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO
logging.Formatter.converter = time.gmtime
log_format = '%(asctime)-15s | %(process)d | %(levelname)s:%(message)s'
logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler(path.join(base_path, 'logs/RaspArDAS.log')),
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
    global stop, downloading, slave_io, data_queue

    while not stop:
        # Read incoming data from slave (ArDAS)
        try:
            byte = b''
            msg = b''
            while byte != b'\r' and byte != b'$':
                byte = slave_io.read(1)
                msg += byte
            logging.debug('Message :' + msg.decode('ascii'))
            if byte == b'$':
                # TODO: reformat data and check crc
                record = b''
                byte = b''
                while byte != b'\r':
                    byte = slave_io.read(1)
                    record += byte
                logging.debug('Storing : ' + record.decode('ascii'))
                # Send data to data_queue
                data_queue.put(record)
            else:
                if len(msg) > 0:
                    # Sort data to store on SD from data to repeat to master
                    logging.debug('Slave says : ' + msg.decode('ascii'))
                    if not downloading:
                        slave_queue.put(msg)
        except queue.Full:
            pass
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
            logging.debug('Saying to Slave : ' + msg.decode('ascii'))
            slave_io.write(msg)
            slave_io.flush()
        except queue.Empty:
            pass
        except serial.SerialTimeoutException:
            logging.error('Could not talk to slave...')

    logging.debug('Closing talk_slave thread...')


def listen_master():
    """This is a listener thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, master_io, master_queue

    while not stop:
        try:
            byte = b''
            msg = b''
            while byte != b'\r':
                byte = master_io.read(1)
                msg += byte
            if len(msg) > 0:
                logging.debug('Master says : ' + msg.decode('ascii'))
                if msg[:-1] == b'#XB':
                    logging.info('Download request')
                    full_download()
                elif msg[:-1] == b'#XP':
                    logging.info('Partial download request')
                elif msg[:-1] == b'#XS':
                    logging.info('Aborting download request')
                elif msg[:-1] == b'#ZF':
                    logging.info('Reset request')
                elif msg[:-1] == b'#KL':
                    stop = True
                else:
                    master_queue.put(msg)
        except queue.Full:
            logging.error('Master queue is full!')
        except serial.SerialTimeoutException:
            pass
    logging.debug('Closing listen_master thread...')


def talk_master():
    """This is a talker thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, downloading, master_io, slave_queue

    while not stop:
        try:
            if not downloading:
                msg = slave_queue.get(timeout=0.25)
                logging.debug('Saying to Master :' + msg.decode('ascii'))
                master_io.write(msg)
                master_io.flush()
        except queue.Empty:
            pass
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
            msg = data_queue.get(timeout=0.25)
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
    global downloading, data_file, master, master_io, chunk_size, sd_file_lock

    downloading = True
    master_io.flush()
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
                master_io.write(chunk)
                master_io.flush()
    except IOError as error:
        logging.error('Download error :' + str(error))
    logging.info('Download complete.')
    downloading = False

def save_file():
    """This is a save_file function.
    """
    global data_file, sd_file_io, sd_file_lock, master_io

    master_io.flush()
    sd_file_lock.acquire()
    sd_file_io.close()

    sd_file_io = gzip.open(data_file, "ab+")
    sd_file_lock.release()
    logging.info('File ' +  + 'saved.')

if __name__ == '__main__':
    logging.info('RaspArDAS version ' + str(version) + '.')
    try:
        st = statvfs('.')
        available_space = st.f_bavail * st.f_frsize / 1024 / 1024
        logging.info('Remaining disk space : %.1f MB' % available_space)
    except:
        pass
    try:
        slave = serial.Serial(slave_device, baudrate=57600, timeout=0.1)
        slave_io = io.BufferedRWPair(slave, slave, buffer_size=128)
        logging.info('saving data to ' + data_file)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with slave! : ' + str(e))
        status &= False
    try:
        master = serial.Serial(master_device, baudrate=9600, timeout=0.1)
        master_io = io.BufferedRWPair(master, master, buffer_size=128)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with master!' + str(e))
        status &= False
    try:
        sd_file_io = gzip.open(data_file, "ab+")
        # sd_file_io = io.BufferedRandom(sd_file, buffer_size=128)
    except IOError as e:
        logging.error('*** Cannot open file ! : ' + str(e))
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
            sd_file_lock = Lock()
            while not stop:
                # show a prompt
                # cmd = input('Type exit to quit.\n> ')
                # if cmd == 'exit':
                #    stop = True
                # else:
                #    print('Unknown command.\n> ')
                pass
            logging.info('Exiting - Waiting for threads to end...')
            slave_listener.join()
            master_talker.join()
            master_listener.join()
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
                master
            except:
                pass
            else:
                master.close()
            try:
                sd_file_io
            except:
                pass
            else:
                sd_file_io.close()

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
            sd_file_io.close()
        except:
            pass