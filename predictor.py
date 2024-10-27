import tensorflow as tf
import keras
import sys
from keras.preprocessing import image
import numpy as np


class Predictor:
    def __init__(self) -> None:
        self.model = keras.models.load_model('trainedModelV1.keras')
        self.mapping = {"50" : "a", "58" : "as", "59" : "b", "60" : "c",
                        "61" : "cs", "62": "d", "63" : "ds", "64" : "e",
                        "65" : "f", "66" : "fs", "67" : "g", "68" : "gs"}

    def getNote(self, spectrogramImagePath):
        i = []
        i.append(image.img_to_array(image.load_img(spectrogramImagePath, target_size=(372, 147, 3))))
        x_test = np.array(i) / 255
        prediction = self.model(x_test)
        try:
            return self.mapping[np.argmax(prediction[0]).item()]
        except KeyError:
            return ""
        
    def getNotes(self, spectrogramImagePaths):
        i = []
        for path in spectrogramImagePaths:
            i.append(image.img_to_array(image.load_img(path, target_size=(372, 147, 3))))
        x_test = np.array(i) /255
        predictions = self.model(x_test)
        pred = []
        for i in predictions:
            try:
                pred.append(self.mapping[str(np.argmax(i).item())])
            except KeyError:
                pred.append("")
        return pred
    
    
