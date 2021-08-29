import os

import numpy as np
from google.cloud import storage
from collections import OrderedDict
from tensorflow.python.keras.models import model_from_json

BUCKET = 'gir-poc-cat-dog-1'
label_map = OrderedDict()
label_map['cat'] = [1, 0]
label_map['dog'] = [0, 1]
label_keys = list(label_map.keys())


def download_from_bucket(bucket_name, source_file_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_file_name)
    blob.download_to_filename(destination_file_name)


class DeepClassification:

    def __init__(self):
        self.cache = True
        if not os.path.exists('model.json'):
            download_from_bucket(BUCKET, 'model.json', 'model.json')
        if not os.path.exists('model.h5'):
            download_from_bucket(BUCKET, 'model.h5', 'model.h5')
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.loaded_model = model_from_json(loaded_model_json)
        self.loaded_model.load_weights("model.h5")
        if not self.cache:
            os.remove('model.json')
            os.remove('model.h5')

    @staticmethod
    def __get_predicted_labels(r):
        result = list()
        r = r[0]
        for idx, p in enumerate(r):
            p = p * 100
            p = np.round(p, 2)
            result.append((label_keys[idx], p))
        result = sorted(result, key=lambda x: x[1], reverse=True)[0:2]
        return result

    def predict(self, x):
        x = [np.array(x)]
        x = np.array(x)
        r = self.loaded_model.predict(x)
        result = self.__get_predicted_labels(r)
        return result[0]
