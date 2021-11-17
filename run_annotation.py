import os,time
import rasterio #for reading images
import napari
import re
import multiprocessing as mlt
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

from matplotlib import path

directory = os.path.join(os.getcwd(), "ee_data")

def runNapari(img):

    viewer = napari.view_image(img)
    napari.run()
    return viewer

def getMap(fileName):

    with rasterio.open('ee_data//Engilchek_2001-10-02.tif') as src:
        img = src.read() 
    napariConcurrent = mlt.Process(target=runNapari, args=img)
    viewer = napariConcurrent.get()
    input("Press ENTER after annotation")
    while True:
        try:
            path_dimention = getPolygonMasks(viewer)
            break
        except KeyError:
            print("Annotate on UI")
            time.sleep(5)

    paths = containsWithin(path_dimention, img)
    ice_contain_map = [containsWithin(path,img) for path in paths["ice"]]
    non_ice_contain_map = [containsWithin(path,img) for path in paths["non_ice"]]
    return ice_contain_map,non_ice_contain_map
    
def getPolygonMasks(viewer)-> list:
    
    ice_layers = {str.lower(layer.name):layer.data for layer in viewer.layers if re.match("^ice.*", str.lower(layer.name))}
    non_ice_layers= {str.lower(layer.name):layer.data for layer in viewer.layers if re.match("^not_ice.*", str.lower(layer.name))}
    ice_coordinate_list, non_ice_coordinate_list = list(),list()

    for i, (x,y) in enumerate(ice_layers.items()):
        ice_coordinate_list.append(np.delete(y[0],(0),axis=1))
    for i, (x,y) in enumerate(ice_layers.items()):
        non_ice_coordinate_list.append(np.delete(y[0],(0),axis=1))

    path_results = {"ice":ice_coordinate_list, "non_ice":non_ice_coordinate_list}
    return path_results
    
def containsWithin(path_dimention, img):

    glacier = path.Path(path_dimention)
    indices = np.where(np.all(img == img, axis=0))
    pixels = np.array(list(zip(indices[0],indices[1])))
#     return pixels
    return glacier.contains_points(pixels).reshape(img.shape[1:])


def getPixelMask(img,paths):
    iceMask = np.where(np.logical_or.reduce([containsWithin(path,img) for path in paths["ice"]]))
    nonIceMask = np.where(np.logical_or.reduce([containsWithin(path,img) for path in paths["non_ice"]]))
    ice_coordinates = list(zip(np.where(iceMask)[0],np.where(iceMask)[1]))
    non_ice_coordinates = list(zip(np.where(nonIceMask)[0],np.where(nonIceMask)[1]))

    iceData,nonIceData=list(),list()
    for (x,y) in ice_coordinates:
        iceData.append(np.rollaxis(img,0,3)[x,y,:])
    for (x,y) in non_ice_coordinates:
        nonIceData.append(np.rollaxis(img,0,3)[x,y,:])
    return np.array(iceData), np.array(nonIceData)

def main():
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] == ".tif":
                test = getMap(file)
    

if __name__ == "__main__":
    main()

