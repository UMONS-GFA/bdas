__author__ = 'kaufmanno'
from osgeo import ogr  # requires ogr

DEBUG = True

_local_sr = ogr.osr.SpatialReference()
_wgs84 = ogr.osr.SpatialReference()
_wgs84.ImportFromEPSG(4326)

class Station(object):
    name = ''
    point = ogr.Geometry(ogr.wkbPoint)

    def __init__(self, a_name='unknown', sr_epsg_code=None):
        """
        @param a_name: station name (a string)
        @param sr_epsg_code: local spatial reference EPSG code
        """
        self.name = a_name
        _local_sr.ImportFromEPSG(sr_epsg_code)
        self.point.AddPoint(0.0, 0.0, 0.0)
        self.point.AssignSpatialReference(_local_sr)
        self.point.TransformTo(_wgs84)

    def move_station(self, xl=None, yl=None, z=None):

        """

        @param xl: X in the local SR
        @param yl: Y in the local SR
        @param z: z in the local VR
        """
        self.point.SetPoint(xl, yl, z)
        self.point.AssignSpatialReference(_local_sr)
        self.point.TransformTo(_wgs84)

    @property
    def geojson(self):
        """


        @return:
        """
        geojson_point = self.point.ExportToJson()
        return geojson_point
