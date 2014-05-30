import sys
import os.path
import socket
import select
import time
from settings import LocalHost, LocalPort, EOL

cl = 0  # current command line index
cmdlines = []  # command lines
eod = False  # end of download
datanewline = False  # new line of data
dl_expectedduration = 5400  # full µDAS download
Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
command_list = [b'#HE', b'#E0', b'#E1', b'#E2', b'#SD', b'#SR', b'#SI', b'#SS', b'#ZR', b'#ZF', b'#XB', b'#RI', b'#XS', b'#XP', b'#RM', b'#RL', b'#RV',
                b'#XN', b'#WB', b'#RW']
for i in range(0, 255):
    command_list.append(bytearray(('-%03d' % i).encode('ascii')))
response_list = [b'!HE', b'!E0', b'!E1', b'!E2', b'!SD', b'!SR', b'!SI', b'!SS', b'!ZR', b'!ZF', b'\xfd', b'!RI', b'!XS',b'\xfd', b'!RM', b'!RL', b'!RV',
                 b'!XN', b'!WB', b'!RW']
for i in range(0, 255):
    response_list.append(b'!HI')
recvdata = b''
data = b''
kmax = 10
timeout = 0.2
outfile = 'out.bin'
cmdfile = ''  # script argument to specify command file
basepath = os.path.dirname(__file__)


def send_command(acmd):
    global data, recvdata, cl
    data = b''
    #print UTC date and time
    # strftime convert tuple retun by gmtime method to a string
    print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime())+'\nSending command %s ...' % acmd.decode('utf-8'))
    if acmd in command_list:
        k = 0
        readable, writable, exceptional = select.select([], [Sock], [], 6)
        if Sock in writable:
            Sock.send(acmd + EOL)
            response = response_list[command_list.index(acmd)]
            print('Expected response: ' + repr(response))
            while k < kmax:
                starttime = time.time()
                while time.time() < starttime + 100 * timeout:
                    readable, writable, exceptional = select.select([Sock], [], [],timeout)
                    if Sock in readable:
                        recvdata = Sock.recv(1)
                        data += recvdata
                        if response in data:
                            data = data[data.find(response):]
                            print('Response to command %s received' % acmd.decode('utf-8'))
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
    global data, recvdata
    print('flushing...')
    command = '#XS\r'
    command = command.encode('ascii')
    data = b''
    while True:
        Sock.send(command)
        recvdata = Sock.recv(1)
        data += recvdata
        if data[data.find('!XS'.encode('ascii')):]:
            break
        time.sleep(1)


def failed_download(msg):
    global eod, cl

    print('Error: incorrect ending of downloaded data...')
    print(msg)
    eod = True
    send_command(b'#XS')

if __name__ == '__main__':

    # print UTC date and time
    # strftime convert tuple retun by gmtime method to a string
    print(time.strftime('____________\nUTC time : %Y %m %d %H:%M', time.gmtime())+'\nTrying to connect...')
    # Socket connection
    try:
        Sock.connect((LocalHost, LocalPort))
    except socket.error as err:
        print('connection failed : %s ' % err)
        sys.exit()
    print('Socket connected')
    time.sleep(1)


    # check if python script has the name of a command file as argument
    # sys.argv[0] is python script name
    if len(sys.argv) == 2:
        cmdfile = str(sys.argv[1])
        # open method create a new file
        cf = open(cmdfile, 'rt')
        # readlines return a list of lines
        cmdlines = cf.readlines()
        cf.close()
        cmd = cmdlines[cl].strip('\n')
    else:
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
                                    outfile = os.path.abspath(os.path.join(basepath, '..', 'DownloadDAS', cmdlines[cl].strip('\n') + time.strftime('_%Y%m%d_%H%M', time.gmtime())+'.bin'))
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
                                        try:
                                            data = Sock.recv(1)  # receive data from remote host
                                            k += 1
                                        except:
                                            data = b''
                                            print('Waiting for data...', end='\r')
                                if time.time() >= dl_timeout:
                                    failed_download('Download takes too much time, job canceled')
                                else:
                                    print('*** Download complete! ***')
                                f.close()
                                datanewline = False
                            except IOError:
                                print('Error: unable to open file %s ! - Exiting command file %s ...' % (outfile, cmdfile))
                                cl=len(cmdlines)
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
            cmd=input("> ")
        else:
            cl += 1
            print('Next command...')
            if cl < len(cmdlines):
                cmd = cmdlines[cl].strip('\n')
            else:
                cmd = 'exit'

    if cmdfile != '':
        print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')
        Sock.close()
