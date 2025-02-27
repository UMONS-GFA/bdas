import sys
import os.path
import socket
import select
import time
import logging
import json
import re
import bdas.report_jobs_status as rjs

try:
    from bdas.settings import LocalHost, LocalPort, EOL, BIN_DIR
except:
    LocalHost = None
    LocalPort = None
    BIN_DIR = None
    EOL = b'\r'

__author__ = 'kaufmanno'

version = '2.30'
cl = 0  # current command line index
cmd_lines = []  # command lines
eod = False  # end of download
data_newline = False  # new line of data
dl_expected_duration = 5400  # full µDAS download
Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_list = [b'#HE', b'#E0', b'#E1', b'#E2', b'#SD', b'#SR', b'#SI', b'#SS', b'#ZR', b'#ZF', b'#XB', b'#RI', b'#XS',
                b'#XP', b'#RM', b'#RL', b'#RV', b'#XN', b'#WB', b'#RW']
for i in range(0, 256):
    command_list.append(bytearray(('-%03d' % i).encode('ascii')))
response_list = [b'HELP COMMAND :', b'!E0', b'!E1', b'!E2', b'!SD', b'!SR', b'!SI', b'!SS', b'!ZR', b'!ZF', b'\xfd',
                 b'!RI', b'!XS', b'\xfd', b'!RM', b'*', b'!RV', b'\xfd', b'!WB', b'!RW']
for i in range(0, 256):
    response_list.append(b'!HI')
recvdata = b''
data = b''
das_params = {'Station': None, 'NetId': None, 'Integration': None, 'Channels': [], 'Used_Mem': None, 'Total_Mem': None,
              'Previous_Connection': None}
kmax = 10
timeout = 0.2
outfile = 'out.bin'
cmdfile = ''  # script argument to specify command file
basepath = os.path.dirname(__file__)
if not os.path.exists(os.path.join(basepath, 'logs')):
    os.makedirs(os.path.join(basepath, 'logs'))
if BIN_DIR is None:
    BIN_DIR = os.path.join(basepath, '..', 'DownloadDAS')
if not os.path.exists(BIN_DIR):
    os.makedirs(BIN_DIR)
verbose = False
db_logging = True  # if True logs status in the download_database automatically set to false in interactive sessions
conn = None
job_id = None
timestamp = ''
logging_level = logging.DEBUG
logging.Formatter.converter = time.gmtime
log_format = '%(asctime)-15s | %(process)d | %(levelname)s:%(message)s'
logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
                    handlers=[logging.FileHandler(os.path.join(basepath, 'logs/client2.log')), logging.StreamHandler()])
command = ''
tags = []
status = -1  # -1 : unknown; 0 : OK; 1 : Warning(s); 2 : Errors 3: no connection
status_dict = {-1: 'Unknown', 0: 'OK', 1: 'Warning', 2: 'Error', 3: 'No connection'}


def send_command(acmd):
    """

    :param acmd: binary
    :return
    """
    global data, recvdata, cl, status
    data = b''
    k = 0
    logging.info('Sending command %s ...' % acmd.decode('utf-8'))
    if acmd[0:1] == b'-':
        acmd_root = acmd[0:4]
    else:
        acmd_root = acmd[0:3]
    if acmd_root in command_list:
        readable, writable, exceptional = select.select([], [Sock], [], 6)
        if Sock in writable:
            Sock.send(acmd + EOL)
            response = response_list[command_list.index(acmd_root)]
            if verbose:
                logging.info('Expected response: ' + repr(response))
            while k < kmax:
                starttime = time.time()
                while time.time() < starttime + 100 * timeout:
                    readable, writable, exceptional = select.select([Sock], [], [], timeout)
                    if Sock in readable:
                        recvdata = Sock.recv(1)
                        data += recvdata
                        if response in data:
                            data = data[data.find(response):]
                            if verbose:
                                logging.info('Response to command %s received' % acmd_root.decode('utf-8'))
                            return
                        elif b'!ERROR : Unknown Command' in data:
                            logging.warning('*** Unknown command! : repeating command...')
                            if status < 2:
                                status = 1
                            send_command(acmd)
                            return
                    else:
                        Sock.send(acmd + EOL)
                        logging.warning('*** No response! : repeating command...')
                k += 1
            if k == kmax:
                logging.error('*** Das is not responding')
                status = 2
                logging.debug(data)
                cmd_lines.append('exit')
                cl = len(cmd_lines)-1
        else:
            logging.error('*** Unable to send command !')
            status = 2
            cmd_lines.append('exit')
            cl = len(cmd_lines)-1
    else:
        logging.warning('*** Unknown command: %s', acmd.decode('utf-8'))
        status = 1


def flush():
    """ remove pending data in socket stream """
    logging.info('flushing...')
    send_command(b'#XS')
    send_command(b'#E0')


def failed_download(msg):
    """ interrupt download if the ending sequence is wrong

        :param msg: string

    """
    global eod, cl, status

    logging.error('*** Incorrect ending of downloaded data...')
    logging.debug(msg)
    status = 2
    eod = True
    send_command(b'#XS')

