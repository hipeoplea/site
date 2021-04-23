from data import db_session
from data.models import User, Teams, Tasks
from flask import Flask, redirect, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import UserForm, AdminForm
from werkzeug.security import check_password_hash
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


points = 0
chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


def create_password():
    password = ''
    for n in range(10):
        password += random.choice(chars)
    return password



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return redirect('/login')


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
                if len(users) < 7:
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
        admin = db_sess.query(User).filter(User.username == name).filter(User.role == 1).first()
        team = db_sess.query(Teams).filter(Teams.name == 'Admins').first()

        if admin and check_password_hash(team.password_hash, password):
            print('ll')
            login_user(admin)
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
            'tasks': [z[0] for z in db_sess.query(Tasks.name).filter(Tasks.id.in_(
                [y for y in map(int,
                                [x[0] for x in db_sess.query(Teams.open_tasks).filter(Teams.name == current_user.team)]
                                [0].split())])).all()],
            'team_name': current_user.team,

        }
        print(params['tasks'])
        task_list = ['проиграть', 'хотите', 'быть лучше США', 'sdaadwsd', 'awdawda', 'awdawdad', 'dawdad']
        points = [10, 232, 74]
        count = len(task_list)
        return render_template('main.html', count=len(params['tasks']), points=points,
                                opened=len(params['tasks']), all_task='10', point='100', all_point='150')
    else:
        return unauthorized_error(404)


# @app.route('/sett')
# def sett():
#     return render_template('sett.html')


@app.route('/admin')
@login_required
def admin():
    if current_user.role == 1:
        team_list = ['Россия свещеная', 'USA', 'not Usa', 'canada']
        task_list = [['Победить', 'Путен', 'Держава'], 'проиграть', 'проиграть если хотите', 'быть лучше США']
        count = len(team_list)
        return render_template('aaa.html', teams=team_list, tasks=task_list, count=count)
    else:
        print(current_user.role)
        return unauthorized_error(404)


@app.route('/addtasks', methods=['POST', 'GET'])
@login_required
def addtasks():
    if current_user.role == 1:
        if request.method == 'GET':
            return render_template('for_2nd.html')
        elif request.method == 'POST':
            print(request.form['namepoint'])  # название теста
            print(request.form['tests'])  # тест(ы)
            print(request.form['descriptpoint'])  # описание
            print(request.form['number'])  # баллы за тест
            print(request.form['pcoord'])  # координаты
            return render_template('afterform.html', taskname=request.form['namepoint'])
        return render_template('for_2nd.html')
    else:
        return unauthorized_error(404)


@app.route('/addteam', methods=['POST', 'GET'])
@login_required
def addteam():
    if current_user.role == 1:
        passw = create_password()
        if request.method == 'GET':
            return render_template('for_3rdpage.html', password=passw)
        elif request.method == 'POST':
            print(request.form['teamName'])
            return render_template('afterform2.html', teamname=request.form['teamName'], password=passw)
    else:
        return unauthorized_error(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(401)
def unauthorized_error(e):
    return 'oh', 401


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")

    app.run()
