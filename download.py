import ee, os
import geemap
from datetime import datetime
import numpy as np
import rasterio #for reading images
import matplotlib.pyplot as plt 
import pandas as pd


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

def band_select(bands):
    
    bbox =[(79.8096398872554,42.295437794411406),
(79.8096398872554,42.169352359125746),
(80.24634643022415,42.169352359125746),
(80.24634643022415,42.295437794411406)]

    start_date = datetime(1999,1,1)
    end_date = datetime(2003,1,1)

    region = ee.Geometry.Polygon(bbox)

    collection = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA').filterDate(start_date,end_date).filterBounds(region)
    
    collection = collection.select(bands)
    collection_list = collection.toList(collection.size())

    # type(collection_list)
    collection_size = collection_list.size().getInfo()
    dates = geemap.image_dates(collection, date_format='YYYY-MM-dd').getInfo()
    glacier_name = "Engilchek"

#     list_a = []
    for i, date in enumerate(dates):
        subdir = "ee_data"
        image = ee.Image(collection_list.get(i))
        geemap.ee_export_image(image, filename = os.path.join("ee_data", "{}_{}.tif".format(glacier_name,date)), scale = 100, region = region, file_per_band = False)
    #     list_a.append(filename)
    image_names = []
    for i, date in enumerate(dates):
        image_names.append(os.path.join("ee_data", "{}_{}.tif".format(glacier_name,date)))
    return dates, region, bbox, image_names


def main():
    ee.Authenticate()
    ee.Initialize()
    dates, region, bbox, image_names = band_select(['B1','B2','B3'])

if __name__ == "__main()__":
    main()