import argparse
import logging
import os
import pickle
from train import DeepClassification, download_from_bucket, BUCKET

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--content',
                        type=str,
                        required=True,
                        help='The content of the file.')
    args = parser.parse_args()
    logging.info(args.content)
    SOURCE_FILENAME = 'td.pkl'

    download_from_bucket(BUCKET, SOURCE_FILENAME, SOURCE_FILENAME)
    logging.info("Downloaded training data from bucket.")
    with open(SOURCE_FILENAME, 'rb') as f:
        training_data = pickle.load(f)
    os.remove(SOURCE_FILENAME)
    logging.info("Found " + str(len(training_data)) + " training entries.")
    model = DeepClassification(training_data)
    logging.info("Built deep classification model.")
    model.prepare_training_data()
    logging.info("Prepared data for training.")
    model.train()
    logging.info("Training completed.")
