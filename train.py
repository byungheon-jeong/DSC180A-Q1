import yaml
import sklearn as sk
import numpy as np
import pandas as pd
import rasterio, os, napari

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", help="The download config file")

    args = parser.parse_args()
    config_file = args.config

    with open(config_file) as config_file:
        cfg = yaml.load(config_file,Loader=yaml.Loader)
    train(**cfg)


def runNapari(img_path, full_img_path):
    with rasterio.open(img_path) as src:
        img = src.read()
    
    with rasterio.open(full_img_path) as src:
        img_full = src.read()

    viewer = napari.view_image(img, show=False)
    return viewer, img, img_full


def loadAndTest(full_directory,rgb_directory, label_directory, trained_model):
    
    viewer,ndsi,full = runNapari(rgb_directory,full_directory)
    e_dims = full.shape
    print(e_dims)
    testbals = np.rollaxis(full.reshape(9,e_dims[1]*e_dims[2]),0,2)
    print(testbals)
    prediction = trained_model.predict(testbals)

    prediction = prediction.reshape(e_dims[1],e_dims[2])
    # np.count_nonzero(testbals.reshape(9,145,363) != full)
    display_dims = prediction.shape
    img_coordinates = np.array(list(zip(np.arange(0,display_dims[0]),np.arange(0,display_dims[1]))))
    
    ice_indexes = np.where(prediction == "Ice")
    non_ice_indexes = np.where(prediction == "Not Ice")
    ice_coordinates = list(zip(ice_indexes[0],ice_indexes[1]))
    non_ice_coordinates = list(zip(non_ice_indexes[0], non_ice_indexes[1]))
    
    viewer = napari.view_image(ndsi,show=True)
    viewer.add_points(ice_coordinates,face_color="red",edge_color ="red",size=1, name="Ice")
    viewer.add_points(non_ice_coordinates,face_color="blue",edge_color ="blue",size=1, opacity=0,name="Not Ice")
    viewer.screenshot(label_directory)


def train(training_data_path:str, testing_data_path:str, model_output_path:str, labeled_pictures_path:str, pictures_to_be_labeled_path:str, **kwargs):
    with open(training_data_path, "rb") as file:
        data = np.load(file)
    with open(testing_data_path, "rb") as file:
        labels = np.load(file)

    filtered = [[point[0],point[1]] for point in zip(data, labels) if np.sum(np.abs(point[0])) < 255*9]
    data, label = zip(*filtered)
    X_train, X_test, y_train, y_test = train_test_split(data,label, test_size=0.2)

    a = pd.Series(y_train).value_counts()
    b = pd.Series(y_test).value_counts()

    print(a)
    print("\n")
    print(b)

    fclf = RandomForestClassifier(max_depth=20, n_estimators=100, max_features=1)
    # fclf = RandomForestClassifier(max_depth=40, n_estimators=100, max_features=1)

    fclf.fit(X_train, y_train)
    
    accuracy_score = fclf.score(X_test, y_test)
    f1_score = sk.metrics.f1_score(y_test,fclf.predict(X_test), pos_label='Not Ice')

    print(f"Random Forest accuracy: {accuracy_score} /n Random Forest f1_score: {f1_score}")

    files = os.listdir(os.path.join(pictures_to_be_labeled_path,"rgb"))
    for file in files:
        file_name = file.split(".")[0]
        full_directory = os.path.join(os.path.join(pictures_to_be_labeled_path, "full"),file)
        rgb_directory = os.path.join(os.path.join(pictures_to_be_labeled_path, "rgb"),file)
        label_directory = os.path.join(os.path.join(labeled_pictures_path),file_name+ r".png")
        loadAndTest(full_directory, rgb_directory, label_directory, fclf)
        print(full_directory)


if __name__ == "__main__":
    main()