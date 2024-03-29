from flask import *
from forms import AddNewsForm, ChangePasswordForm, LoginForm, SignUpForm, ChangeApiKeyForm, ChangeClientIDForm
from db_connect import *
import os
from flask import request, redirect
from werkzeug.utils import secure_filename
from flask import Flask
#from RESTful import *
from ozon_api import get_postings_info, get_markings, get_postings_info_awaiting_packaging,\
    get_postings_info_awaiting_deliver, get_postings_info_arbitration, get_postings_info_delivering,\
    get_postings_info_delivered, get_postings_info_cancelled, print_acts, deliver_selected_postings, get_all_items
from json import load, dump
from threading import Thread
from multiprocessing import Process
import os


db = DB()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.errorhandler(404)
def not_found(error):
    return """<h1>404?</h1>"""


def check_postings(uid):
    try:
        with open(f"{session['user_id']}/postings_" + str(uid) + '.json', 'r+', encoding='utf-8') as f:
            with open(f"{session['user_id']}/postings_" + str(uid) + '_awaiting_packaging.json', 'r+', encoding='utf-8') as f:
                with open(f"{session['user_id']}/postings_" + str(uid) + '_awaiting_deliver.json', 'r+', encoding='utf-8') as f:
                    with open(f"{session['user_id']}/postings_" + str(uid) + '_arbitration.json', 'r+', encoding='utf-8') as f:
                        with open(f"{session['user_id']}/postings_" + str(uid) + '_delivering.json', 'r+', encoding='utf-8') as f:
                            with open(f"{session['user_id']}/postings_" + str(uid) + '_delivered.json', 'r+', encoding='utf-8') as f:
                                with open(f"{session['user_id']}/postings_" + str(uid) + '_cancelled.json', 'r+', encoding='utf-8') as f:
                                    return True
    except Exception as e:
        print(e)
        return False


def print_markings(posting_numbers):
    print("here", posting_numbers)
    get_markings(session['api_key'], session["client_id"], posting_numbers, session["user_id"])


@app.route('/downloads', methods=['GET', 'POST'])
def download_center():
    path = f'./{session["user_id"]}'
    if not os.path.isdir(path):
        os.mkdir(path)
    files = [i for i in os.listdir(path) if i.startswith("Маркировки") or i.startswith("Акты")]
    return render_template('downloads.html', files=files, is_empty=(len(files) == 0))


@app.route('/get_download/<filename>', methods=['GET', 'POST'])
def get_download(filename):
    if os.path.isfile(f'./{session["user_id"]}/{filename}'):
        return send_from_directory(f'./{session["user_id"]}/',
                                   filename, as_attachment=True)
    return redirect("/downloads")


def get_acts():
    print_acts(session["api_key"], session["client_id"], session["user_id"])

'''
<style>
        .zoom {
        transition: transform .1s;
    }
    .zoom:hover {
        transform: scale(5);
    }
    </style>
'''


@app.route('/get_act', methods=['GET', 'POST'])
def get_act():
    with app.app_context():
        thread = Process(target=get_acts, args=())
        thread.daemon = True
        thread.start()
        with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '.json', 'r+', encoding='utf-8') as f:
            s = load(f)
        return render_template('index.html', username=session['username'],
                               postings_data=s, act_started=True)


def check_items():
    try:
        with open(f"{session['user_id']}/items_ALL.json", 'r+', encoding='utf-8') as f:
            with open(f"{session['user_id']}/items_VISIBLE.json", 'r+', encoding='utf-8') as f:
                with open(f"{session['user_id']}/items_INVISIBLE.json", 'r+', encoding='utf-8') as f:
                    with open(f"{session['user_id']}/items_READY_TO_SUPPLY.json", 'r+', encoding='utf-8') as f:
                        with open(f"{session['user_id']}/items_STATE_FAILED.json", 'r+', encoding='utf-8') as f:
                            return True
    except Exception as e:
        print(e)
        return False


def get_items():
    get_all_items(session["api_key"], session["client_id"], session["user_id"])


