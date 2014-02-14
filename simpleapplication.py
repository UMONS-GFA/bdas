__author__ = 'su530201'

import busconnection as bc
import das


def main():
    tcpcon = bc.DasConnectionTCP()
    adas = das.Das('255',tcpcon)

    #adas.connect()
    #print('connected')
    output=adas.get_das_info()
    adas.set_no_echo()

    print(output)

if __name__ == "__main__":
    print('.')
    main()