import ee 
import geemap
import os
import yaml
import numpy as np
import rasterio #for reading images
import matplotlib.pyplot as plt 
import pandas as pd
from argparse import ArgumentParser

from datetime import datetime, date

# def ifFlag(cloud_flag):
#     if cloud_flag:

# def cloudscore(image,region):
#     '''
#     Inner function for computing cloud score such that we can remove 
#     bad images from the landsat collections we download.
#     Implementation in javascript can be found of Google Earth Engine 
#     website under (landsat algorithms), translation to python by KH.
#     Further help from Nicholas Clinton at 
#     https://urldefense.com/v3/__https://gis.stackexchange.com/questions/252685/filter-landsat-images-base-on-cloud-cover-over-a-region-of-interest*5Cn__;JQ!!LLK065n_VXAQ!zP9K-68-_oPkaNWFZdbTYYnai85ggL4j3FhdqssLkim-RneBr2NqD6Ka4fu6yw-v$         '''
#     cloud = ee.Algorithms.Landsat.simpleCloudScore(image).select('cloud')
#     cloudiness = cloud.reduceRegion(ee.Reducer.mean(),
#                                     geometry=region,
#                                     scale=30)
#     image = image.set(cloudiness)
#     return image

class imageCollection:
    def __init__(self, image_collection:str, dates: list, regional_boundaries:list, bands:list, **kwargs) -> ee.ImageCollection:
        """
            BALLS DUDE
        """        
        start_date = datetime(*dates["start"])
        end_date = datetime(*dates["end"])
        region = ee.Geometry.Polygon(regional_boundaries)

        try:
            collection = ee.ImageCollection(image_collection).filterDate(start_date,end_date).filterBounds(region).select(bands)
            self.collection = collection
            self.bands = bands
        except TypeError as e:
            raise(e)

    def download(self, picture_path):
        collection_length = self.collection.size()
        collection_list = self.collection.toList(collection_length)

        for index, date in enumerate(geemap.image_dates(self.collection, date_format="YYY-MM-dd").getInfo()):
            image = ee.Image(collection_list.get(index)).select(self.bands)
            NDSI_image = (image.select('B2').subtract(image.select('B5')).divide(image.select('B5').add(image.select('B5'))))
            geemap.ee_export_image(image, filename = f"{picture_path}/full/Engilchek_glacier_{date}.tif", scale = 300, file_per_band = False)
            geemap.ee_export_image(NDSI_image, filename = f"{picture_path}/ndsi/Engilchek_glacier_{date}.tif", scale = 100, file_per_band = False)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config", help="The download config file")

    args = parser.parse_args()
    config_file = args.config

    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.Loader)

    # Trigger the authentication flow
    ee.Authenticate()

    # Initialize the library
    ee.Initialize()
    
    test = imageCollection(**config)
    test.download(r"C:\Users\marke\Documents\DSC180A-Q1\testing_data")
