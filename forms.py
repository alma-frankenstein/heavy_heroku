from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from models import User

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('sign in')

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('repeat password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('please try a different username')

class EmptyForm(FlaskForm):
    submit = SubmitField('submit')

class PostForm(FlaskForm):
    song = TextAreaField('song name', validators=[DataRequired(), Length(min=1, max=60)])
    artist = TextAreaField('artist name', validators=[DataRequired(), Length(min=1, max=60)])
    song_link = TextAreaField('link to song (optional)')
    submit = SubmitField('submit')

class EditProfileForm(FlaskForm):
    file = FileField('File')
    username = StringField('username')
    about_me = TextAreaField('about me', validators=[Length(min=0, max=140)])
    submit = SubmitField('submit')
