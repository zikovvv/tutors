from typing import *
import random
from flask import *
from db import DB
app = Flask(__name__)

class Server :
    def __init__(self, db : DB):
        self.db = db

    def get_new_bearer_key(l = 64) :
        return random.getrandbits(l)

    def decorate_route(self, endpoint : str, methods : List[str]) :
        def _decorate_route(func : Callable) :
            def inner(*args, **kwargs) :
                print('i am in decorated callback')
                return func(*args, **kwargs)
            return app.route(endpoint, methods = methods)(inner)
        return _decorate_route

    @app.route('/signup', methods = ['GET', 'POST'])
    #@decorate_route('/signup', methods = ['GET', 'POST'])
    def signup(self) :
        if request.is_json :
            print(request.host, request.args, request.json, request.headers)
            if request.method == 'GET' :
                return "enter your email and pasword and abcde..."
            else :
                return "ok"
        return 'request must be json', 400

    @app.route('/login', methods = ['GET', 'POST'])
    def login(self) :
        if request.is_json :
            data = request.json
            if request.method == 'GET':
                return "enter your email and pasword"
            else:
                try :
                    login, passwd = data['login'], data['password']
                    assert login
                    assert passwd
                except KeyError | AssertionError | TypeError :
                    return 'login', 400
                if (login, passwd) == ('1', '1') :
                    return 'main page'
        return 'request must be json', 400

    @app.get('/')
    def main(self):
        if request.is_json :
            data = request.json
            try :
                key = request.cookies['Authorization']
                print(key)
            except KeyError | AssertionError | TypeError :
                return 'login', 401

        return 'request must be json', 400


if __name__ == '__main__':
    db = DB()
    server = Server(db)
    app.run(host = '0.0.0.0', port = 6000)