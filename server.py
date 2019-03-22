from flask import *
from forms import AddNewsForm, ChangePasswordForm, LoginForm, SignUpForm
from db_connect import *
import os
from flask import request, redirect
from werkzeug.utils import secure_filename
from flask import Flask

db = DB()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = '/home/mint/Documents/file_database/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.errorhandler(404)
def not_found(error):
    return """<h1>404?</h1>"""


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/start')
    md = NewsModel(db.get_connection())
    news = md.get_all(session['user_id'])
    h = set(Permissions(db.get_connection()).get_user_permissions(session['user_id']))
    return render_template('index.html', username=session['username'],
                           news=news, affordable=[md.get(i) for i in h])


@app.route('/start')
def start():
    return render_template('start.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if not exists[0]:
            user_model.insert(user_name, password)
        return redirect("/index")
    return render_template('signup.html', title='Регистрация', form=form)    


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect("/index")
        return render_template('login.html', title='Авторизация', form=form, attempt=True)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/get_upload/<string:news_id>/<string:file_name>', methods=['GET', 'POST'])
def get_upload(news_id, file_name):
    if session['user_id'] not in Permissions(db.get_connection()).get_news_permissions(news_id):
        redirect('/access_denied')
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_name)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if request.method == 'POST':
        title = form.title.data
        content = form.content.data
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nm = NewsModel(db.get_connection())
        h = nm.insert(title, content, session['user_id'], filename)
        nm = Permissions(db.get_connection())
        nm.add_permission(h, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости', form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    if str(nm.get(news_id)[3]) != str(session['user_id']):
        return redirect('/access_denied')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    nm = Permissions(db.get_connection())
    nm.delete_news(news_id)
    return redirect("/index")


@app.route('/news_page/<int:news_id>', methods=['GET'])
def news_page(news_id):
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection()).get(news_id)
    nm = Permissions(db.get_connection())
    nmm = nm.get_news_permissions(news_id)
    h = list(map(str, nmm))
    if str(session['user_id']) not in h:
        return redirect('/access_denied')
    owner = False
    if str(news[3]) == str(session['user_id']):
        owner = True
    usernames = UserModel(db.get_connection())
    owner_cred = usernames.get(str(news[3]))
    return render_template('news_page.html', title='Публикация',
                           news=news, permissions=nmm, owner=owner, usernames=usernames.get_id_logins_dictionary(),
                           owner_name=owner_cred[1], owner_id=owner_cred[0], filename=news[4].split('/')[-1])


@app.route('/access_denied')
def access_denied():
    return '''<h1>Access denied :(</h1>'''


@app.route('/add_permission/<int:news_id>')
def add_permission(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if str(news[3]) != str(session['user_id']):
        return redirect('/access_denied')
    userlist = UserModel(db.get_connection()).get_all()
    return render_template('add_permission.html', title='Изменение параметров публикации',
                           news=news, userlist=userlist)


@app.route('/delete_permission/<int:news_id>')
def delete_permission(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if str(news[3]) != str(session['user_id']):
        return redirect('/access_denied')
    nm = Permissions(db.get_connection()).get_news_permissions(news_id)
    jk = UserModel(db.get_connection()).get_id_logins_dictionary()
    return render_template('delete_permission.html', title='Изменение параметров публикации',
                           news=news, userlist=jk, displayed=nm)


@app.route('/submit_user_added/<int:news_id>/<int:user_id>')
def submit_user_added(news_id, user_id):
    h = Permissions(db.get_connection())
    exists = h.exists(news_id, user_id)
    if not exists[0]:
        h.add_permission(news_id, user_id)
    return redirect(f'news_page/{news_id}')


@app.route('/submit_user_deleted/<int:news_id>/<int:user_id>')
def submit_user_deleted(news_id, user_id):
    h = Permissions(db.get_connection())
    h.delete_permission(news_id, user_id)
    return redirect(f'news_page/{news_id}')


@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def user_page(user_id):
    user = UserModel(db.get_connection())
    owner = user_id == session['user_id']
    uname = user.get(user_id)
    form = ChangePasswordForm()
    if form.validate_on_submit():
        UserModel(db.get_connection()).change_password(user_id, form.new_password.data)
        return render_template('user_page.html', username=uname[1], form=form, title=uname[1], owner=owner, success=True)
    return render_template('user_page.html', username=uname[1], title=uname[1], owner=owner, form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