@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'POST':
        with app.app_context():
            thread = Process(target=get_items, args=())
            thread.daemon = True
            thread.start()
        return render_template('updating_wait.html')
    path = f'./{session["user_id"]}'
    if not os.path.isdir(path):
        os.mkdir(path)
    if not check_items():
        return render_template("update_items.html")
    try:
        with open(f"{session['user_id']}/items_ALL.json", 'r+', encoding='utf-8') as f:
            items_ALL = load(f)
    except Exception as e:
        items_ALL = []
    try:
        with open(f"{session['user_id']}/items_VISIBLE.json", 'r+', encoding='utf-8') as f:
            items_VISIBLE = load(f)
    except Exception as e:
        items_VISIBLE = []
    try:
        with open(f"{session['user_id']}/items_INVISIBLE.json", 'r+', encoding='utf-8') as f:
            items_INVISIBLE = load(f)
    except Exception as e:
        items_INVISIBLE = []
    try:
        with open(f"{session['user_id']}/items_READY_TO_SUPPLY.json", 'r+', encoding='utf-8') as f:
            items_READY_TO_SUPPLY = load(f)
    except Exception as e:
        items_READY_TO_SUPPLY = []
    try:
        with open(f"{session['user_id']}/items_STATE_FAILED.json", 'r+', encoding='utf-8') as f:
            items_STATE_FAILED = load(f)
    except Exception as e:
        items_STATE_FAILED = []
    return render_template("items.html", items_ALL=items_ALL, items_VISIBLE=items_VISIBLE,
                           items_INVISIBLE=items_INVISIBLE, items_READY_TO_SUPPLY=items_READY_TO_SUPPLY,
                           items_STATE_FAILED=items_STATE_FAILED)



def deliver_selected(posting_numbers):
    print(posting_numbers)
    deliver_selected_postings(session["api_key"], session["client_id"], session["user_id"], posting_numbers)


@app.route('/delete/<filename>', methods=['GET', 'POST'])
def delete(filename):
    if os.path.isfile(f'./{session["user_id"]}/{filename}'):
        os.remove(f'./{session["user_id"]}/{filename}')
    return redirect("/downloads")


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        posting_numbers = request.form.getlist('posting_labels')
        print(posting_numbers)
        if posting_numbers:
            if request.form['action'] == 'Распечатать маркировки':
                with app.app_context():
                    thread = Process(target=print_markings, args=(posting_numbers,))
                    thread.daemon = True
                    thread.start()
                    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '.json', 'r+', encoding='utf-8') as f:
                        s = load(f)
                    return render_template('index.html', username=session['username'],
                                           postings_data=s, markings_started=True)
            elif request.form['action'] == 'Собрать выбранные':
                with app.app_context():
                    thread = Process(target=deliver_selected, args=(posting_numbers,))
                    thread.daemon = True
                    thread.start()
                    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '.json', 'r+', encoding='utf-8') as f:
                        s = load(f)
                    return render_template('index.html', username=session['username'],
                                           postings_data=s, deliver_started=True)
    print("!!!!!!!!!!!")
    if 'username' not in session:
        return redirect('/start')
    if session['api_key'] == '-' or session['client_id'] == '-':
        return render_template('no_apikey.html')
    session["postings_data"] = check_postings(session["user_id"])
    if not session["postings_data"]:
        return redirect("/upgrade")
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '.json', 'r+', encoding='utf-8') as f:
        s = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_awaiting_packaging.json', 'r+', encoding='utf-8') as f:
        postings_data_awaiting_packaging = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_awaiting_deliver.json', 'r+', encoding='utf-8') as f:
        postings_data_awaiting_deliver = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_arbitration.json', 'r+', encoding='utf-8') as f:
        postings_data_arbitration = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_delivering.json', 'r+', encoding='utf-8') as f:
        postings_data_delivering = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_delivered.json', 'r+', encoding='utf-8') as f:
        postings_data_delivered = load(f)
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_cancelled.json', 'r+', encoding='utf-8') as f:
        postings_data_cancelled = load(f)
    return render_template('index.html', username=session['username'],
                           postings_data=s, postings_data_awaiting_packaging=postings_data_awaiting_packaging,
                           postings_data_awaiting_deliver=postings_data_awaiting_deliver,
                           postings_data_arbitration=postings_data_arbitration,
                           postings_data_delivering=postings_data_delivering,
                           postings_data_delivered=postings_data_delivered,
                           postings_data_cancelled=postings_data_cancelled)


