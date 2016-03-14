from os import path, mkdir, statvfs
import io
import serial
import time
import datetime
import logging
import binascii
import queue
import gzip
from struct import unpack_from
from threading import Thread, Lock
#import PyCRC

version = 0.21
DEBUG = False
master_device = '/dev/ttyUSB0'
slave_device = '/dev/ttyACM0'
data_file = 'raw.dat.gz'
n_channels = 4
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

def unpack_record(self, message):
        """ unpacks a record received from the ArDAS and checks the CRC """

        # # Unpack the received message into struct
        # (messageID, acknowledgeID, module, commandType,
        #  data, recvChecksum) = unpack('<LLBBLL', message)
        #
        # # Calculate the checksum of the recv message minus the last 4
        # # bytes that contain the sent checksum
        # calcChecksum = crc32(message[:-4])
        # if recvChecksum == calcChecksum:
        #     print "Checksum checks out"
        pass


def listen_slave():
    """This is a listener thread function.
    It processes items in the queue one after
    another.  This daemon threads runs into an
    infinite loop, and only exit when
    the main thread ends.
    """
    global stop, downloading, slave_io, data_queue, n_channels

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
                #logging.debug('record : {0:X}'.format(record))
                logging.debug('record : %s' %str(record))
                #logging.debug('{0:X}'.format(record_crc))
                logging.debug('record_crc : %d' %record_crc)
                #logging.debug('msg_crc : {0:X}'.format(crc))
                logging.debug('msg_crc : %d' %msg_crc)
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
                    for i in range(n_channels):
                        decoded_record += ' %04d %11.4f' %(instr[i], freq[i])
                    decoded_record += '\n'
                    logging.debug('Storing : ' + decoded_record)
                    # Send data to data_queue
                    data_queue.put(decoded_record.encode('ascii'))
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
                try:
                    logging.debug('Master says : ' + msg.decode('ascii'))
                except:
                    logging.warning('*** listen_master thread - Unable to decode master message...')
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
                try:
                    logging.debug('Saying to master :' + msg.decode('ascii'))
                except:
                    logging.warning('*** talk_master thread - Unable to decode slave message...')
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
    logging.info('File ' + ' saved.')

if __name__ == '__main__':
    logging.info('RaspArDAS version ' + str(version) + '.')
    # if len(sys.argv) > 1:
    #     if len(sys.argv) % 2 == 1:
    #         while i < len(sys.argv)-1:
    #             if sys.argv[i] == 'master':
    #                 LocalHost = str(sys.argv[i+1])
    #                 logging.info('   Host : ' + LocalHost)
    #             elif sys.argv[i] == 'slave':
    #                 LocalPort = int(sys.argv[i+1])
    #                 logging.info('   Port : ' + str(LocalPort))
    #                 # LocalPort = int(LocalPort)
    #             elif sys.argv[i] == 'cmdfile':
    #                 cmdfile = str(sys.argv[i+1])
    #                 logging.info('   Command file : ' + cmdfile)
    #                 # open method create a new file
    #                 cf = open(cmdfile, 'rt')
    #                 logging.info('Executing command file %s.' % cmdfile)
    #                 command = os.path.basename(cmdfile).split('.')[0]
    #                 # readlines returns a list of lines
    #                 cmd_lines = cf.readlines()
    #                 cf.close()
    #                 cmd = cmd_lines[cl].strip('\n')
    #                 interactive = False
    #             elif sys.argv[i] == 'tag':
    #                 tags.append(str(sys.argv[i+1]))
    #                 logging.info('Tag %s.' % tags[-1])
    #             else:
    #                 logging.info('   Unknown argument : ' + sys.argv[i])
    #             i += 2
    #     else:
    #         logging.info('Parsing failed : arguments should be given by pairs [key value], ignoring arguments...')
    # else:
    #     logging.info('No argument found... Using defaults.')
    try:
        st = statvfs('.')
        available_space = st.f_bavail * st.f_frsize / 1024 / 1024
        logging.info('Remaining disk space : %.1f MB' % available_space)
    except:
        pass
    try:
        slave = serial.Serial(slave_device, baudrate=57600, timeout=0.01)
        slave_io = io.BufferedRWPair(slave, slave, buffer_size=128)  # FIX : BufferedRWPair does not attempt to synchronize accesses to its underlying raw streams. You should not pass it the same object as reader and writer; use BufferedRandom instead.
        logging.info('saving data to ' + data_file)
    except IOError as e:
        logging.error('*** Cannot open serial connexion with slave! : ' + str(e))
        status &= False
    try:
        master = serial.Serial(master_device, baudrate=9600, timeout=0.01)
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
