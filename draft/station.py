__author__ = 'su530201'
from osgeo import ogr # requires ogr

# DEBUG = True
#
# class Station(object):
#     name = ''
#     point = ogr.Geometry(ogr.wkbPoint)
#     point.AddPoint(1198054.34, 648493.09)
#
#
#     def __init__(self, a_name='unknown'):
#         self.name = a_name

from osgeo import ogr # requires ogr

LB72 = ogr.osr.SpatialReference()
LB72.ImportFromEPSG(31370)
WGS84 = ogr.osr.SpatialReference()
WGS84.ImportFromEPSG(4326)

point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(119805.00, 84930.00)
point.AssignSpatialReference(LB72)
point.TransformTo(WGS84)

geojson_point = point.ExportToJson()
print(geojson_point)