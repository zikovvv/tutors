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

if __name__ == '__main__':
    ...
