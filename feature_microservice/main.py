import cv2
import pickle
import numpy as np
from rest_client import fetch
from tensorflow.keras import Model
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input


def init():
    _model = VGG16(include_top=False)
    _model.layers.pop()
    _model = Model(inputs=_model.inputs, outputs=_model.layers[-1].output)
    return _model


def get_features(_model, image):
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    if _model:
        features = _model.predict(image)
        features = features.flatten().tolist()
    else:
        features = list()
    return features


if __name__ == "__main__":
    training_data = list()
    model = init()
    training_image_data = fetch()
    for td in training_image_data:
        np_arr = np.fromstring(td[1], np.uint8)
        img_np = cv2.imdecode(np_arr, flags=1)
        features = get_features(model, img_np)
        training_data.append((td[0], features))
    with open('td.pkl', 'wb') as f:
        pickle.dump(training_data, f)
