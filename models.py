from heavy_app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

followers = db.Table('followers',      # association table
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Column instance creates field
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    songs = db.relationship('Song', backref='contributer', lazy='dynamic')
    about_me = db.Column(db.String(140))

    followed = db.relationship(         # many-to-many
        'User', secondary=followers,    # user being followed (left side following right side)
        primaryjoin=(followers.c.follower_id==id),
        secondaryjoin=(followers.c.followed_id==id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
        # The "c" is an attribute of SQLAlchemy tables that are not defined as models. For these tables, 
        # the table columns are all exposed as sub-attributes of this "c" attribute.
   
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_songs(self):
        followed = Song.query.join(
            followers, (followers.c.followed_id == Song.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Song.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Song.timestamp.desc())


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(140))
    song_name = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Song {}'.format(self.song_name)
