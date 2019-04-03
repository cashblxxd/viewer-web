from flask import *
from db_connect import *
import os
from flask import request, redirect, jsonify, make_response
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename
from werkzeug import datastructures
import werkzeug
import random
from flask import Flask, session
from flask_session import Session


db = DB()
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = 'file_database/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.system(f'mkdir {UPLOAD_FOLDER}')
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)
session_uid = {
    'username': -1,
    'user_id': -1
}



'''def init():
    parser_init()
    add_API_resources()'''


class Hello(Resource):
    def post(self):
        return jsonify({"hello!": 'user'})


class News(Resource):
    def post(self, news_id):
        if session_uid['user_id'] == -1:
            abort(401, message='Unauthorized user. Please log in via /login'
                               'or sign up via /signup')
        args = parser.parse_args()
        if not all(key in args for key in ['title', 'description']) or 'file' not in request.files:
            abort(400, message='Bad request. Make sure you fill title, description and file fields in.')
        title, content, file, file_name = args['title'], args['description'], request.files['file'], args['file_name']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
        nm = NewsModel(db.get_connection())
        h = nm.insert(title, content, session_uid['user_id'], file_name)
        nm = Permissions(db.get_connection())
        nm.add_permission(h, session_uid['user_id'])
        return jsonify({'status': 'OK', 'message': 'News created successfully.', 'news_id': h})

    def get(self, news_id):
        global session
        if session_uid['user_id'] == -1:
            abort(401, message='Unauthorized user. Please log in via /login'
                               'or sign up via /signup')
        abort_if_news_not_found(news_id)
        nm = Permissions(db.get_connection())
        nmm = nm.get_news_permissions(news_id)
        h = list(map(str, nmm))
        if str(session_uid['user_id']) not in h:
            abort(403, message='Access denied:(')
        news = NewsModel(db.get_connection()).get(news_id)
        title = news[1]
        description = news[2]
        creator = UserModel(db.get_connection()).get(news[3])[1]
        file = news[4]
        return jsonify({
            'title': title,
            'creator': creator,
            'description': description,
            'attached file': file
        })

    def delete(self, news_id):
        global session
        if session_uid['user_id'] == -1:
            abort(401, message='Unauthorized user. Please log in via /login')
        abort_if_news_not_found(news_id)
        nm = NewsModel(db.get_connection())
        if str(nm.get(news_id)[3]) != str(session_uid['user_id']):
            abort(403, message='Access denied:(')
        nm.delete(news_id)
        nm = Permissions(db.get_connection())
        nm.delete_news(news_id)
        NewsModel(db.get_connection()).delete(news_id)
        return jsonify({'success': 'OK'})


class NewsList(Resource):
    def get(self):
        if 'user_id' not in session:
            abort(401, message='Unauthorized user. Please log in via /login')
        news = NewsModel(db.get_connection()).get_all()
        return jsonify({'news': news})

    def post(self):
        if 'user_id' not in session:
            abort(401, message='Unauthorized user. Please log in via /login')
        args = parser.parse_args()
        news = NewsModel(db.get_connection())
        news.insert(args['title'], args['content'], args['user_id'])
        return jsonify({'success': 'OK'})


def OAuth(username, user_id):
    global session
    session['username'] = username
    session['user_id'] = user_id
    session_uid['username'] = username
    session_uid['user_id'] = user_id


class Login(Resource):
    def post(self):
        global session
        args = parser.parse_args()
        if 'login' not in args or 'password' not in args:
            abort(400, message='Bad request. Make sure you fill login and password fields in.')
        user_model = UserModel(db.get_connection())
        success = user_model.login(args['login'], args['password'])
        if success[0]:
            OAuth(args['login'], success[1])
            return jsonify({'success': 'Logged in successfully.'})
        return jsonify({
            'status': 'Error',
            'message': 'Login failed. Please re-check your login and password'
                       ' or try again later. To register please use /signup .'
        })


class Signup(Resource):
    def post(self):
        args = parser.parse_args()
        if 'login' not in args or 'password' not in args:
            a, b = 'login' in args, 'password' in args
            abort(400, message=f'Bad request. Make sure you fill login and password fields in. {a} {b}')
        user_name = args['login']
        password = args['password']
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name)
        if not exists[0]:
            user_model.insert(user_name, password)
            return jsonify({
                'status': 'OK',
                'message': 'Registered successfully'
            })
        return jsonify({
                'status': 'Error',
                'message': 'Sorry, this username is already taken.'
            })


class Index(Resource):
    def get(self):
        md = NewsModel(db.get_connection())
        h = set(Permissions(db.get_connection()).get_user_permissions(session_uid['user_id']))
        affordable = [md.get(i) for i in h]
        return jsonify({'Available news:': ', '.join([str(i[0]) for i in affordable])})


class Upload(Resource):
    def get(self):
        if session_uid['user_id'] == -1:
            abort(401, message='Unauthorized user. Please log in via /login')
        args = parser.parse_args()
        if not all(key in args for key in ['news_id', 'filename']):
            abort(400, message='Bad request. Make sure you fill news_id and filename fields in.')
        if session_uid['user_id'] in Permissions(db.get_connection()).get_news_permissions(args['news_id']) \
                and args['filename'] in NewsModel(db.get_connection()).get(args['news_id']):
            return send_from_directory(app.config['UPLOAD_FOLDER'], args['filename'])
        abort(403, message='Access denied:(')


def abort_if_news_not_found(news_id):
    if not NewsModel(db.get_connection()).get(news_id):
        abort(404, message="News {} not found".format(news_id))


# init()
'''def parser_init():
    global parser'''
parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('description')
parser.add_argument('user_id')
parser.add_argument('username')
parser.add_argument('login')
parser.add_argument('password')
parser.add_argument('news_id')
parser.add_argument('filename')
parser.add_argument('file_name')
parser.add_argument('file', type=datastructures.FileStorage, location='files')
api.add_resource(Upload, '/get_upload')
api.add_resource(News, '/news/<int:news_id>')  # для одного объекта
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Index, '/index')
app.run(port=5000, host='127.0.0.1')