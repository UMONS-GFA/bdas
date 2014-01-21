__author__ = 'Olivier Kaufmann'
import busconnection as bc
import das
#import time
#import datetime

DEBUG = True

class Sensor(object):
    type=''
    idnum=0
    revnr=0

    def __init__(self, a_type ='unknown', an_idnum=0, a_revnum=0):
        self.type = a_type
        self.idnum = an_idnum
        self.revnr = a_revnum


    def install(self, astation, adate):
        # Use this method to install a sensor somewhere (on a known station) sometime

    def connect(self, adas, achannel, adate):
        # Use this method to connect a sensor on a channel of a das at a given date

