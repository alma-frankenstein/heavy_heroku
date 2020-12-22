# combines app/__init__.py, app/routes.py, and microblog.py from Grinberg

from flask import Flask, render_template, flash, redirect, url_for, request, abort
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

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
    # if form.validate_on_submit():
    if request.method == 'POST':
        song = Song(song_name=form.song.data, artist_name=form.artist.data, song_link=form.song_link.data, contributer=current_user)
        db.session.add(song)
        db.session.commit()
        flash('you have posted a song')
        return redirect(url_for('browse'))
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
    # format file name
    userIdStr = str(current_user.get_id())
    avatarLocation = 'static/avatars/'+ userIdStr + '.jpeg'
    avatarFromUser = '../static/avatars/'+ userIdStr + '.jpeg'
    if form.validate_on_submit():
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(uploaded_file.filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            else:
                # uploaded_file.save(uploaded_file.filename)
                # uploaded_file.save(os.path.join('static/avatars', current_user.get_id()))
                uploaded_file.save(avatarLocation)
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('user', username=current_user.username, avatarLocation=avatarLocation, avatarFromUser=avatarFromUser))

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
    songs = Song.query.order_by(Song.timestamp.desc()).paginate(page, app.config['SONGS_PER_PAGE'], False)
    next_url = url_for('browse', page=songs.next_num) \
        if songs.has_next else None
    prev_url = url_for('browse', page=songs.prev_num) \
        if songs.has_prev else None
    return render_template('browse.html', songs=songs.items, next_url=next_url, prev_url=prev_url)

@app.route('/see_users')
@login_required
def see_users():
    users = User.query.all()
    return render_template('see_users.html', users=users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(413)
def file_too_large(e):
    return render_template('413.html'), 413

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400