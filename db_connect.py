import sqlite3
 
 
class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn
 
    def get_connection(self):
        return self.conn
 
    def __del__(self):
        self.conn.close()


class Permissions:
    def __init__(self, connection):
        self.connection = connection
        self.init_table()

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS permissions 
                            (news_id INTEGER, 
                             user_id INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def add_permission(self, news_id, user_id):
        if not self.exists(news_id, user_id)[0]:
            cursor = self.connection.cursor()
            cursor.execute('''INSERT INTO permissions
                              (news_id, user_id) 
                              VALUES (?,?)''', (str(news_id), str(user_id)))
            cursor.close()
            self.connection.commit()

    def get_news_permissions(self, news_id=None):
        cursor = self.connection.cursor()
        if news_id:
            cursor.execute("SELECT user_id FROM permissions WHERE news_id = ?",
                           (str(news_id),))
        else:
            cursor.execute("SELECT news_id, user_id FROM permissions")
        rows = cursor.fetchall()
        return [list(i)[0] for i in rows]

    def get_user_permissions(self, user_id=None):
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute("SELECT news_id FROM permissions WHERE user_id = ?",
                           (str(user_id)))
        else:
            cursor.execute("SELECT news_id, user_id FROM permissions")
        rows = cursor.fetchall()
        k = [list(i)[0] for i in rows]
        return k # [i for i in k if self.checked(i, user_id)]

    def checked(self, news_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT news_id FROM permissions WHERE news_id = ? AND user_id = ?",
                       (str(news_id), str(user_id)))
        rows = cursor.fetchall()
        if rows:
            return True
        return False

    def delete_permission(self, news_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM permissions WHERE news_id = ? AND user_id = ?''', (str(news_id), str(user_id)))
        cursor.close()
        self.connection.commit()

    def delete_news(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM permissions WHERE news_id = ?''', (str(news_id)))
        cursor.close()
        self.connection.commit()

    def delete_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM permissions WHERE user_id = ?''', (str(user_id)))
        cursor.close()
        self.connection.commit()

    def exists(self, news_id, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM permissions WHERE news_id = ? AND user_id = ?",
                       (news_id, user_id))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


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
                             description VARCHAR(1000)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, description) 
                          VALUES (?,?,?)''', (user_name, password_hash, 'No description provided'))
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
        return (True, row[0]) if row else (False,)

    def change_password(self, user_id, new_password):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?",
                       (new_password, user_id))
        print('Password changed!')
        cursor.close()
        self.connection.commit()

    def change_description(self, user_id, new_description):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET description = ? WHERE id = ?",
                       (new_description, user_id))
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
