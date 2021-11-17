import os,time
import rasterio #for reading images
import napari
import multiprocessing as mlt
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

from matplotlib import path

directory = os.path.join(os.getcwd(), "ee_data")

def run_napari(img):
    viewer = napari.view_image(img)
    napari.run()
    return viewer

def get_mask(fileName):
    with rasterio.open('ee_data//Engilchek_2001-10-02.tif') as src:
        img = src.read() 
    napariConcurrent = mlt.Process(target=run_napari, args=img)
    viewer = napariConcurrent.get()
    input("Press ENTER after annotation")
    while True:
        
        try:

            path_dimention = get_polygon_path(viewer)
            mask = containsWithin(path_dimention, img)
        except KeyError:
            print("Annotate on UI")
            time.sleep(5)
        break
    return mask
    

def get_polygon_path(viewer):
    ts = {str.lower(layer.name):layer.data for layer in viewer.layers}
    test = np.delete(ts["shapes"][0], (0), axis=1)
    return test

    
def containsWithin(path_dimention, img):
    glacier = path.Path(path_dimention)
    indices = np.where(np.all(img == img, axis=0))
    pixels = np.array(list(zip(indices[0],indices[1])))
#     return pixels
    return glacier.contains_points(pixels).reshape(img.shape[1:])


def main():
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1] == ".tif":
                test = get_mask(file)


if __name__ == "__main__":
    main()

