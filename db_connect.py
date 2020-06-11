import sqlite3
 
 
class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn
 
    def get_connection(self):
        return self.conn
 
    def __del__(self):
        self.conn.close()


class UserModel:
    
    def __init__(self, connection):
        self.connection = connection
        self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             api_key VARCHAR(1000),
                             client_id VARCHAR(1000)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, api_key, client_id) 
                          VALUES (?,?,?,?)''', (user_name, password_hash, '-', '-'))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id)))
        row = cursor.fetchone()
        return row
 
    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [
            (i[0], i[1]) for i in rows
        ]

    def get_id_logins_dictionary(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        ans = {}
        for i in rows:
            ans[i[0]] = i[1]
        return ans

    def exists(self, user_name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ?",
                       (user_name,))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)

    def login(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0], row[3], row[4]) if row else (False,)

    def change_password(self, user_id, new_password):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                       (new_password, user_id))
        print('Password changed!')
        cursor.close()
        self.connection.commit()

    def change_api_key(self, user_id, api_key):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET api_key = ? WHERE id = ?",
                       (api_key, user_id))
        cursor.close()
        self.connection.commit()

    def change_client_id(self, user_id, client_id):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET client_id = ? WHERE id = ?",
                       (client_id, user_id))
        cursor.close()
        self.connection.commit()

    def delete(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM users WHERE id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()


class NewsModel:

    def __init__(self, connection):
        self.connection = connection
        self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             content VARCHAR(1000),
                             user_id INTEGER,
                             filename VARCHAR(1000)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, content, user_id, filename):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, content, user_id, filename) 
                          VALUES (?,?,?,?)''', (title, content, str(user_id), filename))
        print('Success!!')
        cursor.close()
        self.connection.commit()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM news WHERE title = ? AND content = ? AND user_id = ?",
                       (title, content, str(user_id)))
        rows = cursor.fetchall()
        rows = rows[0][0]
        cursor.close()
        self.connection.commit()
        return rows

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id)))
        row = cursor.fetchone()
        return row
 
    def get_all(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT * FROM news WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT id, title FROM news")
        rows = cursor.fetchall()
        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()
