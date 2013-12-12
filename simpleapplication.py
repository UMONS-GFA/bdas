__author__ = 'su530201'

import busconnection as bc
import das


def main():
    tcpcon = bc.DasConnectionTCP()
    adas = das.Das('255',tcpcon)

    adas.connect()
    output=adas.listen(2)
    print(output.decode('ascii'))

if __name__ == "__main__":
    main()