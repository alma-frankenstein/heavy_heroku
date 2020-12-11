# combines __init__.py, routes.py, and app.py from Grinberg

from flask import Flask, render_template, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

from models import Song, User
from forms import LoginForm, RegistrationForm, EmptyForm, PostForm

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Song': Song, 'User': User}

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        song = Song(song_name=form.song.data, artist_name=form.artist.data, contributer=current_user)
        db.session.add(song)
        db.session.commit()
        flash('you have posted a song')
        redirect(url_for('index'))
    songs = [
        {
         'contributer': {'username': 'David'},
            'song_name': 'pacific coast',
            'artist_name': 'lele'
        }
    ]
    return render_template('home.html',  songs=songs, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('congratulations, now you\'re registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('wrong name or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='sign in', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    songs = [
        {'contributer': user, 'song_name': 'I Go To Sleep', 'artist_name': 'Anika'},
        {'contributer': user, 'song_name': 'GAmma Ray', 'artist_name': 'Beck'},
    ]
    form = EmptyForm()
    return render_template('user.html', user=user, songs=songs, form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('user {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('you can\'t follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('you are following {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('user {} not found'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('you can\'t unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('you are unfollowing {}'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500