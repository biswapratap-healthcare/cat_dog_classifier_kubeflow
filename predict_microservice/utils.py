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
        _features = _model.predict(image)
        _features = _features.flatten().tolist()
    else:
        _features = list()
    return _features
