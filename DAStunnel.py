__author__ = 'Olivier Kaufmann'

from settings import LocalPort, RemoteHost, RemotePort
import sys
import subprocess

print('Opening tunnel...')
try:
    retcode = subprocess.call('nc -l -p %i -c "nc %s %i"' % (LocalPort, RemoteHost, RemotePort), shell=True)
    if retcode < 0:
        print('Process was terminated by signal', -retcode, file=sys.stderr)
    else:
        print('Process returned', retcode, file=sys.stderr)
except OSError as e:
    print("Execution failed:", e, file=sys.stderr)
