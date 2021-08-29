import os
from google.cloud import storage
from collections import OrderedDict
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense
from sklearn.model_selection import train_test_split


BUCKET = 'gir-poc-cat-dog-1'
label_map = OrderedDict()
label_map['cat'] = [1, 0]
label_map['dog'] = [0, 1]


def download_from_bucket(bucket_name, source_file_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_file_name)
    blob.download_to_filename(destination_file_name)


def upload_to_bucket(bucket_name, destination_file_name, upload_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(upload_file_name)


class DeepClassification:

    def __init__(self, data):
        self.__X = list()
        self.__Y = list()
        self.__data = data

        self.__model = Sequential()
        self.__model.add(Dense(512, activation='relu'))
        self.__model.add(Dense(64, activation='relu'))
        self.__model.add(Dense(32, activation='relu'))
        self.__model.add(Dense(len(label_map), activation='softmax'))

        self.__model.compile(
            loss='categorical_crossentropy',
            metrics=['acc'],
            optimizer='adam'
        )

    def prepare_training_data(self):
        for td in self.__data:
            feature_vector = td[1]
            label = td[0]
            self.__X.append(feature_vector)
            self.__Y.append(label_map.get(label))

    def train(self):
        try:
            download_from_bucket(BUCKET, "model.h5", "model.h5")
            self.__model.load_weights("model.h5")
            os.remove("model.h5")
        except:
            pass
        x_train, x_val, y_train, y_val = train_test_split(self.__X, self.__Y, test_size=0.30)
        self.__model.fit(x_train,
                         y_train,
                         epochs=10,
                         batch_size=5,
                         validation_data=(x_val, y_val),
                         verbose=1)

        model_json = self.__model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        upload_to_bucket(BUCKET, "model.json", "model.json")
        os.remove("model.json")
        self.__model.save_weights("model.h5")
        upload_to_bucket(BUCKET, "model.h5", "model.h5")
        os.remove("model.h5")