def get_postings():
    path = f'./{session["user_id"]}'
    if not os.path.isdir(path):
        os.mkdir(path)
    postings_data = get_postings_info(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '.json', "w+", encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_awaiting_packaging(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_awaiting_packaging.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_awaiting_deliver(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_awaiting_deliver.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_arbitration(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_arbitration.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_delivering(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_delivering.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_delivered(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_delivered.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)
    postings_data = get_postings_info_cancelled(session["api_key"], session['client_id'], session['user_id'])
    with open(f"{session['user_id']}/postings_" + str(session["user_id"]) + '_cancelled.json', 'w+', encoding='utf-8') as f:
        dump(postings_data, f, indent=4, ensure_ascii=False)


@app.route('/updater')
def updater():
    if 'username' not in session:
        return redirect('/start')
    if session['api_key'] == '-' or session['client_id'] == '-':
        return render_template('no_apikey.html')
    try:
        with app.app_context():

            thread = Process(target=get_postings, args=())
            thread.daemon = True
            thread.start()
            return render_template("loading.html")
    except Exception:
        return render_template('no_apikey.html')


@app.route('/upgrade')
def update():
    if "update" in request.form:
        return render_template("loading.html")
    return render_template('load_postings.html')


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
        exists = user_model.exists(user_name)
        if not exists[0]:
            user_model.insert(user_name, password)
            return redirect("/login")
        return render_template('signup.html', title='Регистрация', form=form, attempt=True)
    return render_template('signup.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UserModel(db.get_connection())
        success = user_model.login(user_name, password)
        if success[0]:
            session['username'] = user_name
            session['user_id'] = success[1]
            session['api_key'] = success[2]
            session['client_id'] = success[3]
            session["postings_data"] = check_postings(session["user_id"])
            return redirect("/index")
        return render_template('login.html', title='Авторизация', form=form, attempt=True)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    session.pop('api_key', 0)
    session.pop('client_id', 0)
    session.pop('postings_data', 0)
    return redirect('/index')

'''
@app.route('/get_upload/<string:news_id>/<string:file_name>', methods=['GET', 'POST'])
def get_upload(news_id, file_name):
    if session['user_id'] in Permissions(db.get_connection()).get_news_permissions(news_id)\
            and file_name in NewsModel(db.get_connection()).get(news_id):
        return send_from_directory(app.config['UPLOAD_FOLDER'], file_name)
    return redirect('/access_denied')


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
'''


@app.route('/delete_user/', methods=['GET'])
def delete_user():
    if 'username' not in session:
        return redirect('/login')
    nm = UserModel(db.get_connection())
    nm.delete(session['user_id'])
    return redirect("/logout")


'''
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
'''

@app.route('/access_denied')
def access_denied():
    return '''<h1>Access denied :(</h1>'''

'''
@app.route('/add_permission/<int:news_id>')
def add_permission(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if str(news[3]) != str(session['user_id']):
        return redirect('/access_denied')
    userlist = UserModel(db.get_connection()).get_all()
    return render_template('add_permission.html', title='Изменение параметров публикации',
                           news=news, userlist=userlist)


@app.route('/make_public/<int:news_id>', methods=['GET'])
def make_public(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if str(news[3]) != str(session['user_id']):
        return redirect('/access_denied')
    nm = Permissions(db.get_connection())
    for idx, name in UserModel(db.get_connection()).get_all():
        nm.add_permission(news_id, idx)
    return redirect(f'news_page/{news_id}')


@app.route('/make_private/<int:news_id>', methods=['GET'])
def make_private(news_id):
    news = NewsModel(db.get_connection()).get(news_id)
    if str(news[3]) != str(session['user_id']):
        return redirect('/access_denied')
    nk = Permissions(db.get_connection())
    for idx in nk.get_news_permissions(news_id):
        if str(session['user_id']) != str(idx):
            nk.delete_permission(news_id, idx)
    return redirect(f'news_page/{news_id}')


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

'''


@app.route('/panel', methods=['GET', 'POST'])
def user_page():
    user = UserModel(db.get_connection())
    user_id = session['user_id']
    uname = user.get(user_id)
    print(user_id)
    print(uname)
    form = ChangePasswordForm()
    form1 = ChangeApiKeyForm()
    form2 = ChangeClientIDForm()
    if form.validate_on_submit() and form.new_password.data != '':
        UserModel(db.get_connection()).change_password(user_id, form.new_password.data)
        uname = user.get(user_id)
        return render_template('user_page.html', username=uname[1], form=form, form1=form1, form2=form2, title=uname[1],
                               success_pass=True, user_id=uname[0], api_key=uname[3], client_id=uname[4])
    if form1.validate_on_submit() and form1.new_apikey.data != '':
        UserModel(db.get_connection()).change_api_key(user_id, form1.new_apikey.data)
        session["api_key"] = form1.new_apikey.data
        uname = user.get(user_id)
        return render_template('user_page.html', username=uname[1], form=form, form1=form1, form2=form2, title=uname[1],
                               success_api_key=True, user_id=uname[0], api_key=uname[3], client_id=uname[4])
    if form2.validate_on_submit() and form2.new_clientid.data != '':
        UserModel(db.get_connection()).change_client_id(user_id, form2.new_clientid.data)
        session["client_id"] = form2.new_clientid.data
        uname = user.get(user_id)
        return render_template('user_page.html', username=uname[1], form=form, form1=form1, form2=form2, title=uname[1],
                               success_client_id=True, user_id=uname[0], api_key=uname[3], client_id=uname[4])
    return render_template('user_page.html', username=uname[1], title=uname[1],
                           form=form, form1=form1, form2=form2, api_key=uname[3], client_id=uname[4], user_id=uname[0])


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', threaded=True)
    app.app_context().push()
