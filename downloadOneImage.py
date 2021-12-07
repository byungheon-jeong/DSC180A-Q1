import ee 
import geemap
import os,shutil
import yaml
import numpy as np
import rasterio #for reading images
import matplotlib.pyplot as plt 
import pandas as pd
from argparse import ArgumentParser

from datetime import datetime, date

class imageCollection:
    def __init__(self, image_collection:str, dates: list, regional_boundaries:list, bands:list, **kwargs):

        rrf = regional_boundaries
        bbox = [(79.8096398872554,42.295437794411406),
        (79.8096398872554,42.169352359125746),
        (80.24634643022415,42.169352359125746),
        (80.24634643022415,42.295437794411406)]

        start_date = datetime(*dates["start"])
        end_date = datetime(*dates["end"])
        region = ee.Geometry.Polygon(regional_boundaries)

        try:
            collection_hold = ee.ImageCollection(image_collection).filterDate(start_date,end_date).filterBounds(region)
            collection_hold = collection_hold.select(bands)
            self.collectionz = collection_hold
            self.bands = bands
            self.region = region
            self.blackout = [blackout_date for blackout_date in kwargs["blackout_dates"]] 
        except TypeError as e:
            raise(e)
        

    # def ifFlag(cloud_flag, func):
    #     if cloud_flag:
    #         return func

    # @ifFlag()
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

    def download(self, picture_path, glacier_name):

        collection_length = self.collectionz.size()
        collection_list = self.collectionz.toList(collection_length)

        if os.path.lexists(picture_path):
            shutil.rmtree(picture_path)
        
        os.mkdir(picture_path)
        os.mkdir(os.path.join(picture_path,"full"))
        os.mkdir(os.path.join(picture_path,"ndsi"))
        os.mkdir(os.path.join(picture_path,"rgb"))

        dates = geemap.image_dates(self.collectionz, date_format="YYYY-MM-dd").getInfo()
        dates = [date for date in dates if date not in self.blackout]
        region = self.region


        for index, date in enumerate(dates):
            image = ee.Image(collection_list.get(index)).select(self.bands)
            NDSI_image = (image.select('B2').subtract(image.select('B5')).divide(image.select('B5').add(image.select('B5'))))
            rgb = image.select(["B1","B2","B3"])
        
            # geemap.ee_export_image(image, filename = f"{picture_path}/full/Engilchek_glacier_{date}.tif", scale = 280, file_per_band = False)
            # geemap.ee_export_image(rgb, filename = f"{picture_path}/ndsi/Engilchek_glacier_{date}.tif", scale = 100, file_per_band = False)
            geemap.ee_export_image(rgb, filename = f"{picture_path}/rgb/{glacier_name}_{date}.tif", scale = 40, region=region, file_per_band = False)
            geemap.ee_export_image(image, filename = f"{picture_path}/full/{glacier_name}_{date}.tif", scale = 40, region=region, file_per_band = False)
            geemap.ee_export_image(NDSI_image, filename = f"{picture_path}/ndsi/{glacier_name}_{date}.tif", scale = 40, region=region, file_per_band = False)

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
    test.download(r".\testing_data", config["glacier_name"])
