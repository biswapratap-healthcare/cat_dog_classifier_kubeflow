import argparse
import os
import cv2
import pickle
import logging
import numpy as np
from rest_client import fetch
from google.cloud import storage
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


def upload_to_bucket(bucket_name, destination_file_name, upload_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_file_name)
    blob.upload_from_filename(upload_file_name)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--project',
                        type=str,
                        required=True,
                        help='The GCP project to run the dataflow job.')
    parser.add_argument('--bucket',
                        type=str,
                        required=True,
                        help='Bucket to store outputs.')
    parser.add_argument('--mode',
                        choices=['local', 'cloud'],
                        help='whether to run the job locally or in Cloud Dataflow.')
    parser.add_argument('--handle',
                        type=str,
                        required=True,
                        help='The annotation service handle.')

    args = parser.parse_args()
    logging.info("Project --> " + str(args.project) + ".")
    logging.info("Bucket --> " + str(args.bucket) + ".")
    logging.info("Mode --> " + str(args.mode) + ".")
    logging.info("Handle --> " + str(args.handle) + ".")

    DESTINATION_FILENAME = 'td.pkl'
    BUCKET = 'gir-poc-cat-dog-1'

    training_data = list()
    model = init()
    training_image_data = fetch(args.handle)
    logging.info("Found " + str(len(training_image_data)) + " training entries.")
    for td in training_image_data:
        np_arr = np.fromstring(td[1], np.uint8)
        img_np = cv2.imdecode(np_arr, flags=1)
        features = get_features(model, img_np)
        training_data.append((td[0], features))
    logging.info("Collected all the training features.")
    with open(DESTINATION_FILENAME, 'wb') as f:
        pickle.dump(training_data, f)
    upload_to_bucket(BUCKET, DESTINATION_FILENAME, DESTINATION_FILENAME)
    logging.info("Uploaded training data to the bucket " + BUCKET + ".")
    os.remove(DESTINATION_FILENAME)

    with open('bucket.txt', 'w') as f:
        f.write("Hello from Feature Extraction Microservice")
    upload_to_bucket(args.bucket, 'bucket.txt', 'bucket.txt')
    os.remove('bucket.txt')

    with open("/output.txt", "w") as output_file:
        output_file.write("This is the content of the output.txt file in Feature Extraction microservice.")
        print("Done!")
