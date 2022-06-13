import datetime
import string
from collections import defaultdict
from dataclasses import dataclass
from typing import *
import random
from flask import *
from db import DB, User
from utils import *
import config as cfg
app = Flask(__name__)
'''
def decorate_route(self, endpoint : str, methods : List[str]) :
    def _decorate_route(func : Callable) :
        def inner(*args, **kwargs) :
            print('i am in decorated callback')
            return func(*args, **kwargs)
        return app.route(endpoint, methods = methods)(inner)
    return _decorate_route
'''

clip = lambda x, mi, ma : (((x if x > mi else mi) if x < ma else ma) if ma > mi else ma) if isinstance(x, int) or isinstance(x, float) else ma

def get_new_bearer_key(l = 64) :
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join([random.choice(chars) for i in range(64)])

@app.route('/signup', methods = ['GET', 'POST'])
def signup_page() :
    data = request.json
    subjects = db.get_subjects()
    roles = db.get_roles()
    if request.method == 'GET' :
        return {'page' : 'signup', 'roles' : roles, 'subjects' : subjects}
    else :
        email = data['email']
        if db.get_user_by_email(email) :
            return {'page' : 'signup', 'error' : 'email is already in system', 'roles' : roles, 'subjects' : subjects}, 400
        else :
            key = get_new_bearer_key()
            role = data['role']
            db.add_user(
                roles.index(role) + 1, data['email'], data['password'], data['first_name'], data['last_name'],
                data['phone'], data['telegram'], data['about'], data['education'],
                data['year_born'], key
            )
            if role == 'Tutor' :
                tutor_user = db.get_user_by_email(data['email'])
                db.add_tutor_info([subjects.index(a) + 1 for a in data['subjects']], tutor_user.id, data['price'], data['experience'])
            return {'page' : 'main', 'key' : key, 'role' : role}

@app.route('/signin', methods = ['GET', 'POST'])
def signin_page() :
    data = request.json
    if request.method == 'GET':
        return {'page' : 'signin'}
    else:
        email, password = data['email'], data['password']
        user = db.get_user_by_email_and_password(email, password)
        if user :
            if (current_time() - user.key_created).seconds > 24 * 60 * 60 * 60 :
                key = get_new_bearer_key()
                db.set_user_key(user.id, key)
            return {'page' : 'main', 'key' : user.key, 'role' : ['Student', 'Tutor'][user.role - 1]}
        else:
            return {'page': 'signin', 'error': 'wrong email or password'}, 401

@app.get('/')
def main():
    user = get_user()
    print(user)
    if not user :
        return redirect(url_for('auth'))
    else :
        return {'page' : 'main'}

@app.get('/auth')
def auth():
    return {'page' : 'auth'}

@app.get('/my_profile')
def my_profile():
    user = get_user()
    print(user)
    if not user :
        return redirect(url_for('auth'))
    else :
        prf = {
            'first_name' : user.first_name,
            'last_name' : user.last_name,
            'email' : user.email,
            'role' : db.get_roles()[user.role - 1],
            'phone' : user.phone,
            'telegram' : user.telegram,
            'signup_date' : user.signup_date,
        }
        return {'page' : 'my_profile', 'profile' : prf}

@app.get('/tutors')
def tutors():
    user = get_user()
    if not user :
        return redirect(url_for('auth'))
    else :
        data = request.json
        nb_tutors_on_page = 10
        nb_tutors = db.exe("SELECT COUNT(*) FROM tutors")[0][0]
        max_page_idx = nb_tutors // nb_tutors_on_page
        subjects = db.get_subjects()
        orders = ['id', 'rating', 'nb_reviews', 'price']
        orders_names = ['No order', 'Order by rating', 'Order by number of reveiews', 'Order by price']
        filters = data['filters'] if 'filters' in data else {}
        page_index =  clip(filters['page_index'], 0, max_page_idx) if 'page_index' in filters and isinstance(filters['page_index'], int) else 0
        order_by =  orders[filters['order_by']] if 'order_by' in filters and isinstance(filters['order_by'], int) and 0 <= filters['order_by'] < len(orders) else orders[0]
        max_price =  clip(filters['max_price'], 50, 1000)if 'max_price' in filters and isinstance(filters['max_price'], int) else 1000
        min_price =  clip(filters['min_price'], 51, 1000)if 'min_price' in filters and isinstance(filters['min_price'], int) else 50
        subject = filters["subject"] if 'subject' in filters and isinstance(filters['subject'], int) and 1 <= filters["subject"] <= len(subjects) else None
        if max_price <= min_price :
            max_price = 1000
            min_price = 50
        keys = ['email', 'first_name', 'last_name', 'phone', 'telegram', 'education', 'price', 'subjects', 'rating', 'nb_reviews']
        tutors = [dict(zip(keys, t)) for t in db.get_tutors(nb_tutors_on_page, page_index, order_by, max_price, min_price, subject, keys)]
        return {'page' : 'tutors', 'tutors' : tutors, "filters" : {'page_index' : page_index, 'order_by' : orders.index(order_by), 'max_price' : max_price, 'min_price' : min_price, 'subject' : subject - 1 if subject is not None else None}, 'max_page_idx' : max_page_idx, 'subjects' : subjects, "orders" : orders_names}
