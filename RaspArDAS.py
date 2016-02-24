import os
import io
import serial
import time
import logging
import queue
from threading import Thread, Lock
# import PyCRC

version = 0.13
DEBUG = True
master_device = '/dev/ttyUSB0'
slave_device = '/dev/ttyACM0'
now = time.strftime('%Y%m%d%H%M%S', time.gmtime())
print(now)
data_file = 'raw' + now + '.dat'
status = True
base_path = os.path.dirname(__file__)
if not os.path.isdir('logs'):
    os.mkdir('logs')
chunk_size = 4096
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

# def read_bytes_from_stream(stream, chunksize=8192):
#     """ This is a generator that yields bytes
#      from a file-like object (stream), reading it
#      in chunks
#
#     :param chunksize:
#     :return:
#     """
#     while True:
#         chunk = stream.read(chunksize)
#         if chunk:
#             for b in chunk:
#                 yield b
#         else:
#             break


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
            byte = b''
            msg = b''
            while byte != b'\r':
                byte = slave_io.read(1)
                msg += byte
            if len(msg) > 0:
                # Sort data to store on SD from data to repeat to master
                if DEBUG:
                    logging.debug('Slave says : ' + msg.decode('ascii'))
                if msg[0] == b'*':
                    # TODO: reformat data and check crc
                    logging.debug('Storing : ' + msg)
                    # Send data to data_queue
                    data_queue.put(msg)
                    if not downloading:
                        slave_queue.put(msg)
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
                logging.debug('Saying to Slave : ' + msg.decode('ascii'))
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
            byte = b''
            msg = b''
            while byte != b'\r':
                byte = master_io.read(1)
                msg += byte
            if len(msg) > 0:
                if DEBUG:
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
                    logging.debug('Saying to Master :' + msg.decode('ascii'))
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
    global DEBUG, stop, sd_file_io, data_queue, sd_file_lock

    offset = sd_file_io.tell()
    while not stop:
        try:
            msg = data_queue.get(timeout=0.25)
            if len(msg) > 0:
                if DEBUG:
                    logging.debug('Writing to disk :' + msg.decode('ascii'))
                sd_file_lock.acquire()
                sd_file_io.fseek(offset)
                sd_file_io.write(msg)
                sd_file_io.flush()
                offset = sd_file_io.tell()
                sd_file_lock.release()
        except queue.Empty:
            pass
    sd_file.flush()
    logging.info('Closing write_disk thread...')


def full_download():
    """This is a full_download function.
    """
    global downloading, data_file, master_io, chunksize

    downloading = True
    master_io.flush()
    offset = 0
    chunk = b''
    try:
        while True:
            sd_file_lock.acquire()
            sd_file_io.seek(offset)
            chunk = sd_file.read(chunk_size)
            offset = sd_file_io.tell()
            sd_file_lock.release()
            if not chunk:
                break
            else:
                master_io.write(chunk)
                master_io.flush()
    except IOError as e:
        logging.error('Download error :' + str(e))
    logging.info('Download complete.')


if __name__ == '__main__':
    try:
        slave = serial.Serial(slave_device, baudrate=9600, timeout=0.25)
        slave_io = io.BufferedRWPair(slave, slave, buffer_size=128)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with slave! : ' + str(e))
        status &= False
    try:
        master = serial.Serial(master_device, baudrate=57600, timeout=0.25)
        master_io = io.BufferedRWPair(master, master, buffer_size=128)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with master!' + str(e))
        status &= False
    try:
        sd_file = open(data_file, "ab+")
        sd_file_io = io.BufferedRandom(sd_file, buffer_size=256)
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