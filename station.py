__author__ = 'su530201'
from osgeo import ogr # requires ogr

DEBUG = True

class Station(object):
    name = ''
    point = ogr.Geometry(ogr.wkbPoint)

    def __init__(self, a_name='unknown'):
        self.name = a_name