from requests import get, post, delete
import random


def testcase1():
    signup('fast', 'fourier')
    login('fast', 'fourier')
    create_publication(
        title='Server.py',
        description='Server description',
        filename='server.py'
    )
    index()
    create_publication(
        title='Forms.py',
        description='Forms description',
        filename='forms.py'
    )
    index()
    get_publication(1)
    get_publication(2)
    get_publication(3)
    delete_publication(1)
    index()
    get_upload(2, 'forms.py')
    index()


def signup(login='password', password='login'):
    signup = post('http://127.0.0.1:5000/signup', data={
        'login': login,
        'password': password
    })
    print(signup.json())


def login(login='password', password='login'):
    login = post('http://127.0.0.1:5000/login', data={
        'login': login,
        'password': password
    })
    print(login.json())


def create_publication(title, description, filename):
    new_pub = post(f'http://127.0.0.1:5000/news/{random.randint(1, 1000)}', data={
        'title': title,
        'description': description,
        'file_name': filename.split('/')[-1]
    }, files={'file': open(filename)})
    print(new_pub.json())


def index():
    index = get('http://127.0.0.1:5000/index')
    print(index.json())


def get_publication(id):
    pub = get(f'http://127.0.0.1:5000/news/{id}')
    print(pub.json())


def delete_publication(id):
    deletion = delete(f'http://127.0.0.1:5000/news/{id}')
    print(deletion.json())


def get_upload(id, filename):
    uploadster = get('http://127.0.0.1:5000/get_upload', data={
        'news_id': id,
        'filename': filename
    })
    if uploadster.status_code != 200:
        print(uploadster.json())
    else:
        with open(input('Where to save? > '), 'w') as f:
            f.write(uploadster.text)
        print('File saved successfully.')


if __name__ == "__main__":
    testcase1()
