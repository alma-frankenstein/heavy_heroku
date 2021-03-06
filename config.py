import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'unguessable'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SONGS_PER_PAGE = 6
        MAX_CONTENT_LENGTH = 3000000
        UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif', '.jpeg', '.JPG']