from typing import List
import queries as q
import psycopg2 as sql
import config as cfg
import datetime
from dataclasses import dataclass

@dataclass(init=True, repr=True)
class User :
    id : int
    role : int
    signup_date : datetime.datetime
    email : str
    password : str
    first_name : str
    last_name : str
    phone : str
    telegram : str
    about : str
    education : str
    year_born : int
    key: str
    key_created : datetime.datetime

class DB :
    def __init__(self, db_name, db_host, db_user, db_password):
        self.conn = sql.connect(
            database = db_name,
            host = db_host,
            user = db_user,
            password = db_password
        )
        self.cur = self.conn.cursor()

    def exe(self, query, args = None, commit = True):
        self.cur.execute(query, args)
        self.conn.commit()
        if 'SELECT' in self.cur.statusmessage :
            return self.cur.fetchall()

    def get_all_users(self):
        return self.exe(q.get_all_users)

    def set_user_key(self, user_id, key):
        return self.exe(q.set_user_key, (user_id, key))

    def get_user_by_email_and_password(self, email, password):
        res = self.exe(q.get_user_by_email_and_password, (email, password))
        if res :
            res = User(*res[0])
        return res

    def get_user_by_email(self, email):
        res = self.exe(q.get_user_by_email, (email, ))
        if res:
            res = User(*res[0])
        return res

    def get_user_by_key(self, key):
        res = self.exe(q.get_user_by_key, (key, ))
        if res:
            res = User(*res[0])
        return res

    def get_tutors(self, nb_tutors_on_page, page_index, order_by, max_price, min_price, subject, project = None):
        query = f'SELECT {", ".join(project) if isinstance(project, list) else "*"} FROM tutors WHERE price BETWEEN %s AND %s ' + (' AND %s = ANY(subjects)' if subject is not None else '') + f' ORDER BY {order_by} LIMIT %s OFFSET %s;'
        if subject is not None :
            return self.exe(query, (min_price, max_price, subject, nb_tutors_on_page, nb_tutors_on_page * page_index))
        else:
            return self.exe(query, (min_price, max_price, nb_tutors_on_page, nb_tutors_on_page * page_index))

    def get_subjects(self):
        return [a[0] for a in self.exe(q.get_subjects)]

    def get_roles(self):
        return [a[0] for a in self.exe(q.get_roles)]

    def add_user(self, *args):
        return self.exe(q.add_user, args)

    def add_tutor_info(self, subjects : List[int], tutor_id, price, experience):
        for sub in subjects :
            self.exe(q.add_subject_to_tutor, (tutor_id, sub))
        self.exe(q.add_tutor_info, (tutor_id, price, experience))

    def get_schedule_for_turor(self, tutor_id):
        days = self.get_days()
        return [(days[a[2]], a[3]) for a in self.exe('SELECT * FROM schedule WHERE tutor_id = %s;', (tutor_id, ))]#(self.exe('SELECT id from users where email=%s', (tutor_email, ))))

    def get_schedule_for_student(self, student_id):
        return self.exe('SELECT * FROM schedule WHERE student_id = %s;', (student_id, ))#(self.exe('SELECT id from users where email=%s', (student_email, ))))

    def get_tutors_of_student(self, student_id):
        return self.exe('SELECT * FROM tutors_have_students WHERE student_id = %s;', (student_id, ))

    def get_students_of_tutor(self, tutor_id):
        return self.exe('SELECT * FROM tutors_have_students WHERE tutor_id = %s;', (tutor_id, ))

    def add_schedule(self, tutor_id, day, hour):
        self.exe('INSERT INTO schedule(tutor_id, day, hour) VALUES(%s, %s, %s);', (tutor_id, day, hour))
        self.conn.commit()

    def remove_schedule(self, tutor_id, day, hour):
        self.exe('DELETE FROM schedule WHERE tutor_id = %s AND day = %s AND hour = %s;', (tutor_id, day, hour))
        self.conn.commit()

    def get_days(self):
        return [a[0] for a in self.exe('SELECT name FROM days;')]

    def get_reviews(self, tutor_id):
        return self.exe('SELECT * FROM reviews WHERE tutor_id = %s;', (tutor_id, ))

    def add_review(self, student_id, tutor_id, text, rating):
        return self.exe('INSERT INTO reviews(student_id, tutor_id, text, rating, date) VALUES(%s, %s, %s, %s, CURRENT_TIMESTAMP);', (student_id, tutor_id, text, rating))


if __name__ == '__main__':
    db = DB(cfg.db_name, cfg.db_host, cfg.db_user, cfg.db_password)
    #print(db.get_all_users())
    page_index = 0
    order_by = 'id'
    max_price = 1000
    min_price = 50
    subject = 7
    print(db.get_tutors(5, page_index, order_by, max_price, min_price, subject, ['first_name', 'last_name', 'subjects']))

