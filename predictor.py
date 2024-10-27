import tensorflow as tf
import keras
import sys
from keras.preprocessing import image
import numpy as np


class Predictor:
    def __init__(self) -> None:
        self.model = keras.models.load_model('trainedModelV1.keras')
        self.mapping = {"C":{np.int64(60)}, 
                        "A#":{np.int64(58)},
                        "D":{np.int64(62)},
                        "G":{np.int64(67)},
                        "D#":{np.int64(64), np.int64(63)},
                        "G#":{np.int64(68)},
                        "C#":{np.int64(61)},
                        "A":{np.int64(50), np.int64(69)},
                        "F#":{np.int64(66)}
                    }

    def getNote(self, spectrogramImagePath):
        i = []
        i.append(image.img_to_array(image.load_img(spectrogramImagePath, target_size=(372, 147, 3))))
        x_test = np.array(i) / 255
        prediction = self.model(x_test)
        return self.mapping[np.argmax(prediction[0]).item()]
    
    def getNotes(self, spectrogramImagePaths):
        i = []
        for path in spectrogramImagePaths:
            i.append(image.img_to_array(image.load_img(path, target_size=(372, 147, 3))))
        x_test = np.array(i) /255
        predictions = self.model(x_test)
        pred = []
        for i in predictions:
            pred.append(i.value())
        return pred
    
    