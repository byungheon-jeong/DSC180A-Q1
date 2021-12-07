import yaml,pickle
import sklearn as sk
import numpy as np
import pandas as pd
import rasterio, os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from argparse import ArgumentParser


def runNapari(img_path, full_img_path):
    with rasterio.open(img_path) as src:
        img = src.read()
    
    with rasterio.open(full_img_path) as src:
        img_full = src.read()

    viewer = napari.view_image(img, show=False)
    return viewer, img, img_full


def loadAndTest(full_directory,rgb_directory, raw_directory, label_directory, trained_model):
    
    viewer,ndsi,full = runNapari(rgb_directory,full_directory)
    e_dims = full.shape
    print(e_dims)
    full_band_img = np.rollaxis(full.reshape(9,e_dims[1]*e_dims[2]),0,2)

    # filtered_data = [bal if np.sum(np.abs(bal)) < 255*9 else [0]*9 for bal in full_band_img]
    try:
        prediction = trained_model.predict(full_band_img)
    except ValueError as e:
        raise e

    prediction = prediction.reshape(e_dims[1],e_dims[2])
    # np.count_nonzero(filtered_data.reshape(9,145,363) != full)
    display_dims = prediction.shape
    img_coordinates = np.array(list(zip(np.arange(0,display_dims[0]),np.arange(0,display_dims[1]))))
    
    ice_indexes = np.where(prediction == "Ice")
    non_ice_indexes = np.where(prediction == "Not Ice")
    ice_coordinates = list(zip(ice_indexes[0],ice_indexes[1]))
    non_ice_coordinates = list(zip(non_ice_indexes[0], non_ice_indexes[1]))
    viewer = napari.view_image(ndsi,show=True)

    viewer.screenshot(raw_directory)
    
    viewer.add_points(ice_coordinates,face_color="red",edge_color ="red",size=1,  opacity=0.7, name="Ice")
    viewer.add_points(non_ice_coordinates,face_color="blue",edge_color ="blue",size=1, opacity=0,name="Not Ice")

    viewer.screenshot(label_directory)


def train(training_data_path:str, testing_data_path:str, labeled_pictures_path:str, model_output_path:str, pictures_to_be_labeled_path:str, do_labeling:bool, **kwargs):
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

    model = None
    model_f1= np.array([])
    model_accuracy = np.array([])

    for i in np.arange(50):
        fclf = RandomForestClassifier(max_depth=20, n_estimators=100, max_features=1)
        fclf.fit(X_train, y_train) 
        accuracy_score = fclf.score(X_test, y_test)
        f1_score = sk.metrics.f1_score(y_test,fclf.predict(X_test), pos_label='Not Ice')
        
        model_accuracy = np.append(model_accuracy,accuracy_score)
        model_f1 = np.append(model_f1, f1_score)

        if accuracy_score >= np.max(model_accuracy) and f1_score >= np.max(model_f1):
            model = fclf   

        print(i+1)
    
    accuracy_score = model.score(X_test, y_test)
    f1_score = sk.metrics.f1_score(y_test,model.predict(X_test), pos_label='Not Ice')
    
    mean_accuracy = np.mean(model_accuracy)
    mean_f1 = np.mean(model_f1)

    print(f"Random Forest accuracy: {accuracy_score} /n Random Forest f1_score: {f1_score}")

    print(f"Averaged Random Forest accuracy: {mean_accuracy} /n Averaged Random Forest f1_score: {mean_f1}")
    
    # pickle.dump(model, model_output_path)
    s = pickle.dumps(model)
    

    if do_labeling:
        import napari
        files = os.listdir(os.path.join(pictures_to_be_labeled_path,"rgb"))
        for file in files:
            file_name = file.split(".")[0]
            full_directory = os.path.join(os.path.join(pictures_to_be_labeled_path, "full"),file)
            rgb_directory = os.path.join(os.path.join(pictures_to_be_labeled_path, "rgb"),file)

            raw_directory = os.path.join(os.path.join(os.path.join(labeled_pictures_path, "raw")),file_name+ r".png")
            label_directory = os.path.join(os.path.join(os.path.join(labeled_pictures_path, "labeled")),file_name+ r".png")

            try:
                loadAndTest(full_directory, rgb_directory, raw_directory, label_directory, model)
            except ValueError:
                continue

            print(full_directory)
    
    return fclf


def main():
    parser = ArgumentParser()
    parser.add_argument("--config", help="The download config file")

    args = parser.parse_args()
    config_file = args.config

    with open(config_file) as config_file:
        cfg = yaml.load(config_file,Loader=yaml.Loader)
    
    model = train(**cfg)
    
    # Model saving


if __name__ == "__main__":
    main()