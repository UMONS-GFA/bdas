"""
Act like a proxy between a client and a remote server.
A port is opened on the locahost and every command sent to it is repeated to the remote host on the remote port.

"""

import sys
import subprocess   # used to launch shell command
from settings import LocalPort, RemoteHost, RemotePort


print('Opening tunnel...')
try:
    # launch netcat for proxy server socket
    retcode = subprocess.call('nc -l -p %i -c "nc %s %i"' % (LocalPort, RemoteHost, RemotePort), shell=True)
    if retcode < 0:
        print('Process was terminated by signal', -retcode, file=sys.stderr)
    elif retcode == 0:
        print("Tunnel opened")
    else:
        print('Process returned', retcode, file=sys.stderr)
except OSError as e:
    print("Execution failed:", e, file=sys.stderr)
