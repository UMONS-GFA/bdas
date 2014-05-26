import sys
import os.path
import socket
import time
from settings import LocalHost, LocalPort, EOL

cl = 0  # current command line index
cmdlines = []  # command lines
eod = False  # end of download
nmaxloops = 18  # number of loops used to wait for end of all transmission
loopduration = 5  # time in secs to wait in each loop
nXS = 5 # number of #XS commands
datanewline = False # new line of data
dl_expectedduration = 5400  # full µDAS download
Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def flush():
    print('flushing...')
    data=b'0'
    nl=0
    while (data!=b'') and (nl < nmaxloops):
        #beginning time
        starttime = time.time()
        data=b''
        while time.time() < starttime+loopduration:
            recvdata = Sock.recv(10)
            data += recvdata
            time.sleep(1)
        nl += 1


def failed_download(msg):
    print('Error: incorrect ending of downloaded data...')
    print(msg)
    for i in range(1,nXS):
        cl=len(cmdlines)-1
        cmdlines.append('#XS\n')
    cmdlines.append('exit\n')
    eod = True

if __name__=='__main__':
    data = bytearray()
    timeout = 0.2
    outfile = 'out.bin'
    cmdfile = ''  # script argument to specify command file
    basepath = os.path.dirname(__file__)

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

    cmd = bytearray(cmd.encode('ascii'))
    cmd += EOL
    Sock.setblocking(False)
    newline = False
    while 1:
        Sock.send(cmd)
        #beginning time
        starttime = time.time()
        while 1:
            #if you got some data, then break after timeout -> show prompt
            if data and time.time()-starttime > timeout:
                break

            #if you got no data at all, wait a little longer
            elif time.time()-starttime > timeout*3:
                break
            #recv something
            try:
                recvdata = Sock.recv(1)
                if recvdata:
                    t = 0
                    data += recvdata
                    starttime = time.time()
                    if b'\xfd' in data:
                        data = data[data.find(b'\xfd'):]
                        print('*** Downloading data ... ***')
                        # check if there is a command file as parameter
                        if cmdfile != '':
                            # create output file name
                            cl += 1
                            outfile = os.path.abspath(os.path.join(basepath, '..', 'DownloadDAS', cmdlines[cl].strip('\n') + time.strftime('_%Y%m%d_%H%M', time.gmtime())+'.bin'))
                            # read expected download duration
                            cl += 1
                            dl_expectedduration = int(cmdlines[cl])
                        print('Saving results in %s' % outfile)
                        try:
                            f = open(outfile, 'wb')
                            k = 0  # use to calculate file size
                            nxfe = 0  # number of terminating \xfe
                            eod = False  # end of download
                            dl_timeout = starttime + dl_expectedduration
                            while not eod and time.time() < dl_timeout:
                                # show the weight of the downloaded file in Kb
                                if k/256-round(k/256) == 0 and cmdfile == '':
                                    print(repr(round(k/1024, 1)) + ' Kb', end='\r')
                                f.write(data)  # write data to file
                                if data == b'\xfe':
                                    nxfe += 1
                                    if nxfe == 12: # generalize for less than 4 channels
                                        eod = True
                                else:
                                    if data != b'' and nxfe >= 3:
                                        failed_download('Incorrect ending sequence.')
                                    elif data != b'':
                                        nxfe = 0
                                if not eod:
                                    try:
                                        data = Sock.recv(1) # receive data from remote host
                                        k += 1
                                    except:
                                        data = b''
                                        #print('Waiting for data...',end="\r")
                            if time.time() > dl_timeout:
                                failed_download("Download takes too much time, job canceled")
                            else:
                                print('*** Download complete! ***')
                            f.close()
                            datanewline = False
                        except:
                            print('Error: unable to open file %s ! - Exiting command file %s ...' % (outfile, cmdfile))
                            cmdlines[cf+1] = 'exit'
                    elif recvdata.decode('ascii') == '\n':
                        datanewline = True
                    elif recvdata.decode('ascii') == '\r':
                        if datanewline:
                            print(data.decode('utf-8'))
                            data = bytearray()
                        datanewline = False
                    else:
                        sys.stdout.write(data)
                        datanewline = False
                else:
                    #sleep for sometime to indicate a gap
                    t += 1
                    time.sleep(0.1)
                    print("Waiting cycles..." + t, "\r")
            except:
                pass
        data = bytearray()
        if cmdfile == '':
            cmd=input("> ")
        else:
            cl += 1
            if cl < len(cmdlines):
                cmd=cmdlines[cl].strip('\n')
            else:
                cmd='exit'
        #print(">")
        #cmd = sys.stdin.readline()
        #cmd=cmd[:-1]
        if cmd.lower() == 'exit':
            Sock.close()
            break
        elif cmd.lower() == 'flush':
            flush()
            cmd=input("> ")
            cmd = bytearray(cmd.encode('ascii'))
            cmd += EOL
        else:
            cmd = bytearray(cmd.encode('ascii'))
            cmd += EOL
    if cmdfile != '':
        print('Ending at ' + time.strftime('UTC time : %Y %m %d %H:%M', time.gmtime()) + '\n____________')
