import queries as q
import psycopg2 as sql

class DB :
    def __init__(self):
        self.conn = sql.connect(
            dbname = "tutors1",
            user = "postgres",
            password = "opangangnamstyle"
        )
        self.cur = self.conn.cursor()
        self.exe = self.cur.execute

    def get_all_users(self):
        return self.exe(q.get_all_users)

    def set_user_key(self, user_id, key):
        return self.exe(q.set_user_key.format(user_id, key))

if __name__ == '__main__':
    ...
