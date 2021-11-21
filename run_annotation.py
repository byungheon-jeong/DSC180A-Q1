import os,time, pickle, re
import rasterio #for reading images
import napari

import multiprocessing as mlt
import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd

from matplotlib import path

directory = os.path.join(os.getcwd(), "ee_data")

def runNapari(img_path):
    with rasterio.open(img_path) as src:
        img = src.read()
   
    viewer = napari.view_image(img)
    return viewer, img


def getPolygonMasks(viewer)-> list:
    ice_layers = {str.lower(layer.name):layer.data for layer in viewer.layers if re.match("^ice.*", str.lower(layer.name))}
    non_ice_layers= {str.lower(layer.name):layer.data for layer in viewer.layers if re.match("^not.*ice.*", str.lower(layer.name))}
    ice_coordinate_list, non_ice_coordinate_list = list(),list()

    for i, (x,y) in enumerate(ice_layers.items()):
        ice_coordinate_list.append(np.delete(y[0],(0),axis=1))
    for i, (x,y) in enumerate(non_ice_layers.items()):
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

    ice_coordinates = list(zip(iceMask[0],iceMask[1]))
    non_ice_coordinates = list(zip(nonIceMask[0],nonIceMask[1]))    
    iceData,nonIceData=list(),list()
    for (x,y) in ice_coordinates:
        iceData.append(np.rollaxis(img,0,3)[x,y,:])
    for (x,y) in non_ice_coordinates:
        nonIceData.append(np.rollaxis(img,0,3)[x,y,:])
    return np.array(iceData), np.array(nonIceData)


def getTrainingData(iceData, nonIceData):
    data,labels = np.array([]), np.array([])

    iceLabels = np.array(["Ice"]*iceData.shape[0])
    nonIceLabels = np.array(["Not Ice"]*nonIceData.shape[0])
    data = np.vstack((iceData, nonIceData))
    labels = np.hstack((iceLabels, nonIceLabels))

    return data, labels


def testPixelMask(img,paths,viewer):
    iceMask = np.where(np.logical_or.reduce([containsWithin(path,img) for path in paths["ice"]]))
    nonIceMask = np.where(np.logical_or.reduce([containsWithin(path,img) for path in paths["non_ice"]]))

    ice_coordinates = list(zip(iceMask[0],iceMask[1]))
    non_ice_coordinates = list(zip(nonIceMask[0],nonIceMask[1]))    

    viewer.add_points(ice_coordinates,face_color="red",edge_color ="red",size=1)
    viewer.add_points(non_ice_coordinates,face_color="blue",edge_color ="blue",size=1)
    
    return ice_coordinates,non_ice_coordinates


def loadCheckpoint(directory):
    logpath = os.path.join(directory, "imgAnnotatedData.pickle")
    try:
        imageList = pickle.load(open(logpath,"rb"))
    except (OSError, IOError) as e:
        imageList = []
        pickle.dump(imageList, open(logpath,"wb"))

    data, labels = np.empty([0,3]),np.empty([0])
    if os.path.exists(os.path.join(directory,"data.npy")) and os.path.exists(os.path.join(directory,"labels.npy")):
        with open(os.path.join(directory, "data.npy")) as f:
            data= np.load(f)
        with open(os.path.join(directory, "labels.npy")) as f:
            labels=np.load(f)

    return imageList, data, labels


def updateLog(imageList,directory):
    logpath = os.path.join(directory, "imgAnnotatedData.pickle")
    pickle.dump(imageList, open(logpath,"wb"))


def runTestsAndLog(img, paths, viewer, annotated_list,image_file,directory):
    testPixelMask(img, paths, viewer)

    annotated_list.append(image_file)
    updateLog(annotated_list, directory)
    input("Input ENTER after checking RB pixels")


def updateArraysAndSave(data,image_data,labels,image_labels,directory):
    data = np.vstack((data,image_data))
    labels = np.hstack((labels, image_labels))

    with open(os.path.join(directory, "data.npy"),"wb") as f:
        np.save(f, data)
    with open(os.path.join(directory, "label.npy"), "wb") as f:
        np.save(f, labels)

def test():
    try:
        test_image_path = input("Input the image to test:\n")
        with rasterio.open(test_image_path) as src:
            img = src.read()
    except:
        raise ValueError("YOU MUST INPUT PATH TO .TIF IMAGE")
    test_viewer = runNapari(img)
    # napari_process = mlt.Process(target=napari.run())
    # napari_process.run()xs

    while True:
        input("Press Enter after Labeling")
        try:    
            paths = getPolygonMasks(test_viewer)
            test_mask = getPixelMask(img,paths)
            testPixelMask(img, paths, test_viewer)
            break
        except:
            print("Label the image")
    return test_mask


def main():
    # directory = input("Enter Directory:\n")
    directory = r"C:\Users\marke\Documents\DSC180A-Q1\ee_data"
    annotated_list, data, labels = loadCheckpoint(directory)

    for root, dirs, files in os.walk(directory):            
        for image_file in files:
            image_path = os.path.join(directory, image_file)
            print(image_path)
            if os.path.splitext(image_path)[1] == ".tif" and image_file not in annotated_list:
                viewer,img = runNapari(image_path)
                while True:
                    response = input("Press Enter after Labeling or input \"SKIP\" in order to skip image:\n")
                    if response == "SKIP":
                        viewer.close()
                        annotated_list.append(image_file)
                        updateLog(annotated_list, directory)
                        break
                    try:    
                        paths = getPolygonMasks(viewer)
                        ice,not_ice = getPixelMask(img,paths)
                        image_data,image_labels = getTrainingData(ice,not_ice)
                        
                        # data = np.vstack((data,image_data))
                        # labels = np.hstack((labels, image_labels))
                        
                        updateArraysAndSave(data,image_data,labels,image_labels,directory)
                        runTestsAndLog(img, paths, viewer, annotated_list,image_file,directory)
                        # testPixelMask(img, paths, viewer)  
                        # annotated_list.append(image_file)
                        # updateLog(annotated_list, directory)
                        # input("Input ENTER after checking RB pixels")

                        viewer.close()
                        break
                    except Exception as e:
                        print(f"{e} \nLabel the image")
        dftest = pd.DataFrame(data)
        dftest = dftest.assign(pd.Series(labels))
                # return test_mask

    

if __name__ == "__main__":

    main()
    # test()
