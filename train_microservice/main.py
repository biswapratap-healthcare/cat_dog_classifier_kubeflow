import logging
import os
import pickle
from train import DeepClassification, download_from_bucket, BUCKET

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    SOURCE_FILENAME = 'td.pkl'

    download_from_bucket(BUCKET, SOURCE_FILENAME, SOURCE_FILENAME)
    with open(SOURCE_FILENAME, 'rb') as f:
        training_data = pickle.load(f)
    os.remove(SOURCE_FILENAME)
    model = DeepClassification(training_data)
    model.prepare_training_data()
    model.train()
