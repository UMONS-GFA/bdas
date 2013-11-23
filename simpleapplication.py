__author__ = 'su530201'

import busconnection as bc
import das


def main():
    sercon = bc.DasConnectionSerial('/dev/ttyUSB0')
    adas = das.Das()

    adas.connection = sercon
    adas.connect()

if __name__ == "__main__":
    main()