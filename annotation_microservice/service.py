import os
import shutil
import tempfile
import time
import zipfile

from waitress import serve
from flask_cors import CORS
from flask import Flask
from flask_restplus import Resource, Api, reqparse

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from db_driver import if_table_exists, create_table, insert_data


def current_milli_time():
    return round(time.time() * 1000)


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


def init():
    if not if_table_exists():
        create_table()


def create_app():
    init()
    app = Flask("foo", instance_relative_config=True)

    api = Api(
        app,
        version='1.0.0',
        title='Annotation App',
        description='Annotation App',
        default='Annotation App',
        default_label=''
    )

    CORS(app)

    upload_parser = reqparse.RequestParser()
    upload_parser.add_argument('file',
                               location='files',
                               type=FileStorage,
                               help='The zip of all the dog and cat images',
                               required=True)

    @api.route('/upload')
    @api.expect(upload_parser)
    class UploadService(Resource):
        @api.expect(upload_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = upload_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404
            extract_dir = None
            download_dir = None
            try:
                with_errors = 0
                file_from_request = args['file']
                extract_dir = tempfile.mkdtemp()
                download_dir = tempfile.mkdtemp()
                ret, file_path = store_and_verify_file(file_from_request, download_dir)
                if ret == 0:
                    zip_handle = zipfile.ZipFile(file_path, "r")
                    zip_handle.extractall(path=extract_dir)
                    zip_handle.close()
                    data_dir = os.path.join(extract_dir, 'data')
                    _dirs = os.listdir(data_dir)
                    if set(_dirs).issubset(['cat', 'dog']):
                        cat_dir = os.path.join(data_dir, 'cat')
                        dog_dir = os.path.join(data_dir, 'dog')
                        cat_files = os.listdir(cat_dir)
                        dog_files = os.listdir(dog_dir)
                        for cat_file in cat_files:
                            _id = str(current_milli_time())
                            label = 'cat'
                            image = os.path.join(cat_dir, cat_file)
                            ret, status = insert_data(_id, label, image)
                            if ret != 0:
                                with_errors = 1
                                print(status)
                        for dog_file in dog_files:
                            _id = str(current_milli_time())
                            label = 'dog'
                            image = os.path.join(dog_dir, dog_file)
                            ret, status = insert_data(_id, label, image)
                            if ret != 0:
                                with_errors = 1
                                print(status)
                rv = dict()
                if with_errors:
                    rv['status'] = "Uploaded With Errors"
                else:
                    rv['status'] = "Uploaded Successfully"
                if extract_dir:
                    shutil.rmtree(extract_dir)
                if download_dir:
                    shutil.rmtree(download_dir)
                if ret == 0:
                    return rv, 200
                else:
                    return rv, 404
            except Exception as e:
                if extract_dir:
                    shutil.rmtree(extract_dir)
                if download_dir:
                    shutil.rmtree(download_dir)
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    return app


if __name__ == "__main__":
    serve(create_app(), host='0.0.0.0', port=7000, threads=20)
