import sys
import os.path
import socket
import select
import time
try:
    from settings import LocalHost, LocalPort, EOL
except:
    LocalHost = None
    LocalPort = None
    EOL = b'\r'

cl = 0  # current command line index
cmdlines = []  # command lines
eod = False  # end of download
datanewline = False  # new line of data
dl_expectedduration = 5400  # full µDAS download
Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_list = [b'#HE', b'#E0', b'#E1', b'#E2', b'#SD', b'#SR', b'#SI', b'#SS', b'#ZR', b'#ZF', b'#XB', b'#RI', b'#XS',
                b'#XP', b'#RM', b'#RL', b'#RV', b'#XN', b'#WB', b'#RW']
for i in range(0, 256):
    command_list.append(bytearray(('-%03d' % i).encode('ascii')))
response_list = [b'HELP COMMAND :', b'!E0', b'!E1', b'!E2', b'!SD', b'!SR', b'!SI', b'!SS', b'!ZR', b'!ZF', b'\xfd',
                 b'!RI', b'!XS', b'\xfd', b'!RM', b'!RL', b'!RV', b'!XN', b'!WB', b'!RW']
for i in range(0, 256):
    response_list.append(b'!HI')
recvdata = b''
data = b''
kmax = 10
timeout = 0.2
outfile = 'out.bin'
cmdfile = ''  # script argument to specify command file
basepath = os.path.dirname(__file__)
verbose = False
version = '2.13'


def send_command(acmd):
    """

    :param acmd: binary
    :return
    """
    global data, recvdata, cl
    data = b''
    k = 0
    #print UTC date and time
    # strftime converts tuple returned by gmtime method to a string
    print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime()) +
          '\nSending command %s ...' % acmd.decode('utf-8'))
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
                print('Expected response: ' + repr(response))
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
                                print('Response to command %s received' % acmd_root.decode('utf-8'))
                            return
                        elif b'!ERROR : Unknown Command' in data:
                            print('Repeating command...')
                            send_command(acmd)
                            return

                k += 1
            if k == kmax:
                print('Das is not responding')
                print(data)
                cmdlines.append('exit')
                cl = len(cmdlines)-1
        else:
            print('Error : unable to send command !')
            cmdlines.append('exit')
            cl = len(cmdlines)-1
    else:
        print('Unknown command: %s', acmd.decode('utf-8'))


def flush():
    """ remove pending data in socket stream """
    print('flushing...')
    send_command(b'#XS')
    send_command(b'#E0')


def failed_download(msg):
    """ interrupt download if the ending sequence is wrong

        :param msg: string

    """
    global eod, cl

    print('Error: incorrect ending of downloaded data...')
    print(msg)
    eod = True
    send_command(b'#XS')

if __name__ == '__main__':
    cmd = []
    # print UTC date and time
    # strftime converts tuple returned by gmtime method to a string
    print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime()) + '\nclient2.py version ' + version
          + '\nParsing arguments...')
    # check if python script arguments
    # sys.argv[0] is python script name
    interactive = True # interactive session by default (unless a command file is passed as argument
    i = 1
    if len(sys.argv) > 1:
        if len(sys.argv) % 2 == 1:
            while i < len(sys.argv)-1:
                if sys.argv[i] == 'host':
                    LocalHost = str(sys.argv[i+1])
                    print('   Host : ' + LocalHost)
                elif sys.argv[i] == 'port':
                    LocalPort = int(sys.argv[i+1])
                    print('   Port : ' + str(LocalPort))
                    #LocalPort = int(LocalPort)
                elif sys.argv[i] == 'cmdfile':
                    cmdfile = str(sys.argv[i+1])
                    print('   Command file : ' + cmdfile)
                    # open method create a new file
                    cf = open(cmdfile, 'rt')
                    # readlines returns a list of lines
                    cmdlines = cf.readlines()
                    cf.close()
                    cmd = cmdlines[cl].strip('\n')
                    interactive = False
                else:
                    print('   Unknown argument : ' + sys.argv[i])
                i += 2
        else:
            print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime()) +
                  '\nParsing failed : arguments should be given by pairs [key value], ignoring arguments...')
    else:
        print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime()) +
              '\nNo argument found...')
        verbose = True

    # print UTC date and time
    # strftime converts tuple returned by gmtime method to a string
    print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime()) + '\nTrying to connect...')

    # Socket connection
    if isinstance(LocalHost, str) & isinstance(LocalPort, int):
        try:
            Sock.connect((LocalHost, LocalPort))
        except socket.error as err:
            print('connection failed : %s ' % err)
            sys.exit(3)
        print('Socket connected')
        time.sleep(1)
    else:
        print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime())
              + '\nInvalid connection parameters...')
        print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')
        sys.exit(3)

    if interactive:
        print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime())
              + '\nStarting interactive session...')
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
                            print('*** Downloading data ... ***')
                            # check if there is a command file as parameter
                            if cmdfile != '':
                                if cl < len(cmdlines)+2:
                                    # create output file name
                                    cl += 1
                                    outfile = os.path.abspath(os.path.join(basepath, '..', 'DownloadDAS',
                                                                           cmdlines[cl].strip('\n') +
                                                                           time.strftime('_%Y%m%d_%H%M',
                                                                                         time.gmtime())+'.bin'))
                                    # read expected download duration
                                    cl += 1
                                    dl_expectedduration = int(cmdlines[cl])
                                else:
                                    print('Incorrect arguments in command file !')
                                    cl = len(cmdlines)
                                    cmdlines.append('exit')
                                    break
                            print('Saving results in %s' % outfile)
                            try:
                                f = open(outfile, 'wb')
                                k = 0  # use to calculate file size
                                nxfe = 0  # number of terminating \xfe
                                eod = False  # end of download
                                starttime = time.time()
                                dl_timeout = starttime + dl_expectedduration
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
                                            #print('Waiting for data...', end='\n')
                                if time.time() >= dl_timeout:
                                    failed_download('Download takes too much time, job canceled')
                                else:
                                    print('*** Download complete! ***')
                                f.close()
                                datanewline = False
                            except IOError:
                                print('Error: unable to open file %s ! - Exiting command file %s ...' % (outfile,
                                                                                                         cmdfile))
                                cl = len(cmdlines)
                                cmdlines.append('exit')
                        elif recvdata.decode('ascii') == '\n':
                            datanewline = True
                        elif recvdata.decode('ascii') == '\r':
                            if datanewline:
                                print(data.decode('utf-8'))
                                data = bytearray()
                            datanewline = False
                        else:
                            datanewline = False
                else:
                    break
            except:
                pass
        data = bytearray()
        if cmdfile == '':
            cmd = input("> ")
        else:
            cl += 1
            if verbose:
                print('Next command...')
            if cl < len(cmdlines):
                cmd = cmdlines[cl].strip('\n')
            else:
                cmd = 'exit'

    if cmdfile != '':
        print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')
        Sock.close()