if __name__ == '__main__':
    cmd = []
    # connect to the status logging database
    if db_logging:
        timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())+"'"
        conn = rjs.connect_to_logDB()

    # set the logging environment up
    # logging_level = logging.DEBUG
    # logging.Formatter.converter = time.gmtime
    # log_format = '%(asctime)-15s %(levelname)s:%(message)s'
    # logging.basicConfig(format=log_format, datefmt='%Y/%m/%d %H:%M:%S UTC', level=logging_level,
    #                     handlers=[logging.StreamHandler(sys.stdout)])
    logging.info('_____ Started _____')
    logging.info('client2.py version ' + version)

    logging.info('Parsing arguments...')
    # check if python script has the name of a command file as argument
    # sys.argv[0] is python script name
    interactive = True  # interactive session by default (unless a command file is passed as argument
    i = 1
    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'host':
                    LocalHost = str(sys.argv[i+1])
                    logging.info('   Host : ' + LocalHost)
                elif sys.argv[i] == 'port':
                    LocalPort = int(sys.argv[i+1])
                    logging.info('   Port : ' + str(LocalPort))
                    # LocalPort = int(LocalPort)
                elif sys.argv[i] == 'cmdfile':
                    cmdfile = str(sys.argv[i+1])
                    logging.info('   Command file : ' + cmdfile)
                    # open method create a new file
                    cf = open(cmdfile, 'rt')
                    logging.info('Executing command file %s.' % cmdfile)
                    command = os.path.basename(cmdfile).split('.')[0]
                    # readlines returns a list of lines
                    cmd_lines = cf.readlines()
                    cf.close()
                    cmd = cmd_lines[cl].strip('\n')
                    interactive = False
                elif sys.argv[i] == 'tag':
                    tags.append(str(sys.argv[i+1]))
                    logging.info('Tag %s.' % tags[-1])
                else:
                    logging.info('   Unknown argument : ' + sys.argv[i])
                i += 2
        else:
            logging.info('Parsing failed : arguments should be given by pairs [key value], ignoring arguments...')
    else:
        logging.info('No argument found...')
        verbose = True
        db_logging = False
        # show a prompt
        cmd = input('Type command (type #HE for help or exit to quit).\n> ')

    # create a job in logging database
    if db_logging and (conn is None):
        logging.error('*** Unable to connect to database for status logging !')
        status = 2
        db_logging = False
    else:
        rjs_status, job_id = rjs.insert_job(conn, timestamp, command, tags)
        logging.info('job id :' + str(job_id))
        if not rjs_status:
            logging.error('*** Unable to insert current job to database for status logging !')
            status = 2

    # Socket connection
    if isinstance(LocalHost, str) & isinstance(LocalPort, int):
        logging.info('Trying to connect...')
        try:
            Sock.connect((LocalHost, LocalPort))
            # status = 0
        except socket.error as err:
            logging.error('*** Connection failed : %s ' % err)
            status = 3
            if db_logging:
                timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())+"'"
                if not rjs.update_job_status(conn, job_id, timestamp, status_dict[status]):
                    logging.warning('*** Unable to log status to database')
                rjs.close_connection_to_logDB(conn)
            sys.exit(status)
        logging.info('Socket connected')
        time.sleep(1)
    else:
        logging.info('Invalid connection parameters...')
        print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')
        sys.exit(3)

    if interactive:
        logging.info('Starting interactive session...')
        # show a prompt
        cmd = input('Type command (type #HE for help or exit to quit).\n> ')

    Sock.setblocking(False)
    newline = False
    while True:
        if cmd.lower() == 'exit':
            Sock.close()
            break
        elif cmd.lower() == 'flush':
            flush()
            cmd = bytearray(cmd.encode('ascii'))
            cmd += EOL
        elif cmd.lower() == 'sync':
            cmd = '#SD ' + time.strftime('%Y %m %d %H %M %S', time.gmtime())
            cmd = bytearray(cmd.encode('ascii'))
            send_command(cmd)
        else:
            cmd = bytearray(cmd.encode('ascii'))
            send_command(cmd)
        while True:
            try:
                readable, writable, exceptional = select.select([Sock], [], [], timeout)
                if Sock in readable:
                    recvdata = Sock.recv(1)
                    if len(recvdata) == 1:
                        data += recvdata
                        if b'\xfd' in data:
                            data = data[data.find(b'\xfd'):]
                            logging.info('*** Downloading data ... ***')
                            # check if there is a command file as parameter
                            # logging.debug('Command file: %s length %d' %(cmdfile, len(cmd_lines)))
                            if cmdfile != '':
                                if cl < len(cmd_lines)+2:
                                    # create output file name
                                    cl += 1
                                    # logging.debug('*** command line %d: %s' %(cl, cmd_lines[cl]))
                                    outfile = os.path.abspath(os.path.join(BIN_DIR, cmd_lines[cl].strip('\n') +
                                                              time.strftime('_%Y%m%d_%H%M', time.gmtime()) + '.bin'))
                                    # logging.debug('*** outfile: %s ***' %outfile)
                                    # read expected download duration
                                    cl += 1
                                    # logging.debug('*** command line %d: %s' %(cl, cmd_lines[cl]))
                                    dl_expected_duration = int(cmd_lines[cl])
                                    # logging.debug('*** Expected duration: %d ***' %dl_expected_duration)
                                else:
                                    logging.error('*** Incorrect arguments in command file !')
                                    status = 2
                                    cl = len(cmd_lines)
                                    cmd_lines.append('exit')
                                    break
                            logging.info('Saving results in %s' % outfile)
                            if not os.path.exists(os.path.join(basepath, '..', 'DownloadDAS')):
                                logging.warning('*** DownloadDAS directory does not exist!')
                                os.makedirs(os.path.join(basepath, '..', 'DownloadDAS'))
                                logging.info('*** Created DownloadDAS directory')
                            try:
                                f = open(outfile, 'wb')
                                k = 0  # use to calculate file size
                                nxfe = 0  # number of terminating \xfe
                                eod = False  # end of download
                                start_time = time.time()
                                dl_timeout = start_time + dl_expected_duration
                                while not eod and time.time() < dl_timeout:
                                    # show the size of the downloaded file in Kb
                                    if k/256-round(k/256) == 0 and cmdfile == '':
                                        print(repr(round(k/1024, 1)) + ' Kb', end='\r')
                                    f.write(data)  # write data to file
                                    if data == b'\xfe':
                                        nxfe += 1
                                        if nxfe == 12:  # generalize for less than 4 channels
                                            eod = True
                                    else:
                                        if data != b'' and nxfe >= 3:
                                            failed_download('Incorrect ending sequence.')
                                        elif data != b'':
                                            nxfe = 0
                                    if not eod:
                                        readable, writable, exceptional = select.select([Sock], [], [], timeout)
                                        if Sock in readable:
                                            data = Sock.recv(1)  # receive data from remote host
                                            k += 1
                                        else:
                                            data = b''
                                            # print('Waiting for data...', end='\n')
                                if time.time() >= dl_timeout:
                                    failed_download('Download takes too much time, job canceled')
                                else:
                                    logging.info('*** Download complete! ***')
                                f.close()
                                data_newline = False
                                # save a .jsn file with the parameters of the DAS
                                try:
                                    f = open(outfile+'.jsn', 'wt')
                                    json.dump(das_params, f)
                                    f.close()
                                    logging.info('DAS parameters saved to %s...' % outfile+'.jsn')
                                except:
                                    logging.warning('*** Unable to save DAS parameters to %s...' % outfile+'.jsn')
                                    status = max(status, 1)

                            except IOError:
                                logging.error('*** Unable to open file %s ! - Exiting command file %s ...'
                                              % (outfile, cmdfile))
                                status = 2
                                cl = len(cmd_lines)
                                cmd_lines.append('exit')
                        elif recvdata.decode('ascii') == '\n':
                            data_newline = True
                        elif recvdata.decode('ascii') == '\r':
                            if data_newline:
                                logging.info(data.decode('utf-8'))
                                if cmd == b'#RI':
                                    logging.debug('parsing !RI...')
                                    regex = '^!RI Station:\d{4} DasNo:\d{3} Integration:\d{4} I1:\d{4} I2:\d{4} I3:\d{4} I4:\d{4}.*'
                                    # creates a dictionary of DAS parameters (to be saved as a json structure in a .jsn
                                    # file along with the bin file)
                                    s = data.decode('utf-8')
                                    if re.match(regex, s) is not None:
                                        s = s[:-2].replace(':', ' ').split(' ')
                                        das_params['Station'] = s[2]
                                        das_params['NetId'] = s[4]
                                        das_params['Integration'] = s[6]
                                        i = 7
                                        channels = []
                                        while s[i][0] == 'I':
                                            channels.append(s[i+1])
                                            i += 2
                                        das_params['Channels'] = tuple(channels)
                                        das_params['Used_Mem'] = s[i]
                                        das_params['Total_Mem'] = s[i+1]
                                        das_params['Previous_Connection'] = s[i+2]
                                        logging.info(repr(das_params))
                                    else:
                                        logging.warning('*** Unable to parse RI... ***')
                                data = bytearray()
                            data_newline = False
                        else:
                            data_newline = False
                else:
                    break
            except:
                logging.debug('### Exception in infinite loop !')
                pass
        data = bytearray()
        if cmdfile == '':
            cmd = input("> ")
        else:
            cl += 1
            if verbose:
                print('Next command...')
            if cl < len(cmd_lines):
                cmd = cmd_lines[cl].strip('\n')
            else:
                cmd = 'exit'

    if cmdfile != '':
        logging.info('______ Ended ______\n\n')
        if status == -1:
            status = 0
        Sock.close()
        if db_logging:
            timestamp = "'"+time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime())+"'"
            if not rjs.update_job_status(conn, job_id, timestamp, status_dict[status]):
                status = 2
                logging.warning('*** Unable to log status to database')
            rjs.close_connection_to_logDB(conn)
        sys.exit(status)
    else:
        Sock.close()
