import datetime
import json
import os
import re
import time
from typing import *
from weakref import finalize

import requests as r
import config as cfg
from utils import last_exception
clip = lambda x, mi, ma : (((x if x > mi else mi) if x < ma else ma) if ma > mi else ma) if isinstance(x, int) or isinstance(x, float) else ma

class Page :
    def __init__(self, client, code_name, title) :
        self.client : Client = client
        self.client.pages[code_name] = self
        self.code_name = code_name
        self.title = title
        self.get_cookies = self.client.get_cookies
        self.request = self.client.request


    def input(self, default_caption, error_caption, regexp):
        bad = False
        while 1 :
            res = input(default_caption if not bad else error_caption)
            bad = not re.match(regexp, res)
            if not bad :
                return res

    def choise(self, variants, is_menu = True):
        while 1 :
            try :
                choice = int(input(('\tM E N U\n' if is_menu else '') + '\n'.join([f'[{i}] {var}' for i, var in enumerate(variants)]) + '\n'))
                if 0 <= choice <= len(variants) - 1 :
                    return choice
                else :
                    print(f'{choice} is not in the list of all possible answers, try again.')
            except ValueError :
                pass

    def show(self, error, page, data):
        print('====================================')
        print(self.title)
        if error :
            print(f'Error : {error}')

    def input_integer(self, text = 'Your answer : ', wrong = 'Answer has to be integer!', min_ = 0, max_ = 1000000000):
        while 1 :
            try :
                return int(input(text))
            except ValueError :
                print(wrong)

class PageAuth(Page) :
    def __init__(self, client):
        super().__init__(client, 'auth', 'Authorization')

    def show(self, error, page, data):
        super().show(error, page, data)
        match self.choise(['Sign in', 'Sign up']):
            case 0:
                self.request({}, 'signin')
            case 1:
                self.request({}, 'signup')

