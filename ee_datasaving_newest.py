import ee 
import geemap
from datetime import datetime
import numpy as np
import rasterio #for reading images
import matplotlib.pyplot as plt 
import pandas as pd
import os
from datetime import date
from datetime import timedelta 

def cloudscore(image):
    '''
    Inner function for computing cloud score such that we can remove 
    bad images from the landsat collections we download.
    Implementation in javascript can be found of Google Earth Engine 
    website under (landsat algorithms), translation to python by KH.
    Further help from Nicholas Clinton at 
    https://urldefense.com/v3/__https://gis.stackexchange.com/questions/252685/filter-landsat-images-base-on-cloud-cover-over-a-region-of-interest*5Cn__;JQ!!LLK065n_VXAQ!zP9K-68-_oPkaNWFZdbTYYnai85ggL4j3FhdqssLkim-RneBr2NqD6Ka4fu6yw-v$         '''
    cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud')
    cloudiness = cloud.reduceRegion(ee.Reducer.mean(),
                                    geometry=region,
                                    scale=30)
    image = image.set(cloudiness)
    return image

# Trigger the authentication flow
ee.Authenticate()

# Initialize the library
ee.Initialize()

#test

# bands = ['B1', 'B2','B3','B4','B5','B6_VCID_1','B6_VCID_2','B6_VCID_2','B8', 'BQA', 'BQA Bitmask']:

bbox =[(79.8096398872554,42.295437794411406),
(79.8096398872554,42.169352359125746),
(80.24634643022415,42.169352359125746),
(80.24634643022415,42.295437794411406)]

bands = ['B2','B3','B5']

start_date = datetime(1999,1,1)
end_date = datetime(2021,10,23)

region = ee.Geometry.Polygon(bbox)

collection = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').filterDate(start_date,end_date).filterBounds(region)

cloud_tol=30
collection= collection.map(algorithm=cloudscore).filter(ee.Filter.lt('cloud', cloud_tol))

#dates extracted from a different ipynb file

bad_dates = ['1999-12-16',
 '2000-01-17',
 '2000-08-12',
 '2001-01-03',
 '2001-10-02',
 '2001-12-21',
 '2002-02-23',
 '2003-03-14',
 '2003-12-27',
 '2004-04-01',
 '2004-10-10',
 '2004-11-11',
 '2004-11-27',
 '2005-03-03',
 '2005-08-10',
 '2005-11-30',
 '2005-12-16',
 '2006-12-19',
 '2007-01-04',
 '2007-10-19',
 '2009-01-09',
 '2009-01-25',
 '2009-03-14',
 '2010-10-27',
 '2010-11-12',
 '2010-11-28',
 '2010-12-14',
 '2010-12-30',
 '2011-10-30',
 '2013-11-20',
 '2013-12-06',
 '2014-10-22',
 '2014-11-23',
 '2015-03-15',
 '2015-06-03',
 '2015-11-26',
 '2016-02-14',
 '2016-03-01',
 '2016-12-14',
 '2017-02-16',
 '2017-12-17',
 '2020-02-09',
 '2020-03-12',
 '2020-10-22',
 '2020-11-07',
 '2021-01-10',
 '2021-10-09']

from datetime import date

# list_set = []
# for i in range(len(bad_dates)):   
#     datetime_object = date.fromisoformat(bad_dates[i])
#     start = datetime_object + timedelta(days=1)
#     end = datetime_object - timedelta(days=1)
    
#     list_set.append((str(start), str(end)))

# for i in range(len(list_set)):
#     collection = collection.filterfrom datetime import dat(ee.Filter.date(list_set[i][0], list_set[i][1]).Not()

collection = collection.select(bands)
collection_list = collection.toList(collection.size())


collection_size = collection_list.size().getInfo()
dates = geemap.image_dates(collection, date_format='YYYY-MM-dd').getInfo()


s_imgs = [] #to delete after
for i, date in enumerate(dates[:111]):

    if date in bad_dates:
        continue
        
    image = ee.Image(collection_list.get(i))


    NDSI_image = (image.select('B2').subtract(image.select('B5'))
         .divide(image.select('B5').add(image.select('B5'))))

    geemap.ee_export_image(NDSI_image, filename = "./Engilchek_glacier_{}.tif".format(date), scale = 100, region = region, file_per_band = False)
    #get dates here to filter
    s_imgs.append(NDSI_image)