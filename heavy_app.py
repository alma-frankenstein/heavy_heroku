# combines app/__init__.py, app/routes.py, and microblog.py from Grinberg

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

#from models import Song, User
from models import *
from forms import LoginForm, RegistrationForm, EmptyForm, PostForm, EditProfileForm

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Song': Song, 'User': User}

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        song = Song(song_name=form.song.data, artist_name=form.artist.data, song_link=form.song_link.data, contributer=current_user)
        db.session.add(song)
        db.session.commit()
        #flash('you have posted a song')
        #redirect(url_for('index'))
        # redirect(url_for('user', username=current_user.username))
        redirect(url_for('browse'))

    # songs = [
    #     {
    #      'contributer': {'username': 'David'},
    #         'song_name': 'pacific coast',
    #         'artist_name': 'lele'
    #     }
    # ]
    # page = request.args.get('page', 1, type=int)
    # songs = current_user.followed_songs().all() #followed_posts() method in User model
    # songs = current_user.followed_songs().paginate(page, app.config['SONGS_PER_PAGE'], False)
    # next_url = url_for('index', page=songs.next_num) \
    #     if songs.has_next else None
    # prev_url = url_for('index', page=songs.prev_num) \
    #     if songs.has_prev else None
    # return render_template('index.html',  songs=songs.items, form=form, next_url=next_url, prev_url=prev_url)
    return render_template('index.html',form=form)

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
    # songs = [
    #     {'contributer': user, 'song_name': 'I Go To Sleep', 'artist_name': 'Anika'},
    #     {'contributer': user, 'song_name': 'Gamma Ray', 'artist_name': 'Beck'},
    # ]
    #songs = current_user.songs.all() 
    # songs = Song.query.order_by(Song.timestamp.desc()).all()
    page =  request.args.get('page', 1, type=int)
    songs = user.songs.order_by(Song.timestamp.desc()).paginate(page, app.config['SONGS_PER_PAGE'], False)
    form = EmptyForm()
    next_url = url_for('user', username=user.username, page=songs.next_num) \
        if songs.has_next else None
    prev_url = url_for('user', username=user.username, page=songs.prev_num) \
        if songs.has_prev else None
    return render_template('user.html', user=user, songs=songs.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        #return redirect(url_for('index'))
        return redirect(url_for('user', username=current_user.username))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='edit profile', form=form)

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

@app.route('/browse')
@login_required
def browse():
    page = request.args.get('page', 1, type=int)
    # songs = Song.query.order_by(Song.timestamp.desc()).all()
    songs = Song.query.order_by(Song.timestamp.desc()).paginate(page, app.config['SONGS_PER_PAGE'], False)
    next_url = url_for('browse', page=songs.next_num) \
        if songs.has_next else None
    prev_url = url_for('browse', page=songs.prev_num) \
        if songs.has_prev else None
    return render_template('browse.html', songs=songs.items, next_url=next_url, prev_url=prev_url)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500