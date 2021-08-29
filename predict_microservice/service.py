import os
import cv2
import shutil
import tempfile

from PIL import Image
from waitress import serve
from flask_cors import CORS
from flask import Flask
from flask_restplus import Resource, Api, reqparse

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from classifier import DeepClassification
from utils import init, get_features


def store_and_verify_file(file_from_request, work_dir):
    if not file_from_request.filename:
        return -1, 'Empty file part provided!'
    try:
        file_path = os.path.join(work_dir, secure_filename(file_from_request.filename))
        if os.path.exists(file_path) is False:
            file_from_request.save(file_path)
        return 0, file_path
    except Exception as ex:
        return -1, str(ex)


def create_app():
    app = Flask("foo", instance_relative_config=True)

    api = Api(
        app,
        version='1.0.0',
        title='Prediction App',
        description='Prediction App',
        default='Prediction App',
        default_label=''
    )

    CORS(app)

    predict_parser = reqparse.RequestParser()
    predict_parser.add_argument('file',
                                location='files',
                                type=FileStorage,
                                help='The image to classify.',
                                required=True)

    @api.route('/predict')
    @api.expect(predict_parser)
    class PredictionService(Resource):
        @api.expect(predict_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = predict_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404
            download_dir = None
            try:
                file_from_request = args['file']
                download_dir = tempfile.mkdtemp()
                ret, f = store_and_verify_file(file_from_request, download_dir)
                if ret == 0:
                    f_split = os.path.basename(f).split('.')
                    new_name = '_'.join(f_split[:-1]) + '_converted.' + f_split[-1]
                    converted_image = os.path.join(download_dir, new_name)
                    classifier = DeepClassification()
                    im = Image.open(f).convert('LA')
                    new_size = (512, 512)
                    im = im.resize(new_size)
                    im = im.convert('RGB')
                    im.save(converted_image)
                    im = cv2.imread(converted_image, flags=1)
                    model = init()
                    features = get_features(model, im)
                    result = classifier.predict(features)
                    rv = dict()
                    rv['result'] = str(result)
                    return rv, 200
            except Exception as e:
                if download_dir:
                    shutil.rmtree(download_dir)
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    return app


if __name__ == "__main__":
    serve(create_app(), host='0.0.0.0', port=8000, threads=20)
