import random

from data import db_session
from data.models import User, Teams, Tasks
from flask import Flask, redirect, render_template, request
from data import qrs as qrcode
from data.password import create_password
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import UserForm, AdminForm
from werkzeug.security import check_password_hash, generate_password_hash



UPLOAD_FOLDER = 'tests'
ALLOWED_EXTENSIONS = {'py'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('promo.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    userf = UserForm()
    admin = AdminForm()

    if userf.validate_on_submit():

        comand = userf.comand_name.data
        username = userf.username.data
        password = userf.password.data
        db_sess = db_session.create_session()
        team = db_sess.query(Teams).filter(Teams.name == comand).filter(Teams.name != 'Admins').first()

        if team and check_password_hash(team.password_hash, password):
            users = db_sess.query(User.username).filter(User.team == team.name).all()
            users_names = [x[0] for x in users]

            if username in users_names:
                login_user(db_sess.query(User).filter(User.team == team.name).filter(User.username == username).first())
                return redirect("/user")

            else:
                if len(users) < 6:
                    us = User()
                    us.username = username
                    us.team = comand
                    db_sess.add(us)
                    db_sess.commit()
                    login_user(us)
                    return redirect("/user")

                else:
                    return render_template('index.html',
                                           message="Команда заполненна :(",
                                           form=userf, adm_form=admin)
        return render_template('index.html',
                               message="Неверный пароль :(",
                               form=userf, adm_form=admin)

    if admin.validate_on_submit():

        name = admin.ad_username.data
        password = admin.ad_password.data
        db_sess = db_session.create_session()
        admins = db_sess.query(User).filter(User.username == name).filter(User.role == 1).first()
        team = db_sess.query(Teams).filter(Teams.name == 'Admins').first()

        if admins and check_password_hash(team.password_hash, password):
            login_user(admins)
            return redirect('/admin')

        else:
            return render_template('index.html',
                                   message="Неверный пароль :(",
                                   form=userf, adm_form=admin)
    return render_template('index.html', title='Авторизация', form=userf, adm_form=admin)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/user')
@login_required
def user():
    if current_user.role == 0:
        db_sess = db_session.create_session()
        params = {
            'teammates': [x[0] for x in db_sess.query(User.username).filter(User.team == current_user.team).filter(
                User != current_user)],
            'tasks': [x for x in db_sess.query(Tasks.name).all()],
            'team_name': current_user.team,
            'points': [x[0] for x in db_sess.query(Tasks.max_price).filter(Tasks.id.in_(
                [y for y in map(int,
                                [x[0] for x in db_sess.query(Teams.open_tasks).filter(Teams.name == current_user.team)]
                                [0].split())])).all()],
            'opened': len([x[0] for x in db_sess.query(Teams.open_tasks).filter(Teams.name == current_user.team)]
                          [0].split()),
            'all_tasks': len(db_sess.query(Tasks.id).all()),
            'point': db_sess.query(Teams.points).filter(Teams.name == current_user.team).first()[0],
            'all_point': sum([x[0] for x in db_sess.query(Tasks.max_price).all()]),
            'geo': [x for x in map(lambda x: (x.split(',')[::-1]),
                                  [x[0] for x in db_sess.query(Tasks.coords).all()])],
            'disct': [x for x in db_sess.query(Tasks.body).all()]
        }
        return render_template('main.html', param=params, disct=params['disct'])

    else:
        return unauthorized_error(401)


@app.route('/admin')
@login_required
def admin():
    if current_user.role == 1:
        db_sess = db_session.create_session()
        param = {
            'team_list': [x[0] for x in db_sess.query(Teams.name).filter(Teams.name != 'Admins').all()],
        }
        team_list = []
        for i in param['team_list']:
            team_list.append([x for x in db_sess.query(Teams.points).filter(Teams.name == i).first()])
            print(team_list)
        param['task_list'] = team_list
        return render_template('aaa.html', teams=param['team_list'], tasks=param['task_list'],
                               count=len(param['team_list']))
    else:
        return unauthorized_error(401)


@app.route('/addtasks', methods=['POST', 'GET'])
@login_required
def addtasks():
    if current_user.role == 1:
        if request.method == 'GET':
            return render_template('for_2nd.html')
        elif request.method == 'POST':
            db_sess = db_session.create_session()
            task = Tasks()
            task.name = request.form['namepoint']  # название теста
            f = request.files['tests']
            print(f.read())
            f.save('tests/testing.py')
            task.body = request.form['descriptpoint']  # описание
            task.max_price = request.form['number']  # баллы за тест
            task.coords = request.form['pcoord']  # координаты
            db_sess.add(task)
            db_sess.commit()
            qrcode.create_qr(task.body)
            return render_template('afterform.html', taskname=request.form['namepoint'])
        return render_template('for_2nd.html')
    else:
        return unauthorized_error(401)


@app.route('/addteam', methods=['POST', 'GET'])
@login_required
def addteam():
    if current_user.role == 1:
        passw = create_password()
        if request.method == 'GET':
            return render_template('for_3rdpage.html', password=passw)
        elif request.method == 'POST':
            db_sess = db_session.create_session()
            team = Teams()
            team.name = request.form['teamName']
            team.password_hash = generate_password_hash(passw)
            db_sess.add(team)
            db_sess.commit()
            return render_template('afterform2.html', teamname=request.form['teamName'], password=passw)
    else:
        return unauthorized_error(401)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

    
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized_error(e):
    return "you haven't got enough rights", 401


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    qrcode.create_qr('а вы любопытны:)')
    app.run()