class PageSignUp(Page) :
    def __init__(self, client):
        super().__init__(client, 'signup', 'Sign up')

    def show(self, error, page, data):
        super().show(error, page, data)
        subjects_names, roles_names = data['subjects'], data['roles']
        email = self.input('Email : ', "Enter a valid email : ", regexp='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        password = input('Password : ')
        while 1:
            if input('Repeat password : ') != password:
                print('Passwords do not match!')
            else:
                break
        print('Choose who you are : ')
        role = roles_names[self.choise([f'I am {role.lower()}' for role in roles_names], is_menu=False)]
        req = {
            'role' : role,
            'email': email,
            'password': password,
            'first_name': input('First name : '),
            'last_name': input('Last name : '),
            'phone': input('Phone : '),
            "telegram": input('Telegram : '),
            'about': input('Tell some words about you : '),
            'education': input('What is your education : '),
            'year_born': clip(self.input_integer('What is your year of birth : '), 1930, datetime.datetime.now().year)
        }
        if role == 'Tutor' :
            subjects : Set[str] = set()
            print('What subjects do you teach?(5 max)\n')
            for i in range(5) :
                if subjects :
                    print(f'You choosed :\n' + '\n'.join(subjects))

                choise = self.choise(['Add subject', 'Continue']) if i != 0 else 0
                match choise :
                    case 0 :
                        subj = subjects_names[self.choise(subjects_names)]
                        subjects.add(subj)
                        print(f'Subject #{i} : {subj}')
                    case 1 :
                        break
            req['subjects'] = list(subjects)
            req['price'] = self.input_integer('Enter price for one hour of your services in UAH : ')
            req['experience'] = self.input_integer('How many years of experience do you have? : ')
        self.request(req, 'signup', method='POST')

class PageSignIn(Page) :
    def __init__(self, client):
        super().__init__(client, 'signin', 'Sign in')

    def show(self, error, page, data):
        super().show(error, page, data)
        if error:
            if self.choise(['Back', 'Try again']) == 0 :
                return self.request({})
        email = self.input('Email : ', "Enter a valid email : ", regexp='^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        password = input('password : ')
        self.request({'email': email, 'password': password}, 'signin', method='POST')

class PageMain(Page) :
    def __init__(self, client):
        super().__init__(client, 'main', 'Main page')

    def show(self, error, page, data):
        super().show(error, page, data)
        vars = ['My profile', 'All tutors']
        if self.get_cookies()['role'] == 'Tutor' :
            vars.append('My schedule')
        '''
        atch self.get_cookies()['role'] :
            case 'Student' :
                vars += ['My tutors']
            case 'Tutor' :
                vars += ['My students']
        '''
        vars.append('Log out')
        vars.append('Exit')
        choice = self.choise(vars)
        match vars[choice] :
            case 'My profile' :
                self.request({}, 'my_profile')
            case 'All tutors' :
                self.request({}, 'tutors')
            #case 'My tutors' :
            #    self.request({}, 'my_tutors')
            case 'My schedule' :
                self.request({}, 'my_schedule')
            #case 'My students' :
            #    self.request({}, 'my_students')
            case 'Log out' :
                self.client.set_default_cookies()
                self.request({})
            case 'Exit' :
                os.remove(self.client.lock_path)
                return 'exit'

class PageMyProfile(Page) :
    def __init__(self, client):
        super().__init__(client, 'my_profile', 'My profile')

    def show(self, error, page, data):
        super().show(error, page, data)
        print(data['profile'])
        choice = self.choise(['Back'])
        match choice:
            case 0 :
                self.request({})

class PageTutors(Page) :
    def __init__(self, client):
        super().__init__(client, 'tutors', 'Tutors')

    def show(self, error, page, data):
        super().show(error, page, data)
        tutors, filters, orders_names, subjects_names = data['tutors'], data['filters'], data['orders'], data['subjects']
        print(filters, orders_names, subjects_names)
        print_filters = lambda : print(f"\nFilters :\n\tPage : {filters['page_index']}\n\tOrder by : {orders_names[filters['order_by']]}\n\tMin price : {filters['min_price']} UAH\n\tMax price : {filters['max_price']} UAH\n\tSubject : {subjects_names[filters['subject'] - 1] if filters['subject'] else 'No subject'}")
        print_filters()
        print('\nWe found this tutors for you : ')
        #['email', 'first_name', 'last_name', 'phone', 'telegram', 'education', 'price', 'subjects', 'rating', 'nb_reviews']
        for j, t in enumerate(tutors) :
            print(f"{j} \t\nName : {t['first_name']} {t['last_name']}\n\tSubjects : {', '.join([subjects_names[i - 1] for i in t['subjects']])}\n\tRating : {t['rating']}. Number of reviews : {t['nb_reviews']}\n\tEmail : {t['email']} | Phone : {t['phone']} | Telegram")
        choice = self.choise([f'View info about tutor {i}' for i in range(len(tutors))] + ['Edit filters', 'Previous page', 'Next page', 'Back'])
        if choice < len(tutors) :
            self.request({'email' : tutors[choice]['email']}, 'tutor')
        else :
            choice -= len(tutors)
            match choice :
                case 0 :
                    while 1 :
                        choice = self.choise(['Order by', 'Max price', 'Min price', 'Subject', 'Confirm'])
                        match choice :
                            case 0 :
                                #order by
                                filters["order_by"] = self.choise(orders_names)
                            case 1 :
                                #max price
                                filters["max_price"] = self.input_integer('Enter max price : ')
                            case 2 :
                                # min price
                                filters["min_price"] = self.input_integer('Enter min price : ')
                            case 3 :
                                # subject
                                filters["subject"] = self.choise(subjects_names) + 1
                            case 4 :
                                self.request({'filters': filters}, 'tutors')
                                break
                        print_filters()
                case 1 :
                    filters["page_index"] = clip(filters['page_index'] - 1, 0, 100000)
                    self.request({'filters' : filters}, 'tutors')
                case 2 :
                    filters['page_index'] = clip(filters["page_index"] + 1, 0, 100000)
                    self.request({'filters': filters}, 'tutors')
                case 3:
                    self.request({})

class PageTutor(Page) :
    def __init__(self, client):
        super().__init__(client, 'tutor', 'Tutor')

    def show(self, error, page, data):
        super().show(error, page, data)
        #print(data['tutor'], data['schedule'], data['reviews'])
        t, subjects_names, schedule, reviews, days = data['tutor'], data['subjects'], data['schedule'], data['reviews'], data['days']
        print(f"\nName : {t['first_name']} {t['last_name']}\n\tSubjects : {', '.join([subjects_names[i - 1] for i in t['subjects']])}\n\tRating : {t['rating']}. Number of reviews : {t['nb_reviews']}\n\tEmail : {t['email']} | Phone : {t['phone']} | Telegram")

        d = {day: [] for day in days}
        for day, hour in schedule:
            d[day].append(hour)

        #print(days)
        #print(d)
        print('\t', '\t'.join(f'{h}:00' for h in range(8, 21)))
        for day, hours in d.items():
            row = f'{day} '
            for h in range(8, 21):
                if h in hours:
                    row += '\t____'
                else:
                    row += '\t    '
            print(row)

        print('\n\bReviews : ')
        for j, rev in enumerate(reviews) :
            print(f'{j}, {rev[-1]}, {rev[3]}\nRating : {rev[-2]}')

        if self.get_cookies()['role'] == 'Student' :
            choice = self.choise(['Back', 'Leave a review'])
        else:
            choice = self.choise(['Back'])
        match choice:
            case 1:
                review = input('Your review : ')
                print('How would you rate your experince with rhis tutor?(0 to 5)')
                rating = self.choise(['0', '1', '2', '3', '4', '5'])
                self.request({'email' : t['email'], 'text' : review, 'rating' : rating}, 'tutor', method = 'POST')
            case 0:
                self.request({})

class PageMySchedule(Page):
    def __init__(self, client):
        super().__init__(client, 'my_schedule', 'My schedule')

    def show(self, error, page, data):
        super().show(error, page, data)
        days = data['days']
        schedule = data['schedule']
        print(schedule)
        d = {day : [] for day in days}
        for day, hour in schedule :
            d[day].append(hour)

        print(days)
        print(d)
        print('\t', '\t'.join(f'{h}:00' for h in range(8, 21)))
        for day, hours in d.items() :
            row = f'{day} '
            for h in range(8, 21) :
                if h in hours :
                    row += '\t_'
                else:
                    row += '\t '
            print(row)

        choice = self.choise(['Edit schedule', 'Back'])
        match choice:
            case 0:
                print('Choose action')
                action = self.choise(data['actions'])

                print('Choose day')
                day = self.choise(data['days'])

                print('Choose hour')
                hour = self.choise([str(i) for i in range(8, 21)])

                self.request({'hour' : hour, 'day' : day + 1, 'action' : action}, 'my_schedule', method = 'POST')
            case 1:
                self.request({})

"""
class PageMyTutors(Page) :
    def __init__(self, client):
        super().__init__(client, 'my_tutors', 'My tutors')

    def show(self, error, page, data):
        super().show(error, page, data)
        choice = self.choise(['Back'])
        match choice:
            case 0:
                self.request({})

class PageMyStudents(Page):
    def __init__(self, client):
        super().__init__(client, 'my_students', 'My students')

    def show(self, error, page, data):
        super().show(error, page, data)
        vars = data['students']
        choice = self.choise(vars + ['Back'])
        if choice < len(vars) :
            self.request({'email'}, 'student')
        else :
            self.request({})
"""

class Client :
    def __init__(self, server_ip) :
        self.server_ip = server_ip
        profiles_path = './profiles/'
        if not os.path.exists(profiles_path) :
            os.mkdir(profiles_path)

        for i in range(100000) :
            self.profile_path = profiles_path + str(i) + '/'
            if not os.path.exists(self.profile_path) :
                os.mkdir(self.profile_path)

            self.lock_path = self.profile_path + 'lock'
            if not os.path.exists(self.lock_path) :
                with open(self.lock_path, 'wb') as f :
                    f.write(b'0')
                break

        self.cookies_path = self.profile_path + "cookies.json"
        self.res = None
        self.pages : Dict[str, Page] = {}
        self.finalizer = finalize(self, lambda : os.remove(self.lock_path))

    def get_cookies(self) -> dict[str, str] :
        if 'cookies.json' not in os.listdir(os.path.dirname(self.cookies_path)):
            self.set_default_cookies()
        with open(self.cookies_path, 'r+') as f :
            return json.load(f)

    def set_cookies(self, cookies : dict[str, str]):
        with open(self.cookies_path, 'w+') as f :
            json.dump(cookies, f)

    def set_default_cookies(self):
        with open(self.cookies_path, 'w+') as f:
            json.dump({'key': '', 'role': ''}, f)
        os.remove(self.lock_path)

    def set_cookie(self, key, val):
        c = self.get_cookies()
        c[key] = val
        self.set_cookies(c)

    def request(self, data : dict or list, endpoint : str = '/', method = 'GET', save_result = True):
        res = r.request(
            method,
            f'{self.server_ip}/{endpoint}',
            headers = {'Content-Type': 'application/json', 'Authorization' : f'Bearer {self.get_cookies()["key"]}'},
            data = json.dumps(data)
        )
        if save_result :
            self.res = res
        return res

    def start(self):
        self.request({})
        while 1 :
            try :
                data = self.res.json()
                page = data['page']
                error = None
                if 'error' in data :
                    error = data['error']
                if 'key' in data :
                    self.set_cookie('key', data['key'])
                if 'role' in data :
                    self.set_cookie('role', data['role'])

                if page is not None :
                    if self.pages[page].show(error, page, data) == 'exit' :
                        try :
                            os.remove(self.lock_path)
                        except BaseException :
                            pass
                        return
            except KeyboardInterrupt :
                os.remove(self.lock_path)
            except SystemExit :
                os.remove(self.lock_path)
            except BaseException :
                print(last_exception())
                time.sleep(1)

    def add_page(self, page : Page):
        self.pages[page.code_name] = page


if __name__ == '__main__':
    client = Client(cfg.server_ip)
    client.add_page(PageAuth(client))
    client.add_page(PageSignIn(client))
    client.add_page(PageSignUp(client))
    client.add_page(PageMain(client))
    client.add_page(PageMyProfile(client))
    client.add_page(PageTutors(client))
    client.add_page(PageTutor(client))
    #client.add_page(PageMyTutors(client))
    client.add_page(PageMySchedule(client))
    #client.add_page(PageMyStudents(client))
    client.start()


