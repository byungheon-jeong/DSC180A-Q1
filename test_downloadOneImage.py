import unittest

import ee
import datetime

from downloadOneImage import downloadSatImage

class test_downloadSatImage(unittest.TestCase):
    def testDownloadSatImage(self):
        bbox =[(79.8096398872554,42.295437794411406),
        (79.8096398872554,42.169352359125746),
        (80.24634643022415,42.169352359125746),
        (80.24634643022415,42.295437794411406)]

        bands = ['B1','B2','B3', 'B4', 'B5', 'B6_VCID_1', 'B6_VCID_2', 'B7', 'B8']
        start_date = datetime(1999,10,3)
        end_date = datetime(2021,10,19)

        expected = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').filterDate(start_date,end_date).filterBounds(ee.Geometry.Polygon(bbox)).select(bands)
        actual = downloadSatImage('LANDSAT/LE07/C01/T1_TOA', start_date, end_date, bbox, bands)

        self.assertEqual(expected, actual)


if __name__=="__main__":
    unittest.main()