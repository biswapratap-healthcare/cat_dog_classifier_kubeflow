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

from db_driver import if_table_exists, create_table, insert_data, truncate_table, drop_table, get_all_data, \
    get_study_from_to
from utils import get_image


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

    from_to_parser = reqparse.RequestParser()
    from_to_parser.add_argument('from',
                                type=str,
                                help='from date',
                                required=True)
    from_to_parser.add_argument('to',
                                type=str,
                                help='to date',
                                required=True)

    @api.route('/get_data_from_to')
    @api.expect(from_to_parser)
    class FromToService(Resource):
        @api.expect(from_to_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = from_to_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['health'] = str(e)
                return rv, 404
            try:
                from_date = args['from']
                to_date = args['to']
                ret_dict, ret_str = get_study_from_to(from_date, to_date)
                if ret_str != "Success":
                    rv = dict()
                    rv['status'] = ret_str
                    return rv, 404
                else:
                    return ret_dict, 200
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    get_all_data_parser = reqparse.RequestParser()
    get_all_data_parser.add_argument('table_name',
                                     type=str,
                                     help='List all data of this table name',
                                     required=True)

    @api.route('/get_all_data')
    @api.expect(get_all_data_parser)
    class GetAllDataService(Resource):
        @api.expect(get_all_data_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = get_all_data_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404
            try:
                table_name = args['table_name']
                if if_table_exists(table_name=table_name):
                    ret_dict, ret_str = get_all_data(table_name=table_name)
                    return ret_dict, 200
                else:
                    rv = dict()
                    rv['status'] = table_name + " doesn't exist!"
                    return rv, 404
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    drop_table_parser = reqparse.RequestParser()
    drop_table_parser.add_argument('table_name',
                                   type=str,
                                   help='The Table to be destroyed/dropped',
                                   required=True)

    @api.route('/drop_table')
    @api.expect(drop_table_parser)
    class DropTableService(Resource):
        @api.expect(drop_table_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = drop_table_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404
            try:
                table_name = args['table_name']
                if if_table_exists(table_name=table_name):
                    ret, status = drop_table(table_name)
                else:
                    status = table_name + " doesn't exist!"
                    ret = -1
                rv = dict()
                rv['status'] = status
                if ret == 0:
                    return rv, 200
                else:
                    return rv, 404
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    truncate_table_parser = reqparse.RequestParser()
    truncate_table_parser.add_argument('table_name',
                                       type=str,
                                       help='The Table to be truncated',
                                       required=True)

    @api.route('/truncate_table')
    @api.expect(truncate_table_parser)
    class TruncateTableService(Resource):
        @api.expect(truncate_table_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = truncate_table_parser.parse_args()
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404
            try:
                table_name = args['table_name']
                if if_table_exists(table_name=table_name):
                    ret, status = truncate_table(table_name)
                else:
                    status = table_name + " doesn't exist!"
                    ret = -1
                rv = dict()
                rv['status'] = status
                if ret == 0:
                    return rv, 200
                else:
                    return rv, 404
            except Exception as e:
                rv = dict()
                rv['status'] = str(e)
                return rv, 404

    annotate_parser = reqparse.RequestParser()
    annotate_parser.add_argument('file',
                                 location='files',
                                 type=FileStorage,
                                 help='The zip of all the dog and cat images',
                                 required=True)

    @api.route('/annotate')
    @api.expect(annotate_parser)
    class AnnotationService(Resource):
        @api.expect(annotate_parser)
        @api.doc(responses={"response": 'json'})
        def post(self):
            try:
                args = annotate_parser.parse_args()
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
                            image = get_image(cat_dir, cat_file)
                            ret, status = insert_data(_id, label, cat_file, image)
                            if ret != 0:
                                with_errors = 1
                                print(status)
                        for dog_file in dog_files:
                            _id = str(current_milli_time())
                            label = 'dog'
                            image = get_image(dog_dir, dog_file)
                            ret, status = insert_data(_id, label, dog_file, image)
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
