import yaml, unittest, os

import run_annotation

class Test_MultiLayers(unittest.TestCase):
    def setUp(self):
        config_file = r"C:\Users\marke\Documents\DSC180A-Q1\config\test.yml"
        with open(config_file) as config_file:
            cfg = yaml.load(config_file,Loader=yaml.Loader)
        image_path = cfg["image_path"]
        full_image_path = cfg["full_image_path"]
        viewer,img, img_full = run_annotation.runNapari(image_path,full_image_path)

        while True:
            response = input("Press Enter after Labeling or input \"SKIP\" in order to skip image:\n")
            if response == "SKIP":
                print("WHAT?")
            try:
                self.viewer = viewer
                return None
            except Exception as e:
                print(e)


    def test_getPolygonMasks(self):
        old_paths = run_annotation.getPolygonMasks(self.viewer)
        new_paths = run_annotation.getPolygonMasks_new(self.viewer)
        self.assertEqual(old_paths, new_paths)
    


if __name__ == "__main__":
    unittest.main()