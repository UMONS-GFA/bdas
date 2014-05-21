__author__ = 'Olivier Kaufmann'

from settings import LocalPort, RemoteHost, RemotePort
import sys
import subprocess   # used to launch shell command


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