'''
@app.get('/my_tutors')
def my_tutors():
    user = get_user()
    if not user :
        return redirect(url_for('auth'))
    else :
        if user.role == 1 :
            #keys = ['email', 'first_name', 'last_name', 'phone', 'telegram', 'education', 'price', 'subjects', 'rating',
                    #'nb_reviews']
            #tutors = [dict(zip(keys, t)) for t in db.get_tutors(1000, 0, 'id', 1000, 50, None, keys)]
            tutors = db.get_tutors_of_student()
            return {'page': 'my_tutors', 'tutors': tutors}
        else :
            return {'page': 'main'}
'''

@app.route('/my_schedule', methods = ['GET', 'POST'])
def my_schedule():
    user = get_user()
    if not user :
        return redirect(url_for('auth'))
    else :
        if user.role == 2 :
            data = request.json
            days = db.get_days()
            actions = ['Add lesson', 'Remove lsesson']
            if request.method == 'GET' :
                schedule = db.get_schedule_for_turor(user.id)
                return {'page' : 'my_schedule', 'schedule' : schedule, 'days' : days, 'actions' : actions}
            else :
                action = data['action']
                h, d = clip(data['hour'], 8, 21), clip(data['day'], 0, 6)
                if action == 0 :
                    db.add_schedule(user.id, d, h)
                elif action == 1 :
                    db.remove_schedule(user.id, d, h)
                db.conn.commit()
                schedule = db.get_schedule_for_turor(user.id)
                return {'page' : 'my_schedule', 'schedule' : schedule, 'days' : days, 'actions' : actions}
        else :
            return {'page': 'main'}

@app.route('/tutor', methods = ['POST', 'GET'])
def tutor():
    user = get_user()
    if not user :
        return redirect(url_for('auth'))
    else :
        data = request.json

        if request.method == 'POST' :
            if user.role == 1 :
                keys = ['id', 'email', 'first_name', 'last_name', 'phone', 'telegram', 'education', 'price', 'subjects',
                        'rating', 'nb_reviews', 'about']
                t = dict(zip(keys, db.exe(f'SELECT {", ".join(keys)} FROM tutors WHERE email = %s', (data['email'],))[0]))
                db.add_review(user.id, t['id'], data['text'], data['rating'])

        keys = ['id', 'email', 'first_name', 'last_name', 'phone', 'telegram', 'education', 'price', 'subjects', 'rating', 'nb_reviews', 'about']
        t = dict(zip(keys, db.exe(f'SELECT {", ".join(keys)} FROM tutors WHERE email = %s', (data['email'], ))[0]))
        print(t)
        subjects_names, schedule, reviews, days = db.get_subjects(), db.get_schedule_for_turor(t['id']), db.get_reviews(t['id']), db.get_days()
        print(subjects_names, schedule, reviews, days)
        return {'page' : 'tutor', 'tutor' : t, 'subjects' : subjects_names, 'reviews' : reviews, 'days' : days, "schedule" : schedule}

'''
@app.get('/my_students')
def my_students():
    user = get_user()
    if not user :
        return redirect(url_for('auth'))
    else :
        data = request.json
        if user.role == 2:
            students = db.get_students_of_tutor(user.id)
            return {'page': 'my_students', 'students': students}
        else:
            return {'page': 'main'}
'''

def get_user() :
    try :
        key = request.headers['Authorization'].split('Bearer ')[1]
        return db.get_user_by_key(key)
    except BaseException :
        db.conn.rollback()
        return None


if __name__ == '__main__':
    db = DB(cfg.db_name, cfg.db_host, cfg.db_user, cfg.db_password)
    app.run(host = cfg.web_app_host, port = cfg.web_app_port)